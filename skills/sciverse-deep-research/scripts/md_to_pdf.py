#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_to_pdf.py — 把本 skill 交付的 final.md（Markdown 综述）用本地 LaTeX 渲染成 PDF

定位：交付环节的可选第二步。在 detect_latex.py 判定为 full 的前提下执行；
产出与 final.md 同名的 .pdf 文件，与 Markdown 源稿并存（MD 始终是源稿，
PDF 是其排版视图——本 skill 仍以 Markdown 为唯一事实源，PDF 不回写正文）。

转换策略（零依赖，不依赖 pandoc）：
  1. 读取 Markdown，逐行解析成结构化为本 skill 综述骨架的子集：
     - # / ## / ### 标题        → section*/subsection*/subsubsection*（无自动编号，
       保留正文手写序号"一、""3.1"）
     - GFM 表格（|...|）        → longtable/tabular（v2：修复此前表格完全不渲染）
     - 无序/有序列表           → itemize/enumerate
     - 空行分段正文             → 分段
     - 行内 **粗体**、`代码`    → \\textbf{} / \\texttt{}
     - 希腊字母/数学符（κ θ γ ρ σ ν α 等，综述高频）→ $\\kappa$ 等数学模式
       （v2：修复此前希腊字母因字体缺字形而乱码成 ff_/空）
       （序数标记 ★ 映射为 $\\bigstar$）
  2. 用 xelatex 编译（UTF-8 + ctex 中文），PDF 与 .md 同目录。
  3. 保留 .tex 中间文件供排错（--keep-tex）；默认成功后删除。

用法：
  python3 md_to_pdf.py final.md [--keep-tex] [--engine xelatex]
  python3 md_to_pdf.py final.md --out 自定义路径.pdf

本脚本 Python 标准库零依赖。xelatex 路径自动探测（PATH + /Library/TeX/texbin）。
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

# --- 引擎/宏包探测（复用 detect_latex 同款路径策略，避免跨文件耦合） ---
EXTRA_BIN_DIRS = ["/Library/TeX/texbin", "/usr/local/texlive", "/usr/bin", "/usr/local/bin"]


def find_bin(name):
    p = shutil.which(name)
    if p:
        return p
    for d in EXTRA_BIN_DIRS:
        cand = os.path.join(d, name)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


# 希腊字母/常用数学符 → LaTeX 数学模式命令（综述正文高频出现，缺映射会因
# 中文字体无该字形而渲染成乱码/空白；这是 v2 修复的关键之一）
GREEK_MAP = {
    "\u03ba": "\\kappa",     # κ
    "\u03b8": "\\theta",     # θ
    "\u03b3": "\\gamma",     # γ
    "\u03b1": "\\alpha",     # α
    "\u03c1": "\\rho",       # ρ
    "\u03c3": "\\sigma",     # σ
    "\u03bd": "\\nu",        # ν
    "\u03bb": "\\lambda",    # λ
    "\u03bc": "\\mu",        # μ
    "\u03c4": "\\tau",       # τ
    "\u03a9": "\\Omega",     # Ω
    "\u0394": "\\Delta",     # Δ
    "\u2148": "\\imath",     # ⅈ (虚数单位)
}

