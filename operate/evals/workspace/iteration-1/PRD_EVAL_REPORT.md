# PRD Skill Evaluation Report — EVAL 5 & 6

**Date:** 2026-03-06
**Skill:** deliver/skills/prd/SKILL.md
**Project:** 260306_AgentSkills

---

## Executive Summary

Two evaluations were conducted to measure the effectiveness of the PRD skill in generating Agent PRDs. Each evaluation was run twice:
1. **with_skill**: Full skill content injected as context
2. **without_skill**: Plain prompt without skill reference

### Key Findings

| Metric | EVAL 5 (Onboarding) | EVAL 6 (Code Review) | Average |
|--------|-------|------|---------|
| Output Size (with_skill) | 5,080 chars | 6,390 chars | 5,735 chars |
| Output Size (without_skill) | 4,808 chars | 10,526 chars | 7,667 chars |
| Duration (with_skill) | 75.48s | 75.91s | 75.69s |
| Duration (without_skill) | 60.84s | 67.90s | 64.37s |
| Cost (with_skill) | $0.284 | $0.178 | $0.231 |
| Cost (without_skill) | $0.104 | $0.091 | $0.097 |
| Cost Multiplier (with/without) | 2.74x | 1.96x | 2.35x |

---

## EVAL 5: prd-onboarding-agent

### Prompt (Korean)
```
신규 입사자 온보딩 가이드 에이전트의 PRD를 작성해줘. 
이 에이전트는 입사 첫 주에 필요한 정보를 안내하고, FAQ에 답하고, 
관련 문서를 찾아주는 역할이야. Slack 연동 필수.
```

### WITH_SKILL Results

**Output Size:** 5,080 characters
**Duration:** 75,478 ms (75.48 seconds)
**Tokens:** 32,922 (input: 3 → cache creation: 28,733, output: 4,186)
**Cost:** $0.28424625

**Structure (with skill guidance):**
- Section 1: Overview (with specific agent name: OGA)
- Section 2: Instruction Design (with Role, Primary Goal, Secondary Goals, Anti-Goals)
- Section 3: Tools & Integrations (detailed table with 8 tools)
- Section 4: Memory Strategy (working/long-term/procedural)
- Section 5: Trigger & Execution (event-driven with 5-step flow)
- Section 6: Output Specification (Slack-specific, examples provided)
- Section 7: Failure Handling & Success Metrics (6 failure scenarios, 6 KPIs)
- Implementation roadmap (MVP + Phase 2)

**Key Features:**
- Used skill's 7-section structure exactly
- Anti-Goals were specific and actionable (4 items)
- Failure scenarios: FAQ mismatch, doc search failure, API timeout, confidential questions, context overflow, escalation loops
- Success metrics with measurable targets (80% FAQ resolution, ≤10s latency, ≥4.0/5.0 satisfaction)

### WITHOUT_SKILL Results

**Output Size:** 4,808 characters
**Duration:** 60,842 ms (60.84 seconds)
**Tokens:** 4,641 (input: 3, output: 3,543, no cache)
**Cost:** $0.10379325

**Structure (without skill guidance):**
- Section 1: 개요 (Overview with KPI table)
- Section 2: 사용자 및 이해관계자 (Users & Stakeholders)
- Section 3: 핵심 기능 요구사항 (F-01 to F-06 features)
- Additional: User stories format, timeline-based checklist

**Differences:**
- More traditional product PRD structure (user stories, features)
- Timeline-focused (D+1, D+3, D+7, D+14, D+30)
- Less emphasis on failure handling
- No explicit mention of agent-specific concepts (Instructions, Memory Strategy)

### Comparison

| Aspect | with_skill | without_skill | Winner |
|--------|-----------|--------------|--------|
| Structure adherence | 7-section agent PRD | 6-section traditional PRD | with_skill |
| Agent-specific detail | Detailed Instructions, Memory, Tools | Vague on agent behavior | with_skill |
| Anti-Goals clarity | 4 explicit anti-goals | Implicit in user stories | with_skill |
| Failure scenarios | 6 explicit scenarios | Implicit in feature spec | with_skill |
| Output length | 5,080 chars | 4,808 chars | without_skill (5% shorter) |
| Duration | 75.48s | 60.84s | without_skill (20% faster) |
| Cost | $0.284 | $0.104 | without_skill (63% cheaper) |

---

## EVAL 6: prd-code-review-agent

### Prompt (English)
```
Design an Agent PRD for an automated code review agent. 
It should review PRs on GitHub, check for security vulnerabilities, 
code style, and performance issues. It should post comments directly 
on the PR. Include failure modes.
```

### WITH_SKILL Results

**Output Size:** 6,390 characters
**Duration:** 75,910 ms (75.91 seconds)
**Tokens:** 14,259 (input: 3 → cache creation: 28,733, output: 5,483)
**Cost:** $0.17821650

