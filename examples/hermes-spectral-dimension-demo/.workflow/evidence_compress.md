# 证据压缩 · 检索阶段

检索日期：2026-08-13 (CST)。检索视角：SP1 随机行走 / SP2 同步 / SP3 共识。滚雪球：以 Millán 2019 为种子反查 REFERENCES，确认关键谱维数文献已入池。

## SP1 随机行走
- ✅ [@AlexanderOrbach] Alexander & Orbach 1982, "Density of states on fractals: fractons", J. Physique Lettres。密度泛函 d̄ = 2d/(2+θ) = 2d_f/d_w；渗流 d̄=4/3。顶1%，2084被引。存在性 VERIFIED（工具返回）。
- ✅ [@RammalToulouse] Rammal & Toulouse 1983, "Random walks on fractal structures and percolation clusters", J. Physique Lettres。引入谱维数并推导 Sierpinski gasket 之值；随机行走紧凑访问 S_N ~ N^{2/3} 于渗流阈值。965被引。
- ✅ [@LeyvrazStanley] Leyvraz & Stanley 1983, PRL "To What Class of Fractals Does the Alexander-Orbach Conjecture Apply?"。AO 猜想对"齐次"分形成立（严格于 Cayley 树），对非齐次（渗流主干、Sierpinski gasket）不必成立。
- ✅ [@ArgyrakisKopelman] Argyrakis & Kopelman 1984, PRB "Random walk on percolation clusters"。模拟确认 2D/3D 阈值处 S_N 超普适、fracton 谱维 4/3；含 fractal→Euclidean 交叉。
- ✅ [@HavlinBenAvraham] Havlin & ben-Avraham 1987, Adv. Phys. "Diffusion in disordered media"。经典综述；Crossref 已核验 Adv. Phys. 36:695-798 (1987), DOI 10.1080/00018738700101072。
- ✅ [@YuShi1995] Yu Shi 1995, J. Phys. A "Critical spectral dimensionalities of random walks and phase transitions on fractals"。分形上存在多个临界谱维数，为欧氏空间临界空间维的直接推广。
- ✅ [@BurioniCassi] Burioni & Cassi 1996, PRL "Universal Properties of Spectral Dimension"。谱维数精确取代欧氏维数于多数含维数律；对有限尺度拓扑不变（几何普适性）；证明 diffusive 与 vibrational 谱维可能不重合。
- ✅ [@BurioniCassi1995] Burioni & Cassi 1995, PRE "Spectral dimension of fractal trees"。分形树谱维数解析计算（非反常扩散 NT_D 树）。
- ✅ [@GwynneMiller] Gwynne & Miller 2021, Ann. Probab. "Random walk on random planar maps"。UIPT/随机平面图谱维数 a.s.=2，返回概率 n^{-1+o(1)}；resistance/displacement 界。
- ✅ [@Zhou1993] Zhou 1993, J. Theoret. Probab. "Resistance dimension, random walk dimension and fractal dimension"。Telcs 关系推广：电阻维/随机行走维/分形维。含 alpha 版本。
- ✅ [@LechmanSpectra] Lechman et al 2019, PRE "Random walks on jammed networks: Spectral properties"。jammed 接触网络经验谱密度给出谱维数 3，类欧氏但特征向量有差异（拓扑 vs 几何无序）。

## SP2 同步
- ✅ [@MillanBianconi] Millán, Torres & Bianconi 2019, PRE "Synchronization in network geometries with finite spectral dimension"。**核心**：Kuramoto 同步相态仅当 d_s>4 热力学稳定；相位卷入仅 d_s>2。用 complex network manifolds（可调 d_s）数值验证。顶1%。
- ✅ [@BaeKori] Bae & Kori 2026, arXiv "Spectral dimension determines criticality in nonreciprocal phase oscillators"。非互易 Kuramoto-Sakaguchi；谱维数决定临界性（dRG 分析）。预印本。
- ✅ [@Odor2024] Ódor, Deng & Kelling 2024, Entropy "Frustrated Synchronization of the Kuramoto Model on Complex Networks"。d_s>4 谱维：d=5 平均场、d=4 对数修正；ll 网络高 d_s 时 smeared/非平均场、震荡修正、Griffiths 型受阻同步。
- ✅ [@Qiu2025] Qiu, Wu, Fang, Meng & Fan 2025, arXiv "Criticality and Universality of Generalized Kuramoto Model"。偶 D 广义 Kuramoto：β=1/2, ν̄=5/2，非寻常上临界维 d_u=5；局域耦合用自旋波。用户本人工作。预印本。

## SP3 共识
- ✅ [@OlshevskyTsitsiklis] Olshevsky & Tsitsiklis 2009, SIAM J. Control Optim. "Convergence Speed in Distributed Consensus and Averaging"。线性时不变共识算法最坏情况收敛时间下界，与谱隙相关。567被引。
- ✅ [@DimakisGossip] Dimakis, Kar, Moura, Rabbat, Scaglione 2010, Proc. IEEE "Gossip algorithms for distributed signal processing"。gossip 平均时间 ≈ 随机行走混合时间 × n，由谱隙 1-λ_2 控制。
- ✅ [@Patterson2010] Patterson, Bamieh & El Abbadi 2010, IEEE TAC "Convergence Rates of Distributed Average Consensus With Stochastic Link Failures"。随机链路失效下共识收敛速率（二阶矩递归、谱表示）。
- ✅ [@EstradaConsensus] Estrada, Vargas-Estrada & Ando 2015, PRE "Communicability angles reveal critical edges for network consensus dynamics"。共识时间由 Laplacian 代数连通性与等周数控制；真实网络平均共识时间~连通性缺失敏感。

## 盲区检查
- 三类子方向均 ≥3 篇，无整方向空白。
- 时效探针：已含 2024 (Ódor)、2025 (Qiu)、2026 (Bae & Kori) 最新进展，覆盖"近 3 年"档。
- ⚠️ 潜在盲区：共识方向直接显式引用"谱维数"的文献稀少——共识文献多以谱隙 λ_2 表述，隐含受谱维约束。这本身即 finding（见综合讨论）。已用 semantic_search 补查 consensus+mixing time+spectral gap，确认 Dimakis/Estrada/Becchetti 等锚点。
- ❌ 未采用：量子引力领域谱维数观测（Lifshitz 点谱维、branched polymer）——跨领域、非本综述三类动力学内核，记入开放问题一笔带过，不入账。

## 检索收敛声明
滚雪球 1 轮（Millán REFERENCES）新增 0 篇入选；三个子方向 ≥3 篇；时效档已探。has_enough_context_for_synthesis = TRUE。
