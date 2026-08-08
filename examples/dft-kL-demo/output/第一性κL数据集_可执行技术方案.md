# 第一性晶格热导率（κ_L）数据集：可执行技术方案（v1）

> 本方案是 dft-kL-demo overlap 结论的工程落地：用现有 MLIP-DFT 工具 + VASP/Phonopy/Phono3py/ShengBTE
> 造一套**不依赖 Slack/AGL 模型**的第一性 κ_L 数据集。
> 读法：第 1-4 节定"做什么、按什么标准做"；第 5-6 节是"怎么跑"（流水线 + 命令骨架）；
> 第 7-11 节是数据格式、质控、成本、风险、里程碑。
> 文中所有协议参数均给出默认值，**Stage 0 基准测试通过后冻结为 protocol v1，全库统一**。

## 1. 目标与产出物定义

**目标**：对每个候选材料，产出一行"第一性真值记录"——特征列由我们自己的 MLIP-DFT 重算
（替代 AFLOW 里 Slack/AGL 来源的 B, G, γ, θ_D, θ_ac, Cv, α），目标列 κ_L 用 BTE 级计算
（谐 + 三阶力常数 + Boltzmann 输运方程），不再经过任何经验模型。

**数据集三档定位**（先想清楚再造，避免算力错配）：

| 档位 | 内容 | 单条成本 | 目标规模 |
|---|---|---|---|
| Tier-0 筛选层 | 全部特征 + 符号回归公式预估 κ_L（无 BTE） | 分钟级（MLIP） | 全候选池（10³-10⁴） |
| Tier-1 真值层 | 特征 + BTE 级 κ_L(300 K)，RTA 起步、精选迭代解 | 10²-10³ 核时 | 10²-10³ |
| Tier-2 校验层 | 有可靠实验 κ_L 的校准子集，计算-实验对照 | 同 Tier-1 | 30-50 |

**一行数据的最小 schema**（详见第 7 节）：
`material_id | 结构 | 特征列(B,G,ρ,V,N,M̄,γ,θ_D,θ_ac,Cv,α,v_l,v_t) | κ_L(300K) | 方法标志 | QC 状态 | 协议版本`

## 2. 总体架构

```
候选池(AFLOW 条目, 绝缘/半导体)
   │
   ▼
[入池闸]  带隙>0 + 声子无虚频 + 形成能稳定性        —— 剔金属/不稳定相
   │
   ├──► 特征层(批量, MLIP-DFT): 弹性→B,G,v_s,θ_D,θ_ac;  准谐→γ,α,Cv
   │         │
   │         ▼
   ├──► 筛选层: 符号回归公式预估 κ_L → 分层抽样(高/中/低 κ 都要)
   │         │
   │         ▼
   └──► 真值层(BTE):  谐力常数(phonopy) + 三阶力常数(phono3py/thirdorder)
              │        力评估: 小胞纯 DFT; 大胞/多构型走 MLIP 加速
              ▼
        校验层: 实验 κ_L 校准集对照 + MLIP-MD(HNEMD) 交叉验证子集
```

关键设计两条：

1. **协议先行**：所有材料用同一份冻结协议（泛函/收敛/超胞/位移/截断/q 网格），
   协议版本号写进每行数据。口径不一致是 AFLOW-AGL 类数据最大的坑，我们自己造库第一天就锁死。
2. **MLIP 用在刀刃上**：MLIP 不替代 DFT 定协议，而是替代"成百上千个位移构型的力评估"
   （三阶力常数那一步，是纯 DFT 路线的成本瓶颈）。协议本身由 DFT 基准测试定死。

## 3. 材料候选池与入池门槛

- **来源**：用户已有 AFLOW 条目（符号回归公式用过的那批），保证新旧数据集可逐条对比。
- **第一道闸（电子）**：PBE 带隙 > 0（绝缘体/半导体）。Slack 类公式与 BTE 声子气模型都只
  对声子主导体系成立；金属电子热导占主导，直接剔除（或单独建金属分区，本方案不覆盖）。
- **第二道闸（动力学稳定）**：谐声子谱无虚频（容差 |ω| < 0.1 THz 内视作数值噪声）。
  有虚频的条目打 `qc=unstable` 标记，不进真值层。
