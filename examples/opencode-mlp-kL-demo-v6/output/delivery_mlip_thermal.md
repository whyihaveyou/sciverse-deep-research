# 机器学习势函数在晶格热导率预测中的应用进展：计算路径、材料谱系与精度边界

## 关键引用

- 综述：MLIP 在热导率计算系统的回顾 [1]；基于机器学习的晶格热导率预测综述 [2]。
- 架构奠基：Moment Tensor Potentials（MTP）[3]、神经进化势（NEP）[4]、Gaussian Approximation Potential（GAP）[5]。
- 谱方法路径：以 MTP [3] 配合主动学习打通复相 CoSb3 声子输运 [6]；MTP [3]/ShengBTE 多尺度建模 [7]；机器提取非谐力常数加速声子热导 [8]；四声子散射 + MLP [9]；高阶非谐性从 MD 精确刻画 [10]；MoS2/MoSe2 高阶非谐 [11]。
- 直接 MD 路径：晶态与非晶硅 [12]；等变 GNN 势 Green-Kubo 相变材料 [13]；$\beta$-Ag$_2$Se 的 Green-Kubo [14]；非晶二氧化硅 ML-MD [15]。
- 材料系统：h-BN 单层（GAP [5]）[16]；二维材料族（MTP [3]）[17]；SnSe 高温输运 [18]；下地幔 MgSiO$_3$ 的深度势 MD [19]；Mg-Te-Pb 热电深势模型 [20]；GaN 点缺陷 [21]。
- 精度-局限：力误差对热导的影响 [22]；MLIP 基础模型前瞻 [23]。

## 摘要

机器学习原子间势（Machine-Learning Interatomic Potentials, MLIPs）正在从根本上改变晶格热导率（$\kappa_\mathrm{lat}$）的预测范式：它以 DFT 量级的准确性和经验势量级的成本，刻画声子-声子相互作用，从而把声子玻尔兹曼输运方程（BTE）与 Green-Kubo 分子动力学（MD）两类传统上计算昂贵的方法推进到复杂化合物、二维材料、非晶与高温体系。本综述梳理 MLIPs 在晶格热导率预测中的两条主流计算路径——（i）声子谱方法：以机器势构建二阶/三阶/四阶力常数并衔接声子 BTE 求解器；与（ii）直接分子动力学：以机器势驱动 Green-Kubo 或非平衡 MD 处理强非谐、非晶、缺陷与大胞体系。文中在代表性材料系统（二维族、热电与超低热导、高温地幔与相变材料、含缺陷半导体）上交叉对比各架构（MTP、NEP、GAP、深度势、等变图神经网络 [3, 4, 5, 19, 13]）的适用边界，并聚焦“力误差如何传播到热导率”这一精度瓶颈，指出当前梯队仍以体系专一副势为主、缺乏统一的基准与跨体系泛化标准。未来方向指向主动学习闭环与面向多体系的基础化势模型。

## 核心要点

- **两条路径的谱系分工**：谱方法（力常数 + BTE）保留声子分辨信息、适合预测晶态材料，MLIP 主要作为昂贵的 DFT 力常数采样的加速器 [6, 7, 8]；直接 MD（Green-Kubo）天然涵盖全域非谐与实际温域，适合强非谐、非晶、缺陷体系，代价是统计噪声与尺寸收敛 [12, 13, 15]。
- **高阶非谐性是把双刃剑**：MLIP 能稳定捕获四阶及以上非谐力常数，显著修正低估声子寿命的热导率（如四声子散射可大幅压低 wurtzite BAs 的预测值）[9, 10]，但在强非谐体系中其结果对势的质量与采样异常敏感 [11]。
- **力误差是精度下限的决定项**：热导率对力常数的噪声放大是非线性的，单纯看势的能量/力均方误差难以直接推断 $\kappa_\mathrm{lat}$ 可靠性 [22]。
- **材料谱系已从基础二维扩展到功能材料**：从二维 h-BN [16]、石墨烯/硼硼烷 [7] 到热电 SnSe [18]、Ag$_2$Se [14]、相变材料（PCM）[13]、地幔矿物 MgSiO$_3$ [19] 与含缺陷 GaN [21]，应用覆盖“超高热导”与“玻璃态超低热导”两极。
- **体系专一副势仍为主流**：当前成功案例几乎都是“一体系一势”，基础化/跨体系泛化（foundation MLIP）仍处萌芽 [23]。

