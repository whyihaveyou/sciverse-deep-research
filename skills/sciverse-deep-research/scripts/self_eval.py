#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
self_eval.py — sciverse-deep-research 自评工具链（P1 核心）

定位：把「这份调研/综述做得好不好」从主观印象变成可复核的数字。
两路并行的自评信号，互不替代：

  1) judge   —— LLM-as-judge：把 final.md 喂给 PJLab API 的 judge 模型
                 （deepseek-v4-flash-0731），按本 skill 的 7 维内部质量门禁
                 （Angle/Coverage/Citation/Taxonomy/Calibration/Weaving/Insight）
                 逐维打分（1-5），同一份文本采样 N 次（默认 5）取**均值和极差**，
                 抵消单次 LLM 打分的随机性，得到一个带稳定度的自评分数。
  2) objective—— 客观指标采集：门禁 FAIL/WARN 数、台账来源数（引用文献数）、
                 每章节字数。这些是机械可测的硬指标，不依赖网络和 LLM，
                 无 API key 时也能跑，作为 judge 的旁证。

红线（安全）：
  - API key **绝不进 git**。key 只从两个地方读，且这两个地方都不在本仓库：
      1) 环境变量  SCIVERSE_DEEPSEEK_API_KEY
      2) 宿主配置  ~/.hermes/config.yaml 的 providers.pujiang-deepseek.api_key
  - 脚本内不写死任何 key；--judge-key 参数出于安全考虑**故意不提供**。
  - 找不到 key 时 judge 明确报错并 exit 3，绝不静默降级、绝不打空分。

零依赖：仅 Python 标准库（urllib / argparse / json / re / statistics）。
网络不可达时如实报错（exit 1），把「judge 不可用」与「得分低」区分开。

用法：
  # 客观指标（无 key 也能跑）
  python3 self_eval.py objective --report <final.md> \
      [--citation-ledger <cited.json|delivery.json>]

  # LLM-as-judge，默认 5 次采样取平均
  python3 self_eval.py judge --report <final.md> [--samples 5] [--message 简评标题]

  # 离线自检（回归门禁用，不碰网络/key）
  python3 self_eval.py --selftest

输出：judge 按维打分（mean +/- range）并给总分（各维均值）；objective 给硬指标，
     二者均以 JSON 兜底（--format json）。
"""

import argparse
import json
import os
import re
import statistics
import sys
import urllib.request

# judge 模型与源（base_url 可被环境变量 SCIVERSE_DEEPSEEK_BASE_URL 覆盖，方便切换/自建）
JUDGE_MODEL = os.environ.get("SCIVERSE_DEEPSEEK_MODEL", "deepseek-v4-flash-0731")
DEFAULT_BASE = "https://token.pjlab.org.cn/v1"

# 7 维内部质量门禁（与 references/quality-gates.md 保持一致；每维一句话评分锚点）
DIMS = [
    ("Angle",      "是否有清晰独立的判断/核心结论，而非只罗列话题"),
    ("Coverage",   "是否覆盖该子问题的关键方面/主要流派，无明显缺口"),
    ("Citation",   "引用是否准确绑定、题录可信、防错绑防编造"),
    ("Taxonomy",   "分类/组织是否严谨，同类是否合并、异类是否分清"),
    ("Calibration","取舍分寸是否恰当（不过度承诺、不夸大、标注不确定）"),
    ("Weaving",    "多来源/多子问题是否交织成一个整体，而非拼盘"),
    ("Insight",    "是否有超越罗列的洞见/综合/批判性观察"),
]
DIM_NAMES = [d[0] for d in DIMS]

CONFIG_PATH = os.path.expanduser("~/.hermes/config.yaml")
ENV_KEY = "SCIVERSE_DEEPSEEK_API_KEY"


# ---------------------------------------------------------------------------
# key / 配置来源（红线：绝不硬编码，绝不写进仓库）
# ---------------------------------------------------------------------------
def _load_yaml_key(path):
    """极简 YAML 子集解析：取 providers.<name>.api_key / api。

    不引 PyYAML（守零依赖），只按缩进规整提取我们要的两三个标量字段。
    结构期望（顶层缩进 0，provider 缩进 2，字段缩进 4）：
        providers:
          pujiang-deepseek:
            api: https://...
            api_key: sk-...
    """
    try:
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
    except OSError:
        return {}
    prov = {}
    cur = None
    for raw in lines:
        line = raw.split("#", 1)[0].rstrip()  # 去行内注释
        m = re.match(r"^(\s*)(\S.*?:)\s*(.*)$", line)
        if not m:
            continue
        indent = len(m.group(1))
        field = m.group(2).rstrip(":").strip()
        val = m.group(3).strip().strip('"').strip("'")
        if indent == 0 and field == "providers":
            cur = "__root__"
            continue
        if indent == 2 and cur == "__root__":
            cur = field
            prov.setdefault(cur, {})
            continue
        if indent == 2 and cur and cur != "__root__":
            prov.setdefault(cur, {})  # 未显式 root 的容错
            continue
        if indent == 4 and cur and cur != "__root__":
            if field in ("api", "api_key", "base_url"):
                prov[cur][field] = val
            continue
    return prov


def _get_key():
    """返回 (key, base_url) 或 (None, base_url)。key 只来自环境变量或宿主 config。"""
    base = os.environ.get("SCIVERSE_DEEPSEEK_BASE_URL", DEFAULT_BASE)
    key = os.environ.get(ENV_KEY)
    if key:
        return key, base
    prov = _load_yaml_key(CONFIG_PATH)
    p = prov.get("pujiang-deepseek", {})
    key = p.get("api_key")
    if p.get("api"):
        base = p["api"].rstrip("/")
    return (key or None), base


# ---------------------------------------------------------------------------
# objective —— 客观指标采集（零网络、无 key）
# ---------------------------------------------------------------------------
def _count_chapter_words(md_text):
    """按 ## 标题切章节，返回 [(标题, 字数)]。无标题则整体算一节。"""
    lines = md_text.splitlines()
    chapters = []
    cur_title = "(全文)"
    cur = []
    for ln in lines:
        m = re.match(r"^##\s+(.+)$", ln.strip())
        if m:
            if cur or cur_title != "(全文)":
                chapters.append((cur_title, sum(len(c) for c in cur)))
            cur_title = m.group(1).strip()
            cur = []
        else:
            cur.append(ln)
    chapters.append((cur_title, sum(len(c) for c in cur)))
    return chapters


