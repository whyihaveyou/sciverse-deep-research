# opencode-mlp-kL-demo-v2

**2026-08-11 改进后 skill 验证运行**——与 `examples/opencode-mlp-kL-demo/`
（v1，旧版 skill）和 `examples/kimi-mlp-kL-demo/`（Kimi Code 对照组）同题目，
用于检验 DeerFlow 白箱改进写进 skill 后的 OpenCode+DeepSeek 效果变化。

- 宿主：OpenCode 1.18.16（deepseek-chat，与 v1 完全一致）
- 调研题目：与 v1 逐字相同（见 opencode-mlp-kL-demo/README.md）
- 运行指标：约 6 分 30 秒；24 篇文献；check_report 门禁 FAIL 0 / WARN 1
  （独立复核：L69 点名未引用 `'PbTe'` 一处轻微 WARN，其余全绿）
- 完整运行日志：`.scratch/opencode-research-run-v2.log`（未入库）

## 目录

- `output/机器学习势函数_晶格热导率_综述.md` — 交付稿（check_report
  `--export-clean` 产物）
- `.workflow/` — 管线工件：`citation_ledger.json`（24 条引用台账）、`draft.md`
  （键值草稿）、`final.md`（compile 产物，内部事实源）

## 与 v1 和 Kimi 的关系

- **v1**（`examples/opencode-mlp-kL-demo/`）：旧版 skill，22 篇/7m18s/FAIL 0 WARN 0，
  质量被用户认为不够专业。
- **v2**（本目录）：改进后 skill 的 OpenCode 重跑，24 篇/6m30s/FAIL 0 WARN 1。
- **Kimi 组**（`examples/kimi-mlp-kL-demo/`）：同一题目，kimi CLI 0.34.0 +
  ark-code-latest，25 篇/约 18 分钟/FAIL 0 WARN 0。

三方对比报告见 leader 的最终汇报。
