---
name: agent-ab-test
description: "Design and analyze A/B tests for AI agents — compare prompt versions, model choices, or architecture variants with statistical rigor. Use when optimizing agent performance, testing new instructions, evaluating model upgrades, or validating TK-based improvements."
argument-hint: "[agent and variants to A/B test]"
allowed-tools: ["Read", "Write"]
context: fork
model: sonnet
---

# Agent A/B Test

> 에이전트 A/B 테스트 설계 및 분석 — 프롬프트, 모델, 아키텍처 변형을 통계적으로 비교

## Core Goal

- **에이전트의 변경 영향을 통계적으로 검증** — 노이즈가 아닌 실제 개선임을 입증하는 설계 제공
- **합리적 비교를 위한 방법론 체계화** — 프롬프트, 모델, 아키텍처 변형별 테스트 전략 수립
- **LLM 특성 반영한 테스트 실행** — 비결정론적 특성과 시간대 편향을 통제한 실험 설계

---

## Trigger Gate

### Use This Skill When

- 프롬프트 버전을 비교하거나 모델 업그레이드 효과를 검증해야 할 때
- 에이전트의 구조적 변경(단일 → 멀티 에이전트) 영향을 정량화해야 할 때
- TK 주입이나 새로운 학습 데이터가 성능에 미치는 영향을 측정해야 할 때
- 성능 개선 가설을 증거 기반으로 검증하고 의사결정해야 할 때

### Route to Other Skills When

- **north-star** → 테스트 결과로 North Star 지표 경향성을 분석하는 경우
- **cohort** → A/B 결과를 장기 코호트 성능으로 추적할 필요가 있을 때
- **burn-rate** → 모델 변경(예: Haiku)이 토큰 비용에 미치는 영향을 분석할 때
- **reliability** → A/B 테스트에서 에러율이나 안정성 차이가 관찰될 때

### Boundary Checks

- **단순 비교와의 구분** — "B가 좋아 보여"는 주관적 판단이 아니라 p-value 기반 유의성 검증이 필수
- **샘플 크기 충분성** — MDE 계산 없이 진행한 테스트는 통계적 신뢰도 부족 가능 → 재설계 권고
- **테스트 오염 여부** — A/B 동시 실행이 아닌 순차 실행은 시간대 편향 발생 가능 → 재실행 필요

---

## 개념

에이전트 A/B 테스트는 웹 A/B 테스트와 다르다. 클릭률이 아닌 "판단의 품질"을 측정해야 하고, LLM의 비결정론적(non-deterministic) 특성 때문에 같은 입력에도 결과가 다를 수 있다. 통계적 유의성 없이 "B가 좋아 보인다"로 판단하면 노이즈에 속는다.

## Instructions

You are designing an **A/B test** for: **$ARGUMENTS**

### Step 1 — Test Hypothesis

```
현재 상태 (Control — A):
  [현재 에이전트 구성]

변형 (Variant — B):
  [변경하려는 요소]

가설:
  "[변경 요소]를 적용하면 [측정 지표]가 [방향]으로 [목표치]만큼 변한다"

변경 유형:
  □ Prompt/Instruction 변경
  □ Model 변경 (예: Sonnet → Haiku)
  □ Architecture 변경 (단일 → 멀티에이전트)
  □ TK Injection (새 TK 추가 전후 비교)
  □ Parameter 변경 (temperature, max_tokens 등)
```

### Step 2 — Metric Selection

| 계층 | 메트릭 | 설명 | 측정 방법 |
|------|--------|------|----------|
| **Primary** | [핵심 지표 1개] | 의사결정 기준 | |
| **Secondary** | [보조 지표 2-3개] | 트레이드오프 확인 | |
| **Guardrail** | [안전 지표] | 악화되면 즉시 중단 | |

에이전트 A/B 테스트 주요 메트릭:
- **Task Accuracy**: 정답률 (human evaluation 기반)
- **Latency**: 응답 시간 (P50, P95, P99)
- **Token Cost**: 태스크당 토큰 비용
- **User Satisfaction**: 유저 평가 (thumbs up/down)
- **Hallucination Rate**: 환각 발생 비율
- **Escalation Rate**: 사람에게 에스컬레이션된 비율

### Step 3 — Sample Size & Duration

```
필요 표본 크기 계산:
  Baseline metric: [현재 값]
  Minimum Detectable Effect (MDE): [최소 감지 차이]
  Significance level (α): 0.05
  Power (1-β): 0.80

  → 필요 표본 수: [N] per variant
  → 예상 기간: [N]일 (일일 트래픽 [N]건 기준)
```

**에이전트 테스트 특이사항:**
- LLM 비결정론 → 같은 입력 5회 반복 실행 권장
- 시간대별 편향 → A/B 동시 실행 (순차 X)
- 프롬프트 캐싱 → 캐시 워밍 후 측정 시작

### Step 4 — Test Execution Plan

