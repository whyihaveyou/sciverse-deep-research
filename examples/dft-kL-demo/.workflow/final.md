# DFT 能算什么物理量：以晶格热导率为中心的第一性原理能力边界与数据生成启示

## 摘要

回答"DFT 到底能算哪些物理量、尤其是能不能算出晶格热导率 κ_L"这一问题，本文梳理第一性原理（DFT/DFPT）在材料物性计算上的能力谱系与精度边界，并把它落到一个具体诉求上——用 DFT 为主、机器学习势（MLIP）加速，构造**替代 SLACK/Slack 型模型**的第一性原理热导数据集。核心结论分三层：(1) DFT 能算的物理量极其广泛——电子结构（能带、带隙、态密度）、力学（弹性模量张量、声速）、热力学（声子谱、德拜温度、热容、热膨胀、Grüneisen 参数）、电子输运（电导、Seebeck、电子热导）与晶格输运（声子群速度、散射率、κ_L）；(2) **κ_L 完全可以用 DFT 算，且这是当前"无参数真值"的黄金标准**——标准路径是谐/非谐力常数 → 声子色散与群速度 → 三声子散射率 → 线性化玻尔兹曼输运方程（BTE），工具如 Phono3py、ShengBTE 已成熟并被广泛验证；(3) 对高通量建数据集，纯 DFT 的 BTE 计算成本过高，**MLIP 加速是现实解**——既可用 MLIP 直接跑分子动力学/抽取非谐力常数（较 BTE 快一个量级），也可用弹性量驱动的近似模型（如 PET）做初筛，但需区分"真值级精度"与"近似筛选级"。关键提醒：AFLOW/AGL 的 κ_L 恰是 quasiharmonic Debye（Slack 型）模型输出而非 BTE 真值 [1]，这正是需要被替代的对象；造新数据集时，全第一性 BTE 结果才是可与实验对标的"真值"，近似模型只宜做初筛或特征。

## 一、引言

你此前的工作（Slack → Wang → 符号回归）把三代热导经验公式梳理清楚并基于 AFLOW 数据验证了新公式，但一个根本性的怀疑贯穿始终：**AFLOW 里的 κ_L 不是实验值，也不是第一性原理精确解，而是 Slack 型模型的输出** [1]。用这样的"目标值"训练新公式，本质上是在逼近一个近似模型，而非逼近物理真值。你们已有的基于机器学习势函数（MLIP）的 DFT 工具，正是为了绕开这个循环——用第一性原理直接算真值。本文要回答三个问题：

- **RQ1**：DFT（第一性原理）能计算哪些物理量？其能力谱系与各自精度如何？
- **RQ2**：晶格热导率 κ_L 能不能用 DFT 算？有哪些方法路径（力常数+BTE、平衡/非平衡 MD、MLIP 加速）？
- **RQ3**：对你们"构造替代 SLACK 的第一性原理新数据集"这件事，最可行的技术路线是什么？哪些量必须精确算、哪些可近似、哪些需用 MLIP 加速与如何校验？

结论在最后逐条回答。本文聚焦绝缘体/半导体的晶格热导（声子主导），金属与合金热导只作边界提及。

## 二、研究方法

检索经 sciverse MCP 执行（`search_papers` 多视角：first-principles phonon/BTE、DFT transport properties、MLIP lattice thermal conductivity、Grüneisen parameter/quasiharmonic Debye），并以 arXiv 补充 MLIP-加速非谐力常数等预印本。纳入 13 篇代表工作：覆盖第一性 BTE 标准框架 `[2, 3, 4]`、AFLOW/AGL 模型的原始论文 `[1]` 与 Slack 式公式修正 `[5]`、MLIP 加速声子/热导 `[6, 7, 8, 9]`、高通量热导与描述符 `[10, 11]`、单晶应用 `[12]`、电子热导 `[13]`。未做滚雪球扩展（时间预算），为已知覆盖边界。

## 三、分类框架

按"DFT 能算什么"的物理维度分四支：

- **A. 电子结构与电子输运**——能带/带隙/态密度，电导/Seebeck/电子热导 `[13]`；
- **B. 力学与声子（谐）**——弹性张量、声速、声子色散、德拜温度、热容 `[2, 10, 11]`；
- **C. 非谐与晶格输运**——Grüneisen 参数、三/四声子散射、κ_L（本文核心）`[2, 3, 4, 12]`；
- **D. 高通量与 MLIP 加速**——如何把上面"贵"的 DFT 变成"可批量跑真值"的工具 `[6, 7, 8, 9, 1, 5]`。

