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

  if [ -n "${HPLAN_PROFILE:-}" ]; then
    profile_path="$HPLAN_PROFILE"
  elif [ "$(basename "${SHELL:-bash}")" = "zsh" ]; then
    profile_path="$HOME/.zshrc"
  else
    profile_path="$HOME/.bashrc"
  fi
  launcher_ready=false
  launcher_issue=""
  if [ -f "$profile_path" ] && grep -Fq "alias claude-hplan=" "$profile_path"; then
    launcher_ready=true
    for plugin in hplan discover architect deliver operate; do
      if [ ! -d "${ROOT_DIR}/${plugin}" ] || [ ! -r "${ROOT_DIR}/${plugin}" ]; then
        launcher_ready=false
        launcher_issue="${plugin} plugin directory is missing or unreadable"
        break
      fi
      if ! grep -Fq -- "--plugin-dir ${ROOT_DIR}/${plugin}" "$profile_path"; then
        launcher_ready=false
        launcher_issue="${plugin} plugin-dir is not registered"
        break
      fi
    done
  fi
  if "$launcher_ready"; then
    normal_check "claude-hplan launcher" "${profile_path}에 이 설치 경로의 5개 plugin-dir가 등록되어 있습니다."
  else
    launcher_detail="이 설치 경로의 launcher를 ${profile_path}에서 찾지 못했습니다."
    if [ -n "$launcher_issue" ]; then
      launcher_detail="${launcher_issue}."
    fi
    recoverable_check "claude-hplan launcher" "$launcher_detail" "bash scripts/setup.sh --dir \"${ROOT_DIR}\" --no-hooks 를 실행한 뒤 source \"${profile_path}\" 하세요."
  fi

  if command -v python3 >/dev/null 2>&1 && python3 -c 'import json, sys; assert sys.version_info >= (3, 9)' >/dev/null 2>&1; then
    normal_check "Python" "$(python3 --version 2>&1)"
  else
    escalate_check "Python" "Python 3.9 이상이 필요합니다." "Python 3.9 이상을 설치한 뒤 다시 실행하세요."
  fi

  if command -v python3 >/dev/null 2>&1; then
    snapshot_result="$(python3 - "$ROOT_DIR" "$SCRIPT_DIR/../hplan-core-fixture/contracts" <<'PY'
