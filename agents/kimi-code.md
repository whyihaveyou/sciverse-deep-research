# Kimi Code 适配

## Skill

```bash
ln -s <仓库根目录>/skills/sciverse-deep-research ~/.kimi-code/skills/sciverse-deep-research
```

注意：`<仓库根目录>` 替换为你本机克隆仓库的绝对路径。Kimi Code 不支持嵌套 skill 目录（kimi-cli#1894），本 skill 已扁平化，直接可用。

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
      "args": ["run", "--project", "<仓库根目录>/mcp-server", "sciverse-survey-gates"]
    }
  }
}
```

（若你已有 sciverse 配置，只需追加第二个 server。）

## Headless（非交互）用法

用 `kimi -p "<prompt>"` 跑一次性任务时的坑（0.34.0 实测）：

- **`-p` 与 `-y` / `--auto` 均不可同用**——同用会直接 `error: Cannot combine --prompt with ...`
  报错退出。headless 模式的权限不走命令行旗标，而是走 `~/.kimi-code/config.toml` 的
  `default_permission_mode`；设为 `"yolo"` 后裸 `kimi -p` 即全自动（自动批准常规工具调用）。
- 想让 agent 自己写文件/跑脚本完成全流程（如本 skill 的台账与门禁），务必确认
  `default_permission_mode = "yolo"`，否则 headless 下无人可批准、流程会卡住或降级。

## 实测验证记录

- **2026-08-11**：Kimi Code CLI 0.34.0 + `ark/ark-code-latest`，headless（`kimi -p`，
  yolo 权限）跑"机器学习势函数 × 晶格热导率"小调研（与 OpenCode 对照实验同题目，
  逐字相同 prompt）：约 18 分钟、25 篇真实文献，台账 → 键值草稿 → compile →
  check_report 全链路走通，门禁 `FAIL 0 / WARN 0`（独立复核一致）。产物见
  `examples/kimi-mlp-kL-demo/`（对照组：`examples/opencode-mlp-kL-demo/`，
  OpenCode 1.18.16 + deepseek-chat，22 篇，同门禁全绿）。

## 备注

- 网页工具映射：WebSearch / FetchURL。
- 本地脚本门禁用 Bash 直接跑即可；MCP 门禁 server 二选一或并用。
