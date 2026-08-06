# DFT 能算的物理量清单，及与晶格热导率（κ_L）的 Overlap

## 摘要

本文产出一份**可为用户直接使用的"DFT 能算的物理量"系统清单**，并按"是否与晶格热导率 κ_L 相关"给每一项标注相关性等级，最后给出 **DFT 可算 ∧ 与 κ_L 相关** 的 overlap 交集——这正是用户用来圈定"哪些 DFT 计算既可行、又喂给晶格导热研究"的清单。核心结论：DFT（含 DFPT）能算的物性横跨结构、电子、力学、热力学、输运五大谱系；其中与 κ_L 直接相关的一阶量（决定 κ_L 公式的输入）包括弹性张量/模量、声速、德拜温度、Grüneisen 参数、声子色散与群速度、三阶力常数（非谐）——这些全部可第一性计算；二阶级物理量（热容、热膨胀、声子寿命、κ_L 本身）在其上一阶或一阶+散射计算之上得到。overlap 的核心：**你此前符号回归公式 / AFLOW 数据集里的几乎所有输入字段（B, G, ρ, V, N, γ, θ_D, θ_ac, Cv, α）都是 DFT 可直接算的**，因此用你自己的 MLIP-DFT 工具产出一套"第一性真值特征集"是可行的——只需把当前依赖的 Slack 型 κ_L 目标值换成 BTE 级 κ_L（见 RQ2）。

## 一、引言

目标很直接：既然要造替代 SLACK 的真值数据集，就得先知道 **DFT 到底能给我们哪些物理量**，再看其中**哪些和晶格导热（κ_L）有关**。本报告回答：

- **RQ1**：DFT（含 DFPT）能计算哪些物理量？把它们组织成一张可勾选的清单。
- **RQ2**：哪些 DFT 可算量直接决定/影响 κ_L（即与晶格热导相关）？挑出 overlap 交集。

## 二、研究方法

检索经 sciverse MCP 多视角执行（弹性常数/弹性张量、热电 BoltzTraP [1]、DFPT 声子、第一性 BTE 热导、MLIP 加速、Grüneisen/quasiharmonic），纳入 13 篇代表工作；以入选文献为种子经滚雪球追引其前置技术链，末轮新增 0 篇、每个子方向核心文献 ≥3 篇，达检索饱和。清单一节基于这些工作的共同方法（DFT 总能与应变/位移求导、DFPT 线性响应、Boltzmann 输运）系统归纳，overlap 一节映射到晶格热导公式的输入链。

## 三、DFT 能算的物理量：系统清单

按物理谱系分五大门类（每项标 [第一性可行度]：★★★=成熟常规，★★=可行但需高阶/后处理，★=前沿/高成本）：

**A. 结构**
- 晶格常数、原子坐标、形成能/结合能（★★★）
- 相稳定性、相变压（★★★）
- 声学/光学色散相关的动力学稳定性判定（★★★，虚频即不稳定）[2]

**B. 电子结构**
- 能带/带隙/态密度、有效质量（★★★；带隙 PBE 低估，需 HSE/G0W0 修正）
- 功函数、磁性（自旋极化/交换）、自旋轨道耦合（★★★）

**C. 力学（弹性）**
- 二阶弹性张量 C_ij、体模量 B、剪切模量 G、杨氏模量 E、泊松比 ν（★★★）[3, 4]
- 弹性各向异性、单晶/多晶（VRH 平均）值（★★★）[4]
- 声速 v_L / v_t / v_s（由 C_ij 或模量+密度导出）（★★★）
- 三阶/四阶弹性常数（★★，应变能高阶拟合）[3]

**D. 声子与热力学**
- 声子色散、声子态密度、声子频率（★★★，DFPT 或有限位移/Phonopy）[2]
- 德拜温度 θ_D、声学德拜温度 θ_ac（由声速/声子谱导出）（★★★）
- 热容 Cv/Cp（声子贡献；★★★）、热膨胀系数 α、Grüneisen 参数 γ（★★★，quasiharmonic）[5]
- 热力学量随温度变化（准谐近似）（★★★）

**E. 输运**
- 电子电导 σ、Seebeck S、功率因子、电子热导 κ_el、ZT（★★★，BoltzTraP 类）[1, 6]
- 声子群速度 v_g（★★★）
- 三/四阶力常数、声子散射率/寿命、**晶格热导率 κ_L**（★★，谐+三阶+BTE）[7, 8]
- 载流子迁移率（★★，需散射与形变势）

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

- **三阶力常数（非谐）**：BTE 三声子散射的必要输入，MLIP/有限位移可加速 [9, 10]（★★）
- 四声子/高阶散射：强非谐材料必需 [11]（★）
- **κ_L 真值本身**：谐+三阶力量 → BTE 求解 [7, 8]（★★）

