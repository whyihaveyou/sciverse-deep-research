# 谱维数如何统摄三类网络动力学：随机行走、同步与共识的低临界维框架

## 关键引用

- [1] Alexander, 1982, "Density of states on fractals: « fractons »"
- [2] Rammal, 1983, "Random walks on fractal structures and percolation clusters"
- [3] Havlin, 1987, "Diffusion in disordered media"
- [4] Burioni, 1996, "Universal Properties of Spectral Dimension"
- [5] Millán, 2019, "Synchronization in network geometries with finite spectral dimension"
- [6] Ódor, 2024, "Frustrated Synchronization of the Kuramoto Model on Complex Networks"
- [7] Qiu, 2025, "Criticality and Universality of Generalized Kuramoto Model"
- [8] Gwynne, 2021, "Random walk on random planar maps: Spectral dimension, resistance and displacement"
- [9] Dimakis, 2010, "Gossip algorithms for distributed signal processing"
- [10] Olshevsky, 2009, "Convergence Speed in Distributed Consensus and Averaging"

## 摘要

谱维数（spectral dimension, $d_s$）由 Laplace 算子谱密度在零频附近的幂律 $\rho(\lambda)\sim\lambda^{d_s/2-1}$ 定义，是刻画分形与复杂网络上扩散与集体动力学的"有效维度"。本综述围绕三个研究问题梳理该概念与三类动力学的关系：随机行走的常返性与均方位移、Kuramoto 同步的临界行为、共识/分布式平均的收敛速率。跨文献对读显示三类动力学共享同一控制参数——低能谱密度，但显式程度不同：随机行走传统上直接以 $d_s$ 表述，同步以两个低临界维 $d_s=2$（相位卷入）与 $d_s=4$（同步相热力学稳定）为框架，共识则隐式地由谱隙 $\lambda_2$ 受 $d_s$ 约束。综合给出统一视角：$d_s$ 是决定这三类动力学普适类与临界定标的共同源头。

## 核心要点

- **要点 1**：谱维数 $d_s$ 是比欧氏维、Hausdorff 维更贴合动力学的有效维度——它通过谱密度 $\rho(\lambda)\sim\lambda^{d_s/2-1}$ 同时控制随机行走返回概率、热扩张与集体相变的定标，且 Burioni-Cassi 证明它对有限尺度拓扑具有几何普适性（不随粗粒化等细节改变）[1, 2, 4]。
- **要点 2**：随机行走的所有关键量都挂在 $d_s$ 上：返回概率 $P(0,t)\sim t^{-d_s/2}$ 在 $d_s=2$ 处分出常返/暂态，紧凑访问数 $S_N\sim N^{d_s/2}$（$d_s\le 2$）；渗流团簇处 Alexander-Orbach 猜想给出 $d_s=4/3$ 的"超普适"值，但其适用范围仅限齐次分形 [1, 2, 11]。
- **要点 3**：网络同步存在与磁体相变对应的两个低临界维——相位卷入需 $d_s>2$（Mermin-Wagner 型下临界维），同步相热力学稳定需 $d_s>4$（上临界维）；数值与重整化群证据支持此框架，并延伸出 $d_s>4$ 时平均场定标与受阻同步 [5, 6, 12]。
- **要点 4**：共识动力学没有相变，但其收敛时间由 Laplacian 谱隙 $\lambda_2$ 决定，而 $\lambda_2$ 对多项式增长图类以 $\lambda_2\sim N^{-2/d_s}$ 标度——共识时间在谱维数可调图上应随 $d_s$ 变化，这一连接在现有文献中多为隐性 [10, 9, 13]。
- **要点 5**：主要开放问题在共识分支——尚无工作在谱维数可调的分形网络上直接测量共识收敛时间与 $d_s$ 的标度关系；这恰好是三类动力学中可设计实验裁决的关键空白。

## 一、引言

### 为什么需要这篇综述

