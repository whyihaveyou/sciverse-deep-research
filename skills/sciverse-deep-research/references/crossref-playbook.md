# Crossref 检索手册

## 端点

- **反查题录**（已知标题+作者）：`https://api.crossref.org/works?query.bibliographic=<q>&rows=3`
  - `<q>` = 论文标题 + 第一作者姓，空格用 `+` 或 `%20` 编码。
- **DOI 直查**（校验已知 DOI）：`https://api.crossref.org/works/<DOI>`
  - 返回 404 = 该 DOI 不存在于 Crossref（可能是编造的，也可能是中文注册机构的 DOI——结合文献语言判断）。
  - 返回 200 但标题对不上 = 张冠李戴，按"不一致"处理。

有代码执行环境时，以上端点访问不手工逐条进行——用 `scripts/verify_citations.py` 批量跑（首次使用先 `--probe` 自检网络可达性；查询类 URL 被网络层破坏时用 `--emit-urls` + `--from-dir` 混合模式，见主 SKILL.md"题录核验环节"）。

## 脚本使用纪律（verify_citations.py）

- **输入 JSON 键名必须是规范名**：`id` / `title` / `first_author`（可选 `journal` / `doi` / `year` / `volume` / `issue` / `pages`）。脚本会自动纠正常见别名（如 first_author_last）并提示，缺少必填字段会硬报错且不发起网络请求——但请一开始就用规范键名。
- **title 必须是论文原文标题**（英文文献用英文原题）——不得使用聚合站返回的中文翻译标题或截断标题，这是脚本全线未命中的头号原因。若脚本报告全部 NOT_FOUND 且 probe 正常，按台账中的"最佳候选"诊断修正输入后重跑，不得直接弃用脚本通道。
- **脚本不会抽样**：输入几篇就核验几篇——篇级完备性闸门由此天然满足，前提是最终清单必须整体作为输入，不许只喂一部分。误匹配防御（标题归一化相似度阈值 + 第一作者姓氏比对）已写入代码，无需人工执行。
- 已知 DOI 填 `doi` 字段即启动张冠李戴校验；已有卷期页的填入即启动逐字段比对。脚本输出的"不一致告警"逐条消解后才能出稿。
- 脚本对 VERIFIED 条目会额外告警"疑似简报/评论/更正"（页跨度 ≤3 或 type 非 journal-article）——**题录正确不等于文献类型合格**，同族的 Policy Brief 与研究正文各有 DOI，任务要求原创研究时必须选正文。
- 混合模式：`--probe` 若显示"路径类 OK、查询类 FAIL"，运行 `--emit-urls citations_input.json` 生成 URL 清单，用网页抓取工具逐条访问并把每条返回的 JSON 原样保存为 `responses/<id>.json`，再运行 `--from-dir responses/ citations_input.json -o verification_ledger.md`——匹配逻辑、台账、报数与在线模式完全一致，确定性不受影响。

## 两个已验证的陷阱

- `https://doi.org/<DOI>` 会 302 跳转到出版商页面，网页抓取工具通常报错（link fetch error）。**一律走 api.crossref.org。**
- 裸 DOI 字符串直接作为网页检索工具的 query，返回的是共享相同 DOI 前缀的无关文献。**不要这样搜**；网页通道用"标题 + 期刊名"检索。

## JSON 字段映射

| 报告字段 | Crossref JSON 路径 | 备注 |
|---|---|---|
| 题目 | `message.title[0]` | |
| 作者 | `message.author[].family` / `.given` | |
| 期刊全称 | `message.container-title[0]` | |
| 卷 | `message.volume` | |
| 期 | `message.issue` | 部分期刊部分卷无期号，缺失是正常的，如实写"该卷无期号"，不要编 |
| 页码 | `message.page` | article-number 时代的期刊可能返回文章号而非页码区间，照抄即可 |
| DOI | `message.DOI` | |
| 正式刊出时间 | `message.published-print.date-parts` | 参考文献年份以此（卷期归属）为准 |
| 在线发表时间 | `message.published-online.date-parts` | 与 print 都记录，两者差一年以上很常见 |
| 被引数 | `message.is-referenced-by-count` | Crossref 口径，与 Google Scholar 被引数不同，标注口径 |

## 匹配判定（误匹配防御细则）

`query.bibliographic` 返回按相关度排序，第一条不保证是目标。对 rows 内每条结果检查：

1. **标题归一化比对**：双方标题转小写、去标点、连字符与空格互换视为等同、忽略首尾空白后，一致或仅有极小差异（如单复数、英式美式拼写）。
2. **第一作者姓氏一致**：注意中文姓名拼音可能姓/名顺序颠倒（"Qin Zhu" vs "Zhu Qin"），姓氏能对上即可。
3. **期刊名核对**（若上游给了期刊）：container-title 一致或为公认缩写。

条件 1、2 必须同时满足才算命中；否则按未命中处理，进入网页通道。**宁可未核验，不可错核验。**（`scripts/verify_citations.py` 已把条件 1、2 写进代码，无需人工执行；手工通道仍须照做。）

## 常见陷阱

- **在线年 vs 刊出年**：online-first 与正式编卷常跨年（2022 在线、2023 编入 23 卷）。凡两者不同，都记录，正文与参考文献用刊出年。
- **预印本与正式版**：arXiv 版与期刊版是不同 DOI，确认引的是哪个版本。
- **会议论文**：container-title 是论文集名，常无卷期页，以返回为准，不补全。
- **中文期刊**：多数不在 Crossref（DOI 归中文注册机构管理），Crossref 404 不等于不存在，直接走网页通道查知网/万方/期刊官网。
- **Elsevier DOI 后缀**：2019 年前后规则不同——前期是任意序号（如 `j.enpol.2012.05.068`），后期等于文章号（如 `j.jclepro.2020.121479`）。任意序号无法从页码或年份推出，这正是禁止构造 DOI 的原因。
