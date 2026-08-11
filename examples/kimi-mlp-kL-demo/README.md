# kimi-mlp-kL-demo

**2026-08-11 Kimi Code 对照实验产物**——与 `examples/opencode-mlp-kL-demo/` 同题目、
同 skill、同双 MCP server，控制变量仅"agent 框架 + 模型"，用于对比两份产出的质量差异。

- 宿主：Kimi Code CLI 0.34.0（headless `kimi -p`，config 默认 `default_permission_mode = "yolo"`；
  注意 `-p` 与 `-y/--auto` 均不可同用，headless 权限走 config 默认值）
- 模型：`ark/ark-code-latest`（config.toml default_model）
- 调研题目（与 OpenCode 那次逐字相同）：
  「帮我调研一下机器学习势函数在晶格热导率预测中的应用进展，出一份小综述。要求：用 sciverse
  检索工具找真实文献，综述用中文，按你可用的 sciverse-deep-research skill 的流程走
  （检索→综合→引用台账→门禁编译），最终产出 Markdown 文件。规模控制在小综述即可
  （15-25 篇文献）。」
- 运行指标：约 18 分钟；25 篇文献；check_report 门禁 FAIL 0 / WARN 0（独立复核一致）
- 完整运行日志：`.scratch/kimi-research-run.log`（未入库）

## 目录

- `output/机器学习势函数_晶格热导率_综述.md` — 对外交付版（check_report
  `--export-clean` 产物）
- `.workflow/` — 管线工件：`citation_ledger.json`（25 条引用台账）、`draft.md`
  （键值草稿）、`final.md`（compile 产物，内部事实源）、`insight_reflection.md`
  （洞见清单，本 run 特有工件）

## 与 opencode-mlp-kL-demo 的范围差异（如实说明）

本 run 在纳入标准中明确**排除了纯描述符回归式高通量筛选**（"纯性质回归式的高通量筛选
工作不纳入"），而 OpenCode 那次把直接回归列为三个分支之一；另外本 run 含 2 篇 arXiv
预印本与 2 篇不限年份的背景文献。这是 agent 自主的方法学决策差异，非人工干预。
