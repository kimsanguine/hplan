---
name: cost-sim
description: "Simulate and forecast agent operating costs before building. Model token consumption, API call frequency, and monthly burn rate across different models and usage patterns. Use when evaluating agent feasibility, setting cost KPIs, or comparing build vs buy economics. Prevents the 'it's just API calls' cost surprise."
argument-hint: "[agent to model costs for]"
allowed-tools: ["Read", "Write", "WebSearch", "WebFetch"]
model: inherit
hooks:
  Stop:
    - type: command
      command: "bash scripts/validate-cost-sim.sh . 2>/dev/null || true"
---

## Core Goal
- 에이전트 운영 비용을 사전에 시뮬레이션하여 비용 폭탄을 방지한다.
- 토큰/API/외부 서비스 비용을 통합 모델링한다.
- 스케일 시나리오(1→10→100→1,000명)별 비용 곡선을 예측한다.

---

## Trigger Gate

### Use This Skill When
- 에이전트 타당성 평가 시 월간 비용을 추정해야 할 때
- build-or-buy 판단의 비용 축 근거가 필요할 때
- 에이전트 KPI에 비용 상한을 설정해야 할 때
- "이거 비용 얼마 들어?" 류의 질문이 나올 때

### Route to Other Skills When
- 비용이 아닌 모델 성능/품질 기준이면 → `architect/orchestration --pattern router`
- 비용 **추적/최적화**(이미 운영 중)면 → `operate/ops-review`
- 비용이 과다해서 직접 구축 vs 외부 솔루션을 비교한다면 → `discover/assumptions --mode build-or-buy`
- 결정론적 p50/p90 마진 + free-user abuse 시뮬레이션 수치가 필요할 때 → `cogs-sentinel` (hplan plugin)

### Boundary Checks
- 이 스킬은 **사전 시뮬레이션** 전용이다. 실 비용 추적/모니터링은 `operate/ops-review` 범위.
- 모델 가격은 2026-03 기준이며 빠르게 변동함을 항상 명시한다.
- 추정치를 확정 수치로 표현하지 않는다 — 범위(range)로 제시.

---

## Agent Cost Model

에이전트 비용은 일반 SaaS와 완전히 다른 구조입니다.

| 일반 SaaS | 에이전트 |
|---|---|
| 고정 인프라 비용 | 사용량 비례 비용 |
| 서버 × 시간 | 토큰 × 호출 수 × 모델 단가 |
| 예측 가능 | 사용 패턴에 따라 변동 |
| 스케일 시 점진 증가 | 스케일 시 비용 폭발 가능 |

가장 흔한 실수: MVP에서 $5/월이었던 비용이, 사용자 100명에서 $500/월로 폭증.

---

### 비용 구조 3요소

**요소 1 — 토큰 비용 (Token Cost)**

```
Input Cost  = 입력 토큰 수 × 모델별 입력 단가
Output Cost = 출력 토큰 수 × 모델별 출력 단가
Total Token Cost = (Input + Output) × 호출 횟수
```

모델별 단가 (2026-03 기준, 1M 토큰당):

| 모델 | 입력 | 출력 | 특징 |
|---|---|---|---|
| Claude Haiku | $0.25 | $1.25 | 비용 효율, 단순 작업 |
| Claude Sonnet | $3.00 | $15.00 | 균형, 대부분의 작업 |
| Claude Opus | $15.00 | $75.00 | 최고 품질, 복잡한 판단 |
| GPT-4o | $2.50 | $10.00 | 범용 |
| GPT-4o-mini | $0.15 | $0.60 | 저비용 대안 |

> ⚠️ 모델 가격은 빠르게 변동합니다. 실제 계획 시 최신 가격 확인 필수.

**요소 2 — 호출 빈도 (Call Frequency)**

```
일간 호출 수 = 트리거 횟수 × 에이전트당 평균 API 호출 수
월간 호출 수 = 일간 × 30
```

에이전트 유형별 일반적 호출 패턴:

