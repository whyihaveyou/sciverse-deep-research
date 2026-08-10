#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""md_to_pdf.py — sciverse deep-research 渲染策略分发器（Markdown → PDF / Word）

定位：交付环节的可选第二步。在 detect_latex.py 判定为 full 的前提下执行；
产出与 final.md 同名（或 --out 指定）的 .pdf / .docx，与 Markdown 源稿并存
（MD 始终是唯一事实源，PDF/Word 只是排版视图，不回写正文）。

渲染策略（分层，自动回退）：
  1. 预处理 normalize()：把遗留正文里的 ASCII 直引号 "…" 规范成 “…”（弯引号），
     并把纯文本数学（d_s、t^(−d_s/2)、Δ_ij、d̃ 等）焊接成真正的 $...$ TeX 数学。
     —— 这一层对 Pandoc 路径与手写回退路径都生效，是"上下标正确"的关键。
     （SKILL 纪律已要求新稿直接用 $...$ 与 “…”；本层负责修复违反纪律的遗留稿。）
  2. 优先 Pandoc（若有 pandoc 可执行文件）：
       - PDF:  pandoc -f markdown+smart → xelatex PDF（smart 自动弯引号 + CJK 字体）
       - Word: pandoc -f markdown+smart → .docx
  3. 无 Pandoc 回退：保留手写转换器（md→tex→xelatex），基于已 normalize 的文本渲染。
     Word（docx）若无 Pandoc 则无法生成，明确报错而非静默降级。

用法：
  python3 md_to_pdf.py final.md                        # 默认 PDF（探测 pandoc，缺则回退）
  python3 md_to_pdf.py final.md --format docx          # Word
  python3 md_to_pdf.py final.md --format markdown      # 只输出 normalize 后的 .md（排版视图源）
  python3 md_to_pdf.py final.md --no-pandoc            # 强制走手写回退路径
  python3 md_to_pdf.py final.md --out 自定义路径.docx   # 按扩展名推断 format
  python3 md_to_pdf.py final.md --keep-tex --engine xelatex

