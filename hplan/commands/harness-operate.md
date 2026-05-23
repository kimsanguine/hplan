---
description: "Full production operations workflow — KPI dashboard, reliability scan, cost review, improvement planning, knowledge extraction, decision pattern matching, and TK-to-instruction conversion. Use when an agent is live and needs a weekly/monthly operational review, or when running any individual operations step."
argument-hint: "[agent] [--mode kpi|reliability|cost|improve|extract|decide|tk]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /harness-operate

> 에이전트 운영 전체 워크플로우 — 주간/월간 건강 점검 + 개선 계획 + PM 암묵지 추출

## Routing

`$ARGUMENTS`에서 `--mode` 플래그를 파싱한다.

| 플래그 | 실행 범위 |
|--------|-----------|
| `--mode kpi` | KPI 대시보드만 실행 |
| `--mode reliability` | 신뢰성 스캔만 실행 |
| `--mode cost` | 비용 리뷰만 실행 |
| `--mode improve` | 개선 계획만 실행 |
| `--mode extract` | PM 암묵지 추출만 실행 |
| `--mode decide` | 의사결정 패턴 매칭만 실행 |
| `--mode tk` | TK→Instruction 변환만 실행 |
| 플래그 없음 | Phase 1(kpi) → 2(reliability) → 3(cost) → Checkpoint → 4(improve) → 5(extract) 전체 실행 |

플래그 뒤의 나머지 텍스트가 대상 에이전트/시스템입니다.

---

## Instructions

You are running **Production Operations Review** for: **$ARGUMENTS**

---

### Phase 1 — KPI Dashboard (`--mode kpi`)

> **왜**: 에이전트가 배포된 후에도 "잘 작동하고 있는가"를 숫자로 확인해야 합니다.
> 측정하지 않으면 개선도, 문제 감지도 불가능합니다.

두 축의 KPI를 수집하고 이전 기간과 비교한다.
> **KPI (Key Performance Indicator)**: 제품이 목표를 달성하고 있는지 측정하는
> 핵심 지표들입니다. North Star 지표 1개 + 운영 지표 여러 개로 구성합니다.

**Operational KPIs (에이전트 건강)**

| Metric | Value | Target | WoW Δ | Status |
|--------|-------|--------|-------|--------|
| p50 latency (ms) | | < 3,000 | | |
| p99 latency (ms) | | < 10,000 | | |
> **P95/P99**: 100번의 요청 중 95번째/99번째로 느린 응답 시간입니다.
> '평균'이 아닌 '최악의 일반적 경험'을 나타내므로 SLA 설정의 기준이 됩니다.
| Success rate | | > 95% | | |
| Error rate | | < 2% | | |
| HITL escalation rate | | < 10% | | |

**Business KPIs (가치 전달)**

| Metric | Value | Target | WoW Δ | Status |
|--------|-------|--------|-------|--------|
| Task completion rate | | | | |
| User satisfaction (CSAT) | | | | |
| Cost per successful task | | | | |
| MAU / DAU | | | | |
| North Star metric | | | | |
> **North Star 지표**: 팀 전체가 하나로 정렬되는 단 하나의 핵심 지표입니다.
> 모든 의사결정이 이 지표를 개선하는 방향인지 기준으로 삼습니다.

**Status 기준**: 🟢 목표 달성 / 🟡 5–20% 이탈 / 🔴 >20% 이탈 또는 정책 위반

>20% 불리한 변화가 있는 지표는 🔴로 표시한다.

**출력**: 두 KPI 테이블 + 전체 트래픽 라이트 요약 (🟢/🟡/🔴 × 운영/비즈니스)

*`--mode kpi` 선택 시 여기서 종료.*

---

### Phase 2 — Reliability Scan (`--mode reliability`)

> **왜**: 평균 응답 시간이 빠르더라도 일부 요청이 매우 느리거나 실패하면
> 사용자 신뢰를 잃습니다. 최악의 일반적 경험을 측정하고 기준을 세웁니다.

에러 로그와 실패 패턴을 분류한다.