| 유형 | 트리거 빈도 | 회당 API 호출 | 월간 호출 |
|---|---|---|---|
| Cron Agent (1일 1회) | 30/월 | 2~5 | 60~150 |
| Monitor Agent (1시간) | 720/월 | 1~3 | 720~2,160 |
| On-demand Agent | 사용자 의존 | 3~10 | 변동 |
| Orchestrator | 하위 에이전트 수 의존 | 10~50 | 높음 |

**요소 3 — 외부 API 비용 (External API Cost)**

에이전트가 사용하는 외부 서비스 비용:

| 서비스 | 무료 티어 | 유료 단가 |
|---|---|---|
| Brave Search API | 2,000 쿼리/월 | $3/1,000 쿼리 |
| Google Search API | 100 쿼리/일 | $5/1,000 쿼리 |
| Telegram Bot API | 무제한 | 무료 |
| Notion API | 무제한 (개인) | 무료 |
| SendGrid | 100/일 | $0.001/이메일 |

---

### 비용 시뮬레이션 템플릿

```
에이전트: [이름]
모델: [선택]

=== 토큰 비용 ===
평균 입력: [N] tokens/호출
평균 출력: [N] tokens/호출
일간 호출: [N]회
월간 호출: [N]회

입력 비용: [N tokens × N회 × 단가] = $X/월
출력 비용: [N tokens × N회 × 단가] = $Y/월
토큰 소계: $Z/월

=== 외부 API ===
[서비스1]: [호출 수] × [단가] = $A/월
[서비스2]: [호출 수] × [단가] = $B/월
API 소계: $C/월

=== 총 비용 ===
월간: $[Z + C]
연간: $[Z + C] × 12

=== 스케일 시나리오 ===
사용자 1명:   $[현재]
사용자 10명:  $[×10 추정]
사용자 100명: $[×100 추정]
```

---

### 비용 최적화 전략

**전략 1 — 모델 라우팅**
```
모든 작업에 Sonnet을 쓰지 말 것.
단순 분류/추출 → Haiku ($0.25 vs $3.00 = 12배 절감)
복잡한 판단 → Sonnet
최종 검증/고품질 → Opus (필요 시에만)
```

**전략 2 — 캐싱**
```
동일 입력 → 동일 출력인 작업은 캐싱
예: 동일 뉴스 소스를 여러 에이전트가 조회 → 1회 조회 후 공유
절감 효과: 중복 호출 50~80% 감소
```

**전략 3 — 입력 최적화**
```
전체 문서 대신 요약본 입력
10,000 tokens → 2,000 tokens = 80% 입력 비용 절감
→ context-window-budget 스킬과 연계
```

**전략 4 — 배치 처리**
```
실시간 처리 대신 배치 처리
개별 호출 10회 → 1회 배치 호출 (Batch API 50% 할인)
적합: 긴급하지 않은 정기 작업
```

**전략 5 — 비용 상한 설정**
```
월간 비용 상한: $N
초과 시: 에이전트 일시 중지 + 알림
→ metrics-design --step okr의 비용 KR과 연결
```

---

## Project Context (auto-injected)

> 아래 섹션은 스킬 실행 시 자동으로 현재 프로젝트 데이터로 치환됩니다.
> 도구가 설치되지 않은 경우 graceful하게 건너뜁니다.

**프로젝트 메모리:**
!`cat .claude/MEMORY.md 2>/dev/null || echo "프로젝트 메모리 없음 — .claude/MEMORY.md를 생성하면 자동 참조됩니다."`

**최근 API 사용량 (참고용):**
!`cat .claude/usage.json 2>/dev/null || cat logs/api-usage*.log 2>/dev/null | tail -20 || echo "사용량 데이터 없음 — .claude/usage.json 또는 logs/ 디렉토리에 사용량 로그가 있으면 자동 참조됩니다."`

---

## Instructions

You are helping simulate the operating cost for: **$ARGUMENTS**

