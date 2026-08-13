# section_reviews.md — 结构化草稿审稿审计

## 分支 1（描述符/组成监督学习代理）

```
claims_verification:
  - "Kim2026MTComm: R2=0.569 / MAE=0.911 (Li), F1=0.83-0.92（区分>1e-4 S/cm）" → 与摘要一致 ✓
  - "Kim2026JCP: GBR MAE=0.543 (log S/cm), n=499" → 与摘要一致 ✓
  - "Chen2024: 20717 材料、468 样本库" → 与摘要一致 ✓
  - "Kang2023: 19480 含锂材料" → 与摘要一致 ✓
  - "Kong2025: Li6.7Ge0.595Si0.105P0.3S5I 7.2e-3 S/cm；'co-substituted argyrodite'" → 与摘要一致 ✓
  - "Xiang2025: 电负性/密度/离子半径为 A 位关键特征" → 与摘要一致 ✓
L3_L4_verdict: L3 —『小数据下分类/排序可靠、绝对回归存疑』为跨 Kim2026MTComm/Kim2026JCP/Zhang2019 多源收敛判断
evidence_gaps: E2I 的"语义对位"表述已删，改为直接引用 [@Kong2025]；实验验证端文献仍偏少（仅 Kong2025/Kim2025）
patch_plan: 已移除 bare `[Kong2025]`（改 [@Kong2025]）；确认分支产出 ≥1 条 L3 洞见
```

## 分支 2（机器学习势函数 / MD）

```
claims_verification:
  - "Gurwell2026: 18 个 uMLIP、四家族、12 种锂化合物、对照 7Li NMR+DFT" → 与摘要一致 ✓
  - "Zhang2024: 小超胞高估 RT 电导率；~420K 超离子转变" → 与摘要一致 ✓
  - "Hajibabaei2021: SGPR on-the-fly、Li-P-S/Li-Sb-S/Li-Ge-P-S 组合势" → 与摘要一致 ✓
  - "Shantsila2026: STING 委员会不确定性细调 > foundation MLIP" → 与摘要一致 ✓
  - "Sun2025: CDHE garnet 多步筛选用 CHGNet" → 与摘要一致 ✓
  - "Lee2025: argyrodite 阴离子笼心局域" → 与摘要一致 ✓
L3_L4_verdict: L4 —『通用势 = 初始化+先验，非免训练终态；需系统特定数据细调』跨 Gurwell2026/Zhang2024/Shantsila2026 裁决后成结论
evidence_gaps: 通用势在界面/晶界扩散的可靠度证据仍单薄；晶界 MLIP 工作未纳入（数据/论文主体为体相）
patch_plan: 移除对未入账 Ong ECS 摘要的具名引用，改以 [@Hajibabaei2021] 承接可迁移理念；满足分支 L3/L4 要求
```

## 分支 3（生成式与主动搜索）

```
claims_verification:
  - "Zhao2021: CubicGAN 训练 375,749 三元材料、506 个声子验证新原型" → 与摘要一致 ✓（正文写"37 万余"，量级自检通过）
  - "Tawfik2025: 贝叶斯优化最大化 Li 扩散，Li3YBr6" → 与摘要一致 ✓
  - "Rajapriya2026: BO 冷烧结 LATP，CSP 1.94e-4 S/cm" → 与摘要一致 ✓
  - "Hong2026: 深度主动学习+知识迁移，对称电池寿命 ×3" → 与摘要一致 ✓
  - "Sun2023: active learning 降不确定性" → 与摘要一致 ✓
L3_L4_verdict: L3 —『从性质绝对值到信息效率』为方法学洞见；生成/搜索的验证闭环缺失为 gap
evidence_gaps: 生成模型专用于 SSE 的文献仍缺，仅借 CubicGAN（通用户）与反钙钛矿数据扩增作方法参照——已如实限定
patch_plan: 已删三个脚注（[^sting-doc]/[^ong-paper]/[^rajapriya]）；确认无 bare 编号引用
```

## 分支 4（界面 / SEI ML 建模）

```
claims_verification:
  - "Diddens2022: 代理模拟器+深度生成+物理协同，指向 SEI 逆向设计" → 与摘要一致 ✓
  - "Zheng2025: 锂化依赖的 SEI 成核路径（Si/Li6PS5Cl）" → 与摘要一致 ✓
  - "Zhong2025: ML 引导 SEI 电导率、非晶锂氟磷酸盐" → 与摘要一致 ✓
  - "Stevenson2023: ML 力场排序候选 SEI 结构" → 与摘要一致 ✓
  - "Jia2024: 界面多物理耦合（化学/力学/电输运）" → 与摘要一致 ✓
L3_L4_verdict: L3 —『ML 应用密度与商业紧迫性成反比（界面最急却最稀）』为跨分支对照洞见
evidence_gaps: 界面 ML 文献密度明显低于体相；Diddens2022 为 2022 年前瞻，后续进展慢——已如实呈现
patch_plan: 分支 4 证据密度薄是客观 finding，非写作缺陷；以"对比单薄"作为洞见而非遮掩
```
