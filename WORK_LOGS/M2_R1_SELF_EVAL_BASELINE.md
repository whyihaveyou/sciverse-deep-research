---
title: "M2 R1 自评基线：dft-kL-demo 质量快照与首条质量曲线 v1"
tags: [self-eval, m2, quality-baseline, dft-kl]
status: active
created: 2026-08-09
---

# M2 Round 1 自评基线：dft-kL-demo 质量快照

> 这是我（Honey）用 P1 自评工具链（`skills/sciverse-deep-research/scripts/self_eval.py`）对现存交付物跑的第一轮自评闭环，产出「可复核的质量基线」与「首条质量曲线 v1」。
> 本任务属**测量 + 记录**实现向，不改调研内容本身。

---

## 1. 对象与方法

- **评测对象**：`examples/dft-kL-demo` 主综述
  - 报告：`examples/dft-kL-demo/.workflow/final.md`（总 119 行 / 7440 字符）
  - 台账：`examples/dft-kL-demo/.workflow/citation_ledger.json.delivery.json`
- **两路信号（互不替代）**：
  1. `objective` —— 零网络、无 key 的硬指标（门禁、台账来源数、章节字数）
  2. `judge` —— LLM-as-judge（PJLab API，`deepseek-v4-flash-0731`，temperature 0.8，**5 次采样取均值±极差**）按 7 维内部质量门禁逐维打分 1–5
- **复现命令**（在 `skills/sciverse-deep-research/scripts/` 下执行）：
  ```bash
  python3 self_eval.py objective --report <worktree>/examples/dft-kL-demo/.workflow/final.md \
      --citation-ledger <worktree>/examples/dft-kL-demo/.workflow/citation_ledger.json.delivery.json
  python3 self_eval.py --format json judge --report <...>/final.md --samples 5 \
      --message "M2 R1 自评基线：dft-kL-demo 综述"
  ```

---

## 2. 客观指标（objective，无 key）

| 指标 | 值 |
|---|---|
| 总字符数 | 7440 |
| 章节数 | 9（摘要 / 引言 / 方法 / 三 / 四 / 五 / 六 / 参考文献 + 标题行） |
| 台账来源数（引用文献） | **16** |
| 交付门禁 exit | 0 |
| 交付门禁 FAIL | **0** |
| 交付门禁 WARN | **0** |

章节字数分布（字符）：

| 章节 | 字符 |
|---|---|
| (全文标题行) | 36 |
| 摘要 | 503 |
| 一、引言 | 182 |
| 二、研究方法 | 283 |
| 三、DFT 能算的物理量：系统清单 | 1919 |
| 四、与晶格热导 κ_L 的 Overlap | 867 |
| 五、对造真值数据集的直接启示 | 351 |
| 六、结论 | 233 |
| 参考文献 | 3066 |

> 备注：参考文献章节占约 41% 字符，属正常（16 条完整题录）；正文主体约 4374 字符。门禁全绿（FAIL=0 / WARN=0），台账 16 条全部 VERIFIED。

---

## 3. judge 结果（PJLab · deepseek-v4-flash-0731 · 5/5 采样成功）

| 维度 | mean | range | n |
|---|---|---|---|
| Angle（独立判断/核心结论） | 4.8 | 1.0 | 5 |
| Coverage（关键方面覆盖） | 4.6 | 1.0 | 5 |
| **Citation（引用绑定/题录可信）** | **4.4** | 1.0 | 5 |
| Taxonomy（分类/组织严谨） | 4.8 | 1.0 | 5 |
| **Calibration（取舍/不过度承诺）** | **4.4** | 1.0 | 5 |
| **Weaving（多来源织成整体）** | **4.2** | 1.0 | 5 |
| Insight（超越罗列的洞见） | **5.0** | 0.0 | 5 |
| **总体 mean** | **4.6** | — | 5 |

> 5/5 采样成功、无网络/key 报错；整体无维度低于 4，属高质量交付物。
> range=1.0 为 5 次采样整数打的正常离散；Insight range=0（5 次全 5 分）最稳定。

---

## 4. 质量基线快照（v1）

- **客观**：门禁全绿（FAIL=0/WARN=0）· 台账 16 条 · 正文约 4.4k 字符 / 9 章
- **主观 7 维**：Angle 4.8 · Coverage 4.6 · Citation 4.4 · Taxonomy 4.8 · Calibration 4.4 · Weaving 4.2 · Insight 5.0
- **overall_mean**：**4.6 / 5**
- **短板维**（相对低分，按低到高）：**Weaving 4.2 → Citation 4.4 / Calibration 4.4 → Coverage 4.6**

