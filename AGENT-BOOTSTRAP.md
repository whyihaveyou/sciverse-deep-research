# AGENT-BOOTSTRAP.md — Agent 接入引导（Agent-Ready）

> **读这段的人（或 Agent）**：你是一个被请求在本机装配 `sciverse-deep-research`
> 学术深度调研模块的 AI Agent（Codex / Claude Code / Kimi Code / Hermes / 其他）。
> 下面的内容是一段**可直接执行的引导**：请按顺序完成三步，每步都有可验证的
> 通过标准。目标是让本机任意 Agent 框架都能调用 sciverse 检索 + 本仓库门禁。

本文件是"一开始的引导过程"。读完并执行完，你的宿主就具备了深度文献调研能力。

---

## 你将要装配的东西：两个 MCP server

| Server | 角色 | 工具 |
|---|---|---|
| `sciverse` | 学术文献检索（官方） | search_papers / semantic_search / list_catalog / list_paper_relations / read_content / get_resource |
| `sciverse-survey-gates` | 本仓库门禁（随 skill 分发） | survey_ledger_validate / survey_compile / survey_check / survey_verify_citations |

核心调研逻辑在 `skills/sciverse-deep-research/SKILL.md` 里（引用键编译 → 门禁验收），
两个 MCP 一是数据源、一是机械门禁，二者都要配齐。

---

## Step 0 — 先确定你的宿主 Agent 是谁

不同的 Agent 配置 MCP 的位置不同。先确认你在哪个框架里运行，去对应的落点写配置：

- **Hermes**：`~/.hermes/config.yaml` 的 `mcp_servers:`（推荐用 `hermes mcp add` 命令，见 Step 2）
- **Kimi Code**：`~/.kimi-code/mcp.json`（`mcpServers` 键）
- **Claude Code**：`.mcp.json` 或 `~/.claude.json`
- **Codex / OpenCode / Qwen Code / OpenClaw**：见本仓库 `agents/` 目录逐一说明

> 如果你不确定，用 `ls ~/.claude ~/.codex ~/.kimi-code ~/.config/opencode ~/.agents ~/.hermes 2>/dev/null` 探测哪个存在。

---

## Step 1 — 安装 skill（一份，多 agent 符号链接）

skill 本体在 `~/sciverse-deep-research/skills/sciverse-deep-research`。直接跑安装脚本：

```bash
~/sciverse-deep-research/install.sh
```

它会自动检测本机已装 agent 并符号链接 skill。**注意**：Hermes 的 skill 必须放在
分类子目录（`~/.hermes/skills/research/sciverse-deep-research`）才会被识别，这是本仓库
已修正过的坑——install.sh 已按此处理。

通过标准：`install.sh` 输出你所在 agent 的"已链接/跳过"。

---

## Step 2 — 配置两个 MCP server

### 前置：确认 PATH 里有 npx 和 uv，用绝对路径最稳

很多 Agent 框架启动 MCP 子进程时会**过滤环境变量**（只保留 PATH/HOME 等基线变量），
API Token 和自定义 PATH 都要显式传。先用 `which npx uv` 找到绝对路径（典型：
`/Users/<你>/.local/bin/npx`、`/Users/<你>/.local/bin/uv`）。

### 2a. sciverse 官方检索 server

需要 **SCIVERSE_API_TOKEN**（从 https://sciverse.space 控制台「密钥」页获取）。

- **Hermes（推荐用命令）**：
  ```bash
  hermes mcp add sciverse \
    --env "SCIVERSE_API_TOKEN=<你的 token>" \
    --command npx --args -y sciverse-mcp-server
  ```
  ⚠️ **坑（实测）**：`--env` 必须写在 `--args` **之前**。`--args` 是"最后位置参数"
  （argparse 把其后所有内容吞进 args），若 token 跟在 `--args` 后面会被错塞进命令行，
  连接必失败。配完验证：`hermes mcp test sciverse` 应列出 6 个工具、`hermes mcp list`
  显示 enabled。

