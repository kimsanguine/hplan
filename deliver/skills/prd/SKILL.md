---
name: prd
description: "Write a complete unified PRD covering user/JTBD/decisions/scope/agent-spec/metrics/hypotheses in 14 sections. Single source of truth for both customer-facing products and the LLM agents inside them. Replaces the older 7-section agent-only template. --mode design-shotgun reads §1+§11 from existing PRD and generates harness/design-variants/ (4 HTML variants + comparison.md)."
argument-hint: "[product or agent name] | --mode design-shotgun"
allowed-tools: ["Read", "Write"]
model: sonnet
hooks:
  Stop:
    - type: command
      command: "bash scripts/validate-prd.sh . 2>/dev/null || true"
---

## Project Context (auto-injected)

**프로젝트 메모리:**
!`cat .claude/MEMORY.md 2>/dev/null || echo "프로젝트 메모리 없음."`

**현재 이슈 (Linear/GitHub):**
!`linear issue list --mine --status "In Progress" --limit 5 2>/dev/null || gh issue list --limit 5 --json number,title --jq '.[] | "#\(.number) \(.title)"' 2>/dev/null || echo "이슈 트래커 연결 없음."`

---

## Unified PRD Template — 14 Sections

## Core Goal

- 고객(인간) 대상 제품과 그 안의 LLM 에이전트 사양을 **단일 PRD 14-section**으로 통합
- "사람·문제·결정"이 상단 (1-6), "에이전트·실행 사양"이 중단 (7-11), "지표·가설·실패"가 하단 (12-14)
- 1인 빌더 60일 사이클 + 5명 사랑 검증 + Live URL 도착까지 같은 PRD를 매번 갱신

---

## Trigger Gate

### Use This Skill When

- 새 SaaS·버티컬 앱·1인 빌더 제품의 정식 사양 문서화 (PRD v0.1)
- 5명 사랑 검증 직전 PRD v0.2~v0.3 갱신
- 도메인 특화 제품 (법률·교육·의료) — 사용자 페르소나·JTBD가 핵심
- 내부용 LLM 에이전트 spec — Section 1·3에 페르소나 = 내부 사용자, Section 7-11에 에이전트 상세
- 투자자·파트너·외부 엔지니어에게 제품 사양 공식 전달
- PRD §11 Output Spec 작성 후 UI 변형 4개를 비교해 설계 방향을 결정할 때 → `--mode design-shotgun`

### Route to Other Skills When

- **ICP·beachhead 정의** → `discover/agent-gtm`로 라우팅 후 Section 1에 주입
- **JTBD·Switch Interview** → `discover/agent-gtm`로 라우팅 후 Section 2에 주입
- **결정 옵션 매트릭스** → `discover/build-or-buy` (6축) + `architect/orchestration` (4패턴) + `discover/hitl` (5레벨) → Section 4
- **제외사항 자동 인용** → `hplan/exclusions` 레지스트리 fuzzy match → Section 5
- **MVP 비용 시뮬레이션** → `discover/cost-sim` (lognormal p50/p90) → Section 6
- **Instruction 7요소 상세 설계** → `deliver/instruction` → Section 7 보강
- **OKR 정의** → `operate/metrics-design --step okr` (dual-axis) → Section 12
- **가설 분해** → `discover/assumptions` (4축) → Section 13
- **신뢰성·SLO** → `measure/reliability` → Section 14
- **Multi-ecosystem export** → `hplan/handoff` (Spec-Kit / Kiro / GStack / Claude Code)
- **사용자 인터페이스가 있는 LLM 에이전트 (UI/UX 강제)** → `deliver/respect --mode brief` (RESPECT.md 디자인 시그니처) → Section 11 출력 사양 보강
- design-shotgun 변형 선택 후 TC 자동 생성 → `deliver/qa-checklist`

### Boundary Checks

