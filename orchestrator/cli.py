# -*- coding: utf-8 -*-
"""cli.py — M2 编排管线入口：A(brief_freeze) → B(retrieve_fanout) → C(ledger_build)。

用法：
  python3 -m orchestrator.cli run --workdir <dir> --brief brief.json \
      --seeds-dir <dir> [--run-id X] [--resume] [--max-workers N]
  python3 -m orchestrator.cli --selftest     # 离线确定性自检（零网络零依赖）

图（规格 §0/§1.1）：
  START → brief_freeze → retrieve_fanout → ledger_build → END
                                               │ 门禁不过（ledger invalid 且重试<1）
                                               └──条件边──→ retrieve_fanout（纯函数 router）
"""
import argparse
import io
import json
import os
import sys
import tempfile
import time

from .state_machine import StateMachine, END, validate, state_hash, _atomic_write_json
from . import nodes

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(_HERE)
CONTRACTS_DIR = os.path.join(REPO_ROOT, "contracts")


class Ctx:
    """节点执行上下文（编排层透传，节点只读配置、写自己的产物目录）。"""

    def __init__(self, workdir, run_id, seeds_dir=None, max_workers=4,
                 retriever=None, subtask_delay=0.0, contracts_dir=CONTRACTS_DIR):
        self.workdir = os.path.abspath(workdir)
        self.run_id = run_id
        self.seeds_dir = seeds_dir
        self.max_workers = max_workers
        self.retriever = retriever          # 可注入真实检索器；默认离线种子
        self.subtask_delay = subtask_delay  # 测试用：模拟子任务耗时
        self.contracts_dir = contracts_dir
        self.ledger_path = os.path.join(self.workflow_dir, "citation_ledger.json")

    @property
    def workflow_dir(self):
        return os.path.join(self.workdir, ".workflow")

    @property
    def run_dir(self):
        return os.path.join(self.workflow_dir, "runs", self.run_id)

    def node_dir(self, node):
        return os.path.join(self.workflow_dir, "nodes", self.run_id, node)


def build_graph(ctx):
    """装配 M2 图。ledger 校验回退走条件边（router 纯函数），带重试上限防死循环。"""
    sm = StateMachine(ctx.run_dir, ctx)
    sm.add_node("brief_freeze", nodes.brief_freeze)
    sm.add_node("retrieve_fanout", nodes.retrieve_fanout)
    sm.add_node("ledger_build", nodes.ledger_build)
    sm.add_edge(StateMachine.START, "brief_freeze")
    sm.add_edge("brief_freeze", "retrieve_fanout")
    sm.add_edge("retrieve_fanout", "ledger_build")
    sm.add_edge("ledger_build", END,
                condition=lambda s: s.get("ledger", {}).get("valid", False))
    sm.add_edge("ledger_build", "retrieve_fanout",
                condition=lambda s: (not s.get("ledger", {}).get("valid", False))
                and s.get("ledger", {}).get("retries", 0) <= 1)
    return sm


def cmd_run(args):
    brief = json.loads(io.open(args.brief, encoding="utf-8").read())
    run_id = args.run_id or time.strftime("run-%Y%m%d-%H%M%S")
    ctx = Ctx(args.workdir, run_id, seeds_dir=args.seeds_dir,
              max_workers=args.max_workers, subtask_delay=args.subtask_delay)
    sm = build_graph(ctx)
    initial = {"run_id": run_id, "brief_input": brief}
    state = sm.run(initial, resume=args.resume)
    led = state.get("ledger", {})
    print(json.dumps({
        "run_id": run_id,
        "completed_nodes": state["completed_nodes"],
        "checkpoint": os.path.join(ctx.run_dir, "checkpoint.json"),
        "ledger": {"path": led.get("path"), "version": led.get("version"),
                   "valid": led.get("valid")},
        "candidates": state["artifacts"]["retrieve_fanout"]["count"],
        "max_concurrency": state["artifacts"]["retrieve_fanout"]["max_concurrency"],
    }, ensure_ascii=False, indent=2))
    return 0 if led.get("valid") else 1


# ---------------- selftest（离线确定性） ----------------

def _seed(path, cands):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    io.open(path, "w", encoding="utf-8").write(
        json.dumps({"candidates": cands}, ensure_ascii=False, indent=2))


_C1 = {"title": "Towards Total Recall in Industrial Anomaly Detection",
       "first_author": "Roth", "authors": "Roth K, et al.", "year": "2022",
       "venue": "CVPR", "verify_status": "VERIFIED", "aliases": ["PatchCore"],
       "source": "sciverse"}
