# 检索日志（sciverse 综述模式）

话题：机器学习势函数（MLIP）在晶格热导率预测中的应用进展
信息源：sciverse（唯一信息源，按用户指定）
日期：2026-08-12
时效精度分级：成熟领域 / 奠基 + 前沿增量 → 近 3 年档为主，鉴基档核对经典

## 检索视角与 query

视角 A（宽域 / 综述）：`machine learning interatomic potential lattice thermal conductivity`
视角 B（方法流派 / NEP）：`NEP machine learning potential phonon thermal conductivity`；`neuroevolution potential NEP GPUMD phonon thermal transport`
视角 C（方法流派 / Green-Kubo）：`deep potential DeePMD thermal conductivity Green-Kubo`；`machine learning potential phonon Boltzmann transport equation three-phonon scattering high throughput`
视角 D（方法流派 / MTP + 精度）：`moment tensor potential MTP phonon thermal conductivity benchmark accuracy`
视角 E（中文 / 相邻综述）：`机器学习势函数 晶格热导率 综述`
视角 F（裁判型 / 质疑，semantic）：`limitations ... of MLIP for lattice thermal conductivity where they fail`
视角 G（滚雪球 / 时效）：Arabha2021 综述参考文献反查；2024-2026 近窗口检索

## 检索意图演化

- updated_intent：聚焦两条技术路线——①声子玻尔兹曼方程（BTE，从 MLIP 数值求二阶/三阶/四阶力常数）+ ②分子动力学（EMD/GK、NEMD）直接热流；并把"MLIP 逐层/方法流派的精度与边界"作为贯穿裁判轴。
- updated_checklist：方法奠基（MTP/DeePMD/GAP）；BTE 路线；GK/NEMD 路线；高温/强非谐/无序体系；缺陷/多晶/异质结；高通量与通用势；裁判型精度/失效分析。
- missing_coverage：强非谐/超出准粒子图象体系 → 已由 Zhang2026 (Rb2ZnTe 近 Ioffe-Regel)、ultralow-κ 工作补齐；通用势高通量 → Lee2025 (MACE) 补齐。
- evidence_gaps：部分 MTP 光学支精度争议偏少 → Lu2026 定向补齐；MLIP Green-Kubo 数值噪声/多体热流定义争议 → Tai2025 补齐。

## 检索收敛声明

- 研究简报子方向数：7
- 每子方向核心文献 ≥3 篇：是（MTP 应用 6 / DeePMD、GNN、NEP 7 / GK+代理 3 / 综述 2 / 奠基 2 / 裁判型 4）
- 末轮滚雪球新增入选：0 篇（以 Arabha2021 综述 REFERENCES 反查一轮，返回为已覆盖经典 MTP/DeePMD/GAP）
- 时效探针已执行：是（窗口 2024-01 至 2026-08，命中 Dai2025 / Lu2026 / Zhang2026 / Lee2025 等多篇；检索末段 MCP 临时 fetch 报错，以既有近窗口覆盖为准，未发现漏失的关键近作）
- 多源覆盖：sciverse（指定唯一源）
- 盲区检查：强非谐/超准粒子是唯一潜在盲区，已由 Zhang2026 + ultralow-κ 系列补齐；中文综述未命中专门 MLIP-热导率综述（sciverse 对中文期刊覆盖有限），以英文综述 Arabha2021 / Dong2024 承托
- 裁判型文献定向检索：是（Tai2025 多体热流；Lu2026 光学支精度；McGaughey2025 Phonon Olympics 基准；Broido2005 经验势失效）
- 意图演化已记录：是
- 是否进入阶段二：是（has_enough_context_for_synthesis = true）