- **第三道闸（复杂度）**：真值层第一批只收原胞原子数 ≤ 12 的条目，把单条 BTE 成本压住；
  大原胞条目留到 v2。

## 4. 统一计算协议（protocol v1，Stage 0 后冻结）

对齐 Phonon Olympics 2025 开源工具链基准的思路：同一批材料、同一组协议参数、跨工具交叉核对。
默认值如下（★ = Stage 0 必须做收敛扫描确认的参数）：

| 项 | 默认值 | 备注 |
|---|---|---|
| 泛函 | PBE（Stage 0 与 PBEsol 对比后二选一冻结） | PBE 晶格常数系统性偏高 ~1%，κ 偏低；选定后全库统一 |
| 平面波截断 | ENCUT = 1.3 × max(ENMAX) | PREC=Accurate, ADDGRID=.TRUE. |
| k 网格 | 间距 ≤ 0.2 Å⁻¹，Γ 中心 | 超胞力算按超胞尺寸等比减稀 |
| 电子收敛 | EDIFF = 1E-8 | 力常数对电子收敛极敏感 |
| 结构优化 | ISIF=3, EDIFFG = -1E-4 eV/Å | 力收敛到 1E-4 以下再算声子 |
| 谐力常数 | phonopy 有限位移，超胞使最近像距 ≥ 8 Å（典型 2×2×2）★ | 位移 0.01 Å ★ |
| 极性修正 | 极性材料必须 NAC（DFPT 算 Born 有效电荷 + 介电张量） | 漏 NAC → LO-TO 劈裂错 → κ 错，常见翻车点 |
| 三阶力常数 | phono3py 或 thirdorder.py(ShengBTE)，截断第 4 近邻（≈4-5 Å）★ | 位移 0.03 Å ★；文献区间 4-8 近邻 |
| 三阶力算 k 网格 | 超胞够大时 Γ 点单点 | 文献惯例 |
| BTE 求解 | phono3py `--br`(RTA) 初筛 + `--lbte` 迭代解入库 | RTA 系统性低估，正过程强的材料差 >30%，必须迭代解收尾 |
| q 网格 | 扫描 12³→24³，κ 变化 <5% 收 ★ | Si 类高 κ 材料要更密 |
| 同位素散射 | 自然丰度，开关状态写入方法标志 | Si 上影响 ~5-10%，入库建议开 |
| 温度 | 300 K 必算；100-1000 K 曲线可选 | v1 先锁 300 K |

**高阶修正触发器**（不全量做，按 Jain 2025 高阶输运综述的选择标准触发）：
γ > 2.5、或 300 K/θ_D > 0.5、或已知强非谐体系（如岩盐结构、含重元素的低 κ 材料）→
标记 `needs_4ph=true`，对这部分补四声子（FourPhonon）或 TDEP 温度重正化。v1 只打标，
v2 再批量补算。

## 5. 流水线（Stage 0-4）

### Stage 0 — 协议标定与基准（不做完这个，后面都算白跑）

- 选 6 个实验 κ_L 可靠的标准材料：**Si, Ge, 金刚石, GaAs, MgO, LiF**（覆盖高/中/低 κ、
  极性/非极性、轻/重元素）。
- 每个材料用默认协议全流程跑到 κ_L(300 K)，同时做 ★ 参数的收敛扫描。
- **验收门**：计算 κ_L 与实验值偏差全部 < 10%（Broido 2007 基准是 Si/Ge < 5%，
  留一倍余量给高通量妥协）；PBE vs PBEsol 谁更准就冻结谁。
- 顺带产出：MLIP vs DFT 的力对比（见 Stage 2）。

### Stage 1 — 特征层批量重算（MLIP-DFT 主战场）

对入池条目批量产出 overlap 清单前 10 项：

- **弹性**：应变-应力拟合 C_ij → VRH 平均得 B, G（与 AFLOW 口径一致）→ 声速 v_l, v_t、
  θ_D、θ_ac（声学支 Debye 温度）。
- **准谐**：±3% 体积点扫 E-V + 各体积声子 → γ（模式 Grüneisen 取平均）、α、Cv(300 K)。
- **结构常数**：ρ, V, N, M̄ 直接由结构算。
- MLIP 与 DFT 分工：MLIP 出全部初值；**每个化学体系抽 1-2 个条目用纯 DFT 复核**，
  B 偏差 >5% 的体系整列回退 DFT。