## 一、引言

晶格热导率 $\kappa_\mathrm{lat}$ 是热电、热管理、地幔地球物理与相变存储器件设计的核心物理量。它的第一性原理预测长期受困于“准确-昂贵的双难”：声子玻尔兹曼输运方程（phonon BTE）需要高阶（三阶乃至四阶）原子间力常数，其从头算（ab initio）获取对大胞、低对称、强非谐体系代价极高；而经验势虽快，其声子描述通常不够可靠。机器学习原子间势（MLIPs）在这两条要求之间提供了一个新的平衡点——它以 first-principles 数据训练，把成百上千次 DFT 计算的代价分摊到离线建势阶段，从而让“DFT 精度、经验势规模”的热输运模拟变得可行。

需要说明的是，MLIPs 属于更广义的“机器学习驱动晶格热导率预测”的一部分——后者还包括直接以成分/结构特征回归 $\kappa_\mathrm{lat}$ 的数据驱动模型 [2]。本综述聚焦其中更能保真物理的**势函数路线**：把机器势嵌入成熟的声子/MD 输运框架，而非端到端地直接回归标量导热值。我们据此提出三个研究问题：

- **RQ1**：MLIPs 相比 DFT 与传统势，在晶格热导率预测上实际提供了怎样的精度-成本收益？两条实现路径（谱方法 vs 直接 MD）各在何时占优？
- **RQ2**：不同的 MLIP 架构（MTP、NEP、GAP、深度势、等变图神经网络 [3, 4, 5, 19, 13]）在刻画声子色散与热输运上的适用边界各是什么？它们的代表性应用落位在哪些材料系统？
- **RQ3**：当前方法的精度瓶颈、泛化局限与标准化缺失具体何在？未来（主动学习闭环、基础化势模型）的可能走向是什么？

与已有的机器学习综述相比，本文不追求算法清单的穷举，而是以“热导率预测”为锚点，围绕计算路径与材料谱系组织证据，并把“力误差如何传播到导热预测”作为贯穿的精度主线。正文结构如下：第二部分说明检索与纳入方法；第三部分给出分类框架；第四与第五部分分别考察谱方法与直接 MD 两条路径；第六部分在代表性材料系统上做交叉对比；第七部分讨论精度-局限与开放问题；最后结论逐条回答上述 RQ。

## 二、研究方法

本综述的检索仅使用 sciverse 学术文献源，围绕“机器学习势函数 $\times$ 晶格热导率/声子输运”构造检索视角：主流方法（谱方法、直接 MD）、相邻领域（热电、非晶/高温、二维材料、相变材料）、方法论（高阶非谐性、四声子散射、力误差）。每个视角用关键词族执行结构化检索，再以已入选文献为种子经引文网络向后（REFERENCES）与向前（CITATIONS）滚雪球至饱和；检索按选题的时效档补充了近期（2024–2026）文献以追踪“基础化势模型”与“力误差传播”等前沿视角。

纳入标准：主题必须是“机器学习原子间势（或机器学习的力场）嵌入到声子 BTE / 分子动力学的晶格热导率计算或高阶力常数刻画”，且核心论证建立在机器势之上。排除标准：仅以成分/结构回归标量 $\kappa_\mathrm{lat}$ 而脱离势函数框架的数据驱动模型（仅在背景处提及 [2]）、纯实验热导测量、以及体相经验势工作。最终纳入 24 条文献，全部经 sciverse 反查确认存在、摘要支撑其核心论断（存在性核验：VERIFIED）。多数为第一性原理+机器势的计算研究、旗舰应用或方法综述；少量为架构奠基论文。证据强度通过正文措辞传达，不在文中另加显式标签。

## 三、分类框架

分类轴的设计遵循互斥且完备（MECE）原则，采用一条**计算路径轴**贯穿全部材料系统，叠加一条**材料维度轴**用于交叉对比：

