# 机器学习势函数在晶格热导率预测中的应用进展：从第一性原理精度到何样的可靠性

## 关键引用

- [1] Arabha 等, 2021, "Recent advances in lattice thermal conductivity calculation using machine-learning interatomic potentials"
- [2] Dong 等, 2024, "Molecular dynamics simulations of heat transport using machine-learned potentials: A mini-review and tutorial on GPUMD with neuroevolution potentials"
- [3] Korotaev 等, 2019, "Accessing thermal conductivity of complex compounds by machine learning interatomic potentials"
- [4] Ouyang 等, 2022, "Accurate description of high-order phonon anharmonicity and lattice thermal conductivity from molecular dynamics simulations with machine learning potential"
- [5] Tai 等, 2025, "Revisiting Many-Body Interaction Heat Current and Thermal Conductivity Calculations Using the Moment Tensor Potential/LAMMPS Interface"
- [6] Lu 等, 2026, "The accuracy of moment tensor potential on predicting phonon properties of 1T' and 2H phase MoS2"
- [7] McGaughey 等, 2025, "Phonon Olympics: Phonon property and lattice thermal conductivity benchmarking from open-source packages"
- [8] Lee 等, 2024, "Equivariant graph neural network interatomic potential for Green-Kubo thermal conductivity in phase change materials"
- [9] Zhang 等, 2026, "Beyond Boltzmann transport: Green-Kubo prediction of lattice thermal conductivity with machine-learned potentials"

## 摘要

机器学习势函数在晶格热导率（$\kappa_L$）预测中已成为衔接第一性原理与大规模原子模拟的关键桥梁，其承诺是"DFT 级精度、经典势级成本"。本综述基于 sciverse 单一信息源、以滚雪球至饱和的原则系统检索 21 篇核心文献，围绕两条计算路线展开：声子玻尔兹曼输运方程（从势函数数值求高阶力常数）与分子动力学热流路线（Green–Kubo / NEMD）。核心判断是：MLIP 的相对优劣由"架构 × 技术路线"耦合决定——声子 BTE 路线把精度押在高阶力常数（尤其三阶及以上）的生命周期上，而 Green–Kubo 路线天然包含全阶非谐但对势函数的多体热流算符正确性极其敏感（处理不当可改动 $\kappa_L$ 达 29–64%）。因此热导导向的 MLIP 验收不应以力 RMSE 为准，而应以高阶力常数复现精度、小体系 Green–Kubo 对照与力误差噪声外推为判据。本文最后指出，通用势在高通量声子筛选上的初步成功与强非谐/无序体系上的证据空缺，构成了下一阶段最高杠杆的研究方向。

## 核心要点

- **要点 1**：MLIP 已能把 $\kappa_L$ 计算从"谐频好、寿命差"的经验势困局中解放出来；经典经验势对硅热导率系统性失灵 [10]，而 MLIP 主动学习以数百次 DFT 单点即可复现色散与 $\kappa_L$ [11, 3]。
- **要点 2**：技术路线决定误差来源。BTE 三声子路线在四声子重要的材料（BAs、InSe）系统性高估 $\kappa_L$ [12, 13]；Green–Kubo 路线天然含全阶非谐，在强非谐材料与实验更吻合 [4, 8]。
- **要点 3**：$\kappa_L$ 对三阶力常数导出的寿命比对谐频/群速度敏感得多——多软件基准显示 $\kappa_L$ 差异几乎全部来自三声子寿命 [7]，故 MLIP 应用应以动量分辨的声子散射率而非仅色散为验收 [6]。
- **要点 4**：Green–Kubo 路线存在独特的方法性陷阱——若热流算符按两体 virial 近似，会系统性低估多体势对热流的贡献，实测可改变 $\kappa_L$ 达 29–64% [5]。
- **要点 5**：通用势（MACE 等）在谐频高通量声子计算上已达可用精度（频段 MAE 0.18 THz、动态稳定性分类 86.2%）[14]，但其对强非谐材料散射寿命的刻画仍未验证，是主要开放问题。