- PRD 14-section은 "무엇을 하는가"를 명시하지만, "어떻게 기술적으로 구현하는가"는 별도 구현 문서
- 각 섹션은 "5명 사랑 인터뷰에 그대로 쓸 수 있는가? + 엔지니어가 이것만으로 구현 가능한가?" 두 기준으로 검증
- 제외사항(Section 5)이 최소 5개 이상 — "의식적으로 안 만드는 것" 명시
- Section 7-11 (에이전트 사양)은 1인 빌더가 LLM 에이전트를 포함하지 않으면 "N/A — 일반 SaaS"로 간단 표기 가능
- `--mode design-shotgun` 사용 시 `docs/PRD.md` 부재 → fail loud: "docs/PRD.md 없음. /prd [제품명] 먼저 실행하세요."
- `--mode design-shotgun` 사용 시 §11 섹션 부재 → fail loud: "PRD §11 Output Specification 섹션이 필요합니다."

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|----------|------|------|
| ICP가 "20-50대 일반인" 같이 추상적 | Section 1 검토 시 beachhead 5-criteria 통과 못 함 | `discover/agent-gtm` 라우팅으로 ICP 재정의 |
| JTBD가 솔루션 어조 ("편하게 X 할 수 있다") | Section 2가 Job이 아닌 Feature 설명 | Switch Interview 4 Forces (Push·Pull·Anxiety·Habit)로 재작성 |
| 결정 옵션 매트릭스가 옵션 1개만 | Section 4에 옵션 A/B/C 중 하나만 | 최소 2개 옵션 + 트레이드오프 강제. `discover/build-or-buy` 호출 |
| 제외사항 비어 있음 | Section 5 빈 칸 | "절대 안 만드는 것 5개" 강제 입력. `hplan/exclusions` 자동 인용 |
| MVP·Full vision 분리 없음 | Section 6에 Now/Next/Later 구분 없음 | 3-tier 분할 + 각 tier에 cogs p50/p90 첨부 |
| Anti-Goals 없음 | Section 7에 "하면 안 되는 것" 없음 | 최소 3개 강제. 도메인 룰·hallucination 정책·법적 책임 영역 포함 |
| Tools 호출 제한 없음 | Section 8 일부 행에 "호출 제한" 컬럼 빈 칸 | `deliver/instruction` 라우팅으로 도구별 상세 조건 정의 |
| Trigger 모호 ("필요 시") | Section 10 트리거 유형 미지정 | Cron/Event/Manual/Pipeline 중 명시적 선택 |
| Output 예시 없음 | Section 11 출력 샘플 칸 빈 칸 | 실제 출력 1개 작성 강제 (Markdown / JSON / Plain text) |
| 성공 지표가 추정·동기 부재 | Section 12에 측정·기한 없음 | `operate/metrics-design --step okr` 라우팅으로 Dual-axis 재작성 |
| 검증 가능 가설 없음 | Section 13에 가설 0개 | `discover/assumptions`로 top-3 + 2-day experiment 강제 |
| HITL 트리거 모호 | Section 14에 "사용자 확인" 같이 추상 | 구체적 임계값·이벤트로 재정의 (예: 충실성 < 0.7) |
| `docs/PRD.md` 부재 (`--mode design-shotgun`) | `ls` 실패 | fail loud + "/prd 먼저" 후 종료 |
| §11 부재 (`--mode design-shotgun`) | 섹션 추출 없음 | fail loud + "PRD §11 필요" 후 종료 |
| §1 부재 (`--mode design-shotgun`) | 섹션 추출 없음 | WARN + ICP 적합도 평가 생략, 계속 진행 |

---

## Quality Gate

- [ ] Section 1: ICP 1줄 + 페르소나 2~3개 + 도달 채널 (Yes/No)
- [ ] Section 2: JTBD 1~3개 + Switch 4 Forces (Yes/No)
- [ ] Section 3: 핵심 문제 1~3개 + "10배 가치" 정량 (Yes/No)
- [ ] Section 4: 결정 옵션 매트릭스 (최소 2개 옵션·트레이드오프) (Yes/No)
- [ ] Section 5: 제외사항 5개 이상 (Yes/No)
- [ ] Section 6: Now/Next/Later + cogs p50/p90 (Yes/No)
- [ ] Section 7: Role + Primary Goal + Anti-Goals 3개 이상 (Yes/No)
- [ ] Section 8: Tools + 사용 조건 + 호출 제한 (Yes/No)
- [ ] Section 9: 3-tier 메모리 (Working / Long-term / Procedural) (Yes/No)
- [ ] Section 10: 트리거 유형 + 실행 흐름 Step-by-Step (Yes/No)
- [ ] Section 11: 채널/형식/길이/언어/톤 + 출력 샘플 (Yes/No)
- [ ] Section 12: OKR + North Star + Anti-Metric + Cost KR mandatory (Yes/No)
- [ ] Section 13: Top-3 가설 + 2-day experiment 링크 (Yes/No)
- [ ] Section 14: 실패 시나리오 (4개 이상) + HITL 트리거 (Yes/No)
- [ ] 디자인 시그니처 commit: UI/UX 있으면 `deliver/respect --mode brief` 호출 + RESPECT.md 참조, 없으면 "N/A — 백엔드만" 명시 (Yes/No/N/A)
- [ ] 전체 일관성: 섹션 간 충돌·누락 없음 (Yes/No)
- [ ] TK 인용: `learn/pm-engine` 쿼리로 관련 TK-NNN 3~5개 (Yes/No)
- [ ] `--mode design-shotgun`: docs/PRD.md 부재 시 즉시 종료
- [ ] `--mode design-shotgun`: §11 부재 시 즉시 종료
- [ ] `--mode design-shotgun`: 4개 HTML 변형 + comparison.md 생성됨
- [ ] `--mode design-shotgun`: 각 HTML 파일에 §11 해석 주석 포함

