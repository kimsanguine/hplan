#!/usr/bin/env bash
# setup.sh — private hplan installer served from https://habix.ai/hplan/install.sh

set -euo pipefail

DEFAULT_BASE_URL="https://habix.ai/hplan"
BASE_URL="${HPLAN_BASE_URL:-${DEFAULT_BASE_URL}}"
BASE_URL="${BASE_URL%/}"
INSTALL_DIR="${HPLAN_DIR:-$HOME/hplan}"
INSTALL_HOOKS=true

for arg in "$@"; do
  case "$arg" in
    --no-hooks)
      INSTALL_HOOKS=false
      ;;
    --dir=*)
      INSTALL_DIR="${arg#--dir=}"
      ;;
    --help|-h)
      echo "Usage: bash setup.sh [--no-hooks] [--dir=<path>]"
      echo "  --no-hooks   Skip optional git hook installation"
      echo "  --dir=<path> Install directory (default: ~/hplan)"
      exit 0
      ;;
    *)
      echo "Unknown option: $arg" >&2
      echo "Run with --help for usage." >&2
      exit 1
      ;;
  esac
done

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

curl_args=(-fsSL --retry 2 --connect-timeout 10)
if [ -n "${HPLAN_TOKEN:-}" ]; then
  curl_args+=(-H "x-hplan-token: ${HPLAN_TOKEN}")
fi

download() {
  local url="$1"
  local output="$2"
  curl "${curl_args[@]}" "${url}" -o "${output}"
}

json_get() {
  local key="$1"
  local file="$2"

  if command -v python3 >/dev/null 2>&1; then
    python3 - "$key" "$file" <<'PY'
import json
import sys

key = sys.argv[1]
path = sys.argv[2]
with open(path, "r", encoding="utf-8") as handle:
    data = json.load(handle)
print(data.get(key, ""))
PY
  else
    sed -nE "s/.*\"${key}\"[[:space:]]*:[[:space:]]*\"([^\"]+)\".*/\1/p" "$file" | head -n 1
  fi
}

checksum() {
  if command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk '{print $1}'
  elif command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk '{print $1}'
  else
    echo "Neither shasum nor sha256sum is available." >&2
    exit 1
  fi
}

write_aliases() {
  local profile="$1"
  local marker="# hplan-aliases"

  touch "$profile"

  if grep -q "$marker" "$profile" 2>/dev/null; then
    echo "Alias block already exists in $profile"
    return
  fi

  cat >> "$profile" <<ALIASES

$marker
# hplan — Product Build Gate ADK
alias claude-hplan='claude \\
  --plugin-dir ${INSTALL_DIR}/hplan \\
  --plugin-dir ${INSTALL_DIR}/discover \\
  --plugin-dir ${INSTALL_DIR}/architect \\
  --plugin-dir ${INSTALL_DIR}/deliver \\
  --plugin-dir ${INSTALL_DIR}/operate'

alias claude-hplan-gate='claude --plugin-dir ${INSTALL_DIR}/hplan'
ALIASES
}

echo ""
echo "========================================"
echo " hplan private installer"
echo "========================================"
echo ""
echo "Manifest: ${BASE_URL}/version.json"

download "${BASE_URL}/version.json" "${TMP_DIR}/version.json"

PACKAGE_NAME="$(json_get package "${TMP_DIR}/version.json")"
EXPECTED_SHA="$(json_get sha256 "${TMP_DIR}/version.json")"
VERSION="$(json_get version "${TMP_DIR}/version.json")"
COMMIT="$(json_get commit "${TMP_DIR}/version.json")"

if [ -z "${PACKAGE_NAME}" ] || [ -z "${EXPECTED_SHA}" ]; then
  echo "Invalid hplan manifest. Missing package or sha256." >&2
  exit 1
fi

echo "Downloading: ${BASE_URL}/${PACKAGE_NAME}"
download "${BASE_URL}/${PACKAGE_NAME}" "${TMP_DIR}/${PACKAGE_NAME}"

ACTUAL_SHA="$(checksum "${TMP_DIR}/${PACKAGE_NAME}")"
if [ "$ACTUAL_SHA" != "$EXPECTED_SHA" ]; then
  echo "Checksum mismatch." >&2
  echo "Expected: ${EXPECTED_SHA}" >&2
  echo "Actual:   ${ACTUAL_SHA}" >&2
  exit 1
fi

mkdir -p "${TMP_DIR}/payload"
tar -xzf "${TMP_DIR}/${PACKAGE_NAME}" -C "${TMP_DIR}/payload"

SOURCE_DIR="${TMP_DIR}/payload/hplan"
if [ ! -f "${SOURCE_DIR}/hplan/.claude-plugin/plugin.json" ]; then
  echo "Package does not contain hplan/.claude-plugin/plugin.json." >&2
  exit 1
fi

PARENT_DIR="$(dirname "${INSTALL_DIR}")"
STAGING_DIR="${INSTALL_DIR}.staging.$$"
BACKUP_DIR="${INSTALL_DIR}.backup.$(date +%Y%m%d%H%M%S)"

mkdir -p "$PARENT_DIR"
rm -rf "$STAGING_DIR"
cp -R "$SOURCE_DIR" "$STAGING_DIR"

if [ -d "$INSTALL_DIR" ]; then
  mv "$INSTALL_DIR" "$BACKUP_DIR"
fi

mv "$STAGING_DIR" "$INSTALL_DIR"

if [ -d "$BACKUP_DIR" ]; then
  echo "Previous install backed up at $BACKUP_DIR"
fi

if [ -n "${ZSH_VERSION:-}" ] || [ "$(basename "${SHELL:-bash}")" = "zsh" ]; then
  PROFILE="$HOME/.zshrc"
else
  PROFILE="$HOME/.bashrc"
fi

write_aliases "$PROFILE"

if $INSTALL_HOOKS && [ -f "$INSTALL_DIR/scripts/install-hooks.sh" ]; then
  if [ -d ".git" ]; then
    echo "Installing optional git hooks into current repository..."
    bash "$INSTALL_DIR/scripts/install-hooks.sh"
  else
    echo "No .git directory here; optional hook installation skipped."
  fi
fi

echo ""
echo "hplan installed successfully."
echo "Version: ${VERSION:-unknown}"
echo "Commit: ${COMMIT:-unknown}"
echo "Location: ${INSTALL_DIR}"
echo ""
echo "Restart your shell or run:"
echo "  source ${PROFILE}"
echo ""
echo "Then use:"
echo "  claude-hplan"
echo "  claude-hplan-gate"
echo ""
