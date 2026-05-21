---
name: kpi
description: "Define and track Key Performance Indicators for AI agents — operational metrics (latency, success rate, error rate) and business metrics (task completion, user satisfaction, cost per task). Use when setting up agent monitoring dashboards, defining SLAs, or establishing performance baselines."
argument-hint: "[agent to define KPIs for]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# Agent KPI

> AI 에이전트의 핵심 성과 지표(KPI) 정의 및 추적

## Core Goal

- **에이전트의 운영 건강도와 비즈니스 임팩트를 동시에 추적** — 정량화된 대시보드로 의사결정 기반 확보
- **Leading과 Lagging 지표를 균형 있게 설정** — 조기 경고(Leading)로 문제를 미리 감지하고 결과(Lagging)로 영향 측정
- **팀 전체가 공유할 수 있는 명확한 메트릭 정의** — 모호함을 배제하고 자동화 추적 가능한 형태로 구성

---

## Trigger Gate

### Use This Skill When

- 에이전트를 처음 배포하고 모니터링 대시보드를 설정할 때
- 기존 KPI가 비즈니스 목표와 정렬되지 않았을 때
- SLA(Service Level Agreement)를 정의하거나 업데이트해야 할 때
- 팀 내에서 "성공"의 정의가 다를 때 (지표 통일 필요)

### Route to Other Skills When

- **north-star** → 여러 KPI를 하나의 North Star로 통합하는 경우
- **burn-rate** → KPI 대시보드에 비용 효율 메트릭 추가
- **cohort** → KPI 변화를 코호트별로 추적할 필요가 있을 때
- **incident** → KPI 임계값 이탈 시 자동으로 incident 분류

### Boundary Checks

- **측정 불가능한 지표는 제외** — "사용자 만족도"는 주관적이므로 NPS/CSAT 같은 정량 대체지표 사용
- **과도한 지표 개수** — 5-7개 KPI로 제한 (10개 이상은 추적 불가)
- **Alert Threshold 현실성** — 달성 불가능한 목표는 팀 사기 저하 → 비교값(이전 버전, 경쟁사, 업계 표준) 기반 설정

---

## 개념

에이전트 KPI는 두 축으로 나뉜다: **운영 건강도**(잘 돌아가는가)와 **비즈니스 임팩트**(가치를 만드는가). 둘 다 측정하지 않으면 "잘 돌아가지만 쓸모없는" 또는 "가치있지만 불안정한" 에이전트가 된다.

## Instructions

You are defining **KPIs** for: **$ARGUMENTS**

### Step 1 — Operational Health Metrics

These measure "Is the agent working correctly?"

| Metric | Formula | Target | Alert Threshold |
|--------|---------|--------|-----------------|
| **Accuracy** | Correct outputs ÷ Total executions | >95% | <90% |
| **Reliability** | Successful runs ÷ Total runs | >99% | <95% |
| **Latency** | Average execution time | <Xs | >2Xs |
| **Cost per Execution** | Total cost ÷ Executions | <$X | >1.5×$X |
| **Error Rate** | Failed runs ÷ Total runs | <1% | >5% |

### Step 2 — Business Impact Metrics

These measure "Is the agent creating value?"

| Metric | Formula | Target |
|--------|---------|--------|
| **Time Saved** | Manual time - Agent time per task | >X hrs/week |
| **Cost Saved** | Manual cost - Agent cost | >$X/month |
| **Throughput Increase** | Tasks completed with agent ÷ without | >Xx |
| **Error Prevention** | Errors caught by agent ÷ Total errors | >X% |
| **User Satisfaction** | NPS or CSAT score from agent users | >X |

### Step 3 — KPI Dashboard Design

For each KPI, define:
```
KPI: [name]
├── Definition: [precise formula]
├── Data Source: [where the data comes from]
├── Collection Method: [automated/manual]
├── Frequency: [real-time/daily/weekly]
├── Owner: [who monitors this]
├── Baseline: [current value]
├── Target: [goal value]
└── Alert: [threshold that triggers review]
```

### Step 4 — Leading vs Lagging Indicators

Separate early warning signals from outcomes:
```
Leading (predict future performance):
- Input data quality score
- Prompt version performance delta
- User engagement frequency

Lagging (confirm past performance):
- Monthly cost savings
- Quarterly business impact
- User retention rate
```

### Step 5 — Review Cadence

| Cadence | What to Review | Action |
|---------|---------------|--------|
| Daily | Error rate, latency spikes | Immediate fix |
| Weekly | Accuracy trends, cost tracking | Optimization |
| Monthly | Business impact KRs | Strategy adjustment |
| Quarterly | North Star metric, OKR review | Goal revision |

### Output

