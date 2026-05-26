---
name: metrics-design
description: "Design the metrics hierarchy and OKRs for an AI agent — North Star, KPI derivation, and OKR setting. Supports --step north-star | kpi | okr | all (default)."
argument-hint: "[agent or product] [--step north-star|kpi|okr|all]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# metrics-design

> AI 에이전트의 메트릭 계층 설계 — North Star 정의 후 KPI 파생

## Core Goal

- **단일 North Star 메트릭으로 팀 전략 정렬** — 운영 건강도와 비즈니스 임팩트를 동시에 반영하는 "하나의 숫자" 확립
- **North Star를 KPI 대시보드의 최상위에 연결** — Leading/Lagging 지표 계층을 결정론적 공식으로 정의
- **의사결정 우선순위 명확화** — 충돌하는 지표 간 트레이드오프를 North Star 기준으로 일관성 있게 해결

---

## Trigger Gate

### Use This Skill When

- "북극성 메트릭 정의해줘" — North Star가 필요한 모든 상황
- "KPI 설정해줘" — 에이전트 성과 지표 체계 구축 시
- "에이전트 성과 측정 기준 잡아줘" — 메트릭 계층 전체가 필요할 때
- 새로운 에이전트 제품 론칭, 기존 KPI 충돌, 분기 OKR 연결 시

### Route to Other Skills When

- **portfolio-report --view scorecard** → 정의된 KPI로 상대 비교 점수화
- **burn-rate** → North Star에 비용 효율 요소가 포함될 때
- **cohort** → North Star 추이를 코호트별로 추적할 때
- **agent-ab-test** → A/B 테스트의 Primary 메트릭으로 North Star 사용 시

### Boundary Checks

- **코드 배포해줘** → deliver 플러그인으로 라우팅
- **UI 점검해줘** → craft 플러그인으로 라우팅
- 메트릭 선택의 주관성 → 5가지 기준(Actionable · Measurable · Understandable · Leading · Composite) 충족 여부 점검
- Anti-metric 설정 → North Star 최적화로 인한 다른 지표 악화를 사전에 차단

---

## 개념

North Star Metric은 에이전트의 성공을 하나의 숫자로 표현한다. KPI는 그 숫자를 분해한 운영 건강도(잘 돌아가는가)와 비즈니스 임팩트(가치를 만드는가)의 두 축이다. 두 층을 함께 설계하지 않으면 "정확도만 높고 쓸모없는" 또는 "가치있지만 불안정한" 에이전트가 된다.

---

## Instructions

You are designing metrics for: **$ARGUMENTS**

Parse `--step` from the arguments:
- `--step north-star` → Run Phase A only
- `--step kpi` → Run Phase B only
- `--step okr` → Run Phase C only (OKR 설계)
- `--step all` or no `--step` flag → Run Phase A then Phase B then Phase C (default)

---

### Phase A — North Star 정의 (`--step north-star` or `--step both`)

**A1 — North Star Criteria 체크**

좋은 North Star Metric은 다음 5가지를 충족해야 한다:
- [ ] **Actionable**: 팀이 직접 영향을 미칠 수 있는가
- [ ] **Measurable**: 자동으로 추적 가능한가
- [ ] **Understandable**: 누구나 설명할 수 있는가
- [ ] **Leading**: 미래 성공을 예측하는가 (과거 기록 아님)
- [ ] **Composite**: 품질과 임팩트를 동시에 반영하는가

**A2 — 후보 생성**

3~5개 후보를 다음 공식으로 생성한다:
```
North Star = f(Quality, Volume, Impact)

예시:
- "Successful agent actions per week" (volume × quality)
- "Hours saved per user per month" (impact × adoption)
- "Accurate outputs delivered within SLA" (quality × reliability)
- "Revenue-impacting decisions supported" (impact × quality)
```

**A3 — 평가 매트릭스**

| 후보 | Actionable | Measurable | Understandable | Leading | Composite | Score |
|-----|:----------:|:----------:|:--------------:|:-------:|:---------:|:-----:|
| | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ | ✓/✗ | /5 |

**A4 — 분해 트리**