A–C 是物理能力谱系，D 是工程化路径；四个维度共同支撑"造真值数据集"的决策。

## 四、A. DFT 的物理量能力谱系

DFT 的第一性原理能力远超"算个总能"。从标准 DFT/DFPT 可以直接或经后处理得到：

- **电子结构**：能带、带隙、态密度、有效质量、功函数——预测带隙本身有 PBE 低估问题，需 G0W0/HSE 修正，这是已知边界。
- **力学**：把原胞做小应变扰动，由总能-应变曲线拟合弹性常数张量 C_ij，进而得体模量 B、剪切模量 G、声速与德拜温度。高通量弹性计算已被 AGL 等模块大量应用 `[1, 10]`。
- **谐声子/热力学**：DFPT 或有限位移法得谐力常数 → 声子色散、声子态密度、德拜温度、定容热容。这部分是"热学量"的地基。
- **电子输运**：结合半经典 Boltzmann（如 BoltzTraP）算 Seebeck、电导、电子热导率。注意电子热导的鲁棒估计需与 Seebeck 自洽，不能简单用 Wiedemann-Franz 常数 Lorenz 数（高 Seebeck/半导体时失效）`[13]`。
- **晶格输运**：见下一章，是 DFT 热导能力的核心。

### 4.1 哪些物理量与"热导数据"直接相关

对照你们数据集里的字段，DFT 能第一性给出其中大部分：弹性模量 B/G（直接）、声速 v_L/v_t/v_s（由弹性与密度导出）、德拜温度（由声速/声子谱导出）、Grüneisen 参数 γ（由声子频率对体积的依赖导出，见 C 章）、热容、热膨胀、以及**κ_L 本身**。也就是说，你们现在从 AFLOW 查表的这些量，原则上都能用 DFT 自己算——这正是"摆脱对 SLACK 模型的依赖"的前提。

## 五、B. 声子与热力学的谐性计算

谐性部分是"能算得好"的成熟区间。标准流程（`[2]` 框架）：DFT/DFPT 给出谐力常数 → 谐晶格动力学得声子频率与极化矢量 → 从而得声子色散、群速度、态密度与德拜温度。谐声子的收敛判据是 q 网格与截断收敛、以及"无虚频"（虚频＝动力学不稳定，该材料不可作为稳定晶体纳入数据集）。声子频率是后续所有量（热容、Grüneisen、散射率）的基础，因此**数据集里每个材料的声子谱本身就是一个关键、可与 AGL [1] 对比的校验量**。高通量下谐声子也可用 MLIP 通用势加速（见 D 章），声子频率 MAE 可达 ~0.18 THz `[6]`。

## 六、C. 非谐与晶格热导率：DFT 能不能算 κ_L

### 6.1 标准路径：力常数 → 三声子散射 → BTE（能算，且是黄金标准）

**结论先行：κ_L 完全能由 DFT 第一性算出，且精度可与实验对标、无需拟合参数。** 路径（`[2, 3]`）：

1. 谐力常数 → 声子频率 ω、群速度 v_g；
2. 三阶（三次）力常数 → 三声子散射矩阵元；
3. 由散射矩阵元 + 占据数算声子散射率（寿命）；
4. 代入线性化 Peierls-Boltzmann 输运方程（或弛豫时间近似 RTA）解出 κ_L [3]。

这要求对每个材料做谐 + 三阶力常数计算（有限位移法需数个超胞、每超胞多次位移的 DFT 计算）。工具套件成熟：Phono3py、ShengBTE 等，已在硅等基准材料上与实验高度吻合 `[2, 3]`。晶体实例有多元化合物（如 CrSi2，单晶+多晶、含 Cahill 最低 κ_L 与晶粒尺寸效应）`[12]`。

### 6.2 两个精度陷阱

- **RTA/三声子的局限**：最低阶理论（三声子 + RTA）在部分材料不够——如强非谐材料、光学支与声学支能隙大的体系，需考虑四声子/更高阶散射与频移展宽 `[4]`。四声子若不纳入，会高估 κ_L（如 InSe 案例）。
- **偶发的不一致**：BTE 某些情况下与实验偏差因高阶散射显著；此时平衡/非平衡 MD + MLIP 可捕获全阶非谐、有时反而更准 `[8]`。这意味着**造数据集时应允许"方法级校核"**：高价值/异常值材料用两种独立方法交叉验证。

