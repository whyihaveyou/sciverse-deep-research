# Hermes 适配

## Skill

Hermes 兼容 agentskills.io 的 SKILL.md（约 99%，仅 frontmatter 字段位置有小差异）。
注意：Hermes 的 skill 必须放在**分类子目录**（`research/*`）下才会被扫描识别，放顶层 `~/.hermes/skills/sciverse-deep-research` 识别不到：

```bash
mkdir -p ~/.hermes/skills/research
ln -s ~/sciverse-deep-research/skills/sciverse-deep-research ~/.hermes/skills/research/sciverse-deep-research
```

装好后用 `hermes skills list | grep sciverse` 确认出现在 `research` 分类且为 `enabled`。

## MCP

Hermes 的 MCP 配置格式请以其当前版本文档为准（生态仍在快速变动）。
需要配置的两个 server 与所有 agent 相同：

- `sciverse`：`npx -y sciverse-mcp-server`，env `SCIVERSE_API_TOKEN`
- `sciverse-survey-gates`：`uv run --project ~/sciverse-deep-research/mcp-server sciverse-survey-gates`

若 Hermes 版本不支持 MCP 或 skill 加载有坑，退路：把 `skills/sciverse-deep-research/SKILL.md`
的内容粘贴进会话/AGENTS.md 使用，脚本门禁经其 shell 工具直接执行。

## 备注

- 已知兼容性问题跟踪：NousResearch/hermes-agent#31241（frontmatter 字段位置）。