复杂网络动力学的研究长期分为两支：一支关心"扩散怎么走"（随机行走、混合时间），一支关心"集体态怎么形成"（同步、共识）。二者的控制器是同一个对象——网络 Laplacian 的本征谱，而谱维数正是从谱密度中提取的、把"维度"这个概念推广到非平移不变网络上的自然量 [1, 2]。已有综述多分领域展开（扩散落在无序介质物理学，同步落在非线性动力学，共识落在分布式控制），缺少一条把三类动力学横着贯通的线索。本文以一个贯穿性视角综述：谱维数如何同时决定随机行走的常返、Kuramoto 同步的临界维、以及共识收敛的速率——并指出三者在"低能谱密度是共同控制器"这一点上的统一性与其显式程度的差异。

### 研究问题

- RQ1: 谱维数 $d_s$ 如何通过谱密度决定图/网络上随机行走的常返性（Pólya 型判据 $d_s=2$）与均方位移/紧凑访问？
- RQ2: $d_s$ 如何刻画网络结构并调控 Kuramoto 同步的临界耦合与临界普适类（$d_s=2$ 卷入、$d_s=4$ 热力学稳定）？
- RQ3: 是否存在把随机行走、同步、共识三类动力学联系起来的统一低临界维框架，且共识如何隐性地受 $d_s$ 约束？

### 本文组织方式

本文先界定谱维数并给出其普适性地位（第四节），随后三个分支分别综述它如何控制随机行走（第五节）、同步（第六节）、共识（第七节）；第八节做跨分支综合，识别 $d_s=2$ 与 $d_s=4$ 的统一框架与分歧；第九节列出开放问题；第十节逐条回答三个 RQ。

## 二、研究方法

检索经 sciverse MCP（`search_papers` 结构化检索、`semantic_search` 语义检索、`list_paper_relations` 引文反查），辅以 Crossref API 题目录核验。按三个子方向组织检索视角：

- 随机行走视角：关键词族 "spectral dimension"、"random walk"、"recurrence"、"Alexander-Orbach"（[11]）、"fracton dimension"、"percolation"；时间窗口跨 1982（奠基）至 2021（随机平面图谱维数序贯解析）。
- 同步视角：关键词族 "spectral dimension"、"synchronization"、"Kuramoto"、"critical dimension"、"fractal network"；覆盖 2019-2026 最新进展（含重整化群与非互易推广）。
- 共识视角：关键词族 "consensus"、"convergence rate"、"spectral gap"、"distributed averaging"、"mixing time"；覆盖 2009-2015 奠基与控制论结果。

以 Millán 2019 为种子做一轮引文反查（REFERENCES），确认关键谱维数文献已入池。纳入标准：研究对象的动力学显式或隐含地由谱维数/谱密度控制，且出处可核验。最终纳入 19 篇文献，全部完成存在性核验；其中 1 篇（Havlin & ben-Avraham 综述）经 Crossref 逐条核对卷期页码。检索收敛声明：滚雪球 1 轮，末轮新增 0 篇，达检索饱和；时效探针已打（纳入 2024-2026 最新工作）。分类框架按"定义与普适性 / 随机行走 / 同步 / 共识"四轴设计，轴间互斥、覆盖三类动力学且各回答 RQ 一部分。

## 三、分类框架

本综述的分类轴是"谱维数介入动力学的方式"，四个分支互斥且覆盖研究问题：

表 1：分类轴按谱维数介入动力学的方式划分——随机行走与同步显式使用 $d_s$，共识隐性受谱隙约束

| 分支 | 谱维数介入方式 | 回答的 RQ | 该分支的空格（= gap） |
|---|---|---|---|
| 四、定义与普适性 | $d_s$ 作为有效维数、几何普适性 | RQ1/RQ3 概念基础 | 多量子引力降维观测属跨界复用，未入综述主体 |
| 五、随机行走 | 显式 $d_s$：返回概率、紧凑访问、AO 猜想 | RQ1 | 非齐次分形的普适谱维理论缺失 |
| 六、同步 | 显式 $d_s$：临界维 $d_s=2,4$、受阻同步 | RQ2 | $d_s\in(2,4)$ 区间的精确临界行为 |
| 七、共识 | 隐性 $d_s$：收敛时间受谱隙约束 | RQ3 | 分形网络上共识时间 vs $d_s$ 的直接测量空白 |