**실패 분류표**

| 카테고리 | 건수 | 심각도 | 이전 기간 대비 추이 |
|---------|------|--------|-----------------|
| Prompt failures (환각, 범위 이탈, 포맷 불일치) | | | |
| Tool failures (API 타임아웃, 인증 오류, rate limit) | | | |
| Data failures (입력 누락, 스키마 불일치, stale context) | | | |
| Logic failures (잘못된 분기, 잘못된 툴 선택, 루프) | | | |

각 카테고리별:
- 건수 및 사용자 가시적 실패 여부
- 이전 기간 대비 증가/감소 추이
- 이번 기간에 처음 등장한 새 실패 유형 → 실패 모드 레지스트리에 추가 제안

**SLA 준수**: 합의된 latency 및 success rate 목표 내에 있는가?

**출력**: 실패 분류표 + SLA 준수 여부 + 신규 실패 유형 목록

*`--mode reliability` 선택 시 여기서 종료.*

---

### Phase 3 — Cost Review (`--mode cost`)

> **왜**: 에이전트 사용량이 늘어날수록 비용도 함께 증가합니다.
> 비용 구조를 정기적으로 확인하지 않으면 수익성이 언제 무너졌는지 알 수 없습니다.

**Burn Rate 분석**
> **Burn Rate (토큰 소진율)**: 에이전트가 LLM API를 호출하며 소비하는 비용의
> 소진 속도입니다. 예산 대비 얼마나 빠르게 소모되는지 추적합니다.

| 항목 | 이번 기간 비용 | 예산 대비 | 이전 기간 대비 |
|------|-------------|---------|------------|
| 총 토큰 비용 | | | |
| MAU당 비용 | | | |
| 성공 태스크당 비용 | | | |
| 모델별 비용 (Opus / Sonnet / Haiku) | | | |

**효율성 신호**:
- 태스크당 비용이 감소 추세이면 ✅ (학습 중)
- 증가 추세이면 ⚠️ (스케일링 문제)

**최대 비용 드라이버**: 전체 지출의 >30%를 차지하는 태스크 타입 또는 사용자 세그먼트는?

**최적화 기회**: 캐싱 / 모델 다운그레이딩 / 프롬프트 압축이 p90 비용을 >15% 줄일 수 있는가?

**출력**: Burn rate 요약 테이블 + 효율성 신호 + 최대 비용 드라이버 + 최적화 기회

*`--mode cost` 선택 시 여기서 종료.*

---

### 🔍 Checkpoint — 상태 평가

*전체 플로우에서만 실행. Phase 3 완료 후 Phase 4 진입 전.*

다음 3가지를 제시하고 사용자 확인을 대기한다:

1. **트래픽 라이트 요약** — 신뢰성 / 비즈니스 / 비용 각각 🟢/🟡/🔴
2. **가장 긴급한 이슈** (1문장)
3. **선택지** — 3가지 중 하나를 선택:
   - A) "개선 계획으로 계속 진행"
   - B) "[특정 지표]를 더 깊이 분석"
   - C) "데이터 불완전 — 추가 컨텍스트 필요"

**사용자 선택 후 결정을 기록하고 진행한다:**

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "operate" \
  --q "운영 리뷰 대응 방향" \
  --options "A: 개선 계획으로 계속|B: [특정 지표] 심층 분석|C: 추가 컨텍스트 수집" \
  --chosen "[사용자가 선택한 옵션 (A/B/C)]" \
  --why "[이유]"