### 6.3 Grüneisen 参数的第一性来源

你们新公式依赖 γ。γ 可由声子频率对体积（或应变）的依赖算出（quasiharmonic），是全第一性的量 `[14]`；也可由 AGL 这类 quasiharmonic Debye 模型给出 `[1]`。区别在于前者更准、后者更便宜但带模型近似。Gan 2022 提出的 GQA 进一步修正了 Slack 式公式对多原子原胞的尺寸不一致问题，用第一性 Grüneisen 更贴近实验趋势 `[5]`——这对"用 γ 预测 κ_L"的半经验路线是直接升级。

## 七、D. 高通量与 MLIP 加速：造数据集的工程解

纯 DFT 的 BTE 对数千材料太贵（每材料数天机时），高通量造数据集必须分层：

**第一层（真值层）：全第一性 BTE 或 MLIP-MD**，对"最终入库的 κ_L 真值"用。全 BTE 精度最高但最贵；MLIP 加速是现实折中——MLIP 可把抽取非谐力常数的成本降一个量级 `[7]`，或用 MLIP 直接跑分子动力学（MLP-MD）捕获全阶非谐 `[8]`。MLIP 的准确性取决于训练覆盖度，需对每个体系做 DFT 校核（见 6.2）。

**第二层（筛选/特征层）：弹性量驱动的高通量近似**。如 PET 模型用体模量/剪切模量估计高温极限 κ_L，226 材料与实验吻合 `[11]`；或建立"弹性/声子 + ML 预测 κ_L"的 property map `[10]`。这类方法只宜做初筛、或与你们已有的符号回归公式类比，**不适合当真值**。

**通用 MLIP 声子加速**：MACE 等在 2738 材料语料上训练，声子频率误差可控，可直接复用加速谐声子计算 `[6]`。这正好利用你们已有的 MLIP-DFT 工具。

**一个直接的注意点**：AFLOW 的 AGL 用 quasiharmonic Debye 给出 κ_L，其论文自己声明"显著比全 ab initio 便宜、能可靠预测 κ_L 的序数排名" `[1]`——即 AGL/Slack 给出的是**趋势级/排名级**结果，不是数值真值。这正是你们想摆脱的东西：**新数据集若以 "κ_L 真值" 为目标，应以全第一性 BTE 结果入库，AGL/Slack 值只宜作为对照/旧基线，绝不作为 ground truth。**

## 八、综合讨论

把四支合起来，对"造替代 SLACK 的第一性原理热导数据集"给出一个清晰的可行域：

- **能算的物理量足够支撑数据集**：弹性、声子、德拜温度、热容、Grüneisen、κ_L 都能 DFT 全第一性给出 `[2, 10, 1]`，不必再依赖任何经验模型。
- **κ_L 真值的现实路径**：对目标材料清单，先用 MLIP 加速谐声子 + 非谐力常数抽取（较 BTE 快一个量级）`[7, 6]`，得到 BTE 级 κ_L 作为入库真值；对高价值或异常材料用 MLP-MD 交叉校验以覆盖高阶散射 `[8, 4]`。
- **与现有公式工作的衔接**：你们的符号回归公式 ABLK 可以作为"特征/初筛"与真值库共存——真值库用于训练/验证，近似公式用于高通量初筛，两层各司其职，而非互相替代。

争议不是"DFT 能不能算 κ_L"（能，很清楚），而是"规模与精度怎么取舍"——这正是数据生成要决策的。

## 九、开放问题与落地建议

- **真值量级齐整**：BTE 级 κ_L 的公认系统误差尚未完全量化，建议在数据集里对每材料标注"方法（RTA/全 BTE/MLP-MD [8]）+ 泛函（PBE/GGA 等）+ q 网格收敛"，像 AGL [1] 一样提供可追溯元数据，但精度目标远高于 AGL。
- **校验基准**：建议先跑一个已知实验 κ_L 的校准集（如 Si、金刚石、BAs）`[8, 2]`，确立 BTE 与 MLP-MD 两条路径的误差带，再推广到未知材料。
- **四声子/强非谐体系**：对强非谐或光学支能隙大的材料，三声子 BTE 可能高估，需 MLP-MD 或四声子处理 `[4, 8]`——数据集应标记这些"需高阶校正"的样本。
- **泛函依赖**：弹性/声子依赖交换关联泛函（PBE 是 AGL [1] 默认），造库时应统一泛函或对比 GGA 与 meta-GGA 以量化偏差。