## 一、引言

### 为什么需要这篇综述

晶格热导率 $\kappa_L$ 是热电、微电子散热、核材料等应用的基石参数，但其第一性原理计算长期受两难制约：声子玻尔兹曼输运方程（PBTE）需要三阶及以上力常数，数值代价高昂且对复杂晶体结构急遽上升；而经典经验势虽然便宜，却常无法同时正确刻画谐频与高阶非谐——早在 2005 年，对硅用多种经验势求得的 $\kappa_L$ 就与实验系统性不符，且其 Grüneisen 参数与热膨胀也偏离第一性原理 [10]。这一"经验势不可靠、DFT 太贵"的张力，正是机器学习势函数登上热输运舞台的动机。

近年来该方向快速成熟：以 Moment Tensor Potentials（MTP）为代表的势类定义了可系统改进、可直接数值求高阶力常数的数学框架，DeePMD-kit 则把深度多体势能表示做成工程化软件栈 [11, 15]。另有若干专门综述与教程 [1, 2]。但多数既有资料要么聚焦单一路线（仅 BTE 或仅 MD），要么偏重方法宣传。"MLIP 到底在多可靠的程度上接管了 $\kappa_L$ 预测"这一问题，仍缺乏以技术路线与精度边界为轴的批判性梳理。

### 研究问题

本文围绕三个可回答的问题展开：

- RQ1：MLIP 相比第一性原理 DFT 与经典经验势，在晶格热导率预测上的精度—成本权衡如何？它是否真的兑现了"DFT 精度、经典成本"的承诺，又在哪些环节打折扣？
- RQ2：不同 MLIP 架构（MTP、DeePMD、等变图神经网络、NEP、通用势等，其方法学对应见第四、五节 [11, 15, 2, 8, 14]）在两条技术路线——声子 BTE 力常数路线与分子动力学热流路线（Green–Kubo / NEMD）——中的适用性与相对差异是什么？
- RQ3：在强非谐、无序/超准粒子、缺陷与多维结构等复杂情形下，MLIP 的可靠性边界在哪里，存在哪些尚未裁决的争议？

### 本文组织方式

第二节交代检索与纳入方法；第三节给出按"技术路线"为主轴、以"方法架构"为行的 MECE 分类框架；第四节讨论方法学地基；第五、六节分别展开声子 BTE 路线与分子动力学热流路线；第七节梳理精度边界与失效裁判；第八节跨分支综合，第九节给出开放问题，第十节逐条回答 RQ。

## 二、研究方法

本综述的信息源为 sciverse（MCP `search_papers` / `semantic_search` / `list_paper_relations`），信息源仅此一个（按用户指定）。检索覆盖七个视角：以综述 [1] 锚定的宽域视角、以神经演化势（NEP）/GPUMD 教程 [2] 锚定的热流路线视角、Green–Kubo 视角、以 MTP [11] 锚定的精度视角、中文相邻综述视角、裁判型失效语义视角，以及对综述 [1] 参考文献的滚雪球反查。时效上，本话题归"成熟领域 + 前沿增量"档，以近三年（2024–2026）为主、奠基/经典档核对经典文献。

纳入标准：以 MLIP 的构建或应用为核心、明确以晶格热导率（或直接决定它的声子/热流量）为输出对象的第一性原理级工作；方法学奠基与裁判型基准作支撑。排除：只测电导率/总热导率而未区分晶格贡献的宏观实验、纯经验势拟合而无 MLIP 的内容（除作为失效对照组外）。最终纳入 21 篇，与参考文献条数一致；滚雪球补搜一轮后新增入选为 0，达检索饱和。分类框架以"计算路线"为分类轴（互斥且完备），"方法架构"充当行维度，见第三节。

证据类型按学科惯例分级：

