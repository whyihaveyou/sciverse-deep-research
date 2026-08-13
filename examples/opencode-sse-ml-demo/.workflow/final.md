# 机器学习辅助固态电解质筛选与界面设计：方法路线、证据成熟度与开放瓶颈

## 摘要

全固态电池的安全性优势建立在固态电解质（SSE）之上，但理性设计仍受制于庞大的成分-结构化学空间与脆弱的界面稳定性。本文综述机器学习（ML）如何加速 SSE 的筛选，并逐步渗入电解质-电极界面/中间相（SEI）的设计。围绕三条技术路线——描述符与组成驱动的监督学习代理模型、机器学习势函数结合分子动力学（MLIP-MD）、生成式与主动搜索（贝叶斯优化/主动学习/深度生成）——梳理各自的能力边界；随后转向界面与中间相的 ML 建模。证据显示：体相材料的筛选已趋成熟，但呈现出"可定性、难定量"的一致性规律——跨数据集的共识是分类/排序预测比绝对电导率的数值回归更可靠 [1, 2]；从计算筛选到实验验证之间存在明显的"验证赤字"，多数候选止步于 DFT/MD 验证 [3, 4]；通用机器学习势的预测误差随化学体系漂移，必须结合系统特定数据细调 [5, 6, 7]。相比之下，ML 在界面与 SEI 设计中的应用仍停留在早期，证据密度显著低于体相筛选，这是当前最被忽视的瓶颈 [8, 9]。

## 关键引用

- [10] 层次筛选 2 万余种含 Li 材料的 SSE 预测管线
- [5] 通用 MLIP 对照 7Li NMR 评估锂迁移预测可靠性
- [6] 机器学习分子动力学揭示超胞尺寸对电导率预测的系统误差
- [1] 大规模电导率数据集上 ML 模型的定量局限与定性价值
- [8] ML 在 SEI 建模中的角色前瞻综述
- [3] 组成式 ML 指导 argyrodite 电解质发现并经实验验证

## 核心要点

- SSE 发现的主要范式差异不在模型结构，而在特征设计：组成/元素描述符、几何结构描述符、以及机器学习势引发的"模拟即观测"路线。
- 数据集稀缺与不均匀是贯穿所有路线的共同约束：成熟数据集规模在数百条量级，驱动模型向"定性/排序"目标收敛。
- MLIP-MD 以接近第一性原理精度换取 2-3 个数量级的效率，但其可迁移性在锂扩散预测上系统相关，直接外推不可靠。
- 生成式与主动搜索把优化目标从"预测某点性质"升级为"高效探明整个化学空间"，但验证闭环多停留在计算层。
- 界面/SEI 的 ML 设计远滞后于体相筛选，且界面问题的多物理耦合（化学、力学、电荷输运）使建模难度陡增，构成下一个主要战场。

## 一、引言

尽管全固态锂电池在安全性与能量密度上被寄予厚望，其工程化仍卡在固态电解质这一关键环节：既要本征高离子电导、宽电化学窗口，又要在电极界面上保持化学与力学稳定 [11, 12]。传统试错法在这类多维约束下效率极低，而 SSE 的成分-结构空间又极其庞大，推动研究者转向数据驱动的机器学习。

本文的目标不是罗列"哪些 SSE 被算出来了"，而是回答三个问题：
- RQ1：ML 在 SSE 体相筛选中形成了哪几条主流技术路线，各自的能力与适用边界是什么？
- RQ2：ML 如何介入电解质-电极界面及中间相（SEI）的设计与稳定性评估，其成熟度如何？
- RQ3：从体相筛选走向界面稳定的过程中，制约证据成熟度的开放瓶颈是什么？

与既有综述着重枚举算法与体系不同 [12, 13, 14]，本文以"ML 介入机制"为分类轴，强调证据强度和验证闭环的差异——这正是现有综述较少系统处理的角度。

## 二、研究方法

