# OpenCode + DeepSeek-chat 第四轮改进验证：机器学习势函数 × 晶格热导率

这是 2026-08-12 使用改进后 sciverse-deep-research skill 进行的端到端验证运行产物，对应第四轮 skill 改进（Retrieve→Reflect 意图演化、可编辑 search_plan、Mini scattered-and-stacked 深度合成、段落级 citation grounding）。

## 运行条件

- Agent / 模型：OpenCode 1.18.16 + deepseek-chat（API baseURL `https://api.deepseek.com`）
- 工作目录：`.scratch/opencode-run-v4/`
- 原始 prompt 见 `.scratch/opencode-onboarding-report.md`（与 v1/v2/v3 同一题目，仅补充 Step0 明确选择以支持非交互 `opencode run --auto`）
- 信息源：仅 sciverse（search_papers / semantic_search）

## 运行指标

| 指标 | v4（本轮） | v3 | v2 | v1 | Kimi（对照） |
|---|---|---|---|---|---|
| 耗时 | ~4m08s | ~8m28s | ~6m01s | ~6m55s | ~18m |
| 检索调用 | 14（9 search_papers + 5 semantic_search） | 39 | 28 | 33 | — |
| 入选文献 | 22 | 22 | 24 | 22 | 25 |
| 中文字符 | 5196 | 6251 | 5590 | 6033 | — |
| 引用密度（citations/sentences） | 0.30 | 0.33 | 0.57 | 0.28 | — |
| 独立复核 FAIL / WARN | 0 / 10 | 0 / 1 | 0 / 1 | 0 / 0 | 0 / 0 |

> 注：独立复核使用 `skills/sciverse-deep-research/scripts/check_report.py`；agent 自报 export-clean 视图为 FAIL 0 / WARN 0，但独立复核发现 10 条 WARN，主要为点名未引用/编号疑似错位。

## 目录结构

- `output/机器学习势函数与晶格热导率预测进展综述.md`：交付视图（export-clean）
- `output/final.md`：事实源（含 `[N]` 编号引用）
- `.workflow/`：完整工件（draft.md、search_log.md、citation_ledger.json、final.md、交付稿等）

## 关键观察

1. **意图演化（Retrieve→Reflect）**：`search_log.md` 明确记录了 `updated_intent`、`missing_coverage`、`evidence_gaps`，将组织轴从“罗列应用”收窄为“BTE/MD 两条路线 + 四声子刻画 + 通用势可靠性”。
2. **Mini scattered-and-stacked**：最终文本中未见显式的 Solver/Critic/Rewriter/Selector 角色痕迹；agent 以单稿高质量综合完成了输出，结构（关键引用、核心要点、研究问题、分类表、跨分支综合）优于 v3，但多解竞争机制未以可观测形式落地。
3. **段落级 citation grounding**：v4 与 v3 的“无引用中文概括段落”均为 25 个（≥15 中文字符的段落），但 v4 总段落数更少（57 vs 66），结构性段落（要点、表注、节标题展开句）占比更高；独立复核 WARN 由 v3 的 1 升至 10，说明点名引用纪律仍有退化。
4. **效率**：v4 检索调用数（14）和耗时（4m08s）均显著低于前三版，新机制让弱模型检索更聚焦，未出现流程卡死。

## 结论

第四轮改进中的“意图演化”条款明显生效，产出的结构化和洞见浓度（ especially 四声子材料异质性裁决、热导导向验收协议）较 v1/v2/v3 有提升；但“Mini scattered-and-stacked”多角色竞争机制在 OpenCode+DeepSeek 上未以显式角色痕迹执行，段落级 citation grounding 的量化指标也未改善（独立复核 WARN 反而增加）。v4 与 Kimi 版的主要差距仍在语言的学术紧凑度和部分高阶判据文献的覆盖深度。