该分类轴本身反映一个结构性事实：随机行走与同步的文献把谱维数当作显式计算对象，而共识文献几乎不援引 $d_s$，只在谱隙 $\lambda_2$ 的层面隐性地受其约束 [1, 5, 10]。这三类动力学落在同一张轴上、显式程度不同，正是第八节综合讨论要处理的张力。

## 四、谱维数：定义、由来与普适性

谱维数的概念源自两类独立动机。其一是振动/扩散理论：Alexander & Orbach 在研究分形的态密度时证明，若扩散常数随距离按 $\delta$ 指数衰减，则模式计数需要一个新的"fracton 维数" $\bar{d}=2d_f/d_w$（$d_f$ 为分形维、$d_w$ 为随机行走维），对渗流团簇数值上约等于 $4/3$，且与欧氏维数 $d$ 无关 [1]。其二是随机行走理论：Rammal & Toulouse 定义自相似结构上的"谱维数"，并证明随机行走的闭合回路概率与访问格点数都被它控制 [2]。这两种表述在低能谱密度处汇合：对 Laplace 算子，若零频附近谱密度 $\rho(\lambda)\sim\lambda^{d_s/2-1}$，则当时间趋于无穷时返回概率 $P(0,t)\sim t^{-d_s/2}$ [2]。

谱维数之所以成为"有效维度"，关键性质由 Burioni & Cassi 奠定：在多数含欧氏维数 $d$ 的定律中，$d_s$ 精确取代 $d$——谐波振荡谱、随机行走平均自相关、球模型临界指数、低温比热、广义 Mermin-Wagner 定理、Gaussian 模型红外奇异性等皆然 [4, 3]。更本质地，他们证明 $d_s$ 对所有只改动有限尺度拓扑的几何变换不变（拟等距、粗粒化、加有限程耦合），即具有"几何普适性"，并对分形树给出解析计算 [4, 14]。这解释了为何 $d_s$ 对"哪条走法、哪种耦合"不敏感，从而适合刻画由复杂网络承载的普适类。

对随机行走力学本身，谱维口袋"传统上不齐"须提醒：Alexander-Orbach 猜想认为渗流阈值处 $d_s=4/3$ 具超普适性，但其适用范围仅限齐次分形与 Cayley 树这类结构；对渗流主干、Sierpinski gasket 等非齐次结构并不必然成立 [11]。这一边界的意义在于：$d_s$ 虽是强普适量，却非万能——它在守恒量/结构齐次的体系里普适，在结构异质处会退化为依赖具体构造的值。

## 五、谱维数与随机行走

随机行走是谱维数最直接、最成熟的应用场景，几乎所有经典量都由 $d_s$ 单一参数定标。返回概率 $P(0,t)\sim t^{-d_s/2}$ 直接给出 Pólya 型判据：$d_s>2$ 时随机行走暂态（transient），$d_s\le 2$ 时常返（recurrent）——这与欧氏空间中 $d>2$ 暂态、$d\le2$ 常返的经典结论同构，只是把欧氏维换成了谱维 [2, 3]。均方位移与"紧凑访问"同样挂在 $d_s$ 上：当 $d_s\le2$ 时随机行走呈紧凑访问，n 步访问的不同格点数 $S_N\sim n^{d_s/2}$ [2]。这些定标在 1984 年即被渗流团簇数值模拟确认：阈值处观测到 $d_s=4/3$ 的超普适行为以及分形到欧氏的交叉 [15]。

