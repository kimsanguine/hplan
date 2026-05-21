---
name: reliability
description: "Systematically review and improve AI agent reliability — identify failure patterns, assess error handling, design safeguards, and set reliability targets. Use when agents are producing inconsistent results, after incidents, or when preparing for production deployment."
argument-hint: "[agent to assess]"
allowed-tools: ["Read", "Write"]
context: fork
model: sonnet
hooks:
  Stop:
    - type: command
      command: "bash scripts/validate-review.sh reliability . 2>/dev/null || true"
---

# Reliability Review

> 에이전트 신뢰성 체계적 점검 및 개선

## Core Goal

- **에이전트의 "최악의 경우" 신뢰성을 정량화** — 평균이 아니라 백분위수(P95, P99)로 신뢰도 평가
- **실패 패턴을 분류하고 각각에 대한 safeguard 설계** — 입력 오류, 모델 오류, 통합 오류 등 유형별 방어책 구축
- **신뢰성 수준(Basic/Standard/High/Critical)을 비즈니스 요구에 맞추기** — 내부 도구는 95%, 고객 대면은 99.9% 같이 차등 목표 설정

---

## Trigger Gate

### Use This Skill When

- 에이전트를 프로덕션에 배포하기 전에 신뢰성 평가가 필요할 때
- incident 이후 비슷한 실패를 방지하기 위해 safeguard를 강화할 때
- 에이전트 성능이 불안정하거나 예측 불가능한 패턴을 보일 때
- SLA 보장(예: 99.5% uptime)이 필요한 고객 계약을 체결할 때

### Route to Other Skills When

- **incident** → 실제 장애가 발생한 후 근본 원인 분석과 신뢰성 개선 연결
- **premortem** → 신뢰성 개선 계획의 리스크를 사전 분석할 때
- **kpi** → 신뢰성을 KPI 대시보드(Success Rate, Error Rate)에 포함
- **cohort** → 신뢰성이 코호트(버전)별로 다르게 나타날 때 (버전 비교)

### Boundary Checks

- **기준선 데이터 부족** — 최소 1주일 이상 데이터 필요 (일일 변동성 흡수)
- **실패 분류의 표준화** — 팀마다 "에러"를 다르게 정의하면 신뢰성 측정 불가 → formula 명시
- **Safeguard 과도화** — 모든 가능한 실패에 방어책을 세우면 성능 저하 → 영향도 × 발생 확률로 우선순위화

---

## 개념

에이전트 신뢰성은 "평균적으로 잘 되는가"가 아니라 "최악의 경우에도 허용 가능한가"로 측정한다. 99%의 성공률은 100번 중 1번 실패를 의미하고, 실패 1번의 비용이 99번의 가치를 초과할 수 있다.

## Instructions

You are conducting a **reliability review** for: **$ARGUMENTS**

### Step 1 — Reliability Baseline

Collect current data:
```
Total executions (last 30 days): ___
Successful: ___ (___%)
Failed: ___ (___%)
Partially correct: ___ (___%)
```

### Step 2 — Failure Taxonomy

Classify all failures:

| Category | Count | Severity | Example |
|----------|-------|----------|---------|
| **Input Error** | | Low-High | Malformed input, missing data |
| **Model Error** | | Medium | Hallucination, wrong format |
| **Tool Error** | | Medium | API timeout, rate limit |
| **Logic Error** | | High | Wrong decision, missed edge case |
| **Output Error** | | Medium | Correct answer, wrong format |

### Step 3 — Failure Pattern Analysis

For each failure category:
```
Pattern: [description]
Frequency: [how often]
Root Cause: [why it happens]
Impact: [what goes wrong for the user]
Detection: [how we know it failed]
Recovery: [what happens after failure]
```

### Step 4 — Safeguard Design

For each high-impact failure, design a safeguard:

| Safeguard Type | When to Use | Example |
|---------------|------------|---------|
| **Input Validation** | Predictable bad inputs | Schema validation before execution |
| **Output Validation** | Format/content requirements | JSON schema check, range validation |
| **Confidence Gate** | Uncertain outputs | If confidence < 0.8, escalate to human |
| **Retry with Backoff** | Transient failures | Retry 3x with exponential backoff |
| **Fallback Path** | Critical failures | Switch to simpler model or manual flow |
| **Circuit Breaker** | Cascading failures | Stop after N consecutive failures |

### Step 5 — Reliability Target Setting

| Level | Success Rate | Meaning | Appropriate For |
|-------|-------------|---------|-----------------|
| Basic | 90% | 1 in 10 fails | Internal tools, non-critical |
| Standard | 95% | 1 in 20 fails | Regular business ops |
| High | 99% | 1 in 100 fails | Customer-facing, financial |
| Critical | 99.9% | 1 in 1000 fails | Safety, compliance |

Current level: ___
Target level: ___

### Step 6 — Improvement Roadmap

