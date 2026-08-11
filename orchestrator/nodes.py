# -*- coding: utf-8 -*-
"""nodes.py — M2 三节点：brief_freeze / retrieve_fanout / ledger_build。

契约落点（规格 §2/§3）：
  - Node A brief_freeze：冻结研究简报 → brief.json，过 brief.schema.json。
  - Node B retrieve_fanout：按 RQ×视角静态 fan-out（ThreadPoolExecutor 并行），
    每个子任务只写自己的候选落盘文件并过 candidates.schema.json；merge 屏障做
    append 合并（reducer 语义）+ 去重，产出 candidates.json。
  - Node C ledger_build：**单写者**。候选 → .workflow/citation_ledger.json，
    条目过 ledger_entry.schema.json + citation_ledger.validate_entries；
    乐观锁：写前比对磁盘台账 version 与 state.ledger.version，不符即冲突 FAIL
    （M2 不自动合并）。「门禁不过回 Node B」用条件边（见 cli.build_graph），
    不在节点内抛异常当控制流。

幂等守卫（续跑/重放安全）：节点产物已存在且内容等价 → 跳过副作用，直接回读。
"""
import hashlib
import io
import json
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor

from .state_machine import validate, load_schema, _atomic_write_json


def _sha256_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _read_json(path):
    return json.loads(io.open(path, encoding="utf-8").read())


def _write_json_if_changed(path, data):
    """幂等落盘：内容相同则不动（返回 False），否则原子写（返回 True）。"""
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if os.path.isfile(path) and io.open(path, encoding="utf-8").read() == text:
        return False
    _atomic_write_json(path, data)
    return True


# ---------------- Node A：简报冻结 ----------------

def brief_freeze(state, ctx):
    """冻结研究简报：校验 brief.schema → 规范落盘 brief.json → 记 sha256 进 state。"""
    brief = state.get("brief_input")
    if not isinstance(brief, dict):
        raise ValueError("state.brief_input 缺失或非对象——Node A 需要冻结前的简报输入")
    errs = validate(load_schema(ctx.contracts_dir, "brief"), brief, path="$brief")
    if errs:
        raise ValueError("简报未过 brief.schema：\n" + "\n".join(errs))
    node_dir = ctx.node_dir("brief_freeze")
    path = os.path.join(node_dir, "brief.json")
    _write_json_if_changed(path, brief)  # 幂等：同内容不重写
    digest = _sha256_text(io.open(path, encoding="utf-8").read())
    return state, {"brief_path": path, "sha256": digest,
                   "rq_count": len(brief["rq"])}


# ---------------- Node B：检索 fan-out（静态，并行） ----------------

def _default_seed_retriever(ctx, subtask):
    """默认离线检索器：读 seeds_dir/<subtask_id>.json（确定性、可复现）。
    真实 sciverse/arxiv 检索由宿主注入 ctx.retriever 替换——编排层不直连数据源。
    返回候选 list（dict）。"""
    p = os.path.join(ctx.seeds_dir, subtask["id"] + ".json")
    if not os.path.isfile(p):
        raise FileNotFoundError(f"子任务 {subtask['id']} 缺种子候选文件：{p}")
    data = _read_json(p)
    cands = data.get("candidates", data if isinstance(data, list) else [])
    if ctx.subtask_delay:  # 测试用：模拟检索耗时，让并行可观测
        time.sleep(ctx.subtask_delay)
    return cands


def _run_subtask(ctx, subtask, schema):
    """单个子任务：幂等守卫（候选文件已存在即回读）→ 检索 → 验 schema → 落盘。"""
    out_path = os.path.join(ctx.node_dir("retrieve_fanout"),
                            subtask["id"] + ".candidates.json")
    if os.path.isfile(out_path):
        data = _read_json(out_path)  # 已存在即跳过副作用（续跑不重查）
        return subtask["id"], data["candidates"], True
    with ctx.concurrency_lock:  # 并行度观测（验收：fan-out 确为并行）
        ctx.concurrency += 1
        ctx.max_concurrency = max(ctx.max_concurrency, ctx.concurrency)
    try:
        retriever = ctx.retriever or (lambda st: _default_seed_retriever(ctx, st))
        cands = retriever(subtask)
    finally:
        with ctx.concurrency_lock:
            ctx.concurrency -= 1
    payload = {"subtask": subtask["id"], "rq": subtask["rq"],
               "perspective": subtask["perspective"], "candidates": cands}
    errs = validate(schema, payload, path=f"$candidates[{subtask['id']}]")
    if errs:
        raise ValueError(f"子任务 {subtask['id']} 候选未过 candidates.schema：\n"
                         + "\n".join(errs))
    _write_json_if_changed(out_path, payload)
    return subtask["id"], cands, False


