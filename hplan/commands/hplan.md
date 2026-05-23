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

### Step 0 — Signal Gate (4-document check)

Verify that all four Signal Gate documents exist before proceeding. If any are missing, stop immediately.

```bash
for f in harness/pain.md harness/cogs.md harness/market.md harness/competitors.md; do
  [ -f "$f" ] && echo "✅ $f" || echo "❌ $f MISSING"
done
```

**If any document is missing — output verdict and stop:**

```
VERDICT: HOLD
Reason:  Signal Gate: [list each missing document]
Next:    Create the missing document(s):
         - pain.md     : 누가, 어떤 상황에서, 뭘 못하는가
         - cogs.md     : p50/p90 단위 경제성 시뮬레이션
         - market.md   : 시장 규모 + 진입 시점 근거
         - competitors.md : 직접 경쟁사 2개 + 대체재 1개
Gate:    SIGNAL
```

Stop. Do not proceed to Step 1.

**Evidence Source 요건 (v0.9.7)**

각 Signal Gate 문서에 아래 섹션 키워드 중 하나 이상이 포함되어야 한다:

| 문서 | 최소 요건 |
|---|---|
| pain.md | 인터뷰 날짜(`YYYY-MM-DD`) 또는 `## Evidence` 섹션 |
| cogs.md | 가격 출처(`provider pricing`, `API 가격`) 또는 `## Evidence` 섹션 |
| market.md | 시장 규모 출처(`산업 리포트`, `TAM source`) 또는 `## Evidence` 섹션 |
| competitors.md | 직접 테스트 또는 사용자 발화 인용 |

4개 문서 모두 미충족 → gate_guard.py 차단. 일부 미충족 → 경고 출력.

**If all four documents are present:** Read them and extract key signals (pain summary, cogs verdict, market size, competitive gaps) as context for Steps 2–3.

(Optional) Also check for a richer context file:
```bash
ls harness/context-intake.md 2>/dev/null && echo "FOUND" || echo "MISSING"
```
If FOUND, read it and extract `interview_notes` as supplementary input for Step 2 scoring.

Also check for competitor blockers:
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

> **Evidence Source 요건 (Signal Gate v2)**
> 각 문서의 주장에는 출처가 있어야 합니다. 출처 없는 문서는 점수에서 자동 차감됩니다(-5점/문서).
>
> | 문서 | 요구 출처 |
> |------|---------|
> | `harness/pain.md` | 인터뷰 날짜 + 인터뷰이 역할 |
> | `harness/cogs.md` | 실제 가격 페이지 URL 또는 견적서 날짜 |
> | `harness/market.md` | 보고서명 + 발행 연도 + 인용 페이지 |
> | `harness/competitors.md` | 직접 테스트 날짜 또는 사용자 인용 출처 |
>
> 각 문서에 `## Evidence Source` 섹션을 작성하세요.

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
- **75–100** + economic pain signal → `build` — proceed to Step 3
- **55–74** → `interview` — flag weakest criteria, gather more evidence before Step 3
- **35–54** → `pivot` — problem definition is weak; reframe before proceeding
- **< 35** → `hold` — HOLD — insufficient evidence. Output verdict now:

  ```
  VERDICT: HOLD
  Reason:  Evidence score [X]/100 — below 35 threshold. Weakest: [criterion]
  Next:    Run /harness-build --step evidence for a full rubric + interview synthesis
  Gate:    EVIDENCE
  ```

  Stop.

**Anti-gaming note:** The `build` verdict requires an economic pain signal (돈·매출·비용·리스크·기회 언급). A high score without economic pain defaults to `interview`. The underlying script (`generate_report.py`) enforces this mechanically. Interviews are encouraged but not gated.

**Next 3 actions per verdict:**
- `build` → run `/harness-build --step product` · confirm COGS via `/harness-build --step cogs` · log decision via `decision-log` skill
- `interview` → identify the weakest axis above · draft 3 targeted interview questions · re-run `/harness-build --step evidence` after 3+ new interviews
- `pivot` → revisit ICP and problem statement · reframe around a more economically painful problem · re-run `/harness-build --step evidence`
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
  Next:    Run /harness-build --step cogs with adjusted --arpu or --tokens-in to find GREEN scenario
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

**GO** — All 3 gates pass. Suggest `/harness-build --step product` to begin full product brief.

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
- `/harness-build --step evidence` — full 100-point rubric with interview synthesis ingestion
- `/harness-build --step cogs` — detailed COGS with custom provider pricing inputs
- `/harness-build --step product` — full product brief (requires GO verdict first)
- `/harness-handoff` — export to Spec-Kit / Kiro / Claude Code after GO

All decisions are logged to `harness/build-gate/decision_log.jsonl` automatically when the underlying scripts run.
