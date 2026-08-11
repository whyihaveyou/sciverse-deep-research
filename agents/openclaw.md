# OpenClaw 适配

## Skill

```bash
ln -s <仓库根目录>/skills/sciverse-deep-research ~/.openclaw/skills/sciverse-deep-research
```

（`<仓库根目录>` 替换为你本机克隆仓库的绝对路径，下同。OpenClaw 支持 skills 目录加载；也可考虑打包上传 ClawHub，见官方文档。）

## MCP

OpenClaw 的 MCP 配置格式请以其当前版本文档为准。需要的两个 server 与所有 agent 相同：

- `sciverse`：`npx -y sciverse-mcp-server`，env `SCIVERSE_API_TOKEN`
- `sciverse-survey-gates`：`uv run --project <仓库根目录>/mcp-server sciverse-survey-gates`

## 备注

- OpenClaw SkillHub 上已有学术类 skill（academic-deep-research），但无引用台账/机械门禁——
  本 skill 的差异化在 scripts/ 的三个确定性脚本与 7 维门禁。
