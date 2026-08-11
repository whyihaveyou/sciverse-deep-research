# -*- coding: utf-8 -*-
"""state_machine.py — M2 自研轻量状态机内核（学 LangGraph StateGraph 概念，stdlib 零依赖）。

规格：~/.buzz/PLANS/M2_ORCHESTRATION_SPEC.md §1；设计要点（§1.1，勤务员研究笔记校验）：
  - State：可 JSON 序列化的 dict（run_id / completed_nodes / artifacts / version）。
  - Node：fn(state, ctx) -> (state, artifacts)；幂等可重放，产物落盘带「已存在即跳过」守卫。
  - Edge：add_edge(src, dest, condition=None)；condition 是纯函数 router（禁拿异常当控制流）；
    多条出边按注册顺序求值，condition=None 为无条件兜底边。
  - START / END 隐式哨兵：入口/出口显式声明，不靠「谁没入边」约定推断。
  - Checkpoint：每节点完成后落盘 {completed_nodes, active_node, state_snapshot, version}；
    节点开跑前先落「in-flight」checkpoint（active_node=当前节点）——崩溃可能发生在节点
    中途，--resume 从第一个未完成节点续，而非只看最后完成节点。
  - 并行合并靠 reducer：fan-out 子任务结果在 Node B 内 append 合并（见 nodes.py）；
    ledger 单写覆盖 + 乐观锁（见 nodes.py ledger_build）。

回环语义：正常前向执行不跳过任何节点；仅 --resume 时跳过「已完成前缀」，一旦遇到第一个
未完成节点即恢复为「逢节点必执行」——此后条件边路由回已完成节点（门禁回退）会正常重跑。
"""
import hashlib
import io
import json
import os

START = "<START>"
END = "<END>"


class ContractError(Exception):
    """节点产物未过 out_schema 契约——run 失败，checkpoint 停在该节点可 --resume。"""


class GraphError(Exception):
    """图结构/路由错误：未注册节点、死端（无出边命中）等。"""


# ---------------- JSON-Schema 子集校验（stdlib 零依赖） ----------------
# 支持：type / required / properties / items / enum / minItems / minLength / minimum。
# 覆盖 contracts/ 三份 schema 的用语；node out_schema 与节点 I/O 校验共用。

def validate(schema, payload, path="$"):
    """按 JSON-Schema 子集校验 payload，返回错误列表（空 = 通过）。"""
    errs = []
    if not isinstance(schema, dict):
        return errs
    typ = schema.get("type")
    if typ:
        ok = {
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
        }.get(typ)
        if ok is None:
            errs.append(f"{path}: 未知 schema type {typ!r}")
            return errs
        if not ok(payload):
            errs.append(f"{path}: 期望 {typ}，得到 {type(payload).__name__}")
            return errs  # 类型不符则子约束无意义，避免级联误报
    if "enum" in schema and payload not in schema["enum"]:
        errs.append(f"{path}: 取值 {payload!r} 不在枚举 {schema['enum']!r}")
    if typ == "string" and "minLength" in schema and len(payload) < schema["minLength"]:
        errs.append(f"{path}: 字符串长度 {len(payload)} < minLength {schema['minLength']}")
    if typ in ("integer", "number") and "minimum" in schema and payload < schema["minimum"]:
        errs.append(f"{path}: 取值 {payload!r} < minimum {schema['minimum']}")
    if typ == "array":
        if "minItems" in schema and len(payload) < schema["minItems"]:
            errs.append(f"{path}: 数组长度 {len(payload)} < minItems {schema['minItems']}")
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(payload):
                errs.extend(validate(item_schema, item, f"{path}[{i}]"))
    if typ == "object":
        for req in schema.get("required", []):
            if req not in payload:
                errs.append(f"{path}: 缺必填字段 {req!r}")
        props = schema.get("properties", {})
        for k, sub in props.items():
            if k in payload:
                errs.extend(validate(sub, payload[k], f"{path}.{k}"))
    return errs


def load_schema(contracts_dir, name):
    """读取 contracts/<name>.schema.json。"""
    p = os.path.join(contracts_dir, f"{name}.schema.json")
    return json.loads(io.open(p, encoding="utf-8").read())


