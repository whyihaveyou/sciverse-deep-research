---
title: "O1 Phase A 轻量验证：续跑确定性底盘确认"
tags: [o1, context-budget, checkpoint, verification]
status: active
created: 2026-08-10
---

# O1 Phase A 轻量验证（stage_contract.py）

承接 P5 计划（PLANS/P5_CONTEXT_BUDGET_CHECKPOINT.md）的 Phase A：先轻量验证「每阶段预算 + 工件边界 + 收束续跑」真有收益、且不破坏 compile/门禁确定性，再进 Phase B 全量改 SKILL 措辞。

## 交付

新增 `scripts/stage_contract.py`（stdlib 零依赖），三个子命令作为阶段单元契约的可执行载体：

1. `check <workdir>` —— 阶段单元入口工件边界：续跑必须从盘上工件（`citation_ledger.json` + `draft.md`）恢复；台账必须过 validate 才准开工（不得绕过直接改编号）；草稿 [@键]残留给 WARN。
2. `resume-idempotent <workdir>` —— **续跑确定性实证**：从同一盘上工件跑两次 compile，逐字节一致 = 换上下文续跑不会漂移（确定性由盘上文件保证，与上下文实例数无关）。这正是治 10.7M token 上下文漂移的底盘。
3. `budget <budget.json> <workdir>` —— 预算契约：阶段上限合法校验；记账超限（cost_log）→ exit 1 触发 checkpoint 续跑，不得带病往下滚；工件齐备照查。

## 实证结果（真实 demo）

- dft-kL / space-compute 两 demo：`check` 工件契约 PASS；`resume-idempotent` 两次 compile **逐字节一致**（7673 / 9203 字符）——续跑确定性成立。
- `budget` 三态：合法未超限 → PASS；记账超限（synthesis 999999 > 800）→ FAIL 触发；非法预算上限（-5）→ FAIL。
- 全量回归 `run_regression.py --slow`：**PASS 27 / FAIL 0**（原 24 + 新增 3 个 Phase A 回归用例），无破坏。

## 结论（Phase A 判定）

盘上工件足以支撑"换上下文续跑不漂移"——compile 幂等，确定性由盘上文件保证。机制可行、有收益、不破坏确定性链路，**Phase A 通过**，可进 Phase B（改 SKILL'单执行者同上下文'强绑定为'工件连接、换上下文按工件恢复'）。

## 状态

- [x] Phase A 轻量验证
- [ ] Phase B SKILL 措辞 + 重跑终验
