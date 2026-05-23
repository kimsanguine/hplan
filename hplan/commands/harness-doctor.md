---
description: "Diagnostic health check for hplan installation — verifies Claude Code hook registration, gate_guard execution, checkpoint state, exclusions registry integrity, and git pre-commit hook. Run after fresh install, when gate behavior is unexpected, or to confirm setup is correct."
argument-hint: ""
allowed-tools: ["Read", "Bash"]
---

# /harness-doctor

Runs 5 deterministic checks and reports `[ PASS ]`, `[ WARN ]`, or `[ FAIL ]` per item.

## Instructions

You are running the **hplan installation health check**.

Execute all 5 checks in sequence. Do not skip any check. Collect all results, then output the summary block.

---

### Check 1 — Claude Code Hook Registration

```bash
cat .claude/settings.json 2>/dev/null || cat ~/.claude/settings.json 2>/dev/null
```

- **PASS**: Output contains `gate_guard.py` under `PreToolUse` hooks
- **WARN**: `settings.json` not found — hook may not be registered
- **FAIL**: File found but `gate_guard.py` not in `PreToolUse`

Remedy if WARN/FAIL: add the hook path to `.claude/settings.json` under `hooks.PreToolUse`.

---

### Check 2 — gate_guard.py Execution

```bash
echo '{"tool_input": {"file_path": "docs/PRD.md"}}' \
  | python3 hplan/hooks/gate_guard.py
echo "exit=$?"
```

- **PASS**: `exit=2` — gate_guard blocked the write as expected (no checkpoint present)
- **WARN**: `exit=0` — gate_guard ran but did not block (checkpoint may already exist)
- **FAIL**: Any Python error or `hplan/hooks/gate_guard.py` not found

Note: `exit=2` is the *correct* behavior here. The hook is designed to block writes to protected files until `harness/build-gate/checkpoint.json` shows `status: "approved"`.

---

### Check 3 — Checkpoint State

```bash
python3 -c "
import json, pathlib, sys
cp = pathlib.Path('harness/build-gate/checkpoint.json')
if not cp.exists():
    print('MISSING')
    sys.exit(0)
try:
    d = json.loads(cp.read_text())
    print(d.get('status', 'NO_STATUS'))
except Exception as e:
    print(f'PARSE_ERROR: {e}')
"
```

- **PASS (approved)**: Project has passed the Build Gate — writes to PRD/spec files are unblocked
- **PASS (MISSING)**: No checkpoint yet — normal for a project that hasn't run `/harness-build` yet
- **WARN (CONDITIONAL_GO / other status)**: Gate was run but not fully approved
- **FAIL (PARSE_ERROR)**: `checkpoint.json` is malformed — delete it and re-run `/harness-build`

---

### Check 4 — Exclusions Registry Integrity

```bash
python3 hplan/scripts/exclusions_registry.py list 2>&1 | head -10
echo "exit=$?"
```

- **PASS**: Valid JSON output or empty output with `exit=0` (empty registry is normal)
- **FAIL**: JSON parse error or `exit != 0`

Remedy if FAIL: delete `harness/exclusions.jsonl` and re-add exclusions via `/harness-exclude`.

---

### Check 5 — Git Pre-commit Hook

```bash
if [ -f .git/hooks/pre-commit ]; then
  grep -q "hplan" .git/hooks/pre-commit && echo "INSTALLED" || echo "NO_HPLAN_MARKER"
else
  echo "NOT_INSTALLED"
fi
```

- **PASS**: `INSTALLED` — git pre-commit hook contains hplan marker
- **WARN (NOT_INSTALLED)**: No pre-commit hook — run `bash scripts/install-hooks.sh` to install
- **WARN (NO_HPLAN_MARKER)**: A pre-commit hook exists from another tool — hplan hook not added

---

## Output Format

After all 5 checks, output this block:

```
hplan-doctor — [DATE]

[ PASS/WARN/FAIL ] Hook registration    [detail]
[ PASS/WARN/FAIL ] Hook execution       [detail]
[ PASS/WARN/FAIL ] Checkpoint           [detail]
[ PASS/WARN/FAIL ] Exclusions registry  [detail]
[ PASS/WARN/FAIL ] Git pre-commit       [detail]

Summary: N PASS / N WARN / N FAIL

Recommended actions:
  [List only WARN/FAIL items with a one-line fix]
```

If all 5 checks are PASS, output:
```
hplan-doctor — [DATE]
✅ All checks passed — hplan is correctly installed and active.
```