def _count_ledger(ledger_path):
    """台账条目数（来源/引用文献数）。兼容 cited.json 与 delivery.json 两种形态。"""
    try:
        with open(ledger_path, encoding="utf-8") as f:
            data = json.load(f)
    except OSError:
        return None
    if isinstance(data, dict):
        # 找装条目的键：entries / citations / sources / papers / items
        for k in ("entries", "citations", "sources", "papers", "items", "references"):
            if isinstance(data.get(k), list):
                return len(data[k])
        # 若 data 本身是 {"<键>": {...}} 且值是含 doi/title 的对象，按 1 条计
        vals = [v for v in data.values() if isinstance(v, dict)]
        if vals and all(("doi" in v or "title" in v or "id" in v) for v in vals):
            return len(vals)
        return None
    if isinstance(data, list):
        return len(data)
    return None


def _run_delivery_gate(report_path, ledger_path):
    """调 check_report.py 的门禁输出，解析 FAIL/WARN 数。失败返回 None（不阻塞客观项）。"""
    from check_report import main as check_main  # 同目录模块复用
    import io
    import contextlib
    buf = io.StringIO()
    sys.argv = ["check_report.py", report_path, "--citation-ledger", ledger_path]
    try:
        with contextlib.redirect_stdout(buf):
            code = check_main()
    except SystemExit as e:
        code = e.code if isinstance(e.code, int) else 1
    except Exception:
        return None
    out = buf.getvalue()
    m = re.search(r"FAIL\s+(\d+)", out)
    w = re.search(r"WARN\s+(\d+)", out)
    if m is None:
        return None
    return {
        "exit": code,
        "fail": int(m.group(1)),
        "warn": int(w.group(1)) if w else 0,
    }


def cmd_objective(args):
    try:
        with open(args.report, encoding="utf-8") as f:
            md = f.read()
    except OSError as e:
        print(f"[self_eval] 读取报告失败: {e}", file=sys.stderr)
        return 1
    chapters = _count_chapter_words(md)
    gate = None
    ledger = None
    if args.citation_ledger:
        ledger = _count_ledger(args.citation_ledger)
        gate = _run_delivery_gate(args.report, args.citation_ledger)
    total_words = sum(w for _, w in chapters)
    result = {
        "mode": "objective",
        "report": args.report,
        "total_chars": total_words,
        "chapter_count": len(chapters),
        "chapters": [{"title": t, "chars": c} for t, c in chapters],
        "ledger_entries": ledger,
        "delivery_gate": gate,
    }
    _emit(result, args.format)
    return 0


# ---------------------------------------------------------------------------
# judge —— LLM-as-judge 多采样平均
# ---------------------------------------------------------------------------
_JUDGE_SYSTEM = (
    "你是一个严格的学术综述质量评审员。下面给你一份调研综述/报告，"
    "请按 7 个维度逐项打分。每个维度只输出 1-5 的整数（1=很差 3=中等 5=优秀），"
    "并给一句 30 字以内的判定理由。最后输出 JSON（不要 markdown code fence），"
    "格式固定为：{\"scores\": {\"Angle\":1,\"Coverage\":2,...}, "
    "\"notes\": {\"Angle\":\"理由\",...}, \"overall\": 3}"
)


