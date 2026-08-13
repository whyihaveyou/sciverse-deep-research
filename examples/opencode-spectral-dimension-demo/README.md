# 谱维数 × 随机行走 × 同步 × 共识动力学：最新版 skill 泛化验证

> 运行时间：2026-08-12  
> Agent / LLM：OpenCode + deepseek-chat  
> Skill 版本：main @ 9e8932d（含第五轮 harness 架构 + 第六轮 P0/P1/P2 + 过程工件闸口）  
> 题目："帮我调研谱维数（spectral dimension）与随机行走（random walks）、同步（synchronization）、共识动力学（consensus dynamics）之间关系的研究进展，出一份小综述"

## 目录

- `output/survey.md`：最终交付综述（即 `.workflow/final.md`）
- `output/交付.md`：含门禁足迹的交付说明
- `.workflow/`：完整过程工件
  - `draft.md`：草稿
  - `section_reviews.md`：结构化自批判审稿记录
  - `evidence_compress.md`：证据压缩块
  - `search_log.md`：检索日志（含意图演化记录）
  - `citation_ledger.json` / `citation_ledger.json.delivery.json`：引用台账

## 运行与复核结果

- **工作目录**：`.scratch/opencode-run-spectral/`
- **运行日志**：`.scratch/opencode-research-run-spectral.log`
- **独立复核**：`python3 skills/sciverse-deep-research/scripts/check_report.py .scratch/opencode-run-spectral/.workflow/final.md --citation-ledger .scratch/opencode-run-spectral/.workflow/citation_ledger.json.delivery.json`
  - 结果：`FAIL 0 / WARN 0 / INFO 0`
- **门禁状态**：通过（含过程工件闸口检查）

## 关键指标

| 指标 | 数值 |
|---|---|
| 入选文献数 | 23 篇 |
| 核验通过 | 21/23 VERIFIED；2/23 存在但题录未全核验（[20] 标注"未核验"） |
| 检索调用 | 15 次（`semantic_search` 9 次 + `search_papers` 6 次；`list_paper_relations` 1 次） |
| 检索轮次 | 3 视角定向检索 / 0 轮滚雪球 |
| wall-clock 用时 | ≈ 5 分钟（search_log 17:48 → final 17:54） |
| 最终综述篇幅 | ≈ 1,600 词（final.md 20,825 字节） |
| section_review 块 | 4 个 |
| evidence_compress 块 | 1 个（20 条 ✅ 标记） |

## 机制激活清单

| 机制 | 是否激活 | 痕迹位置 |
|---|---|---|
| RQ 冻结 / 收敛检查表 | ✅ | `search_log.md` 检索收敛声明 |
| 意图演化（updated_intent / missing_coverage） | ✅ | `search_log.md` 第 1 轮 |
| 裁判型文献定向检索 | ✅ | `search_log.md`、`evidence_compress.md` |
| 压缩块 ✅/⚠️/❌ 标记 | ✅ | `evidence_compress.md`（20 ✅ / 0 ⚠️ / 0 ❌） |
| section_review 结构化审稿 | ✅ | `section_reviews.md`（4 块） |
| L3/L4 洞见等级判定 | ✅ | `section_reviews.md` 每块 verdict |
| 段落级 citation grounding | ✅ | 最终报告正文每段末尾密集挂引用 |
| 过程工件闸口 | ✅ | 独立复核通过；`section_reviews.md` + `evidence_compress.md` 均存在且非空 |
| 效率附录 | ✅ | `final.md` 第 10 节"调研成本" |

## 与旧版 `examples/spectral-dimension-demo/` 的对比

旧版是同领域的早期基准 demo，主要差异：

- **文献规模**：旧版 6 篇（严格数学结果导向），新版 23 篇（覆盖定义/随机行走/同步/共识三分支）。
- **结构深度**：旧版按"平面型随机几何 vs 分形层级"两分；新版按"定义/随机行走/同步/共识"三分，并加入关键引用、核心要点、综合讨论、开放问题、调研成本等结构化章节。
- **洞见等级**：旧版以事实陈述为主；新版明确产出 L3/L4 级综合洞见（如"谱维数是把网络几何与动力学相行为连接起来的单一几何量"、"调大谱维数比盲目增加连边更本质"）。
- **过程可审计性**：旧版无过程工件；新版完整保留 `section_reviews.md`、`evidence_compress.md`、`search_log.md` 与引用台账。

## 质量评价

- **优点**：新题上 skill 的各机制激活稳定；23 篇文献覆盖三子方向，分类框架清晰；L3/L4 洞见明确且均有引用支撑；过程工件齐全；门禁 WARN=0。
- **观察**：压缩块全为 ✅（无 ⚠️/❌），说明检索结果与意图高度一致，但也可能是弱模型回避标记负面状态的倾向；过程工件闸口有效促成了工件的保留。
- **与 κL 系列对比**：谱维数题文献更偏统计物理/网络科学，跨学科接口（经济学长记忆、生物网络）也被触及；整体结构纪律与 κL 验证一致，说明 skill 已具备一定领域泛化能力。
