#!/usr/bin/env bash
# install-hooks.sh — Install hplan hooks (ADK L3 Guardrail Layer + git enforcement).
#
# ADK Layer 3 = Three Claude Code hooks + git pre-commit:
#   SessionStart.sh  → display gate status at session start
#   PreToolUse.sh    → block writes without approved checkpoint (soft, UX layer)
#   PostToolUse.sh   → scan for accidental secret exposure (warn only)
#   git pre-commit   → hard block before the commit lands (enforcement layer)
#
# Why two layers?
#   Claude Code hooks (#17688) are intermittently unreliable.
#   Git pre-commit is deterministic — no model behavior dependency.
#   Both layers together = complete defense.
#
# Usage:
#   bash scripts/install-hooks.sh          # install all hooks
#   bash scripts/install-hooks.sh --remove # uninstall all hooks

set -euo pipefail

HOOK_PATH=".git/hooks/pre-commit"
MARKER="# hplan-gate-guard"
SETTINGS_FILE=".claude/settings.json"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$SCRIPT_DIR/../hooks"

# ─── Remove ─────────────────────────────────────────────────────────────────

remove_hook() {
  # Remove git pre-commit
  if [ -f "$HOOK_PATH" ] && grep -q "$MARKER" "$HOOK_PATH" 2>/dev/null; then
    rm "$HOOK_PATH"
    echo "hplan: git pre-commit hook removed."
  else
    echo "hplan: no hplan git pre-commit hook found — skipping."
  fi

  # Remove Claude Code hook entries from settings.json
  if [ -f "$SETTINGS_FILE" ] && command -v python3 &>/dev/null; then
    python3 - "$SETTINGS_FILE" << 'PYEOF'
import json, sys

path = sys.argv[1]
try:
    d = json.load(open(path))
    hooks = d.get("hooks", {})
    for event in ["PreToolUse", "PostToolUse", "SessionStart"]:
        if event in hooks:
            hooks[event] = [
                entry for entry in hooks[event]
                if not any("hplan" in str(h.get("command","")) for h in entry.get("hooks", []))
            ]
            if not hooks[event]:
                del hooks[event]
    if hooks:
        d["hooks"] = hooks
    elif "hooks" in d:
        del d["hooks"]
    json.dump(d, open(path, "w"), indent=2)
    print(f"hplan: Claude Code hooks removed from {path}")
except Exception as e:
    print(f"hplan: could not update {path}: {e}", file=sys.stderr)
PYEOF
  fi
  exit 0
}

if [ "${1:-}" = "--remove" ]; then
  remove_hook
fi

if [ ! -d ".git" ]; then
  echo "Error: run from the root of a git repository."
  exit 1
fi

if [ -f "$HOOK_PATH" ] && ! grep -q "$MARKER" "$HOOK_PATH" 2>/dev/null; then
  echo "Warning: existing pre-commit hook found (not from hplan)."
  echo "         Rename it to pre-commit.local and re-run, or chain manually."
  exit 1
fi

cat > "$HOOK_PATH" << 'HOOK'
#!/usr/bin/env bash
# hplan-gate-guard — git pre-commit enforcement layer.
# Blocks commits that include Build Gate artifacts (PRD.md, specs/*, etc.)
# unless harness/build-gate/checkpoint.json shows status="approved".

MARKER="# hplan-gate-guard"

GUARDED_RE="(PRD\.md|AGENTS\.md|ARCHITECTURE\.md|IMPLEMENTATION_READINESS\.md|METRICS\.md|specs/[0-9]{3}-|\.kiro/specs/)"
CHECKPOINT="harness/build-gate/checkpoint.json"

STAGED=$(git diff --cached --name-only 2>/dev/null)
GUARDED=$(echo "$STAGED" | grep -E "$GUARDED_RE" || true)

if [ -z "$GUARDED" ]; then
  exit 0
fi

# Bypass: CLAUDE_HPLAN_BYPASS=1 in environment
if [ "${CLAUDE_HPLAN_BYPASS:-}" = "1" ]; then
  echo "hplan pre-commit: bypass via CLAUDE_HPLAN_BYPASS=1" >&2
  exit 0
fi

# Read checkpoint from the staged index (not working tree) to prevent bypass via
# unstaged approved checkpoint. git show :path reads the index blob.
STAGED_CHECKPOINT=$(git show ":$CHECKPOINT" 2>/dev/null)

if [ -z "$STAGED_CHECKPOINT" ]; then
  echo "" >&2
  echo "hplan pre-commit BLOCKED ──────────────────────────" >&2
  echo "  Staged files require Build Gate approval:" >&2
  echo "$GUARDED" | sed 's/^/    /' >&2
  echo "  Missing from index: $CHECKPOINT" >&2
  echo "  Stage the approved checkpoint first: git add $CHECKPOINT" >&2
  echo "  Run /hplan \"<idea>\" to complete the gate first." >&2
  echo "────────────────────────────────────────────────────" >&2
  exit 1
fi

