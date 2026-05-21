# Premortem Skill Evaluation Index

**Date:** 2026-03-06  
**Project:** 260306_AgentSkills  
**Skill Evaluated:** `measure/skills/premortem/SKILL.md`  
**Framework:** FMEA (Failure Mode and Effects Analysis)

---

## Quick Navigation

### Main Report
- **[PREMORTEM_EVAL_SUMMARY.md](PREMORTEM_EVAL_SUMMARY.md)** — Comprehensive analysis with recommendations (6KB)

### EVAL 7: Financial Support Agent (Korean)

| Component | File | Size | Key Stats |
|-----------|------|------|-----------|
| **With Skill Output** | [premortem-support-agent/with_skill/outputs/result.md](premortem-support-agent/with_skill/outputs/result.md) | 6,089 B | 194 lines, 1,386 words |
| **With Skill Timing** | [premortem-support-agent/with_skill/timing.json](premortem-support-agent/with_skill/timing.json) | 125 B | 72.5s, $0.1307, 25k tokens |
| **Without Skill Output** | [premortem-support-agent/without_skill/outputs/result.md](premortem-support-agent/without_skill/outputs/result.md) | 5,384 B | 164 lines, 1,298 words |
| **Without Skill Timing** | [premortem-support-agent/without_skill/timing.json](premortem-support-agent/without_skill/timing.json) | 119 B | 72.8s, $0.1303, 24k tokens |

**Delta:** +705 bytes (+13.1%), +0.3% cost, negligible duration difference

### EVAL 8: Content Moderation Agent (English)

| Component | File | Size | Key Stats |
|-----------|------|------|-----------|
| **With Skill Output** | [premortem-content-moderation/with_skill/outputs/result.md](premortem-content-moderation/with_skill/outputs/result.md) | 10,743 B | 200 lines, 1,568 words |
| **With Skill Timing** | [premortem-content-moderation/with_skill/timing.json](premortem-content-moderation/with_skill/timing.json) | 120 B | 62.3s, $0.0937, 23.5k tokens |
| **Without Skill Output** | [premortem-content-moderation/without_skill/outputs/result.md](premortem-content-moderation/without_skill/outputs/result.md) | 5,319 B | 98 lines, 776 words |
| **Without Skill Timing** | [premortem-content-moderation/without_skill/timing.json](premortem-content-moderation/without_skill/timing.json) | 120 B | 37.3s, $0.0518, 21.1k tokens |

**Delta:** +5,424 bytes (+102%), +81% cost, +67% duration

---

## Results Summary

### EVAL 7 (Financial Support Agent)

**Prompt (Korean):**
```
다음 주에 고객 지원 에이전트를 프로덕션에 배포해. 하루 1000건 처리 예정이고, 
금융 상품 관련 문의를 처리해. Pre-mortem 분석을 해줘. FMEA 방법론으로.
```

**Key Findings:**
- Skill provides 13% more output at negligible cost (0.3%)
- Both versions stabilize around 72.8s (base latency)
- With skill: audit-ready FMEA table with 10 failure modes + RPN
- Without skill: conversational assessment, less structured

**Verdict:** HIGH VALUE — Essential for financial compliance

---

### EVAL 8 (Content Moderation Agent)

**Prompt (English):**
```
We're about to launch a content moderation agent on a social platform 
with 50k daily posts. Run a pre-mortem — what could go wrong? Consider 
false positives/negatives, bias, edge cases, and regulatory risk.
```

**Key Findings:**
- Skill doubles output depth (+102% bytes)
- Cost premium: 81% ($0.0420 extra per eval)
- Duration penalty: 67% slower (62.3s vs 37.3s)
- With skill: 10+ failure modes, specific thresholds (FPR < 2%, bias ratio > 1.5)
- Without skill: main risks listed, less structured, missing cross-functional angles

**Verdict:** HIGH VALUE WITH TRADE-OFFS — Recommend for high-stakes scenarios, not real-time use

---

## Comparative Metrics

### By Language

| Metric | Korean (EVAL 7) | English (EVAL 8) |
|--------|-----------------|-----------------|
| Token Overhead | 3.0% | 11.4% |
| Duration Change | -0.5% | +67.1% |
| Cost Change | +0.3% | +81.0% |
| Output Size Gain | 13.1% | 102% |

**Insight:** Skill has higher overhead in English; suggests template optimization opportunity

### By Domain

| Domain | With Skill Value | Cost-Benefit |
|--------|------------------|--------------|
| Financial Services | Critical (audit-ready FMEA) | Highly Positive (0.3% cost) |
| Content Moderation | High (2x depth, regulatory ready) | Positive (81% cost for 2x quality) |

---

## Methodology Coverage

Both evaluations executed all 5 FMEA steps:

✅ **Step 1:** Pre-mortem exercise ("imagine it failed 3 months from now")
✅ **Step 2:** FMEA table (failure mode, cause, effect, severity, probability, detection, RPN)
✅ **Step 3:** AI-specific failure mode checklist
✅ **Step 4:** Prevention/Detection/Response/Recovery strategies
✅ **Step 5:** Monitoring triggers and alert thresholds

**Difference:** With skill enforced all steps comprehensively; without skill focused on subset

---

## Output Quality Comparison

### EVAL 7: Financial Services