Present KPI card:
```
┌─────────────────────────────────────┐
│ Agent: [name]                        │
├── Operational Health ────────────────┤
│ Accuracy:     [current] → [target]  │
│ Reliability:  [current] → [target]  │
│ Latency:      [current] → [target]  │
│ CPE:          [current] → [target]  │
├── Business Impact ───────────────────┤
│ Time Saved:   [current] → [target]  │
│ Cost Saved:   [current] → [target]  │
│ Throughput:   [current] → [target]  │
└─────────────────────────────────────┘
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **KPI 정의 불명확** | 팀마다 "Accuracy"를 다르게 계산 (정답 판단 기준 불일치) | 정의 표준화 (formula, data source, collection method 명시), 자동화 계산으로 전환 |
| **임계값 설정 오류** | Accuracy > 95% 목표 → 첫 주부터 달성 못 함 (기준선 92%) | 비교값 기반 재설정 (현재 92% → 3개월에 95% 달성 같이 단계적 목표) |
| **Guardrail 부재** | CPE 최적화에만 집중 → Accuracy 85%로 급락 | Anti-metric 명시 (e.g., CPE < $0.1이어도 Accuracy > 90% 유지) |
| **데이터 수집 지연** | 일일 리포트가 2-3일 후 생성 → 의사결정 타이밍 놓침 | 자동화 대시보드 구축, 실시간/일일 메트릭 분리 |
| **KPI 보고 없음** | 대시보드 존재하나 팀이 주기적으로 검토하지 않음 | 고정 리뷰 일정 설정 (주간/월간), 담당자 지정 |

---

## Quality Gate

- [ ] 운영 건강도 메트릭(Accuracy, Reliability, Latency, CPE)이 정의되었는가? (Yes/No)
- [ ] 비즈니스 임팩트 메트릭(Time Saved, Cost Saved, User Satisfaction)이 정의되었는가? (Yes/No)
- [ ] 각 KPI가 명확한 formula, data source, collection method를 갖고 있는가? (Yes/No)
- [ ] Leading과 Lagging 지표가 분리되어 있는가? (Yes/No)
- [ ] Alert threshold가 현실적이고 비교값(baseline/경쟁사)을 기반으로 하는가? (Yes/No)
- [ ] 자동화된 대시보드와 주기적 리뷰 일정(일일/주간/월간)이 설정되었는가? (Yes/No)

---

## Examples

### Good Example

```
KPI 정의: 고객 지원 에이전트

운영 건강도:
┌──────────────────────┐
│ Accuracy: 94% → 96%  │ (주간 리뷰, 자동 계산)
│ 기준: 정답률          │
│ 목표: 월 0.5% 증가   │
│ Alert: < 90%         │
├──────────────────────┤
│ Latency: 1.2s → 1.0s│ (P95, 실시간)
│ 목표: 1초 이하       │
│ Alert: > 2초         │
├──────────────────────┤
│ CPE: $0.08 → $0.06  │ (일일)
│ 목표: 분기 10% 절감  │
│ Alert: > $0.12       │
└──────────────────────┘

비즈니스 임팩트:
- Time Saved: 8hrs/day (지원팀)
- Cost Saved: $2,400/month
- CSAT: 4.2/5.0

Leading 지표:
- 응답 형식 오류율 (매일)
- 메모리 용량 사용량 (주간)

리뷰 주기:
- 일간: 실시간 alert 확인
- 주간: Accuracy, Latency 추이 검토
- 월간: Business impact 분석 + OKR 연결
```

### Bad Example

```
"잘 돌아가는 것 같으니까 KPI는 대충 정해도 되겠지"

❌ 문제점:
- Accuracy 정의 불명확 (정답 판단 기준 불일치)
- 목표값이 주관적 ("좋은 정확도")
- 자동화 추적 없음 (수동 계산)
- Leading 지표 없음 (문제 조기 감지 불가)
- 리뷰 일정 없음 (대시보드만 존재)
- 의사결정 기준 불명확

→ 재작업: formula 명시 → data source 자동화 → Alert threshold 설정 → 리뷰 일정 고정
```

---

## Further Reading
- Alistair Croll & Benjamin Yoskovitz, *Lean Analytics* — Metric design
- Cagan & Jones, *INSPIRED* / *EMPOWERED* — Product metrics

---


---

## Implementation Reference

KPI를 정의한 다음 단계 — **실제로 측정하는 코드**:

```bash
# ScoreCard 구현체 로드 (참고)
cat references/scorecard-python.md
```

| 클래스 | 역할 |
|-------|------|
| `EvalResult` | 평가 입력 데이터 (accuracy, latency, cost, impact) |
| `ScoreCard` | 5차원 점수 + overall 가중 계산 + tier 자동 산정 |
| `MultiDimScorer` | EvalResult → ScoreCard 변환, 차원별 비교 |
| `EvalReporter` | ScoreCard 목록 → Markdown 랭킹 테이블 |

> `overall = accuracy×0.35 + reliability×0.25 + speed×0.20 + cost×0.10 + impact×0.10`  
> 점수 75+ → L2+ | 90+ → L3

전체 코드 및 사용 예시: [`references/scorecard-python.md`](references/scorecard-python.md)

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

### ScoreCard Implementation
!`cat references/scorecard-python.md 2>/dev/null || echo ""`
