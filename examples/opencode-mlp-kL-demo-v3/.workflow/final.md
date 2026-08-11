# 机器学习势函数在晶格热导率预测中的应用进展

## 摘要

晶格热导率（lattice thermal conductivity）的精确预测长期受制于两种手段的固有瓶颈——第一性原理玻尔兹曼输运方程（BTE）精度高但三阶力常数计算昂贵，经验势分子动力学（MD）成本低却精度与迁移性不足。机器学习势函数（machine-learned interatomic potentials, MLIP）以接近 DFT 的精度、接近经验势的成本填平了这一鸿沟，正在重构热输运计算的工作流。本综述以 22 篇经存在性核验的文献为证据，系统梳理 MLIP 用于晶格热导率预测的两条计算范式（MLIP 驱动的力常数+BTE 谱学路线，与 MLIP 驱动的分子动力学线性响应/非平衡路线）、主要方法族（NEP、DeePMD、MTP、GAP/HDNNP）的适配场景，并重点剖析两个贯穿性挑战：力场精度（force error）对高导热体系的热导率系统性低估，以及四阶声子散射与波粒二象性输运的体系依赖性。核心判断是：方案选择（BTE 还是 MD）的重要性低于力场精度本身的状态，而高阶散射的作用须按体系非谐性强弱逐一裁决，不能一概而论。

## 核心要点

- **两条范式成本瓶颈相反**：BTE 路线的瓶颈在高阶力常数，MLIP 将其批量替换实现 2–10 倍乃至五个数量级加速；MD 路线的瓶颈在经验势精度，MLIP 首次让 MD 在复杂/大体系上逼近第一性原理精度。
- **方法族分化**：NEP 以极高计算效率和 GPU 大规模模拟见长；DeePMD 早期即用于相变与二维体系；MTP 以少参数、弱数据需求适配高熵合金等复杂多组元；GAP/HDNNP 奠定了精度标杆。
- **力误差是一条被低估的暗线**：多个独立来源收敛到同一结论——MLIP 的力误差会系统性低估本就很高的热导率，须通过力误差外推/校正恢复。
- **四声子与波粒二象性是裁决点而非默认项**：Mg₂GeSe₄ 研究显示四声子使 $\kappa$ 降低 22–27%，而 MoS₂/MoSe₂ 的 MLFF 复核认为完全收敛的四声子贡献可忽略——正确边界取决于声子带宽、非谐性与体系维度。
- **复杂体系（非晶/缺陷/高熵/界面）是 MLIP 的主场**，但也暴露出迁移性、电子-振动耦合等新的开放问题。

## 一、引言

热管理是当今功率电子、热电材料、低维器件与能源存储共同面对的核心瓶颈。晶格热导率 $\kappa_L$ 决定器件散热能力与热电优值 $zT$，其可靠预测因此成为材料计算的核心目标之一。长期以来，$ \kappa_L $ 的预测存在一道熟悉的取舍：基于第一性原理（DFT）提取原子间力常数（interatomic force constants, IFC）并求解声子玻尔兹曼输运方程（Boltzmann transport equation, BTE）的路线精度高，但三阶乃至四阶力常数的计算代价使其难以覆盖低对称、大原胞、含缺陷或无序的体系；反之，基于经验势的分子动力学（MD）路线可以承载十万乃至百万原子，却因势函数精度与迁移性不足而常常失真——经典二体势甚至难以可靠复现硅的热导率。[1] 机器学习势函数（MLIP）通过拟合第一性原理能量-力场数据，在保留接近 DFT 的精度同时把单点计算成本降低 2–10 个数量级，从而为上述取舍提供了一条新解。[2][1]

本综述研究问题如下：

- **RQ1（方法体系）**：MLIP 分别如何加速 BTE 与 MD 两条热导率计算范式？各自解决的成本瓶颈与适用上限是什么？
- **RQ2（方法族适配）**：NEP、DeePMD、MTP、GAP/HDNNP 等主要 MLIP 方法族在热输运场景下有何精度—成本—适用体系的分化？
- **RQ3（挑战与边界）**：力场精度（force error）如何系统性影响 $\kappa_L$ 预测？四声子散射与波粒二象性输运的作用在何种体系中显著、何种体系中可忽略？