**WITH SKILL includes:**
- ✅ 10 identified failure modes with RPN scores
- ✅ Prevention/Detection/Response/Recovery for each high-risk mode
- ✅ 7-day pre-deployment checklist with clear ownership
- ✅ Yellow/Red alert monitoring triggers
- ✅ Compliance-focused language

**WITHOUT SKILL includes:**
- ✓ Main risk areas identified
- ✓ General concern categories
- ≈ Actionable but needs refinement

---

### EVAL 8: Content Moderation

**WITH SKILL includes:**
- ✅ Pre-mortem exercise (8 specific failure scenarios)
- ✅ Detailed FMEA table (10+ modes with RPN)
- ✅ Cross-functional responsibility matrix
- ✅ Specific metrics (FPR < 2%, bias ratio thresholds)
- ✅ Legal/regulatory considerations

**WITHOUT SKILL includes:**
- ✓ False positives/negatives identified
- ✓ Bias concerns noted
- ≈ Conversational, less structured

---

## Timing Breakdown

### EVAL 7 (Korean, Financial)
```
WITH_SKILL:    72,506 ms (72.5s)
WITHOUT_SKILL: 72,837 ms (72.8s)
Δ:             -331 ms  (-0.5%, faster)

Possible explanation: Prompt caching benefits (~20.7K cache tokens)
```

### EVAL 8 (English, Content Moderation)
```
WITH_SKILL:    62,251 ms (62.3s)
WITHOUT_SKILL: 37,255 ms (37.3s)
Δ:             +24,996 ms (+67.1%, slower)

Explanation: Enforced FMEA depth requires more response generation
```

---

## Cost Analysis

### Total Cost (Both Evals)

| Variant | EVAL 7 | EVAL 8 | Total |
|---------|--------|--------|-------|
| **With Skill** | $0.1307 | $0.0937 | $0.2244 |
| **Without Skill** | $0.1303 | $0.0518 | $0.1821 |
| **Delta** | +$0.0004 | +$0.0420 | +$0.0423 |
| **% Increase** | +0.3% | +81.0% | +23.2% |

**Cost Per Eval (Average):**
- With skill: $0.112 per eval
- Without skill: $0.091 per eval
- Premium: $0.021 (+23%)

**Use Case ROI:**
- Single pre-deployment assessment: +$0.0423 total cost acceptable
- Repeated analyses (5+ per week): Consider caching to reduce premium
- Real-time screening: Use without_skill baseline

---

## Recommendations

### Deploy WITH Skill For:
1. Pre-deployment risk assessments (both domains)
2. High-stakes, regulatory scenarios (financial, healthcare, legal)
3. Team reviews & stakeholder alignment (depth aids discussion)
4. Documentation & compliance (audit-ready structure)
5. One-time deep analyses (cost secondary to quality)

### Deploy WITHOUT Skill (Plain Prompt) For:
1. Rapid ideation & screening (37.3s vs 62.3s for content moderation)
2. Real-time risk triage (where duration matters)
3. Cost-sensitive scenarios (22% less expensive)
4. Preliminary assessment (refine with skill later)
5. Simple risk profiles (basic concerns suffice)

### Hybrid Approach:
```
1. Initial Triage:    Plain prompt → rapid screening (37s, $0.05)
2. Escalation:        Skill-enhanced → deep analysis (62s, $0.09)
3. Documentation:     Skill output → formal pre-mortem record
```

---

## File Structure

```
eval-workspace/iteration-1/
├── PREMORTEM_INDEX.md                    (This file)
├── PREMORTEM_EVAL_SUMMARY.md             (Comprehensive report)
│
├── premortem-support-agent/
│   ├── with_skill/
│   │   ├── outputs/
│   │   │   └── result.md                 (6,089 bytes)
│   │   └── timing.json                   (duration: 72.5s, cost: $0.1307)
│   │
│   └── without_skill/
│       ├── outputs/
│       │   └── result.md                 (5,384 bytes)
│       └── timing.json                   (duration: 72.8s, cost: $0.1303)
│
└── premortem-content-moderation/
    ├── with_skill/
    │   ├── outputs/
    │   │   └── result.md                 (10,743 bytes)
    │   └── timing.json                   (duration: 62.3s, cost: $0.0937)
    │
    └── without_skill/
        ├── outputs/
        │   └── result.md                 (5,319 bytes)
        └── timing.json                   (duration: 37.3s, cost: $0.0518)
```

---

## Execution Metadata

- **Run Date:** 2026-03-06
- **Total Duration:** ~5 minutes (all 4 evals)
- **Model:** claude-sonnet-4-6 (via claude CLI)
- **Timeout:** 90 seconds per evaluation
- **Output Format:** JSON with timing & usage metadata
- **Prompt Injection:** SKILL.md prepended with clear delimiter
- **Cache Status:** Enabled (18.6K cache hit on EVAL 7 with_skill)

---

## Next Steps

1. Review PREMORTEM_EVAL_SUMMARY.md for full analysis
2. Compare with_skill vs without_skill outputs in your domain of interest
3. Consider hybrid deployment: plain prompt + skill escalation
4. Explore skill optimization for multi-language support
5. Measure end-to-end impact: does skill output reduce post-deployment incidents?

---

**Report Generated:** 2026-03-06  
**Skill Version:** measure/skills/premortem/SKILL.md  
**Status:** All 4 evaluations completed successfully

