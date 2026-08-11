# OpenCode 适配

## Skill

OpenCode 完整实现 SKILL.md spec：

```bash
mkdir -p ~/.config/opencode/skills
ln -s <仓库根目录>/skills/sciverse-deep-research ~/.config/opencode/skills/sciverse-deep-research
```

（`<仓库根目录>` 替换为你本机克隆仓库的绝对路径，下同。install.sh 会自动完成这一步；
手工补链接时记得先 `mkdir -p`，否则 `ln -s` 会报 "No such file or directory"。）

## Provider（LLM）

OpenCode 的内置模型目录不含国产 provider 时，需在 `~/.config/opencode/opencode.json`
手写 `provider` 段。以 DeepSeek 为例：

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "deepseek/deepseek-chat",
  "provider": {
    "deepseek": {
      "options": {
        "apiKey": "<你的 DeepSeek API key>",
        "baseURL": "https://api.deepseek.com/v1"
      }
    }
  }
}
```

- 模型 ID 形如 `<provider>/<model>`，即 `deepseek/deepseek-chat`。
- **安全红线**：apiKey 只写本机 `~/.config/opencode/`，绝不写进项目仓库、绝不 commit。
- 官方文档：https://opencode.ai/docs/providers/ 与 https://opencode.ai/docs/config/ 。

## MCP

编辑 `~/.config/opencode/opencode.json`，在 `mcp` 键下加两个 server。**建议 command
一律用绝对路径**（与 AGENT-BOOTSTRAP Step 2 口径一致）：Agent 框架启动 MCP 子进程时
常只放行极简 PATH，GUI 启动或非登录 shell 场景下裸 `npx`/`uv` 会找不到，报
"Connection closed"。先 `which npx uv` 拿到本机绝对路径再填：

```json
{
  "mcp": {
    "sciverse": {
      "type": "local",
      "command": ["/Users/<you>/.local/opt/node/bin/npx", "-y", "sciverse-mcp-server"],
      "environment": {
        "SCIVERSE_API_TOKEN": "<你的token>",
        "PATH": "/Users/<you>/.local/opt/node/bin:/Users/<you>/.local/bin:/usr/local/bin:/usr/bin:/bin"
      },
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

注意 OpenCode 的 MCP 配置键名是 `environment`（不是 Claude/Kimi 风格的 `env`），
`command` 是数组（命令与参数合写）。

## 实测验证记录

- **2026-08-11**：OpenCode 1.18.16 + DeepSeek deepseek-chat，macOS 裸机接入（本机
  此前无 OpenCode）。从 npm 安装到两个 MCP server 连通约 30 分钟；随后用
  `opencode run` 非交互跑完整小调研（机器学习势函数 × 晶格热导率）：82 步 / 7m18s /
  22 篇真实文献，台账 → 键值草稿 → compile → check_report 全链路走通，门禁
  `FAIL 0 / WARN 0`。skill 被正确触发（agent 主动读取 references/*.md 并对齐管线）。
- 观察：该组合下 agent 倾向按 SKILL.md 文字直接跑 `scripts/citation_ledger.py` /
  `check_report.py` 完成门禁，而非调用 sciverse-survey-gates MCP 工具——两条路径结果
  等价，MCP 门禁主要价值是无 python 环境时的兜底。

## 备注

- 网页工具映射：OpenCode 的 websearch / webfetch 工具。