---

## Unified PRD 14-section 구조

> **상단** = 사람·문제·결정 (Section 1~6) → 비즈니스가 읽음
> **중단** = 에이전트·실행 사양 (Section 7~11) → 엔지니어가 읽음
> **하단** = 지표·가설·실패 (Section 12~14) → PM이 매주 갱신

---

### Section 1 — 사용자 / ICP / 페르소나

```
ICP (Ideal Customer Profile):
[한 줄 정의 — beachhead 5-criteria 통과]

페르소나 (2~3개):

### 페르소나 A. [이름·역할]
- 하루 일과:
- 핵심 고통 (top 3):
- 현재 대안:
- 도달 채널 (verified):
```

> 자동 호출: `discover/agent-gtm` beachhead 5-criteria 결과 inject

**이해관계자 영향도 매트릭스 (조직 도입 시 선택):**

에이전트가 조직 전체에 영향을 미치거나 여러 팀 합의가 필요한 경우, 페르소나 이후 아래 항목을 추가한다.

| 이해관계자 그룹 | Power (1-5) | Interest (1-5) | 전략 | 핵심 메시지 |
|---|---|---|---|---|
| 경영진 (C-Level) | | | Engage Actively | ROI + 리스크 대비책 |
| 직접 사용자 | | | Engage Actively | 반복 작업 해방 |
| 엔지니어링 | | | Manage Closely | 깔끔한 아키텍처 + 소유권 |
| 법무/컴플라이언스 | | | Keep Informed | HITL + 감사 로그 |
| 운영/CS | | | Keep Informed | 안정성 + 에스컬레이션 경로 |
| 재무 | | | Keep Informed | 비용 예측 가능성 + ROI |

주요 저항 유형: Job Threat("내 일 대체") → Co-pilot 포지셔닝 / Trust Deficit("AI 믿을 수 없다") → Shadow Mode 검증 / Control Loss("통제 못 함") → HITL 설계

---

### Section 2 — JTBD (Jobs To Be Done)

```
핵심 Job (1~3개):

### Job-1: [상황]에서 [목표]를 달성하고 싶다, 그래서 [성공 기준]
- Push (현 상태 불만):
- Pull (새 솔루션 매력):
- Anxiety (도입 불안):
- Habit (기존 습관 관성):
```

> 자동 호출: `discover/agent-gtm` Switch Interview 산출물

---

### Section 3 — 핵심 문제 + 해결할 가치

```
문제 (top 1~3 — 절실히 이해):
1. [페르소나]는 [상황]에서 [고통] — 매일 N시간 또는 ₩M 손실

해결 방식 (워크플로우, 솔루션 X):
[본 제품이 풀어주는 흐름 — 일하는 방식이 어떻게 바뀌는가]

10배 가치 (정량):
- 시간: [Before] N시간 → [After] N분 (M배)
- 돈: [Before] ₩M → [After] ₩K (M배)
- 또는: 새로 가능해지는 것
```

---

### Section 4 — 결정 옵션 매트릭스

```
| 결정 항목 | 옵션 A | 옵션 B | 옵션 C | 선택 | 트레이드오프 | 재검토 시점 |
|---------|--------|--------|--------|------|-------------|------------|
| RAG 인프라 | Supabase pgvector | ChromaDB | Pinecone | A | Cloud 한 스택 vs 로컬 자유도 | 100명 |
| 결제 | Paddle MoR | Stripe | Lemon Squeezy | A | 사업자 등록 vs 직접 통합 | 1,000명 |
| Orchestration | Sequential | Parallel | Router | A | 디버깅 vs 속도 | Wave 2 |
| HITL 레벨 | L2 (suggest) | L3 (approve) | L4 (autonomous) | L3 | 안전성 vs 속도 | 5명 사랑 후 |
```