与既有综述 [2][1] 侧重"ML 用于热导率的整体图谱"不同，本文聚焦 MLIP 这一类作为第一性原理与大规模模拟之间桥梁的势函数，并把"力误差敏感性"与"高阶散射裁决"两条被散落在各应用中的线索显式抬升为核心脉络。全文组织如下：第二、三节给出检索方法与分类框架；第四节起按两条范式、方法族、两大挑战、复杂体系应用逐层展开；最后综合讨论、开放问题与结论。

## 二、研究方法

本综述遵循系统调研流程：以 sciverse 检索工具（语义检索为主）围绕"MLIP × 晶格热导率"生成多视角检索，覆盖通用方法、各方法族专项、四声子机制、力误差裁判型、界面与复杂体系等视角，滚雪球补搜至饱和（滚雪球 1 轮，末轮新增 0 篇，达检索饱和）。纳入标准为：正文核心对象为机器学习/机器势在晶格热导率或声子输运中的应用或方法建制；排除纯端到端热导率回归（非势函数）与纯粹经验势工作。共入选 22 篇文献，均经存在性核验（标题/作者/年份与检索来源一致），参照期刊或预印本来源抄录取用。证据类型覆盖：方法奠基原文、系统应用研究、裁判型（边界/误差）研究、权威综述，构成"方法—应用—批判—综述"的完整证据链。综述模式下参考文献按编译工具由引用台账自动铸造。

## 三、分类框架

按"计算范式 × 核心挑战"二维组织，形成 MECE 的分类骨架：

- **范式轴**：MLIP 驱动 BTE（力常数+谱学）与 MLIP 驱动 MD（Green-Kubo / NEMD / HNEMD 线性与非平衡响应）——两种范式解决的成本瓶颈不同，构成 RQ1 的主体。
- **方法轴**：NEP / DeePMD / MTP / GAP·HDNNP——构成 RQ2 的主体。
- **挑战轴**：力场精度（force error）敏感性、高阶（四声子/波粒）输运机制——构成 RQ3 的主体，也是本文的洞见主线。

框架的空格（gap）：高熵合金热导率的 MLIP 直接研究仍偏少，多数 MLIP 高熵工作聚焦力学/腐蚀；迁移性（势在训练域之外的泛化）与电子-声子耦合在热输运场景尚未系统融合。

## 四、范式一：MLIP 驱动 BTE——以力常数替换实现的谱学加速

BTE 路线把 $ \kappa_L $ 写成各声子模的贡献，核心难点在于获得足够精确的原子间力常数（尤其是三阶）。MLIP 在一个方法内同时给出二阶与三阶力常数，天然适配这一流程。HDNNP 的奠基工作以力训练替身，在硅与氮化镓（GaN）块体上把由 DFT 计算的 $ \kappa_L $ 复现到 5% 以内，验证了"ML 力场 + BTE"作为 DFT 的忠实代理。[3] 该系统化思路被进一步推广到 25 种不同对称性、热导率跨越多个数量级的材料，MLIP 统一了各体系的计算成本，相对纯 DFT 获得 2–10 倍（缩小训练集时可达约 50 倍）的加速而不明显损失精度。[4] 这印证了一个关键事实：MLIP 与 BTE 组合直接继承了 BTE 的高精度，同时把成本瓶颈从频繁的 DFT 力常数采样转移到一次性的势函数训练上。

MTP 在二维体系上的应用同样依托这一范式。对 Janus/非-Janus 二胺（diamane）单层，以 AIMD 短轨迹拟合的 MTP 取代 DFT 生成非谐力常数，配合完整迭代 BTE 求得室温 $\kappa_L$（石墨烯约 3636，C₂F 二胺约 377 W/m·K），量级与机制均合理。[5] 这显示 MTP 以较少的拟合参数即可为全谱学流程供给足够的力常数，尤其适合需要反复扫描结构-性质关系的场景。BTE 架构下 MLIP 的另一类应用是端到端代理：直接把声子散射率（含三、四阶）作为学习对象，可对第一性原理计算实现约两个数量级的加速——[2] 将此概称为"间接预测"，与本文聚焦的"势函数代理"互补。

BTE 范式的内在局限随之浮现：它依赖周期晶格的声子图像。当体系存在强无序、非晶化或界面时，准粒子声子图像部分失效，此时 MD 范式反而成为首选。[1] 这一互补性引出范式二。

