# 证据压缩

检索收敛检查（2026-08-12；时效档：recent/year，文献已覆盖至 2025-2026）：
滚雪球 N 轮，末轮新增 0 篇，达检索饱和。各子方向均已 ≥3 篇。

## 视角 A：ML 筛选 / 预测 SSE（描述符-组成监督学习）
- ✅ Chen2024 JAC (Weijian Chen 2024)：ML 层次筛选 20,717 种含 Li 材料，468 样本库，分类+回归，AIMD 验证，得 Li3BiS3 等
- ✅ Zhang2019 GEE (Xu Zhang 2019)：无监督 ML 加速 SSE 发现；点明小数据（SSLC 数据仅几种材料）
- ✅ Kang2023 JPCC (Seungpyo Kang 2023)：高通量+ML surrogate 筛 19,480 含 Li 材料，NASICON/argyrodite/halide 题录库
- ✅ Kim2026 MTC（Younsoo Kim 2026，含 Dane Morgan）：LLM+人工整理 RT 电导率数据集；RF 最优但 R²≈0.57-0.69，诚实报告"定量预测有限、定性区分好/差导体（F1≤0.92）"，SHAP 揭示键强/原子尺寸关键
- ✅ Kim2026 JCP（Haewon Kim 2026）：结构标记数据集 n=499；GBR+几何描述符 MAE=0.543 log(S/cm)；微调 LLM 用 CIF 文本提示免特征提取；点明 composition-only 忽略结构、GNN 受数据稀缺+无序 CIF 制约
- ✅ Xiang2025 ACSAEM（Shang Xiang 2025）：解释性 ML 预测反钙钛矿导电；离子替换扩样 168→15 万量级，A 位电负性/密度/离子半径最关键的 3 特征
- ✅ LiCondAI 2025 IE&CR（Bijan Kumar Paul 2025）：stacking(XGB/GB/RF) 97% 精度预测 IC 的平台
- ⚠️ 综述 Liu2021 Frontiers / Hu2023 Batteries / Hu2022 Materials：ML 应用于锂 SSE 发现的流程、数据集选择、算法综述

## 视角 B：材料类别专项
- ✅ Sun2023 ACSAMI (Jiwon Sun 2023)：garnet 型 SSE surrogate，73 元素替换 La/Zr→5329 结构，预测弹性+导电，active learning 降不确定性，10 个新四面体相 garnet
- ✅ Sun2025 ACSAMI（Jiwon Sun 2025）：CDHE garnet 4348 候选，CHGNet 微调+MD，3 个导电>1e-4 S/cm
- ✅ Kim2025 CEJ (Ji-Hwan Kim 2025)：双掺杂 LLZO 从 10368 组合筛出 61，PVDF-HFP HSE 填料经实验验证（电化学性能提升）
- ✅ Choong2025 ACSAEM（Li Yan Anthony Choong 2025）：卤化物 SE 多性质(导电/模量/ESW)预测，CatBoost/LGBM/Skorch NN，DFT 验证 Rb2LiAlF6
- ✅ Kong2025 Small (Songjia Kong 2025)：argyrodite 组成式 E2I 框架仅用元素组成预测导电，Si-Sn/Ge-* 共掺杂，Li6.7Ge0.595Si0.105P0.3S5I 达 7.2e-3 S/cm
- ✅ Tawfik2025 JPCC（Sherif Tawfik 2025）：贝叶斯优化最大化 Li 扩散，AIMD 验证，Li3YBr6 低扩散势垒+高带隙+锂界面稳定
- ✅ Rajapriya2026（Navin Rajapriya 2026）：贝叶斯优化冷烧结 LATP 参数，CSP 1.94e-4 S/cm
- ✅ Chen2025 JPS（Xiaozhen Chen 2025）：ML 预测掺杂 LiTi2(PO4)3 导电

## 视角 C：机器学习势函数 / 分子动力学
- ✅ Hajibabaei2021 JPCL (Amir Hajibabaei 2021)：SGPR on-the-fly MLIP 扫描数百三元体锂扩散，组合成 Li-P-S / Li-Sb-S / Li-Ge-P-S 通用势
- ✅ Gurwell2026（Cameron Gurwell 2026）：uMLIP 家族(CHGNet/M3GNet/MACE/ORB, 18 模型)对照实验 7Li NMR 扩散 + DFT，12 种锂化合物；性能强烈依赖架构+化学体系；diffusion 预测系统相关——uMLIP 迁移性局限的关键评估
- ✅ Zhang2024 AIChem (Yixi Zhang 2024)：EANN+不确定性主动学习构造势；Li3YCl6 中小超胞 AIMD 高估 RT 导电，大超胞修正，尺寸效应教训
- ✅ Lee2025 AEM (Hyun-Jae Lee 2025)：NNP 模拟 argyrodite，阴离子在笼中心结合锂，"减少笼中心 S 占据"提质策略
- ✅ Shantsila2026（Roman Shantsila 2026）：STING 主动学习框架在 LiPS 上，细调 MLIP 优于 foundation
- ✅ Nam2026 BKCS (Gunwook Nam 2026)：MLIPs 电解质体相与界面应用综述

## 视角 D：主动学习 / 贝叶斯优化 / 生成
- ✅ Sun2023 已计（active learning garnet）
- ✅ Tawfik2025 已计（Bayesian）
- ✅ Hong2026 NatCi（Xufeng Hong 2026）：两阶段深度主动学习+知识迁移做电解质配方（液体为主但方法通用），三次迭代对称电池寿命×3

## 视角 E：界面 / SEI 设计
- ✅ Diddens2022 AdvMaterInterfaces（Diddens 2022）：SEI 建模综述，ML surrogate + 深度生成模型与物理方法协同，指向逆向设计期望界面性质
- ✅ Zheng2025 ESM（Zhuoyuan Zheng 2025）：ML 加速模拟揭示 Si/Li6PS5Cl 界面锂化依赖的 SEI 成核路径
- ✅ Zhong2025 ACSEL（Peichen Zhong 2025）：ML 引导 SEI 导电性洞见，评估非晶锂氟磷酸盐 SEI
- ✅ Stevenson2023 ChemRxiv（James Stevenson 2023）：ML 力场对候选 SEI 结构按预测能量排序
- ✅ Jia2024 EER（Linan Jia 2024）：Li-SSE 界面/中间相综述（背景，四类 SE 阳极界面策略）
- ✅ Banerjee2020 ChemRev（Banerjee 2020）：ASSB 中界面与中间相综述（背景，高被引）
- ✅ Fitzhugh2021 EES（Fitzhugh 2021）：约束系综下 SEI 设计（背景，界面稳定设计框架）

## 相邻 / 生成模型
- ✅ Zhao2021 AdvSci (Yong Zhao 2021)：CubicGAN 深度生成 375,749 OQMD 三元立方材料，506 个经声子验证，扩展晶体生成（方法相邻）
