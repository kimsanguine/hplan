#!/usr/bin/env bash
# hooks/SessionStart.sh — ADK L3: Guardrail Layer (SessionStart)
#
# Called by Claude Code at the start of every session.
# Displays the current hplan gate status so the agent starts informed:
#   - Build Gate: checkpoint.json status (approved / pending / missing)
#   - STATE.md: active conditions and their verification state
#   - Evidence docs: which Signal Gate docs are present
#
# Exit codes:
#   0 → always (SessionStart cannot block sessions)
#
# Registration: scripts/install-hooks.sh adds this to .claude/settings.json

set -euo pipefail

PROJECT_DIR="$(pwd)"
CHECKPOINT="$PROJECT_DIR/harness/build-gate/checkpoint.json"
STATE_MD="$PROJECT_DIR/harness/STATE.md"

echo "" >&2
echo "┌─ hplan Gate Status ────────────────────────────────────┐" >&2

# --- Build Gate checkpoint ---
if [ -f "$CHECKPOINT" ]; then
  if command -v python3 &>/dev/null; then
    python3 - "$CHECKPOINT" << 'PYEOF' 2>/dev/null || true
import json, sys
from datetime import date

path = sys.argv[1]
try:
    d = json.load(open(path))
    status   = d.get("status", "unknown")
    decision = d.get("decision", "")
    idea     = d.get("idea", "")[:50]
    ts       = d.get("timestamp", "")[:10]

    icon = "✅" if status == "approved" else ("⚠️ " if status == "pending" else "❌")
    print(f"│  {icon} Build Gate   {status.upper()}", file=sys.stderr)
    if decision:
        print(f"│     Decision : {decision}", file=sys.stderr)
    if idea:
        print(f"│     Idea     : {idea}", file=sys.stderr)
    if ts:
        print(f"│     Date     : {ts}", file=sys.stderr)
except Exception:
    print("│  ❓ Build Gate   checkpoint.json unreadable", file=sys.stderr)
PYEOF
  else
    echo "│  ✅ Build Gate   checkpoint.json present" >&2
  fi
else
  echo "│  ─  Build Gate   no checkpoint (gate not run yet)" >&2
fi

echo "│" >&2

# --- Signal Gate docs ---
DOCS=("harness/pain.md" "harness/cogs.md" "harness/market.md" "harness/competitors.md")
MISSING=0
for doc in "${DOCS[@]}"; do
  if [ -f "$PROJECT_DIR/$doc" ]; then
    echo "│  ✅ $(basename "$doc" .md)" >&2
  else
    echo "│  ─  $(basename "$doc" .md)   missing" >&2
    MISSING=$((MISSING + 1))
  fi
done

echo "│" >&2

# --- STATE.md summary ---
if [ -f "$STATE_MD" ]; then
  if command -v python3 &>/dev/null; then
    python3 - "$STATE_MD" << 'PYEOF' 2>/dev/null || true
import re, sys

path = sys.argv[1]
try:
    text = open(path, encoding="utf-8").read()
    ok_count  = len(re.findall(r'✅', text))
    fail_count = len(re.findall(r'❌', text))
    print(f"│  STATE.md     {ok_count} ✅ / {fail_count} ❌ conditions", file=sys.stderr)
except Exception:
    print("│  STATE.md     present (unreadable)", file=sys.stderr)
PYEOF
  else
    echo "│  ✅ STATE.md   present" >&2
  fi
else
  echo "│  ─  STATE.md   not created yet" >&2
fi

echo "│" >&2
echo "│  Run /harness-doctor for full diagnostics" >&2
echo "└────────────────────────────────────────────────────────┘" >&2
echo "" >&2

exit 0
