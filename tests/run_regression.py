#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_regression.py — sciverse-deep-research 一键回归门禁（stdlib 零依赖）

用法：
    python3 tests/run_regression.py            # 快速回归
    python3 tests/run_regression.py --slow     # 含慢速项（md_to_pdf 真实 LaTeX 编译）

设计：
    - 零依赖：直接 `python3` 可跑（与 scripts/ 的零依赖哲学一致）。
    - 每个用例 = 一个真实可复现命令 + 对输出/退出码的断言。
    - 新增脚本或新门禁时，用 @check 登记一个用例即可；审查员补用例也加在这里。

退出码：0 = 全绿；1 = 有 FAIL。
"""
import os
import re
import json
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "skills", "sciverse-deep-research", "scripts")

CHECKS = []       # (name, fn)，定义顺序即执行顺序
SLOW_CHECKS = []  # 仅 --slow 时执行


def run_script(script, *args):
    """跑 scripts/ 下的脚本，返回 (exit_code, 合并输出)。"""
    p = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS, script)] + list(args),
        cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    return p.returncode, p.stdout


def last_line(out):
    lines = out.strip().splitlines()
    return lines[-1] if lines else ""


def check(name, slow=False):
    """装饰器：登记一个回归用例。用例函数返回 (ok: bool, detail: str)。"""
    def deco(fn):
        (SLOW_CHECKS if slow else CHECKS).append((name, fn))
        return fn
    return deco


# ---------- 快速用例 ----------

@check("citation_ledger --selftest")
def _selftest_ledger():
    code, out = run_script("citation_ledger.py", "--selftest")
    return code == 0, last_line(out)


@check("check_report --selftest")
def _selftest_check():
    code, out = run_script("check_report.py", "--selftest")
    return code == 0, last_line(out)


@check("verify_citations --selftest")
def _selftest_verify():
    code, out = run_script("verify_citations.py", "--selftest")
    return code == 0, last_line(out)


@check("spectral-demo 台账 validate = FAIL 0")
def _ledger_validate():
    code, out = run_script(
        "citation_ledger.py", "validate",
        "--ledger", "examples/spectral-dimension-demo/.workflow/citation_ledger.json")
    return code == 0 and "FAIL 0" in out, out.strip()


@check("dft-kL-demo 交付门禁 = FAIL 0 / WARN 0")
def _delivery_gate():
    code, out = run_script(
        "check_report.py", "examples/dft-kL-demo/.workflow/final.md",
        "--citation-ledger",
        "examples/dft-kL-demo/.workflow/citation_ledger.json.delivery.json")
    ok = code == 0 and "FAIL 0" in out and "WARN 0" in out
    return ok, last_line(out)


@check("space-compute-demo 台账 validate = FAIL 0")
def _sc_ledger_validate():
    code, out = run_script(
        "citation_ledger.py", "validate",
        "--ledger", "examples/space-compute-demo/.workflow/citation_ledger.json")
    return code == 0 and "FAIL 0" in out, out.strip()


@check("space-compute-demo 交付门禁 = FAIL 0 / WARN 0")
def _sc_delivery_gate():
    code, out = run_script(
        "check_report.py", "examples/space-compute-demo/.workflow/final.md",
        "--citation-ledger",
        # 用已跟踪的 output delivery（.workflow/*.delivery.json 被 gitignore/未跟踪，
        # clean clone 里不存在，门禁必须引用入仓的 output/引用台账_delivery.json）
        "examples/space-compute-demo/output/引用台账_delivery.json")
    ok = code == 0 and "FAIL 0" in out and "WARN 0" in out
    return ok, last_line(out)


@check("space-compute-demo 台账 compile 幂等（draft -> final 可重铸）")
def _sc_compile_idempotent():
    with tempfile.TemporaryDirectory() as td:
        out_md = os.path.join(td, "final.md")
        code, out = run_script(
            "citation_ledger.py", "compile",
            "--ledger", "examples/space-compute-demo/.workflow/citation_ledger.json",
            "--report", "examples/space-compute-demo/.workflow/draft.md",
            "--output", out_md)
        if code != 0:
            return False, last_line(out)
        with open(out_md) as f:
            compiled = f.read()
        leftover_keys = re.search(r"\[@[^\]]+\]", compiled) is not None
        has_numcite = re.search(r"\[\d+\]", compiled) is not None
        return (not leftover_keys) and has_numcite, \
            f"残留键={leftover_keys} 数字引用={has_numcite}"


@check("detect_latex 探测可执行")
def _detect_latex():
    # 不断言 level=full（没装 LaTeX 的机器也应跑通），只要求正常退出且给出 level
    code, out = run_script("detect_latex.py")
    return code == 0 and "level=" in out, last_line(out)


# O1(P5) Phase A：阶段单元工件契约 + 续跑确定性 + 预算记账（治上下文漂移根因的轻量验证底盘）。
@check("O1 PhaseA stage_contract 工件契约 check")
def _phasea_contract():
    code, out = run_script("stage_contract.py", "check", "examples/dft-kL-demo/.workflow")
    return code == 0 and "PASS" in out, last_line(out)


@check("O1 PhaseA 续跑确定性（compile 幂等，换上下文不漂移）")
def _phasea_resume_idempotent():
    code, out = run_script("stage_contract.py", "resume-idempotent", "examples/dft-kL-demo/.workflow")
    return code == 0 and "逐字节一致" in out, last_line(out)


@check("O1 PhaseA budget 超限记账 = exit 1（漂移触发器，不得带病完工）")
def _phasea_budget_over():
    import json as _json
    with tempfile.TemporaryDirectory() as td:
        cf = os.path.join(td, "cost.json"); bf = os.path.join(td, "b.json")
        with open(cf, "w") as f:
            _json.dump({"spent": {"synthesis": 999999}}, f)
        with open(bf, "w") as f:
            _json.dump({"limits": {"synthesis": 100}, "cost_log": cf}, f)
        code, out = run_script("stage_contract.py", "budget", bf, "examples/dft-kL-demo/.workflow")
        return code == 1 and "超预算" in out, last_line(out)


# md_to_pdf 的 normalize/mathify 是纯文本变换（不触发 LaTeX/Pandoc），
# 可确定性离线断言：ASCII 直引号归零、裸 `x_i` 焊接成 `$x_{i}$` 数学、
# smartquote 不误伤已归档的 $...$ 数学块。这是 M3 渲染修复的根因回归。
@check("md_to_pdf normalize 直引号归零 + 裸公式数学化")
def _md_normalize():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "md_to_pdf", os.path.join(SCRIPTS, "md_to_pdf.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cases = [
        # (输入, 必须含, 必须不含)
        (u'他说"这是关键"', u'“这是关键”', u'"'),
        (u'公式 x_i 与 t^(−d_s/2) 相关', u'$x_{i}$', None),
        (u'已有 $\\kappa$ 数学块保留', u'$\\kappa$', None),
    ]
    fails = []
    for src, must_have, must_not in cases:
        out = m.normalize(src)
        if must_have and must_have not in out:
            fails.append(f"{src!r} -> 缺 {must_have!r}: {out!r}")
        if must_not and must_not in out:
            fails.append(f"{src!r} -> 意外含 {must_not!r}: {out!r}")
    if fails:
        return False, "; ".join(fails)
    # 抓一个真实遗留稿做基准：230 个直引号应全部归零（若不存在该稿则跳过，不断言）
    demo = os.path.join(
        ROOT, "examples", "spectral-dimension-survey",
        "谱维数与拉普拉斯谱_随机行走综述.md")
    if os.path.isfile(demo):
        raw = open(demo, encoding="utf-8").read()
        n_raw = raw.count('"')
        n_norm = m.normalize(raw).count('"')
        if n_raw and n_norm != 0:
            fails.append(f"遗留稿直引号 {n_raw} -> normalized 后仍剩 {n_norm}")
    if fails:
        return False, "; ".join(fails)
    return True, "直引号归零 + 数学化 OK"


# M3 收尾回归：审查员审计提的潜伏缺陷——混排弯引号锚点方向、连写下标+上标不焊。
# 覆盖：①多对交替弯引号/代码内引号保护；②裸公式焊接（含连写 _^）；③已归档
# $..$/代码块不被误伤；④normalize 幂等。stdlib 零依赖。
@check("md_to_pdf normalize edge（混排引号锚点 + 连写脚本焊接 + 幂等）")
def _md_normalize_edge():
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "md_to_pdf", os.path.join(SCRIPTS, "md_to_pdf.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    fails = []

    def eq(name, src, want):
        got = m.normalize(src)
        if got != want:
            fails.append(f"{name}: {src!r} -> {got!r}, 期望 {want!r}")

    # ① 混排弯引号锚点方向（ASCII 对方向不再反）+ 多对交替 + 代码内引号保护
    eq("混排弯引号锚点", u'“A” then "B"', u'“A” then “B”')
    eq("交替两对", u'"甲" 与 "乙"', u'“甲” 与 “乙”')
    # 代码跨度内的 " 不参与配对（保护段原样保留）
    eq("代码内引号保护", u'`print("a")` 前后 "x"', u'`print("a")` 前后 “x”')
    # 裸 ASCII 单对归零
    eq("裸一对归零", u'他说"关键"', u'他说“关键”')

    # ② 裸公式焊接：连写下标+上标并入同一数学块；花括号形态保持
    eq("连写下标+上标", u'a_1^2', u'$a_{1}^{2}$')
    eq("连写上标+下标", u'a^2_1', u'$a^{2}_{1}$')
    eq("三段连写", u'a_1^2_3', u'$a_{1}^{2}_{3}$')
    eq("花括号形态保持", u'n^{-d_s/2}', u'$n^{-d_s/2}$')
    eq("裸单词下标", u'd_s', u'$d_{s}$')
    eq("裸组合波浪线", u'd\u0303', u'$\\tilde{d}$')

    # ③ 已归档 $..$ / 代码块不被误伤
    eq("已归档数学块保留", u'已含 $\\kappa$ 块', u'已含 $\\kappa$ 块')
    eq("数学块内引号不被改", u'$"a"$ 保留', u'$"a"$ 保留')
    eq("代码块内数学不加焊", u'`x_i` 是代码', u'`x_i` 是代码')

    # ④ normalize 幂等
    for src in (u'“A” then "B"', u'a_1^2', u'n^{-d_s/2}', u'他说"关键" 与 $\\kappa$'):
        once = m.normalize(src)
        twice = m.normalize(once)
        if once != twice:
            fails.append(f"幂等失效: {src!r} -> {once!r} != {twice!r}")

    if fails:
        return False, "; ".join(fails)
    return True, "edge 全过（引号锚点/连写脚本/归档保护/幂等）"



# fetch_sources.py 是网络脚本（arXiv/OpenAlex），回归只做离线 CLI 契约断言，
# 不触发真实 HTTP，保证任何环境（含无网/离线 CI）下确定性可复现。
@check("fetch_sources --list 离线可用")
def _fetch_list():
    code, out = run_script("fetch_sources.py", "--list")
    # 退出 0，且把 arxiv/openalex 都列出来（so known sources contract held）
    return code == 0 and "arxiv" in out and "openalex" in out, last_line(out)


@check("fetch_sources 未知来源 = exit 2（不静默降级）")
def _fetch_unknown_source():
    code, out = run_script("fetch_sources.py", "notasource", "q")
    # 未识别来源必须报错退出 2，绝不能去网络、更不能当空结果返回 0
    return code == 2 and "未知来源" in out, f"exit={code} {last_line(out)}"


@check("fetch_sources 缺 query = exit 2")
def _fetch_missing_query():
    code, out = run_script("fetch_sources.py", "arxiv")
    # 缺检索词是用户输入错误（exit 2），不是网络故障（exit 1）
    return code == 2 and "缺少 query" in out, f"exit={code} {last_line(out)}"


# self_eval.py（P1 自评工具链）离线契约断言：不触发真实 HTTP、不需要 API key，
# 保住「key 永不进 git / judge 脱网也可验证语义」这条红线。
@check("self_eval --selftest 离线 ALL PASS")
def _selfeval_selftest():
    code, out = run_script("self_eval.py", "--selftest")
    return code == 0 and "ALL PASS" in out, last_line(out)


@check("self_eval objective 客观指标（无 key 也能跑）")
def _selfeval_objective():
    code, out = run_script(
        "self_eval.py", "objective", "--report",
        "examples/dft-kL-demo/.workflow/final.md")
    ok = code == 0 and "total_chars" not in out and "总字符" in out
    return ok, last_line(out)


@check("self_eval judge 无 key = exit 3（红线：不静默降级）")
def _selfeval_judge_nokey():
    # 用空 HOME + 空环境变量跑 judge：config 也读不到 key，
    # 必须因缺 key 退出 3，绝不能去网络或打空分。
    import os as _os
    with tempfile.TemporaryDirectory() as td:
        env = dict(_os.environ)
        env.pop("SCIVERSE_DEEPSEEK_API_KEY", None)
        env["HOME"] = td            # ~/.hermes/config.yaml 不存在 -> 无 key
        p = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "self_eval.py"), "judge",
             "--report", "examples/dft-kL-demo/.workflow/final.md"],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, env=env)
    last = p.stdout.strip().splitlines()[-1] if p.stdout.strip() else ""
    return p.returncode == 3, f"exit={p.returncode} {last}"


# P2：compile 多格式引用输出（--style）。固定离线样例断言各风格渲染差异 +
# bibtex 可解析 + 默认无 --style 时与现有格式逐字节一致（向后兼容烟囱）。
P2LEDGER = {"entries": [
    {"id": 1, "first_author": "Ullah", "authors": "Ullah Z, Khan R",
     "year": "2025", "title": "High-temperature thermoelectric",
     "venue": "Computational Materials Science", "verify_status": "VERIFIED",
     "volume": "512", "issue": "1", "pages": "115000", "doi": "10.1016/x",
     "aliases": ["Ullah2025"]},
    {"id": 2, "first_author": "Broido", "authors": "Broido DA, Malorny M",
     "year": "2007", "title": "Intrinsic lattice thermal conductivity",
     "venue": "Applied Physics Letters", "verify_status": "UNVERIFIED",
     "volume": "91", "pages": "231922", "aliases": ["Broido2007"]},
]}


def _p2_render(style):
    with tempfile.TemporaryDirectory() as td:
        lp = os.path.join(td, "ledger.json")
        with open(lp, "w", encoding="utf-8") as f:
            json.dump(P2LEDGER, f, ensure_ascii=False)
        if style:
            code, out = run_script("citation_ledger.py", "print-refs",
                                   "--ledger", lp, "--style", style)
        else:
            code, out = run_script("citation_ledger.py", "print-refs",
                                   "--ledger", lp)
        return code, out


@check("P2 默认无 --style = 现有格式（逐字节向后兼容）")
def _p2_default_backcompat():
    code, out = _p2_render(None)
    expect = ("[1] Ullah Z, Khan R, “High-temperature thermoelectric,” "
              "Computational Materials Science, 2025.\n"
              "[2] Broido DA, Malorny M, “Intrinsic lattice thermal "
              "conductivity,” Applied Physics Letters, 2007.（未核验）")
    return code == 0 and out.strip() == expect, last_line(out)


@check("P2 apa/ieee/gbt7714 渲染差异可见")
def _p2_styles_differ():
    _, apa = _p2_render("apa")
    _, ieee = _p2_render("ieee")
    _, gbt = _p2_render("gbt7714")
    ok = ("(2025)." in apa and "https://doi.org/10.1016/x" in apa
          and "[1] Z. Ullah" in ieee and "doi:10.1016/x" in ieee
          and "[J]." in gbt)
    return ok, f"apa/ieee/gbt 各自特征串命中"


@check("P2 apa/ieee/gbt7714 三种输出互不相同")
def _p2_styles_mutually_distinct():
    _, a = _p2_render("apa")
    _, b = _p2_render("ieee")
    _, c = _p2_render("gbt7714")
    return len({a.strip(), b.strip(), c.strip()}) == 3, "三种风格输出互异"


@check("P2 bibtex 侧车可解析（& 无双逗号 & note 标注）")
def _p2_bibtex():
    code, out = _p2_render("bibtex")
    ok = (code == 0 and "@article{Ullah2025," in out
          and "@article{Broido2007," in out
          and "@article{" in out
          and "}}," not in out.replace("}},", "")  # bibtex 不应有 }}, 双尾逗
          and "note = {未核验}," in out)
    return ok, last_line(out)


@check("P2 compile --style bibtex --bib-out 落盘可解析")
def _p2_compile_bibout():
    with tempfile.TemporaryDirectory() as td:
        lp = os.path.join(td, "ledger.json")
        with open(lp, "w", encoding="utf-8") as f:
            json.dump(P2LEDGER, f, ensure_ascii=False)
        dp = os.path.join(td, "draft.md")
        with open(dp, "w", encoding="utf-8") as f:
            f.write("# 综述\n两篇 [@Ullah2025; @Broido2007] 均被引用。\n## 参考文献\n")
        bibout = os.path.join(td, "refs.bib")
        code, out = run_script("citation_ledger.py", "compile", "--ledger", lp,
                               "--report", dp, "--style", "bibtex",
                               "--bib-out", bibout)
        ok = code == 0 and os.path.exists(bibout)
        if ok:
            with open(bibout, encoding="utf-8") as f:
                bib = f.read()
            ok = "@article{Ullah2025," in bib and "@article{Broido2007," in bib
        return ok, f"exit={code} bib_exists={os.path.exists(bibout)}"


@check("demo 台账 compile 幂等（draft -> final 可重铸）")
def _compile_idempotent():
    with tempfile.TemporaryDirectory() as td:
        out_md = os.path.join(td, "final.md")
        code, out = run_script(
            "citation_ledger.py", "compile",
            "--ledger", "examples/dft-kL-demo/.workflow/citation_ledger.json",
            "--report", "examples/dft-kL-demo/.workflow/draft.md",
            "--output", out_md)
        if code != 0:
            return False, last_line(out)
        with open(out_md) as f:
            compiled = f.read()
        # 编译产物不应残留 [@键]，且应含数字编号引用
        leftover_keys = re.search(r"\[@[^\]]+\]", compiled) is not None
        has_numcite = re.search(r"\[\d+\]", compiled) is not None
        return (not leftover_keys) and has_numcite, \
            f"残留键={leftover_keys} 数字引用={has_numcite}"


# ---------- 慢速用例（--slow 才跑） ----------

@check("md_to_pdf 真实编译 spectral-demo final.md", slow=True)
def _md_to_pdf_real():
    with tempfile.TemporaryDirectory() as td:
        dst = os.path.join(td, "final.md")
        shutil.copy("examples/spectral-dimension-demo/.workflow/final.md", dst)
        code, out = run_script("md_to_pdf.py", dst)
        pdf = dst[:-len(".md")] + ".pdf"
        ok = code == 0 and os.path.exists(pdf) and os.path.getsize(pdf) > 10_000
        return ok, last_line(out)


# ---------- 入口 ----------

def main():
    checks = list(CHECKS)
    if "--slow" in sys.argv:
        checks += SLOW_CHECKS

    results = []
    for name, fn in checks:
        try:
            ok, detail = fn()
        except Exception as e:  # 用例自身异常也算 FAIL，不让回归静默跳过
            ok, detail = False, f"用例异常: {e!r}"
        results.append((name, ok, detail))

    n_fail = 0
    for name, ok, detail in results:
        if not ok:
            n_fail += 1
            print(f"[FAIL] {name}  | {str(detail)[:160]}")
        else:
            print(f"[PASS] {name}")
    print(f"summary: PASS {len(results) - n_fail} / FAIL {n_fail}")
    return 1 if n_fail else 0


if __name__ == "__main__":
    sys.exit(main())
