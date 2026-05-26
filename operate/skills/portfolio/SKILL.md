---
name: portfolio
description: "에이전트 포트폴리오 관리 — 단일 에이전트 추적(agent-portfolio)과 포트폴리오 전체 리포트(portfolio-report) 통합. 에이전트 상태 카드, 크로스-에이전트 비용 비교, 포트폴리오 헬스 스코어. Use when managing multiple deployed agents."
argument-hint: "[--mode single|report|health]"
allowed-tools: ["Read", "Write", "Edit"]
model: sonnet
---

# Portfolio

> 에이전트 포트폴리오 관리 — T1~T5 티어링, 5축 스코어카드 비교, 주간 롤업 브리프

## Core Goal

- N개 에이전트를 사업 임팩트·신뢰성·운영 비용 기준으로 **T1~T5 5단계 티어링**한다.
- 티어 × 인시던트 가중치로 운영 주의력을 분배해 "어디부터 손볼지" 결정한다.
- **5축 가중 루브릭으로 에이전트 간 단일 비교 점수 생성** — 투자·일몰 의사결정을 객관 데이터로 지원.
- **포트폴리오 헬스를 한 화면에서** — 총 N개, 활성 비율, T1 우선순위 리스트.

---

## Trigger Gate

### Use This Skill When

- 단일 에이전트의 현재 상태 카드가 필요할 때 (`--mode single`)
- 포트폴리오 전체 5축 스코어카드 또는 주간 롤업이 필요할 때 (`--mode report`)
- 포트폴리오 전반의 헬스 스코어와 운영 주의력 분배가 필요할 때 (`--mode health`)
- 운영 중인 에이전트가 5개를 넘어서 단일 에이전트 KPI 뷰로는 우선순위가 안 보일 때
- 분기/월간 포트폴리오 리뷰 미팅 준비할 때
- 예산 삭감 요구가 와서 어떤 에이전트를 sunset 할지 결정할 때

### Route to Other Skills When

- 개별 에이전트 KPI 정의가 우선이면 → `metrics-design`
- 신뢰도 SLO 설계는 → `reliability`
- 비용 단독 분석이 우선일 때 → `ops-review --mode cost`
- 이상치 에이전트에 대한 깊은 장애 분석이 필요할 때 → `incident`

### Boundary Checks

- 이 스킬은 **포트폴리오 메타 뷰**이지 개별 에이전트 진단이 아니다.
- 에이전트 수 < 5면 과중 — `metrics-design`으로 충분하다.
- 티어링은 **사업 영향**을 기준으로 한다. "내가 좋아하는 에이전트"가 아니다.
- Scorecard 가중치 기본값은 **3분 결정 한정**. 본격 운영은 가중치 명시 필요.

---

## 개념

**Tier 정의 (T1~T5)**

| 티어 | 정의 | 운영 주의력 | 예시 |
|---|---|---|---|
| **T1** | 사업 핵심·실시간·고객 직접 노출 | 24/7 모니터, 인시던트 즉시 대응 | 결제 라우터, 고객 응대 1차 |
| **T2** | 사업 중요·매일 실행·내부 의존 | 매일 헬스체크, 4시간 SLA | 데일리 브리핑, 비용 모니터 |
| **T3** | 운영 효율·주기적·내부용 | 주 1회 리뷰 | 주간 회고, 콘텐츠 큐레이션 |
| **T4** | 실험·신규·검증 단계 | 격주 리뷰 + 자체 평가 | 신규 카피라이팅 에이전트 |
| **T5** | 레거시·sunset 후보 | 월 1회 점검, 삭제 후보군 | 사용 빈도 < 월 1회 |

**5축 스코어카드**

| 축 | 정의 | 기본 가중치 |
|---|---|:---:|
| **Accuracy** | 출력이 사양을 충족하는가 (LLM-as-judge / 사람 평가 0~100) | 25 |
| **Reliability** | 실행 성공률 × P95 latency 충족률 | 25 |
| **Cost** | (목표 CPE / 실측 CPE) × 100, 상한 100 | 20 |
| **Velocity** | 정규화 호출 수 × TTV 충족률 | 15 |
| **User Satisfaction** | NPS/CSAT 정규화 점수 (0~100) | 15 |

합계 100. 사업 컨텍스트에 맞게 재배분 가능.

---

## Instructions

You are managing the portfolio for: **$ARGUMENTS**

Parse `--mode` from the arguments:
- `--mode single` → Run Single Agent Status Card only
- `--mode report` → Run Portfolio Report (Scorecard or Rollup)
- `--mode health` → Run Portfolio Health + Tier distribution
- no `--mode` flag → Default to `--mode health`

---

### Single Agent Status Card (`--mode single`)

**Step 1** — 에이전트 기본 정보
- 이름, 담당팀, 활성 여부, 마지막 실행일
- 1줄 정의 + Primary Goal
- 현재 티어 (T1~T5) + 부여 근거 한 줄

**Step 2** — 헬스 시그널
- 마지막 인시던트 일시 및 내용
- 최근 30일 비용 및 실행 건수
- 성공률 (current vs target)

**Output**
```
에이전트: [name]
티어: T[N] — [근거]
상태: 정상/주의/위험
성공률: [%] → Target [%]
월간 비용: $[N]
마지막 인시던트: [날짜] — [내용]
다음 리뷰: [날짜]
```

---

### Portfolio Report (`--mode report`)

**R1 — 스코어카드 (`--view scorecard`)**

에이전트별 5축 점수 산출 및 가중 합산:
```
단일 점수 = Σ(축 점수 × 가중치) / 100
```

의사결정 기준:
| 점수 범위 | 상태 | 행동 |
|:--------:|------|------|
| ≥ 80 | 정상 | 유지 |
| 60~79 | 주의 | 모니터링 강화 |
| < 60 | 위험 | 즉시 개선 또는 sunset 검토 |

