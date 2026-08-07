# HANDOFF.md — sciverse-deep-research 开发交接手册

> **读这段的 Agent 或开发者**：你即将接手 `sciverse-deep-research` 的后续开发。
> 本文档是一次自包含的交接：项目是什么、当前进度、已完成的关键工作、
> 你要接手的待办、以及怎么安全地继续。读完本文档 + `AGENT-BOOTSTRAP.md`
> + `SKILL.md`，你就应该能无缝接手。

---

## 0. 一句话

这是一个**开源"research Harness"**：让**任意 AI Agent**（Codex / Claude Code / Kimi Code /
Hermes / Qwen Code / OpenCode）获得**学术深度文献调研**能力——通过标准的 **MCP 工具协议
（数据源 + 门禁）** + **SKILL.md（纯 Markdown 流程指令）**，任何支持 MCP 的 agent
都能接入，用**它自己带的 LLM** 驱动调研管线。用户（材料科学研究者）的真实诉求是：
造一个"替代 SLACK 模型"的**第一性原理晶格热导率数据集**。

## 1. 现在在哪 / Git 状态（交接基准线）

- 本地路径：**`/Users/qzp/科研项目/sciverse-deep-research/`**
- GitHub 远端：`https://github.com/whyihaveyou/sciverse-deep-research.git`（public）
- 当前分支 / HEAD：`main` @ `c9cc18e`（本地=origin，工作树干净）
- 最近 10 个 commit 即最新成果史（见 `git log --oneline`）；完整提交史已 push

⚠️ **路径注意**：项目曾位于 `~/sciverse-deep-research`，已迁移到
`/Users/qzp/科研项目/sciverse-deep-research/`。**所有文档里的绝对路径已更新**，
但**本机 MCP 配置里的绝对路径可能还是旧路径**——若某个 mock 找不到 server，
先检查 `~/.hermes/config.yaml` 与 `~/.kimi-code/mcp.json` 的 `--project` 指向。

## 2. 目录结构（谁是谁）

```
科研项目/sciverse-deep-research/
├── AGENT-BOOTSTRAP.md      # ★ AI-Ready 装配引导：任意 agent 按三步配好 MCP+skill（第一步读它）
├── README.md               # 项目总览 + 快速开始
├── install.sh              # skill 符号链接安装脚本（自动检测本机 agent）
├── agents/                 # 7 个 agent 逐一适配说明（claude-code/codex/kimi/qwen/opencode/...）
├── mcp-server/             # 本项目自带门禁 MCP（sciverse-survey-gates，uv 本地）
│   └── sciverse_survey_gates/
├── skills/
│   └── sciverse-deep-research/
│       ├── SKILL.md        # ★ 核心：完整调研流程指令（Step0→检索→铸台账→综合→门禁交付）
│       ├── references/     # 12 份方法论文档（search-strategy / orchestration / research-depth / ...）
│       └── scripts/        # 6 个 Python 脚本（工具层，零依赖 stdlib）
├── examples/
│   ├── spectral-dimension-demo/   # 基准示例（6 篇）
│   └── dft-kL-demo/               # ★ 核心 demo：DFT物理量清单 + 晶格热导率 Overlap
│       ├── .workflow/             # 隐藏：管线中间产物（台账/草稿/final）
│       └── output/                # 交付物（PDF + MD，不隐藏）
```

## 3. 核心架构（必须理解的三层）