```
North Star: [metric]
├── Driver 1: [sub-metric]
│   ├── Lever: [팀이 통제하는 요소]
│   └── Lever: [팀이 통제하는 요소]
├── Driver 2: [sub-metric]
│   └── Lever: [팀이 통제하는 요소]
└── Driver 3: [sub-metric]
    └── Lever: [팀이 통제하는 요소]
```

**A5 — 목표 설정**

```
North Star: [metric name]
현재값: ___
3개월 목표: ___
6개월 목표: ___
12개월 목표: ___
```

**A6 — Anti-Metrics (Guardrails)**

```
Anti-metric 1: [악화되면 안 되는 지표]
  └── Floor: [최소 허용값]
Anti-metric 2: [악화되면 안 되는 지표]
  └── Floor: [최소 허용값]
```

**A 출력 — North Star Card**

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

### Phase B — KPI 파생 (`--step kpi` or `--step both`)

**B1 — 운영 건강도 KPI**

| Metric | Formula | Target | Alert Threshold |
|--------|---------|--------|-----------------|
| **Accuracy** | Correct outputs ÷ Total executions | >95% | <90% |
| **Reliability** | Successful runs ÷ Total runs | >99% | <95% |
| **Latency** | Average execution time | <Xs | >2Xs |
| **Cost per Execution** | Total cost ÷ Executions | <$X | >1.5×$X |
| **Error Rate** | Failed runs ÷ Total runs | <1% | >5% |

**B2 — 비즈니스 임팩트 KPI**

| Metric | Formula | Target |
|--------|---------|--------|
| **Time Saved** | Manual time - Agent time per task | >X hrs/week |
| **Cost Saved** | Manual cost - Agent cost | >$X/month |
| **Throughput Increase** | Tasks with agent ÷ without | >Xx |
| **User Satisfaction** | NPS or CSAT | >X |

**B3 — KPI 대시보드 정의**

각 KPI:
```
KPI: [name]
├── Definition: [precise formula]
├── Data Source: [측정 출처]
├── Collection Method: [automated/manual]
├── Frequency: [real-time/daily/weekly]
├── Owner: [담당자]
├── Baseline: [현재값]
├── Target: [목표값]
└── Alert: [review 트리거 임계값]
```

**B4 — Leading vs Lagging 분리**

```
Leading (미래 예측 신호):
- 입력 데이터 품질 점수
- 프롬프트 버전 성능 delta
- 사용자 참여 빈도

Lagging (과거 성과 확인):
- 월간 비용 절감
- 분기 비즈니스 임팩트
- 사용자 유지율
```

**B5 — 리뷰 주기**

| 주기 | 확인 항목 | 행동 |
|------|----------|------|
| 일간 | Error rate, latency 급등 | 즉시 수정 |
| 주간 | Accuracy 추이, 비용 추적 | 최적화 |
| 월간 | 비즈니스 임팩트 KR | 전략 조정 |
| 분기 | North Star + OKR 연결 검토 | 목표 재설정 |

**B 출력 — KPI Card**

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
| North Star 달성 불가 | 3개월 연속 목표 미달 | 보수적 타겟 재설정 + 분해 트리 막힌 드라이버 파악 |
| Anti-metric 악화 | North Star 최적화 중 다른 지표 급락 | North Star 재정의 (품질 가중치 상향) |
| KPI 정의 불명확 | 팀마다 다른 계산 방식 | formula·data source·collection method 명시 표준화 |
| 임계값 달성 불가 | 첫 주부터 Alert 발동 | 현재 기준선 기반 단계적 목표로 재설정 |
| 팀 정렬 부족 | 개별 KPI만 최적화, North Star 무관 | 월간 North Star 리뷰 고정 + OKR 연결 명시 |

---

## Quality Gate

**Phase A**
- [ ] North Star 후보 3~5개가 평가 매트릭스로 비교되었는가
- [ ] 최종 North Star가 5가지 기준을 모두 충족하는가 (5/5)
- [ ] 분해 트리가 완성되고 각 레버가 팀의 직접 통제 범위인가
- [ ] Anti-metric이 명시되고 악화 임계값이 설정되었는가
- [ ] 현재값 → 3/6/12개월 목표값이 설정되었는가

