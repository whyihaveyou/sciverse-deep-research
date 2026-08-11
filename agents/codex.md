# Codex CLI 适配

## Skill

Codex 原生支持 SKILL.md（`~/.codex/skills/`，`$skill` 调用）：

```bash
ln -s <仓库根目录>/skills/sciverse-deep-research ~/.codex/skills/sciverse-deep-research
```

（`<仓库根目录>` 替换为你本机克隆仓库的绝对路径，下同。）

## MCP

编辑 `~/.codex/config.toml`：

```toml
[mcp_servers.sciverse]
command = "npx"
args = ["-y", "sciverse-mcp-server"]

[mcp_servers.sciverse.env]
SCIVERSE_API_TOKEN = "<你的token>"

[mcp_servers.sciverse-survey-gates]
command = "/Users/<you>/.local/bin/uv"
args = ["run", "--project", "<仓库根目录>/mcp-server", "sciverse-survey-gates"]
```

## 备注

- 网页工具映射：Codex 的 `web.run`。
- Codex 沙箱策略若限制网络，`verify_citations.py`（Crossref）可能失败——走混合模式（emit-urls + 网页工具取回 + from-dir），见 skill 的 citation-guard 章节。