| 层 | 技术 | 作用 |
|---|---|---|
| **数据源层** | sciverse MCP（`SCIVERSE_API_TOKEN`） | 学术检索：search_papers / semantic_search / list_paper_relations / read_content / list_catalog / get_resource |
| **门禁层** | sciverse-survey-gates MCP（无 token，本地 uv） | survey_ledger_validate / survey_compile / survey_check / survey_verify_citations |
| **推理层** | **宿主 agent 自带的 LLM** | 规划/综合/判断——不绑定，谁接入用谁的 |
| **工具层** | scripts/*.py（stdlib 零依赖） | 台账铸号 / 门禁检查 / LaTeX 探测 / PDF 转换 / arXiv+OpenAlex 多源 |

**关键设计**：检索走 sciverse（统一数据源，保证文献质量），**LLM 完全用主机自己的**，
所以任意 agent 不需要给这个工具额外配 LLM。PDF 是**可选的**——只在 `detect_latex.py`
判定本机装了 LaTeX（`pdf_offered=true`）时提供；否则纯 Markdown。MD 始终是唯一事实源。

## 4. 已完成的关键工作（最近的，别重复做）

**a) PDF 渲染器彻底修好（md_to_pdf.py v2）** — commit f8a53b4
- 修了：GFM 表格→`longtable`（此前完全不渲染）、希腊字母 κ/θ/γ→`$\kappa$`、
  ★→`$\bigstar$`、→∧≥×⅓ 等→`\ensuremath`、中引号/间隔点映射、
  零宽组合符删除、`\bigstar` 二次转义破坏
- 验证：见代码内注释 + 每次改动用 `hermes-verify-*` 临时脚本（已清理）
- 之前版本公式/表格乱码的根因都在这里修掉了

**b) 章节去自动编号** — commit 31b87a0
- 改为 `\section*` 系列，消除"LaTeX 数字 + 手写序号"双重编号混乱

**c) 编排模式落地** — commit 66ac54f
- 新建 `references/orchestration.md`：子问题并行深挖（O0-O4）+ 无损合并 + 反思补搜
- SKILL.md 加了"编排 vs 顺序"分流（能否拆 ≥2 个独立子问题来判定）

**d) DeerFlow + 通义 DeepResearch 核实 + 融合** — commit 9820de3
- **DeerFlow = `bytedance/deer-flow`**（79.4k★, 2.0=Agent Skills harness；1.x=多智能体调研闭环）
- **通义 = `Alibaba-NLP/DeepResearch`**（19.8k★, arXiv:2510.24701）
- 融合 6 条写进 `references/research-depth.md` 第 9-14 条
  （Planner"够了没"闸门 / 长程摘要落盘 / test-time scaling 档位 / 动态大纲 / 并行子智能体 / 多源引用对读）

**e) DFT 核心 demo**（用户真实任务）— commit 66ac54f / 31b87a0 深化
- `examples/dft-kL-demo/output/` 有交付：**DFT 能算物理量清单 + 与晶格热导率 κ_L 的 Overlap**
- 17 篇台账、14 篇草稿引用、门禁全绿（FAIL 0 / WARN 0）、中文 PDF 已生成
- 核心结论：DFT 可算 ∧ 与 κ_L 相关 = { B, G, ρ, V, N, γ, θ_D, θ_ac, Cv, α, v_s, 声子频率, 三阶力常数, κ_L(BTE) }
  ——前 10 项正是用户 AFLOW 里来自 Slack 的字段，用他们的 MLIP-DFT 工具重算即得独立真值特征集
- 关键文献：Broido2007（DFT算κL开山基准，Si/Ge<5%）、PhononOlympics2025（造库方法指南）

**f) Kimi Code 端到端测试通过** — commit c9cc18e
- 用本机 Kimi Code 0.33 + MCP 真实调 search_papers 返回文献、读懂 SKILL.md、跑通门禁
- **证明"任意 Agent 可接入"不是口号**
- 顺手修了：Kimi skill 断链（路径迁移后）、Kimi mcp.json 补门禁 server

## 5. 你要接手的待办（按优先级）

### P0 — 回晶格导热项目，落地真值数据集方案（用户的终极目的）
用户已有 **MLIP-DFT 工具**（机器学习势 + DFT），要造**替代 SLACK 的第一性 κ_L 数据集**。
基于 `dft-kL-demo` 的 overlap 结论，给一份**可执行技术方案**：
- 用他们的 MLIP-DFT 工具重算 { B, G, γ, θ_D, θ_ac, Cv, α }（AFLOW 里这些是 Slack 输出）
- κ_L 用 BTE 级真值（谐+三阶力常数+BTE），接 VASP/Phono3py/ShengBTE
- 分层：真值层（BTE/MLIP）+ 筛选层（你们的符号回归公式初筛）+ 校验层（实验 κ_L 校准集）
- 按 PhononOlympics2025 的 best-practice 标准化超胞/位移/截断协议
- **交付形态**：技术方案文档 + 命令骨架，不是理论

### P1 — 5 轮循环 + 自评（用户原始要求）
- 用优化后 Harness 测多轮，每轮"优化→测试→读产出→再优化"，至少 5 轮
- **自评方法需先与用户确认**：用户建议"单独调 DeepSeek API 多次平均"，但本会话无 API 凭证。
  - 方案 A：用户提供 DeepSeek/其他 API key，用 LLM-as-judge 多次平均
  - 方案 B：无 key 时用客观指标（门禁 FAIL/WARN 数、来源数、每章节字数、覆盖度）
  - **接手时先问用户选哪个**，不要擅自假设

### P1 — 白箱参考 deer-flow（深化融合）
- 目的：用户想"对比 DeerFlow 和我们的调研轨迹"找出差距
- **注意**：本机到 GitHub 极慢（~15KB/s，clone 2.7GB 卡 11 分钟、tarball 超时截断）。
  已实测放弃直接 clone。
- 已知可参考：子代理核实报告在
  `/Users/qzp/.hermes/cache/delegation/subagent-summary-0-20260806_205056_238798.txt`
- 用户提到**另一台 Linux 机 `pjnl261070127`** 可能有 clone，`ssh pjnl261070127`（主机可连，
  但返回 `Permission denied`——**需要用户给那台机的 SSH 访问**）。接手后可问用户能否上去查。
- 若不联网：按子代理报告 + 本地 2.0 的 `.agent/skills/` 生态白箱对比即可

### P2 — 其他
- AGENT-BOOTSTRAP 的"Hermes 用命令配置"示例里路径已是新路径（已修）；但若用户重装/新机器，跑 install.sh 即可
- 可考虑把 Kimi 端到端测试的具体命令补进 `agents/kimi-code.md` 作为验证记录（未做）
- `fetch_sources.py` 的 OpenAlex 曾遇 429 限流（共享 IP），重试即可；脚本错误处理正确

## 6. 环境与约束（接手必读）

- **零依赖哲学**：scripts/ 全部 Python 标准库、不引 pandoc。改脚本要保持。
- **LaTeX**：本机 TeX Live 2026 在 `/Library/TeX/texbin`（不在默认 PATH，detect_latex 已探测）；
  中文 PDF 用 ctex+xelatex；**无 pandoc**（不要引入）
- **MCP token**：SCIVERSE_API_TOKEN 在本机 `~/.hermes/config.yaml` 和 `~/.kimi-code/mcp.json`。
  **安全红线：绝不 commit 进 git**。交接后确认 git 里 0 处 token（`grep -c ghp_ .git/config` 应=0）
- **git 身份**：仍是占位符 `qzp / qzp@example.com`，如需真实身份找用户要
- **GitHub push**：本机无 gh 登录态，靠一次性 token URL push（用完清 tracking）。或让用户配好凭据

## 7. 验证方式（怎么知道做对了）

- **门禁**：`python3 skills/sciverse-deep-research/scripts/check_report.py final.md --citation-ledger ...delivery.json`
  应输出 `FAIL 0 / WARN 0`
- **台账**：`citation_ledger.py validate --ledger examples/spectral-dimension-demo/.workflow/citation_ledger.json`
  → FAIL 0
- **PDF**：`python3 skills/sciverse-deep-research/scripts/md_to_pdf.py <final.md> --keep-tex`
  应 exit 0 出 PDF；改渲染器后用临时验证脚本（见 scripts 注释）
- **LaTeX 探测**：`python3 skills/sciverse-deep-research/scripts/detect_latex.py` → level=full
- **AI-Ready**：`kimi -p "..."`（npx/uv 配好 MCP 后）应能调 search_papers

## 8. 沟通 / 交付偏好（用户）

- **中文回复**
- 技术改动要**大白话、按时间线衔接已知内容、每轮结束解释"这轮做了什么"**
- 多步任务先列 todo + 逐步汇报进度
- 最终交付物放**不隐藏目录**（如 `examples/<demo>/output/`），给**绝对路径**
- 用户是材料科学研究者，GitHub 账号 whyihaveyou，熟悉 git/Go/PR

## 9. 下一步第一条指令（可直接发）

> "继续 sciverse-deep-research 的研发。先读 HANDOFF.md 了解交接，确认 git 在 c9cc18e。
> 第一步优先级最高的是回晶格导热项目——基于 dft-kL-demo 的 overlap 清单，给一份
> 用现有 MLIP-DFT 工具造第一性晶格热导率数据集的**可执行技术方案**（接 VASP/Phono3py/ShengBTE，
> 分层：真值+筛选+校验）。先列 todo，逐步汇报。自评方法（DeepSeek API 或客观指标）先问用户。"

---

*交接基准：`c9cc18e` on `main`，工作树干净。写于 2026-08-07。*
