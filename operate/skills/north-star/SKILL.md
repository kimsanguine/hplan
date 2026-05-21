---
name: north-star
description: "Define the single North Star metric for an AI agent that aligns operational performance with business value. Use when launching a new agent product, realigning team focus, setting up metric hierarchies, or when multiple KPIs are creating conflicting priorities."
argument-hint: "[agent or product]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# Agent North Star

> 에이전트의 단일 핵심 지표(North Star Metric) 정의

## Core Goal

- **팀 전체가 공유할 수 있는 단일 성공 지표 정의** — 품질과 임팩트를 동시에 반영하는 "하나의 숫자"로 전략 정렬
- **운영 건강도와 비즈니스 가치를 균형 있게 반영** — 정확도만 높거나, 비용만 낮은 편향 방지
- **의사결정 우선순위 명확화** — 충돌하는 KPI 간 트레이드오프를 North Star 기준으로 일관성 있게 해결

---

## Trigger Gate

### Use This Skill When

- 새로운 에이전트 제품을 론칭하고 팀 방향성을 정렬할 때
- 기존 여러 KPI가 상충할 때 (비용 vs 품질, 속도 vs 정확도)
- 분기 OKR과 에이전트 목표를 연결해야 할 때
- 에이전트 전략의 중심을 재정의해야 할 때

### Route to Other Skills When

- **kpi** → North Star를 KPI 대시보드의 최상위로 배치
- **burn-rate** → North Star에 비용 효율 요소가 포함되면 (비용 최적화 추진)
- **cohort** → North Star 추이를 코호트별로 추적하는 경우
- **agent-ab-test** → A/B 테스트의 Primary 메트릭으로 North Star 사용

### Boundary Checks

- **지표 선택의 주관성** — "좋은 지표"가 아니라 5가지 기준(Actionable, Measurable 등) 충족 여부 점검
- **분해 가능성** — North Star가 팀의 직접 통제 범위에 있는가? (통제 불가능 → 재정의 필요)
- **Anti-metric 설정** — North Star 최적화로 인한 다른 지표 악화를 사전에 차단

---

## 개념

North Star Metric은 에이전트의 성공을 하나의 숫자로 표현한다. 운영 건강도와 비즈니스 임팩트를 동시에 반영하는 복합 지표여야 하며, 팀 전체가 이 하나의 숫자를 중심으로 의사결정한다.

## Instructions

You are defining a **North Star Metric** for: **$ARGUMENTS**

### Step 1 — North Star Criteria

A good North Star Metric must be:
- [ ] **Actionable**: Team can influence it directly
- [ ] **Measurable**: Can be tracked automatically
- [ ] **Understandable**: Anyone can explain what it means
- [ ] **Leading**: Predicts future success, not just past
- [ ] **Composite**: Reflects both quality and impact

### Step 2 — Candidate Generation

Generate 3-5 candidates using this formula:
```
North Star = f(Quality, Volume, Impact)

Examples:
- "Successful agent actions per week" (volume × quality)
- "Hours saved per user per month" (impact × adoption)
- "Accurate outputs delivered within SLA" (quality × reliability)
- "Revenue-impacting decisions supported" (impact × quality)
```

### Step 3 — Evaluation Matrix

| Candidate | Actionable | Measurable | Understandable | Leading | Composite | Score |
|-----------|:----------:|:----------:|:--------------:|:-------:|:---------:|:-----:|
| | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ | /5 |

### Step 4 — Decomposition Tree

Break down the North Star into input metrics:
```
North Star: [metric]
├── Driver 1: [sub-metric]
│   ├── Lever: [what team controls]
│   └── Lever: [what team controls]
├── Driver 2: [sub-metric]
│   ├── Lever: [what team controls]
│   └── Lever: [what team controls]
└── Driver 3: [sub-metric]
    ├── Lever: [what team controls]
    └── Lever: [what team controls]
```

### Step 5 — Target Setting

```
North Star: [metric name]
Current value: ___
3-month target: ___
6-month target: ___
12-month target: ___

Growth model:
- Conservative: ___% growth/month
- Expected: ___% growth/month
- Ambitious: ___% growth/month
```

### Step 6 — Anti-Metrics

Define what NOT to optimize (guardrails):
```
Anti-metric 1: [metric that shouldn't degrade]
  └── Floor: [minimum acceptable value]
Anti-metric 2: [metric that shouldn't degrade]
  └── Floor: [minimum acceptable value]
```

Example: If North Star is "agent executions per week", anti-metric is "accuracy rate" (floor: 95%)

