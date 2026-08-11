#!/usr/bin/env bash
# sciverse-deep-research 安装脚本
# 做的事：检测本机已安装的 agent → 把 skill 符号链接进各 agent 的 skills 目录
# 不做的事：不修改任何 agent 的配置文件——MCP 配置片段只打印出来，由你手动粘贴确认。
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_SRC="$REPO/skills/sciverse-deep-research"
SKILL_NAME="sciverse-deep-research"

if [ ! -f "$SKILL_SRC/SKILL.md" ]; then
  echo "ERROR: $SKILL_SRC/SKILL.md 不存在——skills 内容还没就位？" >&2
  exit 1
fi

# agent 名 → skills 目录（存在父目录才安装）
declare -a AGENTS=(
  "claude-code|$HOME/.claude/skills"
  "codex|$HOME/.codex/skills"
  "kimi-code|$HOME/.kimi-code/skills"
  "opencode|$HOME/.config/opencode/skills"
  "qwen-code|$HOME/.agents/skills"
  # Hermes 的 skill 必须放在分类子目录下（research/*）才会被扫描识别——放顶层识别不到
  "hermes|$HOME/.hermes/skills/research"
  "openclaw|$HOME/.openclaw/skills"
)

installed=()
conflicted=()
failed=()

# 单个 agent 的安装子例程。返回码：0=已链接（含修复断链），1=有冲突需手动处理，
# 2=未检测到该 agent，3=安装动作本身失败。任何返回码都不中断后续 agent。
install_one() {
  local name="$1" dir="$2"
  local parent target dest
  parent="$(dirname "$dir")"
  if [ ! -d "$parent" ] && [ ! -d "$dir" ]; then
    echo "[$name] 未检测到安装（$parent 不存在），跳过"
    return 2
  fi
  mkdir -p "$dir" || { echo "[$name] mkdir $dir 失败" >&2; return 3; }
  target="$dir/$SKILL_NAME"
  if [ -L "$target" ]; then
    dest="$(readlink "$target")"
    if [ "$dest" = "$SKILL_SRC" ]; then
      echo "[$name] 已链接，跳过"
    elif [ ! -e "$target" ]; then
      # 失效符号链接（断链，多为仓库搬过家）——目标已不存在，直接修正指向
      ln -sfn "$SKILL_SRC" "$target" || { echo "[$name] 修复断链失败" >&2; return 3; }
      echo "[$name] 修复断链: $target -> $SKILL_SRC（原指向 $dest）"
    else
      echo "[$name] $target 已是指向其他位置的链接（$dest），跳过（请手动处理）" >&2
      return 1
    fi
  elif [ -e "$target" ]; then
    echo "[$name] $target 已存在且不是符号链接，跳过（请手动处理）" >&2
    return 1
  else
    ln -s "$SKILL_SRC" "$target" || { echo "[$name] ln -s 失败" >&2; return 3; }
    echo "[$name] skill 已链接: $target -> $SKILL_SRC"
  fi
  return 0
}

for entry in "${AGENTS[@]}"; do
  name="${entry%%|*}"; dir="${entry##*|}"
  rc=0
  install_one "$name" "$dir" || rc=$?
  case $rc in
    0) installed+=("$name") ;;
    1) conflicted+=("$name") ;;
    3) failed+=("$name") ;;
  esac
done

if [ "${#conflicted[@]}" -gt 0 ] || [ "${#failed[@]}" -gt 0 ]; then
  echo "" >&2
  [ "${#conflicted[@]}" -gt 0 ] && echo "需手动处理（目标被占用）：${conflicted[*]}" >&2
  [ "${#failed[@]}" -gt 0 ] && echo "安装失败：${failed[*]}" >&2
fi

cat <<EOF

====================================================================
skill 安装完成（${#installed[@]} 个 agent）：${installed[*]:-无}

接下来手动配置两个 MCP server（各 agent 配置文件格式见 agents/ 目录）：

【1】sciverse 官方检索 server（需要 SCIVERSE_API_TOKEN）：
{
  "mcpServers": {
    "sciverse": {
      "command": "npx",
      "args": ["-y", "sciverse-mcp-server"],
      "env": { "SCIVERSE_API_TOKEN": "<你的 token>" }
    }
  }
}

【2】本仓库的门禁 server（台账 validate / compile / 交付 check / 题录核验）：
{
  "mcpServers": {
    "sciverse-survey-gates": {
      "command": "$HOME/.local/bin/uv",
      "args": ["run", "--project", "$REPO/mcp-server", "sciverse-survey-gates"]
    }
  }
}

注意：某些 agent 启动 MCP 时 PATH 极简，建议 uv/npx 都用绝对路径，
必要时在 env 里补 PATH（参考 ~/.kimi-code/mcp.json 的写法）。
====================================================================
EOF