| 证据类型 | 含义 | 可信度定位 |
|---|---|---|
| 基准/裁判文献 | 多软件或多势的旁证对比、失效分析 | 高（跨独立实现的一致性） |
| 方法学奠基 | 定义一种 MLIP 架构 | 高（被广泛应用） |
| 单体系案例 | 某势在某材料上的 $\kappa_L$ 计算 + 与实验/DFT 对照 | 中（需看对照强度与受控量） |
| 综述/教程 | 领域现状归纳 | 中（依赖其引用完备性） |

## 三、分类框架

分类轴（互斥且完备）是**计算技术路线**；每个路线内部再按**方法架构**细分，作为对比的行：

| 技术路线 | 物理量/输出 | 误差敏感点 | 代表架构 |
|---|---|---|---|
| 声子 BTE / 力常数路线 | 从势数值求二/三/四阶力常数 → PBTE 解出 $\kappa_L$ | 高阶力常数（尤其三阶）的复现精度 | MTP [11, 3, 12, 16], MACE 通用势 [14] |
| 分子动力学热流路线（Green–Kubo / NEMD） | 直接从原子轨迹取热流自关联或界流 | 热流算符的多体性、力噪声、统计收敛 | DeePMD [15, 13], 等变 GNN [8], NEP [2, 17, 18], MTP+EMD [11, 4, 9] |
| 精度边界与失效裁判 | 评估上述两路线的可靠性、失效与基准 | 不适用（对象是方法本身） | 跨路线裁判 [5, 6, 7, 19, 10] |

分类轴的空格即 gap：**"通用势（MACE 等）在强非谐材料上求散射寿命"这一格子几乎是空的**——通用势已验证于谐频高通量 [14]，但尚未在四声子重要/超准粒子体系上经受与专用势同等的检验。跨分类论文是 Ouyang2022 与 Lee2024 [4, 8]：它们同时对比了 BTE 与 GK 两路线，挑战了"选一条路线即可"的假设，值得单独讨论（见综合讨论）。

## 四、方法学地基：MLIP 如何成为可信赖的热导率势

MLIP 的承诺是用势函数在"DFT 精度、经典成本"的价位上描述能面。Moment Tensor Potentials 从数学上定义了一类可系统改进、可解析求导的势 [11]，其数值求导天然提供力常数抽取的高阶一致性；DeePMD-kit 则把深度多体势能表示落地为可工程化的软件栈，接口到 LAMMPS 与路径积分动力学 [15]。与经验势对比，MTP 这类势（可系统改进性是它的代表性特征）并不依赖预设交互形式 [11]。经验势的失效则被 Broido2005 以硅为例清楚暴露出来：其 $\kappa_L$ 计算系统性偏离实验 [10]，正是这类可改进势价值的反面注脚。

在地基之上，早期工作确立了 MLIP 用于 $\kappa_L$ 的可行性前提：Korotaev2019 用主动学习把训练集压到"数百次量子力学计算"，以 MTP [11, 3] 描述 CoSb3 声子谱并同时对比 BTE 与 Green–Kubo 两种解值方法，表明可靠势无需海量 DFT 数据，这正是 MTP 可系统改进性质 [11] 的直接收益。综述层面，Arabha2021 系统归纳了 MLIP 在 2D/3D 结构上相对实验与量子计数的对齐情况，并指出 MLIP 不仅能估本征性质、也可延展到缺陷 [1]；Dong2024 则以 GPUMD 中的 NEP 为教学主线，给出了从数据集到热导率的完整落地教程 [2]。

小结（≥ L2）：方法学地基已成熟——MLIP 作为热导率势的核心价值不是单一精度参数，而是"可系统改进 + 数值求导一致 + 主动学习压训练成本"三者叠加，使 $\kappa_L$ 计算首次对复杂/低对称晶体（如方钴矿 [3]）实用化。

## 五、技术路线一：声子 BTE / 力常数路线

这条路线把 $\kappa_L$ 分解为声子色散（谐频）、群速度、与各阶散射寿命，核心瓶颈从 DFT 转嫁到了"从 MLIP 数值求高阶力常数"。

