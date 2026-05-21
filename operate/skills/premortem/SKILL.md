---
name: premortem
description: "Pre-mortem failure analysis for AI agents using FMEA methodology — identify how an agent can fail before it does, assess severity and likelihood, and design prevention strategies. Use before launching a new agent, after a near-miss incident, or when reviewing agent risk profiles."
argument-hint: "[agent to analyze risks for]"
allowed-tools: ["Read", "Write"]
context: fork
model: sonnet
hooks:
  Stop:
    - type: command
      command: "bash scripts/validate-review.sh premortem . 2>/dev/null || true"
---

# Failure Mode Analysis

> 에이전트 사전 실패 분석 — 실패하기 전에 실패 모드를 식별하고 예방

## Core Goal

- **잠재적 실패 모드를 사전에 식별 및 우선순위화** — "만약 실패한다면?"이라는 질문으로 숨은 위험 노출
- **위험도(RPN) 기반 예방 전략 설계** — 심각도 × 발생 가능성 × 감지 어려움을 고려한 효율적 자원 배분
- **사후 대응에서 사전 예방으로 전환** — incident 대응의 비용(비즈니스, 신뢰도)보다 낮은 비용으로 문제 차단

---

## Trigger Gate

### Use This Skill When

- 새로운 에이전트 아키텍처를 배포하기 전에 리스크 검토가 필요할 때
- 장애(incident)가 발생한 후 유사 실패 방지 메커니즘을 설계할 때
- 에이전트의 정기적 안전성 검토(분기별, 반기별)를 수행할 때
- 규제/컴플라이언스 요구사항 때문에 리스크 문서화가 필요할 때

### Route to Other Skills When

- **incident** → 실제로 발생한 장애를 분석할 때 (premortem은 사전, incident는 사후)
- **reliability** → premortem 결과로 신뢰성 개선 계획 수립
- **burn-rate** → 비용 폭증 시나리오를 premortem에서 식별한 경우
- **kpi** → premortem 결과로 guardrail KPI 설정

### Boundary Checks

- **과도한 悲觀主義** — 모든 가능한 실패를 나열하면 분석 마비 → RPN 기준으로 상위 10-15개만 우선화
- **기술 중심 편향** — 모델 오류만 초점 → 데이터, 통합, 비즈니스 실패도 포함
- **일회성 분석** — 처음 premortem 후 방치 → 분기별 재검토 필수 (조직/환경 변화 반영)

---

## 개념

Pre-mortem: "이 에이전트가 3개월 후 완전히 실패했다고 가정하자. 왜 실패했을까?" 이 질문으로 시작하면 사후 대응이 아닌 사전 예방이 가능하다.

## Instructions

You are conducting a **failure mode analysis** for: **$ARGUMENTS**

### Step 1 — Pre-mortem Exercise

Imagine it's 3 months from now. The agent has completely failed.
List all possible reasons:

```
"The agent failed because..."
1. ___
2. ___
3. ___
4. ___
5. ___
```

### Step 2 — FMEA Table (Failure Mode and Effects Analysis)

| Failure Mode | Cause | Effect | Severity (1-10) | Probability (1-10) | Detection (1-10) | RPN |
|-------------|-------|--------|-----------------|--------------------|--------------------|-----|
| | | | | | | |

**RPN** (Risk Priority Number) = Severity × Probability × Detection
- Detection: 1 = easily detected, 10 = undetectable
- Focus on RPN > 100 first

### Step 3 — AI-Specific Failure Modes

Check each category:

**Model Failures**
- [ ] Hallucination in critical outputs
- [ ] Inconsistent outputs for same input
- [ ] Performance degradation after model update
- [ ] Context window overflow losing critical info
- [ ] Prompt injection vulnerability

**Data Failures**
- [ ] Input data format changes (upstream API changes)
- [ ] Missing or null data handling
- [ ] Data drift (input distribution changes over time)
- [ ] PII leakage in outputs

**Integration Failures**
- [ ] API rate limits hit during peak usage
- [ ] External service downtime
- [ ] Authentication token expiration
- [ ] Version mismatch between components

**Business Failures**
- [ ] Cost exceeds budget (token cost explosion)
- [ ] Users stop using it (low adoption)
- [ ] Output doesn't match business need (misaligned objectives)
- [ ] Regulatory/compliance violation

### Step 4 — Prevention Strategy

For each high-RPN failure mode:
```
Failure Mode: [name]
├── Prevention: [how to stop it from happening]
├── Detection: [how to know it happened]
├── Response: [what to do when it happens]
└── Recovery: [how to get back to normal]
```

### Step 5 — Monitoring Triggers

Design early warning alerts:
```
⚠️ Yellow Alert (investigate):
- [metric] drops below [threshold]
- [error type] exceeds [N] per [period]

🔴 Red Alert (immediate action):
- [critical metric] breaches [threshold]
- [cascading failure pattern] detected
```

### Step 6 — Go/NoGo 기준 매핑

RPN 점수와 모니터링 트리거를 배포 의사결정 기준으로 변환합니다.

```
📊 Go/NoGo Decision Matrix:

RPN < 50 (저위험)
└─ → GO (자동 배포 가능)
   └─ 예: 모니터링으로 충분

RPN 50-100 (중위험)
└─ → CONDITIONAL GO (완화 조치 필수)
   ├─ 요구사항: Yellow alert 설정 필수
   ├─ 조건: Prevention 메커니즘 구현 및 검증
   └─ 제약: 제한된 범위(1-10% 트래픽 또는 특정 사용자군)에서 시작

RPN > 100 (고위험)
└─ → NO-GO (재설계 필수)
   ├─ 요구사항: Prevention 전략 완성 + Red alert 구현
   ├─ 조건: 액션 아이템 100% 완료, 재premortem 통과
   └─ 재검토: 최소 1주 모니터링 후 재평가
```

