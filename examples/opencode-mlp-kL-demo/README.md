# opencode-mlp-kL-demo

**2026-08-11 OpenCode 裸机接入端到端实测产物**——验证"任意 Agent 均可按
AGENT-BOOTSTRAP.md 接入本仓库"的声称在 OpenCode 上成立。

- 宿主：OpenCode 1.18.16（npm 裸装，本机此前无 OpenCode）
- 模型：DeepSeek `deepseek-chat`（provider 手配，见 `agents/opencode.md`）
- 装配：skill 符号链接 + 两个 MCP server（sciverse 检索 + sciverse-survey-gates 门禁），
  全程约 30 分钟
- 调研运行：`opencode run` 非交互，82 步 / 7m18s / 22 篇真实文献，
  门禁 `check_report` FAIL 0 / WARN 0
- 调研主题：机器学习势函数（MLP）在晶格热导率预测中的应用进展

## 目录

- `output/机器学习势函数_晶格热导率_综述.md` — 对外交付版（check_report
  `--export-clean` 产物）
- `.workflow/` — 管线工件：`citation_ledger.json`（22 条引用台账）、`draft.md`
  （键值草稿）、`final.md`（compile 产物，内部事实源）、
  `citation_ledger.json.delivery.json`（交付台账）

实测过程与评价详见 `agents/opencode.md` 的「实测验证记录」一节。