MTP [11] 是该路线的早期主力。Korotaev2019 以 CoSb3 为例，用主动学习构造的 MTP [11, 3] 同时求多阶力常数，BTE 解得的 $\kappa_L$ 与 Green–Kubo 结果可比，确立了"BTE+MLIP"的组合可用性。把路线推向"四声子"的关键是 Liu2021：对 wurtzite BAs 用 MTP 求高阶力常数并纳入四声子散射后，平面内 $\kappa_L$ 高达 1036 W·m$^{-1}$K$^{-1}$，比不计四声子时降低约 43%，从而证明高阶力常数在 BTE 框架内的不可或缺性 [11, 12]。

对四声子与强非谐的更高要求，Dai2025 展示了 AIMD 数据训 MTP 预测 BAs 的压力依赖 $\kappa_L$，并把同位素散射与缺陷散射纳入，揭示本征材料中 3–声子与 4–声子过程的竞争决定了压力响应 [11, 16]。这与 Liu2021 对 w-BAs 的结论（四声子在 BAs 家族主导）相互印证 [12, 16]，两者虽用不同势、不同相，指向同一物理。

BTE 路线也向"通用化"延伸。Lee2025 用 MACE 通用势配合"全员随机微小位移的超胞"数据策略，在 2738 种材料上训练并用于高通量谐频计算，在 384 种材料上频段 MAE 为 0.18 THz、动态稳定性分类精度 86.2% [14]。但需注意：Lee2025 验证的是**谐频与自由能**，并未宣称 $|\kappa_L|$ 端到端精度——这恰是 BTE 路线的软肋，因为 $\kappa_L$ 主要受三声子寿命支配。

对比表（表 4 含结论）：

| 工作 | 势架构 | 覆盖材料 | 力常数阶数 | 核心结果 |
|---|---|---|---|---|
| Korotaev2019 | MTP（主动学习） | CoSb3 | 谐 + 三阶 | $\kappa_L$ 与 GK 可比，数百 DFT 即足 [11, 3] |
| Liu2021 | MTP | wurtzite BAs | 含四阶 | 含四声子后 $\kappa_L$ 降 43%，1036 W·m$^{-1}$K$^{-1}$ [11, 12] |
| Dai2025 | MTP（AIMD 数据） | 立方 BAs | 含四阶 | 压力依赖 $\kappa_L$，3–/4–声子竞争 [11, 16] |
| Lee2025 | MACE 通用势 | 2738 材料 | 谐（二阶） | 频段 MAE 0.18 THz，动态稳定 86.2% [14] |

小结（≥ L2，L3）：声子 BTE 路线的精度天花板取决于力常数阶数与动量分辨守恒。多软件基准表明，$\kappa_L$ 的跨实现差异几乎全部来自三阶力常数导出的声子寿命，而非谐频或群速度 [7]；一个可检验的解释是——BTE 路线要把"谱域正确"（色散，已验证 [14]）与"动量分辨正确"（散射率）分开验收，前者不足以担保后者（参见第七节 Lu2026 [6] 对光学支的具体证据）。

## 六、技术路线二：分子动力学热流路线（Green–Kubo / NEMD）

该路线直接从原子轨迹提取热流，数学上包含势能面的全阶非谐，因此对"四声子重要"或"强非谐"体系有概念优势；代价是统计收敛、体系尺寸和热流算符的正确性。

Green–Kubo 路线的一个典型实证是单层 InSe 的晶格热导率计算 [13]。该工作用 DeePMD 深度势配合 Green–Kubo，在 300 K 得 $\kappa_L=9.52$ W·m$^{-1}$K$^{-1}$ 与实验吻合，而三声子 BTE-DFT 得 13.08（高估），差出的量被归结为上下光学支能隙导致四声子被截断 [15, 13]。Ouyang2022 在 BAs 与金刚石上得到一致结论：MLP+BTE（仅三声子）显著高估 BAs，而 MLP+平衡分子动力学（E-MD）与实验吻合，作者归因于 BAs 高阶四声子散射被 BTE 忽略 [4]。Lee2024 用等变图神经网络 [8] 在 GeTe 上独立复现同一现象：MACE 类等变势 [14] + GK 与实验一致，而三声子 BTE 高估约 2 倍。三篇来自不同架构与不同材料的独立工作收敛到同一结论：高温/强非谐下，GK 热流路线优于截断的 BTE [13, 4, 8]。

