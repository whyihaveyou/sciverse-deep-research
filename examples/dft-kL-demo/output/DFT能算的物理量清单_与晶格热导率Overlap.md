# DFT 能算的物理量清单，及与晶格热导率（κ_L）的 Overlap

## 摘要

本文产出一份**可为用户直接使用的"DFT 能算的物理量"系统清单**，并按"是否与晶格热导率 κ_L 相关"给每一项标注相关性等级，最后给出 **DFT 可算 ∧ 与 κ_L 相关** 的 overlap 交集——这正是用户用来圈定"哪些 DFT 计算既可行、又喂给晶格导热研究"的清单。核心结论：DFT（含 DFPT）能算的物性横跨结构、电子、力学、热力学、输运五大谱系；其中与 κ_L 直接相关的一阶量（决定 κ_L 公式的输入）包括弹性张量/模量、声速、德拜温度、Grüneisen 参数、声子色散与群速度、三阶力常数（非谐）——这些全部可第一性计算；二阶级物理量（热容、热膨胀、声子寿命、κ_L 本身）在其上一阶或一阶+散射计算之上得到。overlap 的核心：**你此前符号回归公式 / AFLOW 数据集里的几乎所有输入字段（B, G, ρ, V, N, γ, θ_D, θ_ac, Cv, α）都是 DFT 可直接算的**，因此用你自己的 MLIP-DFT 工具产出一套"第一性真值特征集"是可行的——只需把当前依赖的 Slack 型 κ_L 目标值换成 BTE 级 κ_L（见 RQ2）。

## 一、引言

目标很直接：既然要造替代 SLACK 的真值数据集，就得先知道 **DFT 到底能给我们哪些物理量**，再看其中**哪些和晶格导热（κ_L）有关**。本报告回答：

- **RQ1**：DFT（含 DFPT）能计算哪些物理量？把它们组织成一张可勾选的清单。
- **RQ2**：哪些 DFT 可算量直接决定/影响 κ_L（即与晶格热导相关）？挑出 overlap 交集。

## 二、研究方法

检索经 sciverse MCP 多视角执行（弹性常数/弹性张量、热电 BoltzTraP [1]、DFPT 声子、第一性 BTE 热导、MLIP 加速、Grüneisen/quasiharmonic），纳入 17 篇代表工作（含 DFT 算 κL 的开山基准 [2] 与工具包交叉基准 [3]）；以入选文献为种子经滚雪球追引其前置技术链，末轮新增 0 篇、每个子方向核心文献 ≥3 篇，达检索饱和。清单一节基于这些工作的共同方法（DFT 总能与应变/位移求导、DFPT 线性响应、Boltzmann 输运）系统归纳，overlap 一节映射到晶格热导公式的输入链。

## 三、DFT 能算的物理量：系统清单

DFT（含 DFPT 线性响应）第一性能力覆盖五大物理谱系。每一项给出：**它是什么、DFT 怎么算、常规可行度、与 κ_L 的关联**——前三者界定"DFT 能不能给你这个量"，后者标出"这个量对晶格导热研究有没有用"。可行度标记：★★★=常规成熟；★★=需高阶力常数/后处理，可行但较重；★=前沿或高成本。

### 3.1 结构性质（★★★）

- **晶格常数、原子坐标、平衡结构**：总能最小化直接得到，是所有计算的基础。DFT 的 PBE/GGA 通常把晶格常数高估约 1%——对依赖体积的后续量（声速、德拜温度）有系统性小偏差，造库时需统一泛函。
- **形成能/结合能、相稳定性**：总能差给出热力学稳定性排序，是材料筛选的第一道闸。
- **相变压、压力-体积状态方程（EOS）**：E-V 曲线拟合 Birch-Murnaghan 方程得 B 及其压力导数，纯元素全流程已有基准 
[4]。
- **动力学稳定性**：通过声子色散是否含虚频判定（见 3.4），高通量下是稳定性筛选的关键 [5]。

### 3.2 电子结构（★★★；带隙有泛函偏差）

- **能带、带隙、态密度、有效质量**：电子结构计算的核心。注意 PBE 系统性低估带隙，需 GGA+mBJ（如 [1] 的 MgGa2O4 带隙 4.9 eV 用 mBJ）、HSE 或 G0W0 修正才与实验可比。
- **功函数、电负性、磁性、自旋-轨道耦合**：取决于材料体系，常规可行。
- 与 κ_L 的关联：带隙宽窄影响电子-声子耦合，但对本征晶格热导的直接影响弱；主要通过"区分绝缘体/半导体/金属"（金属电子热导占主导，Slack 类公式不适用）间接相关。

### 3.3 力学/弹性（★★★）

弹性张量可从总能-应变或应力-应变拟合得到，是 DFT 最成熟的物性之一：

