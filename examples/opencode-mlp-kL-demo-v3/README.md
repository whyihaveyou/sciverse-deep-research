# opencode-mlp-kL-demo-v3

**2026-08-11 第三轮改进后 skill 验证运行**——在 v2（第二轮改进）基础上追加
「裁判型文献定向检索」+「每分支 L3/L4 强制洞见纪律」，检验这些方法论条款对
OpenCode+DeepSeek 产出的实际拉升效果。

- 宿主：OpenCode 1.18.16 + deepseek-chat（与 v1/v2 完全相同）
- 调研题目：与 v1/v2 逐字相同（见 opencode-mlp-kL-demo/README.md）
- 运行指标：约 8 分 45 秒；67 步；22 篇文献；check_report 门禁 FAIL 0 / WARN 1
  （独立复核一致；WARN 为 L65 InSe 提及对象的良性误报，该句实际已带 [10] 引用）
- 完整运行日志：`.scratch/opencode-research-run-v3.log`（未入库）

## 目录

- `output/机器学习势函数_晶格热导率_综述.md` — 交付综述
- `.workflow/` — 管线工件：`citation_ledger.json`（22 条台账）、`draft.md`
  （键值草稿）、`final.md`（compile 产物）、`search_log.md`（检索日志，含
  裁判型文献标注）

## 与 v1/v2/Kimi 的关系

- **v1**（`examples/opencode-mlp-kL-demo/`）：旧版 skill，22 篇，泛泛而谈。
- **v2**（`examples/opencode-mlp-kL-demo-v2/`）：第二轮改进，24 篇，挖到 Wu 2024
  力误差校正、Kocabas 2025 MoS₂/MoSe₂ 四声子可忽略等关键裁判文献。
- **v3**（本目录）：第三轮改进，22 篇，显式执行了裁判型文献定向检索并写进
  `search_log.md`，分支收尾出现 L3/L4 级洞见；但仍未挖到 Kimi 版中的
  Langer 2023（消息传递势热流公式）、Póta/PFT（基础模型微调）、Ioffe-Regel
  阈值框架等顶级判据。
- **Kimi 组**（`examples/kimi-mlp-kL-demo/`）：25 篇，最深的方法学批判与框架。

四方对比报告见 leader 最终汇报。