MD 路线也承担了经验势无法触及的复杂体系。早在 2020 年，Mortazavi2020 就示范了用短 AIMD 轨迹训练的 MTP 走 DFT/MD/有限元多尺度级联：先算石墨烯与硼烯各相的本征 $\kappa_L$，再推异质结界面热导与连续级有效热输运，把第一性原理精度延伸到宏观层级 [11, 20]。之后，Sha2023 为 2D PbTe 单层构造 NEP，发现双轴应变增大时 $\kappa_L$ 反常升高（低频谱增强所致），此类发现依赖可解析的机器学习势而非经验势 [2, 17]。Zhang2025 用 NEP 刻画 SiC 的堆垛层错热阻，得到高达 10$^{-10}$ K·m$^{2}$·W$^{-1}$ 的层错热阻，为多型与缺陷体系提供了经验势难以企及的界面级量值 [2, 18]。在同一材料的另一势框架下，Fu2024 以 DeePMD 复现 SiC 各多型的结构、声子行为与热输运，验证深度势对该家族的通用刻画 [15, 21]。在超强非谐、近准粒子失效的 Rb2ZnTe 上，Zhang2026 用 MLP + Green–Kubo 得到的 $\kappa_L$ 更接近非晶极限，并较此前 BTE 估计修正了 38%——作者指出该材料已逼近 Ioffe–Regel 极限，准粒子图象濒临失效 [9]。

对比表（表 6 含结论）：

| 工作 | 势架构 | 体系 | 方法 | 相对经验势/DFT 的价值 |
|---|---|---|---|---|
| Han2023 | DeePMD | 单层 InSe | GK | $\kappa_L$ 与实验吻合，优于三声子 BTE [15, 13] |
| Ouyang2022 | MLP（矩阵张量） | BAs、金刚石 | E-MD 对照 BTE | BTE 高估 BAs，E-MD 与实验一致 [4] |
| Lee2024 | 等变 GNN | GeTe（三态） | GK | 单势描述相变，BTE-3ph 高估 $2\times$ [8] |
| Zhang2026 | MLP | Rb2ZnTe | GK | 近非晶极限，$\kappa_L$ 修正 38% [9] |
| Sha2023 / Zhang2025 | NEP | 2D PbTe / SiC | NEMD | 应变/堆垛层错等复杂量值 [2, 17, 18] |
| Fu2024 | DeePMD | SiC 各多型 | LD + MD | 复现结构与声子输运 [15, 21] |
| Mortazavi2020 | MTP | graphene/borophene | DFT/MD/FEM | 多尺度第一性原理热输运 [11, 20] |

小结（≥ L2，L3）：MD 热流路线的优势本质上是**方法论的分立性**——它把"全阶非谐"作为事后事实而非事前假设纳入，因此尤其适合四声子重要 [13, 4] 或准粒子濒临失效 [9] 的材料。但它把赌注押在热流算符的正确性上，这一弱点在下一节展开。

## 七、精度边界与失效裁判

任何 MLIP 的热导率预测若想给出可信度边界，必须回答两个追问：势函数本身的力/散射描述错在哪，以及计算方案（热流算符/力常数抽取）有没有引入独立于势的偏差。