- **二阶弹性张量 C_ij、体模量 B、剪切模量 G、杨氏模量 E、泊松比 ν**：单晶应变法常规可得 [6, 4]。多晶的 B/G 用 VRH 平均（这和你们 AFLOW 数据集口径一致）。
- **弹性各向异性比**：单晶方向性信息，对"热导是否各向异性"有提示（多晶 VRH 会丢失）。
- **三阶/四阶弹性常数**：由总能-应变高阶拟合（应变需较大、数值敏感）[6]——三阶弹性常数与 Grüneisen 参数及非谐性直接相关，是连接"弹性 ↔ 晶格导热"的桥梁。
- **声速 v_L/v_t/v_s**：由模量+密度导出，是动理论 κ=⅓Cv·v·l 中的 v，也是德拜温度的输入。
- 与 κ_L 的关联（强）：B/G/声速/德拜温度是 Slack 型公式和你们符号回归公式的直接输入 [7, 8]。

### 3.4 声子与热力学（★★★）

- **声子色散、声子态密度、声子频率**：DFPT 或有限位移法（Phonopy 类工具）常规可得。DFPT 高通量需注意收敛与虚频陷阱 [5]。
- **德拜温度 θ_D、声学德拜温度 θ_ac**：由声速/声子谱导出；AFLOW/AGL 用 quasiharmonic Debye 给 [7]。
- **热容 Cv/Cp（声子贡献）**：由声子态密度直接积分。
- **Grüneisen 参数 γ**：声子频率对体积的依赖（quasiharmonic），是"非谐性"的核心度量，直接进 κ_L 公式的非谐项 [7, 9]。
- **热膨胀系数 α**：quasiharmonic 由 γ 与热容得到。
- 与 κ_L 的关联（极强）：声子谱是 BTE 热导的第一性输入；γ 决定非谐散射强度；θ_D 决定高温区适用性。

### 3.5 输运（★★ 至 ★★★）

- **电子输运：电导 σ、Seebeck S、功率因子、电子热导 κ_el、ZT**：半经典 Boltzmann（BoltzTraP 类）常规可得 [1]。注意电子热导不能用常数 Lorenz 数粗暴估计（高 Seebeck/半导体时失效）[10]。
- **声子群速度 v_g**：由声子色散导数得到。
- **κ_L 的第一性基准**：DFT+Boltzmann 无参数算 κL，Si/Ge 室温与实验 <5% 吻合 [2]——这是"DFT 能算κ_L"最硬的证据，也是你造库时对标的基准点。
- **三/四阶力常数 → 声子散射率/寿命 → 晶格热导 κ_L**：谐+三阶力常数 + BTE 求解，是 κ_L 真值的黄金标准 [11, 12]。MLIP 可加速 [13, 14]。
- **载流子迁移率**：需形变势+散射近似，★★。
- 与 κ_L 的关联（核心）：κ_L 本身就是这一节的最高阶结果。

## 四、与晶格热导 κ_L 的 Overlap：DFT 可算 ∧ 与 κ_L 相关

晶格热导的三条公式链（动理论 κ=⅓Cv·v·l；Slack 型；BTE）决定了哪些量"既 DFT 可算、又决定 κ_L"。overlap 交集如下，按 κ_L 公式的输入链标注：

### 4.1 一阶决定量（直接作为 κ_L 公式的输入，DFT 全部可算）

| DFT 可算量 | 作用 | 可行度 |
|---|---|---|
| 体/剪切模量 B, G | 声速/德拜温度输入；符号回归公式特征 | ★★★ |
| 声速 v_s | 动理论公式中的 v | ★★★ |
| 德拜温度 θ_D, 声学德拜温度 θ_ac | Slack/Wang/你们公式的输入 | ★★★ |
| Grüneisen 参数 γ | 非谐项（e^-γ / 1/γ²）核心输入 | ★★★ |
| 平均原子质量 M̄、原胞体积 V、原子数 N | 公式结构常数 | ★★★ |
| 热容 Cv（声子） | 动理论 C | ★★★ |
| 声子色散/群速度/谱 | BTE 第一性热导的直接输入 | ★★★ |

### 4.2 二阶量（在多体散射之上，DFT 加技术可得）

- **三阶力常数（非谐）**：BTE 三声子散射的必要输入，MLIP/有限位移可加速 [13, 14]（★★）
- 四声子/高阶散射：强非谐材料必需 [15]（★）
- **κ_L 真值本身**：谐+三阶力量 → BTE 求解 [11, 12]（★★）

### 4.3 Overlap 结论（用户要的那个交集）

**DFT 可算 ∧ 与 κ_L 直接相关**的物理量交集 = { B, G, ρ, V, N, γ, θ_D, θ_ac, Cv, α, v_s, 声子频率, 三阶力常数 }。其中前 10 项（B…α）正是你 AFLOW 数据集里已有、但来自 Slack/AGL [7] 模型的字段——**用你自己的 MLIP-DFT 工具重算这些量，即可得到不与 SLACK 绑定、独立于 AGL [7] 的第一性特征集**；而 κ_L 本身应改用 BTE 级真值 [11, 12]，彻底摆脱 Slack。