本文以 sciverse 学术库为主源，围绕"ML 筛选 SSE"与"ML 界面/SEI 设计"两大关键词族展开多视角检索，覆盖主流方法、材料类别专项、机器学习势函数、生成与主动搜索、以及界面与批判/局限等视角。纳入标准为：以 ML 为方法主体、对象为固态电解质本体或其界面/中间相的原创研究与综述。共滚雪球 1 轮、末轮新增 0 篇，达检索饱和；各子方向文献均不少于 3 篇。所选文献均经 sciverse 检索返回确认存在性。分类框架以 ML 介入机制为轴（见表），它比"按材料类别"更利于定位方法共性，也比"按算法"更能凸显从"筛材料"到"造材料"再到"护界面"的迁移逻辑。

表：ML 介入 SSE 的四种机制（分类框架）

| 分支 | ML 介入机制 | 典型目标 | 典型数据/手段 |
|---|---|---|---|
| 1 | 描述符/组成监督学习代理 | 电导率等性质预测、候选排序 | 实验/文献集成的数百条小数据集 |
| 2 | 机器学习势函数 + 分子动力学 | 原子层面扩散机理、电导率计算 | 第一性原理训练集 + MD 模拟 |
| 3 | 生成式与主动搜索 | 化学空间扩展、多性质优化 | 生成模型、贝叶斯优化、主动学习 |
| 4 | 界面/SEI 建模 | 界面稳定性、中间相结构与导锂机制 | ML 势、代理模拟器、界面 DFT |

## 三、分类框架

四个分支构成"预测-模拟-搜索-界面"的闭环，但各自的证据成熟度并不均衡：分支 1 与 2 文献最密集，分支 3 处于工程化初期，分支 4 明显单薄。这一不均衡本身即关键 finding：**SSE 研究的计算重心仍停留在"把电解质本身算明白"，而界面——真实电池失效的主要来源——恰恰是最少被 ML 触及的环节**。

## 四、描述符与组成驱动的监督学习代理（分支 1）

这一路线把 SSE 性质预测当作有监督回归/分类问题：输入为元素组成、化学描述符或结构参数，输出为目标性质（以室温离子电导率居主导）。它是 SSE 发现文献中最成熟的范式 [12, 13]，也是四种机制中操作门槛最低、被采用最广的一支。

层次筛选框架是这一路线的典型形态。Chen 等从约 2 万种含锂材料中，先凭判据预筛、再用 468 条文献集成样本训练的 ML 模型分类与回归，对候选做电化学窗口评估并配以 AIMD 验证，最终锁定 `$Li_3BiS_3$`、`$Li_5BiS_4$`、`$Li_{10}ZnP_4S_{16}$` 等候选 [10]。Kang 等以类似的高通量 + 代理模型流程从 19480 种含锂材料中筛出三类此前未研究过的超离子导体，训练集中混入 NASICON、argyrodite、halide 等多个体系 [15]。这类工作共享同一叙事：把文献中的电导率数据汇集为"小但异构"的训练集，用集成学习（随机森林、梯度提升、stacking）获得稳健预测，再交由第一性原理与分子动力学复核 [10, 15, 16]。

但恰恰在这个最成熟的路线里，可以观察到最诚实的能力边界披露。Kim 等构造了迄今较大的 Li/Na 电导率数据集（文献+LLM 辅助整理），报告最优随机森林在 Li 集上 $R^2 = 0.569$、MAE = 0.911（log 尺度），却在区分好导体（$\geq 10^{-4}\ \mathrm{S/cm}$）与差导体上达到最高 F1 = 0.83-0.92 [1]。与此平行，Kim 等在结构标注数据集（n = 499）上报告梯度提升树 MAE = 0.543（log S/cm），并指出纯组成模型会忽略结构、而图神经网络又受数据稀缺与无序 CIF 困扰 [2]。把两篇独立来源并置，收敛出一个稳健结论：**这类模型定量预测绝对电导率仍不牢靠，但其分类/排序/筛分能力是可靠的**，与早期"小数据只能定性"的判断 [11] 一脉相承。

特征选择与可解释性进一步揭示了筛选的"物理判据"。反钙钛矿电解质上，可解释 ML 与 SHAP 分析提出电负性、密度、离子半径为 A 位最关键的导电特征 [17]；对 NASICON 型 `$LiTi_2(PO_4)_3$` 的掺杂预测同样依赖元素特征与结构参数的配比 [18]。这些研究指向一条方法论共识：**描述符的意义不在于"更大"，而在于"可归因"——可解释特征是连接数据驱动模型与结构-性能物理的桥梁**。

