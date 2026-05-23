# hooks/ — ADK Layer 3: Guardrail Hooks

Three shell scripts that register as Claude Code hooks via `scripts/install-hooks.sh`.
Together with the git pre-commit hook, they form hplan's dual-defense enforcement layer.

## Quick Setup

```bash
bash scripts/install-hooks.sh    # installs all hooks
/harness-doctor                  # verify installation
```

## Hook Descriptions

| File | Event | What it does |
|------|-------|-------------|
| `SessionStart.sh` | Session start | Displays Build Gate status + Signal Gate doc inventory |
| `PreToolUse.sh` | Before Write/Edit | Delegates to `hplan/hooks/gate_guard.py` — blocks PRD writes without approved checkpoint |
| `PostToolUse.sh` | After Write/Edit | Scans written content for accidental secret/token exposure |

## Manual Test

```bash
# Test PreToolUse (should exit 2 — block — for PRD.md writes)
echo '{"tool_name":"Write","tool_input":{"file_path":"harness/PRD.md","content":"test"}}' \
  | bash hooks/PreToolUse.sh; echo "exit: $?"

# Test PostToolUse (should warn for content with API keys)
echo '{"tool_name":"Write","tool_input":{"file_path":"test.md","content":"sk-abc123456789012345678901234567890"},"tool_result":""}' \
  | bash hooks/PostToolUse.sh; echo "exit: $?"

# Test SessionStart (should display gate status banner)
bash hooks/SessionStart.sh
```

## Uninstall

```bash
bash scripts/install-hooks.sh --remove
```

## How Registration Works

`scripts/install-hooks.sh` writes to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart":  [{ "matcher": ".*",               "hooks": [{ "type": "command", "command": "bash hooks/SessionStart.sh" }] }],
    "PreToolUse":    [{ "matcher": "Write|Edit|NotebookEdit", "hooks": [{ "type": "command", "command": "bash hooks/PreToolUse.sh" }] }],
    "PostToolUse":   [{ "matcher": "Write|Edit",       "hooks": [{ "type": "command", "command": "bash hooks/PostToolUse.sh" }] }]
  }
}
```

> **Note:** Claude Code hooks have a known intermittent issue ([#17688](https://github.com/anthropics/claude-code/issues/17688)).
> The git pre-commit hook installed by `install-hooks.sh` is the deterministic enforcement fallback.