# 其他综述高频但中文字体可能缺字形的符号 → LaTeX 命令
SYMBOL_MAP = {
    "\u2192": "\\ensuremath{\\rightarrow}",     # →
    "\u2194": "\\ensuremath{\\leftrightarrow}",  # ↔
    "\u2227": "\\ensuremath{\\wedge}",           # ∧ (逻辑与 = 交集语境)
    "\u2229": "\\ensuremath{\\cap}",             # ∩
    "\u222a": "\\ensuremath{\\cup}",             # ∪
    "\u2265": "\\ensuremath{\\geq}",             # ≥
    "\u2264": "\\ensuremath{\\leq}",             # ≤
    "\u2260": "\\ensuremath{\\neq}",             # ≠
    "\u00d7": "\\ensuremath{\\times}",           # ×
    "\u00b1": "\\ensuremath{\\pm}",              # ±
    "\u2212": "\\ensuremath{-}",                 # − (数学减号)
    "\u2153": "\\ensuremath{\\tfrac{1}{3}}",     # ⅓
    "\u00b2": "\\ensuremath{^2}",                # ²
    "\u00b3": "\\ensuremath{^3}",                # ³
    "\u00fc": '\\"{u}',                          # ü
    "\u2026": "\\ldots",                         # …
    "\u2014": "---",                             # — 长破折号
    "\u201c": "``",                              # “ 左双引号 → LaTeX 开引号
    "\u201d": "''",                              # ” 右双引号 → LaTeX 闭引号
    "\u00b7": "\\ensuremath{\\cdot}",            # · 间隔点
}  # noqa: E501

STAR_MAP = {"\u2605": "\\bigstar", "\u2606": "\\bigstar", "\u260b": "\\bigstar"}


def _map_specials(s, placeholders):
    """把希腊字母/星号/特殊符号保护为占位符（在转义之前）。
    返回替换后的 s；占位符在函数返回时统一还原为 LaTeX 命令/数学形式。"""
    # 先清掉零宽组合上划线 U+0304（如 M̄/Ā 的音长符）：LaTeX 无法处理，删掉
    # 让其组合的基字符独立（或必要时保留基字符）
    s = s.replace("\u0304", "")
    # 星号 ★★★ -> 数学 $\\bigstar$（\bigstar 是 AMS 符号，必须在数学模式内；
    # 正文文本裸用报 invalid character。用一个不含反斜杠的纯文本占位标记
    # @@STAR_n@@（占位符不含 \，不会被步骤2的转义破坏），统一映射为 $\bigstar$）
    star_i = [0]
    def star_repl(m):
        key = f"@@STAR{len(placeholders)}@@"
        placeholders[key] = r"$\bigstar$"
        return key
    s = re.sub(r"[★☆☾☽]", star_repl, s)
    # 希腊字母逐个 -> $\\greek$
    for ch, cmd in GREEK_MAP.items():
        if ch in s:
            key = f"@@G{len(placeholders)}@@"
            placeholders[key] = "$" + cmd + "$"
            s = s.replace(ch, key)
    # 其他特殊符号 -> LaTeX 命令（含 \\ensuremath{...} 混排安全）
    for ch, cmd in SYMBOL_MAP.items():
        if ch in s:
            key = f"@@S{len(placeholders)}@@"
            placeholders[key] = cmd
            s = s.replace(ch, key)
    return s


def inline(s):
    """行内格式化：**粗**、`代码`、$数学$、希腊字母、★；返回 LaTeX 行。

    顺序要点：
      1. 保护 $..$ / $$..$$ 数学为占位符；
      1b.保护希腊字母/★（映射为数学，避免被步骤 2 转义破坏）；
      2. 再对剩余裸文本做特殊字符转义；
      3. 之后匹配 **粗体** 与 `代码`；
      4. 还原全部占位符。
    """
    placeholders = {}

    def math_repl(m):
        key = f"@@M{len(placeholders)}@@"
        placeholders[key] = m.group(0)
        return key

    # (1) 保护 $ 数学
    s = re.sub(r"\$\$[^$]+?\$\$", math_repl, s)          # display
    s = re.sub(r"(?<!\$)\$[^$\n]+?\$(?!\$)", math_repl, s)  # inline
    s = s.replace("$", r"\$")  # 残余孤立 $ 转义

    # (1b) 保护希腊字母/★（此时已完成 $ 转义，映射产生的 $..$ 不再被破坏）
    s = _map_specials(s, placeholders)

    # (2) 裸文本特殊字符转义
    s = (s.replace("\\", r"\textbackslash{}")
          .replace("{", r"\{").replace("}", r"\}")
          .replace("#", r"\#").replace("%", r"\%")
          .replace("&", r"\&").replace("_", r"\_")
          .replace("~", r"\textasciitilde{}")
          .replace("^", r"\textasciicircum{}"))

    # (3) 粗体 / 代码（此时转义已过，控制序列安全）
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)

    # (4) 还原所有占位符（数学/Greek）
    for k, v in placeholders.items():
        s = s.replace(k, v)
    return s