**裁判一：多体热流算符（机理级、GK 路线专属）。** Tai2025 指出，当从两体经验势迁移到非成对可加的多体势（如 MTP [11, 5]）时，LAMMPS 界面的 virial 热流公式未含广义多体热流项，导致动能守恒不一致；修正后 GK 的 $\kappa_L$ 结果改变 29–64%。这不仅是一个实现细节，而是架构选择直接作用于结果量级的方法性误差——比单篇材料实验对照更普遍地影响 MD 路线。

**裁判二：动量分辨散射率的精度退化。** Lu2026 对 1T′ 与 2H 相 MoS2 训练单一 MTP，整体色散与 $\kappa_L$（室温 118.23 / 15.36 W·m$^{-1}$K$^{-1}$）与 DFT 高度一致，但逐动量查看发现 MTP 对声学声子散射率复现良好、对光学支却出现明显定量偏差，从而要求按动量分布验收势函数而不只是看色散或标量 $\kappa_L$ [11, 6]。

**裁判三：跨软件基准。** McGaughey2025 组织的"Phonon Olympics"对 Ge、RbBr、MoSe2、AlN 用 ALAMODE / phono3py / ShengBTE 交叉计算，$\kappa_L$ 落在各实现均值 ±15% 内，且因由三声子寿命主导 [7]。它提示：即便势被固定，BTE 实现本身的寿命计算决策（超胞、位移、对称）会造成可观差异——为"用 MLIP 算寿命"设定了期望方差的下限。

**趋势：从"拟合力常数/热流"到"直接学散射率"。** Guo2025 跳出"训练势→再解输运"的流程，直接以 ML 预测声子散射率与 $\kappa_L$，在保留第一性原理精度时比第一性原理快两个量级，并借不同阶散射间的分级迁移学习增强外推 [19]；这代表着把"势"层与"输运解算"层脱钩、向专一代理模型演进的路线。

小结（≥ L3）：综合三个裁判，可以给出一个统一的失效模型——**热导率 MLIP 预测的总误差 = 势函数对高阶/光学支力常数的系统误差 ⊕ 计算方案引入的方法性误差（多体热流算符 [5]、寿命抽取决策 [7]）**。这两路误差相互独立，且都主要作用于"寿命"而非"色散"，因此仅以力 RMSE 或色散一致为验收的既有做法，系统性低估了 $\kappa_L$ 预测的不确定性。

## 八、综合讨论

把两条技术路线并置，最醒目的事实是跨架构、跨体系的**收敛与一个张力**。

收敛：在强非谐/四声子/超准粒子材料上，三篇独立架构的工作（DeePMD [15, 13]、矩阵张量 MLP [4]、等变 GNN [8]）与一篇超强非谐案例 [9] 一致指向"截断的 BTE 高估、GK 热流路线更可靠"。这一跨独立来源的收敛，比任何单篇数字都更有力地支持"热流路线在强非谐下的优先地位"。

张力：GK 的优势依赖热流算符的多体正确性 [5]，而正是 MD 路线的这个环节在大多数实现里被当作免费午餐忽略。于是出现一个实践上的两难——对强非谐材料，应当优先 GK（物理更完整），但若所用 MLIP/接口的热流算符未含多体项，GK 反而可能比 BTE 引入更大的系统性偏差。这是本综述识别的核心分歧点，也是"架构×路线耦合"假说的落点：**误差路径依赖"势架构的输出形式 × 路线对它的读取方式"**，不存在普适最优组合。

跨路线共同点：无论 BTE 还是 GK，$\kappa_L$ 的精度都集中在"寿命"权重上 [7, 6]，这意味着热导方向的验收应统一围绕"动量分辨散射率/寿命"建立，而非分散在色散或标量 $\kappa_L$。

## 九、开放问题与未来方向

