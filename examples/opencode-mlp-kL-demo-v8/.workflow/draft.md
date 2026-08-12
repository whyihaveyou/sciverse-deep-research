# 机器学习势函数预测晶格热导率：从"第一性原理替身"到"非谐性全阶求解"的范式演进

## 关键引用

- [@Mortazavi2020] Mortazavi, 2020, "Machine-learning interatomic potentials enable first-principles multiscale modeling of lattice thermal conductivity in graphene/borophene heterostructures"
- [@Ouyang2022] Ouyang, 2022, "Accurate description of high-order phonon anharmonicity and lattice thermal conductivity from molecular dynamics simulations with machine learning potential"
- [@Qian2019] Qian, 2019, "Thermal conductivity modeling using machine learning potentials: application to crystalline and amorphous silicon"
- [@YangQian2021] Yang & Qian, 2021, "Machine learning for predicting thermal transport properties of solids"
- [@Liu2021SnSe] Liu, 2021, "High-temperature phonon transport properties of SnSe from machine-learning interatomic potential"
- [@Arabha2021] Arabha, 2021, "Recent advances in lattice thermal conductivity calculation using machine-learning interatomic potentials"
- [@You2024] You, 2024, "Effects of four-phonon scattering and wave-like phonon tunneling effects on thermoelectric properties of Mg2GeSe4 using machine learning"

## 摘要

晶格热导率 $\kappa_L$ 来自对声子色散与全阶非谐性的精确描述，传统上由基于密度泛函理论（DFT）的声子玻尔兹曼输运方程（PBTE）或平衡分子动力学（EMD）承担，但二者分别受制于计算成本与该成本带来的收敛性风险。本综述以 sciverse 文献库为唯一信息源，围绕机器学习势函数（MLIP）在 $\kappa_L$ 预测中的方法体系、与 DFT 的精度—成本权衡、以及非谐性/长程/数据等瓶颈，滚雪球 5 轮至饱和后选取 21 篇文献进行系统综合。核心发现是：MLIP 已从"DFT 的近似替身"演进为"能够容纳全阶非谐性的求解引擎"——当三声子微扰近似失效（如 BAs 与强非谐材料）时，基于 MLIP 的分子动力学反而已达到与实验更吻合的结果；同时，MLIP 预测 $\kappa_L$ 的精度瓶颈正从拟合误差向曲率与训练数据质量转移，促使声子微调（PFT [@Koker2026]）与参数高效微调（Equitrain [@Grandel2026]）等新范式兴起。本文给出方法分类框架、逐维度对比表，并指出长程相互作用与层状材料建模仍是尚未闭合的空白。

## 核心要点

- **要点 1**：MLIP 预测 $\kappa_L$ 的成熟路径有两条——把 MLIP 当作精确三阶力常数提供者喂给 PBTE（[@Choi2022; @Podryabinkin2020]），或直接跑 EMD/NEMD 以天然容纳全阶非谐性（[@Ouyang2022; @Liu2021SnSe]）；两条路径的成本均较纯 DFT 降低多个数量级，但精度特征不同。
- **要点 2**：当材料存在强高阶非谐性时，PBTE（含四声子）的计算与实验偏差可能超过 EMD 路线；BAs 案例中 EMD 与实验吻合而三声子 PBTE 显著高估（[@Ouyang2022]），说明"更精确的势函数"不能自动弥补微扰框架的截断误差。
- **要点 3**：MLIP 对 $\kappa_L$ 的误差来源正在由"势函数拟合误差"转向"势能面曲率与力常数精度",声子微调（PFT, [@Koker2026]）与参数高效微调（Equitrain, [@Grandel2026]）通过监督二阶力常数显著提升声子与热性质预测，提示精调优于从头训练。
- **要点 4**：长程相互作用与层状/弱范德华材料仍是 MLIP 预测 $\kappa_L$ 的高风险区,其难点在于各向异性能量面与弱层间键（[@Tang2022hBN]）。
- **要点 5**：通向高吞吐筛选的捷径并非全部依赖 MLIP——基于描述符的两阶段可解释 ML（[@Hu2023]）与物理信息 CGCNN 框架 PINK（[@Liu2025PINK]）直接对晶格常数/模量等特征回归 $\kappa_L$，可与 MLIP 互补。

## 一、引言

### 为什么需要这篇综述