### Stage 2 — MLIP 加速三阶力常数（成本瓶颈在这，加速也在这）

纯 DFT 算三阶力常数 = 几百到上千个位移超胞的力计算，这是全管线最贵的环节。
两条加速路径，按你们 MLIP 工具成熟度选：

- **路径 A（直接替换力评估）**：phono3py/thirdorder.py 照常生成位移构型，力由 MLIP 算
  （接口见 6.5 适配层契约）。先例：MTP/ShengBTE 方案（Mortazavi 2020）用 50-700 K 短 AIMD
  训练的势替换 DFT 力，κ 与全 DFT 吻合；NNP 方案（Choi/Han 2022）25 个材料上提速 2-50 倍。
- **路径 B（压缩感知/稀疏回归）**：hiPhive/CSLD——少量 DFT 或 MLIP 构型 + 稀疏拟合直接出
  高阶力常数（Wolverton 组 37 个二元化合物高通量 κ 用的就是 CSLD）。
- **MLIP 可信度门（必做）**：每类体系先用 DFT 校验 MLIP——20 个位移构型力 RMSE、
  声子色散、γ 三项对齐（力 RMSE ≲ 10 meV/Å 量级、色散肉眼重合、γ 偏差 <10%），
  不过线的体系回退纯 DFT。

### Stage 3 — 真值层 κ_L(BTE) 批量

- 每个条目：谐力常数(phonopy) → 三阶力常数(phono3py/thirdorder，力走 Stage 2) →
  RTA 初解 → **迭代解（ShengBTE/phono3py `--lbte`）入库**。
- 分层跑批：筛选层预估高 κ 的材料优先（q 网格收敛更慢，先跑先发现问题）；
  预估低 κ 的快，量大垫后。
- **RTA/迭代差 > 30% 的条目标 `normal_process_strong=true`**——这类材料的 RTA 值不入库，
  只收迭代解。

### Stage 4 — 校验层

- **实验校准集**：30-50 个有公认实验 κ_L(300 K) 的材料（Stage 0 的 6 个 + 扩充），
  算一遍进库并公开对照表；这是数据集对外的"信用状"。
- **MLIP-MD 交叉验证**：对 ~10 个条目用 MLIP 分子动力学（HNEMD 或 Green-Kubo）独立算 κ，
  与 BTE 值对照（先例：Ouyang 2022 PRB）。两条独立路线互相咬住，才能说"真值"。
- **回测旧公式**：用新数据集重训/验证你们的符号回归公式，量化 Slack 特征换第一性特征后
  的精度变化——这是整个项目动机的闭环。

## 6. 命令骨架

> 以下是可直接改用的骨架，路径/伪势按实际环境替换。VASP 版本、POTCAR 哈希写入每行数据溯源。

### 6.1 VASP 模板

结构优化（`INCAR.relax`）：
```bash
PREC = Accurate
ENCUT = 520            # = 1.3 × max(ENMAX)，按体系调整
EDIFF = 1E-8
ISIF = 3
IBRION = 2
NSW = 200
EDIFFG = -1E-4
ISMEAR = 0 ; SIGMA = 0.05   # 半导体/绝缘体
ADDGRID = .TRUE.
LWAVE = .FALSE. ; LCHARG = .FALSE.
```

力常数用单点力（`INCAR.force`）：在上面的基础上去掉 NSW/IBRION（`IBRION=-1; NSW=0`）。

NAC 参数（极性材料，DFPT）：
```bash
LEPSILON = .TRUE.    # 介电张量 + Born 有效电荷 → BORN 文件给 phonopy --nac
```

### 6.2 谐力常数（phonopy）

```bash
# 生成位移构型（2×2×2 超胞，位移 0.01 Å）
phonopy -d --dim 2 2 2 --amplitude 0.01 -c POSCAR-unitcell

# 每个 SPOSCAR-* 跑 VASP 单点力（或 MLIP 力），收集 vasprun.xml / 力文件
phonopy -f SPOSCAR-*/vasprun.xml

# 力常数 + 声子谱（极性材料加 --nac 读 BORN）
phonopy --dim 2 2 2 --nac -c POSCAR-unitcell -p band.conf
# 质控：band.yaml 里查虚频（容差 0.1 THz）
```

