#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
detect_latex.py — 探测本机是否具备"Markdown → PDF"的 LaTeX 能力

定位：本 skill 交付环节的格式选择前置判定。只有本脚本判定 LaTeX 可用时，
Step 0 才会向用户提供"PDF"作为输出可选项；否则只给 Markdown。

判定内容（均可独立存在，PDF 链路需要"引擎 + 中文 CTeX 宏包"同时具备）：
  1. 引擎（engine）：xelatex / lualatex / pdflatex / latexmk 任一可用。
     只认 xelatex/lualatex（能走 ctex/xeCJK 中文字体）为 FULL；仅 pdflatex 为
     PARTIAL（无中文字体支持，英文可编）。latexmk 算调度器，不算引擎。
  2. 中文宏包（ctex / xeCJK）：决定能否渲染中文。md_to_pdf.py 用 ctex 时必需。
  3. 字体（中文字体探测）：xeCJK 需要的系统 CJK 字体是否可被 XeTeX 找到。

搜索位置（按序）：
  1. 环境变量 PATH 中的命令
  2. macOS TeX Live 默认位置 /Library/TeX/texbin（`which` 常因 PATH 不含它而漏判）
  3. Linux /usr/bin、/usr/local/bin 兜底

用法：
  python3 detect_latex.py            # 人类可读报告，退出码 0=可用 1=不可用
  python3 detect_latex.py --json     # 结构化 JSON，供 agent 机械判定

本脚本 Python 标准库零依赖。输出里的布尔/路径字段供上层机械消费。
"""

import json
import os
import shutil
import subprocess
import sys

# --- 候选搜索目录（macOS TeX Live 的 bin 不在默认 PATH，必须显式加入） ---
EXTRA_BIN_DIRS = [
    "/Library/TeX/texbin",   # macOS TeX Live 默认
    "/usr/local/texlive",
    "/usr/bin",
    "/usr/local/bin",
]

# 优先引擎顺序（xelatex/lualatex 支持 ctex 中文，pdflatex 仅英文）
PRIMARY_ENGINES = ["xelatex", "lualatex"]
SECONDARY_ENGINES = ["pdflatex"]
SCHEDULER = "latexmk"

# 中文排版宏包（ctex 是总入口；xeCJK 被 xelatex 使用）
CJK_PACKAGES = ["ctex", "xecjk"]


def _find_bin(name):
    """返回命令绝对路径；找不到返回 None。"""
    # 1) PATH 常规查找
    p = shutil.which(name)
    if p:
        return p
    # 2) 显式目录兜底
    for d in EXTRA_BIN_DIRS:
        cand = os.path.join(d, name)
        if os.path.isfile(cand) and os.access(cand, os.X_OK):
            return cand
    return None


def _kpsewhich_file(file_):
    """用任一 latex 引擎去 kpsewhich 找宏包文件；返回路径或 None。"""
    engine = _find_bin("kpsewhich") or _find_bin("xelatex")
    if not engine:
        # 退化：没有引擎时启发式扫宏包目录
        for d in ["/usr/local/texlive/2026/texmf-dist/tex/latex",
                  "/usr/share/texlive/texmf-dist/tex/latex"]:
            for root, dirs, files in os.walk(d):
                if file_ in files:
                    return os.path.join(root, file_)
        return None
    base = os.path.dirname(engine) if os.path.dirname(engine) else "."
    kpse = os.path.join(base, "kpsewhich") if os.path.exists(os.path.join(base, "kpsewhich")) else engine
    try:
        out = subprocess.run(
            [kpse, file_], capture_output=True, text=True, timeout=15
        ).stdout.strip()
        return out or None
    except Exception:
        return None


def has_cjk_package(pkg):
    """探测 ctex/xecjk 宏包是否安装（文件系统或 kpsewhich）。"""
    for f in (f"{pkg}.sty", f"{pkg}.cls"):
        if _kpsewhich_file(f):
            return True
    return False


def detect_cjk_font():
    """探测一个可被 XeTeX 用到的中文字体路径（偏好系统 Songti/Heiti）。"""
    candidates = [
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/Library/Fonts/Songti.ttc",
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    # 退而求其次：任何 .ttc/.otf 中含 CJK 的（简单按出现即用）
    return None


def main():
    as_json = "--json" in sys.argv

    engines = {}
    for e in PRIMARY_ENGINES:
        path = _find_bin(e)
        if path:
            engines[e] = path
    for e in SECONDARY_ENGINES:
        path = _find_bin(e)
        if path:
            engines[e] = path
    sched = _find_bin(SCHEDULER)

    has_ctex = has_cjk_package("ctex")
    has_xecjk = has_cjk_package("xecjk")
    font = detect_cjk_font()

    primary = any(e in engines for e in PRIMARY_ENGINES)
    secondary = "pdflatex" in engines
    # ctex 宏包（ctexart.cls/ctex.sty）在 xelatex/lualatex 引擎下自带中文排版能力，
    # 内部会自动加载 xeCJK——故"引擎 + ctex 宏包"即视为中文齐备；
    # 独立 xecjk 文件检测仅作次级线索，不作为硬门槛（文件名/路径因发行版而异）。
    cjk_ready = has_ctex

    # 三档能力：
    #   full    = xelatex/lualatex + ctex/xeCJK（中文 PDF 完整可用）
    #   partial = 有引擎但缺 CJK（英文 PDF；中文会缺字）
    #   none    = 无引擎
    if primary and cjk_ready:
        level = "full"
    elif primary or secondary:
        level = "partial"
    else:
        level = "none"

    result = {
        "level": level,
        "available": level != "none",
        # 是否值得在 Step 0 提供 PDF 选项——只有 full 才提供（中文可渲染）
        "pdf_offered": level == "full",
        "engines": engines,
        "latexmk": sched,
        "cjk": {"ctex": has_ctex, "xecjk": has_xecjk, "font": font},
        "missing_reason": (
            "无 LaTeX 引擎"
            if level == "none"
            else ("引擎可用但无 CTeX/xeCJK 中文宏包或中文字体" if level == "partial" else None)
        ),
    }

    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"[detect_latex] level={result['level']}  pdf_offered={result['pdf_offered']}")
        print(f"  引擎: {', '.join(engines) if engines else '未检测到'}")
        print(f"  latexmk: {sched or '无'}")
        print(f"  CTeX/xeCJK: {has_ctex}/{has_xecjk}  字体: {font or '未检测'}")
        if result["missing_reason"]:
            print(f"  提示: {result['missing_reason']}")

    return 0 if level != "none" else 1


if __name__ == "__main__":
    sys.exit(main())