本脚本 Python 标准库零依赖。xelatex / pandoc 路径自动探测
（PATH + /Library/TeX/texbin + pandoc 常见提取目录）。
"""

import argparse
import os
import re
import shutil
import subprocess
import sys

# --- 引擎/宏包/工具探测 ---
EXTRA_BIN_DIRS = ["/Library/TeX/texbin", "/usr/local/texlive", "/usr/bin", "/usr/local/bin"]
# pandoc 非 brew 安装的常见位置（本仓库曾在 /tmp/pandoc_extracted 解包）
PANDOC_EXTRA_DIRS = [
    "/tmp/pandoc_extracted",
    "/opt/homebrew/bin",           # Apple Silicon brew
    "/usr/local/bin",
    os.path.expanduser("~/bin"),
]
# macOS 中文字体名 → 路径（导出时按存在的取第一个）
CJK_FONTS = [
    ("Songti SC", "/System/Library/Fonts/Supplemental/Songti.ttc"),
    ("PingFang SC", "/System/Library/Fonts/PingFang.ttc"),
    ("STSong", "/System/Library/Fonts/Supplemental/Songti.ttc"),
]


def find_bin(name, extra_dirs=None):
    p = shutil.which(name)
    if p:
        return p
    for d in (extra_dirs or EXTRA_BIN_DIRS):
        cand = os.path.join(d, name)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def find_pandoc():
    """在 PATH 与常见位置找 pandoc；找不到返回 None。"""
    p = shutil.which("pandoc")
    if p:
        return p
    import glob
    for base in PANDOC_EXTRA_DIRS:
        # /tmp/pandoc_extracted/pandoc-*/bin/pandoc
        for cand in glob.glob(os.path.join(base, "pandoc-*", "bin", "pandoc")):
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                return cand
        for cand in (os.path.join(base, "pandoc"),):
            if os.path.isfile(cand) and os.access(cand, os.X_OK):
                return cand
    return None


def detect_cjk_font_name():
    for name, path in CJK_FONTS:
        if os.path.isfile(path):
            return name
    return None


# =====================================================================
# 预处理层：弯引号 + 纯文本数学焊接（两个渲染路径共用）
# =====================================================================

# 希腊字母 → LaTeX 数学命令（含 MathMode 内使用的 ω δ Σ，及本仓库遗漏的）
GREEK_CMD = {
    "\u03b1": r"\alpha",   # α
    "\u03b2": r"\beta",    # β
    "\u03b3": r"\gamma",   # γ
    "\u03b4": r"\delta",   # δ
    "\u03b5": r"\epsilon", # ε
    "\u03b6": r"\zeta",    # ζ
    "\u03b7": r"\eta",     # η
    "\u03b8": r"\theta",   # θ
    "\u03ba": r"\kappa",   # κ
    "\u03bb": r"\lambda",  # λ
    "\u03bc": r"\mu",      # μ
    "\u03bd": r"\nu",      # ν
    "\u03be": r"\xi",      # ξ
    "\u03c1": r"\rho",     # ρ
    "\u03c3": r"\sigma",   # σ
    "\u03c4": r"\tau",     # τ
    "\u03c6": r"\phi",     # φ
    "\u03c7": r"\chi",     # χ
    "\u03c8": r"\psi",     # ψ
    "\u03c9": r"\omega",   # ω
    "\u0394": r"\Delta",   # Δ
    "\u0393": r"\Gamma",   # Γ
    "\u0398": r"\Theta",   # Θ
    "\u039b": r"\Lambda",  # Λ
    "\u03a3": r"\Sigma",   # Σ
    "\u03a9": r"\Omega",   # Ω
    "\u2148": r"\imath",   # ⅈ
}

# 高端数学符（math 之外出现会缺字形）→ $...$ 数学形式
MATH_SYMBOL_CMD = {
    "\u2248": r"\approx",     # ≈
    "\u2260": r"\neq",        # ≠
    "\u2264": r"\leq",        # ≤
    "\u2265": r"\geq",        # ≥
    "\u2192": r"\rightarrow", # →
    "\u2194": r"\leftrightarrow",  # ↔
    "\u27fa": r"\iff",        # ⟺
    "\u2261": r"\equiv",      # ≡
    "\u21d2": r"\Rightarrow", # ⇒
    "\u00d7": r"\times",      # ×
    "\u00b7": r"\cdot",       # ·
    "\u2212": "-",            # − (数学负号，并入 -)
    "\u2026": r"\ldots",      # …
}

BASE = r"[A-Za-z\u0370-\u03ff\u00c0-\u024f]"
# 下标/上标原子：base + _/^ + 非空 group（{}、() 或 token 串）
ATOM = re.compile(
    r"(?<![A-Za-z0-9_$\"\u0370-\u03ff])"
    r"(" + BASE + r"+\u0303?)"
    r"([_\^])"
    r"(?:(\{[^{}]*\})|(\([^()]*\))|([A-Za-z0-9\u0370-\u03ff+\-./:;,]+))"
)


def _greek_to_cmd(m):
    """把匹配到的希腊字母集合逐个换成 \\cmd（在选取出后调用）。"""
    return "".join(str(GREEK_CMD[ch]) if ch in GREEK_CMD else ch for ch in m.group(0))


def _tilde_if(base):
    """base 若带组合上波浪线 U+0303（d̃）→ \\tilde{d}；否则原样。"""
    if base.endswith("\u0303"):
        return r"\tilde{" + base[:-1] + "}"
    return base


def _conv_inner(inner):
    """组内（下标/上标内容）处理：希腊字母与数学符号 → LaTeX 命令。"""
    inner = re.sub(r"[\u0370-\u03ff\u2148]", _greek_to_cmd, inner)
    return re.sub(r"[\u2192\u221e\u2264\u2265\u2248\u2260\u27fa\u2261\u21d2\u00d7\u00b7]",
                  lambda mm: {"\u2192": r"\to", "\u221e": r"\infty",
                              "\u2264": r"\leq", "\u2265": r"\geq",
                              "\u2248": r"\approx", "\u2260": r"\neq",
                              "\u27fa": r"\iff", "\u2261": r"\equiv",
                              "\u21d2": r"\Rightarrow", "\u00d7": r"\times",
                              "\u00b7": r"\cdot"}[mm.group(0)], inner)


def _mathify_atom(m):
    base, op = m.group(1), m.group(2)
    brace, paren, tok = m.group(3), m.group(4), m.group(5)
    grp = brace or paren or tok
    # base 内部希腊字母 → 命令
    base = _tilde_if(base)
    base = re.sub(r"[\u0370-\u03ff\u2148]", _greek_to_cmd, base)
    # group 内容：去外层括号；内部希腊/数学符同样转命令
    if grp.startswith("{"):
        inner = grp[1:-1]
    elif grp.startswith("("):
        inner = grp[1:-1]
    else:
        inner = grp
    inner = _conv_inner(inner)
    braced = "{" + inner + "}"
    return "${base}{op}{braced}$".format(base=base, op=op, braced=braced)


def mathify(text):
    """把纯文本数学（d_s、t^(...)、Δ_ij、d̃）焊接成 $...$ TeX 数学。
    对已用 $...$ 的文本幂等（保护 $..$、```、\\tilde{..} 不重复处理）。"""
    protected = []
    def stash(m):
        protected.append(m.group(0))
        return "\x00P%d\x00" % (len(protected) - 1)
    text = re.sub(r"\$\$\s*[^$]*?\s*\$\$", stash, text)         # display math
    text = re.sub(r"(?<!\\)\$(?:[^$\n]|\\\$)*?\$", stash, text) # inline math
    text = re.sub(r"`[^`]*`", stash, text)                      # code span
    text = re.sub(r"\\tilde\{[^}]*\}", stash, text)

    # ① 焊 _/^ 子脚本为主（先跑，避免符号 pass 把 base 字母提前替代掉）
    #    —— 输入里 $..$ 已被 stash 成 \x00Pn\x00 占位符，无 $，可安全抓 ATOM。
    out, last = [], 0
    for m in ATOM.finditer(text):
        out.append(text[last:m.start()])
        out.append(_mathify_atom(m))
        last = m.end()
    out.append(text[last:])
    text = "".join(out)

    # ② 独立组合波浪线 d̃（无 _/^ 的形式）
    def tilde_pass(s):
        return re.sub(r"([A-Za-z])\u0303", lambda m: "$\\tilde{%s}$" % m.group(1), s)
    text = tilde_pass(text)

    # ③ 剩余正文里的希腊字母/高端符号单独焊接成 $...$（无 _/^ 的纯符号，如 ρ(ω)、≈）
    def symbol_pass(s):
        out, last = [], 0
        pat = re.compile(r"(?<![A-Za-z0-9_$\\])([\u0370-\u03ff\u2148\u2248\u2260\u2264\u2265\u2192\u2194\u27fa\u2261\u21d2\u00d7\u00b7])(?![A-Za-z0-9_$\\])")
        for mm in pat.finditer(s):
            out.append(s[last:mm.start()])
            ch = mm.group(1)
            if ch in GREEK_CMD:
                out.append("$" + GREEK_CMD[ch] + "$")
            elif ch in MATH_SYMBOL_CMD:
                out.append("$" + MATH_SYMBOL_CMD[ch] + "$")
            else:
                out.append(ch)
            last = mm.end()
        out.append(s[last:])
        return "".join(out)
    text = symbol_pass(text)

    # ④ 连写 _ / ^ 合并：$a_{1}$^2 → $a_{1}^{2}$（只吸附紧贴数学闭 $ 后的脚本）。
    #    已花括号形态 n^{-d_s/2} 无尾随脚本，不受影响。
    def chain_merge(s):
        pat = re.compile(
            r"(\$[^$\n]+\}\$)([_^])"
            r"((?:\{[^{}]*\})|(?:\([^()]*\))|[A-Za-z0-9\u0370-\u03ff+\-./:;,]+)")
        while True:
            mm = pat.search(s)
            if not mm:
                break
            head, op, grp = mm.group(1), mm.group(2), mm.group(3)
            if grp.startswith("{"):
                inner = grp[1:-1]
            elif grp.startswith("("):
                inner = grp[1:-1]
            else:
                inner = grp
            inner = _conv_inner(inner)
            new = head[:-1] + op + "{" + inner + "}$"
            s = s[:mm.start()] + new + s[mm.end():]
        return s
    text = chain_merge(text)

    def unstore(m):
        return protected[int(m.group(1))]
    return re.sub(r"\x00P(\d+)\x00", unstore, text)


def smart_quotes(text):
    """ASCII 直双引号 " → 规范弯引号 “”。单趟配对（交替开/闭），
    兼容既有弯引号（作为配对状态锚点），保护 ``` 代码、$..$ 数学、\\cmd 序列不被误改。
    返回转换后的文本（保护段原样保留）。"""
    # 先把保护段（代码/数学）暂存成占位符，避免其中的 " 被误配对
    protected = []
    def stash(m):
        protected.append(m.group(0))
        return "\x00Q%d\x00" % (len(protected) - 1)
    text = re.sub(r"`[^`]*`|\$\$[^$]*?\$\$|(?<!\\)\$(?:[^$\n]|\\\$)*?\$", stash, text)
    # 对剩余普通文本做配对
    open_q = True
    buf = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\u201c" or ch == "\u201d":
            # 既有弯引号作为配对状态锚点。
            # 语义：见到开引号「”…」之后下一个 ASCII " 应为闭；见到闭引号
            # 「…”」之后下一个 ASCII " 应为开。故 open_q = (ch 为闭引号)。
            open_q = (ch == "\u201d")
            buf.append(ch)
        elif ch == '"':
            buf.append("\u201c" if open_q else "\u201d")
            open_q = not open_q
        else:
            buf.append(ch)
        i += 1
    out = "".join(buf)
    # 还原保护段
    def unstore(m):
        return protected[int(m.group(1))]
    return re.sub(r"\x00Q(\d+)\x00", unstore, out)


def normalize(text):
    """完整预处理：先弯引号，再焊数学。顺序关键——弯引号产生 “”，
    之后 mathify 的 BASE 前瞻会把“”当分隔符，不误并数学。"""
    from_text = smart_quotes(text)
    return mathify(from_text)


# =====================================================================
# 手写回退转换器（无 pandoc 时代替；基于已 normalize 的文本）
# =====================================================================

SYMBOL_MAP = {
    "\u2192": "\\ensuremath{\\rightarrow}",
    "\u2194": "\\ensuremath{\\leftrightarrow}",
    "\u2227": "\\ensuremath{\\wedge}",
    "\u2229": "\\ensuremath{\\cap}",
    "\u222a": "\\ensuremath{\\cup}",
    "\u2265": "\\ensuremath{\\geq}",
    "\u2264": "\\ensuremath{\\leq}",
    "\u2260": "\\ensuremath{\\neq}",
    "\u00d7": "\\ensuremath{\\times}",
    "\u00b1": "\\ensuremath{\\pm}",
    "\u2212": "\\ensuremath{-}",
    "\u2153": "\\ensuremath{\\tfrac{1}{3}}",
    "\u00b2": "\\ensuremath{^2}",
    "\u00b3": "\\ensuremath{^3}",
    "\u00fc": '\\"{u}',
    "\u2026": "\\ldots",
    "\u2014": "---",
    "\u201c": "``",
    "\u201d": "''",
    "\u00b7": "\\ensuremath{\\cdot}",
}

STAR_MAP = {"\u2605": "\\bigstar", "\u2606": "\\bigstar", "\u260b": "\\bigstar"}


def _map_specials(s, placeholders):
    s = s.replace("\u0304", "")  # 去组合上划线
    star_i = [0]
    def star_repl(m):
        key = "@@STAR%d@@" % len(placeholders)
        placeholders[key] = r"$\bigstar$"
        return key
    s = re.sub(r"[★☆☾☽]", star_repl, s)
    for ch, cmd in GREEK_CMD.items():
        if ch in s:
            key = "@@G%d@@" % len(placeholders)
            placeholders[key] = "$" + cmd + "$"
            s = s.replace(ch, key)
    for ch, cmd in SYMBOL_MAP.items():
        if ch in s:
            key = "@@S%d@@" % len(placeholders)
            placeholders[key] = cmd
            s = s.replace(ch, key)
    return s


def inline(s):
    """行内格式化：**粗**、`代码`、$数学$、希腊、★；返回 LaTeX 行。"""
    placeholders = {}

    def math_repl(m):
        key = "@@M%d@@" % len(placeholders)
        placeholders[key] = m.group(0)
        return key
    s = re.sub(r"\$\$[^$]+?\$\$", math_repl, s)
    s = re.sub(r"(?<!\$)\$[^$\n]+?\$(?!\$)", math_repl, s)
    s = s.replace("$", r"\$")
    s = _map_specials(s, placeholders)
    s = (s.replace("\\", r"\textbackslash{}")
          .replace("{", r"\{").replace("}", r"\}")
          .replace("#", r"\#").replace("%", r"\%")
          .replace("&", r"\&").replace("_", r"\_")
          .replace("~", r"\textasciitilde{}")
          .replace("^", r"\textasciicircum{}"))
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    # 粗体跨越数学/符号已受保护，这里只处理未受保护的纯文本粗体
    s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)
    for k, v in placeholders.items():
        s = s.replace(k, v)
    return s