### 6.3 三阶力常数 + BTE（phono3py 路线）

```bash
# 三阶位移构型（截断 4.5 Å，位移 0.03 Å）
phono3py -d --dim 2 2 2 --cutoff 4.5 --amplitude 0.03 -c POSCAR-unitcell

# 收集力 → fc3（构型多，这一步走 MLIP 适配层）
phono3py --cf3 disp-{00001..NNNNN}/vasprun.xml
phono3py --fc3 --fc2 --dim 2 2 2 -c POSCAR-unitcell

# RTA 初筛
phono3py --br --mesh 20 20 20 --fc3 --fc2 --nac --ts 300

# 迭代解（入库值）+ 同位素
phono3py --lbte --mesh 20 20 20 --fc3 --fc2 --nac --isotope --ts 300

# q 网格收敛扫描：--mesh 12 12 12 / 16 16 16 / 20 20 20 / 24 24 24，κ 变化 <5% 收
```

### 6.4 ShengBTE 路线（与 phono3py 交叉核对用）

```bash
# 三阶构型（-4 = 第 4 近邻截断）
thirdorder.py sow 2 2 2 -4
# …跑力…
thirdorder.py reap 2 2 2 -4   # 产出 FORCE_CONSTANTS_3RD
```

`CONTROL` 关键字段：
```
&allocations
  nelements=2, natoms=<原胞原子数>, ngrid(:)=20 20 20
&crystal
  …(晶格/坐标, 与 phonopy 输入同源)
&parameters
  T=300, scalebroad=1.0
&flags
  isotopes=.TRUE., onlyharmonic=.FALSE.
  # nanowires 不用; espresso=.FALSE.
```
ShengBTE 默认即迭代全解；与 phono3py 结果互差应 <5%（Phonon Olympics 式交叉核对）。

### 6.5 MLIP 适配层契约（关键假设，需与你们的工具对接）

本方案不假设 MLIP 工具的具体形态，只定义它必须满足的**接口契约**：

```
输入:  结构文件(POSCAR/CIF) 列表
输出:  每个构型的 energy / forces(N×3) / stress(3×3)，格式可转成 vasprun.xml 等价物
能力:  (a) 批量单点力评估（Stage 1-3 主力）
       (b) NVT/NPT MD（Stage 4 HNEMD 交叉验证）
质保:  对每类体系输出与 DFT 的力 RMSE 报告（Stage 2 可信度门）
```

落地做法：写一个 `mlip2vasprun` 转换器，把 MLIP 力包装成 phonopy/phono3py 认的格式，
上面 6.2/6.3 的命令**一行不用改**——加速完全发生在力评估这一层，管线其余部分与纯 DFT 完全同构。
这样 MLIP 出问题时回退纯 DFT 零成本。

## 7. 数据 schema（每行一条材料）

| 字段组 | 字段 |
|---|---|
| 标识 | material_id, formula, spacegroup, 结构文件哈希, 来源库条目 id |
| 特征列 | B, G(VRH), ρ, V, N, M̄, γ, θ_D, θ_ac, Cv(300K), α, v_l, v_t |
| 目标列 | kL_300K（迭代解）, kL_300K_rta（备查）, 可选 kL(T) 曲线 |
| 方法标志 | functional, protocol_version, fc3_cutoff, q_mesh, isotopes, nac, needs_4ph, normal_process_strong |
| 质控 | qc_status(pass/unstable/conv_fail/mlip_fallback), 各收敛扫描残差 |
| 溯源 | VASP 版本, POTCAR 哈希, MLIP 模型版本, 力来源(dft/mlip) |

存储建议：每材料一个目录（输入文件 + 力常数 + BTE 输出全套保留，力常数文件是复算的资本），
索引层一张 parquet/CSV。力常数比 κ 值本身更值钱——以后升级 BTE 求解器不用重算力。

## 8. 质控与验收标准（每道闸的量化判据）

