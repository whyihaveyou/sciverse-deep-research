# OpenCode + DeepSeek-chat 泛化性验证：机器学习 × 固态电解质

这是 2026-08-12 用最新版 skill（main @ 9e8932d，含第五轮 harness 架构 + 第六轮机制 + 过程工件闸口）在一个**全新题目**上的端到端验证运行产物。前八版验证均围绕"晶格热导率"一题，本题转向"机器学习辅助固态电解质筛选与界面设计"，以检验 skill 的跨领域泛化能力。

## 运行条件

- Agent / 模型：OpenCode 1.18.16 + deepseek-chat（API baseURL `https://api.deepseek.com/v1`）
- 工作目录：`.scratch/opencode-run-sse/`（OpenCode 正确写入该目录）
- Prompt："帮我调研一下机器学习辅助固态电解质（solid-state electrolyte）筛选与界面设计的研究进展，出一份小综述"，并附加"请用 Markdown 输出，信息源只用 sciverse，跳过 Step0 澄清直接进入检索"
- 信息源：仅 sciverse（search_papers）

## 运行指标

| 指标 | κL 系列（v8） | SSE 新题（本轮） |
|---|---|---|
| 耗时 | ~5m | ~4m（16:38–16:42） |
| 检索调用 | 16 次 | 8 次（均为 search_papers） |
| 入选文献 | 21 篇 | 30 篇 |
| 独立复核 FAIL / WARN | 0 / 2 | 0 / 2 |
| section_reviews.md | ✅ 存在，4 块 | ✅ 存在，4 块 |
| evidence_compress.md | ✅ 存在，含标记 | ✅ 存在，含 ✅/⚠️ |
| 调研成本小节 | ✅ 出现 | ✅ 出现 |

> 注：独立复核用 `skills/sciverse-deep-research/scripts/check_report.py`；WARN 2 均为 LATP/CSP 启发式近邻误报，agent 已人工核正确。

## 目录结构

- `output/交付.md`：交付视图（export-clean，FAIL 0 / WARN 2）
- `.workflow/final.md`：事实源
- `.workflow/draft.md`：键值草稿
- `.workflow/section_reviews.md`：结构化自批判审计工件（4 个分支）
- `.workflow/evidence_compress.md`：证据压缩审计工件
- `.workflow/citation_ledger.json` / `.workflow/citation_ledger.json.delivery.json`：引用台账

## 新题上各机制激活情况

| 机制 | 是否激活 | 观察 |
|---|---|---|
| RQ 冻结 / Step0 跳过 | ✅ | agent 自动拟定 4 个 RQ（筛选/势函数/主动搜索/界面） |
| 检索收敛检查表 | ✅ | evidence_compress.md 中写明"滚雪球 N 轮，末轮新增 0 篇，达检索饱和" |
| 意图演化（updated_intent） | ⚠️ 弱 | evidence_compress.md 有视角修正与盲区记录，但未显式出现 updated_intent 代码块 |
| 裁判型文献定向检索 | ⚠️ 弱 | agent 自述视角 E（批评/失效）偏薄，主要靠侧面覆盖 |
| 压缩块（evidence_compress） | ✅ | 按 A–E 视角组织，含 30 篇文献的 ✅/⚠️ 状态 |
| section_review | ✅ | 4 个分支均产出，含 claims_verification / L3_L4_verdict / evidence_gaps / patch_plan |
| L3/L4 洞见纪律 | ✅ | 每个分支均标注 L3 或 L4 级判定 |
| 引用纪律 | ✅ | 无裸 URL、无未编译引用键、编号连续 |
| 过程工件闸口闭环 | ✅ | section_reviews + evidence_compress 均存在，check_report 无过程工件 WARN |
| 效率附录（调研成本） | ✅ | final.md 末尾出现，内容诚实保守 |

## 产出质量评价（对比 κL 系列）

**结构**：与 κL 系列一致，采用"关键引用 → 摘要 → 核心要点 → 引言/方法/框架 → 分支 → 综合讨论 → 开放问题 → 结论 → 调研成本"的 survey paper 骨架，符合 output-structure.md 要求。

**文献覆盖**：30 篇，覆盖描述符/组成监督学习代理、机器学习势函数/MD、生成式/主动搜索、界面/SEI 设计四大分支，并延伸到材料类别专项（garnet、argyrodite、卤化物等）。比 κL 系列更宽，但单篇深度略浅（部分仅基于摘要）。

**洞见深度**：
- 分支 1（监督学习代理）：L3——"小数据下分类/排序可靠、绝对回归存疑"
- 分支 2（MLIP/MD）：L4——"通用势 = 初始化+先验，非免训练终态；需系统特定数据细调"
- 分支 3（生成/主动搜索）：L3——"从性质绝对值到信息效率"
- 分支 4（界面/SEI）：L3——"ML 应用密度与商业紧迫性成反比（界面最急却最稀）"

整体达到 L3/L4 要求，但新题文献更散、部分数值未逐篇全文对读，agent 在调研成本中已诚实声明。

**与 κL 系列的主要差异**：
- κL 系列有明确的方法论主线（力误差 → 热导率误差传播），SSE 新题分支间独立性更强，综合讨论以"应用密度反比"这类跨分支对照洞见为主；
- SSE 新题检索调用更少（8 vs 16），但文献数更多（30 vs 21），说明 agent 更依赖 search_papers 的关键词召回，semantic_search 未显式使用；
- 过程工件闭环在新题上同样生效，说明程序级闸口具有跨题稳定性。

## 结论

最新版 skill 在新题"机器学习 × 固态电解质"上成功跑通完整管线：RQ 自动拟定、检索收敛声明、压缩块、section_review、L3/L4 洞见、引用纪律、过程工件闸口闭环、效率附录均生效。主要短板是裁判型文献定向检索与意图演化块不够显性（与 κL 系列类似），但核心交付质量达标（FAIL 0）。
