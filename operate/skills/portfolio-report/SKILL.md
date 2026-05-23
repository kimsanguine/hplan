---
name: portfolio-report
description: "Generate portfolio-level performance reports for an agent team — 5-axis weighted scorecard comparison or weekly rollup brief with tier averages, top movers, and anomalies. Supports --view scorecard (default: rollup)."
argument-hint: "[agent | 'all' | week-id like 2026-W19] [--view scorecard|rollup]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
model: sonnet
---

# portfolio-report

> 에이전트 포트폴리오 성과 리포트 — 5축 스코어카드 비교 또는 주간 롤업 브리프

## Core Goal

- **5축 가중 루브릭으로 에이전트 간 단일 비교 점수 생성** — 투자·일몰 의사결정을 객관 데이터로 지원
- **주간 포트폴리오를 단일 롤업 브리프로 압축** — 운영팀이 5분 안에 신호만 받게 함
- **티어별 평균·전주 Δ·Top 이동자·이상치를 모두 포함** — 방어 가능한 의사결정 근거 제공

---

## Trigger Gate

### Use This Skill When

- "포트폴리오 주간 리포트 만들어줘" — 주간 운영 리뷰 직전
- "5축 스코어카드 채점해줘" — N개 에이전트 헤드 투 헤드 비교
- "에이전트 팀 성과 정리해줘" — 월간 보고 데이터 빌드업
- 새 가중치·티어 적용 후 첫 주 검증, 일몰 후보 가려낼 때

### Route to Other Skills When

- **metrics-design** → 에이전트 KPI·North Star 자체가 아직 정의되지 않았을 때
- **burn-rate** → 비용 단독 분석이 우선일 때
- **incident** → 이상치 에이전트에 대한 깊은 장애 분석이 필요할 때
- **agent-portfolio** → 티어 미정 에이전트가 있을 때 먼저 실행

### Boundary Checks

- **개인 업무 스케줄 잡아줘** → 이 스킬 범위 밖 (개인 생산성 도구 사용)
- **단순 할 일 목록 만들어줘** → 이 스킬 범위 밖
- Scorecard 가중치 기본값은 **3분 결정 한정**. 본격 운영은 가중치 명시 필요
- Rollup 스킬은 요약이다 — 새로운 점수 계산은 하지 않고, 입력으로 scorecard 결과가 필요

---

## 개념

**Scorecard 뷰**: 에이전트를 5축(Accuracy · Reliability · Cost · Velocity · User Satisfaction)으로 가중 합산하여 0~100 단일 점수를 부여한다. 상대 비교용이며 절대 품질 인증이 아니다.

**Rollup 뷰**: scorecard 결과를 티어별 평균·전주 Δ·Top 이동자·이상치로 집계한다. 운영팀의 주간 의사결정 신호를 5분 안에 전달하는 것이 목적이다.

---

## Instructions

You are generating a portfolio report for: **$ARGUMENTS**

Parse `--view` from the arguments:
- `--view scorecard` → Run Scorecard View only
- `--view rollup` or no `--view` flag → Run Rollup View (default)

---

### Scorecard View (`--view scorecard`)

**S1 — 가중치 결정**

기본 가중치:
| 축 | 정의 | 기본 가중치 |
|---|---|:---:|
| **Accuracy** | 출력이 사양을 충족하는가 (LLM-as-judge / 사람 평가 0~100) | 25 |
| **Reliability** | 실행 성공률 × P95 latency 충족률 | 25 |
| **Cost** | (목표 CPE / 실측 CPE) × 100, 상한 100 | 20 |
| **Velocity** | 정규화 호출 수 × TTV 충족률 | 15 |
| **User Satisfaction** | NPS/CSAT 정규화 점수 (0~100) | 15 |

> 합계 100. 사업 컨텍스트에 맞게 재배분 가능. 조정 시 근거 한 줄 기록.

**S2 — 축별 점수 산출**

각 에이전트 × 5축 = 점수 산출. 결정론적 방법 사용 (LLM-as-judge는 동일 프롬프트·동일 평가셋).

**S3 — 가중 합산**

```
단일 점수 = Σ(축 점수 × 가중치) / 100
범위: 0~100
```

**S4 — 비교 표 출력**

에이전트별 5축 점수 + 단일 점수 + 전주 대비 Δ, 단일 점수 내림차순 정렬.