Prioritize by: Impact × Frequency × Ease of Fix
```
Quick Wins (this week):
- [ ] [safeguard 1]
- [ ] [safeguard 2]

Medium Term (this month):
- [ ] [improvement 1]
- [ ] [improvement 2]

Long Term (this quarter):
- [ ] [architecture change]
```

### Output

Reliability report card:
```
Agent: [name]
Period: [date range]
Reliability: [current%] → Target: [target%]
Top Failure: [category] ([count] occurrences)
New Safeguards: [count] implemented
Next Review: [date]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **신뢰성 기준선 편향** | "실패율 5%"라고 계산했으나 실패 정의가 팀마다 다름 | 실패의 정의를 formula로 명시화 (예: "응답이 0초 안에 없거나 오류 반환") → 재측정 |
| **Safeguard 성능 저하** | Confidence gate 추가 → 정확도는 올랐지만 응답 불가율 15% 증가 | 임계값 조정 (confidence threshold 하향) 또는 fallback path 개선 |
| **특정 입력에만 실패** | 대부분의 요청은 성공하는데 특정 패턴(예: 특수문자 포함)에서만 오류 | Input validation 강화, 실패 입력 타입별 분류, 패턴별 safeguard 설계 |
| **신뢰성 목표 달성 불가** | 99% 목표는 설정했으나 현재 95% → 4% gap을 닫을 방법 부족 | 1) 빠른 개선 가능한 것(Input validation) 먼저 시행 2) 장기 아키텍처 개선 분리 |
| **Safeguard 비용** | Retry with backoff 추가 → 토큰 비용 20% 증가 | 비용-신뢰성 트레이드오프 명시 (비용 +$100/월로 reliability 98% → 99% 달성), 의사결정 |

---

## Quality Gate

- [ ] 현재 신뢰성 기준선(Success Rate, Error Rate)이 명확하게 정의되고 측정되었는가? (Yes/No)
- [ ] 실패가 5가지 이상의 카테고리(Input, Model, Tool, Logic, Output)로 분류되었는가? (Yes/No)
- [ ] 각 실패 카테고리별로 패턴 분석(Frequency, Root Cause, Impact, Detection, Recovery)이 완료되었는가? (Yes/No)
- [ ] 높은 영향도(High impact) 실패 각각에 대해 safeguard가 설계되었는가? (Yes/No)
- [ ] 신뢰성 목표 수준(Basic/Standard/High/Critical)이 비즈니스 요구와 정렬되었는가? (Yes/No)
- [ ] 현재 수준 → 목표 수준까지의 로드맵(Quick Wins, Medium Term, Long Term)이 명시되었는가? (Yes/No)

---

## Examples

### Good Example

```
신뢰성 리뷰: 내부 업무 효율화 에이전트

기준선 (30일):
├── 총 실행: 2,400건
├── 성공: 2,280건 (95%)
├── 실패: 120건 (5%)
└── 부분 성공: 0건

실패 분류:

| 카테고리 | 개수 | 원인 예시 | 심각도 |
|---------|------|---------|-------|
| Input Error | 30 | 잘못된 형식(JSON 미형성) | Low |
| Model Error | 60 | 환각, 형식 오류 | Medium |
| Tool Error | 20 | API timeout | High |
| Logic Error | 8 | 조건 검사 누락 | High |
| Output Error | 2 | 너무 긴 응답 | Low |

Safeguard 설계:

High Impact 3가지:
1. Model Error (60개) → Confidence gate (threshold 0.7)
   - Expected: 실패 60→ 40 (667% 개선 예상 시간: 5일)

2. Tool Error (20개) → Retry with exponential backoff
   - Expected: 실패 20→ 5 (timeout 복구율 75%)

3. Input Error (30개) → JSON schema validation
   - Expected: 실패 30→ 2 (거의 전부 사전 차단)

목표 수준: High (99%)
- 현재: 95%
- 3주 후: 98% (safeguard 1,3 적용)
- 6주 후: 99% (safeguard 2까지 추가)
```

### Bad Example

```
"에이전트의 신뢰성이 좋지 않은 것 같다"

❌ 문제점:
- "신뢰성"의 정의가 주관적 (기준선 없음)
- 실패 분류 없음 (어떤 실패가 몇 개인지 모름)
- Safeguard 미설계 (대응 방법 불명확)
- 목표 수준 미설정 (뭐가 "좋은" 신뢰성인지 불명확)
- 개선 로드맵 없음

→ 재작업: 기준선 수집 → 실패 분류 → 패턴 분석 → safeguard 설계 → 목표 설정 → 로드맵 수립
```

---

## Further Reading
- Google SRE Book — Site Reliability Engineering principles
- Anthropic, "Building Effective Agents" (2024) — Error handling patterns

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`

### Test Cases
!`cat references/test-cases.md 2>/dev/null || echo ""`

### Troubleshooting
!`cat references/troubleshooting.md 2>/dev/null || echo ""`