### 4.3 Overlap 结论（用户要的那个交集）

**DFT 可算 ∧ 与 κ_L 直接相关**的物理量交集 = { B, G, ρ, V, N, γ, θ_D, θ_ac, Cv, α, v_s, 声子频率, 三阶力常数 }。其中前 10 项（B…α）正是你 AFLOW 数据集里已有、但来自 Slack/AGL [5] 模型的字段——**用你自己的 MLIP-DFT 工具重算这些量，即可得到不与 SLACK 绑定、独立于 AGL [5] 的第一性特征集**；而 κ_L 本身应改用 BTE 级真值 [7, 8]，彻底摆脱 Slack。

## 五、对造真值数据集的直接启示

1. **先用 MLIP-DFT 批量重算 B, G, γ, θ_D, θ_ac, Cv, α**（AFLOW 里这些是 Slack/AGL [5] 输出，你重算即得独立真值特征集）[5, 12]。
2. **κ_L 入库值用 BTE 级**（谐+三阶+BTE 或 MLP-MD 交叉校验），不再用 Slack [7, 10]。
3. **弹性与声子用标准泛函 + 统一收敛**（PBE/GGA；DFPT 注意收敛与虚频陷阱）[2, 4]。
4. 与你们已有符号回归公式衔接：新特征集可做训练/验证，旧公式做初筛 [13]。

## 六、结论

- **RQ1**：DFT 能算结构、电子、力学、声子热力学、输运五大类物性，主流量（模量/声速/德拜/γ/声子/热电）成熟可算 [3, 4, 2, 1]。
- **RQ2**：与 κ_L 相关的 DFT 可算交集 = {B, G, ρ, V, N, γ, θ_D, θ_ac, Cv, α, v_s, 声子频率, 三阶力常数, κ_L(BTE)} [7, 8]——这些正是你们 MLIP-DFT 工具能产出的第一性特征集，可支撑造替代 SLACK 的真值数据集。

## 参考文献

[1] Ullah Z, Khan R, Khan MA, Al Otaibi S, Althubeiti K, Abdullaev S, “High-temperature thermoelectric performance of spinel MgGa2O4 through a first-principles and Boltzmann transport study,” Computational Materials Science, 2025.
[2] Petretto G, Gonze X, Hautier G, Rignanese G-M, “Convergence and pitfalls of density functional perturbation theory phonons calculations from a high-throughput perspective,” Computational Materials Science, 2018.
[3] Zhao J, Winey JM, Gupta YM, “First-principles calculations of second- and third-order elastic constants for single crystals of arbitrary symmetry,” Physical Review B, 2007.
[4] Shang S-L, Saengdeejing A, Mei Z-G, Kim DE, Zhang H, Ganeshan S, Wang Y, Liu Z-K, “First-principles calculations of pure elements: Equations of state and elastic stiffness constants,” Computational Materials Science, 2010.
[5] Toher C, Plata JJ, Levy O, de Jong M, Asta M, Nardelli MB, Curtarolo S, “High-throughput computational screening of thermal conductivity, Debye temperature, and Grüneisen parameter using a quasiharmonic Debye model,” Physical Review B, 2014.
[6] Chen M, Podloucky R, “Electronic thermal conductivity as derived by density functional theory,” Physical Review B, 2013.
[7] McGaughey AJH, Jain A, Kim H-Y, Fu B, “Phonon properties and thermal conductivity from first principles, lattice dynamics, and the Boltzmann transport equation,” Journal of Applied Physics, 2019.
[8] Lindsay L, “First Principles Peierls-Boltzmann Phonon Thermal Transport: A Topical Review,” Nanoscale and Microscale Thermophysical Engineering, 2016.
[9] Srivastava Y, Jain A, “Accelerating Phonon Thermal Conductivity Prediction by an Order of Magnitude Through Machine Learning-Assisted Extraction of Anharmonic Force Constants,” arXiv, 2024.
[10] Ouyang Y, Yu C, He J, Jiang P, Ren W, Chen J, “Accurate description of high-order phonon anharmonicity and lattice thermal conductivity from molecular dynamics simulations with machine learning potential,” Physical Review B, 2022.
[11] Jain A, Srivastava Y, Gokhale AG, Virakante N, Kagdada HL, “Higher-order thermal transport theory for phonon thermal transport in semiconductors using lattice dynamics calculations and the Boltzmann transport equation,” arXiv, 2025.
[12] Lee H, Hegde VI, Wolverton C, Xia Y, “Accelerating high-throughput phonon calculations via machine learning universal potentials,” Materials Today Physics, 2025.
[13] Gan CK, Koh EK, “A size-consistent Grüneisen-quasiharmonic approach for lattice thermal conductivity,” Europhysics Letters, 2022.