def _is_table_row(line):
    return "|" in line and line.strip().startswith("|")


def _handle_table(lines, i):
    out = []
    j = i
    header = None
    if j < len(lines) and _is_table_row(lines[j]):
        header = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        j += 1
    if j < len(lines) and _is_table_row(lines[j]):
        cells = [c.strip() for c in lines[j].strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            aligns = ["r" if c.startswith(":") and c.endswith(":") else
                      ("l" if c.startswith(":") else
                       ("r" if c.endswith(":") else "l")) for c in cells]
            j += 1
    else:
        aligns = ["l"] * (len(header) if header else 1)
    rows = []
    while j < len(lines) and _is_table_row(lines[j]):
        rows.append([c.strip() for c in lines[j].strip().strip("|").split("|")])
        j += 1
    ncol = max(len(header) if header else 0, max((len(r) for r in rows), default=0), 1)
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


def fallback_render(markdown_path, engine="xelatex"):
    """手写回退：md → tex。输入已是 normalize 后的文本（在 main 里先 normalize 写临时文件）。"""
    with open(markdown_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    body = []
    in_code = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue
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
                body.append("\\section*{" + inline(text) + "}")
            elif lvl == 2:
                body.append("\\section*{" + inline(text) + "}")
            elif lvl == 3:
                body.append("\\subsection*{" + inline(text) + "}")
            else:
                body.append("\\subsubsection*{" + inline(text) + "}")
            body.append("")
            i += 1
            continue
        if line.strip().startswith("|"):
            tbody, ni = _handle_table(lines, i)
            body.extend(tbody)
            i = ni
            continue
        if re.match(r"^[-*]\s+", line):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i]):
                items.append(inline(re.sub(r"^[-*]\s+", "", lines[i])))
                i += 1
            body.append("\\begin{itemize}")
            for it in items:
                body.append("  \\item " + it)
            body.append("\\end{itemize}")
            body.append("")
            continue
        if re.match(r"^\d+\.\s+(.*)$", line):
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i]):
                items.append(inline(re.sub(r"^\d+\.\s+", "", lines[i])))
                i += 1
            body.append("\\begin{enumerate}")
            for it in items:
                body.append("  \\item " + it)
            body.append("\\end{enumerate}")
            body.append("")
            continue
        if line.strip() == "":
            i += 1
            continue
        body.append(inline(line))
        body.append("")
        i += 1

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
        print("[md_to_pdf] 找不到引擎 %s；请先运行 detect_latex.py 确认 LaTeX 可用" % engine, file=sys.stderr)
        return 1
    base = os.path.splitext(tex_path)[0]
    cwd = os.path.dirname(tex_path) or "."
    try:
        r = subprocess.run(
            [exe, "-interaction=nonstopmode", "-halt-on-error", os.path.basename(tex_path)],
            cwd=cwd, capture_output=True, text=True, timeout=180,
        )
    except FileNotFoundError:
        print("[md_to_pdf] 引擎 %s 不可执行" % exe, file=sys.stderr)
        return 1
    pdf = base + ".pdf"
    if r.returncode == 0 and os.path.exists(pdf):
        print("[md_to_pdf] 生成 PDF: %s" % pdf)
        if not keep_tex:
            os.remove(tex_path)
        return 0
    print("[md_to_pdf] xelatex 失败(exit=%s)" % r.returncode, file=sys.stderr)
    log = base + ".log"
    if os.path.exists(log):
        print("  最近错误:", file=sys.stderr)
        for line in r.stdout.splitlines():
            if line.startswith("!") or "Error" in line or "error" in line:
                print("  " + line, file=sys.stderr)
    return 1


