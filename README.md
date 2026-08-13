# sciverse-deep-research

一个**跨 Agent 框架的学术深度调研模块**：让任意 Agent（Kimi Code / Claude Code / Codex / OpenCode / Hermes / Qwen Code / OpenClaw）获得系统文献调研能力，对一个研究话题做检索、综合与引用核验，最终产出结构严谨、引用可靠的专业综述（survey paper）。

一句话：sciverse 负责"搜得到、查得准"，本模块负责"引得对、关把得住"。

## 它能做什么

- 给定一个研究方向，自动冻结 2-3 个可回答的研究问题（RQ）。
- 多视角检索 + 引文网络滚雪球到饱和，支持 sciverse 学术检索、arXiv、OpenAlex。
- 用"引用键"机制写草稿，数字编号与参考文献由脚本同一趟从台账铸造——模型不手写编号，错绑在语法上不可表达。
- 交付前过机械门禁：编号连续性、正文↔台账↔参考文献三方对齐、裸 URL/DOI、题录字段只抄不编。
- 可选中文 PDF 排版视图；Markdown 始终是事实源。

### 真实效果：同一弱模型、同一 prompt，三轮改进肉眼可见

我们在"机器学习势函数 × 晶格热导率"这一固定题目上，用 **OpenCode + deepseek-chat** 跑了三轮同 prompt 对照：

| 版本 | 日期 | 文献数 | 运行时间 | 关键差异 |
|---|---|---|---|---|
| [v1 旧版 skill](examples/opencode-mlp-kL-demo/) | 2026-08-11 | 22 | 7m18s | 泛泛而谈，被用户认为"不够专业"。 |
| [v2  DeerFlow 改进后](examples/opencode-mlp-kL-demo-v2/) | 2026-08-11 | 24 | 6m30s | 挖到裁判型文献（Wu 2024 力误差校正、Kocabas 2025 MoS₂/MoSe₂ 四声子可忽略），FAIL 0 / WARN 1。 |
| [v3  第三轮改进后](examples/opencode-mlp-kL-demo-v3/) | 2026-08-11 | 22 | 8m45s | 显式执行裁判型文献定向检索 + 每分支 L3/L4 强制洞见纪律，分支收尾出现深度判断，FAIL 0 / WARN 1。 |
| [Kimi Code 对照组](examples/kimi-mlp-kL-demo/) | 2026-08-11 | 25 | ~18m | 最强模型产出，方法学批判与框架最深。 |

这是本模块区别于其他 deep-research 工具的地方：**不只是 prompt 变长，而是把 DeerFlow 白箱研究里可验证的优势条款（收敛检查表、step_type 纪律、检索预算、固定元数据字段、报告结构前置）写进了 skill，并用同一弱模型证明了效果提升。** 详细分析见 `.scratch/deerflow-deep-dive.md`（工作产物，未入库）。

## 谁该读哪份（2×2）

| 阶段 | 给 **人** | 给 **Agent** |
|---|---|---|
| **安装** | [HUMAN-QUICKSTART.md](HUMAN-QUICKSTART.md)（人只做 4 件事） | [AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md)（任意框架 3 步自装配） |
| **使用** | [HUMAN-QUICKSTART.md](HUMAN-QUICKSTART.md)（一句话丢任务） | `SKILL.md`（运行时完整流程） |

- **你（人）**：装 Agent → 要一个 sciverse token → 克隆仓库 → 跑 `./install.sh`，然后 **一句话让 Agent 做综述**。详见 [HUMAN-QUICKSTART.md](HUMAN-QUICKSTART.md)。
- **你的 Agent**：让它读 [AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md)，它会自己配好 skill + 两个 MCP server（人不需要会写 MCP 配置）。

## 快速开始

```bash
git clone https://github.com/whyihaveyou/sciverse-deep-research.git
cd sciverse-deep-research && ./install.sh
```

