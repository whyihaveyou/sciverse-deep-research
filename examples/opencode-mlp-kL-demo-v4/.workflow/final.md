# 机器学习势函数在晶格热导率预测中的应用进展：从 DFT 替代到高阶非谐与通用势的收敛

## 关键引用

- [Mortazavi B, et al., "Accelerating first-principles estimation of thermal conductivity by machine-learning interatomic potentials: A MTP/ShengBTE solution," Computer Physics Communications, 2020]
- [Korotaev P, et al., "Accessing thermal conductivity of complex compounds by machine learning interatomic potentials," Physical Review B, 2019]
- [Loew A, et al., "Universal machine learning interatomic potentials are ready for phonons," npj Computational Materials, 2025]
- [Kocabas T, et al., "Thermal conductivity limits of MoS2 and MoSe2: Revisiting high-order anharmonic lattice dynamics with machine learning potentials," Applied Physics Reviews, 2025]
- [Liu Z, et al., "High Thermal Conductivity of Wurtzite Boron Arsenide Predicted by Including Four-Phonon Scattering with Machine Learning Potential," ACS Applied Materials & Interfaces, 2021]
- [Wen M, Tadmor E B, "Uncertainty quantification in molecular simulations with dropout neural network potentials," npj Computational Materials, 2020]
- [Qian X, et al., "Thermal conductivity modeling using machine learning potentials: application to crystalline and amorphous silicon," Materials Today Physics, 2019]

## 摘要

晶格热导率（$\kappa_L$）的精确计算长期受制于密度泛函理论（DFT）求解非谐力常数的高昂代价，以及在经典分子动力学中经验势对声子散射精度不足的困境。机器学习势函数（MLIP）以近 DFT 精度、近经典势的算力，同时缓解了这两重瓶颈。本文沿两条技术路线组织综述：基于非谐力常数与玻尔兹曼输运方程（BTE）的路线，与基于平衡/非平衡分子动力学（MD）的路线，并进一步考察 MLIP 对四声子等高阶非谐散射的刻画能力以及通用（universal）势的可靠性边界。证据表明，MLIP 的价值不仅在"替代 DFT"，更在于把非谐力常数与高阶声子散射纳入可系统开展的计算范畴；但四声子贡献强度在材料间高度异质（可在 43% 到可忽略间摆动），而通用势在谐声子性质上的表现并不总能由能量/力的拟合精度预示，预示热导导向的势验收需要以力常数复现与 Green–Kubo 对照为准。

## 核心要点

- **要点 1**：MLIP 在 $\kappa_L$ 预测上收敛为两条互补技术路线——"非谐力常数 + BTE"与"经典 MD（EMD/GK/HNEMD）"，前者保留逐模物理分辨率，后者隐式吸收全部高阶散射。
- **要点 2**：对非谐的刻画精度是 MLIP 用于热导预测的真正检验标准；谐声子（色散）吻合良好并不保证 $\kappa_L$ 准确，高阶力常数的复现能力更能表征势质量。
- **要点 3**：四声子散射贡献存在明显材料异质性——在 BAs 压低热导约 43%、在 WS₂ 约 35%，而在 TMD（MoS₂/MoSe₂）完全收敛后贡献可忽略；该分歧主要由散射相空间与低频带结构决定，而非方法伪差。
- **要点 4**：通用 MLIP 在谐声子性质上已接近 ready，但在强非谐或动力学远平衡构型下仍可能失准；参数高效微调与不确定性量化是通往可靠预测的现实校准路径。
- **要点 5**：热导导向的 MLIP 验收协议应包含第三/四阶力常数复现、小体系 Green–Kubo 对照与力误差噪声外推，而非仅报告力的 RMSE。

## 一、引言

### 为什么需要这篇综述

晶格热导率不仅是电子器件热管理等应用的关键参数，也是热电优值与材料设计的重要判据。其严格计算要么依赖 DFT 求取非谐力常数后解 BTE（成本随原胞原子数与对称性陡增），要么依赖 MD 中经验势的精度（而经验势对 $\kappa_L$ 的预测分散可高达一个数量级）。MLIP 正是被用来同时弥合这两条缺口的工具——它把量子力学的构型采样能力与经典力学的规模化能力合流。尽管已有若干综述系统梳理了"用机器学习预测 $\kappa_L$"的总体现状 [1, 2]，以及 NEP/GPUMD 在热输运 MD 上的方法教程 [3]，但近三年在通用势、参数高效微调与高阶非谐（四声子）重审上的进展，为判断"MLIP 热导预测的精度天花板与失效边界"提供了新的证据，恰恰是既有综述尚未充分覆盖的增量。

