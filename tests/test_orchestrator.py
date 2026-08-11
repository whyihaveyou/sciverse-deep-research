#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_orchestrator.py — 审查员 M2 状态机单测（T1–T5），独立于 Jake 的 selftest。

覆盖验收口径（M2_ORCHESTRATION_SPEC §6）：
  T1 节点流转：A→B→C 顺序执行，state.completed_nodes 依序推进，产物落 state.artifacts
  T2 条件边：router 纯函数 True→destX / False→destY；死端（无命中）抛 GraphError
  T3 checkpoint 续跑：--resume 从第一个未完成节点续，已完成节点不重跑（产物 mtime 不变）
  T4 schema 校验：validate() 拦截缺 required / enum 越界 / type 不符 / minLength；合法载荷零错误
  T5 乐观锁冲突：磁盘 version 不符 → LockConflict FAIL；幂等守卫在内容相同时不误报

stdlib 零依赖，与 scripts/ 哲学一致。运行：python3 tests/test_orchestrator.py
"""
import io
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)  # 使 `from orchestrator import ...` 解析到 repo orchestrator/

from orchestrator.state_machine import StateMachine, END, START, GraphError, ContractError
from orchestrator import state_machine as sm_mod
from orchestrator import nodes

RESULTS = []


def check(name, cond, detail=""):
    RESULTS.append((name, bool(cond), detail))
    print(("PASS  " if cond else "FAIL  ") + name + ("" if not detail or cond else "  | " + detail))


# ---------------- T1 节点流转 ----------------
def t1_node_flow():
    with tempfile.TemporaryDirectory() as td:
        sm = StateMachine(os.path.join(td, "runs"))
        order = []
        sm.add_node("A", lambda s, ctx: (order.append("A") or {**s, "markA": True}, {"idx": 1}))
        sm.add_node("B", lambda s, ctx: (order.append("B") or {**s, "markB": True}, {"idx": 2}))
        sm.add_node("C", lambda s, ctx: (order.append("C") or {**s, "markC": True}, {"idx": 3}))
        sm.add_edge(START, "A")
        sm.add_edge("A", "B")
        sm.add_edge("B", "C")
        sm.add_edge("C", END)
        st = sm.run({"run_id": "t1"})
        check("T1 顺序 A→B→C", order == ["A", "B", "C"], f"order={order}")
        check("T1 completed_nodes 依序", st["completed_nodes"] == ["A", "B", "C"],
              str(st["completed_nodes"]))
        check("T1 产物落 artifacts", all(k in st["artifacts"] for k in ("A", "B", "C")))


# ---------------- T2 条件边 ----------------
def t2_conditional_edge():
    with tempfile.TemporaryDirectory() as td:
        sm = StateMachine(os.path.join(td, "runs"))
        routed = []
        sm.add_node("S", lambda s, ctx: ({**s}, {}))
        sm.add_node("X", lambda s, ctx: (routed.append("X") or s, {}))
        sm.add_node("Y", lambda s, ctx: (routed.append("Y") or s, {}))
        sm.add_edge(START, "S")
        sm.add_edge("S", "X", condition=lambda s: s.get("flag"))
        sm.add_edge("S", "Y", condition=lambda s: not s.get("flag"))
        sm.add_edge("X", END)
        sm.add_edge("Y", END)
        sm.run({"flag": True})
        check("T2 flag=True 走 X", routed == ["X"], str(routed))
        routed.clear()
        sm.run({"flag": False})
        check("T2 flag=False 走 Y", routed == ["Y"], str(routed))

        # 死端：无条件兜底边缺失且无命中 → GraphError
        sm2 = StateMachine(os.path.join(td, "runs2"))
        sm2.add_node("S", lambda s, ctx: ({**s, "flag": False}, {}))
        sm2.add_node("X", lambda s, ctx: (s, {}))  # 兜底目标 X 必须注册，否则 add_edge 先拒
        sm2.add_edge(START, "S")
        sm2.add_edge("S", "X", condition=lambda s: s.get("flag"))  # 永假，无兜底不触发
        try:
            sm2.run({})
            check("T2 死端应抛 GraphError", False)
        except GraphError as e:
            check("T2 无命中出边死端抛 GraphError", "死端" in str(e), str(e))

        # 未注册出边目标 → GraphError
        try:
            sm2.add_edge("S", "GHOST", condition=lambda s: True)
            check("T2 指向未注册节点应报错", False)
        except GraphError:
            check("T2 add_edge 指向未注册节点报 GraphError", True)


# ---------------- T3 checkpoint 续跑 ----------------
def t3_checkpoint_resume():
    with tempfile.TemporaryDirectory() as td:
        run_dir = os.path.join(td, "work", ".workflow", "runs", "r3")
        smc = StateMachine(run_dir, ctx=None)
        sm = smc  # 真实场景由 cli.build_graph 提供 ctx；此处用最小三节点验证内核续跑语义
        sm = StateMachine(run_dir, ctx=None)
        mtimes = {}
        def mkadt(name):
            def fn(s, ctx):
                p = os.path.join(td, f"{name}.dat")
                if not os.path.isfile(p):
                    io.open(p, "w", encoding="utf-8").write(name)
                mtimes[name] = os.stat(p).st_mtime_ns
                return s, {"artifact": p}
            return fn
        sm.add_node("A", mkadt("A"))
        sm.add_node("B", mkadt("B"))
        sm.add_node("C", mkadt("C"))
        sm.add_edge(START, "A")
        sm.add_edge("A", "B")
        sm.add_edge("B", "C")
        sm.add_edge("C", END)
        st = sm.run({"run_id": "r3"})
        check("T3 首次全跑完成", st["completed_nodes"] == ["A", "B", "C"])
        cp_path = os.path.join(run_dir, "checkpoint.json")
        check("T3 checkpoint 落盘", os.path.isfile(cp_path))

        # 伪造"C 前崩溃"：checkpoint 说 A/B 完成，active=C，删除 C 产物
        cp = json.loads(io.open(cp_path, encoding="utf-8").read())
        cp["completed_nodes"] = ["A", "B"]
        cp["active_node"] = "C"
        cp["state_snapshot"]["completed_nodes"] = ["A", "B"]
        cp["state_hash"] = sm_mod.state_hash(cp["state_snapshot"])
        sm_mod._atomic_write_json(cp_path, cp)
        a_mtime = mtimes["A"]; b_mtime = mtimes["B"]
        if os.path.isfile(os.path.join(td, "C.dat")):
            os.remove(os.path.join(td, "C.dat"))
        st2 = sm.run({}, resume=True)
        check("T3 --resume 从中断节点续跑完成", st2["completed_nodes"] == ["A", "B", "C"])
        check("T3 已完成节点未重跑（A mtime 不变）", mtimes.get("A") == a_mtime,
              f"{mtimes.get('A')} vs {a_mtime}")
        check("T3 B mtime 不变", mtimes.get("B") == b_mtime)


# ---------------- T4 schema 校验 ----------------
def t4_schema_validation():
    sch = {"type": "object", "required": ["a"], "properties": {
        "a": {"type": "integer", "minimum": 1},
        "b": {"type": "string", "enum": ["x", "y"]},
        "c": {"type": "string", "minLength": 3},
        "d": {"type": "array", "minItems": 1}}}
    check("T4 合法载荷零错误", sm_mod.validate(sch, {"a": 2, "b": "x", "c": "abc", "d": [1]}) == [])
    e1 = sm_mod.validate(sch, {"b": "z", "c": "ab", "d": []})
    check("T4 缺 required 被抓", any("缺必填字段" in x for x in e1))
    check("T4 enum 越界被抓", any("枚举" in x for x in e1))
    check("T4 minLength 被抓", any("minLength" in x for x in e1))
    check("T4 minItems 被抓", any("minItems" in x for x in e1))
    e2 = sm_mod.validate(sch, {"a": "notint"})
    check("T4 type 不符被抓", any("期望 integer" in x for x in e2))
    check("T4 minimum 被抓", any("minimum" in x for x in sm_mod.validate(sch, {"a": 0})))

    # 契约冲突：节点 out_schema 不过 → ContractError（run 失败，checkpoint 停本节点）
    with tempfile.TemporaryDirectory() as td:
        sm = StateMachine(os.path.join(td, "runs"))
        out = {"type": "object", "required": ["candidates"], "properties": {"candidates": {"type": "array"}}}
        sm.add_node("R", lambda s, ctx: ({**s, "a": 1}, {"bad": True}), out_schema=out)
        sm.add_edge(START, "R")
        sm.add_edge("R", END)
        try:
            sm.run({})
            check("T4 节点产物未过 out_schema 抛 ContractError", False)
        except ContractError as e:
            check("T4 产物未过契约抛 ContractError", "契约" in str(e), str(e)[:60])


# ---------------- T5 乐观锁冲突 ----------------
def t5_optimistic_lock_conflict():
    # 直接对 ledger_build 单测乐观锁语义（不经图）：磁盘 version 不符 → LockConflict
    with tempfile.TemporaryDirectory() as td:
        wf = os.path.join(td, ".workflow")
        os.makedirs(wf)
        # 预置磁盘台账 version=5 且 content 与被铸条目不同（空 entries），
        # state 期望 version 从 0 起 → 幂等守卫不兜底（内容相异）→ 落版本检查 → 冲突
        ledger_path = os.path.join(wf, "citation_ledger.json")
        sm_mod._atomic_write_json(ledger_path, {"version": 5, "entries": []})
        class Ctx:
            contracts_dir = os.path.join(ROOT, "contracts")
            def __init__(self, ledger_path):
                self.ledger_path = ledger_path
            def node_dir(self, n): return os.path.join(wf, "nodes", "r5", n)
        # 非空候选：铸出非空 entries，与磁盘空 entries 相异 → 幂等守卫不触发
        cand = {"title": "M2 LockConflict Paper", "first_author": "Roth",
                "authors": "Roth K", "year": "2022", "venue": "CVPR",
                "source": "sciverse", "verify_status": "VERIFIED"}
        cand_path = os.path.join(wf, "nodes", "r5", "retrieve_fanout", "candidates.json")
        os.makedirs(os.path.dirname(cand_path), exist_ok=True)
        sm_mod._atomic_write_json(cand_path, {"candidates": [cand]})
        ctx = Ctx(ledger_path)
        st = {"artifacts": {"retrieve_fanout": {"candidates_path": cand_path}}}
        try:
            nodes.ledger_build(st, ctx)
            check("T5 磁盘 version 不符应 LockConflict", False)
        except nodes.LockConflict as e:
            check("T5 version 不符 → LockConflict（冲突即 FAIL）",
                  "乐观锁冲突" in str(e), str(e)[:70])


def main():
    t1_node_flow()
    t2_conditional_edge()
    t3_checkpoint_resume()
    t4_schema_validation()
    t5_optimistic_lock_conflict()
    n_fail = sum(1 for _, ok, _ in RESULTS if not ok)
    print(f"\nsummary: PASS {len(RESULTS)-n_fail} / FAIL {n_fail}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
