#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fetch_sources.py — 多信息源统一检索（arXiv / OpenAlex / 预留其他）

定位：本 skill 的"信息源选择"环节落地。Step 0 向用户询问"希望从哪些来源检索"
（多选），随后检索阶段按所选来源逐一调用。sciverse 是主信息源（经 MCP 工具
search_papers/semantic_search，见主 SKILL.md），本脚本补充两个**可直接用 HTTP
查询的公开学术源**，把"多来源"落到实处，且零依赖（仅 Python 标准库 urllib）。

支持的来源与返回规范（统一输出，供下游填空/铸台账）：
  - arxiv    :  arXiv API (export.arxiv.org)  — 预印本；返回 published/title/
               authors/doi(s)/abstract/link
  - openalex :  OpenAlex API (api.openalex.org) — 期刊/会议/预印本聚合；返回
               publication_year/title/authorships/doi/primary_location/abstract

统一返回（--format json 时）每条论文结构：
  {
    "source": "arxiv"|"openalex",
    "title": str,
    "authors": ["First Last", ...],
    "year": int|None,
    "doi": str|None,
    "venue": str|None,
    "abstract": str|None,
    "url": str
  }

用法：
  python3 fetch_sources.py arxiv "quantum error correction" --n 8
  python3 fetch_sources.py openalex "space data center" --n 8 --from-year 2019
  python3 fetch_sources.py --list              # 列出可用来源

网络不可达时（如被代理/防火墙拦截）如实报错并给出 HTTP 状态，不静默降级为
空结果——检索纪律：搜不到 ≠ 不存在，把来源不可用与无命中区分开。
"""

import argparse
import json
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_API = "https://export.arxiv.org/api/query"
OPENALEX_API = "https://api.openalex.org/works"

AUTHORS = "{http://www.w3.org/2005/Atom}"
ARXIV_NS = "{http://arxiv.org/schemas/atom}"


def _fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "sciverse-deep-research/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="replace")


def search_arxiv(query, n=8, year_from=None):
    params = {"search_query": f"all:{query}", "start": 0, "max_results": n,
              "sortBy": "relevance", "sortOrder": "descending"}
    url = ARXIV_API + "?" + urllib.parse.urlencode(params)
    xml = _fetch(url)
    root = ET.fromstring(xml)
    out = []
    for e in root.findall(f"{AUTHORS}entry"):
        title = " ".join((e.findtext(f"{AUTHORS}title") or "").split())
        summary = " ".join((e.findtext(f"{AUTHORS}summary") or "").split())
        authors = [a.findtext(f"{AUTHORS}name") for a in e.findall(f"{AUTHORS}author")]
        published = e.findtext(f"{AUTHORS}published") or ""
        year = int(published[:4]) if len(published) >= 4 else None
        if year_from and year and int(year) < year_from:
            continue
        doi = e.findtext(f"{ARXIV_NS}doi") or ""
        pdf = None
        for link in e.findall(f"{AUTHORS}link"):
            if link.get("title") == "pdf":
                pdf = link.get("href")
        out.append({
            "source": "arxiv", "title": title, "authors": [a for a in authors if a],
            "year": year, "doi": doi or None, "venue": "arXiv",
            "abstract": summary or None, "url": pdf or (e.findtext(f"{AUTHORS}id") or ""),
        })
    return out


def search_openalex(query, n=8, year_from=None):
    params = {"search": query, "per-page": n, "mailto": "sciverse@example.com",
              "sort": "relevance_score:desc"}
    if year_from:
        params["filter"] = f"from_publication_date:{year_from}-01-01"
    url = OPENALEX_API + "?" + urllib.parse.urlencode(params)
    data = json.loads(_fetch(url))
    out = []
    for w in data.get("results", []):
        loc = w.get("primary_location") or {}
        src = (loc.get("source") or {})
        doi = w.get("doi") or None
        # normalize doi full url -> bare
        if doi and doi.startswith("https://doi.org/"):
            doi = doi[len("https://doi.org/"):]
        out.append({
            "source": "openalex",
            "title": w.get("title") or "",
            "authors": [a.get("author", {}).get("display_name") for a in w.get("authorships", [])],
            "year": w.get("publication_year"),
            "doi": doi,
            "venue": src.get("display_name") if src else None,
            "abstract": (w.get("abstract_inverted_index") and _abstract_from_inverted(w.get("abstract_inverted_index"))) or None,
            "url": (w.get("doi") or (loc.get("landing_page_url") if loc else None)),
        })
    return out


def _abstract_from_inverted(inv):
    """OpenAlex 以倒排索引给摘要，需重建为字符串。"""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(range(len(pos)), key=lambda k: (k in pos, k)) if i in pos) if pos else None


SOURCES = {"arxiv": search_arxiv, "openalex": search_openalex}


def main():
    ap = argparse.ArgumentParser(description="多信息源统一检索（arXiv/OpenAlex）")
    ap.add_argument("--list", action="store_true", help="列出可用来源")
    ap.add_argument("source", nargs="?", help="arxiv | openalex")
    ap.add_argument("query", nargs="?", help="检索关键词")
    ap.add_argument("--n", type=int, default=8)
    ap.add_argument("--from-year", type=int, default=None)
    ap.add_argument("--format", default="json", choices=["json", "text"])
    args = ap.parse_args()

    if args.list:
        print("可用信息源:", ", ".join(SOURCES))
        return 0
    if args.source not in SOURCES:
        print(f"未知来源 '{args.source}'；可用: {', '.join(SOURCES)}", file=sys.stderr)
        return 2
    if not args.query:
        print("缺少 query", file=sys.stderr)
        return 2

    try:
        results = SOURCES[args.source](args.query, args.n, args.from_year)
    except Exception as exc:
        print(f"[fetch_sources] {args.source} 检索失败: {exc}（来源不可用或网络被拦截，非无命中）", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"- {r['year']} | {r['title']} | {', '.join(r['authors'][:3])} | {r['venue']} | doi={r['doi']}")
    print(f"\n# {args.source}: {len(results)} 条", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