### 研究问题

本文围绕三个可回答的问题组织证据：

- RQ1：主流 MLIP 在 $\kappa_L$ 预测中收敛为哪两条技术路线，各自的体系适用性与成本—精度特征如何？
- RQ2：MLIP 对非谐声子特性尤其四声子散射的刻画能力如何，精度随高阶力常数如何变化？
- RQ3：通用 MLIP 是否已可直接用于热导预测，其可靠性与失效边界主要在哪里？

### 本文组织方式

全文先给定检索与方法（§二）与分类框架（§三），随后依次展开两条技术路线（§四 BTE/力常数路线、§五 经典 MD 路线）、非谐与四声子刻画能力（§六）、通用势与可靠性（§七），再做跨分支综合（§八）、开放问题（§九），最终逐条回答三个 RQ（§十）。

## 二、研究方法

本综述的检索信息源限定为 sciverse，经 `search_papers` 结构化检索与 `semantic_search` 语义检索执行。围绕五个视角独立检索后跨视角合并：① 视野/综述；② 非谐力常数 + BTE 路线；③ 经典 MD（EMD/GK/HNEMD/NEMD）路线；④ 通用势与方法层（benchmark、微调）；⑤ 裁判型文献（四声子重审、不确定性、失效边界）。关键词族覆盖 "machine learning interatomic potential thermal conductivity"、"ShengBTE anharmonic force constants"、"four-phonon machine learning potential"、"Green-Kubo neuroevolution potential" 等。

纳入标准：与 $\kappa_L$/声子/非谐散射直接相关、存在性经 sciverse 返回确认；综述模式不输出卷期页码/DOI，年份与题录字段从检索源 sciverse 抄录。最终入选 22 篇，覆盖 2019—2026 年，兼顾奠基经典与近三年增量；滚雪球基于高被引种子反查前置/后继，末轮零新增，达检索饱和。

证据类型上，本主题以计算物理的"方法 + benchmark"证据为主：MLIP 对非谐力常数/$\kappa_L$ 的复现精度（对 DFT/实验）构成核心判据，成本多报告为 DFT 的加速倍数或训练构型数。

## 三、分类框架

| 分支 | 组织轴 | 回答的 RQ | 代表性文献 |
|---|---|---|---|
| 四（BTE/力常数路线） | 能否以 MLIP 替代 DFT 求谐与非谐力常数并交 Phonopy/Phono3py/ShengBTE/fourphonon  | RQ1 | Mortazavi2020MTP, Korotaev2019CoSb3, Srivastava2024IFC, Togo2024OnTheFly |
| 五（经典 MD 路线） | MLIP 直接驱动 EMD/GK/HNEMD/NEMD 吸收全阶非谐 | RQ1 | Qian2019Si, Liu2021SnSe, Mortazavi2020C3N, Sha2023PbTe, Cao2025Metals, Chen2025InP |
| 六（非谐与四声子刻画） | MLIP 能否可靠刻画高阶声子散射 | RQ2 | Bandi2024ThO2, Liu2021wBAs, Han2023InSe, Zhang2023WS2, Kocabas2025TMD |
| 七（通用势与可靠性） | 通用势是否 ready + 失效边界 | RQ3 | Loew2025Universal, Grandel2026FT, Wen2020DUNN |

taxonomy 的整体逻辑是以"推算 $\kappa_L$ 的物理中间量"为轴切分：BTE 路线显式构造力常数，MD 路线隐式演进全阶势能面，二者互补；再叠加"势质量如何被刻画/是否可迁移"的纵向维度。空格（gap）在于：把 BTE 力常数的逐模物理分辨率与 MD 的全阶无截断能力真正合一的"跨方法一致性检验"在多数体系仍未常规执行——这是后文综合与开放问题的抓手。

## 四、BTE/非谐力常数路线