现代工作在两个方向深化这条线索。其一是把谱维、随机行走维与电阻维（Telcs 关系）统一为可解析的关系——Zhou 将 Telcs 关于无穷图随机行走维/分形维/电阻维关系的定理推广至更广图类，为"谱维由电阻几何决定"提供数学地基 [16]。其二是把谱维从确定性分形推进到随机结构与真实网络。Gwynne & Miller 证明一大类随机平面图（UIPT、mated-CRT 图等）的谱维数几乎必然等于 2，返回概率 $n^{-1+o(1)}$，并给出位移与电阻的精确量级——这为"随机几何下谱维仍取普适值"提供了序贯证据 [8]。在真实网络中，Lechman 等人对三维 jammed 接触网络做经验随机行走，谱密度给出谱维数 3，与有序欧氏结构相近，但特征向量统计暴露出拓扑与几何无序的可区分性 [17]。

综合言之，随机行走分支给出一幅高度自洽的图像：$d_s$ 是从谱到动力学的直接桥梁，其普适值出现在齐次/自相似结构（4/3 于渗流、2 于随机平面图、$d$ 于欧氏格），非齐次结构则偏离普适值——这个谱维"何时普适、何时不能"的边界，正是连接后面同步临界维讨论的关键线索。

## 六、谱维数与同步

同步方向是近五年谱维数研究最活跃的前沿，核心进展是把"同步临界维"与磁体相变的临界维框架精确对接。Millán、Torres 与 Bianconi 在可调谱维数的 complex network manifolds 上研究 Kuramoto 模型，确立了谱维数的两个决定性阈值：相位卷入（phase entrainment，序参量非零）要求 $d_s>2$；同步相的热力学稳定（无限体积下存在稳定的部分同步态）要求 $d_s>4$ [5]。这两个阈值与平衡态磁体完全平行——$d_s=2$ 对应 Mermin-Wagner 型下临界维（$d\le2$ 无长程序），$d_s=4$ 对应上临界维（$d>4$ 转平均场定标）——但把角色从欧氏维换成了谱维。

这条普适框架得到三方面独立证据的支撑。第一，Ódor、Deng 与 Kelling 在极大图上做局域耦合 Kuramoto 临界性研究，比较正则格与带幂律长链接的异质网络（后者谱维 $d_s>4$）：正则 $d=5$ 网络呈平均场型临界且带强定标修正，$d=4$ 有对数修正，而高谱维异质网络呈现非平均场的 smeared 相变与震荡修正，归因于类似 Griffiths 效应的受阻同步——即"高 $d_s$"不再自动保证平均场，网络异质性本身成为相关扰动 [6]。第二，Bae & Kori 用动力学重整化群将"谱维数决定临界性"推进到非互易（带相位滞后的 Kuramoto-Sakaguchi）情形，数值相图与解析定标吻合 [12]。第三，对高阶/多维 Kuramoto 普适类的追问引向一个值得注意的衔接点：Qiu 等人对偶 $D$ 维广义 Kuramoto 的自洽方程展开给出普适临界指数 $\beta=1/2$、$\bar{\nu}=5/2$ 与非寻常上临界维 $d_u=5$，并把临界普适类刻画为"$D$ 无关、$d$ 相关" [7]——这提示物理空间维 $d$ 与谱维 $d_s$ 何者主导临界相变，仍有待系统对照。

表 2：同步分支四工作共享"几何决定临界维"的结论，但在谱维与欧氏维何者主导、以及高 $d_s$ 是否保证平均场上出现分歧——后者构成第六、第八节的张力点

| 工作 | 结构 | 谱维阈值/定标 | 关键结论 |
|---|---|---|---|
| Millán et al. 2019 [5] | complex network manifolds（可调 $d_s$） | 卷入 $d_s>2$、同步相稳定 $d_s>4$ | 谱维数决定 Kuramoto 临界维 |
| Ódor et al. 2024 [6] | 正则格 + 幂律长链异质网络 | $d_s>4$ 非平均场 | 网络异质性导致受阻/ Griffiths 型同步 |
| Bae & Kori 2026 [12] | 带相位滞后非互易振荡器 | 谱维数决定临界 $d_s$ | dRG 解析支持 |
| Qiu et al. 2025 [7] | 偶 $D$ 广义 Kuramoto | 上临界维 $d_u=5$ | $\beta=1/2$、$\bar{\nu}=5/2$，$D$ 无关 |

