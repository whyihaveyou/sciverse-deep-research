# Kimi Code 适配

## Skill

```bash
ln -s /Users/qzp/科研项目/sciverse-deep-research/skills/sciverse-deep-research ~/.kimi-code/skills/sciverse-deep-research
```

注意：Kimi Code 不支持嵌套 skill 目录（kimi-cli#1894），本 skill 已扁平化，直接可用。

## MCP

编辑 `~/.kimi-code/mcp.json`（本仓库就是按这个格式验证的）：

```json
{
  "mcpServers": {
    "sciverse": {
      "command": "/Users/<you>/.local/node/bin/npx",
      "args": ["-y", "sciverse-mcp-server"],
      "env": {
        "PATH": "/Users/<you>/.local/node/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
        "SCIVERSE_API_TOKEN": "<你的token>"
      }
    },
    "sciverse-survey-gates": {
      "command": "/Users/<you>/.local/bin/uv",
      "args": ["run", "--project", "/Users/<you>/sciverse-deep-research/mcp-server", "sciverse-survey-gates"]
    }
  }
}
```

（若你已有 sciverse 配置，只需追加第二个 server。）

## 备注

- 网页工具映射：WebSearch / FetchURL。
- 本地脚本门禁用 Bash 直接跑即可；MCP 门禁 server 二选一或并用。