跨体系来看，这一路线已覆盖石榴石（garnet，73 元素替换生成的 5329 种候选 [19]）、卤化物（多性质联合预测并经 DFT 验证 [20]）、反钙钛矿 [17]、NASICON [18] 与 argyrodite（仅靠元素组成的 E2I 框架 [3]）。但覆盖广并不等于验证深：除少数工作真正合成了 ML 筛选出的材料并测到高性能——如 E2I 指导下合成 `$Li_{6.7}Ge_{0.595}Si_{0.105}P_{0.3}S_5I$`（离子电导率 7.2 $\times$ 10⁻³ S/cm）[3]、双掺杂 LLZO 作为聚合物复合电解质填料经实验验证 [4]——多数候选止步于计算验证。这种"筛选多、落地少"的不对称，是分支 1 最值得警惕的局限。

## 五、机器学习势函数与分子动力学（分支 2）

机器学习势函数（MLIP）通过拟合第一性原理数据，在接近 DFT 精度的前提下将分子动力学（MD）时间尺度提升 2-3 个数量级，从而既能评估离子电导率，又能直接揭示原子层面的扩散机理 [14]。它把范式从"用描述符预测性质"切换为"用模拟直接观测输运"。

Hajibabaei 等用 on-the-fly 机器学习势（稀疏高斯过程回归）扫描数百种三元锂电导率，并演示将单一体系专家势组合成 Li-P-S、Li-Sb-S 乃至 Li-Ge-P-S 的"通用势"，指向分层建模的可迁移思路 [21]。此后通用机器学习势框架（CHGNet、M3GNet、MACE、ORB 等）成为热点，被用于高温无序石榴石（CDHE）多步筛选 [22]、argyrodite 阴离子局域效应机理 [23] 等。

但通用势的"即插即用"承诺正受到更严格的对标检验。Gurwell 等系统评测 18 个通用势（四个家族）对 12 种含锂化合物的预测，对照实验 7Li NMR 扩散数据与 DFT，得出两个关键结论：性能强烈依赖模型架构与化学体系；锂扩散预测的可靠性是系统相关的，通用势对复杂材料的迁移性仍有限 [5]。这一以实验 NMR 数据为锚的独立盲评，是对分支 2 最有力的一记提醒。更细的误差来源被 Zhang 等在 `$Li_3YCl_6$` 上定位：AIMD 常用的小超胞会显著高估室温电导率，必须用足够大的超胞做机器学习 MD 才能捕获 ~420 K 附近的超离子转变——即"尺寸效应"可造成系统性偏差 [6]。

应对之道正在收敛为"通用势 + 系统特定细调/主动学习"两段式。Shantsila 等提出 STING：以委员会不确定性估计迭代挑选结构、用最少量的 DFT 数据把基础通用势（foundation MLIP）细调为体系专用势，在锂硫代磷酸盐上显著优于通用势 [7]。这一从"通用势"转向"系统专用势"的思路，与 on-the-fly 分层建模的可迁移理念一致 [21]，共同指向：**通用势的价值是"初始化 + 有效先验"，而非"免训练终态"**。

综合分支 1 与 2，一个跨路线的判断浮现：无论走描述符回归还是走模拟势，可靠性的瓶颈最终都回到**训练数据是否覆盖了目标化学子空间**。当数据稀缺时，模型退化为朴素的组合学先验；当 MLIP 未经目标体系数据细调时，其扩散预测可能既准又错得系统化。这一共性或许才是 SSE 机器学习研究的真正第一性约束。

## 六、生成式与主动搜索策略（分支 3）

如果说分支 1、2 回答"给定候选集合如何评估"，分支 3 回答"如何生成或导航候选集合"。它包括深度生成模型（基于 GAN 的晶体结构生成）、贝叶斯优化（BO）与主动学习（AL）三类手段。

