# 证据压缩块（检索阶段）

## 检索视角一：谱维数与随机行走（图/分形基础）
- ✅ [@WireNetwork] Watanabe 1985：用扩散/热核本征态密度定义谱维数；钢丝网络的谱维数独立于局部结构。奠基定义。
- ✅ [@Shi1995] Shi 1995：临界空间维度推广为分形上的临界谱维度，随机行走与相变各有临界谱维数。
- ✅ [@Zhou1992] (Xian Yin Zhou) 1992：预 Sierpinski 垫片所有维度常返，地毯 d=2 常返、d>=3 暂态。
- ✅ [@Zhou1993] 1993：推广 Telcs 定理，厘清随机行走维度/分形维度/电阻维度的关系。
- ✅ [@EdenTree] Nakanishi & Herrmann 1993：Eden 树随机行走谱，检验 d_s=2d_f/d_w 标度关系，有限尺寸 crossover。
- ✅ [@UST] Barlow & Masson 2011：Z^2 均匀生成树谱维数 = 16/13。
- ✅ [@RPM] Gwynne & Miller 2021：随机平面地图谱维数=2，返回概率 n^{-1+o(1)}（UIPT）。
- ✅ [@GFF] Biskup, Ding, Goswami 2019：GFF 驱动行走谱维数=2，返回概率 T^{-1+o(1)}。
- ✅ [@RangeWalk] Okamura 2020：谱维数=2 图上行走范围的强大数律。
- ✅ [@ConformalDim] Sasaya 2022：保形维数与谱维数关系。

## 检索视角二：谱维数与同步（Kuramoto / 可调谱维数几何网络）
- ✅ [@NetGeoSync] Millán, Torres, Bianconi 2019：核心论文。同步相热力学稳定需 d_s>4，相位牵引需 d_s>2；可调谱维数复网络流形上数值测试。
- ✅ [@NGF] Bianconi & Rahmede 2016：Network Geometry with Flavor (NGF)，可调维度 d 的复网络流形，是验证谱维数对动力学作用的模型库。
- ✅ [@NGFHigher] Torres & Bianconi 2020：NGF 单纯复形高阶 Laplacian 的谱维数随阶数增加。
- ✅ [@SpectralVStat] Atay, Bıyıkoğlu, Jost 2006：同步性不能从统计性质推断，只能看谱。
- ✅ [@CoarseGrain] Gfeller & De Los Rios 2008：谱粗粒化保留拉普拉斯动力学。
- ✅ [@KuramotoReview] Rodrigues et al. 2015：复杂网络 Kuramoto 综述。

## 检索视角三：共识动力学与谱隙/图拉普拉斯（共识 ↔ 随机行走慢混合）
- ✅ [@ConsensusRate] Olshevsky & Tsitsiklis 2006：共识收敛速度与分布式平均。
- ✅ [@ConsensusDelay] Bliman, Nedić, Ozdaglar 2008：时滞下共识收敛速率。
- ✅ [@AlgConnEst] Montijano et al. 2017：代数连通度（拉普拉斯第二小特征值）分布式估计。
- ✅ [@AlgConnOpt] He 2019：代数连通度作为共识指数收敛速率的谱隙刻画，加边加速。

## 盲区检查
- 三个子方向各≥3 篇，主观覆盖充分。
- ⚠️ 共识动力学与"谱维数"直连文献偏薄：共识谱分析主流停留在代数连通度（谱隙），把共识与谱维数/慢混合直接挂钩的显式工作相对少——本身即 finding（gap）。以共识↔随机行走↔谱隙的数学桥梁组织成论证。
- ✅ 时效探针：检索到 2019 (NetGeoSync)、2020 (Torres-Bianconi)、2021 (Gwynne-Miller) 等近年工作，谱维数方向近 5 年仍有进展（NGF 高阶、量子网络几何谱维数）。
- ⚠️ 谱维数-同步交叉方向仍以 Bianconi 团队为主，可再补一支独立视角作裁判型对比——以 Atay 谱 vs 统计、Gfeller 粗粒化作为谱方法代表已足够。