- **其他 Agent（手写配置，示例为通用 .mcp.json）**：
  ```json
  {
    "mcpServers": {
      "sciverse": {
        "command": "/Users/<你>/.local/bin/npx",
        "args": ["-y", "sciverse-mcp-server"],
        "env": {
          "SCIVERSE_API_TOKEN": "<你的 token>",
          "PATH": "/Users/<你>/.local/bin:/Users/<你>/.hermes/node/bin:/usr/local/bin:/usr/bin:/bin"
        }
      }
    }
  }
  ```

> **安全红线**：token 只写进本机配置文件（config.yaml / mcp.json），**绝不 commit 进
> 任何 git 文件或公开分享**。`~/.hermes/.env`、`~/.gitignore` 之外的任何位置出现 token
> 都要警惕。

### 2b. sciverse-survey-gates 门禁 server（本项目自带）

- **Hermes（命令）**：
  ```bash
  hermes mcp add sciverse-survey-gates \
    --command uv --args run --project /Users/<你>/sciverse-deep-research/mcp-server sciverse-survey-gates
  ```
  这个无 token，连接稳定，通常一次成功（会列出 4 个 survey_* 工具）。

- **其他 Agent（.mcp.json）**：
  ```json
  {
    "mcpServers": {
      "sciverse-survey-gates": {
        "command": "/Users/<你>/.local/bin/uv",
        "args": ["run", "--project", "/Users/<你>/sciverse-deep-research/mcp-server", "sciverse-survey-gates"]
      }
    }
  }
  ```

---

## Step 3 — 验证（全部通过才算配好）

1. **连接验证**：`hermes mcp test sciverse` 应列出 6 工具；`hermes mcp test sciverse-survey-gates` 应列出 4 工具。
2. **真实调用验证**（最关键）：新建会话，让 Agent 调一次 `search_papers`（例如 query="spectral dimension"，page_size=2），应返回真实文献数据（作者/DOI/年份），而不是报错或空。
3. **门禁链路验证**（可选但推荐）：用仓库自带示例跑一次
   `skills/sciverse-deep-research/scripts/citation_ledger.py validate --ledger examples/spectral-dimension-demo/.workflow/citation_ledger.json`，应输出 `FAIL 0`。

> 注意：MCP 工具通常在**新会话**才注入（启动时发现）。配好后要开新会话才能用。

---

## Step 3.5 — 可选能力（不需要额外装配，随 skill 分发）

以下两项在 skill 里，**装上 skill 即具备**，不需要额外配置 MCP：

- **多信息源**：`skills/sciverse-deep-research/scripts/fetch_sources.py` 直接检索 arXiv / OpenAlex
  （零依赖 HTTP），不必配 MCP。可用 `python3 .../fetch_sources.py --list` 验证。
- **PDF 输出**：`detect_latex.py` 探测本机 LaTeX 能力，可用时 `md_to_pdf.py` 把 final.md
  渲染成中文 PDF。先跑 `python3 .../detect_latex.py` 确认 `level=full`/`pdf_offered=true`。

---

## 排错速查

| 症状 | 原因 / 解法 |
|---|---|
| `Connection closed` / 连接失败 | npx/uv 不在过滤器放行的 PATH 里 → 用绝对路径 command + 在 env 补 PATH |
| token 没生效 | `--env` 放到了 `--args` 之后（Hermes）→ 调到前面 |
| 401 Unauthorized | SCIVERSE_API_TOKEN 缺失或写错 → 检查控制台「密钥」页 |
| 工具找不到 | 配好后没开新会话 → 重开会话让工具注入 |
| `No MCP servers configured` | config.yaml 无 `mcp_servers:` 或为空 → 重新 `hermes mcp add` |

---

## 收尾：这段引导应该被谁读？

本文件应置于项目 README 的开头（"快速开始"第一段），并在 `agents/*.md` 顶部引用，
让任何一个 Agent（人或机器）第一次接触本仓库时就先读它。它把"配置 MCP"从手动贴
代码，变成了 Agent 可自主执行的一趟流程。
