# OpenCode + DeepSeek-chat v7 验证：P0/P1 强制工件化后的快验

这是 2026-08-12 把第六轮 P0（结构化自批判）和 P1（上下文压缩纪律）从"流程建议"升级为"强制可观测工件"后的验证运行产物。目的是检验：固定格式代码块 + 强制文件名 + "未产出不得前进"的措辞，能否让 deepseek-chat 稳定执行。

## 运行条件

- Agent / 模型：OpenCode 1.18.16 + deepseek-chat（API baseURL `https://api.deepseek.com/v1`）
- 工作目录：`.scratch/opencode-run-v7/`（OpenCode 正确写入该目录，未落到项目根 `.workflow/`）
- Prompt：同 v2/v3/v4/v5/v6，并显式附加"请用 Markdown 输出，信息源只用 sciverse，跳过 Step0 澄清直接进入检索"以支持非交互运行
- 信息源：仅 sciverse（search_papers）

## 运行指标

| 指标 | v6 | v7（本轮） | 变化 |
|---|---|---|---|
| 耗时 | ~11m | ~7m（16:09–16:16） | −~4m |
| 检索调用 | 34 | 9（全部 search_papers） | −25 |
| 入选文献 | 24 | 21（台账 22 条，含 1 条综述/重复） | −3 |
| 中文字符 | ~6200 | ~6200 | → |
| 独立复核 FAIL / WARN | 0 / 0（export-clean） | 0 / 0（原始 final 即 0/0） | ✅ 达标 |

> 注：耗时按 `.workflow` 目录创建到交付稿落盘估算；独立复核用 `skills/sciverse-deep-research/scripts/check_report.py`。

## 目录结构

- `output/晶格热导率机器学习势函数综述.md`：交付视图（export-clean，FAIL 0 / WARN 0）
- `.workflow/final.md`：事实源（原始复核 FAIL 0 / WARN 0）
- `.workflow/draft.md`：键值草稿
- `.workflow/citation_ledger.json` / `.workflow/citation_ledger.json.delivery.json`：引用台账

## 强制工件化验收结果

### P0 结构化自批判（section_review）

**未执行。**

- `draft.md` 中无 `section_review` 代码块，也无 `claims_verification`、`L3_L4_verdict`、`evidence_gaps`、`patch_plan` 等固定字段。
- 日志中无 `section_review` / `critique` / `审稿` 等关键字。
- agent 仍以门禁脚本后验修错为主（日志中 `check_report.py` 出现并修正引用格式）。

### P1 上下文压缩纪律（compress_evidence）

**未执行。**

- `.workflow/evidence_compress.md` 不存在。
- 日志中无 `compress` / `压缩` / `✅` / `⚠️` / `❌` 等关键字。
- 检索调用仅 9 次，未出现"每 3–5 篇强制压缩"导致的结构化停顿。

### P2 效率指标附录

**执行。**

- `final.md` 末尾有「调研成本」小节，记录检索次数、滚雪球轮次、入选文献数、题录核验状态。

## v7 vs v6 质量对比

- **文献数减少**：v7 21 篇 vs v6 24 篇，但核心叙事更聚焦（方法家族 → BTE/MD 方法论分歧 → 泛化前沿 → 应用前沿）。
- **检索调用锐减**：v7 仅 9 次 search_papers，没有 semantic_search 和 list_paper_relations 滚雪球。agent 自己宣布"滚雪球约 4 轮，末轮零新增"，但实际调用次数明显少于 v5/v6。
- **门禁仍全绿**：原始 final.md 即 FAIL 0 / WARN 0，不需要 export-clean 后再归零，说明引用纪律已内化为模型行为。
- **洞见深度**：v7 明确提出"能量精度≠声子精度"、"BTE 三声子 vs MD 全阶非谐"等 L3 级判断，质量没有因检索调用减少而下降。

## 结论与下一步建议

- **P2 稳定可执行**："最终报告必须包含调研成本小节"这一输出层强制条款，deepseek-chat 已连续两轮稳定执行。
- **P0/P1 仍不可执行**：即使把条款从"流程建议"改为"强制工件 + 固定格式 + 不得前进"，deepseek-chat 仍然跳过。这说明对 weak-agent 而言，**中间过程层的强制条款需要比措辞更强的约束**。
- **建议下一步**（若继续迭代）：
  1. 把 section_review 和 compress_evidence 从"prompt 层要求"下沉为**程序级闸口**：在 `citation_ledger.py` 或 `check_report.py` 中增加 `--require-section-review`、`--require-evidence-compress` 开关，compile/门禁阶段检查文件是否存在，不存在直接 exit 1。
  2. 或者，在 SKILL.md 的阶段二和阶段一用更短的"必须"句式重复三次以上，并给出一个可直接复制粘贴的模板块，减少模型理解成本。
  3. 接受现实：P0/P1 是强模型才能稳定执行的"上限提升"机制；对 deepseek-chat 这类弱模型，当前能稳定拉下限的是 P2 + 引用纪律 + 洞见深度纪律。