**Phase B**
- [ ] 운영 건강도 메트릭(Accuracy, Reliability, Latency, CPE)이 정의되었는가
- [ ] 비즈니스 임팩트 메트릭(Time Saved, Cost Saved, Satisfaction)이 정의되었는가
- [ ] 각 KPI에 formula, data source, collection method가 명시되었는가
- [ ] Leading과 Lagging 지표가 분리되었는가
- [ ] 리뷰 주기(일간/주간/월간)와 담당자가 지정되었는가

---

## Examples

### Good Example — `--step both`

```
입력: "고객 지원 에이전트 메트릭 설계해줘"

[Phase A]
🌟 North Star: "월별 정확한 지원 건수"
정의: (월간 집행 건수) × (Accuracy %) × (FCR %)
기준선: 4,000 × 92% × 85% = 3,128건
목표: 3개월 3,500건 / 6개월 4,000건 / 12개월 4,500건
Guardrails: Accuracy > 90% / CPE < $0.15

[Phase B]
운영 건강도: Accuracy 94%→96%, Latency 1.2s→1.0s, CPE $0.08→$0.06
비즈니스 임팩트: Time Saved 8hrs/day, Cost Saved $2,400/month, CSAT 4.2/5.0
리뷰: 일간 alert · 주간 trend · 월간 OKR 연결
```

### Bad Example

```
"Accuracy를 North Star로 하자"

❌ 문제점:
- Composite 부족 — 비용·볼륨 미반영
- Actionable 불명확 — 팀 통제 범위 미정의
- Anti-metric 없음 — Accuracy 99%이지만 비용 폭증 가능
- 분해 트리 없음 — "어떻게 높이나?"에 답 불가
```

---

---

## 관련 기법 — A/B 테스트

정의된 North Star 또는 KPI를 기준으로 에이전트 변경의 통계적 유효성을 검증한다.

**핵심 체크포인트:**
- **MDE 계산 필수**: 샘플 크기 없이 진행한 A/B 결과는 통계적 신뢰도 부족 — 재설계 필요
- **동시 실행**: 순차 실행은 시간대 편향 발생. A/B 병렬 실행 원칙
- **LLM 비결정론 대응**: 같은 입력 5회 반복 실행으로 노이즈 통제
- **Guardrail 메트릭**: Primary 개선에도 안전 지표 악화 시 즉시 중단
- **의사결정 프레임**: Ship B / Keep A / Iterate / Investigate 중 하나로 명문화

A/B 테스트 전체 플로우(가설 수립 → 표본 계산 → 실행 → p-value 분석)가 필요하면 이 스킬에서 확장하거나 별도 운영한다.

---

## 관련 기법 — 코호트 분석

North Star 추이를 버전별·세그먼트별·TK 축적 단계별로 추적한다.

**코호트 분석 방법론:**
- **시간 기반 코호트**: 에이전트 버전 배포 시점 기준 (v1.0 → v1.1 → v2.0)
- **세그먼트 기반**: 내부/외부/API 사용자 그룹별 성능 차이 추적
- **TK 기반 코호트**: TK 축적 수준별 (0~10개 → 11~50개 → 51~100개 → 100+개)

**성능 저하 패턴:**
- Sudden Drop: 모델 API 변경, 외부 데이터 소스 장애 → 즉시 롤백
- Gradual Decline: 데이터 드리프트, 프롬프트 노후화 → 주간 리뷰 + 프롬프트 리프레시
- Cohort-Specific Decline: 세그먼트별 요구사항 차이 → 프롬프트 분기 또는 모델 라우팅

**최소 추적 기간**: 코호트당 4주 이상. 1주 데이터는 노이즈로 간주.
**리텐션 건강 기준**: Week 12 리텐션 > 30% = 건강한 에이전트.

---

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Test Cases
!`cat references/test-cases.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`

---

## Phase C — OKR 설계 (`--step okr` or `--step all`)

### Core Goal

- 에이전트 고유의 성과 측정을 위해 비즈니스 임팩트(시간/비용/오류 절감)와 운영 건강성(정확도/비용/신뢰성)의 2축 OKR 설계
- 측정 가능한 Key Result로 에이전트의 가치를 정량화하고, 주간/월간/분기 리뷰 사이클 수립으로 지속적 개선 추진
- 비용 KR을 항상 포함하여 스케일 시에도 운영 비용이 통제 가능한 범위 내에서 증가하도록 제약

