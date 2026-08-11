# 检索策略细则

## 工具选型：sciverse MCP

- **`search_papers`（结构化过滤检索）**：主力检索工具。`query` 是 **BM25 全文关键词**，匹配标题/摘要/期刊名/关键词字段——写查询词时按关键词思维构造，不要写整句自然语言。结构化过滤（任一命中即可）：`title_contains`（标题含词）、`authors`、`journals`（**用规范化载体名**，如 "Nature Communications" 而不是 "Nat Commun"——拿不准先用 `list_catalog` 看取值样本）、`year_from`/`year_to`、`subjects`。排序：`sort_by_year` 与 `query` 模糊检索的相关性排序互斥，`freshness_boost`（MILD 近 10 年加权 / STRONG 近 3 年加权）与 `sort_by_year` 互斥——追时效时在两者之间二选一，不要假设可以叠加。`filters_advanced` 是逃生舱：OA 状态（`access_oa_status`）、DOI 精确匹配等任意字段过滤，可用字段与取值先 `list_catalog` 学，不要猜字段名。
- **`semantic_search`（自然语言检索）**：适合"怎么问比怎么搜更自然"的场景——机制性问题、跨术语概念。返回的是**论文切片**（chunk + doc_id + offset），不是整篇条目；拿到切片后用 `read_content(doc_id, offset)` 扩读上下文，需要题录时再用 `search_papers` 按标题/unique_id 补齐。三个 mode 的速度-质量权衡：`fast` 仅关键词召回（~200ms，适合探针式粗扫）、`balanced` 混合检索（默认，~600ms）、`quality` LLM 改写 + 混合（~2-4s，留给深问题式的关键检索）。
- **`list_catalog`**：学字段 schema 与枚举值（如 `access_oa_status` 的合法取值）。遇到"这个字段能不能过滤、取值是什么"时调用，毫秒级，不要凭记忆猜。
- **`list_paper_relations`（滚雪球主力）**：以入选文献的 `unique_id` 为种子，`relation=REFERENCES`（我引用了谁，向后找前置）/ `CITATIONS`（谁引用了我，向前找后继）/ `RELATED_WORKS`（相关工作）。**CITATIONS 有两个硬限制**：关系总数超 10000 返回 429、page×page_size 超 10000 返回 400——高被引种子论文撞限后，改走 `search_papers` 的 `filters_advanced` 加 `references_unique_id`（查"引用了某篇论文"的工作），它支持深翻页与任意排序，可叠加年份等条件（如"引用了 ResNet 且 2023 年后发表"）。
- **`read_content`**：读论文全文切片，用于引述准确性对读（见 `references/citation-protocol.md`）。

## 时效精度分级

**检索前必须先读当前日期**（用宿主时钟 / `current_date` 等），再按话题对时效的敏感度选对应时间窗口——**不写死固定年数**（旧的"近 3 年优先 / 时效探针取 6-12 个月"已作废）。所选窗口必须写进检索计划/研究简报，作为可核验的时间范围声明。

| 话题时效敏感度 | 典型来源 | 检索窗口 | freshness_boost | 说明 |
|---|---|---|---|---|
| 前沿方法（模型/算法/新材料性能/新数据） | CS/AI 预印本、顶会、近期顶刊 | 近 6-12 个月 | STRONG | 半年内的工作可能关键，须限定到月 |
| 成熟领域（稳定技术、已立范式） | 期刊正式版、综述 | 近 3 年 | MILD | 核心已沉淀，追近年增量即可 |
| 奠基/经典文献（综述、开山之作、高被引原文） | 经典教材、原文 | 不设窗口 | 不用 | 只看经典，不限年份 |

选档判据：研究简报里该子方向**若不是"快速演进的新方法"，就默认归"成熟领域/奠基"档，别一律追最新**。时间窗口决定 `search_papers` 的 `year_from`/`year_to` 取值，以及是否用 `freshness_boost` 及其档位。

**时间粒度**：以上 `today / week / year` 三个粒度词对应"窗口能细到哪"——话题需要实时/周级判断（热点事件、舆情、正在发生的争议）时把窗口压到 today 或 week 级并当日复核；常规学术综述按上表归入 6-12 月 / 3 年 / 不设窗口的 year 级粒度。

## 关键词构造

关键词不是想到什么搜什么。按以下模式系统构造（`search_papers` 的 `query` 用）：