晶格热导率 $\kappa_L$ 是热管理材料与热电材料筛选的核心指标，其精确预测依赖对声子色散与全阶非谐性的刻画。十年前，第一性原理声子计算（DFT + PBTE）已成为计算 $\kappa_L$ 的常规手段 [@YangQian2021]，但对高吞吐筛选、含缺陷晶体、非晶与高温材料仍成本高昂，并面临微扰近似的根本局限。机器学习势函数把 DFT 级精度带到经典分子动力学的时间与尺寸尺度，被视作弥合两者差距的桥梁 [@YangQian2021]。已有综述（[@Arabha2021; @Liu2023mini]）多按"应用案例"组织，本文则提出一个以"求解路线 × 精度瓶颈"为双轴的分类框架，明确 MLIP 在 $\kappa_L$ 预测中的定位正从替身演变为全阶非谐性求解引擎。

### 研究问题

- RQ1: 面向 $\kappa_L$ 预测的 MLIP 方法体系如何组织？存在哪些可复用的求解路线与架构选择？
- RQ2: 与基于 DFT 的 PBTE 相比，MLIP 在精度与成本上的权衡在什么条件下成立、又在何处失效？
- RQ3: 当前制约 MLIP 普适到晶格热导率的瓶颈（长程相互作用、高阶非谐性、训练数据质量）分别处于什么状态、有哪些现存对策？

### 本文组织方式

第二节给出检索与纳入方法，第三节亮出双轴分类框架。第四至六节依序展开三个分支：求解路线、精度—成本权衡、瓶颈与对策。第七节跨分支综合讨论，第八节开列开放问题，第九节逐条回答引言中的 RQ。

## 二、研究方法

本文仅以 sciverse 文献库为信息源，通过其语义检索（`semantic_search`）进行多视角检索，并用结构化检索验证关键文献存在性（存在性判定：VERIFIED）。围绕"方法体系（RQ1）、精度—成本权衡（RQ2）、瓶颈与对策（RQ3）"三个视角，再叠加"高阶非谐性/四声子"与"批评/微调"两个补充视角，关键词族包括：machine learning potential / interatomic potential / lattice thermal conductivity / phonon Boltzmann transport equation / Green–Kubo / four-phonon / anharmonicity / neural network potential / moment tensor potential / neuroevolution potential / Gaussian approximation potential。

纳入标准：研究对象为晶格（声子）热导率、且方法上以机器学习势函数或机器学习回归为核心；综述类文章纳入作为覆盖面锚点。排除：仅关注界面热导、电子热导率或非声子热输运的工作。最终入选并纳入台账 21 篇，含 3 篇综述、多个代表性 MLIP 架构与多体系应用。滚雪球 5 轮，末轮新增 0 篇，达检索饱和；时效探针覆盖 2024–2026 年最新工作，无脱节。

## 三、分类框架

本文以"求解路线 × 精度瓶颈"为双轴组织证据，两条轴互斥且完善：

| 轴 | 分支 | 涵盖工作 | 空格（= gap） |
|---|---|---|---|
| 求解路线 | A. MLIP 喂 PBTE（谐/微扰） | [@Choi2022; @Podryabinkin2020; @Mortazavi2020; @Mortazavi2020efficient] | 四声子 PBTE + MLIP 的规模化（[@You2024] 刚起步） |
| 求解路线 | B. MLIP + 分子动力学（全阶非谐） | [@Ouyang2022; @Liu2021SnSe; @Verdi2021; @Wang2023aSi; @Cao2025metals] | 大温度跨度 + 相变区的 EMD 收敛标准 |
| 求解路线 | C. 描述符回归（不经势函数） | [@Hu2023; @Liu2025PINK] | 可泛化到非晶/无序的描述符 |
| 精度瓶颈 | 高阶非谐性（四声子/波状隧穿） | [@You2024; @Ouyang2022; @Liu2021SnSe] | 六声子及更高阶统一处理 |
| 精度瓶颈 | 长程与层状/弱 vdW | [@Tang2022hBN; @Li2022GeS] | 极性与静电长程修正的库级整合 |
| 精度瓶颈 | 势能面曲率/训练数据质量 | [@Koker2026; @Grandel2026] | 通用预训练势 + 声子导向微调的标准管线 |

## 四、求解路线：MLIP 在 $\kappa_L$ 预测中的三种技术选择

本分支讨论"用什么势函数、送到哪个求解器"。三条主线：把 MLIP 当精确力常数提供者喂给 PBTE、让 MLIP 直接驱动分子动力学、以及绕过势函数做描述符回归。