### Trigger Gate (okr only)

- 새로운 에이전트가 배포될 때 초기 성과 목표 설정
- 배포된 에이전트의 분기별 성과 검토 및 다음 분기 OKR 재설정
- 에이전트 포트폴리오의 우선순위 결정이 필요할 때 (KR 달성률로 비교)
- 에이전트 개선 기회 식별 (비용 KR 초과, 정확도 KR 미달 등)

### Instructions (Phase C)

**C1 — 에이전트 Objective 작성**
비즈니스 임팩트 중심의 야심차고 질적인 목표 1개

**C2 — Business Impact KR 2개**
측정 가능한 비즈니스 아웃컴 지표
현재값 → 목표값 → 달성 기한

측정 지표 유형:
- 시간 절감: "PM이 뉴스 수집에 쓰는 시간 주 5시간 → 0시간"
- 비용 절감: "반복 작업 자동화로 월 N시간 × 시급 절감"
- 매출 기여: "리드 발굴 에이전트 → 월 N건 추가 파이프라인"
- 오류 감소: "수동 데이터 입력 오류율 X% → Y%"

**C3 — Operational Health KR 2개**
정확도 / 비용 / 신뢰성 / 레이턴시 중 가장 중요한 2개
현재값 베이스라인 추정 또는 수집 계획

**C4 — 측정 방법 정의**
각 KR을 어떻게 측정할 것인가 (자동/수동, 도구)

**C5 — 리뷰 사이클 설정**
- 주간: 실행 로그 확인 (성공/실패 건수)
- 월간: KR 달성률 리뷰 + 비용 확인
- 분기: Objective 재검토 + 다음 분기 OKR 설정

**OKR 템플릿**

```
O: [에이전트 이름]이 [사용자]의 [문제]를 [방식]으로 해결하는
   신뢰할 수 있는 파트너가 된다.

KR1 (Business Impact):
   [측정 지표] [현재값] → [목표값] by [날짜]

KR2 (Business Impact):
   [측정 지표] [현재값] → [목표값] by [날짜]

KR3 (Operational Health):
   [측정 지표] [현재값] → [목표값] by [날짜]

KR4 (Operational Health):
   [측정 지표] [현재값] → [목표값] by [날짜]
```

### Failure Handling (Phase C)

| 실패 상황 | 감지 | 대응 |
|----------|------|------|
| 비즈니스 임팩트 KR이 측정 불가능 | KR을 읽었을 때 정량화 방법이 불명확 | 프록시 지표로 변경 (예: "사용자 만족도" → "재사용률 80% 이상") |
| 월간 리뷰 시 데이터 부재로 KR 달성률 계산 불가 | 주간 로그가 없거나 측정 도구 설정 안 됨 | 다음 달부터 자동 로깅 설정, 현재 달은 추정값으로 임시 평가 |
| KR이 너무 높게 설정되어 달성 불가능 확실 | 주간 검토 시 KR 달성 가능성 1% 미만 | 즉시 KR 재협상 (낮게 재설정하되, 이유 문서화) |
| 비용 KR 초과 | 비용 모니터링 중 임계값 초과 감지 | 원인 분석 + 즉시 수정 액션 (프롬프트 최적화/도구 호출 감소) |

### Quality Gate (Phase C)

- [ ] Objective: 야심차고 질적인 1개 명시 (Yes/No)
- [ ] Business Impact KR 2개: 시간/비용/오류 절감 중 2개 선택 (Yes/No)
- [ ] Operational Health KR 2개: 정확도/비용/신뢰성/레이턴시 중 2개 선택 (Yes/No)
- [ ] 각 KR: 현재값 → 목표값 → 달성 기한 명시 (Yes/No)
- [ ] 비용 KR 포함 여부 (항상 포함) (Yes/No)
- [ ] 베이스라인 데이터 수집 계획 (처음 2주 이상) (Yes/No)
- [ ] 측정 방법 정의 (자동/수동, 사용 도구) (Yes/No)
- [ ] 리뷰 사이클 설정 (주간/월간/분기) (Yes/No)