def _build_user_prompt(md_text, message):
    dims_txt = "\n".join(f"- {name}: {desc}" for name, desc in DIMS)
    head = f"简评标题: {message}\n\n" if message else ""
    return (
        f"{head}请评审以下综述（按 7 维打分 1-5）：\n\n"
        f"评分维度：\n{dims_txt}\n\n"
        f"--- 待评审报告 ---\n{md_text[:12000]}"
    )


def _chat_once(base, key, model, messages, timeout=120):
    """调 OpenAI 兼容 /chat/completions，返回 (content, error)。"""
    url = base.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.8,      # 采样多样性 -> 多次平均更有意义
        "max_tokens": 800,
    }).encode("utf-8")
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}",
        "User-Agent": "sciverse-deep-research/0.2",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8", errors="replace"))
        content = data["choices"][0]["message"]["content"]
        return content, None
    except Exception as e:
        return None, f"{type(e).__name__}: {e}"


def _parse_scores(content):
    """从 judge 回复里抽出 {Dimension: int}。容忍 code fence 与前后废话。"""
    text = content.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S)
    if fence:
        text = fence.group(1)
    m = re.search(r"\{.*\}", text, re.S)
    scores = {}
    if m:
        try:
            obj = json.loads(m.group(0))
        except json.JSONDecodeError:
            obj = None
        if obj:
            src = obj.get("scores", obj)
            for name in DIM_NAMES:
                v = src.get(name)
                if isinstance(v, (int, float)):
                    scores[name] = float(v)
    # 兜底：正则抓 "Name": N
    if len(scores) < len(DIM_NAMES):
        for name in DIM_NAMES:
            if name in scores:
                continue
            mm = re.search(rf'"{re.escape(name)}"\s*:\s*(\d+)', text)
            if mm:
                scores[name] = float(mm.group(1))
    return scores


def cmd_judge(args):
    key, base = _get_key()
    if not key:
        print(
            "[self_eval] judge 需要 PJLab API key，但未找到。\n"
            f"  已检查: env {ENV_KEY} 与 {CONFIG_PATH} 的 providers.pujiang-deepseek.api_key。\n"
            "  红线: key 不从仓库读取。可用客观指标（objective 模式）替代，或先配置 key。",
            file=sys.stderr,
        )
        return 3
    try:
        with open(args.report, encoding="utf-8") as f:
            md = f.read()
    except OSError as e:
        print(f"[self_eval] 读取报告失败: {e}", file=sys.stderr)
        return 1
    per_dim = {d: [] for d in DIM_NAMES}
    samples_ok = 0
    last_err = None
    messages = [
        {"role": "system", "content": _JUDGE_SYSTEM},
        {"role": "user", "content": _build_user_prompt(md, args.message)},
    ]
    for i in range(args.samples):
        content, err = _chat_once(base, key, JUDGE_MODEL, messages, timeout=args.timeout)
        if err:
            last_err = err
            print(f"[self_eval] 第 {i+1}/{args.samples} 次采样失败: {err}", file=sys.stderr)
            continue
        sc = _parse_scores(content)
        if not sc:
            print(f"[self_eval] 第 {i+1}/{args.samples} 次无法解析分数: {content[:200]!r}", file=sys.stderr)
            last_err = "unparseable judge output"
            continue
        for d, v in sc.items():
            per_dim.setdefault(d, []).append(v)
        samples_ok += 1
    if samples_ok == 0:
        print(f"[self_eval] judge 完全失败（0/{args.samples} 采样成功）。{last_err}", file=sys.stderr)
        return 1
    summary = {}
    for d in DIM_NAMES:
        vals = per_dim.get(d) or []
        if vals:
            mean = statistics.mean(vals)
            rng = (max(vals) - min(vals)) if len(vals) > 1 else 0.0
            summary[d] = {"mean": round(mean, 2), "range": round(rng, 2), "n": len(vals)}
        else:
            summary[d] = {"mean": None, "range": None, "n": 0}
    used = [summary[d]["mean"] for d in DIM_NAMES if summary[d]["mean"] is not None]
    overall = round(statistics.mean(used), 2) if used else None
    result = {
        "mode": "judge",
        "report": args.report,
        "model": JUDGE_MODEL,
        "samples": args.samples,
        "samples_ok": samples_ok,
        "base_url": base,
        "per_dimension": summary,
        "overall_mean": overall,
        "note": "judge 分数为 LLM 主观自评，需与 objective 硬指标一起看",
    }
    _emit(result, args.format)
    return 0


