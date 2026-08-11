# Hermes 适配

> **装配引导**：本节是 Hermes 宿主的适配细节。你若想一步步完成 skill + 两个 MCP server 的
> 配置，请先读仓库根 **[`AGENT-BOOTSTRAP.md`](../AGENT-BOOTSTRAP.md)**——那是一段
> Agent-Ready 的引导流程，本节只补充 Hermes 特有的路径与命令。

## Skill

Hermes 兼容 agentskills.io 的 SKILL.md（约 99%，仅 frontmatter 字段位置有小差异）。
注意：Hermes 的 skill 必须放在**分类子目录**（`research/*`）下才会被扫描识别，放顶层 `~/.hermes/skills/sciverse-deep-research` 识别不到：

```bash
mkdir -p ~/.hermes/skills/research
ln -s <仓库根目录>/skills/sciverse-deep-research ~/.hermes/skills/research/sciverse-deep-research
```

（`<仓库根目录>` 替换为你本机克隆仓库的绝对路径，下同。）

装好后用 `hermes skills list | grep sciverse` 确认出现在 `research` 分类且为 `enabled`。

## MCP

Hermes 的 MCP 配置格式请以其当前版本文档为准（生态仍在快速变动）。
需要配置的两个 server 与所有 agent 相同：

- `sciverse`：`npx -y sciverse-mcp-server`，env `SCIVERSE_API_TOKEN`
- `sciverse-survey-gates`：`uv run --project <仓库根目录>/mcp-server sciverse-survey-gates`

若 Hermes 版本不支持 MCP 或 skill 加载有坑，退路：把 `skills/sciverse-deep-research/SKILL.md`
的内容粘贴进会话/AGENTS.md 使用，脚本门禁经其 shell 工具直接执行。

## 备注

- 已知兼容性问题跟踪：NousResearch/hermes-agent#31241（frontmatter 字段位置）。