**路线 A：MLIP 作为微扰框架的力常数来源。** 传统上 $\kappa_L$ 由三声子（线性/迭代）PBTE 求取，瓶颈在三阶力常数的 DFT 计算。Choi 等在神经网络势下加速该过程 [@Choi2022]；Mortazavi 与 Podryabinkin 等把 MTP 应用于二维材料，同时给出声子色散与三声子散射成分 [@Podryabinkin2020; @Mortazavi2020],并在 graphene/borophene 异质结构中验证了"DFT 级精度 + 经典 MD 成本"的多尺度可行性 [@Mortazavi2020]。这条路线把 $\kappa_L$ 计算从"每个位移构型一次 DFT"降为"一次训练 + 每次 MD 一次 MLIP 求值"，但保留了微扰框架在强非谐体系中的截断误差。

**路线 B：MLIP 驱动的分子动力学直接求热导。** 当体系存在强高阶非谐性，微扰级的谐波/三声子处理可能定量失效。Ouyang 等在 BAs 与金刚石上的对照是本分支的关键证据：基于 MLIP 的三声子 PBTE 能复现金刚石、却显著高估高非谐性的 BAs，而同一 MLIP 跑 EMD 时两条结果都与实验吻合 [@Ouyang2022]。Liu 等在 SnSe 上证实：MTP 驱动的 EMD 能以无先验假设的方式自然包含四声子作用与温度依赖的各向异性 $\kappa_L$ 张量 [@Liu2021SnSe]。Verdi 等以 on-the-fly 贝叶斯 MLFF 在氧化锆上把相变与 Green–Kubo 热导整合进同一势函数，验证全阶非谐性描述无需先验判断"哪一阶重要" [@Verdi2021]。Wang 等在非晶硅上把 NEP 与量子修正结合起来，说明非晶与有限尺寸体系正是 EMD 路线的优势场景 [@Wang2023aSi];Cao 等进一步用统一神经进化势计算 16 种元素金属的 $\kappa_L$，把"一势覆盖多元素"的能力带到金属热输运 [@Cao2025metals]。Lahnsteiner 等则把机器学习力场用于大热力学系综的非谐晶格动力学，为 EMD 路线在"体系尺寸—声子收敛"冲突上提供了可扩展的实现 [@Lahnsteiner2022]。

**路线 C：描述符回归，走出势函数。** 两条互补的捷径不构建 MLIP：Hu 等以两阶段可解释模型返回 $\kappa_L$ 且保留物理可读性 [@Hu2023];Liu 等提出的 PINK 以物理信息驱动的 CGCNN 直接从 CIF 提取体/剪切模量并套用简化的 Slack 型公式，完成 37 万级材料的批量筛选，命中若干超低 $\kappa_L$ 候选 [@Liu2025PINK]。这条路线牺牲了对原子级动力学细节的描述，换取高吞吐与可解释性，其上限由"特征能否承载 $\kappa_L$ 的物理"决定。

| 对比维度 | 路线 A（MLIP+PBTE） | 路线 B（MLIP+MD） | 路线 C（描述符回归） |
|---|---|---|---|
| 非谐性覆盖 | 止于所取的声子阶数（三/四声子） | 全阶，无先验截断 | 隐含于特征，无法显式控制 |
| 代表性成本 | DFT 级一次性训练 | 训练 + MD 收敛 | 近即时批量推理 |
| 适用体系 | 弱—中非谐、周期晶体 | 强非谐、非晶/高温/无序 | 高通量初筛、材料库 |
| 代表证据 | [@Choi2022; @Podryabinkin2020] | [@Ouyang2022; @Liu2021SnSe; @Verdi2021] | [@Hu2023; @Liu2025PINK] |

小结：三条路线不是竞争而是互补——路线的选择应由"体系非谐强度 + 是否要原子细节 + 是否需要高吞吐"共同决定。

## 五、精度—成本权衡：与 DFT 相比的边界在哪

本分支把 MLIP 与 DFT 基线的偏差分解为"来自拟合误差"与"来自理论框架"两类，并据此划定 MLIP 的更优区间。

**成本端：增益是结构性的。** 多项工作一致报告 MLIP 相对 DFT 有两到五个数量级的速度提升。You 等在 Mg2GeSe4 上对比 MLIP 驱动、含三四声子与波状隧穿的输运计算，报告相对常规 DFT 约五个数量级的加速 [@You2024];综述 [@Arabha2021; @YangQian2021] 亦把"量子级精度 × 经典级成本"列为首要承诺。成本增益几乎不随体系复杂度衰减，这正是它支撑高通量筛选 [@Liu2025PINK] 与多元素覆盖 [@Cao2025metals] 的根基。

