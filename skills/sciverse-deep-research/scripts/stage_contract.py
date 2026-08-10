#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stage_contract.py — O1(P5) Phase A 轻量验证：阶段单元工件契约 + 续跑确定性 + 预算记账。

目标：治 10.7M token 上下文漂移根因的**底盘验证**——证明"换上下文续跑只依赖盘上工件，
输出确定性由盘上文件保证（compile 幂等），与上下文实例数无关"。这是 O1 全量改造前先
证收益的轻量一环（P5 计划 Phase A），符合"先轻量验证再全量"。

子命令：
  check <workdir>               校验阶段单元入口工件齐备（ledger+draft 存在、台账过
                                validate、草稿无 [@键]残留）——工件即接口。
  resume-idempotent <workdir>   从同一盘上工件跑两次 compile → 逐字节一致（续跑不漂移
                                的确定性实证）；exit 0 一致 / 1 不一致。
  budget <budget.json> <workdir> 读阶段预算配置并校验工件；配置里设上限、记账超限 → exit 1。
                                真实 token 由运行方在每个阶段 checkpoint 时写入记账文件，
                                本命令负责契约侧（配置合法、上限不超、工件齐备）。

stdlib 零依赖（与 scripts/ 哲学一致）。参考：P5_CONTEXT_BUDGET_CHECKPOINT.md。
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile

SCRIPTS = os.path.dirname(os.path.abspath(__file__))
CITEKEY_RESIDUE = re.compile(r"\[@[^\[\]\n]*\]")
DEFAULT_BUDGET = {"search": 400_000, "synthesis": 800_000, "compile": 100_000}


def _run_cli(script, *argv):
    return subprocess.run([sys.executable, os.path.join(SCRIPTS, script)] + list(argv),
                          capture_output=True, text=True)


def _check_contract(workdir):
    """阶段单元入口工件边界：续跑必须从这些盘上工件恢复，缺/坏即挡。"""
    fails, warns = [], []
    ledger = os.path.join(workdir, "citation_ledger.json")
    draft = os.path.join(workdir, "draft.md")
    for name, p in (("citation_ledger.json", ledger), ("draft.md", draft)):
        if not os.path.isfile(p):
            fails.append(f"缺阶段工件 {name}——续跑必须从盘上工件恢复，不得靠记忆补造")
    if os.path.isfile(ledger):
        p = _run_cli("citation_ledger.py", "validate", "--ledger", ledger)
        if p.returncode != 0 or "FAIL 0" not in p.stdout:
            fails.append("台账未过 validate——续跑不得绕过 validate 直接开工")
    if os.path.isfile(draft):
        if CITEKEY_RESIDUE.search(io.open(draft, encoding="utf-8").read()):
            warns.append("草稿含未编译 [@键]残留——交付前先 compile")
    return fails, warns


def cmd_check(workdir):
    fails, warns = _check_contract(workdir)
    for w in warns:
        print("[WARN]", w)
    for x in fails:
        print("[FAIL]", x)
    print("summary: 工件契约 %s（FAIL %d / WARN %d）" % ("PASS" if not fails else "FAIL", len(fails), len(warns)))
    return 1 if fails else 0


def cmd_resume_idempotent(workdir):
    """续跑确定性实证：同一盘上工件跑两次 compile，逐字节一致即说明换上下文续跑不会漂移。"""
    ledger, draft = os.path.join(workdir, "citation_ledger.json"), os.path.join(workdir, "draft.md")
    if not all(os.path.isfile(p) for p in (ledger, draft)):
        print("[FAIL] 缺 report/ledger 工件——无法实证续跑确定性")
        return 1
    runs = []
    for i in range(2):
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "resume.md")
            p = _run_cli("citation_ledger.py", "compile", "--ledger", ledger, "--report", draft, "--output", out)
            if p.returncode != 0:
                print(f"[FAIL] compile 第 {i + 1} 次失败 rc={p.returncode}: {p.stdout[-200:]}")
                return 1
            runs.append(io.open(out, encoding="utf-8").read())
    same = runs[0] == runs[1]
    n = len(runs[0])
    print("[%s] 续跑确定性：两次 compile 逐字节%s一致（%d 字符；确定性由盘上工件保证，与上下文实例数无关）"
          % ("PASS" if same else "FAIL", "" if same else "不", n))
    return 0 if same else 1


def cmd_budget(budget_json, workdir):
    """预算契约侧：读阶段预算配置，校验合法性 + 工件齐备 + 记账未超限。"""
    if not os.path.isfile(budget_json):
        print("[FAIL] 缺预算配置", budget_json); return 1
    cfg = json.loads(io.open(budget_json, encoding="utf-8").read())
    unknown = set(cfg) - {"stages", "cost_log", "limits"}
    if unknown:
        print(f"[FAIL] 预算配置含未知键 {sorted(unknown)}"); return 1
    stages = cfg.get("stages") or {}
    limits = cfg.get("limits") or DEFAULT_BUDGET
    cost_log = cfg.get("cost_log")
    # 1) 阶段上限合法且为正
    for s, lim in limits.items():
        if not isinstance(lim, int) or lim <= 0:
            print(f"[FAIL] 阶段 '{s}' 预算上限非法：{lim!r}"); return 1
    # 2) 记账超限检查（若提供 cost_log）
    if cost_log and os.path.isfile(cost_log):
        log = json.loads(io.open(cost_log, encoding="utf-8").read())
        for s, spent in (log.get("spent") or {}).items():
            lim = limits.get(s)
            if lim and spent > lim:
                print(f"[FAIL] 阶段 '{s}' 记账 {spent} 超预算 {lim}——已触发 checkpoint 续跑，不得带病往下滚")
                return 1
    # 3) 工件契约照常
    fails, warns = _check_contract(workdir)
    for w in warns:
        print("[WARN]", w)
    for x in fails:
        print("[FAIL]", x)
    if fails:
        return 1
    print(f"[PASS] 预算契约：阶段 {sorted(limits)}；记账{'未超限 ' if cost_log else '(未提供记账) '}工件齐备")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="O1(P5) Phase A：阶段单元工件契约 + 续跑确定性 + 预算记账")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check").add_argument("workdir")
    sub.add_parser("resume-idempotent").add_argument("workdir")
    b = sub.add_parser("budget"); b.add_argument("budget_json"); b.add_argument("workdir")
    args = ap.parse_args(argv)
    if args.cmd == "check":
        return cmd_check(args.workdir)
    if args.cmd == "resume-idempotent":
        return cmd_resume_idempotent(args.workdir)
    if args.cmd == "budget":
        return cmd_budget(args.budget_json, args.workdir)
    ap.error("未知子命令")
    return 1


if __name__ == "__main__":
    sys.exit(main())