## 五、对造真值数据集的直接启示

1. **先用 MLIP-DFT 批量重算 B, G, γ, θ_D, θ_ac, Cv, α**（AFLOW 里这些是 Slack/AGL [7] 输出，你重算即得独立真值特征集）[7, 16]。
2. **κ_L 入库值用 BTE 级**（谐+三阶+BTE 或 MLP-MD 交叉校验），不再用 Slack [11, 14]。基准对照：各方法在 Si/Ge 上应与实验结果 <5% 内 [2]。
3. **弹性与声子用标准泛函 + 统一收敛**（PBE/GGA；DFPT 注意收敛与虚频陷阱）[5, 4]。造库前先按 Phonon Olympics 的 best-practice 指南标准化超胞/位移/截断协议 [3]。
4. 与你们已有符号回归公式衔接：新特征集可做训练/验证，旧公式做初筛 [8]。

## 六、结论

- **RQ1**：DFT 能算结构、电子、力学、声子热力学、输运五大类物性，主流量（模量/声速/德拜/γ/声子/热电）成熟可算 [6, 4, 5, 1]。
- **RQ2**：与 κ_L 相关的 DFT 可算交集 = {B, G, ρ, V, N, γ, θ_D, θ_ac, Cv, α, v_s, 声子频率, 三阶力常数, κ_L(BTE)} [11, 12]——这些正是你们 MLIP-DFT 工具能产出的第一性特征集，可支撑造替代 SLACK 的真值数据集。

## 参考文献

[1] Ullah Z, Khan R, Khan MA, Al Otaibi S, Althubeiti K, Abdullaev S, “High-temperature thermoelectric performance of spinel MgGa2O4 through a first-principles and Boltzmann transport study,” Computational Materials Science, 2025.
[2] Broido DA, Malorny M, Birner G, Mingo N, Stewart DA, “Intrinsic lattice thermal conductivity of semiconductors from first principles,” Applied Physics Letters, 2007.
[3] McGaughey AJH, Lindsay L, Bao H, et al., “Phonon Olympics: Phonon property and lattice thermal conductivity benchmarking from open-source packages,” Journal of Applied Physics, 2025.
[4] Shang S-L, Saengdeejing A, Mei Z-G, Kim DE, Zhang H, Ganeshan S, Wang Y, Liu Z-K, “First-principles calculations of pure elements: Equations of state and elastic stiffness constants,” Computational Materials Science, 2010.
[5] Petretto G, Gonze X, Hautier G, Rignanese G-M, “Convergence and pitfalls of density functional perturbation theory phonons calculations from a high-throughput perspective,” Computational Materials Science, 2018.
[6] Zhao J, Winey JM, Gupta YM, “First-principles calculations of second- and third-order elastic constants for single crystals of arbitrary symmetry,” Physical Review B, 2007.
[7] Toher C, Plata JJ, Levy O, de Jong M, Asta M, Nardelli MB, Curtarolo S, “High-throughput computational screening of thermal conductivity, Debye temperature, and Grüneisen parameter using a quasiharmonic Debye model,” Physical Review B, 2014.
[8] Gan CK, Koh EK, “A size-consistent Grüneisen-quasiharmonic approach for lattice thermal conductivity,” Europhysics Letters, 2022.
[9] Niranjan MK, Kumar V, Karthikeyan R, “Gruneisen parameter and thermal expansion coefficients of NiSi2 from first-principles,” Journal of Physics D: Applied Physics, 2014.
[10] Chen M, Podloucky R, “Electronic thermal conductivity as derived by density functional theory,” Physical Review B, 2013.
[11] McGaughey AJH, Jain A, Kim H-Y, Fu B, “Phonon properties and thermal conductivity from first principles, lattice dynamics, and the Boltzmann transport equation,” Journal of Applied Physics, 2019.
[12] Lindsay L, “First Principles Peierls-Boltzmann Phonon Thermal Transport: A Topical Review,” Nanoscale and Microscale Thermophysical Engineering, 2016.
[13] Srivastava Y, Jain A, “Accelerating Phonon Thermal Conductivity Prediction by an Order of Magnitude Through Machine Learning-Assisted Extraction of Anharmonic Force Constants,” arXiv, 2024.
[14] Ouyang Y, Yu C, He J, Jiang P, Ren W, Chen J, “Accurate description of high-order phonon anharmonicity and lattice thermal conductivity from molecular dynamics simulations with machine learning potential,” Physical Review B, 2022.
[15] Jain A, Srivastava Y, Gokhale AG, Virakante N, Kagdada HL, “Higher-order thermal transport theory for phonon thermal transport in semiconductors using lattice dynamics calculations and the Boltzmann transport equation,” arXiv, 2025.
[16] Lee H, Hegde VI, Wolverton C, Xia Y, “Accelerating high-throughput phonon calculations via machine learning universal potentials,” Materials Today Physics, 2025.