- **计算路径轴**（两个分支）：
  1. **谱方法**：由 MLIP 计算谐波/非谐力常数 $\rightarrow$ 声子色散与群速度 $\rightarrow$ （三/四声子）散射率 $\rightarrow$ 求解声子 BTE（ShengBTE、phono3py 等）得到 $\kappa_\mathrm{lat}$。MLIP 在此充当“DFT 采样的加速器”。
  2. **直接分子动力学**：由 MLIP 驱动平衡态（Green-Kubo，经热流自相关）或非平衡态（NEMD）MD 获得 $\kappa_\mathrm{lat}$。此路径天然包含全域非谐与实际温域、以及无序/缺陷结构。
- **材料维度轴**（作为分支内部的交叉维度）：二维材料、热电与超低热导、高温/地幔与相变、含缺陷半导体。

两条路径在“声子分辨率 vs 无序/强非谐适用性”上存在明显张力——这正是空位（gap）所在：尚无方法能同时廉价地提供高分辨的声子图像与大尺寸强非谐处理的统一描述（见综合讨论）。

## 四、谱方法路径：MLIP 加速力常数采样与声子 BTE 输运

谱方法的核心是把昂贵的 DFT 力常数采样替换为机器势的一次性建势。其原始动机在 Korotaev 等对 CoSb$_3$ skutterudite 的工作中得到清晰展示 [6]：他们以基于 MTP [3] 的势、在主动学习（active learning）的引导下用**仅仅数百次**量子力学计算构建可靠势，既能复现振动谱，又能同时以声子 BTE 与 Green-Kubo 两种方法得到一致的 $\kappa_\mathrm{lat}$——这确立了“少样本 + 基于力常数输运”这一被后续广泛复用的范式。Ladygin 等随后系统地把 MLIP 融入晶格动力学模拟框架，验证了机器势对声子色散的复现能力 [24]。

Mortazavi 等把这一思路推向多尺度与材料筛选：以 MTP [3]/ShengBTE 的组合，from first principles 地预测石墨烯/硼硼烷异质结与多种二维材料的 $\kappa_\mathrm{lat}$，展示了机器势在不透明构型下仍保持逐次可改进（systematically improvable）的优势 [7]。同一团队在二维材料族上做了批量式的高通量探索 [17]，其成功的关键是 MTP [3] 家族“可系统改进”的性质。

谱方法的真正放大则来自**非谐力常数的机器提取**。Srivastava 与 Jain 证明，用机器学习辅助从 MD 轨迹提取非谐力常数，可将声子热导预测的整体成本降低约一个量级而不牺牲精度 [8]。当超越三阶近似、计入四声子散射时，MLIP 的价值更为突出：Liu 等以 MLP 纳入四声子散射，预测纤锌矿 BAs 具有很高的热导率 [9]；Ouyang 等系统论证了机器势能从 MD 精确刻画高阶非谐性并得到收敛的 $\kappa_\mathrm{lat}$ [10]。

然而谱路径的高声子分辨率是有代价的：它对势的质量、尤其是在长程与四阶乃至更高阶力常数上的真实性高度敏感。Kocabas 等在 MoS$_2$/MoSe$_2$ 上的研究发现，仅依赖三阶近似的机器势会高估热导，而要收敛到实验可比的低热导值必须计入高阶非谐与声子局域化，且结果强烈依赖所选势——这使“高阶非谐性”从精确性提升演化成一个需要小心的校准问题 [11]。

### 表 1. 谱方法路径的代表性工作对比

| 工作 | 势架构 | 力常数阶次 | 求解方式 | 代表体系与要点 |
|---|---|---|---|---|
| Korotaev 2019 [6] | MTP [3] 族 + 主动学习 | 三阶 | 声子 BTE 与 Green-Kubo 直接 MD 双核对 [14] | CoSb$_3$：数百次 DFT 建势，少样本范式的确立 |
| Mortazavi 2020 [7] | MTP [3] | 三阶 | ShengBTE | 石墨烯/硼硼烷异质结：多尺度 first-principles |
| Liu 2021BAs [9] | MLP | 四阶（四声子） | 声子 BTE | 纤锌矿 BAs：四声子压低影响显著 |
| Ouyang 2022 [10] | MLP | 高阶 | MD/声子 BTE | 高阶非谐的精确描述与收敛性论证 |
| Srivastava 2024 [8] | 机器学习力常数 | 非谐 | 声子 BTE | 成本降低约一个数量级的机制化加速 |
| Kocabas 2025 [11] | MLP | 高阶 | 声子 BTE | MoS$_2$/MoSe$_2$：热导上限对势敏感 |