# Parse status, context_dates, and CONDITIONAL_GO fields from staged blob.
if command -v python3 &>/dev/null; then
  _TMP_JSON=$(mktemp)
  _TMP_PY=$(mktemp)
  printf '%s' "$STAGED_CHECKPOINT" > "$_TMP_JSON"
  cat > "$_TMP_PY" << 'PYEOF'
import json, sys, os
from datetime import date

THRESHOLDS = {
    'customer_interviews':  90,
    'competitive_analysis': 90,
    'provider_pricing':     60,
    'market_size':          180,
}

try:
    d = json.load(open(sys.argv[1]))
    status = d.get('status', '')
    today = date.today()

    # --- Freshness ---
    blocked_fresh = []
    for field, limit in THRESHOLDS.items():
        val = (d.get('context_dates') or {}).get(field, '')
        if val:
            try:
                age = (today - date.fromisoformat(val)).days
                if age > limit:
                    blocked_fresh.append(f'{field} ({age}d > {limit}d limit)')
            except ValueError:
                pass
    freshness = 'block:' + '|'.join(blocked_fresh) if blocked_fresh else 'ok'

    # --- CONDITIONAL_GO scope (commit-time checks) ---
    decision = d.get('decision', 'GO')
    scope = 'ok'
    if decision == 'CONDITIONAL_GO':
        expires_at = (d.get('expires_at') or '').strip()
        if expires_at:
            try:
                if today > date.fromisoformat(expires_at):
                    scope = f'expired:{expires_at}'
            except ValueError:
                pass
        if scope == 'ok':
            missing = [
                t for t in (d.get('required_tests') or [])
                if not os.path.exists(t)
            ]
            if missing:
                scope = 'missing_tests:' + '|'.join(missing)

    print(status, freshness, scope)
except Exception:
    print('', 'ok', 'ok')
PYEOF
  read -r STATUS FRESHNESS_VERDICT SCOPE_VERDICT <<< "$(python3 "$_TMP_PY" "$_TMP_JSON" 2>/dev/null)"
  rm -f "$_TMP_JSON" "$_TMP_PY"
else
  STATUS=$(echo "$STAGED_CHECKPOINT" | awk -F'"' '/"status"/{print $4; exit}')
  FRESHNESS_VERDICT="ok"
  SCOPE_VERDICT="ok"
fi

if [ "$STATUS" != "approved" ]; then
  echo "" >&2
  echo "hplan pre-commit BLOCKED ──────────────────────────" >&2
  echo "  Staged files require Build Gate approval:" >&2
  echo "$GUARDED" | sed 's/^/    /' >&2
  echo "  checkpoint.json status = \"$STATUS\" (need \"approved\")" >&2
  echo "  Run /hplan \"<idea>\" to complete the gate first." >&2
  echo "────────────────────────────────────────────────────" >&2
  exit 1
fi

# Freshness check against staged checkpoint context_dates
if [[ "$FRESHNESS_VERDICT" == block:* ]]; then
  STALE=$(echo "$FRESHNESS_VERDICT" | sed 's/^block://' | tr '|' '\n')
  echo "" >&2
  echo "hplan pre-commit BLOCKED ──────────────────────────" >&2
  echo "  Stale context_dates in staged checkpoint:" >&2
  echo "$STALE" | sed 's/^/    /' >&2
  echo "  Re-gather the stale evidence and re-run /hplan." >&2
  echo "────────────────────────────────────────────────────" >&2
  exit 1
fi

# CONDITIONAL_GO scope checks
if [[ "$SCOPE_VERDICT" == expired:* ]]; then
  EXP_DATE=$(echo "$SCOPE_VERDICT" | sed 's/^expired://')
  echo "" >&2
  echo "hplan pre-commit BLOCKED ──────────────────────────" >&2
  echo "  CONDITIONAL_GO expired on $EXP_DATE." >&2
  echo "  Re-run /hplan to reassess or obtain full GO approval." >&2
  echo "────────────────────────────────────────────────────" >&2
  exit 1
fi

if [[ "$SCOPE_VERDICT" == missing_tests:* ]]; then
  MISSING=$(echo "$SCOPE_VERDICT" | sed 's/^missing_tests://' | tr '|' '\n')
  echo "" >&2
  echo "hplan pre-commit BLOCKED ──────────────────────────" >&2
  echo "  CONDITIONAL_GO requires these test files to exist:" >&2
  echo "$MISSING" | sed 's/^/    /' >&2
  echo "  Create the required tests before committing." >&2
  echo "────────────────────────────────────────────────────" >&2
  exit 1
fi

# ─── Signal Gate: 4 evidence docs must exist in the staged index ────────────
SIGNAL_DOCS="harness/pain.md harness/cogs.md harness/market.md harness/competitors.md"
MISSING_SIGNAL=""
for sdoc in $SIGNAL_DOCS; do
  if ! git cat-file -e ":$sdoc" 2>/dev/null; then
    MISSING_SIGNAL="${MISSING_SIGNAL}    ${sdoc}
"
  fi
done
if [ -n "$MISSING_SIGNAL" ]; then
  echo "" >&2
  echo "hplan pre-commit BLOCKED ──────────────────────────" >&2
  echo "  Signal Gate documents missing from staged index:" >&2
  printf "%s" "$MISSING_SIGNAL" >&2
  echo "  Stage them (git add harness/*.md) and ensure /hplan \"<idea>\" completed." >&2
  echo "────────────────────────────────────────────────────" >&2
  exit 1