**Step 1 — 에이전트 프로파일링**
- 에이전트 유형, 트리거 빈도, 사용 모델 확인
- 호출당 평균 입력/출력 토큰 추정

**Step 2 — 토큰 비용 계산**
- 모델별 단가 적용
- 일간/월간/연간 비용 산출

**Step 3 — 외부 API 비용 추가**
- 사용하는 외부 서비스 목록 + 호출 빈도
- 무료 티어 한도 확인

**Step 4 — 총 비용 산출**
- 토큰 + API = 월간 총 비용
- 비용 시뮬레이션 템플릿으로 정리

**Step 5 — 스케일 시나리오**
- 사용자 1 / 10 / 100명 시나리오별 비용 예측
- 비용 폭발 지점 확인

**Step 6 — 최적화 전략 제안**
- 모델 라우팅, 캐싱, 입력 최적화 중 적용 가능한 것 추천
- 예상 절감률 계산

**Step 7 — 비용 KPI 제안**
- 월간 비용 상한 권장값
- `operate/metrics-design --step okr`의 Operational Health KR로 연결

**Step 8 — 다음 단계**
- 비용이 수용 가능 → `deliver/agent-setup`으로 설계
- 비용이 과다 → 모델 다운그레이드 또는 `discover/assumptions --mode build-or-buy` 재검토

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 사용자가 모델/트리거 빈도를 모름 | Step 1에서 필수 입력 누락 | 유형별 기본값 표 제시 후 선택 요청 |
| 외부 API 가격 정보가 변동됨 | 단가 조회 불일치 | "2026-03 기준 추정치"로 명시 + 공식 링크 제공 |
| 스케일 시나리오에서 비선형 비용 증가 | 100명 비용이 1명의 200배 이상 | Orchestrator 호출 폭증 가능성 경고 + 모델 라우팅/캐싱 전략 즉시 제안 |

---

## Quality Gate

- [ ] 비용 시뮬레이션 템플릿이 빠짐없이 작성되었는가 (Yes/No)
- [ ] 스케일 시나리오 3단계(1/10/100명)가 모두 포함되었는가 (3/3)
- [ ] 최적화 전략이 최소 2개 이상 제안되었는가 (Yes/No)
- [ ] 모든 단가에 기준일이 명시되었는가 (Yes/No)
- [ ] 다음 단계 연결(operate/metrics-design --step okr / deliver/agent-setup / discover/assumptions --mode build-or-buy)이 제안되었는가 (Yes/No)

---

## Examples

### Good Example
**요청:** "고객 문의 자동 분류 에이전트 비용 시뮬레이션해줘. Haiku로 하루 200건 처리 예정."

**왜 좋은 요청인가:**
- 에이전트 목적 (고객 문의 분류), 모델 (Haiku), 호출 빈도 (200건/일)가 모두 명확
- 바로 Step 2로 진입 가능

**기대 결과:**
- 토큰 비용: 200건 × 1,500 input tokens × $0.25/1M = ~$0.08/일 → $2.25/월
- 10명 규모: $22.5/월, 100명 규모: $225/월
- 최적화: 입력 요약으로 30% 추가 절감 가능

### Bad Example
**요청:** "에이전트 비용 얼마야?"

**왜 나쁜 요청인가:**
- 에이전트 유형, 모델, 트리거 빈도 전부 불명
- Step 1에서 최소 3개 확인 질문 필요

**올바른 라우팅:**
- cost-sim에서 처리하되, Step 1 프로파일링 질문부터 시작

---

### 참고
- 설계자: AI PM Skills Contributors, 2026-03
- 모델 가격: Anthropic / OpenAI 공식 가격 (2026-03 기준, 변동 가능)
- 모델 라우팅 전략: GPT-5.4 Tool Search 47% 절감 사례에서 영감
- 비용 상한 패턴: production cron job 월간 비용 모니터링 경험 기반

---

## Further Reading
- Anthropic API Pricing — https://docs.anthropic.com/en/docs/about-claude/models
- OpenAI API Pricing — https://openai.com/api/pricing/

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
