# -*- coding: utf-8 -*-
"""citation_api.py — 定位并加载 skills 下的 citation_ledger.py（单写铸账的唯一 API）。

规格 §3：所有台账读写走 scripts/citation_ledger.py 的 API，编排层/子代理禁止
手写条目或自造校验。本模块只做「找到它、import 它」，不重实现其任何逻辑。
"""
import importlib.util
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(_HERE)
_LEDGER_PY = os.path.join(_REPO_ROOT, "skills", "sciverse-deep-research",
                          "scripts", "citation_ledger.py")


def _load():
    spec = importlib.util.spec_from_file_location("citation_ledger", _LEDGER_PY)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_mod = _load()
validate_entries = _mod.validate_entries
load_ledger = _mod.load_ledger
