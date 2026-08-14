#!/usr/bin/env bash
# Read-only installation check for the Claude adapter. It never installs, edits, or sends data.

set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

usage() {
  echo "Usage: bash scripts/hplan-doctor.sh [--root <hplan-directory>]"
  echo "Runs a read-only Claude hplan installation check."
}

if [ "${1:-}" = "--help" ] || [ "${1:-}" = "-h" ]; then
  usage
  exit 0
fi

if [ "${1:-}" = "--root" ]; then
  if [ -z "${2:-}" ] || [ "${3:-}" != "" ]; then
    usage >&2
    exit 2
  fi
  ROOT_DIR="$2"
elif [ "${1:-}" != "" ]; then
  usage >&2
  exit 2
fi

normal=0
recoverable=0
escalate=0

normal_check() {
  normal=$((normal + 1))
  printf '[정상] %s — %s\n' "$1" "$2"
}

recoverable_check() {
  recoverable=$((recoverable + 1))
  printf '[자동 복구 가능] %s — %s\n  다음 조치: %s\n' "$1" "$2" "$3"
}

escalate_check() {
  escalate=$((escalate + 1))
  printf '[강사 호출] %s — %s\n  다음 조치: %s\n' "$1" "$2" "$3"
}

echo "hplan doctor — Claude adapter"
echo "점검 범위: ${ROOT_DIR}"
echo "읽기 전용 점검입니다. 파일·설정·외부 시스템을 변경하지 않습니다."
echo

if [ ! -d "$ROOT_DIR" ]; then
  escalate_check "설치 경로" "지정한 hplan 디렉터리를 찾을 수 없습니다." "설치 경로를 확인한 뒤 다시 설치하거나 강사에게 경로를 문의하세요."
else
  if command -v claude >/dev/null 2>&1; then
    claude_version="$(claude --version 2>&1 | head -n 1)"
    normal_check "Claude Code" "${claude_version:-버전 확인 완료}"
  else
    recoverable_check "Claude Code" "claude 명령을 찾을 수 없습니다." "Claude Code를 설치한 뒤 새 터미널에서 다시 실행하세요."
  fi

  if command -v python3 >/dev/null 2>&1 && python3 -c 'import json, sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
    normal_check "Python" "$(python3 --version 2>&1)"
  else
    escalate_check "Python" "Python 3.9 이상이 필요합니다." "Python 3.9 이상을 설치한 뒤 다시 실행하세요."
  fi

  if command -v python3 >/dev/null 2>&1; then
    snapshot_result="$(python3 - "$ROOT_DIR" <<'PY'
import json
import sys
from pathlib import Path

root = Path(sys.argv[1])
required = {
    "lock": root / "hplan-core.lock",
    "matrix": root / "docs" / "hplan-capability-matrix.json",
    "markdown": root / "docs" / "HPLAN_CAPABILITY_MATRIX.md",
    "adapter": root / "docs" / "hplan-core-adapter.json",
}
missing = [str(path.relative_to(root)) for path in required.values() if not path.is_file()]
if missing:
    print("MISSING|" + ", ".join(missing))
    raise SystemExit

try:
    lock = json.loads(required["lock"].read_text(encoding="utf-8"))
    matrix = json.loads(required["matrix"].read_text(encoding="utf-8"))
    adapter = json.loads(required["adapter"].read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"INVALID|JSON을 읽을 수 없습니다: {exc}")
    raise SystemExit

expected_files = [
    "hplan-core.lock",
    "hplan-capability-matrix.json",
    "HPLAN_CAPABILITY_MATRIX.md",
    "hplan-core-adapter.json",
]
version = lock.get("contract_version")
source = lock.get("source_sha256")
valid = (
    lock.get("target") == "claude"
    and lock.get("files") == expected_files
    and isinstance(source, str)
    and len(source) == 64
    and matrix.get("target") == "claude"
    and matrix.get("contract_version") == version
    and len(matrix.get("capabilities", [])) == 34
    and adapter.get("target") == "claude"
    and adapter.get("core_version") == version
    and adapter.get("core_source_sha256") == source
    and adapter.get("external_connector_writes") == "disabled"
    and f"Contract version: `{version}`" in required["markdown"].read_text(encoding="utf-8")
    and "Target: `claude`" in required["markdown"].read_text(encoding="utf-8")
)
if not valid:
    print("INVALID|lock, matrix, markdown, adapter의 대상·버전·보호 정책이 일치하지 않습니다.")
else:
    print(f"OK|contract {version}, 34 capabilities, external writes disabled")
PY
)"
    case "$snapshot_result" in
      OK\|*)
        normal_check "hplan-core snapshot" "${snapshot_result#OK|}"
        ;;
      MISSING\|*)
        escalate_check "hplan-core snapshot" "필수 artifact 누락: ${snapshot_result#MISSING|}" "hplan을 다시 설치한 뒤에도 계속되면 강사에게 이 출력 전체를 보내세요."
        ;;
      *)
        escalate_check "hplan-core snapshot" "${snapshot_result#INVALID|}" "hplan을 다시 설치한 뒤에도 계속되면 강사에게 이 출력 전체를 보내세요."
        ;;
    esac
  else
    escalate_check "hplan-core snapshot" "Python이 없어 snapshot 무결성을 확인할 수 없습니다." "먼저 Python 3.9 이상을 설치한 뒤 다시 실행하세요."
  fi
fi

echo
echo "요약: 정상 ${normal} / 자동 복구 가능 ${recoverable} / 강사 호출 ${escalate}"
if [ "$escalate" -gt 0 ]; then
  exit 1
fi