> 자동 호출: `discover/build-or-buy` + `architect/orchestration` + `discover/hitl`

---

### Section 5 — 제외사항 (Out-of-Scope)

```
의식적으로 안 만드는 것 (최소 5개):

1. ❌ [기능 X] — 이유: [왜 안 만드나, 한 줄]
2. ❌ [기능 Y] — 이유:
3. ❌ ...
4. ❌ ...
5. ❌ ...

재검토 신호:
- [언제 이 제외 결정을 다시 볼 것인가]
```

> 자동 호출: `hplan/exclusions` 레지스트리 fuzzy match top-10

---

### Section 6 — MVP 범위 / Full vision

```
### Now (Wave 1, Day 1~60) — 5명 사랑 도달
- 핵심 기능 3~5개 (이것 없이 5명 사랑 불가능)
- cogs (p50): $___ / 사용자 / 월
- cogs (p90): $___ / 사용자 / 월
- Live URL 도착: Day 60

### Next (Wave 2, Day 61~120) — 5명 → 30명
- 확장 기능 3~5개
- cogs (p50): $___ / 사용자 / 월

### Later (Wave 3, Day 121+) — 30명 → 100명+
- 확장 기능
- cogs (p50): $___ / 사용자 / 월
```

> 자동 호출: `discover/cost-sim` (p50/p90 lognormal)

---

### Section 7 — Role + Primary Goal + Anti-Goals

> 본 제품이 LLM 에이전트를 포함하면 작성. 일반 SaaS면 "N/A"

```
Role:
[에이전트의 역할 정의 — 1~3문장]

Primary Goal:
[단 하나의 핵심 목표]

Secondary Goals:
1.
2.

Anti-Goals (하면 안 되는 것, 최소 3개):
1. [도메인 룰 — 예: 변호사 책임 영역 hallucination 금지]
2. [데이터 정책 — 예: 사용자 데이터 외부 전송 금지]
3. [법적 책임 — 예: 의료 진단 대체 금지]
```

> 자동 호출: `deliver/instruction` 7요소 상세 설계

---

### Section 8 — Tools & Integrations

```
| 도구/API | 용도 | 사용 조건 | 호출 제한 |
|---------|------|---------|---------|
| OpenAI text-embedding-3-small | 벡터 임베딩 | 새 문서 ingest 시 | 1회/문서 |
| Supabase pgvector | 유사도 검색 | 사용자 쿼리 시 | 무제한 |
| Paddle API | 결제·세금 | 구독 가입·해지 | 이벤트 기반 |
| Channel Talk API | CS 응답 | 사용자 메시지 | 1회/메시지 |
```

최소 권한 원칙: 필요한 도구만 포함, 각 도구 사용 범위 명시

---

### Section 9 — Memory & Context Design

```
Working Memory (컨텍스트):
- 항상 로드: [시스템 프롬프트, 도메인 룰, 사용자 컨텍스트]
- 조건부 로드: [관련 문서 top-5 from RAG]
- 컨텍스트 예산: [최대 N tokens]

Long-term Memory (DB / 파일):
- 읽기: [사용자별 누적 데이터 위치]
- 쓰기: [언제 무엇을 저장]
- 저장 트리거: [세션 종료 / 사용자 액션]

Procedural Memory (Skills):
- [참조하는 도메인 SKILL.md 목록]
```

**컨텍스트 예산 가이드 (토큰 추정 기준):**

| 모델 | 최대 컨텍스트 | 실용적 한도 |
|---|---|---|
| Haiku | 200k tokens | 40k (비용 효율) |
| Sonnet | 200k tokens | 80k (균형) |
| Opus | 200k tokens | 100k (품질 우선) |

토큰 추정: 마크다운 1KB ≈ 250~350 tokens, 코드 1KB ≈ 200~300 tokens, JSON 1KB ≈ 150~250 tokens

임계값: 70% 미만 정상 / 70~85% 경고(새 파일 로드 최소화) / 85%+ 위험(조건부 항목 제외)

