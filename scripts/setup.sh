#!/usr/bin/env bash
# setup.sh — hplan 전체 설치 스크립트 (로컬 클론 경로)
#
# 수행 작업:
#   1. ~/hplan 으로 클론 (이미 있으면 pull)
#   2. shell alias 등록 (claude-hplan-all / claude-hplan-gate)
#   3. git pre-commit hook 설치 (선택)
#
# 사용법:
#   bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan/main/scripts/setup.sh)
#   또는 클론 후:
#   bash scripts/setup.sh [--no-hooks] [--dir ~/hplan]

set -euo pipefail

# ── 기본값 ────────────────────────────────────────────────────────────
INSTALL_DIR="${HPLAN_DIR:-$HOME/hplan}"
INSTALL_HOOKS=true
REPO_URL="https://github.com/kimsanguine/hplan.git"

# ── 인자 파싱 ─────────────────────────────────────────────────────────
for arg in "$@"; do
  case "$arg" in
    --no-hooks) INSTALL_HOOKS=false ;;
    --dir=*)    INSTALL_DIR="${arg#--dir=}" ;;
    --help|-h)
      echo "사용법: bash setup.sh [--no-hooks] [--dir=<경로>]"
      echo "  --no-hooks     git pre-commit hook 설치 건너뜀"
      echo "  --dir=<경로>   설치 디렉터리 지정 (기본: ~/hplan)"
      exit 0 ;;
  esac
done

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║  hplan v0.9.2 — 전체 설치 스크립트      ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── 1. 클론 또는 업데이트 ─────────────────────────────────────────────
if [ -d "$INSTALL_DIR/.git" ]; then
  echo "▶ 기존 설치 발견 — 최신 버전으로 업데이트 중..."
  git -C "$INSTALL_DIR" pull --ff-only
else
  echo "▶ hplan 클론 중 → $INSTALL_DIR"
  git clone "$REPO_URL" "$INSTALL_DIR"
fi
echo "  ✅ 저장소 준비 완료"
echo ""

# ── 2. Shell alias 등록 ───────────────────────────────────────────────
# 사용 중인 shell 감지
if [ -n "${ZSH_VERSION:-}" ] || [ "$(basename "${SHELL:-bash}")" = "zsh" ]; then
  PROFILE="$HOME/.zshrc"
else
  PROFILE="$HOME/.bashrc"
fi

ALIAS_MARKER="# hplan-aliases"

if grep -q "$ALIAS_MARKER" "$PROFILE" 2>/dev/null; then
  echo "▶ Alias 이미 등록됨 — 건너뜀 ($PROFILE)"
else
  echo "▶ Shell alias 등록 중 → $PROFILE"
  cat >> "$PROFILE" << ALIASES

$ALIAS_MARKER
# 전체 5-plugin (gate + discover + architect + deliver + operate)
alias claude-hplan='claude \\
  --plugin-dir ${INSTALL_DIR}/hplan \\
  --plugin-dir ${INSTALL_DIR}/discover \\
  --plugin-dir ${INSTALL_DIR}/architect \\
  --plugin-dir ${INSTALL_DIR}/deliver \\
  --plugin-dir ${INSTALL_DIR}/operate'

# 게이트 전용 (WHETHER 판단만 필요할 때)
alias claude-hplan-gate='claude --plugin-dir ${INSTALL_DIR}/hplan'
ALIASES
  echo "  ✅ Alias 등록 완료"
fi
echo ""

# ── 3. Git pre-commit hook 설치 (선택) ───────────────────────────────
if $INSTALL_HOOKS; then
  if [ -f "$INSTALL_DIR/scripts/install-hooks.sh" ]; then
    # 현재 디렉터리가 git repo인 경우에만 설치
    if [ -d ".git" ]; then
      echo "▶ Git pre-commit hook 설치 중..."
      bash "$INSTALL_DIR/scripts/install-hooks.sh"
    else
      echo "▶ Git repo가 아님 — hook 설치 건너뜀"
      echo "  팁: 프로젝트 루트에서 실행하면 자동 설치됩니다."
    fi
  fi
else
  echo "▶ --no-hooks 지정 — hook 설치 건너뜀"
fi
echo ""

# ── 완료 메시지 ───────────────────────────────────────────────────────
echo "╔══════════════════════════════════════════╗"
echo "║  설치 완료!                              ║"
echo "╚══════════════════════════════════════════╝"
echo ""
echo "  shell을 재시작하거나 아래를 실행하세요:"
echo "    source $PROFILE"
echo ""
echo "  이후 사용법:"
echo "    claude-hplan           # 5-plugin 전체 로드"
echo "    claude-hplan-gate      # 게이트(hplan)만 로드"
echo ""
echo "  ⚠️  데스크탑 앱 사용자: --plugin-dir 플래그는 CLI 전용입니다."
echo "     데스크탑 앱에서는 Claude 세션에서 아래를 실행하세요:"
echo "     /plugin marketplace add kimsanguine/hplan"
echo "     /plugin install hplan@kimsanguine-hplan"
echo ""