## 五、直接分子动力学路径：Green-Kubo 与无序/强非谐体系

当体系偏离谐波图像——强非谐、非晶、含缺陷、大胞或含强相变——谱方法会遇到采样与振动模式定义的困难，此时直接分子动力学成为更自然的选择。MLIP 在此路径回填了经验势精度不足的短板。

Qian 等是把机器势用于晶态与非晶硅热输运建模的早期代表：一个势即可同时处理晶态与无序构型，跨越了传统上需要两套势的鸿沟 [12]。对非晶体系，Liang 等在非晶 SiO$_2$ 上以 machine-learning MD 系统刻画了温度依赖的热输运机制，把非晶态的低热导与玻璃态行为归因于声子局域化与扩散输运，展示了机器势在“没有独特格点参照”体系中的独特能力 [15]。

对强非谐的输运相关材料，Green-Kubo 直接路线尤为常用。Takeshita 等以人工神经网络（ANN）势 + Green-Kubo 计算 $\beta$-Ag$_2$Se 的 $\kappa_\mathrm{lat}$，捕捉了此热电材料因 Ag 离子迁移带来的复杂非谐 [14]。Lee 等更进一步，采用等变图神经网络（equivariant GNN）势 + Green-Kubo 处理相变材料（PCM），在含无序与液态特征的大尺寸模拟中保留第一性原理级的精度 [13]——这是“图神经网络势 + 直接 MD”在热输运中的典型落地。

直接 MD 路径的代价同样清晰：$\kappa_\mathrm{lat}$ 来自热流自相关的时间统计，对有限尺寸与采样长度敏感，且不再能直接获得单支声子的寿命分解。它的优势在于对无序、缺陷、宽温域与任意非谐的一揽子处理，与谱路径形成互补而非替代。

### 表 2. 直接分子动力学路径的代表性工作对比

| 工作 | 势架构 | 热导途径 | 目标体系与要点 |
|---|---|---|---|
| Qian 2019 [12] | 机器势 | 直接 MD | 晶态+非晶硅：一势两态的跨越 |
| Takeshita 2022 [14] | ANN 势 | Green-Kubo | $\beta$-Ag$_2$Se：强非谐热电材料 |
| Lee 2024 [13] | 等变 GNN 势 | Green-Kubo | 相变材料（含无序/液态）：大尺寸 |
| Liang 2023 [15] | 机器势 | 直接 MD | 非晶 SiO$_2$：温度依赖与玻璃态机制 |

## 六、材料系统谱系：从超高热导到玻璃态低热导的两极

跨两条计算路径，MLIPs 的应用已覆盖两极材料——从接近金刚石体系的高热导到热电所需的超低（乃至玻璃态）热导——以及二维、地幔矿物、相变材料等功能体系。

**二维材料**是该领域最早、也是密度最高的落点。基于 GAP [5] 的 h-BN 单层工作表明，用约 30% 的代表性构型即可得到可靠的热导，且高阶力常数为势的质量提供了比谐波近似更可信的基准 [16]；MTP [3] 在二维材料族上的高通量探索进一步验证了“一势覆盖多构型”的规模化潜力 [17]。

**热电与超低热导材料**追求极低的 $\kappa_\mathrm{lat}$。SnSe 是其中的代表：Liu 等在高温下用机器势刻画其强非谐声子输运 [18]。机器势的另一大用武之地是“玻璃态”超低热导的机理研判——此类体系往往有强四阶非谐或动态失谐阳离子，谱方法难以胜任，Be 化的直接 MD 成为主力。Wang 等以深度势模型预测了兼具延展性与超低 $\kappa_\mathrm{lat}$ 的 Mg-Te-Pb 热电家族 [20]，把“势函数预测 $\rightarrow$ 材料筛选”的链路推向功能设计。

