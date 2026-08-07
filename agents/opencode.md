# OpenCode 适配

## Skill

OpenCode 完整实现 SKILL.md spec：

```bash
ln -s /Users/qzp/科研项目/sciverse-deep-research/skills/sciverse-deep-research ~/.config/opencode/skills/sciverse-deep-research
```

## MCP

编辑 `~/.config/opencode/opencode.json`：

```json
{
  "mcp": {
    "sciverse": {
      "type": "local",
      "command": ["npx", "-y", "sciverse-mcp-server"],
      "environment": { "SCIVERSE_API_TOKEN": "<你的token>" },
      "enabled": true
    },
    "sciverse-survey-gates": {
      "type": "local",
      "command": ["/Users/<you>/.local/bin/uv", "run", "--project",
                  "/Users/<you>/sciverse-deep-research/mcp-server", "sciverse-survey-gates"],
      "enabled": true
    }
  }
}
```

## 备注

- 网页工具映射：OpenCode 的 websearch / webfetch 工具。