필수/조건부/제외 분류: 항상 로드(SOUL+USER+최근 메모리)·조건부 로드(MEMORY, 도메인 SKILL)·제외(오래된 파일·원문 전체)로 구분하고 총 예산의 40% 이상을 출력+추론용으로 확보한다.

---

### Section 10 — Trigger & Execution Flow

```
트리거 유형:
☐ Cron (주기적) — 스케줄:
☐ Event-Driven — 이벤트:
☐ Manual — 조건:
☐ Pipeline — 선행 에이전트:

실행 흐름:
Step 1: [입력 수집]
Step 2: [처리]
Step 3: [출력 생성]
Step 4: [전달/저장]

예상 실행 시간: [초/분]
타임아웃 설정: [초]
```

---

### Section 11 — Output Specification

```
출력 채널: [Web UI / Telegram / 이메일 / API]
출력 형식: [Markdown / Plain text / JSON / 구조화 텍스트]
출력 길이: [최대 N자 / N줄]
언어: [한국어 / 영어]
톤: [간결 / 상세 / 브리핑 / 대화형]

출력 예시:
---
[실제 출력 샘플 작성]
---
```

---

### Section 12 — 성공 지표 통합 (Dual-axis)

```
North Star Metric:
[단 하나 가장 중요한 지표 — 사용자 가치와 직결]

Business KRs (3~5개):
1. DAU / WAU / MAU
2. MRR / ARR
3. 리텐션 D7 / D30
4. NPS
5. Sean Ellis 40% — "더 이상 못 쓰면 매우 실망"

Operational KRs (3~5개, mandatory cost KR 포함):
1. TTV (Time To Value) ≤ 5분
2. 도메인 충실성 ≥ 0.85
3. 에이전트 응답 시간 p95 ≤ 3초
4. 월 cogs / 사용자 ≤ $___
5. 에러율 ≤ 1%

Anti-Metric (이 지표가 오르면 위험):
[예: 평균 세션 시간이 30분 넘으면 사용자가 길을 잃은 것]
```

> 자동 호출: `operate/metrics-design --step all` (dual-axis)

---

### Section 13 — 검증 가능 가설 박스

```
Top-3 가설 (Value/Feasibility/Reliability/Ethics 4축):

### 가설 H-1 (Value)
- 가설: [if X then Y because Z]
- 측정: [어떻게 측정]
- 임계값: [통과 기준]
- 2-day experiment: [실험 설계]
- 결과: [통과 / 실패 / 진행 중]

### 가설 H-2 (Feasibility)
...

### 가설 H-3 (Reliability)
...
```

> 자동 호출: `discover/assumptions` (4축 분해 + 2-day experiment)

---

### Section 14 — 실패 모드 + Human-in-the-loop

```
실패 시나리오 매트릭스 (최소 4개):

| 시나리오 | 감지 | 대응 | 사용자 영향 |
|---------|------|-----|------------|
| 도메인 RAG 충실성 < 0.7 | Eval suite | Fallback to GPT + 경고 | 낮음 |
| 결제 API 실패 | HTTPError | 3회 재시도 → 대안 결제 안내 | 중간 |
| 한국어 판례명 잘못 인식 | 사용자 신고 | admin 알림 + roll back | 높음 |
| 데이터 유출 의심 | 비정상 access | 즉시 차단 + audit log | Critical |

Human-in-the-loop 트리거:
- 도메인 충실성 < 0.7 → 사용자 확인 요청
- 결제 분쟁 → admin escalation
- 법률·의료 등 high-stakes → 항상 사용자 확인
```

---

## `--mode design-shotgun` — §11 시각화 변형 생성

`docs/PRD.md`의 §1 ICP + §11 Output Specification을 파싱해
`harness/design-variants/` 에 HTML 변형 4개와 비교 문서를 생성한다.

---

### Rule 5 준수

| 판단 | 도구 | LLM |
|---|---|---|
| PRD 파일 존재 여부 | ls/Read | ❌ |
| §1·§11 섹션 추출 | 텍스트 파싱 | ✅ (비정형 추출) |
| 4개 HTML 변형 생성 | — | ✅ (자연어 생성) |
| comparison.md 적합도 평가 | — | ✅ (판단 설명) |
| 파일 저장 | Write | ❌ |

---

### Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| ICP 정의 + 핵심 고통 | `docs/PRD.md` §1 | 변형 적합도 판단 기준 |
| 출력 채널·형식·톤 | `docs/PRD.md` §11 | 4개 변형의 공통 기반 |