## 五、范式二：MLIP 驱动 MD——面向无序与大规模体系的线性/非平衡响应

MD 路线通过在相空间中直接演化原子来获取热输运，天生适合无序、缺陷、界面与非谐强的体系，但其精度长期受制于经验势。MLIP 把第一性原理精度注入 MD，在几个方向上突破了尺度与保真度的双重极限。

其一，同一套势可以覆盖多相。针对硅在同一立方势中同时拟合晶体、液态与非晶相，用该统一深度势可复现相变路径，并给出各相与实验和第一性原理相符的热导率。[6] 这直接回应了经验势难以跨相迁移的老问题。其二，MLIP 把 MD 的规模上限推向百万原子。NEP 的多晶石墨烯研究在消费级桌面 GPU 上完成超 140 万原子、接近第一性原理精度的热输运模拟，量化了不同晶粒尺寸下晶界对 $\kappa$ 的抑制，并发现晶界使体系在显著拉伸应变下仍保持有限热导率——与完整石墨烯的赝发散行为相反，为低维动量守恒体系的热输运提供了新的物理解读。[7] 其三，MLIP 进入超低热导率极端区。AgTl₂I₃ 通过扩展反键态实现 0.21 W/m·K（300 K）并延续至 0.17 W/m·K（523 K）的晶格热导率，MLIP 驱动的动力学揭示了其抑制粒子型传播与波粒型隧穿的共同机制。[8] 非孔/非晶碳的密度依赖热输运也依赖 NEP 生成真实非晶结构并在百万至千万原子规模上执行均匀非平衡模拟。[9]

MD 范式内部对"用哪种 MD 方法提取 $\kappa$"同样有讲究。Green-Kubo 平衡响应与 NEMD/HNEMD 非平衡响应在无序、声子平均自由程较短或四声子显著的体系中往往比分光学的 BTE 更稳妥。InSe 单层的研究提供了一个经典的对照：Green-Kubo + 深度势（GK-DP）给出 9.52 W/m·K（300 K）的良好估计，而三声子 BTE-DFT 给出 13.08 W/m·K，前者与实验更接近，其差异被归因于光学支间能隙使四声子被排除后高估了低光学支的贡献。[10] 该工作直接指向一个更广的命题：**当体系存在强四声子或强非谐时，BTE 若不纳入更高阶散射便可能系统性地高估 $ \kappa_L $，而 MD 通过对全部阶散射的隐式含纳反而更稳。**

值得指出的是，两条范式并非互斥，而是以算力-精度光谱连接。综合谱系看，BTE 保谱学解析性、适合高对称准粒子体系，MD 保全阶散射与无序能力、适合低对称与拉伸边界体系。[1] 对应用者而言，选择首先取决于目标体系是否仍处在声子准粒子有效范围内。

## 六、方法族分化：NEP、DeePMD、MTP、GAP/HDNNP

在范式之外，方法族本身承载了 RQ2 关注的分化。这里按"基准精度—数据需求—计算效率"三维比较四类主流方法。

**GAP/HDNNP 定义了精度与奠基地位。** HDNNP 在硅与 GaN 上把力 RMSE 压到 40 meV/Å 以下，热导率偏差控制在 5% 以内，确立了"MLIP ≈ DFT 代理"的基准。[3] GAP 通过高斯过程回归以相对较少的结构训练非晶硅势，兼顾晶态与非晶两种相的 $\kappa$ 预测，成为后续 GAP 系在元素半导体上的代表。[11] 此后大量 NEP/MTP 工作都以这类早期精度验证为对照。

**DeePMD 早期即以多相与二维体系立身。** 硅统一相势（覆盖晶态/液态/非晶）的实践充分展示了其跨相迁移能力。[6] 其在二维后过渡金属硫属化物（如 InSe 单层）上与 Green-Kubo 的组合，则展示了深度势在低维各向异性体系中的可靠性。[10] 深度势的优势在于端到端自动特征化，无需人工构造对称函数，[6]；代价是训练数据相对较多、超参敏感。

**NEP 以计算效率与 GPU 大规模化为差异化优势。** 其奠基论文系统论证了神经进化势在"高精度+低成本"上的组合，并把热输运作为代表性应用场景。[12] 依赖 140 万原子仿真的桌面 GPU 可行性、[7] 三个晶型 Ga₂O₃ 由单一势统一预测、[13] 以及 GaN 超参优化中热导率预测与实验结果的高度一致（室温 259 W/m·K），都指向同一判断：NEP 在把 MLIP 推向真正可承载工程级体系尺度上走得最远。