`install.sh` 自动检测本机已装的 agent，把 skill 符号链接进去，并打印两个 MCP server 的配置片段（不改动任何配置文件）：

1. **sciverse**（官方检索）：`npx -y sciverse-mcp-server`，env `SCIVERSE_API_TOKEN`
2. **sciverse-survey-gates**（本仓库门禁）：`uv run --project <仓库根目录>/mcp-server sciverse-survey-gates`

各 agent 的具体配置见 `agents/*.md`。

## 核心机制

- **门禁驱动而非步骤驱动**：7 维内部质量门禁（Angle / Coverage / Citation / Insight / Taxonomy / Calibration / Weaving），不通过就路由回对应阶段重做；检索收敛判据是滚雪球饱和，不是固定轮数。
- **引用键 + 编译铸号**：草稿全程用 `[@引用键]` 写作，数字编号和参考文献由 `citation_ledger.py compile` 同一趟从台账铸造——模型从不手写编号、从不写参考文献，错绑在草稿语法上不可表达。
- **题录只抄不编**：卷 / 期 / 页码 / DOI / 期刊等级只能来自 Crossref 或官方页面（`verify_citations.py` 三通道瀑布 + 篇级完备性闸门），查不到标"未核验"。
- **多源与滚雪球**：sciverse 为主（`search_papers` / `semantic_search` / `list_paper_relations` / `read_content`），arXiv / OpenAlex 为辅（`fetch_sources.py`），网页工具仅用于题录核验。
- **PDF 可选**：本机有 LaTeX 时才提供 PDF 渲染；Markdown 始终唯一事实源。
- **机械验收承重**：`check_report.py` 做编号连续性、三方对齐、正文裸 URL/DOI、声明报数清点等可机械判定的检查，任何 FAIL 未消解不得交付。

## 支持的 Agent

7 家主流 Agent 框架已写适配文档；其中 3 家已完成端到端真实综述验证：

| Agent | 适配文档 | 端到端验证 |
|---|---|---|
| Hermes | [agents/hermes.md](agents/hermes.md) | 2026-08-13，产物 [examples/hermes-spectral-dimension-demo/](examples/hermes-spectral-dimension-demo/) |
| Kimi Code | [agents/kimi-code.md](agents/kimi-code.md) | 2026-08-11，产物 [examples/kimi-mlp-kL-demo/](examples/kimi-mlp-kL-demo/) |
| OpenCode | [agents/opencode.md](agents/opencode.md) | 2026-08-11，产物 [examples/opencode-mlp-kL-demo-v3/](examples/opencode-mlp-kL-demo-v3/)；2026-08-13 谱维数格式轮验证 [examples/opencode-spectral-dimension-demo-v2/](examples/opencode-spectral-dimension-demo-v2/) |
| Claude Code | [agents/claude-code.md](agents/claude-code.md) | 文档适配，待实测 |
| Codex | [agents/codex.md](agents/codex.md) | 文档适配，待实测 |
| Qwen Code | [agents/qwen-code.md](agents/qwen-code.md) | 文档适配，待实测 |
| OpenClaw | [agents/openclaw.md](agents/openclaw.md) | 文档适配，待实测 |

## 目录结构