**高温与地幔地球物理**直接受益于“要么贵、要么不准”的缓解。下地幔的温度压力条件使得 DFT 采样与实验都极端困难，Yang 等在 MgSiO$_3$ 钙钛矿与后钙钛矿上以深度势分子动力学（DeePMD）计算晶格热导 [19]，把机器势扩展到了地球科学的高温高压场景。

**含缺陷与相变半导体**是机器势“保真-规模”权衡最能彰显价值的领域之一。Yang 等在 GaN 上考察了点缺陷对 $\kappa_\mathrm{lat}$ 的影响 [21]——这类含无序的结构恰是经验势描述失真、而纯 DFT 又难以规模化的区间。相变材料（PCM）同样受益，Lee 等的等变 GNN 势直接 MD 工作即是把热导预测与可逆相变给合起来的一例 [13]。

### 表 3. 不同材料维度上 MLIP 的适用性与瓶颈

| 材料维度 | 代表体系 | 适用路径 | 主要瓶颈 |
|---|---|---|---|
| 二维 | h-BN [16]、石墨烯/硼硼烷 [7]、MoS$_2$ 族 [11] | 谱方法为主 | 层间长程、大胞采样 |
| 热电/超低热导 | SnSe [18]、$\beta$-Ag$_2$Se [14]、Mg-Te-Pb [20] | 直接 MD 为主 | 强非谐收敛、玻璃态机理 |
| 高温/地幔 | MgSiO$_3$ [19] | 直接 MD | 极端温压下势的迁移适用性 |
| 含缺陷/相变 | GaN 缺陷 [21]、PCM [13] | 直接 MD | 无序构型势的泛化 |

## 七、精度-成本权衡、局限与开放问题

把谱方法与直接 MD 的证据放在一起，一个共同的精度主线浮现：**机器势的“力误差”如何被放大成热导率预测误差**。Zhou 等的工作明确揭示了这种非平凡传播——$\kappa_\mathrm{lat}$ 对力常数施加的噪声放大是非线性的，势在能量/力上的均方误差并不能直接线性推断导热预测的可靠性 [22]。这解释了为什么“架构选择 + 主动学习 + 采样完备性”三个环节都直接决定最终导热结果，也解释了为何高阶非谐体系（如 MoS$_2$/MoSe$_2$ [11]）成为检验势真实性的试金石。

与之相关的是**体系专一副势的主导地位与泛化缺失**：本综述所述的绝大多数成功案例都是“一体系一势”（[6, 13, 21] 等皆然），跨体系的可迁移性缺乏统一基准。Allen 与 Lubbers 提出以元学习（meta-learning）构建跨多个体系的基础化势模型 [23]，其收敛性与算力开销仍是开放问题。此外，热导预测缺少类似分子力学中公认的基准任务与统一误差度规，导致不同架构的报道数值难以直接对比——这一“标准化缺失”正是该领域从“个案演示”走向“可靠工具”的主要障碍。

### 表 4. 两种计算路径的权衡对比

| 维度 | 谱方法（力常数 + 声子 BTE） | 直接 MD（Green-Kubo/NEMD） |
|---|---|---|
| 声子分辨率 | 高，可逐支解耦 | 低，整体统计 |
| 无序/非晶/缺陷适用 | 弱 | 强 |
| 高阶非谐（≥4 阶） | 依赖解析力常数，成本高 | 天然包含 |
| 统计/采样成本 | 低（解析散射率） | 高（长轨迹、尺寸收敛） |
| 强非谐收敛风险 | 高（势质量敏感） | 中（但受噪声限） |
| 典型 MLIP 角色 | DFT 采样加速器 [6, 7, 8] | 保真-规模桥梁 [12, 13, 15] |

## 八、综合讨论

把四至七节的证据串起来，可以得出几个跨分支的判断性结论：

第一，**MLIP 的两个角色并不冲突，而是同一条“保真-规模”曲线的两端**。谱方法把机器势当作 DFT 采样的廉价替代 [6, 7, 8]，换取声子分辨；直接 MD 则用机器势换取无序与强非谐的天然覆盖 [12, 13, 15]。二者的选择本质上是“要声子内部还是不要”的取舍。

