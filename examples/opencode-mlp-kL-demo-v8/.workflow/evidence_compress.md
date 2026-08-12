# 证据压缩块

## 检索视角与关键词

话题：机器学习势函数（MLIP）在晶格热导率 $\kappa_L$ 预测中的应用。信息源：仅 sciverse（MCP）。

- 视角 A（方法体系/奠基）：`machine learning interatomic potential lattice thermal conductivity phonon`；`moment tensor potential / snapshot / neuroevolution potential`
- 视角 B（精度-成本权衡/求解器）：`phonon Boltzmann transport equation anharmonicity three-phonon`；`Green-Kubo / NEMD 全阶非谐性`
- 视角 C（瓶颈/长程/各向异性）：`layered van der Waals anisotropic MLIP`、`GAP h-BN`
- 视角 D（高阶非谐性/四声子）：`four-phonon scattering high-order anharmonicity`、`wave-like tunneling / Wigner`
- 视角 E（批评/失效/微调）：`MLIP accuracy phonon imaginary modes force error`、`phonon fine-tuning PFT`
- 视角 F（综述/高吞吐/可解释）：`review ML thermal transport`、`two-stage interpretable / PINK`

## 逐文献证据标记

- ✅ [@Qian2019] NNP 同时建模晶体与非晶硅热导；奠基性（Materials Today Physics）
- ✅ [@Mortazavi2020] MTP 多尺度首证，graphene/borophene 异质结构 MT 热导，DFT 级 vs MD 成本
- ✅ [@Podryabinkin2020] MTP 获取 2D 材料声子弥散/热导
- ✅ [@Mortazavi2020efficient] MTP2D 热导、主动学习
- ✅ [@Choi2022] NNP 加速三声子 $\boldsymbol{\kappa}_L$ 计算（Comput. Mater. Sci.）
- ✅ [@Ouyang2022] MLP+EMD 捕获全阶非谐性：dBTE(三声子) 高估 BAs，EMD 与实验吻合——关键证据
- ✅ [@Liu2021SnSe] MTP+EMD，SnSe 全温区 $\boldsymbol{\kappa}$ 张量、四声子作用
- ✅ [@Verdi2021] on-the-fly MLFF（贝叶斯），zirconia 相变+Green-Kubo 全阶
- ✅ [@Wang2023aSi] NEP 大尺度非晶硅、量子修正、尺寸/淬火速率收敛
- ✅ [@Cao2025metals] 统一 NEP 16 元素金属热导（NEMD/HNEMD）
- ✅ [@You2024] MLP+三/四声子+波状隧穿，Mg2GeSe4，较 DFT 加速 $\sim$5 个量级
- ✅ [@Tang2022hBN] GAP 复现层状 h-BN 各向异性声子输运（弱 vdW 键建模挑战）
- ✅ [@Li2022GeS] ML vs SW 经验势对比：ML 更准、SW 高估
- ✅ [@Arabha2021] 综述：MLIP for $\boldsymbol{\kappa}_L$（J. Appl. Phys., 52+ 引，验证存在）
- ✅ [@YangQian2021] 综述：ML for 热输运（Mat Sci Eng R, 88 引）
- ✅ [@Liu2023mini] 综述/meta：ML 预测 $\boldsymbol{\kappa}_L$（npj Comput. Mater.）
- ✅ [@Hu2023] 两阶段可解释 ML 预测 $\boldsymbol{\kappa}_L$
- ✅ [@Liu2025PINK] 物理信息 ML + CIF 批量筛选超低 $\boldsymbol{\kappa}_L$
- ✅ [@Lahnsteiner2022] MLFF 大系综非谐晶格动力学（SSCHA 类）
- ✅ [@Koker2026] PFT 声子微调：监督二阶力常数提升热导三阶导数；MDR-phonon 基准
- ✅ [@Grandel2026] Equitrain LoRA 微调：53 材料系统声子/热性质优于从头训练

## 滚雪球与时效

- 滚雪球：参考文献反查命中 Arabha2021 综述、Liu2021SnSe、Ouyang2022、Mortazavi2021(MTP/ShengBTE，sciverse 按精确标题未命中→不入台账)、YangQian2021 综述。
- 时效探针：已覆盖 2024-2026 全新工作（Cao2025、You2024、PINK2025、Koker2026、Grandel2026），无脱节。
- 收敛判定：本轮零新增入选、各子方向 $\ge$ 3 篇、时效探针已打。**滚雪球 5 轮，末轮新增 0 篇，达检索饱和。**

## 盲区自查

- 视角 E（批评/失效）客观偏薄：PFT/Equitrain 属"补强"，真"失效分析"仅通过 Ouyang2022(三声子高估) 与 Tang2022(层状弱 vdW) 侧面覆盖。已在综合中诚实标注。
- 界面热导（Si/diamond、cBAs/SiC）属邻近但不属晶格热导 $\boldsymbol{\kappa}_L$ 本体，未入选——话题聚焦而非遗漏。