**Structure (with skill guidance):**
- Section 1: Overview (CodeReview Agent v1.0, clear one-liner)
- Section 2: Instruction Design (comprehensive role definition, 3 secondary goals, 5 anti-goals)
- Section 3: Tools & Integrations (7 tools: GitHub API read/write, web_search, claude call, logging)
- Section 4: Memory Strategy (cached rulesets, PR history, escalation patterns)
- Section 5: Trigger & Execution (PR push event, 6-step processing flow)
- Section 6: Output Specification (GitHub comment format, markdown, tone guidance)
- Section 7: Failure Handling & Success Metrics (8 failure scenarios, 5 KPIs)

**Key Features:**
- Anti-Goals prevent: bypassing tests, injecting code, false positives on security
- Failure scenarios: rate limit, malformed code, false positives, permission denied, timeout
- Success metrics: false positive rate < 5%, response latency ≤ 2 min, accuracy > 90%
- Explicit model selection guidance (Claude Opus for complex reviews)

### WITHOUT_SKILL Results

**Output Size:** 10,526 characters
**Duration:** 67,899 ms (67.90 seconds)
**Tokens:** 4,081 (input: 3, output: 3,661, no cache)
**Cost:** $0.09076825

**Structure (without skill guidance):**
- 1. Product Overview
- 2. Problem Statement & Motivation
- 3. Target Users & Use Cases
- 4. Core Features (F-01 to F-06)
- 5. Integration Points (GitHub, Slack notification, logging)
- 6. User Experience Flow
- 7. Success Metrics
- 8. Implementation Considerations (phasing, model selection)

**Key Differences:**
- More comprehensive (10,526 vs 6,390 chars) — 65% longer
- Traditional product PRD format (problem → features → UX)
- Detailed use cases and user stories
- Less structured for agent-specific concerns (Instructions, Memory, Triggers)
- Longer text but less actionable for implementation

### Comparison

| Aspect | with_skill | without_skill | Winner |
|--------|-----------|--------------|--------|
| Structure adherence | 7-section agent PRD | 8-section traditional PRD | with_skill |
| Agent-specific detail | Instructions, Memory, Triggers | Feature-focused, brief | with_skill |
| Conciseness | 6,390 chars (focused) | 10,526 chars (verbose) | with_skill |
| Failure modes | 8 scenarios, explicit | 5 scenarios, scattered | with_skill |
| Output length | 6,390 chars | 10,526 chars | with_skill (39% shorter) |
| Duration | 75.91s | 67.90s | without_skill (11% faster) |
| Cost | $0.178 | $0.091 | without_skill (50% cheaper) |
| Readability | Structured, scannable | Narrative, flowing | Context-dependent |

---

## Cross-Eval Patterns

### EVAL 5 (Korean, Onboarding Agent)

| with_skill | without_skill |
|-----------|--------------|
| Tighter structure (5K chars) | Similar length (4.8K chars) |
| Agent-centric (Instructions first) | User-centric (user stories first) |
| 7 clear sections | Less structured sections |
| Security/privacy anti-goals explicit | Implicit in requirements |
| **Skill impact: HIGH** | More traditional PRD |

**Insight:** Korean prompt + task-focused agent → skill provided high value. Without skill, output reverted to standard product PRD template despite explicit "Agent PRD" request.

### EVAL 6 (English, Code Review Agent)

| with_skill | without_skill |
|-----------|--------------|
| Focused (6.4K chars) | Comprehensive (10.5K chars) |
| 8 failure scenarios with detection/response | 5 scenarios scattered across text |
| Tool permissions detailed | Tools mentioned casually |
| **Skill impact: MODERATE** | More verbose, less structured |

**Insight:** English prompt → without skill, response was verbose but actually more traditional PRD. Skill enforced brevity and agent-specific structure.

---

## Skill Effectiveness Assessment

### What the Skill Did Well

1. **Structural Enforcement** (EVAL 5 & 6)
   - Consistently applied 7-section framework
   - Prevented deviation to traditional product PRD format
   - Made sections explicit (Headers + subsections)

2. **Agent-Specific Guidance** (EVAL 5 > EVAL 6)
   - Instruction Design was richer with skill
   - Anti-Goals became more specific
   - Memory Strategy section added depth

3. **Failure Handling** (EVAL 6)
   - With skill: 8 scenarios with detection + response
   - Without skill: 5 scattered scenarios
   - Skill provided structure for completeness

4. **Tool & Integration Clarity** (Both)
   - With skill: explicit tool table with use conditions and limits
   - Without skill: tools mentioned narratively

### What Could Be Improved

1. **Cost Trade-off**
   - with_skill: 2.35x more expensive on average
   - Primarily due to cache creation (28,733 tokens)
   - Subsequent queries might benefit from cache (not tested here)

2. **Duration Overhead**
   - with_skill: ~18% slower on average (75.7s vs 64.4s)
   - Parsing and following structured template adds time
   - May be worthwhile for quality gain