---

### Instructions (--mode design-shotgun)

**Step 1 — PRD 로드 및 섹션 추출**

```bash
ls docs/PRD.md 2>/dev/null || echo "PRD_MISSING"
```

PRD_MISSING 시:
```
❌ 에러: docs/PRD.md 없음.
/prd [제품명] 먼저 실행하세요.
```
즉시 종료.

`docs/PRD.md` Read → §1 (ICP / 페르소나) + §11 (Output Specification) 추출.
§11 부재 시:
```
❌ 에러: PRD §11 Output Specification 섹션이 필요합니다.
```
즉시 종료.

**Step 2 — 출력 디렉터리 준비**
```bash
mkdir -p harness/design-variants
```

**Step 3 — 4개 HTML 변형 생성**

각 변형은 §11을 다르게 해석한 것이다. 변형 패턴:

| 변형 | §11 해석 전략 | ICP 적합 상황 |
|---|---|---|
| Variant A | 단계 명시 (스텝퍼/탭) — 순서와 진행 상태 강조 | 처음 사용하는 ICP, 학습 비용이 있는 플로우 |
| Variant B | 컨텍스트 보존 (모달/오버레이) — 현재 화면 유지 | 비교·참조가 필요한 ICP, 중단 후 재개 빈번 |
| Variant C | 단순 직선 (미니멀) — 핵심 입력/출력만 | 반복 사용 ICP, 숙련 사용자 |
| Variant D | 프로그레시브 공개 — 기본 옵션 → 고급 옵션 순차 노출 | 입문자+숙련자 혼재 ICP |

각 `harness/design-variants/variant-[A-D].html` 파일은:
- 순수 HTML + 인라인 CSS만 사용 (외부 CDN, JS 프레임워크 금지)
- 파일 상단 주석에 §11 해석 명시:
  ```html
  <!--
    Variant A — §11 해석: [어떤 §11 스펙 부분을 어떻게 해석했는가]
    ICP 적합 시나리오: [어떤 페르소나에 맞는가]
    TC 후보: [이 변형에서 테스트해야 할 시나리오 2개]
  -->
  ```
- 실제 제품 와이어프레임 수준의 HTML 마크업 (더미 텍스트 OK, 구조는 §11 반영)
- 색상: 회색 팔레트 (설계 결정이 아니라 레이아웃 집중)

**Step 4 — comparison.md 생성**

`harness/design-variants/comparison.md`:

```markdown
# Design Variants — [제품명]
생성: YYYY-MM-DD | 소스: docs/PRD.md §1 + §11

## §11 Output Spec 요약
[추출된 §11 핵심 내용 3-5줄]

## ICP 요약 (§1)
[추출된 ICP 핵심 1-2줄]

## 변형 비교

| 변형 | §11 해석 | ICP 적합도 | 주요 TC 후보 | 선택 시 주의점 |
|---|---|---|---|---|
| Variant A | ... | ★★★☆☆ | ... | ... |
| Variant B | ... | ★★☆☆☆ | ... | ... |
| Variant C | ... | ★★★★☆ | ... | ... |
| Variant D | ... | ★★★☆☆ | ... | ... |

## 권장 변형
[ICP 기준으로 가장 적합한 변형 + 이유 2-3줄]

## 다음 단계
1. 변형 선택 후 → `deliver/qa-checklist` 로 해당 변형 TC 생성
2. TC 생성 후 → `deliver/ui-validate --check tc-gate [URL]` 로 증거 수집
```

**Step 5 — 완료 출력**
```
✅ harness/design-variants/ 생성 완료
   Variant A: variant-A.html (스텝퍼/탭 방식)
   Variant B: variant-B.html (컨텍스트 보존 방식)
   Variant C: variant-C.html (미니멀 직선 방식)
   Variant D: variant-D.html (프로그레시브 공개 방식)
   비교: comparison.md

   → comparison.md를 검토하고 변형을 선택한 후 /qa-checklist 를 실행하세요.
```

---

### Failure Handling (--mode design-shotgun)

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| `docs/PRD.md` 부재 | `ls` 실패 | fail loud + "/prd [제품명] 먼저" 후 종료 |
| §11 부재 | 섹션 추출 결과 없음 | fail loud + "PRD §11 필요" 후 종료 |
| §1 부재 | 섹션 추출 결과 없음 | WARN (FAIL 아님) + "§1 없이 ICP 적합도 평가 생략" 후 계속 |
| `harness/` 부재 | `ls` 실패 | `mkdir -p harness/design-variants/` 후 진행 |