第二，**架构差异在热导场景里收敛到共同的结构设计共识**：MTP、NEP、GAP、深度势与等变图神经网络 [3, 4, 5, 19, 13] 都可通过主动学习的高效采样而加强（[6] 确立了这一范式），也都必须面对力误差的非线性放大问题 [22]。换言之，影响 $\kappa_\mathrm{lat}$ 可靠性的，主要不是“选哪个架构”，而是“这个架构在目标体系上把力描述到了多好、采样有没有盖住构型空间”。

第三，**应用正在从“证明可行”转向“功能设计”**：早期工作在已知材料（Si、h-BN、石墨烯）上验证势的质量 [12, 16, 7]，近期则用机器势去预测尚未充分表征的候选（如 Mg-Te-Pb 热电 [20]），把导热预测嵌入材料筛选与发现链路。

## 九、开放问题与未来方向

- **力误差与导热误差的统一度量**：需要建立“势的力误差 $\rightarrow$ $\kappa_\mathrm{lat}$ 误差”的解析或半解析传播模型，作为不同架构、不同采样策略间的可比标尺 [22]。
- **高阶非谐稳定收敛的自动化**：四声子与大 $q$-点四阶力常数在多体系上如何一键化、无人工调参地收敛，仍是工程与理论的双重挑战 [9, 10, 11]。
- **长程相互作用与层间范德华**：二维/多层与异质结构的热输运依赖长程力，机器势对色散相互作用的显式建模仍不成熟 [16, 7]。
- **跨体系泛化与基础化势**：从“一体系一势”到多体系可迁移的基础模型，元学习提供了方向但算力与收敛性待解 [23]。
- **无序/相变/缺陷的一体化标准基准**：目前非晶、PCM、含缺陷体系各自为政，缺乏统一基准以评估并比较直接 MD 路径的势质量 [15, 13, 21]。

## 十、结论

逐条回答引言中的三个 RQ：

- **RQ1（精度-成本收益与路径选择）**：MLIPs 以“一次性建势”把 DFT 量级的非谐力常数采样成本分摊掉，使声子 BTE（谱方法）与 Green-Kubo MD（直接 MD）都能以经验势规模运行于 DFT 量级精度 [6, 12]。谱方法在需要声子分辨与高热导设计时占优 [7, 9]，直接 MD 在强非谐、非晶、缺陷与大胞时占优 [13, 15]，二者互补而非替代。
- **RQ2（架构边界与材料落点）**：MTP/NEP/GAP/深度势/等变 GNN 等架构在热导场景收敛到共同共识——主导成败的是对目标体系力描述的完备性与采样覆盖，而非架构本身 [3, 4, 5, 22]。落点横跨二维、热电/超低热导、地幔高温与相变半导体，呈现从超高热导到玻璃态的热导两极 [16, 18, 19, 13, 20]。
- **RQ3（瓶颈与方向）**：当前最硬的瓶颈是力误差向导热预测的非线性放大 [22] 与“一体系一势”的泛化缺失；高阶非谐收敛、长程与层间相互作用、以及统一的误差与基准标准是三个具体短板。未来方向指向主动学习闭环与基于元学习的基础化势模型 [23]。

## 调研成本

检索视角：主流方法（谱方法/直接 MD）、相邻领域（热电、非晶高温、二维、相变）、方法论（高阶非谐、四声子、力误差）。信息源：sciverse。滚动方式：结构化检索 + 引文网络，滚雪球至检索饱和。纳入 24 篇，全部经 sciverse 存在性反查（VERIFIED）。

## 参考文献