## 七、谱维数与共识动力学

共识/分布式平均与随机行走共享同一线性代数内核：线性共识迭代 $x(t+1)=Wx(t)$ 的谱分解使偏差按特征值收缩，收敛速率由第二大特征值亦即 Laplacian 谱隙 $\lambda_2$ 决定 [10, 9]。Olshevsky & Tsitsiklis 系统证明了线性时不变分布式共识算法最坏情形收敛时间的下界，把收敛复杂度与谱结构直接挂钩 [10]。

共识与谱维数的连接在于谱隙对网络尺寸的标度：对多项式增长的 $d_s$ 维图类，Laplacian 低能本征值按 $\lambda_k\sim(k/N)^{2/d_s}$ 分布，谱隙 $\lambda_2\sim N^{-2/d_s}$——这正是 Weyl 律在离散图上的形态，也即谱密度定义 $d_s$ 的直接推论。与此同时，gossip/随机使用者平均算法的平均时间与随机行走混合时间成比例（约混合时间 × n），而混合时间由谱隙控制 [9]。因此共识收敛时间、随机行走混合时间与 $d_s$ 三者被同一条谱隙链锁在一起：$d_s$ 越大（有效维度越高），谱隙退化越慢、混合与共识越快；$d_s\le2$ 时谱隙随 $N$ 退化更快，收敛显著变慢。Estrada 等人从真实网络出发验证了这一控制链，显示共识时间主要由 Laplacian 代数连通性（谱隙）与等周数决定，移除关键边可显著拖慢共识 [13]。Patterson 等则把分析推广到随机链路失效情形，用谱表示刻画收敛速率的二阶统计 [18]。

值得强调的量化差距：共识文献几乎从不显式引用"谱维数"一词，而是停留在谱隙 $\lambda_2$。这使得共识分支成为三类动力学中谱维数连接最"隐性"的一支——其理论内核（谱隙标度）隐含由 $d_s$ 决定，但缺少像同步分支那样的直接对标研究。这也正是第九节开放问题中的头号空白。

## 八、综合讨论：$d_s=2$ 与 $d_s=4$ 的统一框架

把三个分支并置，能看出一个被单分支观察掩盖的统一图景：谱密度 $\rho(\lambda)\sim\lambda^{d_s/2-1}$ 的低能行为同时是三类动力学的"控制器"。

第一，$d_s=2$ 是三支共用的最低临界维。随机行走在 $d_s=2$ 处分常返/暂态；同步在 $d_s=2$ 处决定相位卷入能否存在（Mermin-Wagner 型下临界维）[2, 5]。把临界判据从欧氏维推广到谱维的合法性，早在"分形上临界谱维数是欧氏临界空间维之直接推广"的早期提法中即已确立 [19]。共识虽无相变，但 $d_s=2$ 是谱密度在低能端的权重大小发生质变的分界——$d_s\le2$ 时低能态密度相对增强、谱隙退化显著加快，共识与混合明显拖缓 [9]。三者共享"$d_s=2$ 是低维/高维行为分野"这一判据。

第二，$d_s=4$ 是上临界维。同步相在 $d_s>4$ 才可能热力学稳定，$d_s>4$ 时（对结构充分齐次的网络）呈现平均场定标 [5, 6]。随机行走与共识无此相变型上临界维，但 $d_s=4$ 同样标记了谱密度低能权重"稀疏化"的转折点。因此可把 $d_s=2$、$d_s=4$ 视为普适的"维度窗户"：$d_s\le2$ 时集体长程序与扩散可达性最脆弱，$d_s>4$ 时集体态趋于自平均。