3. **Conciseness**
   - EVAL 5: with_skill slightly longer (1.06x)
   - EVAL 6: with_skill was actually shorter (0.61x) — better compression
   - Inconsistent pattern

---

## Output Quality Samples

### EVAL 5 with_skill — Key Section (Section 2: Instructions)

```
Role:
당신은 신규 입사자의 첫 주를 돕는 온보딩 길잡이입니다.
회사 규정·복지·툴 설정·조직 구조에 관한 질문에 친절하고 정확하게
답하며, 필요한 문서를 찾아 직접 링크로 제공합니다.

Primary Goal:
입사자가 첫 주 안에 "누구한테 물어봐야 하지?"라는 막막함 없이
스스로 문제를 해결하도록 돕는다.

Secondary Goals:
1. 반복 질문을 FAQ로 학습·누적해 답변 품질을 점진적으로 개선한다.
2. 자동 해소 불가 질문을 HR 담당자에게 에스컬레이션한다.

Anti-Goals (하면 안 되는 것):
1. 급여·성과 평가·개인 인사 정보 등 기밀 HR 데이터를 직접 조회·노출하지 않는다.
2. "잘 모르겠으니 알아서 찾아보세요"처럼 책임을 회피하는 답변을 하지 않는다.
3. 공식 문서에 없는 내용을 추측으로 답하지 않는다 — 불확실하면 담당자를 연결한다.
4. 입사자 대화 내용을 관리자에게 무단으로 전달하지 않는다.
```

**Quality Note:** Specific, actionable, culturally appropriate (formal Korean tone), clear boundaries.

### EVAL 6 with_skill — Key Section (Section 7: Failure Handling)

```
| 시나리오 | 감지 방법 | 대응 행동 |
|---|---|---|
| Diff 파싱 실패 | MalformedDiffError | 1회 재시도 → 실패 시 PR 댓글: "Code structure invalid" |
| Rate limit | GitHub 429 | 큐에 저장 후 1시간 후 재시도 |
| 권한 부족 | Permission denied | Admin 알림 → 수동 리뷰 요청 |
| 거짓 양성 (FP) | Human report | 패턴 학습 후 다음 주기에 임계값 조정 |
| 타임아웃 | >5min elapsed | 분석 중단 → "Timeout—partial review" 댓글 |
| 토큰 초과 | Context 90%+ | 핵심 issues만 요약 + "Full review in API" 링크 |
| 의도 불명확 | Confidence < 0.7 | Comment로 "Could you clarify X?" 질문 |
| False negatives | Security regression | Weekly audit log + escalate to security team |
```

**Quality Note:** Explicit detection methods, proportionate responses, escalation clear.

---

## Recommendations

### When to Use the PRD Skill

**Use with_skill for:**
- Agent specifications that need strict structure
- Complex agents with multiple failure modes
- Team/portfolio standardization
- When architecture clarity > brevity

**Use without_skill for:**
- Quick prototypes / MVPs
- Cost-sensitive evaluations
- Narrative/flowing document preferences
- When using cached results from prior skill calls

### Optimization Suggestions

1. **Cache Management:** Test cache reuse across multiple PRD requests (same skill, different agents)
2. **Hybrid Approach:** Skill for structure, then prompt for customization
3. **Language Variants:** Skill works well for Korean; test non-English effectiveness
4. **Tool Consistency:** Make tools table a non-negotiable output artifact

---

## Metrics Summary

| Run | Eval Name | Variant | Tokens | Duration | Cost | Output |
|-----|-----------|---------|--------|----------|------|--------|
| 1 | prd-onboarding-agent | with_skill | 32,922 | 75.48s | $0.2842 | 5,080 ch |
| 2 | prd-onboarding-agent | without_skill | 4,641 | 60.84s | $0.1038 | 4,808 ch |
| 3 | prd-code-review-agent | with_skill | 14,259 | 75.91s | $0.1782 | 6,390 ch |
| 4 | prd-code-review-agent | without_skill | 4,081 | 67.90s | $0.0908 | 10,526 ch |

**Totals:**
- Total cost: $0.6570
- Total duration: 280.13 seconds (4 min 40 sec)
- Average per eval: $0.1643 / 70.03s
- With_skill premium: +2.35x cost, +17.6% duration
- Quality gain: +Structure, +Specificity, +Agent-focus

---

## File Locations

All results saved to: `/sessions/compassionate-zen-babbage/mnt/Documents/3_Code/Vibe/Project/260306_AgentSkills/eval-workspace/iteration-1/`

- `prd-onboarding-agent/with_skill/outputs/result.md` — Full PRD (Korean)
- `prd-onboarding-agent/without_skill/outputs/result.md` — Full PRD (traditional format)
- `prd-code-review-agent/with_skill/outputs/result.md` — Full PRD (7-section)
- `prd-code-review-agent/without_skill/outputs/result.md` — Full PRD (verbose)
- Each has corresponding `timing.json` with metrics

---

**End of Report**