深度生成模型把化学空间扩展为可采样的分布。Zhao 等提出的 CubicGAN 在 37 万余种三元立方材料上训练，能重新发现已知立方结构并产出 506 个经声子验证的新原型 [24]。虽然这项工作面向一般晶体发现而非 SSE 专精，但它展示了"生成-验证"闭环在晶体领域的可行性，为 SSE 的结构生成提供了方法参照。在 SSE 专情领域，反钙钛矿上的离子替换将样本从 168 条扩到 15 万量级后重新分析导电机制 [17]，表明"数据扩增"与"生成"之间的界线正在模糊。

贝叶斯优化在 SSE 中则承担"逼近式导航"角色。Tawfik 等以最大化锂扩散为目标做 BO，结合 AIMD 评估势垒、验证电子绝缘性与锂金属界面稳定性，最终圈出 `$Li_3YBr_6$` 这一兼具低势垒、高带隙与界面稳定的候选 [25]。主动学习在领域内的体现包括 garnet 上通过不确定性采样降低代理模型误差 [19]，以及冷烧结 LATP 工艺参数的多目标 BO 优化（CSP 实现 1.94 $\times$ 10⁻⁴ S/cm）[26]。值得注意，把主动学习用于液态电解质配方（对称电池寿命提升三倍）的近期工作 [27]，证明了同样的方法骨架可平滑迁移到相邻的电解质设计问题。

分支 3 的共性特征是**优化目标从"性质绝对值"升级为"信息效率"**：它不再只回答"哪个好"，而是回答"下一步该测/该算哪个才能最快收敛"。这使它天然适合数据稀缺场景。但它的验证闭环目前大多仍停留在计算层面——真正把生成/搜索出的候选送到实验合成台的工作仍稀有 [3, 25]，这是分支 3 与分支 1 共同面对的"实验验证赤字"。

## 七、界面与中间相（SEI）的 ML 建模与设计（分支 4）

这是本文与既有 SSE-ML 综述最大的分歧点：大多数综述把界面当作背景问题一笔带过，而其实现的界面/中间相恰恰是真实全固态电池阻抗、库仑效率与循环寿命的支配因素 [28]。界面面临的不是单一性质预测，而是化学（分解反应）、力学（接触与枝晶）、电化学（电荷输运）的多物理强耦合 [28]。这决定了 ML 在界面上的介入路径与体相筛选显著不同，也更困难。

ML 在 SEI 建模中的角色，Diddens 等在综述中做了前瞻性界定：数据驱动的代理模拟器与深度生成模型，能与物理/物理信息方法协同，为"带目标性质逆向设计中间相"提供新通道 [8]。这是对"ML 用于界面"方法论位置的清晰定位——但发表于 2022 年，其后本领域的进展节奏明显慢于体相筛选。少数具体工作正在填补空白：用机器学习加速模拟揭示 Si/`$Li_6PS_5Cl$` 界面上依赖于锂化态的 SEI 成核路径 [9]；ML 引导的 SEI 电导率研究评估非晶锂氟磷酸盐类中间相 [29]；以及用 ML 力场对候选 SEI 结构按预测能量排序 [30]。

把分支 4 与分支 1-3 对照，一个尖锐的规律浮现：**ML 在 SSE 中的应用密度，与目标环节的商业紧迫性成反比**。体相筛选关乎"材料有没有"，文献多、方法熟；界面/SEI 关乎"电池能不能用"，恰恰是电化学与失效的核心，却最少被 ML 系统触及。这一反差既是当前研究的空白，也是机会窗口。

## 综合讨论

跨四个分支，可以提炼三条贯穿性规律。

**其一，小数据是 SSE-ML 的第一性约束，并把结论推向"定性/排序"而非"定量回归"。** 无论是描述符代理 [1, 2]、还是势函数训练 [5, 7]、抑或生成模型的数据基础 [24]，数据集规模都在数百条量级，模型必然倾向学习组合学先验。跨来源的证据收敛于"分类/排序可靠、绝对值存疑"——这一判断需要如实写进任何 SSE-ML 结论的限定里。

**其二，"验证赤字"是横跨所有筛选分支的通用短板。** 计算筛选文献蔚为大观，但真正进入实验合成与电池级验证的只占极少数 [3, 4, 25]。当 ML 的产出仅是"计算上更优的假想材料"时，其工程价值尚未兑现。这提示该领域亟需从"预测准确率"转向"闭环验证率"的评价标准。

