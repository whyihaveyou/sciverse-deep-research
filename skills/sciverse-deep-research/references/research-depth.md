# research-depth.md — 让综述"更长更深、多信息源、自我反思"的机制

> 来源:对主流开源 deep-research 框架的架构调研（open_deep_research、
> gpt-researcher、通义 DeepResearch 论文家族、dzhng/deep-research 等），
> 提炼出的、对本 skill 管线可直接落地的优化。每条注明**借自谁**与**为何能治什么**。

## 治"内容太短"的三条（最高杠杆）

### 1. 无损证据合并稿（借 open_deep_research 的 compress / 通义 ReSum；直接治"短"）
综合前，先产出一份"研究发现合并稿"作为**中间物**（写入 `.workflow/evidence_merge.md`）：
- 规则：**逐字保留、不总结、不丢信息**；多篇论文的同质陈述合并（"三篇都报道 X"）；
  每句带 `[@引用键]`；末尾列全部来源与检索式。
- 目的：报告深度由这个**显式无损地基**决定，而不是由综合时的上下文压缩决定。
  ReSum 论文（arXiv:2509.13313）证明：长程检索里先无损压缩证据再进推理，
  能防上下文溢出、支撑更长调研。
- 落地动作：阶段二综合的第一步，先合并证据稿，再进入主题聚类。

### 2. prompt 显式约束长度与深度（借 open_deep_research final_report / gpt-researcher "2000+字"）
呈现阶段的写作指令写死：
- 每节**尽量长且详细**、段落式为主；动态大纲；覆盖全部相关证据；与提问同语言。
- 零成本、立即见效——把"篇幅充分"从隐性希望变成显式约束。

### 3. 反思多轮收敛（借 think_tool / dzhng "critique→re-search→update"；激活现有补搜循环）
每节**写前 + 写后**自答："缺哪篇 / 哪句无出处 / 哪里矛盾"；
不满足就让 Coverage/Insight/Weaving 门禁**回调阶段一补搜后再回来重写**，
而不是申报一次 FAIL 就算过。这正好把现有"补搜-加深"循环从单次申报变成真正的多轮到收敛。

## 治"深度不够"的两条

### 4. 证据充分性置信度门禁（借通义 BrowseConf 测试时扩展，arXiv:2510.23458）
每个子方向对"证据够不够撑起 RQ/结论"打一个置信分：
- 低置信 → 自动触发针对性补搜，直到收敛。
- 把 Coverage 从**二值 FAIL** 变成**可驱动迭代的梯度**，直击"深度不够"。

### 5. 多信息源真正并行（借 gpt-researcher planner 子问题 + open_deep_research 多源）
现有管线只有 sciverse 单源滚雪球。落地：
- planner 把问题拆成**可独立回答的子问题**，每个子问题设"≥2 个独立来源"硬约束
  （sciverse + OpenAlex citations/references + arXiv + Crossref/网页）。
- 多源**并行**检索后再无损合并（见第 1 条合并稿）。
- 把 `fetch_sources.py` 的 arXiv/OpenAlex 从"补充"提到"与主源并列"的地位。

## 治"结构散、易错绑"的一条

### 6. 动态大纲挂证据（借 WebWeaver 的"动态大纲→逐节点挂证据"）
把"每节开写前重打台账切片"升级为显式"**大纲节点 ↔ 引用键映射表**"：
先定 MECE 大纲 → 逐节点挂证据 → 写完核对每个节点挂载率（防"短"也防"错绑"）。
机器可校验：每个节点至少 ≥1 个 `[@键]`。

## 治"改进无法证明"的一条

### 7. 可复现评测基准（借 OpenHands 评测文化 / Deep Research Bench）
用客观指标证明"更长更深"，而非主观感受：报告字数、来源数、每句引文密度、
门禁 CLEAR 率。有能力可提交 Deep Research Bench 得 RACE 基线。

## 治"成本上限"的一条

### 8. 分层模型/预算分工（借 open_deep_research summarization=小模型 + report=强模型）
证据抽取/检索摘要用 fast 便宜模型批量做；综合/裁决/报告用强模型。
把"深"留给强模型、"全"交给廉价批量抽取，不增加成本上限。
