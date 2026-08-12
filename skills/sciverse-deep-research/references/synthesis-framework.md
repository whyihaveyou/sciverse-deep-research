# 综合框架

## 三步法详细流程

### 第一步：引文抽取

对每篇论文抽取 4 项信息：
- **核心发现**：一两句话
- **方法特征**：和其他论文的方法区别
- **适用条件**：什么条件下成立，已知局限
- **关系网**：支持/挑战/扩展了谁

**固定字段名（与子 agent 元数据抽取对齐）**：

```json
{
  "paper_key": "[@PatchCore] 或 unique_id",
  "title": "论文标题",
  "authors": "第一作者等",
  "year": "发表年份",
  "research_question": "1 句话：解决什么问题",
  "methodology": "1-2 句话：怎么解决的",
  "key_findings": ["3-5 条 bullet：实际发现"],
  "limitations": "1-2 句话：作者承认或显而易见的局限",
  "relation_to_others": "支持/挑战/扩展了哪类工作（含具体 @key）",
  "evidence_chunks": [
    {"doc_id": "...", "offset": 0, "quote": "支持核心发现的一句原文"}
  ]
}
```

`evidence_chunks` 是可选但强烈建议的字段：记录 1-3 条支持该论文核心发现的原文章节（doc_id + offset + 短引文）。它把 SurveyMaster 的"段落级 citation grounding" 落地为可检查的中间产物——综合阶段写 claim 时可直接引用这些片段，减少张冠李戴。

批量抽取时（如 orchestration.md 的 subagent batching），子 agent 返回上述 JSON 数组，主 agent 直接用于主题聚类，不二次转述。不相关的论文整篇丢弃。

### 第二步：主题聚类

按**研究问题或方法流派**聚类。每个主题标记呈现方式：

- **paragraph**：多篇论文的细致综合，关系复杂时用散文
- **table**：3 篇以上可比工作的并排对比

**MECE taxonomy 设计规则**：
- 分类轴互斥且完备
- 空格 = gap = finding（"尚无工作将 X 应用于 Y"本身就是发现）
- 跨分类的论文单独讨论（它们挑战了分类轴本身）
- 如果某轴导致太多跨分类，换轴

### 第三步：逐节串行合成

每节输入 = 研究简报 + 该节分配的文献 + 已写好的前面几节。

串行保证连贯、避免重复、使过渡自然。

## 交叉对比写法

**反面**（逐篇罗列）：
> Smith et al. (2024) proposed method A for task X and achieved 85% accuracy. Lee et al. (2025) proposed method B for task X and achieved 87% accuracy.

**正面**（句内对比）：
> While Smith et al. [1] and Lee et al. [2] both target task X, they take fundamentally different approaches: Smith et al. leverage retrieval augmentation, achieving 85%, whereas Lee et al. rely on in-context learning, reaching 87% but at 3x the inference cost. Notably, Wang et al. [3] show that the retrieval-based strategy generalizes better to the related task Y, suggesting broader applicability despite the lower headline number.

**规则**：每个主题段落至少一个句子同时引用并对比 2+ 篇论文。

## 段落级 citation grounding

综述的每个 claim 段落、每个结构性元素都必须能被读者追溯到具体来源。执行纪律：

- **claim 段落 ≥1 个引用**：除明确的过渡/ framing 段落外，任何包含实质判断、数值、方法描述或归因的段落都必须带有 `[编号]` 引用。
- **结构性元素点名必引用**：关键引用节、核心要点 bullet、分类框架表/对比表的单元格、研究方法中的关键词族，凡出现具体论文/系统/方法/材料名，同行或同条必须带 `[编号]`；禁止把方法/材料名当普通名词裸放在这些结构里。
- **无引用段落显式标注**：若某段确实只是过渡句，必须在段首或段尾标注 `[无引用：过渡句]`，否则视为 citation grounding 失败。
- **引述不悬空**："多项研究表明..." 这类无名声明必须给出具体文献；无法给出时改为"目前证据尚不足以点名具体研究"，禁止用模糊概括冒充共识。
- **证据片段可回查**：对关键 claim，优先引用 `evidence_chunks` 中记录的 doc_id+offset；引述准确性核验时直接对读原文切片。

这是把 SciMaster/SurveyMaster "section-wise generation with explicit citation linking" 落到本地 skill 的写作纪律：不需要专有 citation graph，只靠"每段有源、每源可核验"。

## 对比表设计

