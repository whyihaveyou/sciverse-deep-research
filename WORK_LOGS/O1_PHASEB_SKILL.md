---
title: "O1 Phase B：SKILL 措辞改造——阶段由工件连接、换上下文按工件恢复续跑"
tags: [o1, checkpoint, skill, context-budget]
status: active
created: 2026-08-10
---

# O1 Phase B（SKILL 措辞改造）

承接 Phase A（stage_contract.py 底盘验证通过、PR#12 已合并 main@1135a5c）。Phase B 把 O1 价值落进 SKILL：改掉"单执行者同上下文顺序完成"的强绑定，改为"阶段由盘上工件连接、换上下文按工件恢复续跑"。

## 改动（skills/sciverse-deep-research/SKILL.md 第 37 行）

原「单执行者约束（关键）」（要求同一执行者在同一上下文内顺序完成全部阶段，长综述上下文漂移的根因之一）改为三段：

1. **阶段由盘上工件连接**：台账/键值草稿/切片脚手架/checkpoint 摘要是阶段间唯一接口；确定性仍由 `citation_ledger.py compile` 从同一台账一次铸造，**由盘上文件保证、与上下文实例数无关**；交付/7 维/O2 门禁都以盘上工件为输入。续跑不需要平台级编排——读到本 skill 的 agent 无论从哪个上下文进入都是编排器。
2. **收束**：阶段完即落下游工件（铸账 → validate；综合 → draft+切片）；被 `stage_contract.py budget` 判定超预算 → 先落 checkpoint 摘要，不得带病往下滚。
3. **续跑**：新阶段/换上下文先 `stage_contract.py check` 校验工件齐备、从盘恢复、只加载本单元所需、不重演历史；`resume-idempotent` 验证不漂移。明确"不存在必须一口气跑完的负担"，收敛由门禁判据驱动。

并保留**单写红线**：台账/草稿是单写事实源，续跑是顺序交接，不允许多执行者并发改同一台账/草稿，绕过 validate/compile 改编号仍是硬错误（守住台账一致性与门禁可执行性这个旧约束的真实内核）。

## 验证

- 未动任何代码/门禁/工具，仅 SKILL 措辞改写。
- `run_regression.py --slow`：**PASS 27 / FAIL 0**，无回退。

## 状态

- [x] Phase A 轻量验证（已合并）
- [x] Phase B SKILL 措辞改造（本 PR）
- [ ] 合并后用我们侧同模型同 prompt 重跑 spectral 终验（Lili 排）
