# 检索策略细则

## 工具选型：sciverse MCP

- **`search_papers`（结构化过滤检索）**：主力检索工具。`query` 是 **BM25 全文关键词**，匹配标题/摘要/期刊名/关键词字段——写查询词时按关键词思维构造，不要写整句自然语言。结构化过滤（任一命中即可）：`title_contains`（标题含词）、`authors`、`journals`（**用规范化载体名**，如 "Nature Communications" 而不是 "Nat Commun"——拿不准先用 `list_catalog` 看取值样本）、`year_from`/`year_to`、`subjects`。排序：`sort_by_year` 与 `query` 模糊检索的相关性排序互斥，`freshness_boost`（MILD 近 10 年加权 / STRONG 近 3 年加权）与 `sort_by_year` 互斥——追时效时在两者之间二选一，不要假设可以叠加。`filters_advanced` 是逃生舱：OA 状态（`access_oa_status`）、DOI 精确匹配等任意字段过滤，可用字段与取值先 `list_catalog` 学，不要猜字段名。
- **`semantic_search`（自然语言检索）**：适合"怎么问比怎么搜更自然"的场景——机制性问题、跨术语概念。返回的是**论文切片**（chunk + doc_id + offset），不是整篇条目；拿到切片后用 `read_content(doc_id, offset)` 扩读上下文，需要题录时再用 `search_papers` 按标题/unique_id 补齐。三个 mode 的速度-质量权衡：`fast` 仅关键词召回（~200ms，适合探针式粗扫）、`balanced` 混合检索（默认，~600ms）、`quality` LLM 改写 + 混合（~2-4s，留给深问题式的关键检索）。
- **`list_catalog`**：学字段 schema 与枚举值（如 `access_oa_status` 的合法取值）。遇到"这个字段能不能过滤、取值是什么"时调用，毫秒级，不要凭记忆猜。
- **`list_paper_relations`（滚雪球主力）**：以入选文献的 `unique_id` 为种子，`relation=REFERENCES`（我引用了谁，向后找前置）/ `CITATIONS`（谁引用了我，向前找后继）/ `RELATED_WORKS`（相关工作）。**CITATIONS 有两个硬限制**：关系总数超 10000 返回 429、page×page_size 超 10000 返回 400——高被引种子论文撞限后，改走 `search_papers` 的 `filters_advanced` 加 `references_unique_id`（查"引用了某篇论文"的工作），它支持深翻页与任意排序，可叠加年份等条件（如"引用了 ResNet 且 2023 年后发表"）。
- **`read_content`**：读论文全文切片，用于引述准确性对读（见 `references/citation-protocol.md`）。

## 关键词构造

关键词不是想到什么搜什么。按以下模式系统构造（`search_papers` 的 `query` 用）：

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

## 盲区发现

第二轮检索后做一次盲区检查：

1. **覆盖检查**：研究简报的每个子方向是否有 ≥3 篇文献？
2. **流派检查**：有没有明显的方法流派完全缺席？
3. **引用链检查**：已找到的论文引用的高频工作是否在列表里？（用 `list_paper_relations` REFERENCES 直接查，不靠印象）
4. **弃置检查**（STORM moderator trick）："搜到了但没打算用"的结果是否指向未覆盖的子方向？不要扔掉它们——它们是盲区的线索。
5. **时间检查**：近 1 年有没有重要工作？全是老论文说明可能漏了新进展。（收尾时另有硬性时效探针：宣布饱和前每视角一轮近 6-12 个月限定检索——`search_papers` 加 `year_from` 或 `freshness_boost: STRONG`，见主 SKILL.md 阶段一第五步饱和判据。）

## 按学科调整检索

不同学科的文献分布不同：

- **CS/AI**：arXiv 预印本为主，更新极快，近 6 个月的工作可能关键。时效探针取 6 个月窗口；`freshness_boost: STRONG` 适合追最新进展。
- **生物医学**：NEJM/Lancet/Nature Medicine 的临床论文，搜 "clinical trial" + 疾病名；可用 `journals` 参数限定规范化期刊名。
- **社科**：AER/QJE（经济学）、Nature Human Behaviour（心理学），搜效应量和方法（RCT/DID/IV）。
- **跨学科**：分别搜每个相关学科（`subjects` 参数过滤），再合并。不要只搜一个学科的关键词。
