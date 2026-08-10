---
title: "O2 机械门禁：数学裸残留 + 非标准术语 + 交付干净 md"
tags: [o2, structure-optimization, check-gates, delivery]
status: active
created: 2026-08-10
---

# O2 机械门禁落地（审查员暂代实现位）

承接 @资深产品经理_Lili 委派（Jake 三次零产出被移出实现位，M3 已证可靠的审查员接手）。O2 规格层第一刀（交付即写作纪律写进 SKILL，PR#10）已合，本项完成其**机械门禁**部分。

## 做了什么

全部落在 `skills/sciverse-deep-research/scripts/check_report.py`，沿用现有 check 函数范式，挂进 `run_checks` 检查列表：

1. `check_math_residue`（检查项 9）——正文未用 `$...$` 包裹的裸 `_`/`^`（如 `d_s`、`x^2`、`P_ii`、`C_ij`）= **FAIL**。跳过代码栅栏与已归档 `$..$` 数学块，不误伤已规范数学（红线：安全网不对自己人拉警报）。
2. `check_terminology`（检查项 10）——`--terms <json>` 可配小词表，`fail` 词命中 = FAIL、`warn` 词命中 = WARN。默认表保守（`相变阶次`→WARN 进邱/学报偏好），真正承重靠按学科配置。
3. `--export-clean <path>`——交付默认出数学干净 md：复用 `md_to_pdf.normalize`（弯引号 + 纯文本数学焊接）产出交付视图；`final.md` 仍是 compile 的唯一事实源，不改引用编号/参考文献，不破坏 compile/check_report 确定性链路。

SKILL.md 交付编译阶段补充：check_report 验收命令清单并入 O2 两项门禁；新增"交付默认出数学干净 md"小节。

## 存量交付物升级（门禁承重的直接证据）

O2 门禁一上就抓到存量交付物确实含裸公式（正是邱指的不可读）：
- `examples/dft-kL-demo/.workflow/final.md`：8 处（`C_ij`、`v_L/v_t/v_s`、`v_g`）
- `examples/space-compute-demo/.workflow/final.md`：1 处（`e_id`）

三个 demo 的 final.md 均经 `--export-clean` 覆盖升级为数学干净版（dft、space-compute、spectral-dimension），check 后全部 FAIL 0 / WARN 0。

## 验证

- `check_report.py --selftest`：SELFTEST PASS（新增 6 条 O2 用例全过）
- `run_regression.py --slow`：**PASS 24 / FAIL 0** 全绿

## 下一步

交分支给 Lili 验收合并。O1（P5 上下文预算 + 阶段 checkpoint，架构级）按交代另分支谨慎推进，先轻量验证再全量。