- 列 = 对比维度（方法特征、优势、局限、指标），不是论文属性
- 行 = 具体工作
- **caption 包含结论**（"Table 1: 基于检索的方法在召回率上领先，但推理延迟是端到端方法的 3-5 倍"）
- 缺失信息填"未报告"，不留空不编数字
- 去掉稀疏列（只有 1-2 篇报告的维度不适合做列）

## 洞见深度纪律（每个分支 ≥1 条 L3/L4）

综合阶段不是"按分类把文献讲完"，而是要让读者得到"读完全部入选摘要也得不到"的判断。
执行本纪律前必须先读 `references/insight-protocol.md` 的 L0–L4 结论阶梯。

**硬性要求**：
- 每个分类分支（或每个主题聚类）必须至少产出 **1 条 L3（机制解释）或 L4（可执行协议/判据/研究设计）**级洞见。
- 达不到时，不允许在该分支写"收尾判断（≥L2）"就前进；必须**回路由阶段一补挖裁判型文献或边界条件文献**，把机制或协议"赚到"后再写。
- 分支内部的 L3/L4 可以来自：
  - 入选文献自身给出的机制解释（但要标注是该文献的结论还是你的推断）；
  - 多文献交叉对比后你才能给出的推断（必须显式写推理链：前提文献[编号] → 推断步骤 → 结论）；
  - 证据缺口本身被规格化（"缺少用 X 方法在 Y 体系上的研究来裁决 Z 争议"），这合法计入 L3/L4。

**L1–L4 判定示例（以本次 κL 对照实验为例）**：

| 级 | 形态 | κL 主题示例 |
|---|---|---|
| L1 | 聚合/分布 | "多篇工作报告四声子对 κ 的影响方向不一" |
| L2 | 裁决（有条件立场） | "四声子对 κ 的贡献并非普适：BAs 中显著压低约 43%，MoS₂/MoSe₂ 中在收敛检验后可忽略" |
| L3 | 机制解释 | "力误差作为随机扰动增强低频声子散射，导致 MD 路线系统性低估 κ；BTE/力常数路线因统计平均而对同类误差不敏感" |
| L4 | 可执行协议/判据 | "热导导向的 MLIP 验收应纳入三阶力常数复现精度 + 小体系 Green–Kubo 对照 + 力误差噪声外推，而非仅报告力 RMSE" |

**操作步骤**：
1. 分支写完后，自问："本节教给读者的新判断是什么？删掉所有引用后是否仍有判断？"
2. 把新判断标注 L 级；若最高只有 L2，回到 `references/search-strategy.md` 的"裁判型文献定向检索"补搜该分支的边界/失效/机制文献。
3. 把各分支 L3/L4 汇总进「洞见反思清单】（见 `references/insight-protocol.md`），全文 L3 不足 3 条或 L4 不足 1 条时，综合未收敛。

**禁止**：用"未来需要更多研究"或"各有优劣"替代 L3/L4；遇到缺口必须写清**缺什么设计/什么数据/能裁决哪个问题**，才算合法完成。

A 说 X 有效、B 说 X 无效时：
1. 摆出双方发现（A 说什么、B 说什么）
2. 分析条件差异（数据集？指标？设置？样本量？）
3. 能判断 → 给倾向（"在 Z 条件下 B 更有说服力"）
4. 不能判断 → "目前证据不足以判断，需在 W 条件下验证"

**不要**：写"存在争议"然后跳过；平均掉矛盾；只引支持一方的文献。

## Mini scattered-and-stacked 深度合成

当某个分支按常规三步法仍无法产出 L3/L4 级洞见（或面对明显矛盾却难以裁决）时，
借用 X-Master 的 **Solver / Critic / Rewriter / Selector** 工作流做一次小范围多解竞争。
**关键：这不是在脑中完成的抽象角色扮演，而是必须产出可审计的中间工件。**

### 触发条件（满足其一才触发）

- 分支洞见自检最高只有 L2，且回阶段一补搜后仍无法提升到 L3/L4；
- 分支内存在硬矛盾，常规裁决程序（列调节变量 → 建证据表 → 给条件化立场/证据缺口）走不下去；
- 用户 angle 或 RQ 依赖该分支必须给出机制级判断，不能简单带过。

**不滥用**：证据清晰、L3/L4 已经足够的分支不需要走此流程，避免不必要的成本。

### 执行格式：在 draft.md 中插入显式小节

触发后，在当前分支的 `draft.md` 键值草稿末尾追加一个**多解竞争草稿**小节，使用以下固定小标题，保证可观测、可审计：

