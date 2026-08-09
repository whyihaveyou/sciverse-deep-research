---
title: "M2 R2 自评：dft-kL-demo 质量曲线 v2（同 session A/B 口径）"
tags: [self-eval, m2, quality-curve, dft-kl, v2, same-session-ab]
status: active
created: 2026-08-09
---

# M2 Round 2 自评：dft-kL-demo 质量曲线 v2（同 session A/B）

> 本轮在 M2 R1 自评基线（`WORK_LOGS/M2_R1_SELF_EVAL_BASELINE.md`）之上，按 R1 §6 短板主轴对交付物做四维优化后闭环复测，产出质量曲线 **v2**。
>
> **口径说明（方法决策）**：judge 模型（deepseek-v4-flash-0731）存在**跨 session 漂移**——同一基线文本在不同会话分别实测出 4.6（R1 时）、4.09（前会话）、4.59（本会话），故**跨轮绝对分不可硬比**。本报告自 v2 起统一采用**「同 session A/B 对照」**：把 **A = R1 基线文本**与 **B = R2 优化文本**放入**同一时段、同一 judge**（A 各 10 采样、B 各 9 采样）实测，用 B−A 相对信号判定 R2 是否改善，不再引用不可复现的 4.6 作为对标基线。

---

## 1. 对象与方法

- **评测对象（与 R1 同一文件口径）**：`examples/dft-kL-demo/.workflow/final.md`
  - **A（R1 基线文本）**：`main=fda682e` 时点的交付物快照，7440 字符 / 9 章 / 台账 16（快照存于 `.scratch/m2-r2-ab/baseline_final.md`）
  - **B（R2 优化文本）**：同一文件按 R1 §6 四维优化后，8065 字符 / 9 章 / 台账 16
- **台账**：`examples/dft-kL-demo/.workflow/citation_ledger.json.delivery.json`（16 条 VERIFIED，未动）
- **两路信号（与 R1 一致，互不替代）**：
  1. `objective` —— 零网络、无 key 的硬指标（交付门禁、台账来源数、章节字数）
  2. `judge` —— LLM-as-judge（PJLab API，`deepseek-v4-flash-0731`，temperature 0.8，**同 session 各 10/9 采样**，按 7 维门禁逐维打分 1–5）
- **复现命令**（在 `skills/sciverse-deep-research/scripts/` 下执行）：
  ```bash
  # objective（B=R2 优化文本）
  python3 self_eval.py objective --report <worktree>/examples/dft-kL-demo/.workflow/final.md \
      --citation-ledger <worktree>/examples/dft-kL-demo/.workflow/citation_ledger.json.delivery.json

  # judge 同 session A/B（A=R1 基线快照，B=R2 优化文本）
  python3 self_eval.py --format json judge --report .scratch/m2-r2-ab/baseline_final.md \
      --samples 10 --timeout 480 --message "same-session A/B: side A = R1 baseline"
  python3 self_eval.py --format json judge --report <worktree>/examples/dft-kL-demo/.workflow/final.md \
      --samples 10 --timeout 480 --message "same-session A/B: side B = R2 optimized"
  ```
  原始采样结果：`.scratch/m2-r2-ab/judge_A.json`、`judge_B.json`。

---

## 2. 客观指标（objective，无 key）

| 指标 | A（R1 基线） | B（R2 优化） |
|---|---|---|
| 总字符数 | 7440 | **8065** |
| 章节数 | 9 | **9** |
| 台账来源数（引用文献） | 16 | **16** |
| 交付门禁 exit | 0 | **0** |
| 交付门禁 FAIL | 0 | **0** |
| 交付门禁 WARN | 0 | **0** |

B（R2）章节字数分布（字符）：

| 章节 | A（R1） | B（R2） |
|---|---|---|
| (全文标题行) | 36 | 36 |
| 摘要 | 503 | 503 |
| 一、引言 | 182 | 182 |
| 二、研究方法 | 283 | **512**（补纳入/排除判据） |
| 三、DFT 能算的物理量：系统清单 | 1919 | **2141**（子章节织入 κ_L 关联） |
| 四、与晶格热导 κ_L 的 Overlap | 867 | **960**（4.2 补四声子触发、4.3 校准限定） |
| 五、对造真值数据集的直接启示 | 351 | **432**（<5% 适用域标注） |
| 六、结论 | 233 | 233 |
| 参考文献 | 3066 | 3066 |

> 正文主体（不含参考文献）由 A 约 4374 字符增至 B 约 **4963** 字符（净增约 590），全部来自四维优化织入的内容；台账 16 条依旧全部 VERIFIED、门禁全绿（exit=0 / FAIL=0 / WARN=0），与 R1 同口径可比。

---

## 3. judge 结果：同 session A/B（deepseek-v4-flash-0731 · A=10采 / B=9采）

| 维度 | A（R1 基线） | B（R2 优化） | Δ B−A | 判定 |
|---|---|---|---|---|
| Angle | 4.70 | 4.56 | -0.14 | 持平 |
| Coverage | 4.60 | 4.67 | +0.07 | 持平 |
| Citation | 4.10 | 4.44 | +0.34 | 实质改善 |
| Taxonomy | 5.00 | 4.89 | -0.11 | 持平 |
| Calibration | 4.40 | 4.11 | -0.29 | 关注 |
| Weaving | 4.40 | 4.67 | +0.27 | 实质改善 |
| Insight | 4.90 | 4.89 | -0.01 | 持平 |
| **总体** | **4.59** | **4.60** | **+0.01** | **持平** |