这一路线把 MLIP 用作 DFT 的高保真替身去采集谐与非谐力常数，再交给声子 BTE 求解器（Phonopy/Phono3py/ShengBTE/fourphonon）计算 $\kappa_L$。其核心贡献是把"获取非谐力常数"这一高熵计算瓶颈做分布式后处理，从而把原先仅适用于高对称、少原子原胞的 DFT 计算推广到低对称与多原子体系。

Mortazavi 等的工作是这条路线最早的系统化示范：用 DFT 分子动力学轨迹被动训练矩张量势（MTP），从训练好的 MTP 一次性提取非谐力常数并交给 ShengBTE，对多种体相与二维材料的 $\kappa_L$ 与全 DFT 结果吻合 [4]。这条"势替代 DFT 构型采样、力常数仍走显式提取"的范式与稍早 Korotaev 等对 CoSb₃ 方钴矿的尝试一脉相承——后者用主动学习显著压缩训练所需的量子力学构型数，仅数百次即可复现振动态与 $\kappa_L$，并比较了 BTE 与 Green–Kubo 两种后处理 [5]。二者差别体现了 BTE 路线的内在取舍：MTP/ShengBTE 方案强在把力常数提取并行化，而主动学习则强在减少昂贵的第一性原理训练集。

近年的推进集中在"如何从 MLIP 更省地获取非谐力常数"与"如何规模化"两个方向。Srivastava & Jain 提出用 ML 局部学习势能面来提取非谐力常数，在 220 种三元材料上把总计算耗时从约 48 万 CPU 小时降到 1.2 万以内，同时保持 $\kappa_L$ 误差在 10% 内 [6]——这不仅放大了一两个数量级的吞吐，也直接指向高通量材料筛选的应用。Togo & Seko 则把多项式 MLIP 以 on-the-fly 方式嵌入首性原理 $\kappa_L$ 计算流程，在 103 种 wurtzite/zincblende/rocksalt 化合物上验证了资源节约 [7]。这两项工作解释了 BTE 路线为何仍是高吞吐预测的主流选择：它保留了逐模分解的物理分辨率（能定位哪些声子支贡献最多），而这恰是热设计所需要的。

对比来看，BTE 路线的代价是力常数的阶数截断：高通量实现多止于三阶，四阶（四声子）需要额外高阶力常数，计算与存储都急剧增加。因此该路线对 $\kappa_L$ 的准确度，本质上取决于"把非谐截断到几阶"以及 MLIP 对每阶力常数的复现精度——这正是 §六 四声子重审所揭示的材料异质性来源之一。

| 代表工作 | 力常数获取方式 | 训练/构型代价 | 测试规模 | 与 DFT 吻合 | 说明 |
|---|---|---|---|---|---|
| Mortazavi2020MTP | 被动学习 MTP → ShengBTE | DFT-AIMD 短轨迹 | 多体相/2D 材料 | 良好 | BTE 路线奠基 |
| Korotaev2019CoSb3 | 主动学习 MTP + BTE/GK | 数百构型 | CoSb₃ 方钴矿 | 良好 | 主动学习省构型 |
| Srivastava2024IFC | ML 局部学习 PES 提非谐力常数 | 分布式后处理 | 220 三元材料 | 10% 内 | 数量级吞吐提升 |
| Togo2024OnTheFly | on-the-fly 多项式 MLP | 嵌入首性流程 | 103 化合物 | 良好 | 全流程资源节约 |

## 五、经典 MD 路线

与 BTE 路线显式构造力常数不同，经典 MD 路线让 MLIP 直接驱动平衡（EMD/Green–Kubo）或非平衡（NEMD/HNEMD）分子动力学，热流（或热电流自相关）隐式地吸收了势能面上全部阶数的非谐散射——没有"截断到几阶"的显式选择。这一路线尤其适合强非谐、低对称、含缺陷或无序的体系，其中的声子图像本身可能接近失效。

Qian 等最早把 ML 势应用到晶态与非晶硅的 $\kappa_L$，用 DFT 随机采样的势能面训练 MLIP 后经平衡 MD 计算，晶态与非晶硅均与实验吻合，示范了该路线跨越有序/无序边界的能力 [8]。强非谐热电材料是 MD 路线的天然主场：Liu 等用 MTP 参数化 SnSe 并做 200—900 K 的平衡 MD，复现了温度依赖的各向异性与四声子散射的作用 [9]；Sha 等用 neuroevolution potential（NEP）研究二维 PbTe，反而观察到位错增强应变下热导反常上升（低频声子增强所致）[10]。这两个例子说明 MD 路线不是简单"算数"，而是能揭示 BTE 谐框架难以解释的非谐现象。