```

**사용자 확인 전 Phase 4 진입 금지.**

---

### Phase 4 — Improvement Planning (`--mode improve`)

Phase 1–3 결과를 기반으로 **90일 액션 백로그**를 작성한다.

**이번 주 (Quick Wins)** — 1–2일 내 완료 가능한 변경:
- 예: "툴 타임아웃에 exponential backoff 재시도 추가"
- 예: "시스템 프롬프트 강화 — 엣지 케이스 X의 환각 감소"

**이번 달 (Structural Fixes)** — 1–2스프린트 필요:
- 예: "모델 라우팅 구현: triage=Haiku, generation=Sonnet"
- 예: "상위 10개 반복 쿼리에 semantic cache 추가"

**이번 분기 (Strategic)** — 아키텍처 결정 필요:
- 예: "단일 에이전트 → Prometheus→Worker 패턴으로 전환"
- 예: "context re-injection 비용 감소를 위한 episodic memory 추가"

각 액션마다: **Impact** (High/Medium/Low) + **Effort** (일 단위) 추정.

**출력**: 주/월/분기 버킷별 액션 목록 + Impact × Effort 매트릭스

*`--mode improve` 선택 시 여기서 종료.*

---

### Phase 5 — Knowledge Extraction (`--mode extract`)

> **왜**: 운영하며 쌓인 판단 패턴과 노하우를 문서화하지 않으면
> 담당자가 바뀌거나 에이전트가 업데이트될 때마다 처음부터 다시 시작합니다.

이번 운영 기간에서 재사용 가능한 PM 암묵지를 추출한다.

#### Step 5-1: Experience Analysis

이번 기간의 핵심 인사이트를 식별한다:
- 잘 된 것 (다음 에이전트에 반복할 패턴): 1–3가지
- 실패한 것 (피해야 할 안티패턴): 1–3가지, 근본 원인 포함

#### Step 5-2: TK Unit 구조화
> **TK (Tribal Knowledge, 부족 지식)**: 경험에서 나온 판단 패턴으로,
> 문서화되지 않은 채 특정 사람에게만 있는 노하우입니다.
> pm-engine은 이것을 에이전트가 런타임에 자동 참조하게 하는 시스템입니다.

각 인사이트를 TK 템플릿으로 포맷한다:

| 항목 | 내용 |
|------|------|
| Name | 기억하기 쉬운 설명적 제목 |
| Type | DP(결정 패턴) / FP(실패 패턴) / HE(휴리스틱) / AP(안티패턴) / IN(인사이트) |
| Context | 이 지식이 적용되는 상황 |
| Activation | 이 지식을 활성화하는 트리거 |
| Deactivation | 적용하지 말아야 할 상황 |
| Core Insight | 핵심 지식 1–2문장 |
| Evidence | 지지하는 경험 또는 데이터 |

#### Step 5-3: Checkpoint

저장 전에 사용자에게 제시:
1. 추출된 TK 유닛 요약 (유형 + 활성화 조건)
2. 옵션: "이대로 저장" / "활성화 조건 다듬기" / "추가 TK 추출"

사용자 확인 후 `pm-engine` 스킬로 PM-ENGINE-MEMORY.md에 추가.

#### Step 5-4: 피드백 대응 방향 결정 (HITL)

실사용자 피드백 또는 운영 데이터를 기반으로 3가지 대응 옵션을 제시하고 선택을 기다린다:

- A) **PRD 수정** — 특정 섹션만 업데이트 (scope 유지)
- B) **재설계** — architect 또는 discover로 재진입 (구조적 문제)
- C) **현행 유지** — 이유 기록 후 다음 리뷰까지 계속

**사용자 선택 후 결정을 기록한다:**

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "operate" \
  --q "실사용자 피드백 대응 방향" \
  --options "A: PRD 수정|B: 재설계 (architect/discover 재진입)|C: 현행 유지" \
  --chosen "[선택된 옵션 (A/B/C)]" \
  --why "[이유]"
```

**A 선택 시 — PRD 버전 업데이트:**

1. 수정 대상 섹션을 명시한다 (예: "Section 3 타겟 사용자, Section 8 에이전트 스펙").
2. `docs/PRD.md` 첫 줄 버전 헤더를 업데이트한다:
   ```
   <!-- hplan PRD | v0.3 | {YYYY-MM-DD} | operate 피드백 반영 -->
   ```
   (이후 사이클이면 v0.4, v0.5 순으로 증가)
3. 버전 업데이트를 기록한다:

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "operate" \
  --q "PRD 버전 업데이트 — operate 피드백 반영" \
  --options "PRD 수정 반영" \
  --chosen "PRD 수정 반영" \
  --why "[수정 섹션 목록 및 피드백 근거]" \
  --prd-version "v0.3"
