# Hermes + DeepSeek 谱维数综述 · 第 4 家 Agent 端到端实证

## 运行条件

- **日期**：2026-08-13
- **Agent / LLM**：Hermes CLI v0.20.0 + `deepseek-v4-flash-0731`（浦江 DeepSeek provider）
- **Skill 版本**：main @ 9e8932d（含第五轮 harness 架构 + 第六轮 P0/P1/P2 + 过程工件闸口 + 格式轮 8 条硬条款）
- **工作目录**：`.scratch/hermes-run-spectral/`
- **运行日志**：`.scratch/hermes-research-run-spectral.log`
- **Prompt**：
  > 帮我调研谱维数（spectral dimension）与随机行走（random walks）、同步（synchronization）、共识动力学（consensus dynamics）之间关系的研究进展，出一份小综述。

## 核心指标

| 指标 | 数值 |
|---|---|
| 入选文献数 | 19 篇 |
| 核验通过率 | 19/19 VERIFIED（100%） |
| `check_report` 默认模式 | FAIL 0 / WARN 0 / INFO 0 |
| `check_report --strict-process` | FAIL 0 / WARN 0 / INFO 0 |
| `check_report --strict-format` | FAIL 0 / WARN 0 / INFO 0 |
| wall-clock 用时 | 32 分 38 秒（日志：11:32:25 → 12:05:03） |
| API 调用次数 | 41 次 |
| 对话消息数 | 100 条 |
| prompt tokens 峰值 | 199,614 |
| total tokens 峰值 | 199,902 |
| 最终综述篇幅 | 167 行 / 约 24,800 字节 |

## 交付文件

- `output/final.md`：最终交付综述（编译后数字编号正文）
- `.workflow/draft.md`：键值草稿
- `.workflow/final.md`：与 `output/final.md` 同份文件
- `.workflow/citation_ledger.json` + `.workflow/citation_ledger.json.delivery.json`：引用台账与交付台账
- `.workflow/section_reviews.md`：节级审稿审计轨迹
- `.workflow/evidence_compress.md`：证据压缩块
- `.workflow/search_plan.md` / `.workflow/research_brief.md`：检索计划与研究简报

## 机制激活情况

| 机制 | 是否激活 | 痕迹位置 |
|---|---|---|
| RQ 冻结 / 收敛检查表 | ✅ | `search_plan.md`、正文“研究方法”节 |
| 过程工件闸口 | ✅ | `section_reviews.md`、`evidence_compress.md` 均存在且非空 |
| section_review 结构化审稿 | ✅ | `section_reviews.md` |
| 压缩块 ✅/⚠️/❌ 标记 | ✅ | `evidence_compress.md` |
| 段落级 citation grounding | ✅ | 正文每段末尾密集挂引用 |
| 效率附录（调研成本） | ✅ | `final.md` 第 11 节 |
| 格式轮 8 条硬条款 | ✅ | strict-format 0 FAIL / 0 WARN |

## 与 OpenCode + DeepSeek 谱维数 v2 的对比印象

| 维度 | Hermes + `deepseek-v4-flash-0731` | OpenCode + `deepseek-chat`（v2） |
|---|---|---|
| 文献数 | 19 篇 | 20 篇 |
| 核验率 | 19/19 VERIFIED | 20/20 VERIFIED |
| wall-clock | 32 分 38 秒 | 约 15–20 分钟 |
| API 调用 | 41 次 | 未精确记录 |
| prompt 峰值 | ~199k tokens | 未精确记录 |
| 结构纪律 | 章节顺序、关键引用、核心要点、综合讨论、开放问题、结论、调研成本齐全 | 同 v2 格式轮闭环 |
| 格式闸口 | 默认 / strict-process / strict-format 均为 0 | 默认 / strict-process / strict-format 均为 0 |
| 内容特点 | 突出“低临界维 $d_s=2$ / 上临界维 $d_s=4$”的统一框架，RQ 回答明确 | 更强调“谱同源性”与 L3/L4 洞见 |

**观察**：

- Hermes 运行的 `deepseek-v4-flash-0731` 在格式纪律上表现稳定：直引号、表格 caption、调研成本六字段、子标题层级均符合格式轮要求，strict-format 无 WARN。
- 该模型输出明显比 deepseek-chat 更“听话”——没有绕开格式条款，也没有用行内加粗代替子标题；这可能是 Hermes 版本能够一次通过 strict-format 的重要原因。
- 代价是时间明显更长（约 33 分钟 vs 约 15–20 分钟），且 prompt token 峰值接近 200k；初步判断是 Hermes 的 conversation loop 在长对话中保留的全量上下文更大，导致后期每次 API 调用都携带接近 200k 的 prompt。
- 两篇综述在核心结论上高度一致：$d_s=2$ 是随机行走 / 同步 / 共识共用的低临界维，$d_s=4$ 是同步平均场上临界维；差异主要在叙事重心，Hermes 版更偏向“统一框架 + RQ 逐条回答”，OpenCode v2 更偏向“跨分支洞见 + 格式条款逐项对比”。

## 结论

Hermes 作为第 4 家端到端验证的 Agent，在最新版 skill 上完成了谱维数题的完整闭环：引用核验 19/19、check_report 三种模式均为 0 FAIL/0 WARN、过程工件齐全、格式轮硬条款全部生效。该结果与 OpenCode 版形成模型/宿主差异的对照，说明 skill 的方法论层已具备跨 Agent 的稳定性。
