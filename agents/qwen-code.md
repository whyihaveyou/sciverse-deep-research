# Qwen Code 适配

## Skill

```bash
ln -s <仓库根目录>/skills/sciverse-deep-research ~/.agents/skills/sciverse-deep-research
```

（`<仓库根目录>` 替换为你本机克隆仓库的绝对路径，下同。Qwen Code 读取 `~/.agents/skills`；如你的版本用 `~/.qwen/skills`，链接到对应目录即可。）

## MCP

编辑 `~/.qwen/settings.json`：

```json
{
  "mcpServers": {
    "sciverse": {
      "command": "npx",
      "args": ["-y", "sciverse-mcp-server"],
      "env": { "SCIVERSE_API_TOKEN": "<你的token>" }
    },
    "sciverse-survey-gates": {
      "command": "/Users/<you>/.local/bin/uv",
      "args": ["run", "--project", "<仓库根目录>/mcp-server", "sciverse-survey-gates"]
    }
  }
}
```

## 备注

- 网页工具映射：Qwen Code 的 web_search / web_fetch。
