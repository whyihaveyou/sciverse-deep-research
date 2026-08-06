#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
md_to_pdf.py — 把本 skill 交付的 final.md（Markdown 综述）用本地 LaTeX 渲染成 PDF

定位：交付环节的可选第二步。在 detect_latex.py 判定为 full 的前提下执行；
产出与 final.md 同名的 .pdf 文件，与 Markdown 源稿并存（MD 始终是源稿，
PDF 是其排版视图——本 skill 仍以 Markdown 为唯一事实源，PDF 不回写正文）。

转换策略（零依赖，不依赖 pandoc）：
  1. 读取 Markdown，逐行解析成结构化为本 skill 综述骨架的子集：
     - # / ## / ### 标题        → 章/节（用 section/subsection/subsubsection）
     - 无序列表 - 与有序列表 1.  → itemize/enumerate
     - 空行分段的正文           → 分段
     - 行内的 `代码` 转 \texttt  ；**加粗** 转 \textbf ；$...$ 数学原样透传
     - 独立的 $$...$$          → 数学 display 环境
     - 引用的 [1] / [1, 2] / [1-3] → 原样保留（ctexart 下 [1] 即自然呈现）
     - 【参考文献】节          → 用 plain bibliography 列表排布
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


def tex_escape(s):
    """转义 LaTeX 特殊字符（保留 \textbf{}、数学 $..$、\texttt{} 由下层的 token 化处理）。"""
    # 先保护我们生成的标记与数学，再转义裸字符
    return (s.replace("\\", r"\textbackslash{}")
             .replace("{", r"\{").replace("}", r"\}")
             .replace("#", r"\#").replace("%", r"\%")
             .replace("&", r"\&").replace("_", r"\_")
             .replace("~", r"\textasciitilde{}")
             .replace("^", r"\textasciicircum{}"))


def inline(s):
    """行内格式化：**粗**、`代码`、$数学$；返回 LaTeX 行。

    顺序要点：
      1. 先保护数学（$...$ / $$...$$）为占位符——数学原文是 LaTeX，不能被转义破坏；
      2. 再对剩余裸文本做特殊字符转义（_ {} & % # ~ ^ \ 等）；
      3. 之后才匹配 **粗体** 与 `代码` 生成 \\textbf{} / \\texttt{}——
         这保证生成的控制序列不再被第 2 步转义破坏。
      4. 最后还原数学占位符。
    """
    placeholders = {}

    # (1) 保护数学：$$..$$ 与 $..$（要求成对闭合；单侧美元符不配对、原样保留）
    def math_repl(m):
        key = f"@@M{len(placeholders)}@@"
        placeholders[key] = m.group(0)
        return key

    s = re.sub(r"\$\$[^$]+?\$\$", math_repl, s)        # display 数学
    s = re.sub(r"(?<!\$)\$[^$\n]+?\$(?!\$)", math_repl, s)  # inline 数学

    # (2) 裸文本特殊字符转义（数学已保护，不影响）。
    #     残余 `$`（孤立文字美元符，如 "TFLOPS/$"）在此一并转义为 \$——
    #     必须在"反斜杠替换"同一链内完成，否则前一步生成的 \$ 会被本链的
    #     反斜杠替换再次破坏、让 $ 裸露并误开数学模式。
    s = (s.replace("\\", r"\textbackslash{}")
          .replace("{", r"\{").replace("}", r"\}")
          .replace("#", r"\#").replace("%", r"\%")
          .replace("&", r"\&").replace("_", r"\_")
          .replace("~", r"\textasciitilde{}")
          .replace("^", r"\textasciicircum{}")
          .replace("$", r"\$"))

    # (3) 粗体 / 代码（此时转义已过，生成的控制序列安全）
    s = re.sub(r"\*\*([^*]+)\*\*", r"\\textbf{\1}", s)
    s = re.sub(r"`([^`]+)`", r"\\texttt{\1}", s)

    # (4) 还原数学占位符
    for k, v in placeholders.items():
        s = s.replace(k, v)
    return s


def render(markdown_path, engine="xelatex"):
    with open(markdown_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    body = []
    first_h1 = True
    in_code = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # 代码块(```)整体跳过
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            i += 1
            continue

        # 标题。
        # 等级映射（对齐本 skill 综述骨架：首个 H1=文章标题，其余 H2=章、H3=节、H4=小节）：
        #   H1 → 跳过（由 \maketitle 呈现标题，避免与正文 \section 重复）
        #   H2 → \section    H3 → \subsection    H4 → \subsubsection
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            hashes, text = m.group(1), m.group(2)
            lvl = len(hashes)
            first_heading = body == [] or all(not x for x in body)
            if lvl == 1:
                # 首个 H1 是文章标题，交给 \maketitle；正文中的 H1（罕见）降级为 section
                if first_heading:
                    body.append("")
                    i += 1
                    continue
                body.append(f"\\section{{{inline(text)}}}")
            elif lvl == 2:
                body.append(f"\\section{{{inline(text)}}}")
            elif lvl == 3:
                body.append(f"\\subsection{{{inline(text)}}}")
            else:
                body.append(f"\\subsubsection{{{inline(text)}}}")
            body.append("")
            i += 1
            continue

        # 无序列表：收集连续项 → 包进 itemize
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

        # 有序列表：收集连续项 → 包进 enumerate
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

        # 空行 → 分段（收束上一段）
        if line.strip() == "":
            i += 1
            continue

        # 普通正文段
        body.append(inline(line))
        body.append("")
        i += 1

    # 组装 LaTeX 骨架（用普通字符串避免 f-string 与反斜杠冲突）
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

    # 转成 .tex 临时文件
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
    # 排错
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