第三点也是最重要的一点张力来自异质性。同步分支的最新证据表明，$d_s>4$ 并不必然意味着平均场：网络异质性（长程链接、模结构）会在高 $d_s$ 下引入非平均场的受阻同步与 Griffiths 型效应 [6]。这与随机行走分支 Alexander-Orbach 猜想仅对齐次分形成立的限制遥相呼应 [11]。二者共同指向一条可检验的判断：谱维数是描述齐次/自相似结构动力学普适类的充分量，但在结构异质处，$d_s$ 必须辅以异质性（如长程权重、模块度）才能预言动力学。这条边界正是把"谱维数决定动力学"从格言升级为严格框架的缺口所在。

分歧裁决：同步分支内部"高 $d_s$ 是否保证平均场"存在分歧（[5] 在齐次网络支持平均场、[6] 在异质网络反对）。裁决程序的三个合法结局里，这里落入"有条件立场 + 证据缺口"的复合：调节变量是结构齐次性，但入选文献缺少在同一网络模型上系统扫描 $d_s\in(2,4)$ 与异质性强度的系统设计，故条件化结论只能做定性裁决，定量裁决留待空白填补（见第九节）。

## 九、开放问题与未来方向

- **共识时间 vs $d_s$ 的直接标度测量（最高杠杆空白）**：分类框架第七节是空格——现有共识文献停留在谱隙层面，尚无工作在谱维数可调的分形/复杂网络流形上直接测量共识收敛时间与 $d_s$ 的标度（预期 $\lambda_2\sim N^{-2/d_s}$ 给出 $T\sim N^{2/d_s}$ 型依赖）[9, 5]。这一实验可裁决"共识隐性受 $d_s$ 约束"的推断，是成本最低、信息量最大的下一步。
- **$d_s\in(2,4)$ 区间的精确临界行为**：同步在 $d_s\le2$（无卷入）与 $d_s>4$（平均场）两端有清晰画像，但 $2<d_s<4$ 的准长程序/部分卷入行为的普适类尚无定论 [5, 6]。
- **谱维与欧氏维何者主导临界普适类**：Qiu 等给出的偶 $D$ 广义 Kuramoto 上临界维 $d_u=5$ 与 $D$ 无关、$d$ 相关的普适性，与谱维数框架的"几何决定论"如何自洽，需要把 $d_u$ 表达式推广到谱维语境并系统对照 [7, 4]。
- **非齐次结构的普适谱维理论**：随机行走与同步两分支都警示非齐次结构会使谱维"普适值"失效 [11, 6]，但缺少统一的"谱维 + 异质性序参量"双参量有效理论。
- **量子引力降维观测的跨界对照**：谱维数在 Horava-Lifshitz 引力、因变量重原子化（CDT）等领域被用作"时空维度随尺度变化"的观测，与网络同步里的静态谱维是同一概念的两个使用方向，其方法论互鉴尚有空间（该方向未纳入本综述主体，已在检索时探明）。

## 十、结论

RQ1 的回答：谱维数通过谱密度直接控制随机行走——返回概率 $P(0,t)\sim t^{-d_s/2}$ 在 $d_s=2$ 处给出 Pólya 型常返/暂态判据，紧凑访问数 $S_N\sim n^{d_s/2}$（$d_s\le2$），渗流团簇呈超普适 $d_s=4/3$，该普适性仅对齐次分形成立 [2, 15, 11]。

RQ2 的回答：谱维数刻画网络几何并决定 Kuramoto 同步临界维——相位卷入需 $d_s>2$，同步相热力学稳定需 $d_s>4$；该双阈值由 complex network manifolds 数值与重整化群证据支持，并延伸出 $d_s>4$ 时平均场定标、$d<4$ 时对数修正、异质网络高 $d_s$ 时受阻同步的图景 [5, 6, 12]。

RQ3 的回答：存在以低能谱密度为共同控制器的统一框架，低临界维 $d_s=2$（常返/卷入/谱隙退化变快）与上临界维 $d_s=4$（平均场/自平均）贯穿随机行走、同步与共识；其中共识通过谱隙 $\lambda_2\sim N^{-2/d_s}$ 隐性地受 $d_s$ 约束，是三类动力学中谱维数连接最隐性、也最有待直接验证的一支 [10, 9, 13]。