**精度端：偏差来源的二分。** 关键在于把误差归因清楚。当偏差来自势函数拟合误差时，EMD 与 PBTE 的 MLIP 结果都会偏离 DFT，但可通过更准的势或微调改善（见第六节）。而当偏差来自理论框架时，再准的势也补不回来——BAs 案例中三声子 PBTE 即使配准了 DFT，仍因忽略高阶散射而高估 $\kappa_L$，反而是含全阶非谐的 EMD 与实验一致 [@Ouyang2022]。换言之，MLIP 的真正贡献不只是把一个近似换成更准的近似，而是让"非谐性全阶"在分子动力学里成为默认而非例外。

**失效边界。** 在强各向异性/层状体系，MLIP 的增益可能打折。Li 等在单层 GeS/SnS 上对比机器学习势与 Stillinger–Weber 经验势，MTP 结果更接近 DFT 而 SW 高估 $\kappa_L$ [@Li2022GeS];Tang 等在块体 h-BN 上指出，弱范德华键与高度各向异性的势能面使层状材料成为 MLIP 建模的高风险区，需专门构造的 GAP 才能以 DFT 级精度复现跨层各向异性输运 [@Tang2022hBN]。这一结果提示：MLIP 相对 DFT 的成本优势是普遍的，但其精度优势在"势能面简单、DFT 本身可靠"的体系上最强、在强非谐与弱 vdW 界面上需要更多验证。

小结：精度—成本权衡的成立条件是"拟合误差主导"而非"理论框架主导"；当二阶误差（框架错误）盖过一阶误差（拟合误差）时，MLIP 的精度优势取决于它能否把高阶非谐性放进求解器。

## 六、瓶颈与对策：非谐性、长程与数据质量

本分支处理 RQ3：MLIP 普适到 $\kappa_L$ 的三个现存瓶颈各处于什么状态、已有哪些对策。

**瓶颈一：高阶非谐性的精确表达。** 四声子散射在强非谐热电材料（如 SnSe、Mg2GeSe4）中可显著压低 $\kappa_L$，MLIP 早已能提供其所需力常数或直接跑全阶 EMD [@Ouyang2022; @Liu2021SnSe; @You2024]。真正的空白是超高阶（五、六声子）与波状隧穿在统一框架下的规模化处理 [@You2024]，以及"何时必须升阶"的先验判据——这是 L3 层面的可检验缺口。

**瓶颈二：长程相互作用与层状/弱范德华体系。** 各向异性势能面与弱层间键使层状材料（h-BN 等）成为 MLIP 建模的高风险区，需要专门构造 GAP 才能复现跨层各向异性 [@Tang2022hBN];单层硫族化物上经验势的高估也说明仅靠训练未必弥补描述符的电荷/极化缺失 [@Li2022GeS]。极性材料中的长程静电力常数仍是库级（通用预训练）MLIP 覆盖的薄弱点，合成证据指向"需要显式长程项而非更高阶局域项"。

**瓶颈三：势能面曲率与训练数据质量。** 声子与 $\kappa_L$ 依赖势能面的二阶乃至三阶导数，标准地以能量/力/应力为损失的训练在曲率上可能欠优。Koker 等提出的 PFT 直接监督二阶力常数、使 MLIP 能量 Hessian 匹配 DFT 力常数，在 MDR Phonon 基准上显著提升声子热力学性质并改善依赖三阶导数的热导预测 [@Koker2026];Grandel 等在 53 个材料体系上系统比较多种微调策略并引入基于 LoRA 的 Equitrain，得出微调模型一致优于底层预训练模型与从头训练 [@Grandel2026]。这两项工作共同指向一种新范式：通用预训练势 + 面向声子的参数高效微调，正成为取代逐体系从头训练的主流路径。

## 七、综合讨论

跨分支看，MLIP 在 $\kappa_L$ 预测中的作用已发生一次定性位移。把三节证据并置：求解路线从"MLIP 喂微扰框架"向"MLIP 驱动全阶 MD"迁移（第四节的 EMD 优先证据），精度瓶颈从"拟合误差"转向"曲率与数据质量"（第六节的微调证据），而这恰好与"理论框架误差比拟合误差更难补"的结论（第五节）形成闭环——当微扰框架自带上限，剩余的高价值误差只能靠更准的曲率而非更准的拟合去收敛。

