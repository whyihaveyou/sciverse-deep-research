# 结构化草稿审稿记录（section_reviews）

```section_review: 分支 四 / 定义与结构根源
- claims_verification:
  - claim_1: "谱维数由 Laplacian 谱密度定义，通过回返概率 P(t)~t^{-d_s/2} 涌现" → supported_by: [@RammalToulouse1983][@Aharony1986]; status: 直接支持
  - claim_2: "Sierpinski 三角谱维数 d_s=2 ln(d+1)/ln(d+3)" → supported_by: [@DAuriacRammal1983]; status: 直接支持
  - claim_3: "谱维数与分形维数解耦" → supported_by: [@PattersonBamieh2014][@Grimaldi2025]; status: 直接支持
  - claim_4: "可调谱维数网络模型 1→∞" → supported_by: [@MillanUniversality2021]; status: 直接支持
  - claim_5: "Fiedler 维数与谱维数可解耦" → supported_by: [@Grimaldi2025]; status: 直接支持
- L3_L4_verdict:
  - 本节最高洞见等级：L3
  - L3/L4 级洞见原文：""网络的谱维数在介观尺度上并非单一量"——Fiedler 维数与谱维数解耦，二者在介观/宏观尺度刻画不同集体动力学"
- evidence_gaps:
  - 反向证据或限定条件：AVrachenkov RGG 谱维数≈空间维数为正例
  - 需补搜/对读才能确认的 claim：无
  - 需降级表述的 claim：无
- patch_plan: 无需修订
```

```section_review: 分支 五 / 随机行走
- claims_verification:
  - claim_1: "回返概率 P_0(t)~t^{-d_s/2} 被严格验证" → supported_by: [@MillanUniversality2021]; status: 直接支持
  - claim_2: "谱密度标度时熵增对数，信息维数=谱维数，SG d_s=2ln3/ln2" → supported_by: [@Mulken2017]; status: 直接支持
  - claim_3: "首达时间方差 Var(T)~N^{4/d_s}" → supported_by: [@Haynes2008]; status: 直接支持
  - claim_4: "双分形网络谱维数双值 d_s^min/d_s^max" → supported_by: [@Yakubo2024]; status: 直接支持
  - claim_5: "trapping 效率由分形维数主导(与谱维数对照)" → supported_by: [@ZhangTrapping2011][@ZhangKoch2009]; status: 直接支持
- L3_L4_verdict:
  - 本节最高洞见等级：L3
  - L3/L4 级洞见原文："谱维数是随机行走渐近动力学标度的稳健预言者；分形维数只在同时调控几何连接性时呈决定性——回返/首达渐近量由 d_s 主控，trapping 目标依赖效率受分形维数与 hub 结构介入，二者不矛盾而对应不同观察量"
- evidence_gaps:
  - 反向证据或限定条件：Tejedor 强调 GMFPT 依赖目标节点（目标依赖）
  - 需补搜/对读才能确认的 claim：无
  - 需降级表述的 claim：无
- patch_plan: 无需修订
```

```section_review: 分支 六 / 同步与共识
- claims_verification:
  - claim_1: "同步热力学稳定需 d_s>4，相位锁定需 d_s>2" → supported_by: [@MillanSync2019][@Evnin2026]; status: 直接支持
  - claim_2: "同步稳定性受 d_s 影响，frustrated 同步" → supported_by: [@MillanFrustrated2018]; status: 直接支持
  - claim_3: "一致相干性 H_FO~N^{2/d_s-1}, H_SO~N^{4/d_s-1}" → supported_by: [@PattersonBamieh2014]; status: 直接支持
  - claim_4: "同分形维数可不同相干性，分形维不唯一决定" → supported_by: [@PattersonBamieh2014]; status: 直接支持
  - claim_5: "共识收敛速度由 λ2 界定，正则格子 λ2→0" → supported_by: [@JinMurray2007][@GomezGardynes2013]; status: 直接支持
  - claim_6: "Sierpinski vs 分层图各项共识量不同" → supported_by: [@QiSierpinski2019]; status: 直接支持
- L3_L4_verdict:
  - 本节最高洞见等级：L3
  - L3/L4 级洞见原文："同步与共识对 d_s 的依赖是同一个几何量在网络序参量上的两次呈现——$d_s$ 决定大尺度有序是否可维持；调大谱维数比盲目增加连边更本质"
- evidence_gaps:
  - 反向证据或限定条件：无冲突；时变拓扑下 d_s 角色未覆盖（开放问题）
  - 需补搜/对读才能确认的 claim：无
  - 需降级表述的 claim：无
- patch_plan: 无需修订
```

```section_review: 综合讨论 / 结论
- claims_verification:
  - claim_1: "谱维数统一随机行走、同步、共识三类动力学" → supported_by: [@MillanUniversality2021][@MillanSync2019][@PattersonBamieh2014][@Evnin2026]; status: 直接支持
  - claim_2: "跨线索通过谱密度 p(ω)~ω^{d_s/2-1} 与 λ2~N^{-2/d_s} 串联" → supported_by: [@RammalToulouse1983][@PattersonBamieh2014]; status: 直接支持(推断标注)
  - claim_3: "有限尺寸使谱维数估计偏差、异质网络双值" → supported_by: [@Craig2022][@Yakubo2024][@Grimaldi2025]; status: 直接支持
- L3_L4_verdict:
  - 本节最高洞见等级：L4
  - L3/L4 级洞见原文："对一个要设计能同步/快速共识网络的工程者，调大谱维数(如构造更高 d_s 连通层次)比盲目增加连边更本质——可执行设计判据"
- evidence_gaps:
  - 反向证据或限定条件：谱密度与λ2串联关系为跨文献推断，非单篇直接证明
  - 需补搜/对读才能确认的 claim：λ2~N^{-2/d_s} 与 p(ω) 的关系未逐篇对读
  - 需降级表述的 claim：综合讨论第2条已标注推断性质
- patch_plan: 无需修订
```