# ---------------------------------------------------------------------------
# 输出 & 自检
# ---------------------------------------------------------------------------
def _emit(result, fmt):
    if fmt == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    if result["mode"] == "objective":
        print(f"objective: {result['report']}")
        print(f"  总字符 {result['total_chars']} / {result['chapter_count']} 章")
        for c in result["chapters"]:
            print(f"    - {c['title']}: {c['chars']}")
        if result["ledger_entries"] is not None:
            print(f"  台账来源数(引用文献) = {result['ledger_entries']}")
        if result["delivery_gate"]:
            g = result["delivery_gate"]
            print(f"  交付门禁 exit={g['exit']} FAIL={g['fail']} WARN={g['warn']}")
    else:
        print(f"judge: {result['report']}  model={result['model']}  采样 {result['samples_ok']}/{result['samples']}")
        for d in DIM_NAMES:
            s = result["per_dimension"][d]
            if s["mean"] is not None:
                print(f"  {d:11s} mean={s['mean']:<5} range={s['range']}  (n={s['n']})")
            else:
                print(f"  {d:11s} --   (未采到)")
        print(f"  overall_mean = {result['overall_mean']}")


def _selftest():
    """离线自检：不碰网络、不需要 key。断言语法契约与 key 来源逻辑。"""
    ok = True
    def chk(name, cond, detail=""):
        global ok
        print(f"[{'PASS' if cond else 'FAIL'}] {name} {detail}")
        if not cond:
            ok = False

    # 1) 7 维齐
    chk("7 维门禁维度齐全", DIM_NAMES == ["Angle", "Coverage", "Citation",
        "Taxonomy", "Calibration", "Weaving", "Insight"], f"{DIM_NAMES}")

    # 2) 客观章节切分
    md = "## 一、简介\nabc 12\n## 二、方法\nxyz\n\n## 三、结论\nend"
    chs = _count_chapter_words(md)
    chk("objective 章节切分=3 章", len(chs) == 3, f"{chs}")
    chk("objective 全文字符=12", sum(w for _, w in chs) == 12, f"{sum(w for _, w in chs)}")

    # 3) 台账计数
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "ledger.json")
        with open(p, "w", encoding="utf-8") as f:
            json.dump({"entries": [{"doi": "a"}, {"doi": "b"}, {"doi": "c"}]}, f)
        chk("ledger 计数=3", _count_ledger(p) == 3, f"{_count_ledger(p)}")
        p2 = os.path.join(td, "ledger2.json")
        with open(p2, "w", encoding="utf-8") as f:
            json.dump([{"title": "x"}], f)
        chk("ledger list 形态=1", _count_ledger(p2) == 1, f"{_count_ledger(p2)}")

    # 4) key 来源：宿主 config 解析函数
    prov = _load_yaml_key(CONFIG_PATH)
    if os.path.exists(CONFIG_PATH):
        p = prov.get("pujiang-deepseek", {})
        chk("config 提取到 api_key 字段", "api_key" in p, f"{p.get('api_key','')[:6]}...")
        chk("config key 长度合理(<=60)", not (p.get("api_key") and len(p.get("api_key", "")) > 60),
            f"len={len(p.get('api_key',''))}")
    else:
        chk("config 不存在->返回空 dict", prov == {})

    # 5) 环境变量 key 优先级高于 config
    old = os.environ.get(ENV_KEY)
    os.environ[ENV_KEY] = "sk-ENVDUMMY00000000000000000000000000000000"
    k, _ = _get_key()
    chk("env key 优先级高于 config", k == "sk-ENVDUMMY00000000000000000000000000000000", f"{k[:10]}...")
    if old is None:
        os.environ.pop(ENV_KEY, None)
    else:
        os.environ[ENV_KEY] = old

    # 6) 不存在的 config 返回空
    chk("_load_yaml_key 对不存在文件返回 {}", _load_yaml_key("/nonexistent/x.yaml") == {})

    print(f"summary: {'ALL PASS' if ok else 'HAS FAIL'}")
    return 0 if ok else 1


def main():
    ap = argparse.ArgumentParser(description="sciverse 自评工具链（LLM-as-judge + 客观指标）")
    ap.add_argument("--format", default="text", choices=["text", "json"])
    ap.add_argument("--selftest", action="store_true", help="离线自检")
    sub = ap.add_subparsers(dest="mode")

    so = sub.add_parser("objective", help="客观指标采集（无 key）")
    so.add_argument("--report", required=True)
    so.add_argument("--citation-ledger", default=None)

    sj = sub.add_parser("judge", help="LLM-as-judge 多采样平均")
    sj.add_argument("--report", required=True)
    sj.add_argument("--samples", type=int, default=5)
    sj.add_argument("--message", default=None)
    sj.add_argument("--timeout", type=int, default=480, help="单次 judge 采样秒级超时（deepseek 慢时需>120）")

    args = ap.parse_args()
    if args.selftest:
        return _selftest()
    if args.mode == "objective":
        return cmd_objective(args)
    if args.mode == "judge":
        return cmd_judge(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