**MTP 以少参数、弱数据需求契合复杂多组元体系。** 电子矩张量势（eMTP）在经典 MTP 结构上引入电子温度自由度，可在无额外第一性原理计算下复现 Nb 与 TaVCrW 高熵合金含电子-振动耦合的热力学量。[14] MTP 用较少拟合参数即可在二维二胺等体系上支撑全套 BTE 谱学，[5] 说明其在数据受限、多组元体系中有独特价值。

一个跨方法族的收敛信号值得强调：尽管实现各异，四者在"把 BTE 或 MD 的热导率预测提升到接近 DFT 精度"这一核心目标上殊途同归，而差异集中在训练数据规模、超参敏感性、GPU 可扩展性与跨相迁移性——这不应被理解为优劣高下，而是面向不同成本结构与体系复杂度时的分工。

## 七、挑战一：力场精度（force error）对热导率的系统性影响

这是本综述裁判型线索的核心。热输运对作用于原子上的力的误差异常敏感，远甚于对能量或结构参数的敏感性。

机理层面的证据早已存在：向经典势的三阶力常数注入噪声，即可导致预测的 $\kappa_L$ 大幅偏离基准；即便施加平移不变性约束或 Gruneisen 参数作为判据，也无法保证三阶力常数足够精确。[15] 该工作清楚地展示了：**热导率是力场的"高阶微分"性质，对力误差极度放大。**

MLIP 把这一敏感性问题带到了新的前台，因为 MLIP 的训练目标正是减少能量与力的期望误差，但残余的力噪声在 MD 的 Langevin 恒温器下会产生额外的随机力干扰，从而系统性低估本就偏高的热导率。针对这一机制，ForceCorr 提出了把力误差外推到零限的校正方案，恢复被抑制的热导率。[16] 其同行 GaN 研究同样发现，具有本质上高热导体系的材料往往因 MLIP 预测力误差较大而被低估，并于超参优化的同时实现了力预测误差校正，使 wurtzite GaN 的室温 $\kappa$ 与报道的实验高度吻合（259 W/m·K）。[17]

综合来看，力误差问题把"选 BTE 还是 MD"的争论微妙地改写为"力的精度是不是达标"的状态检查。对极高 $ \kappa_L $ 的体系（如金刚石、BAs、GaN），MLIP 的力学精度直接决定热导率是否被系统性低估；校正或外推成为必要工序。这也反向提示：MLIP 在超高热导率体系上的"成功"往往是以额外误差校正换来的，而非天然成就，评估这类预测时必须把力误差状态纳入视线。

## 八、挑战二：四声子散射与波粒二象性输运——裁决点而非默认项

三声子散射是 BTE 处理非谐的主力，但四声子与"波粒二象性"输运（Wigner 隧穿）正把热导率理论推向更高阶。Feng & Ruan 从量子力学层面首次在完整布里渊区内显式计算四声子散射率，发现其在中高温区可与三声子相比拟，使氩的 $\kappa$ 在 80 K 降低逾 60%，挑战了"高阶过程一般不重要"的默认假设。[18] 此后，针对十七种闪锌矿半导体的研究证实，仅三声子理论会大幅高估许多材料的 $\kappa$，引入四声子后与实验的吻合显著改善；而硼、碳、氮族化合物的四声子散射异常弱，这解释了立方砷化硼、磷化硼与碳化硅的超高热导率。[19]

MLIP 把四声子的研究从昂贵的第一性原理中解放出来。Mg₂GeSe₄ 的研究在单一 MLIP 框架内同时覆盖粒子型与波粒型输运、三声子与四声子散射，相对 DFT 获得五个数量级加速；四声子使 300 K 与 900 K 的 $\kappa$ 分别降低 22.5% 与 26.7%，随温度升高粒子型贡献下降而波粒型贡献上升。[20] 这显示 MLIP 让"全谱学乃至高阶散射"的系统研究首次在可负担的成本内成为可能。