def state_hash(state):
    """state 必须 json.dumps 可序列化且 hash 可校验（规格 §1）。"""
    return hashlib.sha256(
        json.dumps(state, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def _atomic_write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    io.open(tmp, "w", encoding="utf-8").write(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    os.replace(tmp, path)


# ---------------- 状态机内核 ----------------

class StateMachine:
    START = START
    END = END

    def __init__(self, run_dir, ctx=None):
        """run_dir = .workflow/runs/<run_id>/；ctx 透传给节点函数（workdir/seeds 等）。"""
        self.run_dir = run_dir
        self.ctx = ctx
        self.nodes = {}  # name -> (fn, out_schema)
        self.edges = {}  # src  -> [(dest, condition)]，注册顺序即求值顺序

    def add_node(self, name, fn, out_schema=None):
        if name in (START, END):
            raise GraphError(f"{name} 是隐式哨兵，不能注册为真实节点")
        if name in self.nodes:
            raise GraphError(f"节点 {name!r} 重复注册")
        self.nodes[name] = (fn, out_schema)
        return self

    def add_edge(self, src, dest, condition=None):
        """condition: 纯函数 (state)->bool，只读 state、无副作用；None = 无条件兜底边。"""
        if dest != END and dest not in self.nodes:
            raise GraphError(f"边指向未注册节点 {dest!r}")
        if src != START and src not in self.nodes:
            raise GraphError(f"边起点 {src!r} 未注册（入口请用 START 哨兵）")
        self.edges.setdefault(src, []).append((dest, condition))
        return self

    # ---- checkpoint ----

    def _checkpoint_path(self):
        return os.path.join(self.run_dir, "checkpoint.json")

    def _write_checkpoint(self, state, active_node):
        state["version"] = int(state.get("version", 0)) + 1
        _atomic_write_json(self._checkpoint_path(), {
            "completed_nodes": list(state.get("completed_nodes", [])),
            "active_node": active_node,
            "state_snapshot": state,
            "version": state["version"],
            "state_hash": state_hash(state),
        })

    def _load_checkpoint(self):
        p = self._checkpoint_path()
        if not os.path.isfile(p):
            raise GraphError(f"--resume 但无 checkpoint：{p}")
        return json.loads(io.open(p, encoding="utf-8").read())

    # ---- routing ----

    def _next(self, src, state):
        """router：按注册顺序求值出边；condition 必须是纯函数。无命中 = 死端报错。"""
        for dest, cond in self.edges.get(src, []):
            if cond is None or cond(state):
                return dest
        raise GraphError(
            f"节点 {src!r} 无命中出边（死端）——条件边 router 应覆盖全部分支，"
            f"或补一条无条件兜底边")

    # ---- run ----

    def run(self, initial, resume=False, start=START):
        """从 START（或 resume 的 active_node）执行到 END，返回终态 state。

        resume：读 checkpoint，跳过「已完成前缀」节点，从第一个未完成节点续跑。
        """
        if resume:
            cp = self._load_checkpoint()
            state = cp["state_snapshot"]
            if state_hash(state) != cp.get("state_hash"):
                raise GraphError("checkpoint state_snapshot 哈希不符——落盘损坏或被手改")
            completed = set(cp.get("completed_nodes", []))
            node = cp.get("active_node") or self._next(start, state)
        else:
            state = dict(initial)
            state.setdefault("completed_nodes", [])
            state.setdefault("artifacts", {})
            state.setdefault("version", 0)
            completed = set()
            node = self._next(start, state)

        skipping = True  # 仅 resume 前缀跳过；遇到第一个未完成节点后恢复逢节点必执行
        while node != END:
            if skipping and node in completed:
                node = self._next(node, state)
                continue
            skipping = False
            if node not in self.nodes:
                raise GraphError(f"路由到未注册节点 {node!r}")
            fn, out_schema = self.nodes[node]
            # in-flight checkpoint：崩溃发生在节点中途时，--resume 从本节点续
            self._write_checkpoint(state, active_node=node)
            state, artifacts = fn(state, self.ctx)
            if out_schema is not None:
                errs = validate(out_schema, artifacts, path=f"$node[{node}]")
                if errs:
                    raise ContractError(
                        f"节点 {node!r} 产物未过契约：\n" + "\n".join(errs))
            state.setdefault("artifacts", {})[node] = artifacts
            state.setdefault("completed_nodes", []).append(node)
            self._write_checkpoint(state, active_node=self._next(node, state))
            node = self._next(node, state)
        return state