**S5 — 의사결정 권고**

| 점수 범위 | 상태 | 행동 |
|:--------:|------|------|
| ≥ 80 | 정상 | 유지 |
| 60~79 | 주의 | 모니터링 강화 |
| < 60 | 위험 | 즉시 개선 또는 sunset 검토 |

**Scorecard 출력**

```
에이전트 스코어카드 — [기간]
가중치: Accuracy [A] / Reliability [R] / Cost [C] / Velocity [V] / Satisfaction [S]

| 에이전트 | Accuracy | Reliability | Cost | Velocity | Satisfaction | 단일점수 | Δ주차 |
|---------|:--------:|:-----------:|:----:|:--------:|:------------:|:--------:|:-----:|
| ...     |          |             |      |          |              |          |       |

권고:
- [점수 < 60 에이전트]: 즉시 개선 또는 sunset 검토
- [60~79 에이전트]: 모니터링 강화
```

---

### Rollup View (`--view rollup` or default)

**R1 — 데이터 적재**

이번 주 + 전주 scorecard 결과 로드. 누락 에이전트는 명시.

**R2 — 티어별 평균**

T1~T5 각 티어 단일 점수 평균 + 전주 대비 Δ.

**R3 — Top 이동자**

- 상승 Top-3: Δ 양수, 절대값 큰 순
- 하락 Top-3: Δ 음수, 절대값 큰 순

**R4 — 이상치 탐지**

- 단일 점수 < 60 에이전트 명단
- 한 축이 30 이상 하락한 에이전트 명단

**R5 — 브리프 출력**

4~6줄 요약 + 운영 주의 권고 1~3개.

**Rollup 출력**

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

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| 가중치 합이 100이 아님 | S1 검증 실패 | 자동 정규화 + 사용자 확인 요청 |
| 입력 데이터 없음 | Rollup 시 scorecard 산출물 부재 | scorecard-5axis 또는 `--view scorecard` 먼저 실행 안내 |
| 전주 데이터 없음 (첫 주) | Δ 계산 불가 | "베이스라인 주" 표시 + 다음 주부터 Δ 시작 |
| Top 이동자가 같은 팀에 집중 | 한 팀에서 3개 이상 | 팀 차원 이슈 의심 → cross-team-routing 점검 |
| Accuracy LLM-as-judge bias | 평가 대상과 같은 모델 패밀리로 자기 채점 | 채점 모델을 다른 패밀리로 변경 |
| 이상치 0건인데 전체 점수 낮음 | 평균 낮은데 < 60 없음 | 측정 단위 오류 가능 — scorecard 재검토 |

---

## Quality Gate

**Scorecard**
- [ ] 가중치 합 = 100
- [ ] 5개 축 모두 측정 방법이 명시되었는가
- [ ] 단일 점수가 0~100 범위인가
- [ ] 전주 대비 변화량(Δ)이 표시되었는가
- [ ] 점수 < 60 에이전트에 대한 권고가 있는가

**Rollup**
- [ ] 모든 활성 에이전트가 롤업에 포함되었는가
- [ ] 티어별 평균 Δ가 표시되었는가
- [ ] Top 이동자 상승·하락 각 ≤3개 명시
- [ ] 이상치 명단이 표시되었는가
- [ ] 운영 권고가 1~3개로 압축되었는가

---

## Examples

### Good Example — `--view scorecard`

```
입력: "운영 중 에이전트 8개 이번 주 점수 비교. 비용 민감 사업이라 Cost 가중치 35로 올려줘."

출력:
가중치: Accuracy 20 / Reliability 25 / Cost 35 / Velocity 10 / Satisfaction 10
표: 8개 에이전트 × 5축 + 단일 점수 + Δ주차
권고: cost-monitor 단일점수 56 → 즉시 개선 또는 sunset 검토
```

### Good Example — `--view rollup`

```
입력: "2026-W19 rollup view로 포트폴리오 리포트 만들어줘."

출력:
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

### Bad Example

```
"에이전트들 점수 매겨봐."

❌ 문제점:
- 어떤 뷰인지(scorecard/rollup) 명시 없음
- 가중치 의도 없음
- 입력 데이터 없음 → 환각 점수 위험
```

---

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`

### Measurement Protocols
!`cat references/measurement-protocols.md 2>/dev/null || echo ""`
