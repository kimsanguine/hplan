---
name: cohort
description: "Track and analyze agent performance by deployment cohort — compare versions, measure retention, and identify degradation patterns over time. Use when monitoring agent releases, tracking version-over-version improvements, or diagnosing performance drift across user segments."
argument-hint: "[agent to analyze cohorts for]"
allowed-tools: ["Read", "Write"]
context: fork
model: sonnet
---

# Agent Cohort Analysis

> 에이전트 코호트 분석 — 버전별, 기간별, 세그먼트별 성능 추적

## Core Goal

- **시간에 따른 성능 변화를 코호트별로 추적** — "지금 좋은가"가 아니라 "시간이 지나면서 어떻게 변하는가" 파악
- **성능 저하 패턴 조기 발견** — 급락, 점진적 하락, 계절성 등 유형별 대응 전략 수립
- **버전 또는 세그먼트 간 성능 비교** — A/B 결과의 장기 유효성과 세그먼트별 차이 정량화

---

## Trigger Gate

### Use This Skill When

- 새로운 에이전트 버전을 배포하고 장기 성능 추세를 추적해야 할 때
- 에이전트 성능이 서서히 떨어지는 신호(Accuracy -2%/주)를 감지했을 때
- 내부/외부/API 세그먼트 간 성능 격차를 분석해야 할 때
- TK 축적 수준에 따른 에이전트 성능 변화를 측정할 때

### Route to Other Skills When

- **agent-ab-test** → A/B 테스트 결과가 코호트로 장기 추적될 필요가 있을 때
- **kpi** → 코호트별 성능 메트릭을 KPI 대시보드에 통합하는 경우
- **incident** → 특정 코호트가 급락했을 때 원인 파악 및 응급 대응 필요
- **reliability** → 성능 저하 원인이 신뢰성 메커니즘 부족으로 의심될 때

### Boundary Checks

- **일시적 변동 vs 진정한 저하** — 1주 데이터로는 판단 불가, 최소 4주 추세 필요
- **코호트 크기 편향** — 샘플 수가 적으면(< 100건) 통계 신뢰도 낮음 → 기간 연장
- **외부 변수 통제** — 성능 변화의 원인이 에이전트인지 입력 데이터 변화인지 구분 필요

---

## 개념

에이전트 코호트 분석은 "지금 성능이 좋은가?"가 아니라 "시간이 지나면서 어떻게 변하는가?"를 추적한다. 모델 업데이트, 프롬프트 변경, 데이터 드리프트가 성능을 서서히 깎을 수 있다. 코호트로 추적하지 않으면 "언제부터 나빠졌는지" 모른 채 사후 대응하게 된다.

## Instructions

You are performing **cohort analysis** for: **$ARGUMENTS**

### Step 1 — Cohort Definition

에이전트 코호트를 정의합니다:

**시간 기반 코호트** (가장 일반적)
```
Cohort = 에이전트 버전 배포 시점
  v1.0 (2024-01 배포) — Baseline
  v1.1 (2024-02 배포) — Prompt 개선
  v1.2 (2024-03 배포) — Model 변경 (Sonnet → Haiku)
  v2.0 (2024-04 배포) — Architecture 변경
```

**세그먼트 기반 코호트**
```
Cohort = 사용자 또는 사용 유형
  Segment A: 내부 사용자 (직원)
  Segment B: 외부 사용자 (고객)
  Segment C: API 연동 (시스템)
```

**TK 기반 코호트** (이 스킬셋 고유)
```
Cohort = TK 축적 수준
  Phase 1: TK 0~10개 (초기)
  Phase 2: TK 11~50개 (도메인 전문가)
  Phase 3: TK 51~100개 (복합 판단)
  Phase 4: TK 100+개 (PM 분신)
```

### Step 2 — Metric Tracking Matrix

| 메트릭 | Cohort 1 | Cohort 2 | Cohort 3 | 추세 |
|--------|----------|----------|----------|------|
| Task Accuracy | | | | ↗/→/↘ |
| Avg Response Time | | | | |
| Token Cost / Task | | | | |
| User Reuse Rate | | | | |
| Escalation Rate | | | | |
| Hallucination Rate | | | | |

**Week-over-Week 비교:**
- 각 코호트의 첫 1주, 4주, 12주 성능 비교
- 같은 코호트 내 시간에 따른 변화 추적
- 코호트 간 같은 시점 성능 비교

### Step 3 — Retention Curve

에이전트 재사용률(리텐션)을 코호트별로 추적합니다:

```
        Week 0  Week 1  Week 2  Week 4  Week 8  Week 12
v1.0    100%    [%]     [%]     [%]     [%]     [%]
v1.1    100%    [%]     [%]     [%]     [%]     [%]
v2.0    100%    [%]     [%]     [%]     [%]     [%]
```

**해석 가이드:**
- Week 1 리텐션 < 40% → 온보딩 문제 또는 초기 품질 부족
- Week 4 리텐션 < 20% → 핵심 가치 미전달
- Week 12 리텐션 > 30% → 건강한 제품 (에이전트 기준)
- 리텐션 곡선이 평탄해지는 지점 = Natural Usage Frequency

### Step 4 — Degradation Detection

성능 저하 패턴을 식별합니다:

**Sudden Drop** (급락)
- 원인: 모델 API 변경, 외부 데이터 소스 장애
- 대응: 즉시 이전 버전 롤백 + 원인 분석

**Gradual Decline** (점진적 하락)
- 원인: 데이터 드리프트, 컨텍스트 윈도우 오염, 프롬프트 노후화
- 대응: 주간 메트릭 리뷰 + 프롬프트 리프레시 주기 설정

