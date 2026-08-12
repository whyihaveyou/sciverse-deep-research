# OpenCode + DeepSeek-chat v6 验证：机器学习势函数 × 晶格热导率

这是 2026-08-12 在第五轮（harness 架构显性化）与第六轮（P0 结构化自批判 + P1 上下文压缩纪律 + P2 效率指标附录）改进叠加后的端到端验证运行产物。

## 运行条件

- Agent / 模型：OpenCode 1.18.16 + deepseek-chat（API baseURL `https://api.deepseek.com`）
- 工作目录：`.scratch/opencode-run-v6/`；本次运行实际把后期工件落在项目根 `.workflow/`，已事后迁入 `.scratch/opencode-run-v6/.workflow/`
- Prompt：与 v2/v3/v4/v5 保持一致（含 Step0 明确选择以支持非交互 `opencode run --auto`）
- 信息源：仅 sciverse（search_papers / semantic_search / list_paper_relations）

## 运行指标

| 指标 | v5 | v6（本轮） | 变化 |
|---|---|---|---|
| 耗时 | ~10m04s | ~11m（15:54–16:05） | +~1m |
| 检索调用 | 40 | 34 | −6 |
| 入选文献 | 21 | 24 | +3 |
| 中文字符 | 5448 | ~6200 | ↑ |
| 独立复核 FAIL / WARN | 0 / 0 | 0 / 0（export-clean 交付视图） | ✅ 达标 |
| 原始 final.md WARN | 0 | 3 | 待说明 |

> 注：耗时按 `.workflow` 内 `citation_ledger.json` 创建到 `delivery_mlip_thermal.md` 落盘估算；独立复核用 `skills/sciverse-deep-research/scripts/check_report.py`。

## 目录结构

- `output/delivery_mlip_thermal.md`：交付视图（export-clean，FAIL 0 / WARN 0）
- `.workflow/final.md`：事实源（原始复核 FAIL 0 / WARN 3）
- `.workflow/draft.md`：草稿
- `.workflow/citation_ledger.json` / `.workflow/citation_ledger.json.delivery.json`：引用台账

> 说明：本次运行 `.workflow/` 缺少 `search_log.md`、`search_plan.md`、`research_brief.md` 等早期工件（OpenCode 第三次运行只写入了后期工件），因此 P1 压缩块无法从工件中核验，需以日志为准。

## 第六轮三项新机制实效

### P0 结构化自批判（section_review）

**未显式执行。**

- `draft.md` 与 `final.md` 中均未出现 `section_review`、`critique`、`审稿` 等结构化批判块。
- 日志中没有检索到相关关键字。
- agent 实际做的是：在 `final.md` 生成后跑 `check_report.py`，发现 FAIL 6 / WARN 3，再回改 `draft.md` 中的引用格式（把 `MTP [3]、NEP [4]…` 改为 `MTP、NEP… [@…]`），最终通过门禁。这是**门禁脚本驱动的后验修复**，不是 skill 期望的"每节草稿完成后先批判再进入下一节"的前验审稿。

**判断**：P0 条款对 deepseek-chat 来说仍然太抽象，agent 把"批判"替换成了"跑脚本修错"。建议下一迭代把 section_review 改为强制产出可观测工件：每节草稿后必须写一个 `section_review` 代码块（含 `claims`、`evidence_gaps`、`L3_L4_status` 字段），不产出不得进入下一节。

### P1 上下文压缩纪律（compress_evidence）

**未显式执行。**

- 本次 `.workflow/` 没有 `search_log.md`，无法从工件中检查 `✅/⚠️/❌` 标记。
- 日志中未出现 `compress`、`压缩`、压缩块标记等关键字。
- 检索调用数 34 次（vs v5 的 40 次），没有因"每 3–5 篇强制压缩"而增加结构化停顿。

**判断**：P1 条款未能被弱模型执行。可能原因：压缩动作与检索流程耦合不够紧，agent 把"读摘要"直接串行处理了，没有落盘中间压缩块。建议把压缩块改为 `.workflow/evidence_compress.md` 的强制追加文件，并给出固定格式模板。

### P2 效率指标附录

**成功出现。**

- `final.md` 与 `delivery_mlip_thermal.md` 末尾均出现「调研成本」小节，内容：
  > 检索视角：主流方法（谱方法/直接 MD）、相邻领域（热电、非晶高温、二维、相变）、方法论（高阶非谐、四声子、力误差）。信息源：sciverse。滚动方式：结构化检索 + 引文网络，滚雪球至检索饱和。纳入 24 篇，全部经 sciverse 存在性反查（VERIFIED）。
- 这是自 v1–v5 以来首次在最终报告中稳定出现"调研成本"节。

## v6 vs v5 质量对比

- **文献覆盖**：v6 纳入 24 篇（v5 21 篇），新增了 Yang2022（MgSiO₃ 地幔）、Ladygin2020（晶格动力学模拟）等，材料谱系覆盖更完整。
- **论证深度**：v6 在"精度-成本权衡"一节把 Zhou2024 的"力误差非线性放大"作为贯穿主线，比 v5 更突出机制解释（L3 级）。但"每分支必须产出 L3/L4"的显式收尾判断仍不明显。
- **引用纪律**：v6 原始 final.md 有 3 个 WARN（MgSiO 编号近邻启发式误报、Green-Kubo 两处对比提及未挂编号），经 export-clean 后归零。v5 已经 WARN 0，v6 没有回退到 v4 的 10 WARN，说明 v4.1 的引用纪律保持有效。
- **效率**：检索调用从 40 降到 34，但耗时基本持平；自批判/压缩机制未明显增加成本（因为实际未执行），耗时增加主要来自 agent 反复修引用格式和 export-clean 流程。

## 结论

- **P2（效率指标附录）** 成功落地并稳定出现在最终报告中。
- **P0（结构化自批判）与 P1（上下文压缩纪律）** 在 deepseek-chat 上未显式执行：agent 用门禁脚本后验修错替代了前验批判，也未产出压缩块。下一迭代需要把这两项从"流程建议"升级为"强制可观测工件"（固定代码块 / 强制文件），否则弱模型会继续跳过。
- 整体质量没有回退，文献数增加，核心主线更清晰；但第六轮对 weak-agent 的"下限提升"效果主要来自 P2，P0/P1 需要再调。
