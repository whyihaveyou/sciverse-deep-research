# OpenCode + DeepSeek 谱维数综述 · 格式轮验证（v2）

## 运行条件

- **日期**：2026-08-13
- **Agent / LLM**：OpenCode CLI + `deepseek-chat`
- **Skill 版本**：main @ 9e8932d（含第五轮 harness 架构 + 第六轮 P0/P1/P2 + 过程工件闸口 + 格式轮 8 条硬条款）
- **工作目录**：`.scratch/opencode-run-spectral-v2/`
- **运行日志**：`.scratch/opencode-research-run-spectral-v2.log`
- **Prompt**（已冻结 Step 0 决策，避免阻塞）：
  > 用 Markdown 交付、信息源只用 sciverse。帮我调研谱维数（spectral dimension）与随机行走（random walks）、同步（synchronization）、共识动力学（consensus dynamics）之间关系的研究进展，出一份小综述

## 核心指标

| 指标 | 数值 |
|---|---|
| 入选文献数 | 20 篇 |
| 核验通过率 | 20/20 VERIFIED（100%） |
| `check_report` 默认模式（对 `final.md` / `output/交付.md`） | FAIL 0 / WARN 0 / INFO 0 |
| `check_report --strict-process` | FAIL 0 / WARN 0 / INFO 0 |
| `check_report --strict-format` | FAIL 0 / WARN 0 / INFO 0 |
| wall-clock 用时 | 约 15–20 分钟（交付稿自述） |
| 检索调用次数 | `search_papers` 约 8 次（未计 `list_paper_relations` 辅助） |

## 过程工件（强制可观测）

- `.workflow/section_reviews.md`：4 个 section_review 块（分支一/二/三 + 综合/开放/结论），含 `claims_verification` / `L3_L4_verdict` / `evidence_gaps` / `patch_plan` 四字段。
- `.workflow/evidence_compress.md`：3 个视角压缩块，共 20 条文献状态标记（✅/⚠️），含盲区检查。

## 8 条格式硬条款执行对比（v1 → v2）

| 条款 | v1（旧版 skill） | v2（格式轮后） | 闸口闭环证据 |
|---|---|---|---|
| 1. 章节顺序冻结 | ✓ 顺序正确 | ✓ 顺序正确 | 无 WARN |
| 2. 关键引用三要素 | ✗ 用中文弯引号 `“...”` | ✓ ASCII 直引号 `"..."` | 无 WARN |
| 3. 禁止行内加粗代替子标题 | ✗ 研究方法/结论/综合讨论大量 `**标签**：内容` | ✓ 研究方法改为散文，分支内用 `###` 小节 | 默认模式 WARN 0（v1 为 12 条） |
| 4. 表格 caption + 列数一致 | ✗ 两个表均无 caption | ✓ 分类框架表有 `表 1：...` caption | 无 WARN（v1 缺 caption） |
| 5. 数学与化学符号分野 | ✓ 数学变量进 `$...$` | ✓ 无化学符号，数学全进 `$...$` | 无 WARN |
| 6. 调研成本六字段 | △ 有字段但 wall-clock/token 写“未记录” | ✓ 六字段齐全，含估算值 | 无 WARN |
| 7. 统一直引号 | ✗ 参考文献标题全用弯引号 | ✓ 全用 ASCII 直引号 | 无 WARN（v1 25 条弯引号 WARN） |
| 8. 段落长度（软条款 INFO） | 基本合规 | 基本合规 | 无 INFO |

**量化对比**：

- v1 默认模式：`FAIL 0 / WARN 37 / INFO 0`
- v2 默认模式：`FAIL 0 / WARN 0 / INFO 0`
- `--strict-format` 下 v1 全升 FAIL（37 FAIL），v2 仍为 0。

## 质量观察

- **结构**：v2 完全按格式硬条款的章节骨架，关键引用、摘要、核心要点、分支、综合讨论、开放问题、结论、调研成本、参考文献一应俱全。
- **子标题**：v2 在分支章节内使用 `###` 子标题组织（如“从扩散热核到谱维数”“Kuramoto 同步的临界谱维数”），避免了 v1 的 `**裁决**` / `**交叉对比**` 等行内加粗标签。
- **表格**：v2 的分类框架表加了 caption 并包含结论性表题，v1 两个表都缺 caption。
- **引用格式**：v2 关键引用与参考文献均使用 ASCII 直引号，解决了 v1 全篇弯引号问题。
- **调研成本**：v2 给出 wall-clock 和 token 估算，v1 仅写“未记录”。
- **内容**：两篇综述覆盖方向一致（随机行走 / 同步 / 共识），v2 更强调“谱同源性”这一跨分支 L3/L4 洞见，并把“共识文献中谱维数未成显式工具”作为 gap 披露。

## 交付文件

- `output/交付.md`：最终交付综述（`export-clean` 数学干净视图，ASCII 直引号保留）
- `.workflow/final.md`：编译后数字编号正文
- `.workflow/draft.md`：键值草稿
- `.workflow/citation_ledger.json` + `.delivery.json`：引用台账
- `.workflow/section_reviews.md`：节级审稿审计轨迹
- `.workflow/evidence_compress.md`：证据压缩块

## 结论

格式轮 8 条硬条款 + check_report 格式闸口在本题上完全闭环：v2 默认/strict 模式下均为 0 WARN/0 FAIL，过程工件齐全，`export-clean` 交付视图也通过了 strict-format 闸口。主要改进体现在**直引号统一、表格 caption、行内加粗标签消除、调研成本六字段补齐**四个方面。