- **通用势的强非谐空白（gap）**：MACE 通用势已验证谐频高通量 [14]，但尚未在四声子重要（BAs 族 [12, 16]）或超准粒子（Rb2ZnTe [9]）体系上接受与专用势同等的三/四声子寿命检验。填补它需要把"通用势 + 高阶力常数 + 动量分辨散射率"跑通一个代表性强非谐体系。
- **多体热流算符的工程化规范（缺具体设计）**：Tai2025 已给出修正公式的可行性 [5]，但目前缺一项基准：在统一接口下，比较含与不含多体热流项的 GK 结果序列，以量化各主流势（MTP、NEP、DeePMD、等变 GNN [11, 2, 15, 8]）在此环节的误差分布——它能裁决"热流算符误差是否与架构强相关"。
- **散射率代理模型的覆盖边界**：Guo2025 直接学散射率达两个量级加速 [19]，但其训练外推依赖于分级迁移；对光学支主导散射的材料（如 MoS2 光学支退化 [6]），代理模型是否同样可靠缺实证。
- **缺陷/多维度体系的量值可信度**：层错热阻（SiC [18]）、二维应变反常（PbTe [17]）等新颖量值多来自单一势、缺独立复现；其可信度需在同一物理量上跨势交叉验证。

## 十、结论

逐条回答引言中的 RQ：

- **RQ1（精度—成本权衡）**：MLIP 兑现了"DFT 精度、经典成本"的总体承诺：主动学习可把训练压到数百次 DFT 单点即得可靠 $\kappa_L$ [3]，而经验势对硅等的系统性失效被明确裁定 [10]。代价出现在两个环节——高阶/光学支力常数的系统误差 [6] 与计算方案（热流算符 [5]、寿命抽取 [7]）的独立偏差，二者都作用于寿命而非色散。
- **RQ2（架构×路线差异）**：不存在普适最优。声子 BTE 路线最适合高对称、谐限、四声子次要的体系，精度由三阶及以上力常数决定 [3, 12]；分子动力学热流路线（GK/NEMD）天然含全阶非谐，在强非谐/四声子重要/准粒子濒临失效体系上更可靠 [4, 13, 8, 9]，但必须以正确的多体热流算符为前置 [5]。NEP [2] 擅长缺陷/低维复杂体系 [17, 18]，通用势当前仅可信于谐频高通量 [14]。
- **RQ3（可靠性边界）**：边界不在"能不能算"，而在"怎么验收"。多软件基准 [7] 与动量分辨检验 [6] 共同表明，应以三阶及以上力常数导出的寿命、并按动量分解验收，而非以力 RMSE 或色散一致为标准；对强非谐/无序体系，需以"含多体热流的 GK + 小体系对照 + 力误差噪声外推"构成验收组合。

本文的核心贡献是把散落于各架构/各材料的 $\kappa_L$ 证据重组为一条清晰的判断链：MLIP 让 $\kappa_L$ 首次对复杂体系实用化，但其误差是"势架构 × 技术路线"耦合的产物，且集中在寿命环节；下一步的关键不是追求更低的力 RMSE，而是把"动量分辨寿命 + 多体热流正确性"确立为热导导向的 MLIP 验收标准，并由此填补通用势在强非谐材料的证据空缺。

## 参考文献