本综述的核心贡献在于把散落于无序介质物理、非线性动力学与分布式控制三支的"谱维数"线索收束为一根纵轴：三类看似无关的动力学因共享低能谱密度而共享临界维判据与标度律，其分歧点集中于结构异质性如何修正这个理想框架——这一张力既解释了谱维数长期被三方独立使用的现象，也指明了未来最有价值的统一化与验证方向。

## 十一、调研成本

- 总检索调用次数：12（`search_papers` ×10、`semantic_search` ×1、`list_paper_relations` ×1）+ Crossref 题目录核验 2 次
- 入选并纳入台账的文献数：19
- 核验通过率：19/19（全部经 sciverse 返回核验存在性；1 篇综述经 Crossref 逐条核对卷期页码；无灰区条目）
- 检索轮次 / 滚雪球轮次：初始 3 视角 + 4 次定向/补搜 = 约 7 轮检索；滚雪球 1 轮，末轮新增 0 篇
- wall-clock 用时：环境未精确记录（估算约 25-35 分钟）
- 估计总 token 数：环境未记录（检索返回 + 综合写作合计，粗估约 6-8 万）

## 参考文献

[1] Alexander S, Orbach R, "Density of states on fractals: « fractons »," Journal de Physique Lettres, 1982.
[2] Rammal R, Toulouse G, "Random walks on fractal structures and percolation clusters," Journal de Physique Lettres, 1983.
[3] Havlin S, ben-Avraham D, "Diffusion in disordered media," Advances in Physics, 1987.
[4] Burioni R, Cassi D, "Universal Properties of Spectral Dimension," Physical Review Letters, 1996.
[5] Millán AP, Torres JJ, Bianconi G, "Synchronization in network geometries with finite spectral dimension," Physical Review E, 2019.
[6] Ódor G, Deng S, Kelling J, "Frustrated Synchronization of the Kuramoto Model on Complex Networks," Entropy, 2024.
[7] Qiu Z, Wu TC, Fang S, Meng J, Fan J, "Criticality and Universality of Generalized Kuramoto Model," arXiv preprint, 2025.
[8] Gwynne E, Miller J, "Random walk on random planar maps: Spectral dimension, resistance and displacement," Annals of Probability, 2021.
[9] Dimakis AG, Kar S, Moura JMF, Rabbat MG, Scaglione A, "Gossip algorithms for distributed signal processing," Proceedings of the IEEE, 2010.
[10] Olshevsky A, Tsitsiklis JN, "Convergence Speed in Distributed Consensus and Averaging," SIAM Journal on Control and Optimization, 2009.
[11] Leyvraz F, Stanley HE, "To What Class of Fractals Does the Alexander-Orbach Conjecture Apply?," Physical Review Letters, 1983.
[12] Bae M, Kori H, "Spectral dimension determines criticality in nonreciprocal phase oscillators," arXiv preprint, 2026.
[13] Estrada E, Vargas-Estrada E, Ando H, "Communicability angles reveal critical edges for network consensus dynamics," Physical Review E, 2015.
[14] Burioni R, Cassi D, "Spectral dimension of fractal trees," Physical Review E, 1995.
[15] Argyrakis P, Kopelman R, "Random walk on percolation clusters," Physical Review B, 1984.
[16] Zhou XY, "Resistance dimension, random walk dimension and fractal dimension," Journal of Theoretical Probability, 1993.
[17] Lechman JB, Bond S, Bolintineanu D, Grest GS, Yarrington C, Silbert LE, "Random walks on jammed networks: Spectral properties," Physical Review E, 2019.
[18] Patterson S, Bamieh B, El Abbadi A, "Convergence Rates of Distributed Average Consensus With Stochastic Link Failures," IEEE Transactions on Automatic Control, 2010.
[19] Shi Y, "Critical spectral dimensionalities of random walks and phase transitions on fractals," Journal of Physics A: Mathematical and General, 1995.