两类张力值得点明。其一是"路线 A vs 路线 B"：同为 MLIP，喂 PBTE 与跑 MD 在强非谐体系（如 BAs [@Ouyang2022]、SnSe [@Liu2021SnSe]）产生方向相反的系统偏差，说明把一条路线的结论套用到另一条路线是有风险的，综述应把求解器与势函数分开陈述。其二是"通才 vs 专才"：统一势（[@Cao2025metals]）、预训练势 + 微调（[@Grandel2026; @Koker2026]）主张覆盖广度，而体系专用势（[@Tang2022hBN; @Ouyang2022]）主张单体系极值精度；本综述的证据支持"分层使用"——用可泛化模型做初筛，用微调或专用势做终点验证。

被系统性地低估的是"可复现的曲率基准"。三项工作都用自己的误差口径自证，而尚无跨工作、跨求解器的统一声子基准主集（Mini 综述 [@Liu2023mini] 亦点出这一点）。这是最高杠杆的下一步：一个把势函数与求解器正交解耦的声子基准，才能让 IC 级结论在文献间可比。

## 八、开放问题与未来方向

- **统一高阶声子基准**：尚无文献把所有工作放在同一求解器 + 同一声子基准上比较，"四声子何时必要"缺乏定量判据——需要以 BAs [@Ouyang2022]、SnSe [@Liu2021SnSe] 型强非谐体系为试金石、把 MLIP 馈入的 PBTE 与 EMD 在统一势下对撞的基准。
- **长程/极性力常数**：非局域静电与极化长程相互作用在通用 MLIP 库中仍是薄弱点,需要把显式长程项整合进声子/热导管线。
- **五、六声子与波状隧穿的规模化**：波状隧穿在超低 $\kappa_L$ 材料中可超越粒子图像 [@You2024]，但其高效纳入 MLIP 驱动流程仍属空白。
- **微调的标准管线**：PFT/Equitrain 证明微调优于从头训练 [@Koker2026; @Grandel2026]，但"何时微调、微调多少数据、是否回退"尚无准则，值得系统对照。
- **离散动力学特征的可泛化描述符**：路线 C 无法包住非晶/无序构型，一个能承载非谐性与无序特征的描述符将补上高吞吐与全原子之间的缺口。

## 九、结论

RQ1（方法体系）：MLIP 面向 $\kappa_L$ 有三条可复用路线——作为精确力常数来源喂给 PBTE（[@Choi2022; @Podryabinkin2020; @Mortazavi2020]）、驱动分子动力学以容纳全阶非谐性（[@Ouyang2022; @Liu2021SnSe; @Verdi2021]）、以及跳过势函数的描述符回归（[@Hu2023; @Liu2025PINK]）；选择由体系非谐强度与吞吐需求决定。

RQ2（精度—成本权衡）：MLIP 相对 DFT 的成本优势是结构性的（最高约五个数量级 [@You2024]），精度优势则取决于误差来源——当拟合误差主导时（弱—中非谐晶体）MLIP 可靠且配微扰框架即可；当理论框架（微扰截断）主导时（强非谐如 BAs），EMD 路线的 MLIP 才更接近实验 [@Ouyang2022]。因此把"MLIP 更精确"与"MLIP 跑 MD 更精确"分开陈述是必要的。

RQ3（瓶颈与对策）：三大瓶颈均处于"有局部解、无统一方案"的状态——高阶非谐性已可由四声子与 EMD 覆盖但缺升阶判据 [@You2024; @Ouyang2022];长程/层状体系需体系专用势且仍属高风险区 [@Tang2022hBN];曲率与数据质量正被声子微调（PFT）与参数高效微调（Equitrain）撬动，预示通用预训练势 + 微调的范式转移 [@Koker2026; @Grandel2026]。

本综述的核心贡献是提出一个"求解路线 × 精度瓶颈"的双轴框架，把散见于应用案例的证据重新组织为一条清晰的范式演进主线——MLIP 在晶格热导率预测中的角色，正从"第一性原理的可负担替身"转向"能够默认容纳全阶非谐性的求解引擎"，而这一转向的根本依据，是理论框架误差比拟合误差更难用更准的势去弥补。

## 十、调研成本

本次调研以 sciverse 文献库为唯一信息源，效率足迹如下：

- 总检索调用次数：16（`semantic_search` 9 次、`search_papers` 结构化检索 7 次）
- 入选并纳入台账的文献数：21
- 核验通过率：21/21（全部经 sciverse 语义检索命中确认存在，判定 VERIFIED）
- 检索轮次 / 滚雪球轮次：5 轮，末轮零新增，达检索饱和
- wall-clock 用时：未记录
- 估计总 token 数：未记录

## 参考文献