**其三，通用性与系统特定性之间存在张力。** 通用 MLIP 虽便捷，但预测误差随体系漂移 [5]；小超胞/通用描述符均可引入系统偏差 [6, 2]。收敛方案都是"通用初始化 + 系统特定细调/主动学习" [7, 21]。这条经验从计算势延伸到整个 SSE-ML 方法栈，具有普遍方法学价值。

界面分支的单薄与体相筛选的密集形成最刺眼的对比。它不是"难"，而是"更复杂"——需要把化学、力学、电输运纳入同一建模框架。Diddens 前瞻所指的"逆向设计期望性质的目标中间相" [8] 尚远未兑现，这为后续研究划出了最富价值的方向。

## 开放问题与未来方向

- **自动化闭环**：把"筛选-合成-表征"用机器人/主动学习串成闭环，把实验验证从偶发补齐为常态，是化解"验证赤字"的最直接途径 [3, 4]。
- **统一电导率基准数据集**：跨来源、异构、数百条规模的数据集限制了可比性；建设带标注的共享基准，是让"排序可靠"升级为"定量可靠"的前提 [1, 2]。
- **界面多物理建模**：把 ML 势扩展到含分解、力学接触、电荷转移的界面体系，方能支撑 SEI 的逆向设计 [8, 9]。
- **不确定性的常规化**：主动学习与委员会不确定性已证明可降低预测风险 [7, 19]，但在多数 SSE-ML 工作中，不确定性仍未成为默认输出。

## 结论

对应引言三个问题：ML 在 SSE 体相筛选中已形成"描述符代理预测、MLIP-MD 模拟、生成与主动搜索"三条互补而成熟度不等的路线（RQ1）。这些路线的共性是把规模为数百条的稀缺数据转化为可靠的"分类/排序信号"，并借可解释特征与系统特定主动学习缓解数据压力；但定量预测与实验落地仍是被一致披露的短板。ML 在界面与 SEI 设计的介入则明显滞后：仅见成核路径模拟、中间相导锂评估与 SEI 结构排序等早期尝试，其证据密度与体相筛选相差一整个数量级（RQ2）。从筛选走向界面，瓶颈不在算法而在数据与多物理建模的复杂度——界面既缺少像电导率那样可集中标注的标量目标，又缺少覆盖化学-力学-电输运耦合的模拟能力，这正是当前最值得投入的开放地带（RQ3）。

## 调研成本

本综述为阶段性小综述，检索范围聚焦 ML 筛选与界面设计两域，未展开跨语种与商业库（如 WoS/Scopus）检索；文献存在性经 sciverse 检索确认，题录字段（卷期页码/DOI）未逐篇走 Crossref 复核，综述模式按要求从检索来源抄录年份。所选分析以检索返回的标题/摘要为主，部分结论的量化细节未逐篇全文对读，需在引用具体数值时谨慎。

## 参考文献