然而，四声子的重要性并非普遍成立。对 MoS₂ 与 MoSe₂ 的系统重访使用 GAP、MACE、NEP、HIPHIVE 等多种 MLFF 并配合均匀非平衡 MD 做了远超常规的收敛检验，结论是：**完全收敛的四声子过程对这一二维体系的本征 $ \kappa $ 贡献可忽略**，与某些近期夸大四声子作用的论断相反。[21] 它与 Mg₂GeSe₄ 及 InSe [10] 的结论形成鲜明对照。

如何裁决这一矛盾？证据拉开的轴是**体系依赖的声子结构与非谐特征**：在声学/光学支间存在大能隙、声子带宽受限的材料（如 InSe、Mg₂GeSe₄ 这类热电/宽隙体系）中，四声子与波粒型通道容易凸显，排除它们会高估 $\kappa$；而在禁带结构相对平坦、非谐适中的二维材料（如 MoS₂/MoSe₂）中，三声子已足以主导，四声子收敛后贡献趋零。[20][21] 另一轴是温度：四声子散射率随温度升高而增强，其对 $\kappa$ 的压制在室温以上尤为明显——Feng-Ruan 的量子力学计算即指出四声子散射率随温度近似平方地增长[18]，高温时四声子在多种强键半导体中对 $\kappa$ 的抑制也已在选律框架下被证实[19]。 因此，**把"是否需要四声子/波粒项"当作逐体系裁决的问题，而非通用默认，是正确的工程态度**——这正是本综述与"三声子万能"旧范式之间最核心的分野。

## 九、复杂体系应用：缺陷、非晶、高熵合金与界面

MLIP 的价值在 BTE 难以覆盖的复杂体系中最为充分。

**缺陷与晶界**：多晶石墨烯的百万原子研究直接量化了晶界对 $\kappa$ 的抑制及其在应变下的行为差异，[7] 非孔/非晶碳则覆盖了密度从 0.3 到 3.5 g/cm³ 的连续结构谱系。[9]

**界面热导**：硅-金刚石界面的 MLIP 研究显示，以 DFT 训练的 MLIP 得到的界面热导率比 Tersoff/Brenner 等半经验势更贴近实验，传统势高估界面热导约三倍；MLIP 正确复现了声子色散与寿命。[22] 这为"经验势界面模拟系统性失真、MLIP 修复"提供了直接对照。

**高熵合金与多组元**：eMTP 把电子与振动自由度同时纳入，在高熵合金这类电子-振动耦合显著的体系中尤为重要。[14] 但需要如实指出：热导率的 MLIP 直接研究在高熵合金中仍偏少，多数高熵 MLIP 工作聚焦力学或腐蚀预测，这是本综述识别的体系性 gap，也是有待填补的方向。

**非晶**：GAP 系统展示了非晶硅相干/非相干两类结构可在一套势下统一建模并给出与实验一致的 $\kappa$。[11] 非孔/非晶碳的密度依赖热输运同样验证了 NEP 在无序结构上的可靠性。[9]

综合复杂体系应用，可以看到一个贯穿性的模式：**MLIP 越是作用于 BTE 失效的"无序/缺陷/界面"地带，其相对经验势的优势就越显著**。经验势在这些场景下的系统性失真（如硅界面高估三倍）与 MLIP 对 DFT 的忠实性形成鲜明反差，构成 MLIP 最具说服力的应用理由。

## 十、综合讨论

把四条线索并置，一个清晰的图景浮现出来。

**第一，范式之争在实际应用中是光谱而非阵营。** BTE+MLIP（第四节）与 MLMD（第五节）分别治理了成本瓶颈与精度瓶颈，它们的适用边界取决于目标体系是否仍处于声子准粒子有效范围。[1] 对高对称、弱无序体系，BTE 保留谱学解析力与高精度；对非晶、缺陷、强非谐或超大规模体系，MD 的全阶含纳与尺度能力占优。[10][7]

**第二，方法族的两极分化已经清晰。** 一端是 NEP 的工程级 GPU 可扩展性（百万原子/桌面 GPU），[7][12] 另一端是 MTP 的少参数弱数据（高熵、多组元），[14][5] 而 DeePMD 与 GAP/HDNNP 则分别覆盖了跨相迁移与精度奠基。[6][3][11] 这四极没有优劣，只有成本结构与体系复杂度的匹配。