```
sciverse-deep-research/
├── skills/sciverse-deep-research/   # 核心 skill（SKILL.md + references + scripts）
│   ├── SKILL.md                     # 管线编排：Step0 → RQ 冻结 → 检索 → 编号冻结 → 综合 → 交付编译(+PDF)
│   ├── references/                  # 12 份方法论文档（检索策略/编排/质量门禁/引述协议/题录核验手册等）
│   └── scripts/                     # 确定性脚本（Python 标准库，零依赖）
│       ├── citation_ledger.py       #   引用台账：validate / compile / renumber / csv
│       ├── check_report.py          #   交付前机械门禁
│       ├── verify_citations.py      #   Crossref 题录批量核验
│       ├── detect_latex.py          #   探测本机 LaTeX 能力
│       ├── md_to_pdf.py             #   final.md → 中文 PDF
│       └── fetch_sources.py         #   arXiv / OpenAlex 多源检索
├── mcp-server/                      # sciverse-survey-gates：把四个确定性步骤暴露为 MCP 工具
├── agents/                          # 7 个 agent 适配文档
├── examples/                        # 端到端真实用例
│   ├── spectral-dimension-demo/              # 6 篇文献小型综述，FAIL 0 / WARN 0
│   ├── space-compute-demo/                   # 14 篇空间算力综述 + PDF
│   ├── opencode-mlp-kL-demo/                 # OpenCode v1 旧版 skill 基线
│   ├── opencode-mlp-kL-demo-v2/              # DeerFlow 改进后同 prompt 重跑
│   ├── opencode-mlp-kL-demo-v3/              # 第三轮改进后验证
│   ├── kimi-mlp-kL-demo/                     # Kimi Code 对照组
│   ├── opencode-sse-ml-demo/                 # 新题泛化：机器学习 × 固态电解质
│   ├── opencode-spectral-dimension-demo/     # 谱维数 OpenCode v1（格式轮前）
│   ├── opencode-spectral-dimension-demo-v2/  # 谱维数格式轮验证版
│   └── hermes-spectral-dimension-demo/       # Hermes 第 4 家 Agent 端到端实证
├── AGENT-BOOTSTRAP.md               # Agent-Ready 引导
├── HUMAN-QUICKSTART.md              # 人向 Quickstart
└── install.sh                       # 检测本机 agent → symlink skill → 打印 MCP 配置片段
```

## 验证状态（2026-08-13，本机 macOS）

- 回归门禁：`python3 tests/run_regression.py` → **PASS 40 / FAIL 0**（格式轮新增 13 个格式/过程工件闸口用例）。
- MCP server：`uv run --project mcp-server python -c "import sciverse_survey_gates"` 通过；stdio 握手返回 `sciverse-survey-gates 3.4.5`。
- 端到端真实用例：
  - `examples/spectral-dimension-demo/`：sciverse 检索 → 台账 validate → compile → check_report **FAIL 0 / WARN 0**。
  - `examples/opencode-mlp-kL-demo-v3/`：OpenCode + deepseek-chat，22 篇，**FAIL 0 / WARN 1**。
  - `examples/kimi-mlp-kL-demo/`：Kimi Code + ark-code-latest，25 篇，**FAIL 0 / WARN 0**。
  - `examples/opencode-sse-ml-demo/`：新题泛化（机器学习 × 固态电解质），30 篇，**FAIL 0 / WARN 2**（2 条启发式近邻误报）。
  - `examples/opencode-spectral-dimension-demo-v2/`：格式轮验证，20 篇，默认/strict-process/strict-format 均为 **FAIL 0 / WARN 0 / INFO 0**。
  - `examples/hermes-spectral-dimension-demo/`：Hermes 第 4 家 Agent 实证，19 篇，默认/strict-process/strict-format 均为 **FAIL 0 / WARN 0 / INFO 0**。
- 题录核验：`python3 skills/sciverse-deep-research/scripts/verify_citations.py --probe` 确认 Crossref 在线双向可达（网络正常时）。

## 已知限制

- `search_papers` 默认返回不含卷期页码 DOI，venue 字段偶有不准——严格模式务必走 Crossref 通道。
- sciverse 对中文期刊覆盖有限；CNKI/CSSCI 场景按 skill 检索纪律走网页工具定向 + 题录核验。
- Kimi Code 不支持嵌套 skill 目录（本 skill 已扁平化规避）；Hermes / OpenClaw 的 MCP 配置格式以其官方文档为准。
- 引用绑定检查只覆盖点名句；无名声明句的绑定靠综合阶段的台账切片纪律（skill 内如实声明了该覆盖边界）。