[1] Younsoo Kim, “Prediction of ionic conductivity in solid-state electrolytes using machine learning,” Materials Today Communications, 2026.
[2] Haewon Kim, “Data-driven prediction of ionic conductivity in solid-state electrolytes with machine learning and large language models,” The Journal of Chemical Physics, 2026.
[3] Songjia Kong, “From Composition to Ionic Conductivity: Machine Learning-Guided Discovery and Experimental Validation of Argyrodite-Type Lithium-Ion Electrolytes,” Small, 2025.
[4] Ji-Hwan Kim, “Machine learning-driven discovery of innovative hybrid solid electrolytes for high-performance all-solid-state batteries,” Chemical Engineering Journal, 2025.
[5] Cameron A. Gurwell, “Experimental Validation of Universal Machine Learning Interatomic Potentials for Lithium-Ion Dynamics in Solid Electrolytes via 7Li NMR,” ChemRxiv, 2026.
[6] Yixi Zhang, “Size dependent lithium-ion conductivity of solid electrolytes in machine learning molecular dynamics simulations,” Artificial Intelligence Chemistry, 2024.
[7] Roman Shantsila, “STING, guided active learning for Machine Learned Interatomic Potentials examined on Lithium Thiophosphate solid state electrolytes,” ChemRxiv, 2026.
[8] Diddo Diddens, “Modeling the Solid Electrolyte Interphase: Machine Learning as a Game Changer?,” Advanced Materials Interfaces, 2022.
[9] Zhuoyuan Zheng, “Lithiation-dependent solid electrolyte interphase nucleation pathways in Si/Li6PS5Cl interfaces uncovered by machine learning-accelerated simulations,” Energy Storage Materials, 2025.
[10] Weijian Chen, “Accelerated discovery of novel inorganic solid-state electrolytes through machine learning-assisted hierarchical screening,” Journal of Alloys and Compounds, 2024.
[11] Xu Zhang, “Unsupervised machine learning accelerates solid electrolyte discovery,” Green Energy & Environment, 2019.
[12] Hongcan Liu, “Recent Advances in Screening Lithium Solid-State Electrolytes Through Machine Learning,” Frontiers in Energy Research, 2021.
[13] Shengyi Hu, “Machine-Learning Approaches for the Discovery of Electrolyte Materials for Solid-State Lithium Batteries,” Batteries, 2023.
[14] Gunwook Nam, “Machine learning interatomic potentials for lithium battery electrolyte design,” Bulletin of the Korean Chemical Society, 2026.
[15] Seungpyo Kang, “Discovery of Superionic Solid-State Electrolyte for Li-Ion Batteries via Machine Learning,” The Journal of Physical Chemistry C, 2023.
[16] Bijan Kumar Paul, “LiCondAI: A Machine Learning Model for Predicting Lithium-Ion Conductivity in Solid Electrolytes,” Industrial & Engineering Chemistry Research, 2025.
[17] Shang Xiang, “Ionic Conductivity Study of Antiperovskite Solid-State Electrolytes Based on Interpretable Machine Learning,” ACS Applied Energy Materials, 2025.
[18] Xiaozhen Chen, “Machine learning-assisted prediction of ionic conductivity in doped LiTi2(PO4)3 solid electrolytes,” Journal of Power Sources, 2025.
[19] Jiwon Sun, “Accelerated Discovery of Novel Garnet-Type Solid-State Electrolyte Candidates via Machine Learning,” ACS Applied Materials & Interfaces, 2023.
[20] Li Yan Anthony Choong, “Discovery of Effective Halide Solid Electrolytes for Solid-State Rechargeable Batteries via Machine Learning and DFT Calculations,” ACS Applied Energy Materials, 2025.
[21] Amir Hajibabaei, “Universal Machine Learning Interatomic Potentials: Surveying Solid Electrolytes,” The Journal of Physical Chemistry Letters, 2021.
[22] Jiwon Sun, “Cation-Disordered High-Entropy Garnet Structures as Solid-State Electrolytes for All-Solid-State Batteries: Machine Learning-Driven Discovery,” ACS Applied Materials & Interfaces, 2025.
[23] Hyun-Jae Lee, “Lithium Localization by Anions in Argyrodite Solid Electrolytes from Machine-Learning-based Simulations,” Advanced Energy Materials, 2025.
[24] Yong Zhao, “High-Throughput Discovery of Novel Cubic Crystal Materials Using Deep Generative Neural Networks,” Advanced Science, 2021.
[25] Sherif Abdulkader Tawfik, “Accelerated Discovery of Solid-State Electrolytes Using Bayesian Optimization,” The Journal of Physical Chemistry C, 2025.
[26] Navin Rajapriya, “Bayesian Optimization of Cold Sintering Process for High-Conductivity LATP Solid-State Electrolytes,” ACS Applied Energy Materials, 2026.
[27] Xufeng Hong, “Deep active learning and knowledge transfer for rapid discovery of lithium metal battery electrolytes,” Nature Communications, 2026.
[28] Linan Jia, “Li–Solid Electrolyte Interfaces/Interphases in All-Solid-State Li Batteries,” Electrochemical Energy Reviews, 2024.
[29] Peichen Zhong, “Machine-Learning-Guided Insights into Solid-Electrolyte Interphase Conductivity: Are Amorphous Lithium Fluorophosphates,” ACS Energy Letters, 2025.
[30] James Stevenson, “Machine learning force field ranking of candidate solid electrolyte interphase structures in Li-ion batteries,” ChemRxiv, 2023.