[1] S. Arabha, Z. Shokri Aghbolagh, K. Ghorbani, S. M. Hatam-Lee, A. Rajabpour, “Recent advances in lattice thermal conductivity calculation using machine-learning interatomic potentials,” Journal of Applied Physics, 2021.
[2] Y. Luo, M. Li, H. Yuan, “Predicting lattice thermal conductivity via machine learning: a mini review,” npj Computational Materials, 2023.
[3] A. V. Shapeev, “Moment Tensor Potentials: A Class of Systematically Improvable Interatomic Potentials,” Multiscale Modeling & Simulation, 2016.
[4] Z. Fan, “Improving the accuracy of the neuroevolution machine learning potential for multi-component systems,” Journal of Physics: Condensed Matter, 2022.
[5] A. P. Bartok, M. C. Payne, R. Kondor, G. Csanyi, “Gaussian Approximation Potentials: The Accuracy of Quantum Mechanics, without the Electrons,” Physical Review Letters, 2010.
[6] P. Korotaev, I. I. Novoselov, A. Yanilkin, A. V. Shapeev, “Accessing thermal conductivity of complex compounds by machine learning interatomic potentials,” Physical Review B, 2019.
[7] B. Mortazavi, E. V. Podryabinkin, S. Roche, “Machine-learning interatomic potentials enable first-principles multiscale modeling of lattice thermal conductivity in graphene/borophene heterostructures,” Materials Horizons, 2020.
[8] Y. Srivastava, A. Jain, “Accelerating prediction of phonon thermal conductivity by an order of magnitude through machine learning assisted extraction of anharmonic force constants,” Physical Review B, 2024.
[9] Z. Liu, X. Yang, B. Zhang, “High Thermal Conductivity of Wurtzite Boron Arsenide Predicted by Including Four-Phonon Scattering with Machine Learning Potential,” ACS Applied Materials & Interfaces, 2021.
[10] Y. Ouyang, C. Yu, J. He, “Accurate description of high-order phonon anharmonicity and lattice thermal conductivity from molecular dynamics simulations with machine learning potential,” Physical Review B, 2022.
[11] T. Kocabas, M. Keçeli, T. Gürel, “Thermal conductivity limits of MoS2 and MoSe2: Revisiting high-order anharmonic lattice dynamics with machine learning potentials,” Applied Physics Reviews, 2025.
[12] X. Qian, S. Peng, X. Li, “Thermal conductivity modeling using machine learning potentials: application to crystalline and amorphous silicon,” Materials Today Physics, 2019.
[13] S.-H. Lee, J. Li, V. Olevano, “Equivariant graph neural network interatomic potential for Green-Kubo thermal conductivity in phase change materials,” Physical Review Materials, 2024.
[14] Y. Takeshita, K. Shimamura, S. Fukushima, “Thermal conductivity calculation based on Green-Kubo formula using ANN potential for beta-Ag2Se,” Journal of Physics and Chemistry of Solids, 2022.
[15] T. Liang, P. Ying, K. Xu, “Mechanisms of temperature-dependent thermal transport in amorphous silica from machine-learning molecular dynamics,” Physical Review B, 2023.
[16] Y. Zhang, C. Shen, T. Long, H. Zhang, “Thermal conductivity of h-BN monolayers using machine learning interatomic potential,” Journal of Physics: Condensed Matter, 2021.
[17] B. Mortazavi, E. V. Podryabinkin, I. S. Novikov, “Efficient machine-learning based interatomic potentials for exploring thermal conductivity in two-dimensional materials,” Journal of Physics: Materials, 2020.
[18] H. Liu, X. Qian, H. Bao, “High-temperature phonon transport properties of SnSe from machine-learning interatomic potential,” Journal of Physics: Condensed Matter, 2021.
[19] F. Yang, Q. Zeng, B. Chen, “Lattice Thermal Conductivity of MgSiO3 Perovskite and Post-Perovskite under Lower Mantle Conditions Calculated by Deep Potential Molecular Dynamics,” Chinese Physics Letters, 2022.
[20] X.-X. Wang, Z.-S. Lei, W. Li, “Ductile Mg-Te-Pb thermoelectric materials with ultralow lattice thermal conductivity predicted by a deep learning potential model,” npj Computational Materials, 2026.
[21] J. Yang, Y. Sun, B. Xu, “Impact of point defects on the thermal conductivity of GaN studied using machine-learned potentials,” Physical Review B, 2025.
[22] W. Zhou, N. Liang, X. Wu, “Insight into the effect of force error on the thermal conductivity from machine-learned potentials,” Materials Today Physics, 2024.
[23] A. E. A. Allen, N. Lubbers, “Learning together: Towards foundation models for machine learning interatomic potentials with meta-learning,” npj Computational Materials, 2025.
[24] V. Ladygin, P. Korotaev, A. V. Yanilkin, “Lattice dynamics simulation using machine learning interatomic potentials,” Computational Materials Science, 2020.
