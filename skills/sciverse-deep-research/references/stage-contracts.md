# 阶段契约（IOBC）与状态对象

本 skill 的调研管线可映射为若干连续阶段。每个阶段用 **IOBC 四件套**定义：

- **Input**：从上一个阶段或状态对象读入什么。
- **Output**：写出什么产物/字段到状态对象。
- **Boundary**：明确禁止做什么（防止阶段性质混淆）。
- **Gate**：满足什么条件才允许进入下一阶段。

阶段之间通过 `.workflow/` 下的**状态对象**连接。状态对象是单写事实源：前一阶段落盘、下一阶段只读（写操作必须拿到单写锁）。

---

## M1 澄清（Step 0）

**Input**：用户原始话题或问题。

**Output**：
- `research_brief`（概念上，可落进 `.workflow/search_plan.md` 或 agent 内部状态）：
  - 研究话题
  - 2-3 个具体、可回答的 RQ
  - 角度/核心判断方向
  - 目标受众
  - 输出格式（Markdown / PDF）
  - 信息源（sciverse / arXiv / OpenAlex）

**Boundary**：
- 禁止检索。
- 禁止写稿。
- 禁止发散到方法论细节。
- 仅询问为冻结研究简报所必需的澄清问题。

**Gate**：
- 用户确认研究简报（或默认继续）。
- RQ 可回答、信息源已选、输出格式已确定。

---

## M2 定纲（检索计划 + Taxonomy）

**Input**：`research_brief`。

**Output**：
- `.workflow/search_plan.md`：
  - 子问题列表（若 RQ 可拆分）
  - 每子问题关键词族（≥2 组）
  - 信息源分配
  - 时效窗口/精度分级
  - 检索轮次预算（每子方向 ≤3 轮）
- `.workflow/taxonomy.md`（可选，复杂话题）：MECE 分类骨架、空格（gap）、各分支回答的 RQ。

**Boundary**：
- 只做计划，不执行检索。
- 不预先决定会找到哪些论文。
- 若 RQ 不可拆分为子问题，可退化到顺序模式，但仍需书面化检索视角。

**Gate**：
- 检索计划覆盖所有 RQ。
- 子问题 MECE（互斥且完备）或已说明为何采用非 MECE 轴。

---

## M3 检索（文献检索与核验）

**Input**：`research_brief` + `.workflow/search_plan.md`。

**Output**：
- `.workflow/citation_ledger.json`（已过 `validate`）：
  - 每篇入选文献的 id、title、authors、year、venue、unique_id、verify_status、aliases、role、note
  - `criteria` 字段（若用户给定纳入/分级标准）
- `.workflow/search_log.md`：
  - 检索视角与执行 query
  - `updated_intent` / `updated_checklist` / `missing_coverage` / `evidence_gaps`
  - 滚雪球轮次与末轮新增数
  - 检索收敛声明

**Boundary**：
- 禁止跳过存在性核验。
- 禁止从模型记忆补入候选清单。
- 禁止直接写最终文档。
- 禁止无限补检；单方向达到预算上限必须落 checkpoint 暂停。

**Gate**（检索收敛声明三要素必须齐备）：
1. 一轮滚雪球补搜**零新增入选**。
2. 每个子方向/视角 ≥3 篇核心文献。
3. 时效探针已执行（近窗口 + 奠基档核对）。

---

## M4 综合分析

**Input**：`.workflow/citation_ledger.json` + `.workflow/search_log.md` + taxonomy。

**Output**：
- `.workflow/draft.md` 键值草稿：
  - 正文引用统一使用 `[@引用键]`
  - 末尾保留空的 `## 参考文献` 占位节
  - 含关键引用、核心要点、引言 RQ、研究方法、分类框架、分支章节、综合讨论、开放问题、结论
- `.workflow/subproblems/Si.md`（编排模式下）：各子问题产物，用于无损合并。
- `.workflow/intent_evolution_log.md`（编排模式下）：每轮补搜后的意图演化记录。

**Boundary**：
- 禁止在分析步调用检索工具（缺口应回 M3，而不是顺手补搜）。
- 禁止引入台账外的来源。
- 禁止自由手写数字编号。

