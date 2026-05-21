---
description: "Run the hplan Evidence Gate end-to-end — score idea against 100-point rubric, ingest interview synthesis, check exclusions registry. Use when a PM or founder pitches an idea and you need to check whether evidence is strong enough before PRD work."
argument-hint: "[idea description or path to JSON]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /hplan-evidence


## Instructions

You are running the **hplan Evidence Gate** for: **$ARGUMENTS**

Execute these steps in sequence:

### Step 1 — Exclusion collision check
Invoke `exclusions` skill — `python3 hplan/scripts/exclusions_registry.py check "<idea>"`. If COLLISION + reopen_trigger unmet, STOP and report.

### Step 2 — Structure the input
Collect from the user message: `idea`, `target` (ICP behavior), `hypothesis`, `alternatives` (list), `features` (≤3), `interview_notes` (one per line).

### Step 3 — 100-point rubric
Invoke `evidence-rubric` skill — runs `scripts/generate_report.py`. Capture score + missing axes.

### Step 4 — Interview synthesis
If `interview_notes` is thin or `decision == "interview"`, invoke `interview-synthesis` skill to either ingest AI export OR plan fresh interviews. Audit the 5/3 strong-Push rule.

### Step 5 — Decide

The underlying script (`generate_report.py`) determines the decision mechanically:

| Score | Extra conditions | Decision | Meaning |
|-------|-----------------|----------|---------|
| ≥ 75 | interview_lines ≥ 2 AND economic pain present | `build` | Proceed to product gate |
| ≥ 75 | interview_lines < 2 OR no economic pain | `interview` | Score is strong but evidence is thin |
| 55–74 | — | `interview` | More interviews needed |
| 35–54 | — | `pivot` | Problem definition is weak |
| < 35 | — | `hold` | Stop — insufficient evidence |

**Anti-gaming:** `build` requires at least 2 independent interview lines AND an economic pain keyword. A fabricated or AI-synthesized interview without real human quotes will fail the `interview_lines` threshold.

**Next 3 actions per decision:**
- `build` → proceed to `/hplan-product` · verify COGS gate with `/hplan-cogs` · log approval via `decision-log` skill
- `interview` → identify lowest-scoring axis from rubric breakdown · draft 3 targeted interview questions targeting that axis · re-run after 3+ new human interviews
- `pivot` → revisit ICP — is the pain specific, recent, and economic? · reframe the problem statement · re-run `/hplan-evidence`
- `hold` → log with `decision-log` skill · add to exclusions registry with `reopen_trigger` defining what evidence would change this · stop all downstream work

## Output Format

Return:

1. **Exclusion verdict** — CLEAR or COLLISION (with prior id + reopen_trigger)
2. **Rubric score** — N/100 with breakdown of weak axes
3. **Interview audit** — interviews tagged, distinct strong-Push persons
4. **Decision** — `build` / `interview` / `pivot` / `hold` / `CONDITIONAL_GO`
5. **Next gate** — `/hplan-product`, more interviews, or stop
