# sciverse-deep-research —— 人怎么用（Human Quickstart）

> **这份给「人」看。** 给 **Agent** 看的装配引导在根目录
> [AGENT-BOOTSTRAP.md](AGENT-BOOTSTRAP.md)（Agent 自己读、自己配，人不用管）。
> 两份是一对：你安装/使用时照着这份，Agent 装配时让它读那份。

---

## 这套东西是什么（10 秒版）

给任意 AI Agent 配一套「搜得到、查得准、引得对、关把得住」的**学术深度综述**能力。
它不是一个新模型，而是挂在你已有的 Agent（Hermes / Claude Code / Codex / Kimi Code /
OpenCode…）上的一套 **skill 指令 + 两个 MCP 工具**——让你已有的 Agent 能做带**可核验
引用**的系统文献调研，产出结构严谨、引用可靠的综述（survey paper）。

一句话：sciverse 负责「搜得到、查得准」，本模块负责「引得对、关把得住」。

## 2×2 一览：谁在什么阶段看哪份

| 阶段 | 给 **人** | 给 **Agent** |
|------|-----------|--------------|
| **安装** | 本文档「安装时」↓ | `AGENT-BOOTSTRAP.md`（任意框架 3 步自装配） |
| **使用** | 本文档「使用时」↓ | `SKILL.md`（运行时完整调研流程） |

## 安装时，人需要做什么（只有 4 件事）

1. **装好一个 Agent 框架**（Hermes / Claude Code / Codex 等任选其一，已装的跳过）。
2. **要一个 sciverse 学术检索 token**（`SCIVERSE_API_TOKEN`，从
   https://sciverse.space 控制台「密钥」页获取）。
3. **下载仓库**：
   ```bash
   git clone https://github.com/whyihaveyou/sciverse-deep-research.git
   ```
4. **跑安装脚本**（自动检测本机 agent、symlink 装 skill、打印两个 MCP 配置片段）：
   ```bash
   cd sciverse-deep-research && ./install.sh
   ```

> **剩下的 MCP 配置交给 Agent 自己按 `AGENT-BOOTSTRAP.md` 完成**（或人想手动贴，
> 照 `agents/<你的框架>.md`）。**人不需要会写 MCP 配置。**

## 使用时，人需要做什么

把任务**用一句话丢给 Agent** 即可，例如：

> 「帮我调研一下『机器学习力场加速晶格热导率计算』这个方向，做一份系统文献综述。」

Agent 会自己跑完整管线：

冻结研究问题（2-3 个 RQ）→ 多来源检索 + 引文网络滚雪球到饱和 → 铸引用台账 →
草稿综合 → 编译编号 → 机械门禁验收 → 交付 `final.md`（本机装了 LaTeX 才额外给 PDF）。

**你不需要在中间干预**，除非 Agent 问你这几件事：

- **选型**：想从哪些数据源搜（sciverse 为主，可加 arXiv / OpenAlex）。
- **输出格式**：探测到本机有 LaTeX 时会问你要 Markdown 还是 PDF。
- **严格引用**：要求论文带卷期页码/DOI 时，Agent 自动走 Crossref 核验。

## 澄清一个常见误区：自评闭环 = 开发工具，不是每次使用都跑

你可能担心「是不是我每次用都会跑那 5 轮自评、慢吞吞」——**不是**。

- **自评闭环（self_eval.py + A/B 打分）是『开发/质量验证』功能**，用于项目团队迭代时
  验证"这版综述比上版好在哪"（例如当前正在跑的 M2 R1→R5、v1.0 验收线的 5 轮闭环）。
- **日常使用完全不触发它**。你叫 Agent 做一份综述，走的是 `SKILL.md` 的调研管线，
  是**不含自评分级**的正常调研流程。自评只是可选的质检手段，需单独显式调用。

## 项目里已有的文档（别再找重复的）

| 文档 | 给谁看 | 内容 |
|------|--------|------|
| `README.md` | 人 + 开发者 | 项目总览 / 三层结构 / 核心机制 |
| `AGENT-BOOTSTRAP.md` | **Agent** | 三步装配引导（Agent 自己配两个 MCP + skill） |
| **`HUMAN-QUICKSTART.md`（本文档）** | **人** | 安装/使用时人只做哪几件事（与上成对） |
| `agents/*.md`（7 个） | Agent | 各框架（Hermes/Claude/Codex/Kimi/OpenCode…）专属配置路径 |
| `SKILL.md` | Agent（运行时） | 完整调研流程指令（Step0→检索→铸台账→综合→门禁交付） |
| `HANDOFF.md` | 开发者 | 开发交接：进度 / 已完成 / 待办 / 怎么安全继续 |
| `tests/run_regression.py` | 开发者 | 回归门禁（改代码前跑，27/27 全绿是底线） |

## 一句话总结

**人只做两件事：装 Agent + 说一句「帮我调研 X」。** 剩下装配细节交给 Agent 读
`AGENT-BOOTSTRAP.md`，调研全流程由 Agent 用 `SKILL.md` 自动跑完，你要的是一份
**引用可核验**的最终综述。