```
Traffic Split: [50/50 | 90/10 (canary) | multi-arm bandit]

Execution:
  Day 0: 테스트 환경 세팅, baseline 측정
  Day 1-N: A/B 병렬 실행
  Daily: guardrail 메트릭 모니터링
  Day N+1: 결과 분석

Rollback Trigger:
  - Guardrail 메트릭 [X]% 이상 악화 시 즉시 중단
  - Hallucination rate > [threshold] 시 즉시 중단
```

### Step 5 — Result Analysis

```
Results:
              Control (A)    Variant (B)    Difference
Primary:      [value]        [value]        [+/-N%]
Secondary 1:  [value]        [value]        [+/-N%]
Secondary 2:  [value]        [value]        [+/-N%]
Guardrail:    [value]        [value]        [+/-N%]

Statistical Significance: [p-value]
Confidence Interval: [range]
Practical Significance: [meaningful or noise?]

Decision:
  □ Ship B (모든 지표 개선, 통계적 유의)
  □ Keep A (차이 없거나 guardrail 악화)
  □ Iterate (방향은 맞지만 효과 부족 → B' 설계)
  □ Investigate (예상과 다른 패턴 → 추가 분석 필요)
```

### Output

```
A/B Test Summary: [agent name]
──────────────────────────────
Hypothesis: [one-line]
Variants: A=[description] vs B=[description]
Primary Metric: [metric] — A: [value] vs B: [value]
p-value: [value]
Decision: [Ship B / Keep A / Iterate / Investigate]
Cost Impact: [+/-$N per month]
Next Step: [action]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **표본 부족** | 필요 표본 크기 미달로 p-value > 0.05 | MDE 조정 또는 데이터 수집 기간 연장 후 재분석 |
| **텍스트 오염** | A/B 동시 실행 불가, 순차 실행으로 진행 | 모니터링 기간 동안 시간대 편향 보정 또는 테스트 재설계 |
| **비결정론 효과 과도** | 5회 반복 실행에도 표준편차 > 평균의 30% | 모델 온도 조정, 더 긴 테스트 기간, 또는 방법론 재검토 |
| **Guardrail 악화** | 이미 실행 중 안전 지표가 임계값 초과 | 즉시 테스트 중단, Rollback 실행, 원인 분석 (incident 스킬로 전환) |
| **결과 해석 불일치** | Primary 개선하면서 Secondary 큰 악화 | 트레이드오프 분석 후 Ship/Iterate/Investigate 판단 재검토 |

---

## Quality Gate

- [ ] 가설이 명확한가? (변경 요소 · 측정 지표 · 예상 방향 · 목표치 정의) (Yes/No)
- [ ] 샘플 크기가 충분한가? (MDE 계산 기반 필요 표본 수 확보) (Yes/No)
- [ ] Guardrail 메트릭이 설정되었는가? (품질/성능/비용 하한선 정의) (Yes/No)
- [ ] A/B 동시 실행으로 시간대 편향을 통제했는가? (Yes/No)
- [ ] 결과 분석이 p-value + 신뢰 구간 + 실무 유의성을 모두 검토했는가? (Yes/No)
- [ ] 의사결정 기록(Ship/Keep/Iterate/Investigate)과 근거가 명문화되었는가? (Yes/No)

---

## Examples

### Good Example

```
A/B Test: 에이전트 프롬프트 버전 비교

가설: "More specific instruction set을 추가하면 Task Accuracy가 5% 이상 개선된다"

Control (A):
  Current prompt: [기존 프롬프트]

Variant (B):
  Updated prompt: [구체적 지시사항 추가 버전]

필요 표본: 400건 (Baseline: 92% accuracy, MDE: 5%, α=0.05, β=0.20)
기간: 10일 (일일 40건 트래픽)

결과:
  A: 92.1% accuracy (369/400 정답)
  B: 95.8% accuracy (383/400 정답)
  차이: +3.7%
  p-value: 0.032 (통계적 유의)

결론: "Ship B" — 명확한 개선 + Guardrail 안전
```

### Bad Example

```
"B가 더 나은 것 같다"

❌ 문제점:
- 가설 없이 주관적 인상으로 결정
- 표본 크기 계산 없이 1주일 데이터로 결론
- p-value/신뢰 구간 검토 없음
- "2건 중 1건이 B에서 성공"의 50% 성공률을 90%로 착각
- Guardrail 메트릭 미설정으로 비용 폭증 가능성 미추적

→ 재작업: 가설 수립 → MDE 계산 → 충분 기간 테스트 → 통계 검증
```

---

### 참고
- 설계자: AI PM Skills Contributors, 2026-03
- LLM 비결정론 대응: 5회 반복 실행 + 시간대 동시 실행 패턴
- TK 주입 효과 측정: TK-NNN 프레임워크와 연결

---

## Further Reading
- Ron Kohavi, *Trustworthy Online Controlled Experiments* — A/B test design and analysis
- Anthropic, "Evaluating AI Models" — LLM evaluation best practices and metrics

---

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Test Cases
!`cat references/test-cases.md 2>/dev/null || echo ""`

### Troubleshooting
!`cat references/troubleshooting.md 2>/dev/null || echo ""`

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