import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
fixture_contracts = Path(sys.argv[2])
required = {
    "lock": root / "runtime" / "hplan-core" / "hplan-core.lock",
    "matrix": root / "runtime" / "hplan-core" / "hplan-capability-matrix.json",
    "markdown": root / "runtime" / "hplan-core" / "HPLAN_CAPABILITY_MATRIX.md",
    "adapter": root / "runtime" / "hplan-core" / "hplan-core-adapter.json",
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
    print(f"INVALID|hplan-core snapshot 무결성 실패: JSON을 읽을 수 없습니다: {exc}")
    raise SystemExit

try:
    fixture_rules = json.loads((fixture_contracts / "rules.json").read_text(encoding="utf-8"))
    fixture_capabilities = json.loads((fixture_contracts / "capabilities.json").read_text(encoding="utf-8"))
    fixture_aliases = json.loads((fixture_contracts / "aliases.json").read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    print(f"INVALID|hplan-core snapshot 무결성 실패: pinned core fixture를 읽을 수 없습니다: {exc}")
    raise SystemExit

def digest_contracts(directory):
    import hashlib
    digest = hashlib.sha256()
    for filename in ("rules.json", "capabilities.json", "aliases.json"):
        digest.update(filename.encode("utf-8"))
        digest.update(b"\0")
        digest.update((directory / filename).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()

expected_rule_ids = {entry.get("rule_id") for entry in fixture_rules.get("rules", []) if isinstance(entry, dict)}
expected_capability_lifecycles = {
    entry.get("capability_id"): entry.get("lifecycle")
    for entry in fixture_capabilities.get("capabilities", [])
    if isinstance(entry, dict)
}
expected_aliases = {
    entry.get("alias_id"): (entry.get("target"), entry.get("expiry"))
    for entry in fixture_aliases.get("aliases", [])
    if isinstance(entry, dict)
}
expected_source = digest_contracts(fixture_contracts)

expected_files = [
    "hplan-core.lock",
    "hplan-capability-matrix.json",
    "HPLAN_CAPABILITY_MATRIX.md",
    "hplan-core-adapter.json",
]
hex64 = re.compile(r"[0-9a-f]{64}\Z")
errors = []

if not isinstance(lock, dict):
    errors.append("lock 형식")
if not isinstance(matrix, dict):
    errors.append("matrix 형식")
if not isinstance(adapter, dict):
    errors.append("adapter 형식")

if not errors:
    version = lock.get("contract_version")
    source = lock.get("source_sha256")
    if lock.get("target") != "claude" or not isinstance(version, str) or not version:
        errors.append("lock target/version")
    if lock.get("files") != expected_files:
        errors.append("lock files")
    if not isinstance(source, str) or not hex64.fullmatch(source):
        errors.append("lock source_sha256")
    if lock.get("core_source_sha256") != source:
        errors.append("lock core_source_sha256")
    if source != expected_source:
        errors.append("pinned core source identity")

    rules = matrix.get("rules")
    capabilities = matrix.get("capabilities")
    aliases = matrix.get("aliases")
    if matrix.get("target") != "claude" or matrix.get("contract_version") != version:
        errors.append("matrix target/version")
    if not isinstance(rules, list) or len(rules) != 9:
        errors.append("9 rules")
    elif any(not isinstance(rule, dict) or not isinstance(rule.get("rule_id"), str) or not rule["rule_id"] for rule in rules) or len({rule["rule_id"] for rule in rules}) != 9:
        errors.append("unique rule ids")
    elif {rule["rule_id"] for rule in rules} != expected_rule_ids:
        errors.append("canonical rule id set")
    if not isinstance(capabilities, list) or len(capabilities) != 34:
        errors.append("34 capabilities")
        capabilities = []
    capability_ids = []
    for capability in capabilities:
        if not isinstance(capability, dict):
            errors.append("capability type")
            continue
        capability_id = capability.get("capability_id")
        capability_ids.append(capability_id)
        if (
            not isinstance(capability_id, str)
            or not capability_id
            or capability.get("canonical_owner") != "hplan-core"
            or capability.get("support_state") != "native"
            or capability.get("entrypoint") != f"capability:{capability_id}"
            or capability.get("smoke_fixture_id") != f"smoke.{capability_id}"
            or not isinstance(capability.get("fallback_artifact"), str)
            or not capability["fallback_artifact"]
            or not isinstance(capability.get("lifecycle"), str)
            or not capability["lifecycle"]
        ):
            errors.append("capability entrypoint/fallback")
    if len(capability_ids) != 34 or len(set(capability_ids)) != 34:
        errors.append("unique canonical capability ids")
    elif set(capability_ids) != set(expected_capability_lifecycles):
        errors.append("canonical capability id set")
    elif any(capability.get("lifecycle") != expected_capability_lifecycles[capability["capability_id"]] for capability in capabilities):
        errors.append("canonical capability lifecycle")
    if not isinstance(aliases, list) or len(aliases) != 3:
        errors.append("3 aliases")
    elif any(
        not isinstance(alias, dict)
        or not all(isinstance(alias.get(key), str) and alias[key] for key in ("alias_id", "target", "expiry"))
        for alias in aliases
    ) or len({alias["alias_id"] for alias in aliases}) != 3:
        errors.append("unique alias ids")
    elif {alias["alias_id"]: (alias["target"], alias["expiry"]) for alias in aliases} != expected_aliases:
        errors.append("canonical alias mapping")

    if (
        adapter.get("target") != "claude"
        or adapter.get("core_version") != version
        or adapter.get("core_source_sha256") != source
        or adapter.get("capability_status_source") != "hplan-capability-matrix.json"
        or adapter.get("native_execution_policy") != "entrypoint-and-smoke-fixture-required"
        or adapter.get("non_native_fallback") != "fallback_artifact"
        or adapter.get("external_connector_writes") != "disabled"
    ):
        errors.append("adapter policy")

    try:
        markdown = required["markdown"].read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"markdown read: {exc}")
        markdown = ""
    if f"Contract version: `{version}`" not in markdown or "Target: `claude`" not in markdown:
        errors.append("markdown target/version")
    if any(f"| {capability_id} |" not in markdown for capability_id in capability_ids if isinstance(capability_id, str)):
        errors.append("markdown capability rows")

if errors:
    print("INVALID|hplan-core snapshot 무결성 실패: " + ", ".join(dict.fromkeys(errors)))
else:
    print(f"OK|contract {version}, 9 rules, 3 aliases, 34 unique capabilities, external writes disabled")
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