**核心纪律：`search_papers` 的 `query` 走 BM25 全文关键词，用 2-3 个核心词组合，不要写整句自然语言。** 整句会触发短语/整句匹配，极易命中 0 结果。**降级路径：整句导致 0 结果 → 拆成 2-3 个核心词重搜**（从原句抽名词/方法名/领域词，如 "哪些方法能降低 LLM 推理成本" → `"LLM inference cost reduction"`）；再不行换同义词或转 `semantic_search`——**只有 `semantic_search` 才接受整句自然语言提问**，`search_papers` 的 `query` 一律走核心词。

**模式 1：核心方法 × 应用领域**
- "retrieval augmented generation" + "question answering"
- "CRISPR base editing" + "clinical trial"

**模式 2：核心机制 × 目标任务**
- "chain of thought" + "scientific reasoning"
- "碱基编辑" + "遗传病治疗"

**模式 3：领域 + survey/benchmark/meta-analysis**
- "LLM agent survey 2024 2025"
- "social media adolescent mental health meta-analysis"

**模式 4：关键人名 × 方向**（当研究简报提到具体研究者时）
- `authors: ["Haidt"]` + query "social media adolescent"
- `authors: ["Orben"]` + query "screen time well-being"

**模式 5：已知论文的引用网络**
- 首选 `list_paper_relations` 直接走引用关系（见上方工具说明与下方"滚雪球"）；
- 关系查询不可行时（种子无 unique_id、关系数据缺失）退回关键词近似：从核心论文标题提取关键术语，以"工作名/方法名 + extension / follow-up / critique / limitation"式检索其扩展、批评与后继工作；
- 系统化执行与收敛判据见主 SKILL.md「阶段一·第五步：滚雪球至饱和」（向后反查前置、向前找后继、一轮零新增即饱和）。

每个模式至少试一轮。在多视角检索中，每个视角用 1-2 种模式构造关键词，3-5 个视角 × 每视角 2 轮 = 若干轮检索调用。具体次数不设上限，以覆盖充分为准。

## 裁判型文献定向检索

综述质量的天花板常被"谁能找到批判、边界、失效分析类文献"决定。这类文献不只在摘要里写"we improve X"，而是回答"X 何时失效 / 为何被高估 / 系统误差从哪来"。每个子主题至少尝试一次裁判型文献定向检索，把结果写入检索日志，即使未命中也要记录"本主题未找到明确裁判型文献"。

**语义检索探针（`semantic_search`，quality 模式）**：用质疑句式直接搜，不要只搜正面陈述。
- `"limitations of {方法名} for {目标物理量}"`
- `"when {方法名} fails" / `"breakdown of {方法名}"`
- `"systematic error in {测量/计算方法}"`
- `"force error thermal conductivity machine learning potential"`（本主题示例）
- `"four-phonon scattering overestimated" / `"revisiting four-phonon"`
- `"is {方法名} reliable for {体系特征}"`

**结构化关键词探针（`search_papers`）**：把质疑词与核心概念组合成 BM25 query。
- `{核心方法} + "systematic error"`
- `{核心方法} + "underestimation" / "overestimation"`
- `{核心方法} + "critique" / "criticism" / "limitation"`
- `{核心方法} + "vs" + {对照方法}`（常用于挖出对比/裁判型工作）
- `{核心物理量} + "benchmark" + "failure mode"`

**滚雪球中的裁判型分支**：对高被引种子论文，不要只顺着后继工作找"应用"，也要找"质疑"。
- `list_paper_relations` relation=CITATIONS 拿到后继引用后，用 `search_papers` 加 query `"limitations"` / `"critique"` / `"re-examination"` 过滤该引用集（或用 `filters_advanced` 反查 `references_unique_id`，再叠加上述关键词）。
- 对里程碑方法（如 DeePMD-kit、NEP、MTP），定向搜 `"{方法名} force error"`、`"{方法名} thermal conductivity accuracy"`、`"{方法名} benchmark"`。

**裁判型文献的快速识别**：读摘要时优先抓以下信号词——"systematic underestimation"、"overestimation"、"breakdown"、"failure mode"、"limitations"、"revisit"、"re-examine"、"contradict"、"challenges the assumption"、"questions the validity"。

**纳入优先级**：裁判型文献即便方法小众，只要它针对的是本主题核心方法/结论的边界，优先纳入并分配到综合阶段的"矛盾呈现 / 分歧裁决"环节，而不是作为普通相关工作罗列。

## Web 全文读取

检索工具（网页检索 / web search）返回的命中，**必须读取全文正文而非只看 snippet**——snippet 常截断、易断章取义，撑不起引述与判断。规则：