统一势驱动的 MD 是近年另一条强趋势。Cao 等用 UNEP-v1 通用 NEP 结合高效 HNEMD 方法系统计算 16 种元素金属的晶格热导，结果与仅含声子-声子散射的 BTE 吻合，且明显优于传统嵌入原子势 [11]；Chen 等为 InP 训练 NEP 后以平衡 MD 得到 300—900 K 的 $\kappa_L$，与实验一致并刻画了微弱各向异性 [12]。二维材料上，Mortazavi 等用被动学习的 MLIP 经非平衡 MD 估算 C₃N 单层 $\kappa$ 约 418 W/(m·K)，调和了此前经典 MD 与首性原理之间的分歧 [13]。

MD 路线的代价是统计收敛与尺寸效应：有限体系、热流自相关的统计噪声以及 NEMD 的长度依赖都需要仔细处理，其热导本身也常对训练数据在非晶/低对称构型上的覆盖敏感。但当目标体系强非谐或已超出声子准粒子图像时，MD 路线的"无截断"特性构成不可替代的优势。

| 代表工作 | MLIP/方法 | MD 变体 | 体系 | 关键结论 |
|---|---|---|---|---|
| Qian2019Si | ML 势 | EMD | 晶态/非晶 Si | 均与实验吻合 |
| Liu2021SnSe | MTP | EMD | SnSe | 强非谐、各向异性、四声子 |
| Mortazavi2020C3N | 被动 MLIP | NEMD | C₃N 单层 | κ≈418 W/(m·K)，调和分歧 |
| Sha2023PbTe | NEP | EMD | 2D PbTe | 应变可反常增热导 |
| Cao2025Metals | UNEP-v1 | HNEMD | 16 元素金属 | 与声子-声子 BTE 吻合 |
| Chen2025InP | NEP | EMD | 体相 InP | 与实验一致，各向异性微弱 |

## 六、MLIP 对非谐与四声子散射的刻画能力

这个分支回答 RQ2 的核心：MLIP 能否可靠刻画高阶非谐声子散射。它同时是前两节力常数/热流来源的质量检验层，也是本综述分歧最集中之处。

在势质量侧，Bandi 等以 ThO₂ 的非谐振动哈密顿量为基准，对 GAP、ANN、GNN 三类 MLIP 逐一对照声子线宽、线移与 $\kappa_L$，发现 ANN/GNN 可良好复现至五阶非谐解 [14]——这为"MLIP 能刻画多高阶非谐"给出了一个量级上的下限。与之呼应，Loew 等指出训练数据即构型覆盖（而非模型架构）常是声子性质预测精度的更大限制，通过 DFPT 声子计算数据训练神经网络力场可在减少训练构型数的情况下显著提升声子预测精度 [15]。

高阶散射的实际物理贡献则呈现强异质性。在四声子压低的极端案例里：Liu 等在 wurtzite BAs 上用 MTP 获取高阶力常数并计入四声子散射，室温 a-b 面 $\kappa$ 降到约 1036 W/(m·K)，比不含四声子时低 43% [16]；Zhang 等用 GAP+BTE 重审 WS₂ 单层，发现四声子使面内 $\kappa$ 降约 34.68%，主因是低频重分布散射 [17]。Han 等用 Green–Kubo-Deep Potential（GK-DP）算出 InSe 单层 $\kappa\approx 9.52$ W/(m·K)，与实验吻合，而忽略四声子的 BTE-DFT 给出 13.08 W/(m·K)，说明正是四声子的缺位造成了理论高估 [18]。

但 Kocabaş 等对 MoS₂/MoSe₂ 的系统重审提供了相反的裁决：他们用 GAP、MACE、NEP、HIPHIVE 四种 MLFF（含 foundation model）对照 DFT，并把收敛检验延伸到常规极限之外，再用 HNEMD 交叉验证，结论是——与某些近期主张相反——完全收敛的四声子过程对 TMD 本征 $\kappa$ 的贡献可忽略 [19]。