[1] Arabha S, Shokri Aghbolagh Z, Ghorbani K, Hatam-Lee S M, Rajabpour A, “Recent advances in lattice thermal conductivity calculation using machine-learning interatomic potentials,” Journal of Applied Physics, 2021.
[2] Dong H, Shi Y, Ying P, Xu K, Liang T, Wang Y, Zeng Z, Wu X, Zhou W, Xiong S, Chen S, Fan Z, “Molecular dynamics simulations of heat transport using machine-learned potentials: A mini-review and tutorial on GPUMD with neuroevolution potentials,” Journal of Applied Physics, 2024.
[3] Korotaev P, Novoselov I I, Yanilkin A V, Shapeev A V, “Accessing thermal conductivity of complex compounds by machine learning interatomic potentials,” Physical Review B, 2019.
[4] Ouyang Y, Yu C, He J, Jiang P, Ren W, Chen J, “Accurate description of high-order phonon anharmonicity and lattice thermal conductivity from molecular dynamics simulations with machine learning potential,” Physical Review B, 2022.
[5] Tai S T, Wang C, Cheng R, Chen Y, “Revisiting Many-Body Interaction Heat Current and Thermal Conductivity Calculations Using the Moment Tensor Potential/LAMMPS Interface,” Journal of Chemical Theory and Computation, 2025.
[6] Lu W-X, Qu Q-Z, Zeng Y-J, Yao Y, “The accuracy of moment tensor potential on predicting phonon properties of 1T' and 2H phase MoS2,” Journal of Physics D: Applied Physics, 2026.
[7] McGaughey A J H, Lindsay L, Bao H, Hamakawa T, Juneja R, Li S, Li W, Masuki R, Meng F, Meng H, Pandey T, Shao C, Shiomi J, Tadano T, Togo A, Wang A, Zhang X, “Phonon Olympics: Phonon property and lattice thermal conductivity benchmarking from open-source packages,” Journal of Applied Physics, 2025.
[8] Lee S-H, Li J, Olevano V, Sklénard B, “Equivariant graph neural network interatomic potential for Green-Kubo thermal conductivity in phase change materials,” Physical Review Materials, 2024.
[9] Zhang X, Liu N, Guo Q, Shi G-Y, Wang Y, “Beyond Boltzmann transport: Green-Kubo prediction of lattice thermal conductivity with machine-learned potentials,” The Journal of Chemical Physics, 2026.
[10] Broido D A, Ward A, Mingo N, “Lattice thermal conductivity of silicon from empirical interatomic potentials,” Physical Review B, 2005.
[11] Shapeev A V, “Moment Tensor Potentials: A Class of Systematically Improvable Interatomic Potentials,” SIAM Multiscale Modeling and Simulation, 2016.
[12] Liu Z, Yang X, Zhang B, Li W, “High Thermal Conductivity of Wurtzite Boron Arsenide Predicted by Including Four-Phonon Scattering with Machine Learning Potential,” ACS Applied Materials & Interfaces, 2021.
[13] Han J, Zeng Q, Chen K, Yu X, Dai J, “Lattice Thermal Conductivity of Monolayer InSe Calculated by Machine Learning Potential,” Nanomaterials, 2023.
[14] Lee H, Hegde V I, Wolverton C, Xia Y, “Accelerating high-throughput phonon calculations via machine learning universal potentials,” Materials Today Physics, 2025.
[15] Wang H, Zhang L, Han J, E W, “DeePMD-kit: A deep learning package for many-body potential energy representation and molecular dynamics,” Computer Physics Communications, 2018.
[16] Dai L, Li M, Hu Y, “Machine learning for thermal transport and phonon high-order anharmonicity in high thermal conductivity materials: A case study in boron arsenide,” Physical Review Materials, 2025.
[17] Sha W, Dai X, Chen S, Yin B, Guo F, “Phonon thermal transport in two-dimensional PbTe monolayers via extensive molecular dynamics simulations with a neuroevolution potential,” Materials Today Physics, 2023.
[18] Zhang H, Cheng M, Jiang X, Zhang H, Pi X, Yang D, Deng T, “Neuroevolution potential for thermal transport in silicon carbide,” Journal of Materials Informatics, 2025.
[19] Guo Z, Roy Chowdhury P, Han Z, Sun Y, Feng D, Lin G, Ruan X, “Fast and accurate machine learning prediction of phonon scattering rates and lattice thermal conductivity,” npj Computational Materials, 2025.
[20] Mortazavi B, Podryabinkin E V, Roche S, Rabczuk T, Zhuang X, Shapeev A V, “Machine-learning interatomic potentials enable first-principles multiscale modeling of lattice thermal conductivity in graphene/borophene heterostructures,” Materials Horizons, 2020.
[21] Fu B, Sun Y, Jiang W, Wang F, Zhang L, Wang H, Xu B, “Determining the thermal conductivity and phonon behavior of SiC materials with quantum accuracy via deep learning interatomic potential model,” Journal of Nuclear Materials, 2024.