```

**B 선택 시 — 재설계 재진입:**

`harness/decisions.jsonl`의 기존 결정 이력을 컨텍스트로 포함하여 재진입한다:
- 구조적 문제 → `/harness-plan [system]` (architect 재진입)
- 기회 재정의 필요 → `/harness-discover [idea]` (discover 재진입)

**출력**: `PROMOTED / NO_CANDIDATES` + TK 유닛 목록 + Decision log 항목

*`--mode extract` 선택 시 여기서 종료.*

---

### Phase 6 — Decision Pattern Matching (`--mode decide`)

현재 상황에 PM 결정 패턴 라이브러리를 적용한다.

#### Step 6-1: 상황 분석

- 결정 컨텍스트 명시 (무엇을 결정해야 하는가)
- 이해관계자 및 제약 조건 파악
- 검토 중인 옵션 목록

#### Step 6-2: Pattern Matching (`pm-decision` 스킬)

6가지 핵심 결정 패턴 중 가장 적합한 것을 선택:
- 선택된 패턴 + 적용 근거
- 인지 함정 점검: sunk cost / anchoring / availability bias

#### Step 6-3: Pattern 적용 (`pm-framework` 스킬)

선택된 패턴을 현재 상황에 적용:
- 추론 과정 문서화
- 신뢰도 수준 (High/Medium/Low)과 함께 추천 도출

#### Step 6-4: Knowledge Capture (선택)

새로운 인사이트가 도출된 경우 TK 유닛으로 구조화하여 PM-ENGINE-MEMORY.md에 추가.

**출력**: 결정 로그 (컨텍스트 / 매칭 패턴 / 분석 / 추천 + 신뢰도 / 리스크 + 완화 계획)

*`--mode decide` 선택 시 여기서 종료.*

---

### Phase 7 — TK to Instruction (`--mode tk`)

TK(암묵지) 항목을 에이전트 인스트럭션 조각으로 변환한다.

#### Step 7-1: TK 조회 (`pm-engine` 스킬)

`$ARGUMENTS`에서 TK-NNN 식별자를 파싱한다. 특정 TK가 없으면 선택 가능한 항목 목록 제시.

#### Step 7-2: Instruction 번역 (`pm-framework` 스킬)

TK의 핵심 인사이트를 명령형 인스트럭션 언어로 변환:
- 활성화/비활성화 조건 → if/when 절
- 전문가 수준 지식 → 어떤 모델도 따를 수 있는 인스트럭션

#### Step 7-3: Instruction 포맷

```
## [TK Name] (from TK-NNN)
When [activation condition]:
- [Instruction 1]
- [Instruction 2]
Do NOT apply when [deactivation condition].
Rationale: [Why this matters]
```

#### Step 7-4: Integration 가이드

- 시스템 프롬프트의 어디에 배치할지 제안
- 다른 인스트럭션과의 의존성 명시
- 인스트럭션 검증용 테스트 시나리오 1개

**출력**: 시스템 프롬프트에 붙여넣을 준비된 Instruction Fragment + Integration notes

*`--mode tk` 선택 시 여기서 종료.*

---

## Output Format

**전체 플로우 (플래그 없음)** — Operations Report:

1. **Executive Summary** — 🟢/🟡/🔴 × 신뢰성/비즈니스/비용, 3-bullet 상태
2. **KPI Dashboard** — 두 테이블 + WoW/MoM 변화
3. **실패 분류표** — 상위 3개 에러 카테고리 + 건수
4. **비용 효율** — Burn rate + 최대 비용 드라이버 + 최적화 기회
5. **90일 액션 백로그** — 주/월/분기 버킷 + Impact/Effort
6. **PM 암묵지** — 잘 된 것 / 실패한 것 / TK 승인 수
7. **Decision log** — `continue | pivot | deprecate` + 근거

**개별 --mode**: 해당 Phase의 출력 형식으로만 응답.