def _is_table_row(line):
    return "|" in line and line.strip().startswith("|")


def _handle_table(lines, i):
    """从 lines[i] 开始解析 GFM 表格，返回 (body_lines, next_i)。
    GFM 表格格式：首行表头 |a|b|，次行分隔 |---|---|（可选项），后续行数据。"""
    out = []
    rows = []
    j = i
    # 收集从 i 开始的连续 | 行（表头 + 可选分隔行 + 数据行）
    sep_idx = None
    k = j
    collected = []
    while k < len(lines) and _is_table_row(lines[k]):
        # 分隔行：内容是 -、:-, -:  组合
        cells = [c.strip() for c in lines[k].strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            if sep_idx is None:
                sep_idx = len(collected)
        else:
            collected.append([c for c in cells])
        if sep_idx is not None:
            break  # 分隔行后进入数据行循环
        k += 1
    # 上面逻辑简化：GFM 表 = 表头(1行) + 分隔行(1行) + 数据(N行)
    j = i
    header = None
    if j < len(lines) and _is_table_row(lines[j]):
        header = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        j += 1
    # 分隔行（可跳过）
    if j < len(lines) and _is_table_row(lines[j]):
        cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            header_len = len(header) if header else 0
            aligns = ["r" if c.startswith(":") and c.endswith(":") else
                      ("l" if c.startswith(":") else
                       ("r" if c.endswith(":") else "l")) for c in cells]
            j += 1
    else:
        aligns = ["l"] * (len(header) if header else 1)
    rows = []
    while j < len(lines) and _is_table_row(lines[j]):
        cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        rows.append(cells)
        j += 1
    # 列数
    ncol = max(len(header) if header else 0, max((len(r) for r in rows), default=0), 1)
    ncol = max(ncol, 1)
    while len(header or []) < ncol:
        header = (header or []) + [""]
    colspec = "l" * ncol
    out.append("\\begin{longtable}{" + colspec + "}")
    out.append("\\toprule")
    if header:
        out.append("  " + " & ".join(inline(c) for c in header) + r" \\")
    out.append("\\midrule")
    out.append("\\endhead")
    for row in rows:
        while len(row) < ncol:
            row.append("")
        out.append("  " + " & ".join(inline(c) for c in row[:ncol]) + r" \\")
    out.append("\\bottomrule")
    out.append("\\end{longtable}")
    out.append("")
    return out, j


def render(markdown_path, engine="xelatex"):
    with open(markdown_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    body = []
    in_code = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # 代码块整体跳过
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue

        # 标题（无自动编号，保留手写序号）
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            hashes, text = m.group(1), m.group(2)
            lvl = len(hashes)
            first_heading = body == [] or all(not x for x in body)
            if lvl == 1:
                if first_heading:
                    body.append("")
                    i += 1
                    continue
                body.append(f"\\section*{{{inline(text)}}}")
            elif lvl == 2:
                body.append(f"\\section*{{{inline(text)}}}")
            elif lvl == 3:
                body.append(f"\\subsection*{{{inline(text)}}}")
            else:
                body.append(f"\\subsubsection*{{{inline(text)}}}")
            body.append("")
            i += 1
            continue

        # 表格（GFM |a|b| —— v2 新增）
        if line.strip().startswith("|"):
            tbody, ni = _handle_table(lines, i)
            body.extend(tbody)
            i = ni
            continue

        # 无序列表
        if re.match(r"^[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                items.append(inline(re.sub(r"^[-*]\s+", "", lines[i])))
                i += 1
            body.append("\\begin{itemize}")
            for it in items:
                body.append(f"  \\item {it}")
            body.append("\\end{itemize}")
            body.append("")
            continue

        # 有序列表
        if re.match(r"^\d+\.\s+(.*)$", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            body.append("\\begin{enumerate}")
            for it in items:
                body.append(f"  \\item {it}")
            body.append("\\end{enumerate}")
            body.append("")
            continue

        # 空行 → 分段
        if line.strip() == "":
            i += 1
            continue

        # 普通正文段
        body.append(inline(line))
        body.append("")
        i += 1

    # 组装 LaTeX 骨架
    main = "\n".join(x for x in body).strip()
    title = first_title_or_default(lines)
    doc = (
        "\\documentclass[UTF8]{ctexart}\n"
        "\\usepackage{geometry}\n"
        "\\geometry{margin=2.5cm}\n"
        "\\usepackage{amsmath,amssymb}\n"
        "\\usepackage{longtable}\n"
        "\\usepackage{booktabs}\n"
        "\\usepackage[colorlinks=true,linkcolor=black,urlcolor=blue]{hyperref}\n"
        "\\setlength{\\parskip}{4pt}\n"
        "\\title{" + title + "}\n"
        "\\author{sciverse-deep-research}\n"
        "\\date{\\today}\n"
        "\n"
        "\\begin{document}\n"
        "\\maketitle\n"
        "\n"
        + main +
        "\n"
        "\\end{document}\n"
    )

    base = os.path.splitext(markdown_path)[0]
    tex_path = base + ".tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(doc)
    return tex_path


def first_title_or_default(lines):
    for line in lines:
        line = line.strip()
        if line.startswith("# "):
            return inline(line[2:])
    return "学术深度调研综述"


def build(tex_path, engine="xelatex", keep_tex=False):
    exe = find_bin(engine)
    if not exe:
        print(f"[md_to_pdf] 找不到引擎 {engine}；请先运行 detect_latex.py 确认 LaTeX 可用", file=sys.stderr)
        return 1
    base = os.path.splitext(tex_path)[0]
    cwd = os.path.dirname(tex_path) or "."
    try:
        r = subprocess.run(
            [exe, "-interaction=nonstopmode", "-halt-on-error", os.path.basename(tex_path)],
            cwd=cwd, capture_output=True, text=True, timeout=180,
        )
    except FileNotFoundError:
        print(f"[md_to_pdf] 引擎 {exe} 不可执行", file=sys.stderr)
        return 1
    pdf = base + ".pdf"
    if r.returncode == 0 and os.path.exists(pdf):
        print(f"[md_to_pdf] 生成 PDF: {pdf}")
        if not keep_tex:
            os.remove(tex_path)
        return 0
    print(f"[md_to_pdf] xelatex 失败(exit={r.returncode})", file=sys.stderr)
    log = base + ".log"
    if os.path.exists(log):
        print("  最近错误:", file=sys.stderr)
        for line in r.stdout.splitlines():
            if line.startswith("!") or "Error" in line or "error" in line:
                print("  " + line, file=sys.stderr)
    return 1


def main():
    ap = argparse.ArgumentParser(description="把 sciverse-deep-research 的 final.md 渲染成 PDF")
    ap.add_argument("md", help="Markdown 综述路径（.workflow/final.md）")
    ap.add_argument("--out", help="PDF 输出路径（默认与 md 同名）")
    ap.add_argument("--engine", default="xelatex", choices=["xelatex", "lualatex"])
    ap.add_argument("--keep-tex", action="store_true", help="保留中间 .tex 文件")
    args = ap.parse_args()

    if not os.path.exists(args.md):
        print(f"[md_to_pdf] 找不到文件: {args.md}", file=sys.stderr)
        return 1

    tex_path = render(args.md, args.engine)
    rc = build(tex_path, args.engine, args.keep_tex)
    if rc == 0 and args.out and args.out != os.path.splitext(args.md)[0] + ".pdf":
        shutil.move(os.path.splitext(args.md)[0] + ".pdf", args.out)
        print(f"[md_to_pdf] 移动到: {args.out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