**Seasonal Pattern** (주기적 변동)
- 원인: 사용 패턴 변화 (주중/주말, 월초/월말)
- 대응: 정상 범위 설정 + 범위 이탈 시만 알림

**Cohort-Specific Decline** (특정 코호트만 하락)
- 원인: 세그먼트별 요구사항 차이, A/B 테스트 잔류 효과
- 대응: 세그먼트별 프롬프트 분기 또는 모델 라우팅

### Step 5 — Improvement Prioritization

코호트 분석 결과를 개선 액션으로 연결합니다:

```
Priority Matrix:
  Impact (성능 개선 크기) × Reach (영향받는 유저 수) = Priority Score

Action Plan:
  1. [Priority 1]: [action] — 예상 효과: [metric] +[N]%
  2. [Priority 2]: [action] — 예상 효과: [metric] +[N]%
  3. [Priority 3]: [action] — 예상 효과: [metric] +[N]%
```

### Output

```
Cohort Analysis: [agent name]
──────────────────────────────
Cohorts Analyzed: [N]
Best Performing: [cohort] — [primary metric]: [value]
Worst Performing: [cohort] — [primary metric]: [value]
Retention (Week 4): [%]
Degradation Pattern: [type or none]
Top Improvement: [action] — Expected: [metric] +[N]%
Next Review: [date]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **코호트 샘플 부족** | 주간 코호트 < 100건으로 표본 통계학적 신뢰도 낮음 | 추적 기간 연장 또는 코호트 재정의 (월간 코호트로 변경) |
| **급락 탐지 지연** | v1.1 정확도가 -5% 떨어졌으나 4주 후에 발견 | 주간 자동 모니터링 설정 (Accuracy -2%/주 초과 시 알림) → incident 스킬로 전환 |
| **외부 변수 혼동** | 성능 저하가 에이전트 때문인지 입력 데이터 변화 때문인지 불명확 | 입력 데이터 분포 분석 추가, 필요시 A/B 재테스트 |
| **리텐션 해석 오류** | Week 1 리텐션 30%를 "저조"로 판단 → 실은 정상 범위 | 비교 대상(이전 버전, 경쟁사, 업계 표준) 명확화 후 재평가 |
| **계절성 미인식** | 월초 사용량 증가를 "개선"으로 착각 → 월말 급락에 놀람 | 주기적 패턴 학습 후 정상 범위(밴드) 설정 |

---

## Quality Gate

- [ ] 코호트 정의(시간/세그먼트/TK 기반)가 명확한가? (Yes/No)
- [ ] 추적할 메트릭이 일관되게 정의되었는가? (Accuracy, Latency, Cost, Retention 등) (Yes/No)
- [ ] 최소 4주(코호트당 4주) 이상의 데이터를 수집했는가? (Yes/No)
- [ ] 성능 변화의 원인이 에이전트인지 외부 변수인지 분석했는가? (Yes/No)
- [ ] 계절성/주기적 패턴을 인식하고 정상 범위(밴드)를 설정했는가? (Yes/No)
- [ ] 의사결정(Improve/Maintain/Rollback)과 액션 아이템이 명문화되었는가? (Yes/No)

---

## Examples

### Good Example

```
코호트 분석: 고객 지원 에이전트

코호트: 버전별 배포 시점
- v1.0: 2024-01 배포 (Baseline)
- v1.1: 2024-02 배포 (프롬프트 개선)
- v2.0: 2024-04 배포 (아키텍처 변경)

주간 성능 추이 (정확도):

        Week 1  Week 2  Week 4  Week 12
v1.0    92%     91%     90%     88%     → 점진적 하락
v1.1    93%     93%     92%     91%     → 안정적, +1% 개선 유지
v2.0    95%     95%     94%     94%     → 최고 성능 + 안정

분석:
- v1.0: 시간이 지나면서 품질 저하 (프롬프트 노후화 추정)
- v1.1: 점진적 하락 완화 (프롬프트 개선의 장기 효과)
- v2.0: 최고 성능 유지 (아키텍처 개선의 지속적 효과)

액션:
1. v1.0 → v1.1 마이그레이션 가속화
2. v2.0을 프로덕션에서 50% → 100% 트래픽으로 확대
```

### Bad Example

```
"이번 주 정확도가 91%인데 지난주는 92%였네, 뭔가 문제인 것 같다"

❌ 문제점:
- 1주 변동은 노이즈 (정상 범위 내)
- 비교 기준이 불명확 (같은 코호트? 다른 버전?)
- 원인 분석 없음
- 통계적 유의성 확인 안 함
- 즉각 대응(롤백? 최적화?)이 성급함

→ 재작업: 4주 이상 추이 그래프 → 추세선 + 신뢰 구간 → 원인 분석
```

---

### 참고
- 설계자: AI PM Skills Contributors, 2026-03
- TK 기반 코호트: TK-NNN 축적 수준별 성능 변화 추적
- agent-ab-test 스킬과 상호 보완 (A/B 결과 → 코호트 추적)

---

## Further Reading
- Amplitude, "Mastering Retention" — Cohort analysis and retention curve interpretation
- Alistair Croll & Benjamin Yoskovitz, *Lean Analytics* — Cohort metrics for product growth

---

## Test Cases

!`cat references/test-cases.md 2>/dev/null || echo ""`

## Troubleshooting

!`cat references/troubleshooting.md 2>/dev/null || echo ""`

---

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