fi

# ─── Signal Gate: Staged docs must not contain placeholders ─────────────────
PLACEHOLDER_DOCS=""
for sdoc in $SIGNAL_DOCS; do
  STAGED_BLOB=$(git show ":$sdoc" 2>/dev/null || true)
  if [ -n "$STAGED_BLOB" ] && echo "$STAGED_BLOB" | grep -qiE '(TBD|미정|추후|나중에)'; then
    PLACEHOLDER_DOCS="${PLACEHOLDER_DOCS}    ${sdoc}
"
  fi
done
if [ -n "$PLACEHOLDER_DOCS" ]; then
  echo "" >&2
  echo "hplan pre-commit BLOCKED ──────────────────────────" >&2
  echo "  Signal Gate docs contain placeholders (TBD/미정/추후/나중에):" >&2
  printf "%s" "$PLACEHOLDER_DOCS" >&2
  echo "  Fill all evidence sources before committing." >&2
  echo "────────────────────────────────────────────────────" >&2
  exit 1
fi

# STATE.md 조건 anchor 소프트 경고
# 파일 없으면 스킵. 있으면 "추후 기입" 항목 수를 카운트해서 경고만 출력 (exit 0 유지).
if [ -f "harness/STATE.md" ] && command -v python3 &>/dev/null; then
  UNFILLED=$(python3 -c "
import re, sys
try:
    text = open('harness/STATE.md', encoding='utf-8').read()
    # verified_by 컬럼에 '추후 기입' 또는 경로 미기입 상태인 행 카운트
    rows = re.findall(r'\|\s*[^|]+\|\s*(추후 기입[^|]*|)\s*\|\s*❌', text)
    print(len(rows))
except Exception:
    print(0)
" 2>/dev/null)
  if [ "${UNFILLED:-0}" -gt 0 ]; then
    echo "" >&2
    echo "hplan ⚠️  STATE.md 조건 미검증 ─────────────────────" >&2
    echo "  verified_by 미기입 조건: ${UNFILLED}개" >&2
    echo "  완료 선언 전 /hplan-verify 실행을 권장합니다." >&2
    echo "  (커밋은 허용됩니다 — 경고만 표시)" >&2
    echo "────────────────────────────────────────────────────" >&2
  fi
fi

exit 0
HOOK

chmod +x "$HOOK_PATH"
echo "hplan: git pre-commit hook installed at $HOOK_PATH"

# ─── Claude Code Hooks (ADK L3) ─────────────────────────────────────────────

if [ ! -d "$HOOKS_DIR" ]; then
  echo "hplan: hooks/ directory not found — skipping Claude Code hook registration."
  echo "       (Run from the repo root that contains hooks/)"
  echo "       To remove: bash scripts/install-hooks.sh --remove"
  exit 0
fi

if ! command -v python3 &>/dev/null; then
  echo "hplan: python3 not found — skipping Claude Code settings.json update."
  echo "       Add hooks manually. See hooks/README.md."
  echo "       To remove: bash scripts/install-hooks.sh --remove"
  exit 0
fi

mkdir -p "$(dirname "$SETTINGS_FILE")"

python3 - "$SETTINGS_FILE" "$HOOKS_DIR" << 'PYEOF'
import json, sys, os
from pathlib import Path

settings_path = sys.argv[1]
hooks_dir     = sys.argv[2]

HOOK_ENTRIES = {
    "PreToolUse": {
        "matcher": "Write|Edit|NotebookEdit",
        "command": f"bash {hooks_dir}/PreToolUse.sh",
    },
    "PostToolUse": {
        "matcher": "Write|Edit",
        "command": f"bash {hooks_dir}/PostToolUse.sh",
    },
    "SessionStart": {
        "matcher": ".*",
        "command": f"bash {hooks_dir}/SessionStart.sh",
    },
}

# Load or create settings.json
if os.path.exists(settings_path):
    try:
        d = json.load(open(settings_path))
    except Exception:
        d = {}
else:
    d = {}

hooks = d.setdefault("hooks", {})

for event, cfg in HOOK_ENTRIES.items():
    event_list = hooks.setdefault(event, [])
    # Remove any existing hplan entry for this event
    event_list[:] = [
        e for e in event_list
        if not any("hplan" in str(h.get("command","")) for h in e.get("hooks", []))
    ]
    # Add fresh entry
    event_list.append({
        "matcher": cfg["matcher"],
        "hooks": [{"type": "command", "command": cfg["command"]}],
    })

json.dump(d, open(settings_path, "w"), indent=2)
print(f"hplan: Claude Code hooks registered in {settings_path}")
print(f"       · PreToolUse  → hooks/PreToolUse.sh  (gate enforcement)")
print(f"       · PostToolUse → hooks/PostToolUse.sh (secret scanner)")
print(f"       · SessionStart→ hooks/SessionStart.sh (gate status display)")
PYEOF

echo "       To remove: bash scripts/install-hooks.sh --remove"
