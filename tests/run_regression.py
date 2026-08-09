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


@check("detect_latex 探测可执行")
def _detect_latex():
    # 不断言 level=full（没装 LaTeX 的机器也应跑通），只要求正常退出且给出 level
    code, out = run_script("detect_latex.py")
    return code == 0 and "level=" in out, last_line(out)


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
