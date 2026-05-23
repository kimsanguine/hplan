---
description: "Export the Build Gate brief to your downstream coding ecosystem — Spec-Kit, Kiro, GStack, Claude Code, or all four at once. Use when Build Gate is approved and you need to export the brief to a downstream coding ecosystem (Spec-Kit, Kiro, GStack, Claude Code)."
argument-hint: "[brief.json] [--target spec-kit|kiro|gstack|claude|all]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /harness-handoff


## Instructions

You run the **hplan multi-target handoff** for: **$ARGUMENTS**

### Step 1 — Verify Build Gate
Confirm `harness/decisions.jsonl` has a recent `decision: "build"` (or `CONDITIONAL_GO`) for this project AND `harness/build-gate/checkpoint.json` has `status: "approved"`.

### Step 2 — Locate the brief JSON
The brief must include at minimum: product_name, problem, icp, jtbd, cogs_ceiling, decision. Other fields fill gaps in generated artifacts.

### Step 3 — Execute
`python3 hplan/scripts/export_handoff.py <brief.json> --target <spec-kit|kiro|gstack|claude|all> --root .`

### Step 4 — Place outputs
Help the user move generated files from `harness/exports/<target>/` to their actual project location (spec-kit `specs/` at repo root, kiro `.kiro/` at repo root, gstack /office-hours direct paste, claude AGENTS.md+CLAUDE.md at repo root).

## Output Format

Return:

1. **Targets exported** — list of files written per ecosystem
2. **NNN prefix used** — for spec-kit auto-increment
3. **Next manual step** — where to copy the generated files to make the downstream agent see them