---

## 5. 首条质量曲线 v1

质量曲线按「轮次」纵向推进，每轮 = 一次可验收的自评/优化闭环。本轮为 **Round 1（基线）**，即曲线的第一个点；后续 Round 2… 在优化后复测，逐步描出趋势。

| Round | overall | Angle | Coverage | Citation | Taxonomy | Calibration | Weaving | Insight | 备注 |
|---|---|---|---|---|---|---|---|---|---|
| **R1（本轮·基线）** | **4.6** | 4.8 | 4.6 | 4.4 | 4.8 | 4.4 | 4.2 | 5.0 | 首次采集，基线点 v1 |

> 判定基准：7 维 ≥4 为「稳健」，≥4.5 为「优秀」。当前短板 ≤4.4 的三维即下一轮优化目标。

---

## 6. 问题 → 改哪里（按低分维给可执行优化点）

### 6.1 Weaving 4.2（最低，首攻）
**问题**：第 1–3 章（引言/方法/系统清单）以「清单+枚举」为主，各子方向读起来偏并列，交叉与被引用链（哪些量喂给哪条 κ_L 公式链）要到第 4 章才集中出现；「为什么选这 17 篇、为什么构成饱和」论证偏薄。
**改哪里**（可执行）：
1. 在第 3 章每个子节末尾加一行「→ 喂给 κ_L 公式链的哪一环」（如 3.3 力学 → 动理论 v、Slack 输入），把「它能算什么」与「对 κ_L 有什么用」在前文就交织起来，而非只在第 4 章收口。
2. 方法节补一段「纳入/排除判据」（为何 17 篇、滚雪球如何收敛到饱和），把检索叙事织进结论的可信度里。

### 6.2 Citation 4.4
**问题**：题录本身可信（16 条 VERIFIED、门禁绿），但正文多处用「多引用捆绑」[6,4]、[7,16] 未逐条点明各自承担的论据；个别句（如 3.2 带隙 mBJ 那句）引用粒度可更精确。
**改哪里**：
1. 捆绑引用处拆开并注明各自支撑点（例：`[7] 给德拜温度、[16] 给 MLIP 加速`），提升「每个 [n] 都在法庭上」的可追溯性。
2. 对「DFT 算 κL <5%」[2] 这类硬论断，保持现状并可在正文补一句适用边界（单晶、室温、无同位素散射前提）。

### 6.3 Calibration 4.4
**问题**：整体已克制（PBE 高估、带隙低估、虚频陷阱均标注），但个别结论句偏「承诺式」，如 4.3「重算即可得独立真值特征集」、5.2「应 <5% 内」，缺少对「MLIP 三阶力常数仍需校验」「<5% 仅在 Si/Ge 基准成立」的显式限定词。
**改哪里**：
1. 4.3/5.1 的「即可」改为「可得、但需以 Phonon Olympics best-practice 校验 MLIP 力常数」。
2. 5.2 的「<5% 内」标注适用域（基准对 Si/Ge、含体散射假设）。

### 6.4 Coverage 4.6（微调，可选）
**问题**：五大谱系覆盖完整，但「三/四阶力常数、四声子」标注为 ★/★★，未给「哪些体系必须上四声子」的判据。
**改哪里**：4.2 补一句「强非谐/低声学声子材料（如纤锌矿、热电）需上四声子 [15]」的触发条件即可收口。

---

## 7. 本轮结论

- 交付物质量**稳健偏优**（overall 4.6、无维度 <4、门禁全绿），Insight 满分最亮眼。
- **下一轮（R2）优化主轴 = Weaving（4.2）**，次攻 Citation/Calibration（4.4）——三点的优化动作都已在 §6 落到具体章节与语句级。
- 首条质量曲线 v1 已建立（overall 4.6 为基线点），R2 复测同一对象可形成首段趋势。

## 8. 红线合规

- **PJLab key 未进 git**：`self_eval.py` 只从宿主 `~/.hermes/config.yaml` 或环境变量读取，本次运行亦未在仓库写入任何 key；本文件不含密钥。
- 本基线文档单独 commit，与任何调研内容改动隔离。