_C2 = {"title": "EfficientAD: Accurate Visual Anomaly Detection",
       "first_author": "Batzner", "authors": "Batzner K, et al.", "year": "2024",
       "venue": "WACV", "verify_status": "VERIFIED", "aliases": ["EfficientAD"],
       "source": "sciverse"}
_C3 = {"title": "D3Lite-MES: Lightweight Defect Detection, with Deployment",
       "first_author": "Lin", "authors": "Lin J, Wang Q", "year": "2025",
       "venue": "IEEE TII", "verify_status": "MINOR", "aliases": ["D3Lite-MES"],
       "source": "arxiv"}

_BRIEF = {"schema_version": "m2", "topic": "自检专题",
          "rq": [{"id": "rq1", "question": "问题一",
                  "perspectives": ["statphys", "networks"]},
                 {"id": "rq2", "question": "问题二",
                  "perspectives": ["statphys", "networks"]}],
          "sources": ["sciverse", "arxiv"],
          "output_format": "survey", "audience": "selftest"}


def selftest():
    ok = True

    def expect(cond, label):
        nonlocal ok
        print(("PASS  " if cond else "FAIL  ") + label)
        ok = ok and cond

    # ---- validate() 子集校验器 ----
    sch = {"type": "object", "required": ["a"],
           "properties": {"a": {"type": "integer", "minimum": 1},
                          "b": {"type": "string", "enum": ["x", "y"]}}}
    expect(validate(sch, {"a": 1, "b": "x"}) == [], "validate：合法载荷零错误")
    errs = validate(sch, {"b": "z"})
    expect(any("缺必填字段" in e for e in errs), "validate：缺 required 被抓")
    expect(any("枚举" in e for e in errs), "validate：enum 越界被抓")
    expect(validate({"type": "array", "minItems": 2}, [1]) != [],
           "validate：minItems 被抓")

    with tempfile.TemporaryDirectory() as td:
        seeds = os.path.join(td, "seeds")
        # 4 子任务（2 RQ × 2 视角），候选有交叠（rq1/rq2 statphys 都含 _C1）→ 验去重
        _seed(os.path.join(seeds, "rq1__statphys.json"), [_C1, _C2])
        _seed(os.path.join(seeds, "rq1__networks.json"), [_C3])
        _seed(os.path.join(seeds, "rq2__statphys.json"), [_C1, _C3])
        _seed(os.path.join(seeds, "rq2__networks.json"), [_C2])
        brief_path = os.path.join(td, "brief.json")
        io.open(brief_path, "w", encoding="utf-8").write(json.dumps(_BRIEF))

        ctx = Ctx(td, "selftest-run", seeds_dir=seeds, max_workers=4,
                  subtask_delay=0.05)
        sm = build_graph(ctx)
        state = sm.run({"run_id": "selftest-run", "brief_input": _BRIEF})

        expect(state["completed_nodes"] == ["brief_freeze", "retrieve_fanout",
                                            "ledger_build"],
               "A→B→C 顺序跑通")
        cp = json.loads(io.open(os.path.join(ctx.run_dir, "checkpoint.json"),
                                encoding="utf-8").read())
        expect(cp["completed_nodes"] == state["completed_nodes"]
               and cp["active_node"] == END and cp["version"] > 0,
               "checkpoint 落盘：completed+active+version 齐备")
        art_b = state["artifacts"]["retrieve_fanout"]
        expect(art_b["subtasks"] == 4 and art_b["subtasks_fresh"] == 4,
               "fan-out 静态清单 = RQ×视角 = 4 子任务")
        expect(art_b["max_concurrency"] >= 2,
               f"fan-out 确为并行（max_concurrency={art_b['max_concurrency']}）")
        expect(art_b["count"] == 3, "merge 屏障 append 合并 + 去重（4 子任务 6 候选 → 3 篇）")
        ledger = json.loads(io.open(ctx.ledger_path, encoding="utf-8").read())
        expect(ledger["version"] == 1 and len(ledger["entries"]) == 3,
               "铸账落盘：version=1、3 条目")
        from . import citation_api
        fails, _ = citation_api.validate_entries(ledger["entries"])
        expect(not fails, "台账过 citation_ledger.validate_entries（FAIL 0）")
        expect([e["id"] for e in ledger["entries"]] == [1, 2, 3],
               "条目 id 由单写者按确定性顺序铸造")

        # ---- 断点续跑：伪造「C 前崩溃」→ --resume 只重跑 C ----
        brief_mtime = os.stat(state["artifacts"]["brief_freeze"]["brief_path"]).st_mtime_ns
        cand_mtime = os.stat(art_b["candidates_path"]).st_mtime_ns
        os.remove(ctx.ledger_path)
        cp2 = json.loads(io.open(os.path.join(ctx.run_dir, "checkpoint.json"),
                                 encoding="utf-8").read())
        cp2["completed_nodes"] = ["brief_freeze", "retrieve_fanout"]
        cp2["active_node"] = "ledger_build"
        cp2["state_snapshot"]["completed_nodes"] = ["brief_freeze",
                                                    "retrieve_fanout"]
        cp2["state_snapshot"].pop("ledger", None)
        cp2["state_hash"] = state_hash(cp2["state_snapshot"])
        _atomic_write_json(os.path.join(ctx.run_dir, "checkpoint.json"), cp2)
        state2 = sm.run({}, resume=True)
        expect(os.path.isfile(ctx.ledger_path), "--resume：台账被续跑重建")
        ledger2 = json.loads(io.open(ctx.ledger_path, encoding="utf-8").read())
        expect(ledger2["entries"] == ledger["entries"],
               "--resume：续跑产物与全跑逐条一致（盘上工件保证确定性）")
        expect(os.stat(state["artifacts"]["brief_freeze"]["brief_path"]).st_mtime_ns == brief_mtime
               and os.stat(art_b["candidates_path"]).st_mtime_ns == cand_mtime,
               "--resume：已完成节点未重跑（产物 mtime 不变）")

        # ---- 乐观锁冲突：他者抢先写账（内容不同 + version 不符）→ FAIL ----
        bad = {"version": 99, "entries": ledger2["entries"][:-1]}  # 内容相异，幂等守卫不兜底
        _atomic_write_json(ctx.ledger_path, bad)
        try:
            sm.run({"run_id": "selftest-run", "brief_input": _BRIEF})
            expect(False, "乐观锁：磁盘 version 不符必须 LockConflict")
        except nodes.LockConflict:
            expect(True, "乐观锁：磁盘 version 不符 → LockConflict（冲突即 FAIL）")

        # ---- 条件边回退：C 不过 → router 回 B（纯函数）， retry 上限后死端报错 ----
        bad_seed_dir = os.path.join(td, "badseeds")
        _seed(os.path.join(bad_seed_dir, "rq1__statphys.json"),
              [dict(_C1, verify_status="UNVERIFIABLE")])  # 不得入账的状态
        _seed(os.path.join(bad_seed_dir, "rq1__networks.json"), [_C2])
        _seed(os.path.join(bad_seed_dir, "rq2__statphys.json"), [_C3])
        _seed(os.path.join(bad_seed_dir, "rq2__networks.json"), [_C2])
        ctx3 = Ctx(os.path.join(td, "w2"), "bad-run",  # 独立 workdir，避开上面的台账
                   seeds_dir=bad_seed_dir, max_workers=2)
        sm3 = build_graph(ctx3)
        from .state_machine import GraphError
        try:
            sm3.run({"run_id": "bad-run", "brief_input": _BRIEF})
            expect(False, "门禁不过应路由回 B 并最终死端报错")
        except GraphError as e:
            expect("死端" in str(e), "条件边：ledger 不过 → 回 B → 重试上限 → 死端 FAIL（非异常控制流）")

    print("SELFTEST " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


def main(argv=None):
    ap = argparse.ArgumentParser(description="M2 最小编排原型：A 简报冻结 → B 检索 fan-out → C 单写铸账")
    ap.add_argument("--selftest", action="store_true")
    sub = ap.add_subparsers(dest="cmd")
    p = sub.add_parser("run")
    p.add_argument("--workdir", default=".")
    p.add_argument("--brief", required=True, help="冻结前简报 JSON（过 brief.schema）")
    p.add_argument("--seeds-dir", required=True, help="子任务种子候选目录 <subtask_id>.json")
    p.add_argument("--run-id", default=None)
    p.add_argument("--resume", action="store_true", help="从 checkpoint 第一个未完成节点续跑")
    p.add_argument("--max-workers", type=int, default=4)
    p.add_argument("--subtask-delay", type=float, default=0.0)
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.cmd == "run":
        return cmd_run(args)
    ap.error("缺少子命令 run 或 --selftest")
    return 2


if __name__ == "__main__":
    sys.exit(main())