**第三，两条"暗线"把表面繁荣拉扯回理性。** 力误差敏感性（第七节）与四声子/波粒贡献的体系依赖性（第八节）共同指向同一方法论立场：MLIP 预测 $\kappa_L$ 的可靠上限不取决于方法族的标签，而取决于力的精度状态与目标体系的非谐机制是否被正确建模。这正是本综述区别于单纯罗列应用的洞见核心。

**第四，交叉对比显示证据的非平凡张力。** 同样是二维材料，InSe 需要四声子才能与实验吻合[10]，而 MoS₂/MoSe₂ 的四声子收敛后贡献趋零[21]；同样是含硼/碳/氮的强键半导体，其四声子散射异常弱而热导率极高[19]。这些张力说明，把约束条目生搬硬套会失败，必须落到逐体系的声子结构与非谐强度上裁决。

## 十一、开放问题与未来方向

基于上述分析，本综述识别出以下具体开放问题，而非泛泛的"需更多研究"：

1. **高熵合金热导率缺乏体系性 MLIP 建制。** 现有高熵 MLIP 多聚焦力学/腐蚀[14]，热导率的专门工作稀疏，如何构建可在化学无序+局域畸变下稳定迁移的多组元热输运势仍是空白。
2. **力误差校正的通用理论缺失。** 外推校正虽被验证有效[16][17]，但其适用范围（温度、体系、恒温器类型）尚缺通用判据，且缺少可与 IFC 精度谱系[15]衔接的统一误差框架。
3. **四声子与波粒二象性的"何时重要"尚无量纲化判据。** Mg₂GeSe₄ 显著[20] vs MoS₂ 可忽略[21]的对立呼唤一个由声子带宽、非谐参量、温度与维度共同构成的先验判据。
4. **低维动量守恒体系的热输运性质存疑。** 晶界使多晶石墨烯在拉伸应变下保持有限 $\kappa$、而完整层赝发散的对比[7]，暗示长波声子裁剪与边界条件在多维传输理论中尚未闭合。
5. **温度依赖与电子-振动耦合融合有限。** eMTP 已证明电子自由度可并入势框架[14]，但将其与热导率谱学在高温功能材料中系统耦合仍属早期。

## 十二、结论

针对引言中的三个研究问题，本文以 22 篇证据得出如下判断：

**RQ1（方法体系）**：MLIP 同时高效驱动 BTE 与 MD 两条范式，但方式不同——BTE 的路经是把昂贵的高阶力常数替换为 ML 势输出，获得 2–50 倍乃至 5 个数量级加速[4][3][5][20]；MD 的路经是把第一性原理精度注入相空间演化，突破无序/非晶/大体系/界面瓶颈[6][7]。两者是互补光谱而非互斥阵营。[1]

**RQ2（方法族适配）**：NEP 以 GPU 工程级大规模与效率见长[12][7]，DeePMD 长于跨相迁移与二维低维体系[6][10]，MTP 以少参数弱数据契合高熵多组元[14][5]，GAP/HDNNP 建立了精度与奠基基准[3][11]。选择取决于成本结构与体系复杂度。

**RQ3（挑战与边界）**：力误差会系统性低估高导热体系的 $\kappa_L$，需外推/校正恢复[16][17][15]；四声子与波粒二象性输运的作用体系依赖——在能隙受限、声子带宽狭的体系（如 InSe、Mg₂GeSe₄）中显著并须纳入[10][20]，在声子结构平坦的二维材料（如 MoS₂/MoSe₂）中收敛后贡献可忽略[21]，而在高温普遍增强[18][19]。

归结为一句话：**机器学习势函数并未消解热导率预测的困难，而是把困难精确地重新定位到"力的精度"与"非谐机制裁决"这两个可把握的支点上**——这既是它成功的底色，也是未来研究的着力处。

## 参考文献