**매핑 템플릿:**

| Failure Mode | RPN | 의사결정 | 모니터링 | 배포 조건 |
|---|---|---|---|---|
| [이름] | [점수] | GO/COND/NOGO | Yellow: [기준], Red: [기준] | [제약사항] |

### Output

Failure Mode Summary:
```
Agent: [name]
Analysis Date: [date]
Total Failure Modes Identified: [N]
Critical (RPN > 200): [N]
High (RPN 100-200): [N]
Mitigated: [N] / [Total]
Top Risk: [failure mode] (RPN: [score])
Next Review: [date]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **RPN 계산 오류** | 팀마다 같은 실패 모드의 RPN을 다르게 책정 (평가 표준 불일치) | RPN 계산 워크숍 진행, 평가 기준 표준화 (예: Severity 8 = "유저 1000명 영향") |
| **Prevention 설계 미실행** | FMEA 테이블은 완성했으나 Prevention 액션이 미실행 → 같은 실패 반복 | 액션 아이템별 Owner 및 Deadline 명시, 월간 추적 리뷰 |
| **새로운 위험 도입** | Prevention 구현 중 새로운 실패 모드 발생 (예: circuit breaker 추가로 복잡성 증가) | 구현 후 재premortem 수행 (incremental premortem) |
| **감지 어려움 저평가** | Detection score = 3으로 설정했으나 실제로는 감지 불가능 (9~10 수준) | 모니터링 인프라 재검토, 자동 알림 추가, Detection score 재평가 |
| **위험 평가 노후화** | 3개월 전 premortem 결과를 그대로 신뢰 → 조직/기술 변화로 위험도 증가 | 분기별 재premortem, 중요 변화(모델 업그레이드, 사용자 규모 2배)는 즉시 재검토 |

---

## Quality Gate

- [ ] 최소 5개의 "에이전트가 실패한다면?"이 pre-mortem exercise에서 도출되었는가? (Yes/No)
- [ ] FMEA 테이블이 완성되어 있으며, RPN 상위 10개가 명확한가? (Yes/No)
- [ ] 모델, 데이터, 통합, 비즈니스 4가지 카테고리의 실패 모드가 모두 포함되었는가? (Yes/No)
- [ ] RPN > 100인 고위험 모드 각각에 대해 Prevention/Detection/Response/Recovery 전략이 명시되었는가? (Yes/No)
- [ ] 모니터링 트리거(Yellow alert, Red alert)가 실제 감지 가능하도록 설계되었는가? (Yes/No)
- [ ] 모니터링 트리거가 Go/NoGo 의사결정 기준과 연결되어 있는가? (Yes/No)
- [ ] 액션 아이템별로 Owner, Deadline, 완료 여부가 기록되었으며, 분기별 재premortem이 예정되었는가? (Yes/No)

---

## Examples

### Good Example

```
Premortem: 멀티에이전트 오케스트레이터 배포 전

"3개월 후, 이 시스템이 완전히 망했다. 왜일까?"

도출된 실패 모드 (상위 RPN):

1. 하위 에이전트 연쇄 실패 (RPN: 240)
   - Severity: 8 (서비스 전체 중단)
   - Probability: 6 (멀티 에이전트 = 의존성 증가)
   - Detection: 5 (에러 로그에서 감지 가능)

   Prevention: 각 하위 에이전트에 circuit breaker 구현
   Detection: 에이전트별 오류율 > 5% 시 자동 차단
   Response: 즉시 오케스트레이터 "safe mode"로 전환
   Recovery: 개별 에이전트 격리 후 순차 재시작

2. 토큰 폭증 (RPN: 180)
   - Cause: 재시도 루프로 같은 요청 10회 중복
   - Prevention: 멱등성(idempotency) 검증 + 토큰 누적 로그
   - Alert: 일일 비용 2배 초과 시 알림

액션 아이템:
- [ ] Circuit breaker 구현 (Owner: Alice, Deadline: 2026-03-15, Status: 완료)
- [ ] 토큰 모니터링 대시보드 구축 (Owner: Bob, Deadline: 2026-03-22, Status: 진행 중)
- [ ] 재premortem (2026-04-01)
```

### Bad Example

```
"배포 전에 한 번 미팅만 하자"

❌ 문제점:
- Pre-mortem exercise 미실시 (FMEA 테이블 없음)
- RPN 계산 없음 → 어떤 위험부터 해결할지 불명확
- Prevention 전략 미설계 → 실제로 문제 발생 시 대응 불가
- 모니터링 알림 미설정 → 조용한 실패(silent failure) 감지 불가
- 액션 아이템 Owner/Deadline 없음 → 계획만 있고 실행 안 됨

→ 재작업: FMEA 테이블 작성 → RPN 우선순위화 → Prevention + Detection 설계 → 액션 아이템 추적
```

---

## Further Reading
- Gary Klein, "Performing a Project Premortem" — HBR, 2007 (프리모템 원전)
- IEC 60812 — FMEA standard methodology (산업 표준 실패 분석)
- Anthropic, "Building Effective Agents" (2024) — Agent error handling & recovery patterns
- Google, "People + AI Guidebook" — AI failure modes and human-AI interaction design
- NIST AI Risk Management Framework (AI RMF 1.0) — https://www.nist.gov/artificial-intelligence/executive-order-safe-secure-and-trustworthy-artificial-intelligence

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
