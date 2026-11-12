#!/usr/bin/env bash
# 登录 SkillHub 并发布当前 dist 包。
# 用法：
#   tools/publish_skillhub.sh              # 交互输入 Token（不回显、不进 shell 历史）
#   tools/publish_skillhub.sh skh_xxx      # 直接传 Token（会进 shell 历史）
#   CHANGELOG="修复 xxx" tools/publish_skillhub.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILL_DIR="$ROOT/dist/storyframe-video-skill"
HOST="https://api.skillhub.cn"

if [[ ! -f "$SKILL_DIR/SKILL.md" ]]; then
  echo "未找到 $SKILL_DIR/SKILL.md，先运行: python3 tools/package_skill.py" >&2
  exit 1
fi

CLI="$(command -v skillhub || true)"
if [[ -z "$CLI" ]]; then
  CLI="$HOME/.local/bin/skillhub"
fi
if [[ ! -x "$CLI" ]]; then
  echo "未找到 skillhub CLI。安装：" >&2
  echo '  curl -fsSL https://skillhub.cn/install/install.sh | bash -s -- --cli-only' >&2
  exit 1
fi

if [[ $# -gt 0 ]]; then
  TOKEN="$1"
else
  read -r -s -p "SkillHub API Token (skh_...): " TOKEN
  echo
fi

if [[ -z "${TOKEN:-}" ]]; then
  echo "Token 为空，已取消。" >&2
  exit 1
fi

"$CLI" login --key "$TOKEN" --host "$HOST"
unset TOKEN

VERSION="$(tr -d '[:space:]' < "$ROOT/VERSION")"
"$CLI" publish "$SKILL_DIR" \
  --host "$HOST" \
  --changelog "${CHANGELOG:-首次发布：Storyframe 视频生产系统 $VERSION}"