```markdown
#### 多解竞争草稿（分支 X：XXX 主题）

##### 候选解读 A
- 核心 claim：...
- 支撑文献：[@键1][@键2]
- 解释逻辑：...

##### 候选解读 B
- 核心 claim：...
- 支撑文献：[@键3][@键4]
- 解释逻辑：...

##### Critic 批判
- 候选 A 的问题：...
- 候选 B 的问题：...
- 共同盲区：...

##### Rewriter 综合
- 吸收 A/B 的合理部分后，更优的解读是：...
- 对矛盾的处理（条件化裁决 / 证据缺口）：...

##### Selector 定稿
- 最终选择：...
- 选择理由（匹配度 / 推理链 / 限定条件）：...
```

**要求**：
- 每个候选解读必须明确核心 claim 和 2-3 篇关键文献；
- Critic 必须指出每个候选的**致命缺陷**或**不可修正之处**；
- Rewriter 必须处理矛盾，不能和稀泥；
- Selector 必须给出明确选择及理由，选择标准：与证据的匹配度 > 观点新颖度 > 表达流畅度。

### 与最终交付物的关系

多解竞争草稿是内部审计工件，不进入交付综述正文； Selector 定稿的结论作为该分支最终洞见，按正常流程写入分支章节。

## 结构化草稿审稿（section_review）

综合阶段每完成一节正文草稿后、进入下一节前，必须执行一次结构化审稿并产出**强制可观测工件**。这是把 EvoMaster 的 trace→analyze→patch 循环和 ML-Master 的 `review_func_spec` 迁移到综述写作：不依赖模型自觉，而是把 critique 写成固定格式代码块，留在 `draft.md` 中作为审计痕迹。

### 触发时机（硬性）

- 每个分支章节写完后；
- 综合讨论、开放问题、结论写完后；
- 若章节较长（>800 中文字符或含 3 个以上 claim），可在小节末尾追加一次 mid-section review。

**未产出 section_review 块不得进入下一节。**

### 输出格式（固定，可判定）

在 `draft.md` 当前章节末尾追加一个固定字段的代码块：

```markdown
```section_review: 分支 X / 综合讨论 / 结论
- claims_verification:
  - claim_1: "..." → supported_by: [@键1][@键2]; status: 直接支持/弱支持/无支持
  - claim_2: "..." → supported_by: [@键3]; status: ...
- L3_L4_verdict:
  - 本节最高洞见等级：L1/L2/L3/L4（按 insight-protocol.md）
  - L3/L4 级洞见原文（若有）："..."
- evidence_gaps:
  - 反向证据或限定条件：...（无则写"无"）
  - 需补搜/对读才能确认的 claim：...
  - 需降级表述的 claim：...
- patch_plan: 无需修订 / 补搜 X / 改写 Y / 删除 Z / 启用 Mini scattered-and-stacked
```
```

### 判定规则（全部满足方可进入下一节）

1. `claims_verification` 列出本节每个实质 claim；每个 claim 至少有一个 `直接支持` 的引用键；`弱支持`/`无支持` 的 claim 必须在 `patch_plan` 中说明如何补强或降级。
2. `L3_L4_verdict` 明确本节最高洞见等级；分支章节必须至少含 1 条 L3/L4 级洞见，否则 `patch_plan` 必须是"补搜裁判型文献"或"启用 Mini scattered-and-stacked"，不允许写"无需修订"。
3. `evidence_gaps` 不得为空或写"无缺口"来敷衍； genuinely 无缺口时写"已覆盖"并给出理由。
4. `patch_plan` 具体可执行；需要补搜时必须写明关键词/检索工具/预期填补的 claim。

**未通过审稿**：按 `patch_plan` 回阶段一补搜、或在本节内改写、或启用 Mini scattered-and-stacked 多解竞争；不允许带病推进。

### 与交付物的关系

`section_review` 块是**内部审计工件**，保留在 `draft.md` 中，**compile 时不进入 `final.md`**，也**不得因为"担心污染交付物"而在 compile 前删除**。它把 `check_report.py` 的引用/洞见检查点前移到写作阶段，减少最终门禁返工。若 `draft.md` 中找不到 section_review 块，视为阶段二未按流程执行。

## Related Work 思维骨架（每节必过）

写每个主题章节前，脑子里过一遍：

1. **claim**：这些工作放在一起告诉我们什么？
2. **正面证据**：哪几篇最直接支持？独立来源收敛？
3. **反面证据**：哪些工作矛盾或限定了 claim？
4. **条件差异**：正反分歧怎么解释？
5. **跨主题连接**：和其他主题什么关系？

骨架不打印，驱动散文。

**自检**：删掉引用后剩下的还是一篇有判断的分析 → 通过。只剩事实罗列 → 论证链没搭好。