def pandoc_pdf(norm_md, out_pdf, pandoc, keep_tex):
    """pandoc -f markdown+smart -> xelatex PDF。返回 (rc, 输出文件名)。

    pandoc 直接出 .pdf 会先生成 .tex（--pdf-engine=xelatex）。为可选保留中间 .tex，
    这里用 pandoc 生成 .tex 再交给 xelatex，语义与手写回退一致。"""
    base = os.path.splitext(out_pdf)[0]
    tex = base + ".tex"
    # 关键修复：pandoc 默认产出 .tex 是「片段」（无 documentclass/preamble，开头即
    # \section），直接交给 xelatex 必报 Undefined control sequence。必须 -s(standalone)
    # 让 pandoc 用自带 LaTeX 模板生成完整文档；documentclass=ctexart 让 ctex 在
    # xelatex 下自动配置中文字体（macOS + TeX Live 可直接用），无需手挑 CJKmainfont。
    cmd = [pandoc, norm_md, "-o", tex, "--pdf-engine=xelatex",
           "-f", "markdown+smart", "-s", "-V", "documentclass=ctexart"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode != 0 or not os.path.exists(tex):
        print("[md_to_pdf] pandoc 转 tex 失败(exit=%s)" % r.returncode, file=sys.stderr)
        print(r.stdout[-1500:], file=sys.stderr)
        return 1
    # xelatex 编译
    rc = build(tex, "xelatex", keep_tex=keep_tex)
    if rc == 0 and os.path.exists(base + ".pdf") and base + ".pdf" != out_pdf:
        if os.path.abspath(base + ".pdf") != os.path.abspath(out_pdf):
            shutil.move(base + ".pdf", out_pdf)
    return rc


def pandoc_docx(norm_md, out_docx, pandoc):
    cmd = [pandoc, norm_md, "-o", out_docx, "-f", "markdown+smart"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if r.returncode == 0 and os.path.exists(out_docx):
        print("[md_to_pdf] 生成 Word: %s" % out_docx)
        return 0
    print("[md_to_pdf] pandoc 转 docx 失败(exit=%s)" % r.returncode, file=sys.stderr)
    print(r.stdout[-1500:], file=sys.stderr)
    return 1


def main():
    ap = argparse.ArgumentParser(
        description="把 sciverse-deep-research 的 final.md 渲染成 PDF / Word（策略分发）")
    ap.add_argument("md", help="Markdown 综述路径（.workflow/final.md 或已交付 .md）")
    ap.add_argument("--out", help="输出路径（默认与 md 同名，扩展名决定 format）")
    ap.add_argument("--format", choices=["pdf", "docx", "markdown"],
                    help="输出格式；缺省按 --out 扩展名，否则 pdf")
    ap.add_argument("--engine", default="xelatex", choices=["xelatex", "lualatex"])
    ap.add_argument("--keep-tex", action="store_true", help="保留中间 .tex 文件")
    ap.add_argument("--no-pandoc", action="store_true", help="强制走手写回退路径")
    ap.add_argument("--normalize-out", metavar="PATH",
                    help="额外把 normalize 后的 markdown 写出（排错）")
    args = ap.parse_args()

    if not os.path.exists(args.md):
        print("[md_to_pdf] 找不到文件: %s" % args.md, file=sys.stderr)
        return 1

    # 确定输出格式
    if args.format:
        fmt = args.format
    elif args.out and args.out.lower().endswith(".docx"):
        fmt = "docx"
    elif args.out and args.out.lower().endswith(".md"):
        fmt = "markdown"
    else:
        fmt = "pdf"

    base = os.path.splitext(args.md)[0]
    # 默认输出名：PDF/Word 与 md 同名换后缀；markdown 视图默认 base.normalized.md（绝不覆盖输入源）
    out = args.out
    if not out:
        if fmt == "markdown":
            out = base + ".normalized.md"
        else:
            out = base + (".docx" if fmt == "docx" else ".pdf")
    # 防呆：输出路径不得等于输入源路径（normalize/渲染不该回写源稿）
    if os.path.abspath(out) == os.path.abspath(args.md):
        print("[md_to_pdf] 输出路径与输入源相同（%s），拒绝覆盖源稿；请用 --out 指定其他文件名"
              % args.md, file=sys.stderr)
        return 1

    # 预处理：弯引号 + 焊数学
    try:
        with open(args.md, encoding="utf-8") as f:
            raw = f.read()
    except UnicodeDecodeError:
        print("[md_to_pdf] 无法按 UTF-8 读取文件", file=sys.stderr)
        return 1
    norm = normalize(raw)

    if args.normalize_out:
        with open(args.normalize_out, "w", encoding="utf-8") as f:
            f.write(norm)

    # format=markdown：只输出 normalize 后的 md（排版视图源）
    if fmt == "markdown":
        norm_out = out if out.lower().endswith(".md") else base + ".normalized.md"
        with open(norm_out, "w", encoding="utf-8") as f:
            f.write(norm)
        print("[md_to_pdf] 生成 Markdown(normalized): %s" % norm_out)
        return 0

    # 为渲染写临时 normalize 文件
    tmp_md = base + ".normalized.md"
    with open(tmp_md, "w", encoding="utf-8") as f:
        f.write(norm)

    pandoc = None if args.no_pandoc else find_pandoc()
    try:
        if fmt == "docx":
            if not pandoc:
                print("[md_to_pdf] 生成 Word 需要 pandoc，但本机未找到 pandoc；"
                      "无法静默降级。请安装 pandoc 或改用 --format pdf/markdown。",
                      file=sys.stderr)
                return 1
            return pandoc_docx(tmp_md, out, pandoc)

        # fmt == pdf
        if pandoc:
            rc = pandoc_pdf(tmp_md, out, pandoc, args.keep_tex)
            if rc == 0:
                return 0
            print("[md_to_pdf] pandoc 路径失败，回退到手写转换器", file=sys.stderr)
        tex_path = fallback_render(tmp_md, args.engine)
        rc = build(tex_path, args.engine, args.keep_tex)
        if rc == 0:
            # build 以 tex_path 为基准产出同名 pdf——此处 tex_path 来自
            # base+".normalized.md"，故实际产物是 base+".normalized.pdf"。
            # 按“实际产物”移成 out（默认 base.pdf），不再预设 base+".pdf"（旧逻辑
            # if exists(base+".pdf") 恒为假，导致默认产出一套 normalized 名、out 落空）。
            produced = os.path.splitext(tex_path)[0] + ".pdf"
            if os.path.exists(produced) and os.path.abspath(produced) != os.path.abspath(out):
                shutil.move(produced, out)
                print("[md_to_pdf] 移动到: %s" % out)
        return rc
    finally:
        if os.path.exists(tmp_md) and not args.keep_tex:
            os.remove(tmp_md)


if __name__ == "__main__":
    sys.exit(main())
