# OpenCode + DeepSeek-chat v8 验证：程序级过程工件闸口 + 拦截-反馈闭环

这是 2026-08-12 在 check_report.py 新增"过程工件"机械闸口后的验证运行产物。目的是检验：当 prompt 层强制已触顶（v6/v7 中 agent 跳过 section_review 与 evidence_compress）时，程序级 WARN 能否触发 agent 回头补齐工件的闭环。

## 运行条件

- Agent / 模型：OpenCode 1.18.16 + deepseek-chat（API baseURL `https://api.deepseek.com/v1`）
- 工作目录：`.scratch/opencode-run-v8/`（OpenCode 正确写入该目录）
- Prompt：同 v2–v7，并显式附加"请用 Markdown 输出，信息源只用 sciverse，跳过 Step0 澄清直接进入检索"
- Skill 状态：工作树已更新 check_report.py 过程工件检查 + SKILL.md 闭环条款 + synthesis-framework.md 工件落点
- 信息源：仅 sciverse（search_papers / semantic_search）

## 运行指标

| 指标 | v7 | v8（本轮） | 变化 |
|---|---|---|---|
| 耗时 | ~7m | ~5m（16:26–16:31） | −~2m |
| 检索调用 | 9 | 16（7 search_papers + 9 semantic_search） | +7 |
| 入选文献 | 21 | 21 | → |
| 独立复核 FAIL / WARN | 0 / 0 | 0 / 2 | WARN 来自启发式误报 |
| section_reviews.md | 不存在 | 存在，4 个审稿块 | ✅ 闭环生效 |
| evidence_compress.md | 不存在 | 存在，含 ✅/⚠️/❌ 标记 | ✅ 闭环生效 |

> 注：WARN 2 为 `L105/L111 'SnSe' 属台账 [5] 但其最近引用是 [2]`，agent 已核定为启发式误报（正文"BAs [2]、SnSe [5]"中 SnSe 正确绑定 [5]）。

## 目录结构

- `output/交付.md`：交付视图（export-clean）
- `.workflow/final.md`：事实源
- `.workflow/draft.md`：键值草稿
- `.workflow/section_reviews.md`：结构化自批判审计工件
- `.workflow/evidence_compress.md`：证据压缩审计工件
- `.workflow/citation_ledger.json` / `.workflow/citation_ledger.json.delivery.json`：引用台账

## 闭环证据

### section_reviews.md 内容

包含 4 个 `section_review` 代码块，覆盖：
- 第三节（分类框架）：L3 判定——"求解路线选择由体系非谐强度决定"
- 第四节（求解路线）：L3 + L4 判定，含"微扰框架截断误差无法被更准势补偿"
- 第五节（精度—成本权衡）：L3 + L4 判定，含"统一声子基准建议"
- 第六节（瓶颈与对策）：L3 + L4 判定，含"通用预训练势 + 声子微调取代逐体系从头训练"

### evidence_compress.md 内容

- 检索视角与关键词（A–F 六个视角）
- 逐文献证据标记（21 篇全部用 ✅ 标注）
- 滚雪球与时效（5 轮滚雪球，末轮零新增，达检索饱和）
- 盲区自查（诚实标注批评/失效视角偏薄、界面热导未入选）

### 触发路径

从日志可见：
1. agent 先完成综合并生成 `draft.md`；
2. 运行 `check_report.py` 时收到"过程工件"WARN（`.workflow/section_reviews.md` 与 `.workflow/evidence_compress.md` 不存在）；
3. agent 回头补写 `section_reviews.md` 与 `evidence_compress.md`；
4. 重新 compile + check_report，最终 FAIL 0 / WARN 2 交付。

## v8 vs v7 对比

- **过程工件**：v7 完全缺失；v8 因程序级闸口 WARN 而补齐。证明"prompt 触顶→程序级闸口→反馈闭环"的 harness 路线有效。
- **检索调用**：v8 16 次 vs v7 9 次，但语义检索占比更高（9 semantic_search），说明 agent 在补工件过程中用更多自然语言探针填补盲区。
- **耗时**：v8 反而比 v7 短（5m vs 7m），可能因为 agent 流程更聚焦、少走弯路。
- **质量**：v8 与 v7 均为 21 篇，核心判断（MLIP 从"DFT 替身"到"非谐全阶求解引擎"）一致；v8 的 section_review 使每个分支的 L3/L4 判定显性化。

## 结论

程序级过程工件闸口成功触发了 deepseek-chat 的拦截-反馈闭环：
- 单独 prompt 层强制（v6/v7）无法让弱模型稳定产出 section_review / evidence_compress；
- check_report.py 的 WARN 被 agent 读取后，agent 会回头补齐工件以消除 WARN；
- 这是 harness 三层架构（策略层 prompt / 执行层 scripts / 工具层 MCP）的典型生效路径。

下一步建议：若希望进一步硬化，可将 check_report.py 的 `--strict-process` 设为默认 FAIL（当前默认 WARN 以兼容旧 demo），或在 SKILL.md 中要求交付前必须"过程工件 0 WARN"。
