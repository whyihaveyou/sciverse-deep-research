# OpenCode + DeepSeek-chat v4.1 修补验证：机器学习势函数 × 晶格热导率

这是 2026-08-12 在第四轮改进基础上叠加 v4.1 引用纪律修补后的端到端验证运行产物。v4.1 针对 v4 独立复核 WARN 从 1 涨到 10 的回退，在 SKILL.md、references/output-structure.md、references/synthesis-framework.md 中补强了"结构元素点名必引用"条款。

## 运行条件

- Agent / 模型：OpenCode 1.18.16 + deepseek-chat（API baseURL `https://api.deepseek.com`）
- 工作目录：本次运行实际把 `.workflow/` 落在项目根目录，已事后迁到 `.scratch/opencode-run-v5/.workflow/`
- Prompt：与 v2/v3/v4 保持一致（含 Step0 明确选择以支持非交互 `opencode run --auto`）
- 信息源：仅 sciverse（search_papers / semantic_search / list_paper_relations）

## 运行指标

| 指标 | v4 | v5（本轮） | 变化 |
|---|---|---|---|
| 耗时 | ~4m08s | ~10m04s | +5m56s |
| 检索调用 | 14 | 40 | +26 |
| 入选文献 | 22 | 21 | -1 |
| 中文字符 | 5196 | 5448 | +252 |
| 引用密度（citations/sentences） | 0.30 | 0.49 | ↑ |
| 无引用中文概括段落（≥15 字） | 25/57 | 19/64 | ↓ |
| 独立复核 FAIL / WARN | 0 / 10 | 0 / 0 | ✅ 达标 |

> 注：耗时按 `.workflow` 目录 birth 到 `final.md` mtime 估算；独立复核用 `skills/sciverse-deep-research/scripts/check_report.py`。

## 目录结构

- `output/机器学习势函数与晶格热导率预测进展综述.md`：交付视图（export-clean，文件名与原 `交付.md` 内容一致）
- `output/final.md`：事实源（含 `[N]` 编号引用）
- `.workflow/`：完整工件（draft.md、search_log.md、citation_ledger.json、final.md、交付稿等）

## v4.1 修补效果

- **关键引用节**：v5 每条均带 `[@键]` / `[N]` 编号，不再出现方法/材料名裸放。
- **核心要点 / 分类框架表 / 对比表**：凡出现具体论文/系统/方法/材料名，均挂了引用编号。
- **研究方法关键词**：方法/工具名首次出现时视为该方法奠基工作的引用并标注编号。
- **副作用**：
  - 检索调用从 14 次增至 40 次，耗时从 4m 增至 10m——新纪律让 agent 更积极地补搜以支撑引用。
  - 入选文献 21 篇（vs v4 的 22 篇），文献选择略有不同，核心叙事从"BTE/MD 路线 + 四声子异质性"转向"方法族精度 + 多体热流正确性"。

## 新机制痕迹

- **意图演化（Retrieve→Reflect）**：`search_log.md` 明确记录了 `updated_intent`、`updated_checklist`、`missing_coverage`、`evidence_gaps`。
- **Mini scattered-and-stacked**：v5 仍未在 draft.md / final.md / 日志中留下显式的 Solver/Critic/Rewriter/Selector 角色痕迹；agent 以单稿综合完成输出。

## 结论

v4.1 的"结构元素点名必引用"条款成功把独立复核 WARN 从 10 降到 0，证明 v4 的回退是条款覆盖不足而非模型能力问题。代价是检索调用数和耗时显著增加。Mini scattered-and-stacked 机制仍未被弱模型显式执行，建议下一迭代将其改写为要求 agent 在 draft.md 中产出带明确小标题（`#### 候选解读 A/B`、`Critic 批判`、`Rewriter 综合`、`Selector 定稿`）的可观测中间产物，而不是依赖抽象角色描述。
