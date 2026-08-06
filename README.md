# sciverse-deep-research

基于 [Sciverse](https://github.com/opendatalab/Sciverse-Agent-Tools) 学术检索 MCP 的**跨 agent 学术深度调研模块**：对一个研究话题做系统文献调研，产出结构严谨、引用可靠的专业综述（survey paper）。

一句话：sciverse 负责"搜得到、查得准"，本模块负责"引得对、关把得住"。

## 三层结构

```
sciverse-deep-research/
├── skills/sciverse-deep-research/   # 核心 skill（SKILL.md + references + scripts）
│   ├── SKILL.md                     # 管线编排：RQ 冻结 → 检索 → 编号冻结 → 综合 → 交付编译
│   ├── references/                  # 10 份方法论文档（检索策略/质量门禁/引述协议/题录核验手册等）
│   └── scripts/                     # 三个确定性脚本（Python 标准库，零依赖）
│       ├── citation_ledger.py       #   引用台账：validate / compile / renumber / csv
│       ├── check_report.py          #   交付前机械门禁（正文↔台账↔参考文献三方对齐等）
│       └── verify_citations.py      #   Crossref 题录批量核验（卷期页码 DOI 只抄不编）
├── mcp-server/                      # sciverse-survey-gates：把四个确定性步骤暴露为 MCP 工具
├── agents/                          # 各 agent 适配文档（skill 路径 + MCP 配置片段）
├── examples/spectral-dimension-demo/# 端到端真实用例（6 篇文献的小型综述，全门禁通过）
└── install.sh                       # 检测本机 agent → symlink skill → 打印 MCP 配置片段
```

## 核心机制（移植自豆包学术综述 skill，检索层重写为 sciverse）

- **门禁驱动而非步骤驱动**：7 维内部质量门禁（Angle/Coverage/Citation/Insight/Taxonomy/Calibration/Weaving），不通过就路由回对应阶段重做；检索收敛判据是滚雪球饱和，不是轮数。
- **引用防幻觉（BibTeX 思路）**：草稿全程用 `[@引用键]` 写作，数字编号和参考文献由 `citation_ledger.py compile` 同一趟从台账铸造——模型从不手写编号、从不写参考文献，错绑在草稿语法上不可表达。
- **题录只抄不编**：卷/期/页码/DOI/期刊等级只能来自 Crossref 或官方页面（`verify_citations.py` 三通道瀑布 + 篇级完备性闸门），查不到标"未核验"。
- **sciverse 独有能力**：`list_paper_relations` 双向引文网络滚雪球、`read_content` 全文证据切片做引述准确性对读、`list_catalog` 学过滤字段（OA 状态、年份、学科）。
- **机械验收承重**：`check_report.py` 做编号连续性、三方对齐、正文裸 URL/DOI、声明报数清点等可机械判定的检查，任何 FAIL 未消解不得交付；交付说明末尾必须附 `summary:` 门禁足迹。

## 安装

```bash
~/sciverse-deep-research/install.sh
```

自动检测本机已装的 agent（Claude Code / Codex / Kimi Code / OpenCode / Qwen Code / Hermes / OpenClaw），symlink skill 并打印两个 MCP server 的配置片段（不改动任何配置文件）。各 agent 的具体配置见 `agents/*.md`。

需要两个 MCP server：

1. **sciverse**（官方检索）：`npx -y sciverse-mcp-server`，env `SCIVERSE_API_TOKEN`
2. **sciverse-survey-gates**（本仓库门禁）：`uv run --project <repo>/mcp-server sciverse-survey-gates`

skill 内的脚本也可由 agent 直接用 shell 跑（有代码执行环境时这是主路径，MCP 门禁 server 是双保险）。

## 使用

对 agent 说"帮我调研 X 领域 / 做个文献综述"即可触发。管线会：先冻结研究简报（2-3 个 RQ）→ 多视角检索 + 引文网络滚雪球至饱和 → 铸引用台账 → 键值草稿综合 → compile 铸号 → check_report 验收 → 交付 `final.md`。

题录严格模式（要 DOI/卷期页码/期刊等级时）自动启用 Crossref 核验与台账声明；也可以独立说"帮我核验这份参考文献"触发题录核验环节。

## 验证状态（2026-07-31，本机 macOS）

- 三个脚本 selftest 全 PASS；`verify_citations.py --probe` 确认 Crossref 在线双向可达
- MCP server 经 stdio 客户端实测：list_tools + validate/compile/check 全链路通过
- 端到端真实用例 `examples/spectral-dimension-demo/`：sciverse 检索 → 台账 validate → 键值草稿 → compile → check_report **FAIL 0 / WARN 0**（含 `list_paper_relations` 滚雪球与 `read_content` 对读实操）

## 已知限制

- `search_papers` 默认返回不含卷期页码 DOI，venue 字段偶有不准——严格模式务必走 Crossref 通道。
- sciverse 对中文期刊覆盖有限；CNKI/CSSCI 场景按 skill 的检索纪律走网页工具定向 + 题录核验。
- Kimi Code 不支持嵌套 skill 目录（本 skill 已扁平化规避）；Hermes / OpenClaw 的 MCP 配置格式以其官方文档为准（`agents/` 里有说明）。
- 引用绑定检查只覆盖点名句；无名声明句的绑定靠综合阶段的台账切片纪律（skill 内如实声明了该覆盖边界）。

## 渊源

方法论与门禁结构移植自豆包内部 `doubao-academic-researcher` skill（v6.1 思路：引用键 + 编译铸号 + 机械门禁），检索层重写为 sciverse MCP，并扁平化为单 skill 以兼容全部目标 agent。
