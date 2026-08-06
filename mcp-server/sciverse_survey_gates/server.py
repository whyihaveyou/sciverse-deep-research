"""sciverse-survey-gates：把 sciverse-deep-research skill 的确定性门禁脚本暴露为 MCP 工具。

四个工具对应 skill 内 scripts/ 目录的四个确定性步骤，内部均为 subprocess 调用，
不重新实现任何检查逻辑——保证与 skill 内脚本行为完全一致。
"""
import os
import subprocess
import sys
from pathlib import Path

from fastmcp import FastMCP

# 脚本目录：默认取本仓库 skills/sciverse-deep-research/scripts，可用环境变量覆盖
_DEFAULT_SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "sciverse-deep-research" / "scripts"
SCRIPTS_DIR = Path(os.environ.get("SCIVERSE_DR_SCRIPTS", _DEFAULT_SCRIPTS)).resolve()

LEDGER_PY = SCRIPTS_DIR / "citation_ledger.py"
CHECK_PY = SCRIPTS_DIR / "check_report.py"
VERIFY_PY = SCRIPTS_DIR / "verify_citations.py"

TIMEOUT = 180

mcp = FastMCP(
    "sciverse-survey-gates",
    instructions=(
        "sciverse-deep-research 综述管线的机械门禁：引用台账 validate、键值草稿 compile 铸号、"
        "交付前 check_report 验收、Crossref 题录核验。配合 sciverse-deep-research skill 使用——"
        "管线要求 compile 成功、check_report 全 CLEAR 之前不得交付综述。"
    ),
)


def _run(script: Path, args: list) -> str:
    if not script.is_file():
        return "ERROR: 脚本不存在: %s（可用 SCIVERSE_DR_SCRIPTS 环境变量指定 scripts 目录）" % script
    try:
        p = subprocess.run(
            [sys.executable, str(script)] + args,
            capture_output=True, text=True, timeout=TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        return "ERROR: 脚本执行超时（%ds）: %s" % (TIMEOUT, script.name)
    out = (p.stdout or "") + (("\n[stderr]\n" + p.stderr) if p.stderr else "")
    return "exit_code=%d\n%s" % (p.returncode, out.strip())


@mcp.tool()
def survey_ledger_validate(ledger_path: str) -> str:
    """校验引用台账 citation_ledger.json（键冲突、id 重复、schema）。每次向台账追加文献后必须重跑。

    Args:
        ledger_path: citation_ledger.json 的路径
    """
    return _run(LEDGER_PY, ["validate", "--ledger", ledger_path])


@mcp.tool()
def survey_compile(ledger_path: str, report_path: str, output_path: str) -> str:
    """交付编译：把键值草稿（[@键] 引用）按首现顺序铸成数字编号 [N]，同趟打印参考文献。

    草稿含手写数字引用或台账外未知键会直接报错；compile 成功之前禁止交付综述。

    Args:
        ledger_path: 已过 validate 的 citation_ledger.json 路径
        report_path: 键值草稿 markdown 路径（如 .workflow/draft.md）
        output_path: 编译输出路径（如 .workflow/final.md）——交付物是这个文件本身
    """
    return _run(LEDGER_PY, ["compile", "--ledger", ledger_path, "--report", report_path, "--output", output_path])


@mcp.tool()
def survey_check(report_path: str, citation_ledger_path: str = "", ledger_md_path: str = "", mode: str = "auto") -> str:
    """交付验收门禁：编号连续性、正文↔台账↔参考文献三方对齐、正文裸 URL/DOI、声明报数清点等。
    任何 FAIL 未消解不得交付。summary: 行需原样附在交付说明末尾作为门禁足迹。

    Args:
        report_path: compile 产出的 final.md 路径
        citation_ledger_path: compile 生成的 .delivery.json 台账路径（三方对齐检查用）
        ledger_md_path: 题录核验台账单独成文时的路径
        mode: auto / survey / strict
    """
    args = [report_path, "--mode", mode]
    if citation_ledger_path:
        args += ["--citation-ledger", citation_ledger_path]
    if ledger_md_path:
        args += ["--ledger", ledger_md_path]
    return _run(CHECK_PY, args)


@mcp.tool()
def survey_verify_citations(input_json_path: str, output_path: str = "verification_ledger.md", from_dir: str = "") -> str:
    """Crossref 题录核验（citation-guard 通道 1）：逐篇解析卷/期/页码/DOI/被引数并比对，产出核验台账。

    输入 JSON 格式: [{"id","title","first_author","journal"?,"doi"?,"year"?,"volume"?,"issue"?,"pages"?}, ...]
    网络受限时先用 --emit-urls 模式：把 from_dir 指向网页工具保存的 responses/ 目录离线核验。

    Args:
        input_json_path: 待核验文献清单 JSON 路径
        output_path: 核验台账输出路径（markdown）
        from_dir: 混合模式：离线消费已保存 Crossref JSON 的目录；留空则在线查询
    """
    args = []
    if from_dir:
        args += ["--from-dir", from_dir]
    args += [input_json_path, "-o", output_path]
    return _run(VERIFY_PY, args)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