---

### Quality Gate (--mode design-shotgun)

- [ ] PRD 부재 시 즉시 종료, 변형 생성 금지
- [ ] §11 부재 시 즉시 종료
- [ ] 4개 변형 파일 모두 생성됨 (variant-A~D.html)
- [ ] 각 HTML 파일에 §11 해석 주석 포함
- [ ] 외부 CDN / JS 프레임워크 없음 (순수 HTML+인라인 CSS)
- [ ] comparison.md에 권장 변형 명시됨
- [ ] comparison.md에 다음 단계(qa-checklist → tc-gate) 안내 포함

---

### Examples (--mode design-shotgun)

#### Good Example
**입력:** `--mode design-shotgun` (docs/PRD.md 존재, §1·§11 있음)

**기대 동작:**
1. PRD §1 ICP + §11 Output Spec 추출
2. 4개 HTML 변형 생성 (harness/design-variants/)
3. comparison.md 작성 (ICP 적합도 평가 포함)
4. 완료 통계 출력

#### Bad Example
**입력:** `--mode design-shotgun` (docs/PRD.md 없음)

**기대 동작:**
```
❌ 에러: docs/PRD.md 없음.
/prd [제품명] 먼저 실행하세요.
```
실행 중단.

---

## Instructions

You are helping write a complete **Unified PRD** for: **$ARGUMENTS**

**Phase 1** — Section 1-3 (사람·문제·가치)
- Section 1: ICP·페르소나 — `discover/agent-gtm` 호출 (beachhead 5-criteria)
- Section 2: JTBD·Switch 4 Forces
- Section 3: 핵심 문제 + 10배 가치 (정량)

🔍 Checkpoint 1: User 검증 — "ICP·JTBD·문제가 5명 사랑 인터뷰에 그대로 쓸 수 있는가?"

**Phase 2** — Section 4-6 (결정·범위)
- Section 4: 결정 옵션 매트릭스 — `discover/build-or-buy` + `architect/orchestration` + `discover/hitl`
- Section 5: 제외사항 — `hplan/exclusions` 자동 인용
- Section 6: Now/Next/Later — `discover/cost-sim` (cogs p50/p90)

🔍 Checkpoint 2: User 검증 — "MVP가 60일 안에 가능한가? cogs가 1인 빌더 감당 가능한가?"

**Phase 3** — Section 7-11 (에이전트·실행 사양)
- Section 7: Role + Anti-Goals — `deliver/instruction` 호출
- Section 8: Tools & Integrations + 호출 제한 mandatory
- Section 9: 3-tier Memory (Working / Long-term / Procedural)
- Section 10: Trigger & Execution Flow Step-by-Step
- Section 11: Output Specification + 실제 예시 1개
- Section 11 보강 (UI 있으면): `deliver/respect --mode brief` 호출 → RESPECT.md 디자인 시그니처 commit (3초 룰 / 다음 행동 / social proof)

> 일반 SaaS (LLM 에이전트 없음) 이면 Section 7-11에 "N/A — 일반 SaaS" 간단 표기 가능
> 사용자 인터페이스가 없는 백엔드 에이전트면 디자인 시그니처는 "N/A — 백엔드만" 명시

**Phase 4** — Section 12-14 (지표·가설·실패)
- Section 12: Dual-axis OKR — `operate/metrics-design --step okr` (cost KR mandatory)
- Section 13: Top-3 가설 — `discover/assumptions` + 2-day experiment
- Section 14: 실패 모드 (4개 이상) + HITL 트리거

**Phase 5** — PRD 통합 & TK 인용
- `learn/pm-engine` 쿼리로 관련 TK-NNN 3~5개 인용 (각 섹션 하단에 시드)
- Quality Gate 16개 항목 (14 섹션 + 일관성 + TK 인용) 모두 통과 확인
- `docs/PRD.md`에 저장

---

## Further Reading
- Marty Cagan, *INSPIRED* — Discovery before delivery
- Bob Moesta, *Demand-Side Sales* — Switch Interview / JTBD
- Sean Ellis, *Hacking Growth* — 40% PMF Rule
- Marc Andreessen, *Pmarchive 2007* — "The Only Thing That Matters" PMF

## Contextual Knowledge (auto-loaded)

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