[1] X. Qian, R. Yang, “Machine learning for predicting thermal transport properties of solids,” Materials Science and Engineering: R: Reports, 2021.
[2] Y. Luo, M. Li, H. Yuan, H. Liu, Y. Fang, “Predicting lattice thermal conductivity via machine learning: A mini review,” npj Computational Materials, 2023.
[3] E. Minamitani, M. Ogura, S. Watanabe, “Simulating lattice thermal conductivity in semiconducting materials using high-dimensional neural network potential,” Appl. Phys. Express, 2019.
[4] J. M. Choi, K. Lee, S. Kim, M. Moon, W. Jeong, S. Han, “Accelerated computation of lattice thermal conductivity using neural network interatomic potentials,” Computational Materials Science, 2022.
[5] M. Raeisi, B. Mortazavi, E. V. Podryabinkin, F. Shojaei, X. Zhuang, A. Shapeev, “High thermal conductivity in semiconducting Janus and non-Janus diamanes,” Carbon, 2020.
[6] R. Li, E. Lee, T. Luo, “A unified deep neural network potential capable of predicting thermal conductivity of silicon in different phases,” Materials Today Physics, 2020.
[7] X. Zhou, Y. Liu, B. Tang, J. Wang, H. Dong, X. Xiu, S. Chen, Z. Fan, “Million-atom heat transport simulations of polycrystalline graphene approaching first-principles accuracy enabled by neuroevolution potential on desktop GPUs,” arXiv (Cornell), 2024.
[8] R. Cheng, C. Wang, N. Ouyang, X. Shen, Y. Chen, “Strong crystalline thermal insulation induced by extended antibonding states,” arXiv, 2025.
[9] Y. Wang, Z. Fan, P. Qian, M. A. Caro, T. Ala-Nissila, “Density dependence of thermal conductivity in nanoporous and amorphous carbon with machine-learned molecular dynamics,” arXiv, 2024.
[10] J. Han, K. Chen, J. Dai, Q. Zeng, X. Yu, “Lattice thermal conductivity of monolayer InSe calculated by machine learning potential,” Nanomaterials, 2023.
[11] X. Qian, S. Peng, X. Li, Y. Wei, R. Yang, “Thermal conductivity modeling using machine learning potentials: Application to crystalline and amorphous silicon,” Materials Today Physics, 2019.
[12] Z. Fan, Z. Zeng, C. Zhang, Y. Wang, K. Song, H. Dong, Y. Chen, T. Ala-Nissila, “Neuroevolution machine learning potentials: Combining high accuracy and low cost in atomistic simulations and application to heat transport,” Phys. Rev. B, 2021.
[13] G. Zhang, L. Li, Z. Sun, G. Wu, X. Sun, W. Shen, K. Liang, Z. Zhang, Z. Qi, X. Wang, Z. Sun, “A neuroevolution potential for predicting the thermal conductivity of alpha-, beta-, and epsilon-Ga2O3,” Applied Physics Letters, 2023.
[14] P. Srinivasan, D. Demuriya, B. Grabowski, A. Shapeev, “Electronic moment tensor potentials include both electronic and vibrational degrees of freedom,” npj Computational Materials, 2024.
[15] H. Xie, X. Gu, H. Bao, “Effect of the accuracy of interatomic force constants on the prediction of lattice thermal conductivity,” Computational Materials Science, 2017.
[16] X. Wu, W. Zhou, H. Dong, P. Ying, Y. Wang, B. Song, Z. Fan, S. Xiong, “Correcting force error-induced underestimation of lattice thermal conductivity in machine learning molecular dynamics,” J. Chem. Phys., 2024.
[17] Z. Chen, Y. Yuan, W. Ding, S. Li, M. An, G. Zhang, “Hyperparameter optimization and force error correction of neuroevolution potential for predicting thermal conductivity of wurtzite GaN,” arXiv, 2025.
[18] T. Feng, X. Ruan, “Quantum mechanical prediction of four-phonon scattering rates and reduced thermal conductivity of solids,” Phys. Rev. B, 2016.
[19] N. K. Ravichandran, D. Broido, “Phonon-phonon interactions in strongly bonded solids: Selection rules and higher-order processes,” Phys. Rev. X, 2020.
[20] H.-J. You, Y.-T. Chiang, A. Bansil, H. Lin, “Effects of four-phonon scattering and wave-like phonon tunneling effects on thermoelectric properties of Mg2GeSe4 using machine learning,” arXiv (Cornell), 2024.
[21] T. Kocabas, M. Keceli, T. Gurel, M. Milosevic, C. Sevik, “Thermal conductivity limits of MoS2 and MoSe2: Revisiting high-order anharmonic lattice dynamics with machine learning potentials,” arXiv, 2025.
[22] A. Rajabpour, B. Mortazavi, P. Mirchi, J. El Hajj, Y. Guo, X. Zhuang, S. Merabia, “Accurate estimation of interfacial thermal conductance between silicon and diamond enabled by a machine learning interatomic potential,” arXiv (Cornell), 2024.