把这两组证据放在一起，四声子"显著"与"可忽略"的裁决并不矛盾，而是由材料的散射相空间与低频带结构决定：在 BAs、InSe、WS₂ 这类存在大声子带隙或强低频重分布通道的体系中，四声子提供了额外的相空间而显著压低 $\kappa$；在 MoS₂/MoSe₂ 这类由三声子主导、四声子通道被带结构抑制的体系中则贡献可忽略。一个可执行的判据是：**当三声子 BTE 已给出与 Green–Kubo/MD 明显偏高、且体系存在大声子带隙或低频重分布时，四声子不可省略；反之在四声子收敛检验稳定的 TMD 类体系中，三声子即足够**。这一判据把"是否要算四声子"从经验取舍变成可由带结构与收敛性检验驱动的决策。

| 体系 | MLIP/方法 | 四声子对 κ 的影响 | 为何载决 |
|---|---|---|---|
| w-BAs [Liu2021] | MTP + 四声子 | 降约 43% | 高频、大带隙 |
| WS₂ 单层 [Zhang2023] | GAP + BTE | 降约 34.68% | 低频重分布散射 |
| InSe 单层 [Han2023] | GK-DP vs BTE-DFT | BTE 忽略四声子故高估 | 大小光学带隙、高声群速度 |
| MoS₂/MoSe₂ [Kocabas] | GAP/MACE/NEP/HIPHIVE | 收敛后可忽略 | 三声子主导、带结构抑制 |
| ThO₂ [Bandi] | GAP/ANN/GNN | —（非谐基准） | 五阶复现良好 |

## 七、通用势与可靠性

RQ3 指向一个更前沿的问题：面向全元素的全能（universal）MLIP 是否已可直接拿来预测 $\kappa_L$，以及它的可靠性边界。这既涉及能量/力精度与热导精度是否一致，也涉及外推风险的可控性。

Loew 等在约 10 000 个从头声子计算上 benchmark 了一批主流通用势对谐声子性质的预测，发现部分模型能在谐声子性质上达到高精度，但另一些模型即使对接近动力学平衡材料的能量与力拟合极佳，声子预测仍有显著偏差 [20]。这一"能量/力准却不保证声子准"的反差，是对 §六"非谐/高阶刻画才是检验标准"的横向延伸：谐声子（色散）与 $\kappa_L$ 的精度都未必与能量/力 RMSE 单调对应，质的验收必须以声子（乃至力常数）为直接输入。

针对通用势在特定体系上的失准，参数高效微调是低成本校准路径。Grandel 等在 53 个材料体系上对比不同微调策略（含其提出的 Equitrain/LoRA），发现微调后的模型一致优于底层预训练模型与从头训练模型，少至 10 个附加构型即有可观增益 [21]——这为"如何把通用势变成某体系可信势"给出了明确的操作性答案。

不确定性与外推可靠性是通用势发力的另一侧。Wen & Tadmor 指出 MLIP 缺乏内建物理模型，其训练集外延时的精度是未知的，并提出基于 dropout 的不确定性量化（DUNN）势，既能量化静态/动力学性质（含声子色散）的传播误差，也能用于检测训练集外构型、有时充当该次计算的精度预测器 [22]。这一能力对热导预测尤为重要——热导常对稀有的高频或大振幅构型敏感，而这些恰是训练集覆盖最薄弱之处。

## 八、综合讨论

把四条分支并置，可以看到一个跨分支收敛的判断：**MLIP 在 $\kappa_L$ 预测上的真正检验不是"复现 DFT 能量/力"而是"复现非谐声子散射"**。BTE 路线（§四）显式检验每阶力常数，MD 路线（§五）隐式依赖势能面整体形状，二者虽然机制不同，但它们的误差都集中在非谐区域——§六 的四声子重审与 §七 通用势的谐声子 benchmark 从两个方向印证了这一点。

分支间的张力也很明了：BTE 路线强在物理分辨率与高通量（§四 的 220/103 化合物），但受力常数阶数截断约束；MD 路线无截断能覆盖强非谐体系（§五 的 SnSe/PbTe），但牺牲逐模归属并受有限尺寸/统计限制。二者的理想耦合是"跨方法一致性检验"——Korotaev 对 CoSb₃ [5]、Han 对 InSe [18]、Kocabaş 对 TMD [19] 都在做 BTE 与 MD/GK 的互校，但这一做法尚未成为常规，这正是 taxonomy 中最大的空格。