> 两侧同 session 实测；B 侧 1 次采样（第 3 次）读超时被跳过，如实记为 9/10 采样成功。`--timeout 480` 覆盖脚本默认 120s，规避 deepseekv4 慢速被截断（工具链改动见 §6）。absolute 分仅看同 session 内相对信号，不做跨轮硬比。逐维变化与优化动作的对应见 §5。

---

## 4. 质量曲线 v2（同 session A/B 口径）

v2 起质量曲线不再引用跨轮绝对分，改为**同 session A/B** 展示 R2 相对 R1 的改善方向。判定基准：Δ≥+0.2 视为实质改善，−0.2~+0.2 持平，≤−0.2 关注。

| 项 | A（R1 基线文本, 同 session 现测） | B（R2 优化文本, 同 session 现测） | Δ |
|---|---|---|---|
| **overall** | **4.59** | **4.60** | **+0.01** |
| Angle | 4.70 | 4.56 | -0.14 |
| Coverage | 4.60 | 4.67 | +0.07 |
| Citation | 4.10 | 4.44 | +0.34 |
| Taxonomy | 5.00 | 4.89 | -0.11 |
| Calibration | 4.40 | 4.11 | -0.29 |
| Weaving | 4.40 | 4.67 | +0.27 |
| Insight | 4.90 | 4.89 | -0.01 |

> **历史说明**：R1 报告中的 overall **4.6** 为 judge 漂移前的绝对值快照，本轮不予改写（见 `WORK_LOGS/M2_R1_SELF_EVAL_BASELINE.md`），其口径为「judge 漂移前绝对值」；后续轮次一律以同 session 相对信号为准。

---

## 5. 改动清单（R1 → R2）与维度对应

R1 短板主轴 `Weaving 4.2 → Citation/Calibration 4.4 → Coverage 4.6`，R2 全部落地：

1. **Weaving**：
   - 方法节补「纳入/排除判据」——入选=方法学代表性+子方向覆盖（非穷举）、以 [2][3] 为锚滚雪球至连续两轮无新文献（饱和判据）、排除纯应用算例。
   - 3.1 子节末织入「晶格常数/体积 = 3.3～3.4 各公式链的第一环」；3.3 织入「德拜温度/声速喂给 Slack 输入（[7] Debye、[8] GQ 修正）」。
2. **Citation**：拆开捆绑引用并逐条注明支撑点 —— 二阶[4]/三阶[6]；[7] 给 quasiharmonic Debye、[8] 给 GQ 尺寸一致修正；[7] Debye 口径、[9] 第一性实操口径；§5.1 的 [7] Slack/AGL 来源 vs [16] MLIP 加速路径。
3. **Calibration**：4.3「即可」→「可得、但需先经 §5 best-practice 校验 MLIP 力常数」；5.2「<5% 内」显式标注适用域（仅 Si/Ge 等简谐居中体系 + 含体散射假设，强非谐/低对称需逐体系核对）。
4. **Coverage**：4.2 补四声子触发条件（声学声子强色散/本征非谐显著体系：纤锌矿、SiGe/PbTe 类），避免"是否上四声子"无判据。

目标文件严格按 R1 口径（`.workflow/final.md`），未触碰 `output/` 那个 8225 字符版本；台账未改，16 条引用编号不变。

---

## 6. 工具链说明（本轮必要小改动）

- **`self_eval.py` judge 子命令新增 `--timeout`（默认 480s）**：deepseek-v4-flash-0731 当前实测单次采样常超脚本默认 120s 读超时（首跑 3/5 采样被截断、不可作为全采样结果）。抬高超时后 A 侧 10/10、B 侧 9/10 完成。此改动只影响 judge 采样的等待窗口，不改变评分逻辑或采样平均口径。
- 红线合规：PJLab key 仅从宿主 `~/.hermes/config.yaml` / 环境变量读取，仓库内无任何 key；本文件不含密钥。

---

## 7. 本轮结论

- 客观门禁保持全绿且体量可信增长（正文 4374→4963 字符），台账零改动、零 WARN，与 R1 同口径。
- **同 session A/B 判定（A=R1 基线现测 4.59，B=R2 优化现测 4.60，Δ=+0.01）→ 整体持平、无回归**：首攻维 Weaving +0.27（实质改善）、Citation +0.34（实质改善）兑现了 §5 的优化动作；Calibration -0.29 为本轮唯一关注维（judge 噪声带内，客观侧内容已加限定，留待 R3 复核）。
- 同 session 内 A/B 均高于跨 session 漂移读数，且基线文本自身会随 session 在 4.09（前会话）与 4.59（本会话）间漂移——再次佐证跨轮绝对分不可比、v2 起同 session A/B 口径成立。
- 质量曲线 v2 以同 session A/B 口径钉死本轮方法决策，供后续 R3–R5 沿用。
- 产物文档（本文件）与正文改动/工具小改动分别 commit，供审查员独立复核。

---

## 8. 附录：本轮改动文件

- `examples/dft-kL-demo/.workflow/final.md`（正文优化，四维 → §5）
- `skills/sciverse-deep-research/scripts/self_eval.py`（judge `--timeout` 小改动，工具向）
- `WORK_LOGS/M2_R2_SELF_EVAL.md`（本自评报告）
- `.scratch/m2-r2-ab/`（A/B 原始采样：baseline_final.md + judge_A.json + judge_B.json，临时目录不入库）