### Output

North Star Card:
```
┌─────────────────────────────────────────┐
│ 🌟 North Star: [metric name]            │
├─────────────────────────────────────────┤
│ Current: [value]  →  Target: [value]    │
│ Timeframe: [period]                      │
├── Drivers ──────────────────────────────┤
│ 1. [driver] — current: [val]            │
│ 2. [driver] — current: [val]            │
│ 3. [driver] — current: [val]            │
├── Guardrails ───────────────────────────┤
│ ⚠️ [anti-metric 1] must stay > [floor]  │
│ ⚠️ [anti-metric 2] must stay > [floor]  │
└─────────────────────────────────────────┘
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **North Star 달성 불가** | 3개월 연속 목표 미달 (예: 100 → 65) | 목표 현실성 재검토 (보수적 타겟으로 재설정) + 분해 트리 분석 (막힌 드라이버 파악) |
| **Anti-metric 악화** | "Executions per week" 늘렸는데 Accuracy 85% 추락 | North Star 재정의 (품질 가중치 상향) 또는 anti-metric threshold 강화 |
| **분해 트리 미작동** | Lever가 North Star에 영향을 주지 못함 (미연결) | 드라이버-레버 연결 검증, 누락된 레버 추가 |
| **팀 정렬 부족** | 일부 팀이 자신의 KPI만 최적화 (North Star와 무관) | 월간 North Star 리뷰 미팅 강제화, OKR 연결 명시 |
| **목표 달성 후 정체** | North Star 목표 달성 후 팀의 동기 감소 | 새로운 기간의 North Star 목표 설정, 다음 단계 명확화 |

---

## Quality Gate

- [ ] North Star 후보 3-5개가 평가 매트릭스로 비교되었는가? (Actionable, Measurable, Understandable, Leading, Composite) (Yes/No)
- [ ] 최종 North Star가 5가지 기준을 모두 충족하는가? (5/5) (Yes/No)
- [ ] 분해 트리가 완성되어 있고, 각 레버가 팀의 직접 통제 범위인가? (Yes/No)
- [ ] Anti-metric이 명시되어 있고, 악화 시 알림 임계값이 설정되었는가? (Yes/No)
- [ ] 현재값 → 3/6/12개월 목표값이 보수적으로(달성 가능한 수준) 설정되었는가? (Yes/No)
- [ ] 월간 리뷰 일정과 분기 OKR 연결이 명시되었는가? (Yes/No)

---

## Examples

### Good Example

```
North Star: 고객 지원 에이전트

🌟 North Star Metric: "월별 정확한 지원 건수(Accurate Support Tasks Delivered)"

정의: (월간 집행 건수) × (Accuracy %) × (first-contact resolution %)
기준선: 4,000 × 92% × 85% = 3,128건

분해 트리:
├── Driver 1: 월간 집행 건수 (4,000 → 5,000)
│   ├── Lever: 프롬프트 최적화 (응답 시간 -0.5s)
│   └── Lever: 병렬 처리 아키텍처 (동시 실행 2배)
├── Driver 2: Accuracy (92% → 95%)
│   ├── Lever: TK-042 추가 학습
│   └── Lever: Confidence gate 구현
└── Driver 3: FCR (85% → 90%)
    ├── Lever: 에스컬레이션 프롬프트 개선
    └── Lever: 사람 핸드오프 프로세스 최적화

Anti-metrics (Guardrails):
⚠️ Accuracy > 90% (절대 떨어지면 안 됨)
⚠️ Cost per task < $0.15 (비용 폭증 방지)

목표:
- 3개월: 3,500건 (+12%)
- 6개월: 4,000건 (+28%)
- 12개월: 4,500건 (+44%)

월간 리뷰 = North Star + 3개 Driver 추이 확인
```

### Bad Example

```
"North Star는 Accuracy를 택하자"

❌ 문제점:
- Actionable 부족: Accuracy 높이려면? (팀이 통제 불가능한 요소도 있음)
- Composite 부족: 비용 악화 무시
- 비즈니스 임팩트 미반영: 정확도만 높고 사용량 0이면 가치 0
- Anti-metric 없음: Accuracy 99%이지만 비용 폭증 가능
- 분해 불가: "Accuracy를 높이려면?"에 답할 수 없음

→ 재작업: 5가지 기준 점검 → Composite 후보 선정 → 분해 트리 구성 → Anti-metric 설정
```

---

## Further Reading
- Sean Ellis, *Hacking Growth* — North Star Metric framework
- Amplitude, "North Star Playbook" — Metric selection guide

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