**Gate**（7 维门禁相关维度必须 CLEAR）：
- Coverage：每个子方向 ≥3 篇。
- Taxonomy：MECE 且有空格说明。
- Insight：每个分支 ≥1 条 L3/L4 级洞见；不足时回 M3 补挖裁判型文献，或启用 Mini scattered-and-stacked。
- Citation grounding：每个 claim 段落带 `[编号]`；结构性元素点名必引用。

---

## M5 写作（键值草稿定稿）

**Input**：M4 综合分析后的 `draft.md`。

**Output**：
- 定稿的 `.workflow/draft.md`：
  - 全文引用键完整、无占位符
  - 各节切片与台账一致
  - 无裸 URL/DOI、无未归档数学残留

**Boundary**：
- 不引入新文献（新发现应回 M3/M4）。
- 不改 citation_ledger.json（编号冻结后台账是只读事实源）。
- 不自由手写 `[N]` 编号。

**Gate**：
- 自对抗审查无待修项。
- 7 维门禁全部 CLEAR 或已知 WARN 可接受。

---

## M6 核查（交付编译与 lint）

**Input**：`.workflow/draft.md` + `.workflow/citation_ledger.json`。

**Output**：
- `.workflow/final.md`：`citation_ledger.py compile` 产物，含 `[N]` 编号与参考文献。
- `.workflow/citation_ledger.json.delivery.json`：compile 生成的交付用台账。
- `.workflow/交付.md` 或同名中文交付视图（`check_report.py --export-clean` 生成）。
- check_report 足迹（stdout / 摘要行）。

**Boundary**：
- 禁止人工改编号。
- 禁止绕过 `check_report.py`。
- 禁止在 FAIL 未消解时交付。

**Gate**：
- `citation_ledger.py compile` 成功。
- `check_report.py` FAIL 0；WARN 按模式要求（综述模式建议 ≤1）。

---

## M7 交付（呈现给用户）

**Input**：`.workflow/final.md` + 可选的 `.pdf`。

**Output**：
- 用户可见交付物（Markdown / PDF）。
- 若用户要求，可附带 `.workflow/` 内部工件供审计。

**Boundary**：
- 禁止私自 commit/push 到共享仓库（除非用户明确授权）。
- 禁止把用户 API key / token 写进任何交付文件或仓库文件。

**Gate**：
- 用户验收或默认接受。

---

## 状态对象 schema 速查

| 文件 | 阶段 | 字段/内容 | 读写权限 |
|---|---|---|---|
| `.workflow/search_plan.md` | M2 | 子问题、关键词、来源、预算、时效档 | M2 写；M3 读 |
| `.workflow/citation_ledger.json` | M3 | 入选文献元数据、verify_status、aliases、role | M3 写；M4-M6 只读 |
| `.workflow/search_log.md` | M3 | 检索视角、意图演化、收敛声明 | M3 写；后续只读 |
| `.workflow/taxonomy.md` | M2-M4 | 分类骨架、空格 | M2 起草；M4 定稿 |
| `.workflow/draft.md` | M4-M5 | 键值草稿，正文 `[@键]` | M4-M5 写；M6 读 |
| `.workflow/intent_evolution_log.md` | M4（编排） | 每轮补搜的 updated_intent / gaps | M4 追加 |
| `.workflow/subproblems/Si.md` | M3-M4（编排） | 各子问题产物 | 子 agent 写；M4 合并读 |
| `.workflow/final.md` | M6 | compile 后 `[N]` 编号正文 + 参考文献 | M6 写；M7 读 |
| `.workflow/citation_ledger.json.delivery.json` | M6 | compile 生成的交付用台账 | M6 写；M7 读 |
| `.workflow/checkpoint_*.md` | 任意 | 阶段超预算或中断时的衔接摘要 | 超限时写 |

**单写红线**：`citation_ledger.json`、`draft.md`、`final.md` 同一时刻只允许一个上下文实例写。续跑时先 `stage_contract.py check <workdir>` 确认工件齐备，从盘加载后继续，不重演完整历史。