def retrieve_fanout(state, ctx):
    """按 RQ×视角静态 fan-out：并行子任务 → 各自候选落盘 → merge 屏障 append 合并去重。"""
    brief = _read_json(state["artifacts"]["brief_freeze"]["brief_path"])
    schema = load_schema(ctx.contracts_dir, "candidates")
    subtasks = []
    for rq in brief["rq"]:
        for persp in rq.get("perspectives") or ["default"]:
            subtasks.append({"id": f"{rq['id']}__{persp}",
                             "rq": rq["id"], "perspective": persp})
    ctx.concurrency, ctx.max_concurrency = 0, 0
    ctx.concurrency_lock = threading.Lock()
    reused, fresh = 0, 0
    with ThreadPoolExecutor(max_workers=ctx.max_workers) as pool:
        futures = [pool.submit(_run_subtask, ctx, st, schema) for st in subtasks]
        results = [f.result() for f in futures]  # 屏障：任一子任务失败整节点失败
    # reducer 合并：按子任务静态顺序 append（确定性），按 (title, first_author) 去重
    merged, seen = [], set()
    for _st, cands, was_reused in results:
        reused += was_reused
        fresh += not was_reused
        for c in cands:
            key = (str(c.get("title", "")).strip().casefold(),
                   str(c.get("first_author", "")).strip().casefold())
            if key not in seen:
                seen.add(key)
                merged.append(c)
    node_dir = ctx.node_dir("retrieve_fanout")
    merged_path = os.path.join(node_dir, "candidates.json")
    _write_json_if_changed(merged_path, {"candidates": merged})
    return state, {"candidates_path": merged_path, "count": len(merged),
                   "subtasks": len(subtasks), "subtasks_reused": reused,
                   "subtasks_fresh": fresh,
                   "max_concurrency": ctx.max_concurrency}


# ---------------- Node C：单写铸账（乐观锁） ----------------

class LockConflict(Exception):
    """乐观锁冲突：磁盘台账 version 与 state 期望不符——M2 冲突即 FAIL，不自动合并。"""


# 候选 → 台账条目的字段映射（对齐 citation_ledger.py 台账 schema）
_ENTRY_FIELDS = ("first_author", "authors", "year", "title", "venue",
                 "verify_status", "aliases", "role", "criteria", "note",
                 "doi", "volume", "issue", "pages", "unique_id", "doc_id", "key")


def ledger_build(state, ctx):
    """候选 → 单写铸账。乐观锁 + 双校验（ledger_entry.schema + validate_entries）。

    不过 validate 时不抛异常：记 state["ledger"]["valid"]=False，由条件边路由
    回 Node B（router 纯函数）。仅在乐观锁冲突时抛 LockConflict（= FAIL）。
    """
    from . import citation_api  # 延迟导入：定位 skills/scripts/citation_ledger.py
    candidates = _read_json(state["artifacts"]["retrieve_fanout"]
                            ["candidates_path"])["candidates"]
    entries = []
    for i, c in enumerate(candidates):
        e = {"id": i + 1}
        for f in _ENTRY_FIELDS:
            if c.get(f) not in (None, ""):
                e[f] = c[f]
        e.setdefault("verify_status", "UNVERIFIED")
        entries.append(e)

    schema = load_schema(ctx.contracts_dir, "ledger_entry")
    schema_errs = []
    for e in entries:
        schema_errs.extend(validate(schema, e, path=f"$ledger[{e['id']}]"))

    ledger_path = ctx.ledger_path
    expected = int(state.get("ledger", {}).get("version", 0))
    new_payload = {"version": expected + 1, "entries": entries}

    if os.path.isfile(ledger_path):
        disk = _read_json(ledger_path)
        disk_version = int(disk.get("version", 0))
        if disk.get("entries") == entries:
            # 幂等守卫：盘上已是目标内容（崩溃发生在写后/记账前）→ 采用盘版本，不重写
            state["ledger"] = {"version": disk_version, "path": ledger_path,
                               "valid": True, "retries": state.get("ledger", {}).get("retries", 0)}
            return state, {"ledger_path": ledger_path, "entries": len(entries),
                           "version": disk_version, "idempotent_skip": True}
        if disk_version != expected:
            raise LockConflict(
                f"铸账乐观锁冲突：磁盘 version={disk_version}，state 期望 {expected}"
                f"——他者已写台账；M2 冲突即 FAIL，不自动合并")

    fails, warns = citation_api.validate_entries(entries)
    led = state.setdefault("ledger", {})
    if schema_errs or fails:
        led.update({"valid": False, "retries": led.get("retries", 0) + 1,
                    "fails": schema_errs + fails})
        return state, {"ledger_path": ledger_path, "valid": False,
                       "fails": schema_errs + fails}

    _atomic_write_json(ledger_path, new_payload)  # 单写者落盘
    led.update({"version": expected + 1, "path": ledger_path, "valid": True})
    return state, {"ledger_path": ledger_path, "entries": len(entries),
                   "version": expected + 1, "valid": True, "warns": warns}