## 十、结论

- **RQ1**：DFT 能算的物理量极广——电子结构、力学、谐声子/热力学、电子输运、晶格输运全覆盖；你数据集里除微观结构（晶界/缺陷）外几乎都能第一性给出。
- **RQ2**：**晶格热导率 κ_L 能且应当用 DFT 算**——标准路径是谐/三阶力常数 + 声子 BTE，成熟且与实验对标 `[2, 3]`；MLIP 加速是把它推向高通量的现实手段 `[7, 8, 9]`。
- **RQ3**：造替代 SLACK 的真值数据集，可行路线是"MLIP 加速 BTE 级 κ_L 作真值 + 弹性近似模型作初筛 + MLP-MD [8] 交叉校验高阶散射"，并全程标注方法与泛函元数据；AFLOW/AGL 的 Slack 型值仅作旧对照，不当 ground truth `[1]`。

## 参考文献

[1] Toher C, Plata JJ, Levy O, de Jong M, Asta M, Nardelli MB, Curtarolo S, “High-throughput computational screening of thermal conductivity, Debye temperature, and Grüneisen parameter using a quasiharmonic Debye model,” Physical Review B, 2014.
[2] McGaughey AJH, Jain A, Kim H-Y, Fu B, “Phonon properties and thermal conductivity from first principles, lattice dynamics, and the Boltzmann transport equation,” Journal of Applied Physics, 2019.
[3] Lindsay L, “First Principles Peierls-Boltzmann Phonon Thermal Transport: A Topical Review,” Nanoscale and Microscale Thermophysical Engineering, 2016.
[4] Jain A, Srivastava Y, Gokhale AG, Virakante N, Kagdada HL, “Higher-order thermal transport theory for phonon thermal transport in semiconductors using lattice dynamics calculations and the Boltzmann transport equation,” arXiv (Cornell University), 2025.
[5] Gan CK, Koh EK, “A size-consistent Grüneisen-quasiharmonic approach for lattice thermal conductivity,” Europhysics Letters, 2022.
[6] Lee H, Hegde VI, Wolverton C, Xia Y, “Accelerating high-throughput phonon calculations via machine learning universal potentials,” Materials Today Physics, 2025.
[7] Srivastava Y, Jain A, “Accelerating Phonon Thermal Conductivity Prediction by an Order of Magnitude Through Machine Learning-Assisted Extraction of Anharmonic Force Constants,” arXiv (Cornell University), 2024.
[8] Ouyang Y, Yu C, He J, Jiang P, Ren W, Chen J, “Accurate description of high-order phonon anharmonicity and lattice thermal conductivity from molecular dynamics simulations with machine learning potential,” Physical Review B, 2022.
[9] Arabha S, Aghbolagh ZS, Ghorbani K, Hatam-Lee SM, Rajabpour A, “Recent advances in lattice thermal conductivity calculation using machine-learning interatomic potentials,” Journal of Applied Physics, 2021.
[10] Juneja R, Yumnam G, Satsangi S, Singh AK, “Coupling the High-Throughput Property Map to Machine Learning for Predicting Lattice Thermal Conductivity,” Chemistry of Materials, 2019.
[11] Yan S, Wang Y, Fang T, Ren J, “High-Throughput Estimation of Phonon Thermal Conductivity from First-Principles Calculations of Elasticity,” J. Phys. Chem. A, 2022.
[12] Nakasawa H, Hayashi K, Takamatsu T, Miyazaki Y, “Lattice dynamics and lattice thermal conductivity of CrSi2 calculated from first principles and the phonon Boltzmann transport equation,” Journal of Applied Physics, 2019.
[13] Chen M, Podloucky R, “Electronic thermal conductivity as derived by density functional theory,” Physical Review B, 2013.
[14] Niranjan MK, Kumar V, Karthikeyan R, “Gruneisen parameter and thermal expansion coefficients of NiSi2 from first-principles,” Journal of Physics D: Applied Physics, 2014.
