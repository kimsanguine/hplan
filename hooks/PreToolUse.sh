#!/usr/bin/env bash
# hooks/PreToolUse.sh — ADK L3: Guardrail Layer (PreToolUse)
#
# Called by Claude Code before every Write/Edit/NotebookEdit tool use.
# Delegates to gate_guard.py which enforces:
#   - Signal Gate: block PRD/ARCHITECTURE writes without approved checkpoint
#   - No-Placeholder Gate: block TBD/미정/추후/나중에 in evidence documents
#   - Evidence Source Check: warn/block when evidence docs lack sources
#
# Exit codes:
#   0  → allow the tool use
#   2  → block the tool use (Claude Code shows the stderr message)
#
# Registration: scripts/install-hooks.sh adds this to .claude/settings.json

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GATE_GUARD="$SCRIPT_DIR/../hplan/hooks/gate_guard.py"

if [ ! -f "$GATE_GUARD" ]; then
  # Gate guard not found — fail open (don't block Claude Code)
  exit 0
fi

exec python3 "$GATE_GUARD"
