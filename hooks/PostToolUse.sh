#!/usr/bin/env bash
# hooks/PostToolUse.sh — ADK L3: Guardrail Layer (PostToolUse)
#
# Called by Claude Code after every Write/Edit tool use.
# Scans written content for accidental secret/token exposure.
#
# Detection patterns:
#   - API keys: sk-, pk-, Bearer, Authorization headers
#   - Cloud tokens: AKIA (AWS), ya29 (Google OAuth), xoxb/xoxp (Slack)
#   - Database URLs: postgres://, mongodb+srv://
#   - Common env var names: *_SECRET, *_TOKEN, *_KEY with real-looking values
#
# Exit codes:
#   0 → always (PostToolUse cannot block — it only warns)
#
# Registration: scripts/install-hooks.sh adds this to .claude/settings.json

set -euo pipefail

# Read full hook input from stdin
INPUT="$(cat)"

TOOL_NAME="$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || true)"

# Only scan Write and Edit operations
if [[ "$TOOL_NAME" != "Write" && "$TOOL_NAME" != "Edit" && "$TOOL_NAME" != "NotebookEdit" ]]; then
  exit 0
fi

FILE_PATH="$(echo "$INPUT" | python3 -c "import json,sys; d=json.load(sys.stdin); inp=d.get('tool_input',{}); print(inp.get('file_path',''))" 2>/dev/null || true)"

# Skip binary and lock files
if [[ "$FILE_PATH" =~ \.(png|jpg|jpeg|gif|mp4|mp3|pdf|zip|tar|lock|ico)$ ]]; then
  exit 0
fi

# Extract content (Write: content field; Edit: new_string field)
CONTENT="$(echo "$INPUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
inp = d.get('tool_input', {})
# Write has 'content'; Edit has 'new_string'
print(inp.get('content', '') or inp.get('new_string', ''))
" 2>/dev/null || true)"

if [ -z "$CONTENT" ]; then
  exit 0
fi

# Run secret scan — temp file avoids heredoc-in-command-substitution bash parse error
SCANNER=$(mktemp)
cat > "$SCANNER" << 'PYEOF'
import sys, re

PATTERNS = [
    (r'sk-[A-Za-z0-9]{20,}', 'OpenAI/Anthropic API key'),
    (r'pk-[A-Za-z0-9]{20,}', 'Public API key'),
    (r'AKIA[0-9A-Z]{16}', 'AWS Access Key ID'),
    (r'ya29\.[A-Za-z0-9_\-]{30,}', 'Google OAuth token'),
    (r'xox[bpoa]-[A-Za-z0-9\-]{10,}', 'Slack token'),
    (r'ghp_[A-Za-z0-9]{36}', 'GitHub personal access token'),
    (r'ghs_[A-Za-z0-9]{36}', 'GitHub Actions token'),
    (r'(?i)Bearer\s+[A-Za-z0-9\-_\.]{20,}', 'Bearer token'),
    (r'postgres://[^@]+:[^@]+@', 'PostgreSQL connection string with credentials'),
    (r'mongodb\+srv://[^@]+:[^@]+@', 'MongoDB connection string with credentials'),
    (r'mysql://[^@]+:[^@]+@', 'MySQL connection string with credentials'),
    (r'(?i)(API_KEY|SECRET_KEY|ACCESS_TOKEN|AUTH_TOKEN)\s*=\s*["\']?[A-Za-z0-9_\-]{16,}', 'Hardcoded secret env var'),
]

content = sys.stdin.read()
hits = []
for pattern, label in PATTERNS:
    if re.search(pattern, content):
        hits.append(label)

if hits:
    print('\n'.join(hits))
PYEOF
FINDINGS=$(echo "$CONTENT" | python3 "$SCANNER")
rm -f "$SCANNER"

if [ -n "$FINDINGS" ]; then
  echo "" >&2
  echo "hplan ⚠️  PostToolUse: Potential secrets detected ──────" >&2
  echo "  File: $FILE_PATH" >&2
  echo "$FINDINGS" | sed 's/^/  · /' >&2
  echo "  Action: verify these are not real credentials." >&2
  echo "  If real: remove from file, rotate the credential immediately." >&2
  echo "──────────────────────────────────────────────────────────" >&2
fi

# ── MD → HTML 자동 렌더링 ──────────────────────────────────
if [[ "$FILE_PATH" =~ \.md$ ]]; then
  SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  RENDERER="$SCRIPT_DIR/../hplan/scripts/md_renderer.py"
  if [ -f "$RENDERER" ]; then
    PYTHONPATH="$SCRIPT_DIR/../hplan/scripts" \
      python3 "$RENDERER" "$FILE_PATH" 2>/dev/null || true
  fi
fi
# ──────────────────────────────────────────────────────────

# PostToolUse always exits 0 — it cannot block (only warn)
exit 0
