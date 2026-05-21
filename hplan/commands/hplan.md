---
description: "Run the full hplan build gate in one command — exclusions collision check + evidence rubric + COGS analysis — and return a single GO / HOLD / INVESTIGATE verdict with 3-line reason. Use when a PM or founder has a new product idea and wants the fastest WHETHER answer before committing any further time."
argument-hint: "[idea description]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /hplan — Build Gate Orchestrator

Single entry point for the hplan WHETHER gate. Chains all three checks and returns a final verdict. No prior gate knowledge required.

## Instructions

You are running the **hplan Build Gate** for: **$ARGUMENTS**

Execute these steps in sequence. Stop early if a gate fails — do not run downstream gates on a HOLD.

### Step 0 — Context Intake Check (optional but recommended)

Before running gates, check if a context intake file exists:

```bash
ls harness/context-intake.md 2>/dev/null && echo "FOUND" || echo "MISSING"
```

- **FOUND**: Read `harness/context-intake.md`. Then run the Context Quality Score:
  ```bash
  python3 hplan/scripts/context_quality_scorer.py harness/context-intake.md
  ```
  - CQS < 30: Stop. Output "Context insufficient (CQS X/100). Complete context-intake.md before running the gate."
  - CQS 30–54: Proceed with ⚠️ LOW confidence badge noted in final output.
  - CQS 55–74: Proceed with ⚠️ MODERATE confidence badge.
  - CQS ≥ 75: Proceed normally. Extract `idea`, `icp_segment`, `recent_event`, `workaround_tool`, `monthly_cost_estimate`, `alternatives`, `interview_notes`, `interview_count` as inputs for Step 2.
- **MISSING**: Proceed with argument only. Note in output: "No context-intake.md — evidence rubric relies on description alone (lower reliability). See `hplan/references/context-intake.md` to create one."

Also check for competitor context:
```bash
ls harness/competitor-context.md 2>/dev/null && echo "FOUND" || echo "MISSING"
```
If FOUND, read it and extract `blockers` fields. Any `blocker == true` → immediate HOLD before Step 1.

---

---

### Step 1 — Exclusions Collision Check

```bash
python3 hplan/scripts/exclusions_registry.py check "$ARGUMENTS"
```

**If COLLISION detected:**
- Show the matched exclusion entry: date, reason, `reopen_trigger`
- Check whether the `reopen_trigger` condition is met given the current idea
- If **NOT met** → output final verdict immediately:

  ```
  VERDICT: HOLD
  Reason:  Prior exclusion applies — [matched entry reason]
  Trigger: [reopen_trigger text] — not met
  Gate:    EXCLUSIONS
  ```

  Stop. Do not proceed to Step 2.

- If **met** → note "reopen_trigger MET — continuing to evidence check"

---

### Step 2 — Evidence Rubric Score

Score the idea against the 8-criterion rubric. Use only information available in the user's message; do not assume details not provided.

| Criterion | Max pts | Score | Notes |
|-----------|---------|-------|-------|
| ICP specificity (named segment with behavior, not "SMBs") | 20 | | |
| Recent painful event (within 3 months, user-reported) | 15 | | |
| Current alternative/workaround (users already doing something manual) | 15 | | |
| Repetition/frequency (same complaint heard 3+ times) | 10 | | |
| Economic pain (time × frequency × cost, money/risk/opportunity loss) | 15 | | |
| Switching trigger (reason to abandon current workaround) | 10 | | |
| MVP narrowness (one workflow, not a platform; ≤3 features) | 10 | | |
| Acquisition path to first 5 users (specific channel, not "go viral") | 5 | | |

**Score interpretation:**
- **75–100** + 2+ interview lines + economic pain signal → `build` — proceed to Step 3
- **55–74** → `interview` — flag weakest criteria, gather more evidence before Step 3
- **35–54** → `pivot` — problem definition is weak; reframe before proceeding
- **< 35** → `hold` — HOLD — insufficient evidence. Output verdict now:

  ```
  VERDICT: HOLD
  Reason:  Evidence score [X]/100 — below 35 threshold. Weakest: [criterion]
  Next:    Run /hplan-evidence for a full rubric + interview synthesis
  Gate:    EVIDENCE
  ```

  Stop.

**Anti-gaming note:** The `build` verdict requires interview_lines ≥ 2 AND an economic pain signal. A high score alone is not enough — the underlying script (`generate_report.py`) enforces this mechanically.

**Next 3 actions per verdict:**
- `build` → run `/hplan-product` · confirm COGS via `/hplan-cogs` · log decision via `decision-log` skill
- `interview` → identify the weakest axis above · draft 3 targeted interview questions · re-run `/hplan-evidence` after 3+ new interviews
- `pivot` → revisit ICP and problem statement · reframe around a more economically painful problem · re-run `/hplan-evidence`
- `hold` → log via `decision-log` skill · add to `exclusions` registry with `reopen_trigger` · stop

---

### Step 3 — COGS Gate

Run the COGS sentinel only if a pricing signal is available in the idea description (e.g., target price, provider model, usage pattern). If no pricing signal exists, note "COGS: no pricing input — skipping" and proceed to Step 4 with a CONDITIONAL note.

```bash
python3 hplan/scripts/cogs_sentinel.py
```

Interpret result:
- **GREEN** (p50 ≥ 60%, p90 ≥ 40%): Economics confirmed
- **CONDITIONAL_GO** (p50 ≥ 40%, p90 ≥ 20%): Flag pricing risk, continue
- **RED**: HOLD — COGS unworkable at current pricing. Output verdict:

  ```
  VERDICT: HOLD
  Reason:  COGS RED — p90 margin below threshold at current pricing
  Next:    Run /hplan-cogs with adjusted --arpu or --tokens-in to find GREEN scenario
  Gate:    COGS
  ```

  Stop.

---

### Step 4 — Final Verdict

Output a 4-line verdict block:

```
VERDICT: GO / HOLD / INVESTIGATE

Reason:  [1-line summary of the deciding factor]
Next:    [Concrete next action]
Gate:    [Which gate was decisive: EXCLUSIONS / EVIDENCE / COGS / ALL-PASS]
```

**GO** — All 3 gates pass. Suggest `/hplan-product` to begin full product brief.

**HOLD** — Any gate fails (already output in Steps 1–3).

**INVESTIGATE** — CONDITIONAL_GO on COGS, or evidence score 60–79, or COGS skipped due to no pricing signal. Suggest the specific gate command to run next.

---

## Output Format

```
VERDICT: GO / HOLD / INVESTIGATE

Reason:  [1-line summary of the deciding factor]
Next:    [Concrete next action]
Gate:    [Which gate was decisive: EXCLUSIONS / EVIDENCE / COGS / ALL-PASS]
```

## Notes

This command is the fastest WHETHER answer. For deeper analysis, follow with:
- `/hplan-evidence` — full 100-point rubric with interview synthesis ingestion
- `/hplan-cogs` — detailed COGS with custom provider pricing inputs
- `/hplan-product` — full product brief (requires GO verdict first)
- `/hplan-handoff` — export to Spec-Kit / Kiro / Claude Code after GO

All decisions are logged to `harness/build-gate/decision_log.jsonl` automatically when the underlying scripts run.