**스코어카드 출력**
```
에이전트 스코어카드 — [기간]
가중치: Accuracy [A] / Reliability [R] / Cost [C] / Velocity [V] / Satisfaction [S]

| 에이전트 | Accuracy | Reliability | Cost | Velocity | Satisfaction | 단일점수 | Δ주차 |
|---------|:--------:|:-----------:|:----:|:--------:|:------------:|:--------:|:-----:|
```

**R2 — 주간 롤업 (기본)**

- 티어별 평균 + 전주 Δ
- Top 이동자 (상승 Top-3, 하락 Top-3)
- 이상치 탐지: 단일 점수 < 60, 한 축 ≥30 하락

**롤업 출력**
```
주차: [week-id] (N agents)

티어 평균:
  T1 [avg] (Δ [+/-])
  T2 [avg] (Δ [+/-])
  T3 [avg] (Δ [+/-])
  T4 [avg] (Δ [+/-])
  T5 — (sunset N건)

Top 상승: [agent] +[N], [agent] +[N], [agent] +[N]
Top 하락: [agent] -[N], [agent] -[N], [agent] -[N]

이상치 (< 60): [agent]([score])
이상치 (한 축 ≥30 하락): [agent]([axis] -[N])

운영 권고:
1. [권고 1]
2. [권고 2]
3. [권고 3]
```

---

### Portfolio Health (`--mode health`)

**H1 — 인벤토리**

운영 중 에이전트 전수 목록화 (이름, 담당팀, 활성 여부, 마지막 실행일)

**H2 — 티어 부여**

각 에이전트를 T1~T5 중 하나로 배정. **근거 한 줄 명시** (사업 영향, 호출 빈도, 의존도)

**H3 — 운영 주의력 분배**

- T1 합산 % / T2 합산 % / ... 백분율 계산
- 권장 균형: T1 ≤ 20%, T2 30~40%, T3 30~40%, T4~T5 ≤ 15%
- 균형 벗어나면 조정 권고

**H4 — 헬스 시그널**

각 에이전트의 마지막 인시던트 / 비용 / 호출 수 요약. 티어 가중치 × 인시던트 = 우선순위 점수

**H5 — 포트폴리오 헬스 출력**

- 포트폴리오 헬스 표 (티어별 그룹화)
- 이번 주 운영 주의 권고 Top-3

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 티어 부여 근거가 추상적 ("중요해서 T1") | Step H2 출력 점검 | 사업 영향 수치(매출/비용/사용자 수)로 재정의 |
| T1이 50% 초과 | Step H3 백분율 점검 | 진짜 T1인지 재검토 — 통상 T1은 ≤ 20% |
| 가중치 합이 100이 아님 | R1 스코어카드 검증 | 자동 정규화 + 사용자 확인 요청 |
| 입력 데이터 없음 | 롤업 시 scorecard 산출물 부재 | `--mode report --view scorecard`를 먼저 실행 안내 |
| sunset 후보가 T5에 안 모임 | T5가 비어있음 | 사용 빈도 < 월 1회인 에이전트 명시 → T5 분류 |
| Accuracy LLM-as-judge bias | 평가 대상과 같은 모델 패밀리로 자기 채점 | 채점 모델을 다른 패밀리로 변경 |

---

## Quality Gate

**Health**
- [ ] 모든 활성 에이전트가 정확히 한 티어에 속하는가
- [ ] 각 티어 부여 근거가 수치 기반인가
- [ ] T1 비율이 ≤ 20%인가
- [ ] 운영 주의 권고 Top-3가 명시되었는가

**Scorecard**
- [ ] 가중치 합 = 100
- [ ] 5개 축 모두 측정 방법이 명시되었는가
- [ ] 점수 < 60 에이전트에 대한 권고가 있는가

**Rollup**
- [ ] 모든 활성 에이전트가 롤업에 포함되었는가
- [ ] 티어별 평균 Δ가 표시되었는가
- [ ] 이상치 명단이 표시되었는가

---

## Examples

### Good Example — `--mode health`

```
입력: "운영 중인 에이전트 N개, 여러 팀. 포트폴리오 헬스 확인해줘."

출력:
- T1: 4개 (18%) — 결제, 응대 1차, 인시던트 라우터, 비용 가드
- T2: 8개 (36%) — 데일리 브리핑, 주간 회고 등
- T3: 7개 (32%) — 콘텐츠 큐레이션, 리뷰 봇 등
- T4: 2개 (9%) — 신규 카피라이팅(2주 운영)
- T5: 1개 (5%) — sunset 검토: legacy-summarizer (월 0회 실행)

운영 주의 Top-3:
1. T1 응대 1차 — P99 latency 2배 증가, 즉시 조사
2. T2 데일리 브리핑 — 3일 연속 실패, SLA 임박
3. T5 legacy-summarizer — sunset 결정 필요
```

### Good Example — `--mode report` (rollup)

```
입력: "2026-W19 포트폴리오 리포트 만들어줘."

주차: 2026-W19 (22 agents)
티어 평균: T1 84.2 (Δ +1.5) / T2 76.1 (Δ -2.3) / T3 71.4 (+0.8) / T4 68.0 (-5.0)
Top 상승: daily-brief +12, cost-guard +9, weekly-recap +7
Top 하락: copywriter-exp -18, mail-router -11, news-curator -8
이상치 (< 60): copywriter-exp(54)
이상치 (한 축 ≥30): mail-router(reliability -34)
운영 권고:
1. mail-router reliability 즉시 진단
2. copywriter-exp 4주차 하락 → 승격 보류 검토
3. T2 평균 -2.3 → cost-guard 외 T2 전체 점검
```

---

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