| 闸 | 判据 | 不过线怎么办 |
|---|---|---|
| 结构优化 | 残余力 < 1E-4 eV/Å | 重优化 |
| 动力学稳定 | 无虚频（容差 0.1 THz） | 标 unstable，不进真值层 |
| NAC | 极性材料必须有 BORN | 补 DFPT 或标 qc 缺失 |
| fc3 截断收敛 | 截断 +1 近邻，κ 变化 <5% | 加大截断 |
| q 网格收敛 | 相邻网格 κ 变化 <5% | 加密网格 |
| RTA vs 迭代 | 差 >30% 只收迭代解 | 打标 |
| Stage 0 基准 | 6/6 材料与实验 <10% | 协议不冻结，回炉 |
| MLIP 可信度 | 力 RMSE / 色散 / γ 三项对齐 | 该体系回退纯 DFT |

## 9. 成本与算力估算（量级，供排期）

- 单条 Tier-1（原胞 ≤12 原子，纯 DFT）：弹性 ~10² 核时；准谐 ~10²-10³；三阶力常数
  ~10³-10⁴ 核时（瓶颈）；BTE 求解 ~10¹-10²。**单条合计 10³-10⁴ 核时量级**。
- MLIP 路径把三阶力常数那一步压 1-2 个数量级（文献 2-50×），代价是每个新化学体系
  要过可信度门。
- Tier-0 全池（10³-10⁴ 条）走纯 MLIP：单条分钟级，总计可忽略。
- 结论：**第一批 Tier-1 定 100-200 条**，MLIP 加速下是中等集群几周的事；纯 DFT 则要
  砍到 50 条以内或拉长线。

## 10. 风险与对策

1. **PBE 系统性偏差**（晶格常数 +1% → κ 偏低）：统一泛函 + Stage 0 与 PBEsol 对照冻结；
   偏差系统性存在不可怕，可怕的是口径混用。
2. **强非谐材料三阶不够**：γ > 2.5 或高温区材料打 `needs_4ph` 标，v2 补四声子/TDEP；
   v1 对这些条目标注"三阶 BTE 值，可能高估实验偏差"。
3. **MLIP 分布外失效**：可信度门 + 力来源溯源字段；宁可回退 DFT 慢算，不放静默错值进库。
4. **虚频条目污染**：第二道闸直接拦在真值层外。
5. **q 网格/截断没收敛就入库**：收敛扫描残差写进 schema，门禁式检查（FAIL 不出库）。

## 11. 里程碑

| 里程碑 | 内容 | 验收 |
|---|---|---|
| M0（约 1-2 周） | 协议标定：6 基准材料全流程 + 收敛扫描 | 6/6 与实验 <10%，protocol v1 冻结 |
| M1（2-4 周） | 特征层：候选池全量特征重算 | 每体系 DFT 抽检过线，特征表 v1 |
| M2（4-8 周） | MLIP 加速通路打通 + Tier-1 首批 100-200 条 | 可信度门通过率统计 + κ 入库 |
| M3（2 周） | 校验层：实验校准集对照 + MLIP-MD 交叉 + 旧公式回测 | 数据集 v1.0 + 对照报告 |

## 12. 参考依据（本方案关键判断的出处）

- overlap 清单与"重算前 10 项即独立真值特征集"：本项目 dft-kL-demo 综述
  （`output/DFT能算的物理量清单_与晶格热导率Overlap.md`，17 篇台账）。
- DFT+BTE 无参数算 κ、Si/Ge 与实验 <5%：Broido et al., APL 2007。
- 造库协议对齐思路（同协议跨工具基准）：McGaughey et al., Phonon Olympics, JAP 2025。
- 三阶截断 4-8 近邻、Γ 点力算、迭代解必要性：ShengBTE/phono3py 文献惯例
  （Lindroth & Erhart PRB 2016；Shao et al. Sci. Rep. 2016 等）。
- MLIP 替换 DFT 力算三阶力常数：Mortazavi et al., CPC 2020（MTP/ShengBTE）；
  Choi et al., Comput. Mater. Sci. 2022（NNP，2-50×）。
- 压缩感知高阶力常数高通量：Xia et al., PRX 2020（37 个二元化合物 + 四阶非谐）。
- 通用 MLIP 加速高通量声子：Lee et al., Mater. Today Phys. 2025。
- 高阶修正触发标准：Jain et al., 高阶热输运综述 2025（fourPhonon/TDEP/ALAMODE 选择准则）。
- MLIP-MD 交叉验证 κ：Ouyang et al., PRB 2022。

---

*v1 草案，2026-08-07。协议参数在 Stage 0 基准测试通过前均为默认值，不作为最终口径。*