四声子的分歧裁决（§六）是全文洞见浓度最高的地方：同一物理机制（高阶非谐散射）在 BAs/InSe/WS₂ 显著、在 MoS₂/MoSe₂ 可忽略，裁决钥匙是散射相空间与低频带结构而非方法伪差。这一结论同时约束了两条技术路线的适用边界——需要精确 $\kappa_L$ 的体系必须先做四声子显著性检验，而不是默认某一路线。

## 九、开放问题与未来方向

- **跨方法一致性检验未常规化**：BTE 逐模分辨率与 MD 全阶无截断的直接互校（及收敛性检验）在多数体系仍是手动、逐案进行；缺少标准化的"$\kappa_L$ 基准协议"，导致各工作报告的精度口径不统一。
- **四声子显著性的预判指标缺失**：目前只能事后从带隙与收敛检验得知四声子是否重要；缺少一个可先从声子带结构与散射相空间预估"四声子重要性"的廉价先验。
- **强非谐/绝缘体上通用势的完整失效地图未建立**：已有谐声子 benchmark [20]，但强非谐（Ioffe–Regel 接近失效）、$f$-电子、含缺陷等体系上通用势的系统失效刻画仍缺。
- **无序/玻璃体系的 Wigner 隧穿与 MLIP 结合仍在早期**：非晶与强无序体系依赖波粒隧穿输运，MLIP（如 GAP）已被用于无序碳，但其与 Wigner 输运方程的常规化结合仍是开放方向。
- **训练数据覆盖的"热导导向"采样欠发达**：热导对稀有大振幅/高频构型敏感，如何让训练采样显式面向"能校准非谐散射"的构型，而非通用能量/力，仍是方法学空白。

## 十、结论

- **RQ1**：主流 MLIP 已收敛为两条互补技术路线。非谐力常数+BTE 路线（§四）以 MTP/主动学习/on-the-fly 多项式把 DFT 构型采样替换为 MLIP，保留逐模物理分辨率并使高通量（220/103 化合物）成为可能 [4, 5, 6, 7]；经典 MD 路线（§五）让 MLIP 直接驱动 EMD/GK/HNEMD/NEMD，隐式吸收全阶非谐，更适合强非谐与无序体系 [8, 9, 13, 10, 11, 12]。前者贵在分辨率与吞吐，后者贵在无截断与普适。
- **RQ2**：MLIP 对非谐声子散射的刻画可达数阶（ThO₂ 五阶复现良好）[14]，但其物理贡献高度材料依赖——四声子可在 w-BAs 压低 $\kappa$ 约 43% [16]、在 WS₂ 约 35% [17]、在 InSe 若忽略则导致理论高估 [18]，而在 MoS₂/MoSe₂ 完全收敛后可忽略 [19]。该异质由散射相空间与低频带结构决定，故"是否算四声子"应由带结构与收敛性检验驱动，而非猜测。
- **RQ3**：通用 MLIP 在谐声子性质上已接近 ready，但能量/力拟合精度并不保证声子精度 [20]；参数高效微调（少至 10 构型）能把通用势校准为可信势 [21]，而 dropout 类不确定性量化提供了检测训练集外外推的机制 [22]。可靠性边界集中在强非谐体系、动力学远平衡构型与训练覆盖薄弱的高频/大振幅构型。

综合而言，本综述的核心贡献在于把"MLIP 用于 $\kappa_L$"从"DFT 加速器"的单一叙事，重述为"非谐声子散射刻画能力之争"：两条技术路线的分化、四声子的材料异质性、以及通用势"能量准不等价于热导准"的反差，共同指向同一判断——热导导向的 MLIP 验收应以力常数复现（尤其非谐部分）、Green–Kubo 对照与四声子收敛检验为准，而非以能量/力的 RMSE 为准。

## 参考文献

