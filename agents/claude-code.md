# Claude Code 适配

## Skill

```bash
ln -s <仓库根目录>/skills/sciverse-deep-research ~/.claude/skills/sciverse-deep-research
```

（`<仓库根目录>` 替换为你本机克隆仓库的绝对路径，下同。或运行仓库根目录的 `install.sh`，会自动检测并链接。）

## MCP

方式一（推荐，CLI）：

```bash
claude mcp add -s user sciverse \
  -e SCIVERSE_API_TOKEN=<你的token> \
  -- npx -y sciverse-mcp-server

claude mcp add -s user sciverse-survey-gates \
  -- ~/.local/bin/uv run --project <仓库根目录>/mcp-server sciverse-survey-gates
```

方式二（手写 `~/.claude.json` 的 `mcpServers` 节）：

```json
{
  "mcpServers": {
    "sciverse": {
      "command": "npx",
      "args": ["-y", "sciverse-mcp-server"],
      "env": { "SCIVERSE_API_TOKEN": "<你的token>" }
    },
    "sciverse-survey-gates": {
      "command": "~/.local/bin/uv",
      "args": ["run", "--project", "<仓库根目录>/mcp-server", "sciverse-survey-gates"]
    }
  }
}
```

## 备注

- 网页工具映射：WebSearch / WebFetch，skill 内通用表述可直接对应。
- 代码执行：Claude Code 有 Bash，skill 的脚本门禁（`scripts/citation_ledger.py` 等）可直接本地跑，MCP 门禁 server 作为双保险。
