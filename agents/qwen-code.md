# Qwen Code 适配

## Skill

```bash
ln -s ~/sciverse-deep-research/skills/sciverse-deep-research ~/.agents/skills/sciverse-deep-research
```

（Qwen Code 读取 `~/.agents/skills`；如你的版本用 `~/.qwen/skills`，链接到对应目录即可。）

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
      "args": ["run", "--project", "/Users/<you>/sciverse-deep-research/mcp-server", "sciverse-survey-gates"]
    }
  }
}
```

## 备注

- 网页工具映射：Qwen Code 的 web_search / web_fetch。