[1] Luo Y, Li M, Yuan H, Liu H, Fang Y, et al., “Predicting lattice thermal conductivity via machine learning: a mini review,” npj Computational Materials, 2023.
[2] Arabha S, Aghbolagh Z S, Ghorbani K, Hatam-Lee S M, Rajabpour A, et al., “Recent advances in lattice thermal conductivity calculation using machine-learning interatomic potentials,” Journal of Applied Physics, 2021.
[3] Dong H, Shi Y, Ying P, Xu K, Liang T, et al., “Molecular dynamics simulations of heat transport using machine-learned potentials: A mini-review and tutorial on GPUMD with neuroevolution potentials,” Journal of Applied Physics, 2024.
[4] Mortazavi B, Podryabinkin E V, Novikov I S, Rabczuk T, Zhuang X, Shapeev A V, “Accelerating first-principles estimation of thermal conductivity by machine-learning interatomic potentials: A MTP/ShengBTE solution,” Computer Physics Communications, 2020.
[5] Korotaev P, Novoselov I I, Yanilkin A, Shapeev A V, “Accessing thermal conductivity of complex compounds by machine learning interatomic potentials,” Physical Review B, 2019.
[6] Srivastava Y, Jain A, “Accelerating prediction of phonon thermal conductivity by an order of magnitude through machine learning assisted extraction of anharmonic force constants,” Physical Review B, 2024.
[7] Togo A, Seko A, “On-the-fly training of polynomial machine learning potentials in computing lattice thermal conductivity,” arXiv:2401.17531, 2024.
[8] Qian X, Peng S, Li X, Wei Y, Yang R, “Thermal conductivity modeling using machine learning potentials: application to crystalline and amorphous silicon,” Materials Today Physics, 2019.
[9] Liu H, Qian X, Bao H, Zhao C Y, Gu X, “High-temperature phonon transport properties of SnSe from machine-learning interatomic potential,” J Phys Condens Matter, 2021.
[10] Sha W, Dai X, Chen S, Yin B, Guo F, “Phonon thermal transport in two-dimensional PbTe monolayers via extensive molecular dynamics simulations with a neuroevolution potential,” Materials Today Physics, 2023.
[11] Cao S, Wang A, Fan Z, Bao H, Qian P, et al., “Lattice thermal conductivity of 16 elemental metals from molecular dynamics simulations with a unified neuroevolution potential,” Journal of Applied Physics, 2025.
[12] Chen B, Cao L, Wang Q, Cheng C, Qi Z, et al., “Predicting thermal conductivity of InP via molecular dynamics simulations with machine learning potential,” Journal of Physics D: Applied Physics, 2025.
[13] Mortazavi B, Podryabinkin E V, Novikov I S, Roche S, Rabczuk T, et al., “Efficient machine-learning based interatomic potentialsfor exploring thermal conductivity in two-dimensional materials,” Journal of Physics: Materials, 2020.
[14] Bandi S, Jiang C, Marianetti C A, “Benchmarking machine learning interatomic potentials via phonon anharmonicity,” Machine Learning: Science and Technology, 2024.
[15] Loew A, Wang H C, Cerqueira T F T, Marques M A L, “Training machine learning interatomic potentials for accurate phonon properties,” Machine Learning: Science and Technology, 2024.
[16] Liu Z, Yang X, Zhang B, Li W, “High Thermal Conductivity of Wurtzite Boron Arsenide Predicted by Including Four-Phonon Scattering with Machine Learning Potential,” ACS Applied Materials & Interfaces, 2021.
[17] Zhang G, Shi-Lin D, Yang C, Han D, Xin G, et al., “Revisiting four-phonon scattering in WS2 monolayer with machine learning potential,” Applied Physics Letters, 2023.
[18] Han J, Zeng Q, Chen K, Yu X, Dai J, “Lattice Thermal Conductivity of Monolayer InSe Calculated by Machine Learning Potential,” Nanomaterials, 2023.
[19] Kocabas T, Keceli M, Gurel T, Milosevic M V, Sevik C, “Thermal conductivity limits of MoS2 and MoSe2: Revisiting high-order anharmonic lattice dynamics with machine learning potentials,” Applied Physics Reviews, 2025.
[20] Loew A, Sun D Y, Wang H C, Botti S, Marques M A L, “Universal machine learning interatomic potentials are ready for phonons,” npj Computational Materials, 2025.
[21] Grandel J, Benner P, George J, “Parameter-Efficient Fine-Tuning of Machine-Learning Interatomic Potentials for Phonon and Thermal Properties,” arXiv:2604.01017, 2026.
[22] Wen M, Tadmor E B, “Uncertainty quantification in molecular simulations with dropout neural network potentials,” npj Computational Materials, 2020.