- 命中后对关键条目用 `web_fetch`（或宿主等效的 WebFetch / fetch_url）抓取正文再引用。
- **snippet-only 禁用场合**：① 引述具体数值/结论/实验方法时；② 判定期刊等级、题录字段时；③ 判断某篇工作是否存在的关键 claim 时。这些场合只看 snippet = 未核验，不得作为依据。
- 网页内容只作**题录核验与事实核对的指定通道**（见主 SKILL.md 工具段），不作学术观点来源。

## 盲区发现

第二轮检索后做一次盲区检查：

1. **覆盖检查**：研究简报的每个子方向是否有 ≥3 篇文献？
2. **流派检查**：有没有明显的方法流派完全缺席？
3. **引用链检查**：已找到的论文引用的高频工作是否在列表里？（用 `list_paper_relations` REFERENCES 直接查，不靠印象）
4. **弃置检查**（STORM moderator trick）："搜到了但没打算用"的结果是否指向未覆盖的子方向？不要扔掉它们——它们是盲区的线索。
5. **时间检查**：所选时效窗口内有没有重要工作？全是老论文说明可能漏了新进展。（收尾时另有硬性时效探针：宣布饱和前每视角一轮按上方"时效精度分级"表选档限定检索——`search_papers` 加该档 `year_from` 或 `freshness_boost`，见主 SKILL.md 阶段一第五步饱和判据。奠基/经典档的探针是核对经典是否齐备，而非追最新。）

## 按学科调整检索

不同学科的文献分布不同：

- **CS/AI**：arXiv 预印本为主，更新极快，近 6 个月的工作可能关键。**归"时效精度分级"的前沿档**：时效探针取 6 个月窗口；`freshness_boost: STRONG` 适合追最新进展。
- **生物医学**：NEJM/Lancet/Nature Medicine 的临床论文，搜 "clinical trial" + 疾病名；可用 `journals` 参数限定规范化期刊名。
- **社科**：AER/QJE（经济学）、Nature Human Behaviour（心理学），搜效应量和方法（RCT/DID/IV）。
- **跨学科**：分别搜每个相关学科（`subjects` 参数过滤），再合并。不要只搜一个学科的关键词。

## 检索收敛检查表（阶段一合法出口）

进入阶段二（编号冻结/综合）之前，必须显式过一遍以下检查项；任一不满足都继续补搜，而不是"感觉够了"就前进。把结果写成固定标题「检索收敛声明」写进 `.workflow/search_log.md`（或等效工作文件）：

```markdown
## 检索收敛声明
- 研究简报子方向数：N
- 每子方向核心文献 ≥3 篇：是/否（各方向篇数）
- 末轮滚雪球新增入选：0 篇（向后/向前各 X 轮）
- 时效探针已执行：是/否（窗口：YYYY-MM-DD 至 YYYY-MM-DD）
- 多源覆盖：sciverse / arXiv / OpenAlex / 网页核验 各已执行：是/否
- 盲区检查：已列出 K 个已知盲区
- **裁判型文献定向检索：每个子主题至少执行一次，记录命中/未命中：是/否**
- 是否进入阶段二：是 / 继续补搜（理由）
```

**检查项细则**：

1. **每子方向 ≥3 篇核心文献**：核心 = 与研究简报 RQ 直接相关、已做存在性核验、拟进入台账。子方向来自研究简报或 orchestration.md 的 MECE 拆分。
2. **滚雪球一轮零新增**：以当前入选文献为种子，向后（REFERENCES）和向前（CITATIONS 或 `filters_advanced` 反查）各跑一轮，没有新增可入选文献。
3. **时效探针已执行**：按本文件"时效精度分级"为每个子方向选档，执行一次限定时间窗口的检索，记录命中数（可为 0）。
4. **多源至少两源覆盖**：sciverse 为主，arXiv / OpenAlex / Crossref/网页核验 至少再执行一源，避免单源偏差。
5. **盲区已记录而非掩盖**：把"搜不到但应该有的方向"列出来，作为开放问题素材；不许删除或假装不存在。
6. **显式判定**：用一句话给出 `has_enough_context_for_synthesis` 结论。`true` 才允许进阶段二；`false` 必须写清"缺哪块、下一步补搜关键词"。

> 本检查表把 research-depth.md 第 9 条"Planner 够了没闸门"和主 SKILL.md"滚雪球至饱和"落实成阶段切换前的强制出口，防止模型在上下文压力下"差不多就行"。

