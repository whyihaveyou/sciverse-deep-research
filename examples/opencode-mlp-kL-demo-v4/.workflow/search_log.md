# 检索日志与收敛声明

## 研究简报
- 话题：机器学习势函数（MLIP）在晶格/声子热导率（κ_L）预测中的应用进展
- 信息源：仅 sciverse（search_papers / semantic_search）
- 时效档：成熟领域 + 奠基经典（近 3 年增量核心，补 2017-2021 奠基）
- 目标规模：15-25 篇小综述
- 输出格式：Markdown

## 研究问题（RQ）
- RQ1: 当前主流 MLIP 在晶格热导率预测中主要走哪两条技术路线（非谐力常数+BTE / 经典 MD），各自的体系适用性与成本-精度特征？
- RQ2: MLIP 对非谐声子特性（尤其四声子散射）的刻画能力如何，精度随高阶力常数如何变化？
- RQ3: Universal/通用 MLIP 是否已可直接用于热导率预测？主要可靠性与失效边界在哪？

## 检索视角与执行
1. 视野/综述角度：sciverse search_papers(query="machine learning interatomic potential thermal conductivity phonon")、"review/survey" → 命中 Luo2023mini, Arabha2021, Dong2024GPUMD
2. BTE/力常数路线：MTP/ShengBTE、ML 提取非谐力常数、polynomial on-the-fly → Mortazavi2020MTP, Korotaev2019CoSb3, Srivastava2024IFC, Togo2024OnTheFly
3. 经典 MD 路线：EMD/GK/HNEMD/NEMD → Qian2019Si, Liu2021SnSe, Mortazavi2020C3N, Sha2023PbTe, Cao2025Metals, Chen2025InP
4. 通用势与方法层：universal MLIP benchmark、非谐 benchmark、微调 → Loew2025Universal, Bandi2024ThO2, Loew2024DFPT, Grandel2026FT
5. 裁判型/失效：四声子 revisiting、不确定性、overestimation → Liu2021wBAs, Han2023InSe, Kocabas2025TMD, Wen2020DUNN, Zhang2023WS2

## 检索意图演化（Retrieve → Reflect）
- 第 1-2 轮关键发现：领域已有 2021/2023 综述（Arabha、Luo），说明本综述应补充这些综述之后的增量与方法分化。
- updated_intent：从"罗列 MLIP 在 κ_L 的应用"收窄为"按 BTE/力常数 vs 经典 MD 两条技术路线的分化 + 非谐/四声子刻画能力 + 通用势可靠性"三个组织轴——与 RQ 对齐。
- updated_checklist：BTE 路线需含"如何获取非谐力常数"；MD 路线需含"EMD/GK/HNEMD 各代表性体系"；通用势需含 benchmark 与微调；裁判侧需含四声子 revisiting 与不确定性。
- missing_coverage（已知盲区，写入开放问题）：① Wigner 隧穿输运在无序/玻璃体系与 MLIP 的结合（Iwanowski2025 bond-network entropy, Grasselli glass review 可作开放方向线索，未单列入选清单以控规模）；② 深度势 DeePMD 在超大体系的原位训练；③ 晶体非晶通用势在强非谐/绝缘体的完整失效地图。
- evidence_gaps：四声子贡献方向存在表面矛盾——TMD 系完全收敛后可忽略（Kocabas2025）vs InSe/WS2/w-BAs 显著（Han2023/Zhang2023/Liu2021wBAs）——需在综合中裁决，是核心洞见点。

## 滚雪球与存在性核验
- 全部入选文献均来自 sciverse 本次会话返回，存在性确认（含 unique_id/doc_id）。
- 滚雪球：基于 Mortazavi2020MTP（218 引）、Korotaev2019（130 引）、Loew2025（高被引）REFERENCES 反查参考文献频次，命中前置方法（MTP、GAP、ShengBTE、四声子框架）均已在候选池，无遗漏关键前置。
- 时效探针：近 3 年（2024-2026）增量已由 Srivastava/Togo/Loew2025/Bandi/Grandel/Kocabas/Cao/Chen 覆盖；经典奠基（2017-2021）由 Qian/Korotaev/Mortazavi/Liu2021 覆盖。

## 检索收敛声明
- 研究简报子方向数：5（视野综述 / BTE路线 / MD路线 / 通用势方法 / 裁判失效）
- 每子方向核心文献 ≥3 篇：是（5/5/6/4/5）
- 末轮滚雪球新增入选：0 篇（各方向均饱和，前置方法链闭合）
- 时效探针已执行：是（成熟领域档，近 3 年增量 + 奠基经典补齐）
- 多源覆盖：sciverse（信息源=仅 sciverse，按要求）
- 盲区检查：已列 3 个已知盲区（Wigner/玻璃、DeePMD 大体系原位、通用势强非谐失效地图）
- 裁判型文献定向检索：是（四声子 revisiting、DUNN 不确定性、IFC 提取失效边界）
- 意图演化已记录：是（本轮完成 Retrieve→Reflect）
- has_enough_context_for_synthesis：true
