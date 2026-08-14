#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
DIST_DIR="${ROOT_DIR}/dist"
PACKAGE_NAME="hplan-package.tar.gz"
PACKAGE_PATH="${DIST_DIR}/${PACKAGE_NAME}"

required_paths=(
  ".claude-plugin"
  "hplan"
  "discover"
  "architect"
  "deliver"
  "operate"
  "hooks"
  "harness"
  "profiles"
  "hplan-core-fixture"
  "scripts"
  "docs"
  "assets"
  "README.md"
  "README-ko.md"
  "GUIDE-ko.md"
  "CHANGELOG.md"
  "CLAUDE.md"
  "CONTRIBUTING.md"
  "LICENSE"
  "hplan-core.lock"
  "validate_plugins.py"
)

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

json_get() {
  local key="$1"
  local file="$2"
  python3 - "$key" "$file" <<'PY'
import json
import sys

key = sys.argv[1]
path = sys.argv[2]
with open(path, "r", encoding="utf-8") as handle:
    data = json.load(handle)
print(data.get(key, ""))
PY
}

if [ ! -f "${ROOT_DIR}/hplan/.claude-plugin/plugin.json" ]; then
  echo "Missing hplan plugin manifest." >&2
  exit 1
fi

VERSION="${HPLAN_VERSION:-$(json_get version "${ROOT_DIR}/hplan/.claude-plugin/plugin.json")}"
VERSION="${VERSION:-0.0.0-dev}"

COMMIT="${GITHUB_SHA:-}"
if [ -z "${COMMIT}" ]; then
  COMMIT="$(git -C "${ROOT_DIR}" rev-parse --short HEAD 2>/dev/null || true)"
fi
COMMIT="${COMMIT:-local}"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

PAYLOAD_DIR="${TMP_DIR}/hplan"
mkdir -p "${PAYLOAD_DIR}" "${DIST_DIR}"
rm -f "${PACKAGE_PATH}" "${DIST_DIR}/version.json"

for path in "${required_paths[@]}"; do
  if [ -e "${ROOT_DIR}/${path}" ]; then
    cp -R "${ROOT_DIR}/${path}" "${PAYLOAD_DIR}/"
  fi
done

find "${PAYLOAD_DIR}" -name "__pycache__" -type d -prune -exec rm -rf {} +
find "${PAYLOAD_DIR}" -name "*.pyc" -type f -exec rm -f {} +
find "${PAYLOAD_DIR}" -name ".DS_Store" -type f -exec rm -f {} +
find "${PAYLOAD_DIR}" -name ".pytest_cache" -type d -prune -exec rm -rf {} +
find "${PAYLOAD_DIR}" -name "node_modules" -type d -prune -exec rm -rf {} +
find "${PAYLOAD_DIR}" -name ".venv" -type d -prune -exec rm -rf {} +
find "${PAYLOAD_DIR}" -name "*.html" -path "*/harness/*" -type f -exec rm -f {} +
find "${PAYLOAD_DIR}" -path "*/harness/profiles" -type d -prune -exec rm -rf {} +
rm -f "${PAYLOAD_DIR}/PM-ENGINE-MEMORY.md"

tar -czf "${PACKAGE_PATH}" -C "${TMP_DIR}" hplan

SHA256="$(checksum "${PACKAGE_PATH}")"
BUILT_AT="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

cat > "${DIST_DIR}/version.json" <<JSON
{
  "name": "hplan",
  "version": "${VERSION}",
  "commit": "${COMMIT}",
  "built_at": "${BUILT_AT}",
  "package": "${PACKAGE_NAME}",
  "sha256": "${SHA256}",
  "install": "install.sh"
}
JSON

echo "Built ${PACKAGE_PATH}"
echo "SHA256 ${SHA256}"
