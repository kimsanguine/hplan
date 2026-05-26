---
name: brainstorm
description: "Phase 0 Worth-Building Check + Phase 1 대화형 설계 + Phase 2 Signal Gate Bootstrap. 아이디어를 validated 설계 문서로 전환. deliver/prd 스킬 진입 전 필수 단계. 3문 PROCEED/WARN 판정으로 만들 가치를 먼저 확인한다."
argument-hint: "[아이디어 또는 문제 설명]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# /hplan:brainstorm — Validated Brainstorming

Running for: **$ARGUMENTS**

## Core Goal

superpowers:brainstorming과 달리 Phase 0 Worth-Building Check를 먼저 실행해
"만들어야 하는가"를 확인한 뒤 설계 대화를 시작한다.

출력이 설계 문서 1개가 아니라 설계 문서 + Signal Gate Bootstrap 3개 artifact다.

- **Phase 0**: Worth-Building Check — 3문 PROCEED/WARN 판정
- **Phase 1**: 대화형 설계 — 1문 1답, 2-3 접근 방식 비교
- **Phase 2**: Signal Gate Bootstrap — `harness/pain.md` 씨앗 + 가정 목록 + PRD §1 초안

---

## Trigger Gate

### Use This Skill When

- 새 제품·기능·에이전트 아이디어가 있고 설계 전에 검증이 필요할 때
- discover/opp-tree 이전에 빠른 worth-building check가 필요할 때
- deliver/prd 스킬 작성 전 §1 ICP 초안과 §13 가설 씨앗을 미리 준비하고 싶을 때

### Route to Other Skills When

- Phase 0에서 PROCEED → 이 스킬의 Phase 1-2 계속
- Phase 2 완료 후 → `deliver/prd` 스킬로 handoff
- Phase 0에서 WARN이고 깊은 증거 수집 필요 → `discover/opp-tree` + `discover/assumptions`
- 이미 ICP와 문제가 명확히 정의됨 → `deliver/prd` 직접 시작

### Boundary Checks

- Phase 0의 3문은 차단이 아닌 방향 안내다. WARN = "지금 당장 discover 먼저 권장"이지 STOP이 아님
- Phase 2 출력물은 AI 생성 초안이다. 실제 Signal Gate 증거가 아님 — 실제 인터뷰·관찰로 보강 필요
- 이 스킬은 설계까지만. 구현 시작 판단은 harness-build를 통해서.

---

## Instructions

You are running `/hplan:brainstorm` for: **$ARGUMENTS**

### Phase 0 — Worth-Building Check

superpowers에 없는 단계. 3문 이하의 질문으로 "만들 가치가 있는가"를 빠르게 확인한다.

아래 3개 질문을 한 번에 하나씩 대화형으로 묻는다:

**Q1**: "이 문제를 경험한 실제 사람이 특정되나요? (이름·역할·상황을 구체적으로)"

- 구체적 답변 예시: "B2B SaaS CFO, 매주 월요일 오전 수동으로 부서별 지출 분류"
- 추상적 답변 예시: "20-50대 직장인", "바쁜 사람들"

**Q2**: "지금 그들이 쓰는 workaround(임시 해결책)가 있나요?"

- workaround가 있으면 문제가 실재한다는 신호
- workaround 없음 = 문제가 아직 felt pain이 아닐 수 있음

**Q3**: "이것이 해결되면 그들의 행동이 구체적으로 어떻게 바뀌나요?"

- 행동 변화가 명확하면 JTBD(Jobs-to-be-Done)가 있다는 신호

**판정:**

- 3문 모두 구체적 답변 → **PROCEED**: "충분한 신호가 있습니다. Phase 1 설계 대화로 이동합니다."
- 1-2문 답변이 추상적 → **WARN**: "증거가 약합니다. Phase 1을 계속하되, 설계 후 discover/opp-tree로 보강을 권장합니다." (계속 진행)
- 3문 모두 추상적 → **WARN(강)**: "증거가 매우 약합니다. discover/opp-tree를 먼저 실행해 기회를 탐색하는 것을 강력히 권장합니다." (진행 여부 사용자 선택)

---

### Phase 1 — 설계 대화

superpowers:brainstorming의 Phase 1과 동일한 구조. 1문 1답으로 설계를 구체화한다.

**규칙:**

- 한 번에 질문 하나만. 복합 질문 금지
- Multiple choice 우선 제시 후 열린 답변 허용
- 2-3 접근 방식을 제안하고 각각의 트레이드오프와 권장 방향 제시
- 접근 방식 합의 후 설계 상세 확인

**탐색할 내용:**

1. 핵심 사용자 행동 흐름 (어떤 순서로 어떤 행동을 하는가)
2. 기술 접근 방식 (LLM 에이전트 vs 규칙 기반 vs 하이브리드)
3. 범위 경계 (반드시 포함 / 이번 버전 제외)
4. 성공의 모습 (완성됐을 때 사용자가 무엇을 할 수 있는가)

**설계 승인:** 사용자가 설계에 동의하면 Phase 2로 이동.

---

### Phase 2 — Signal Gate Bootstrap

superpowers에 없는 단계. 설계 대화에서 얻은 정보로 Signal Gate 시작 artifact 3개를 자동 생성한다.

설계 승인 후 아래 3개를 자동 생성한다:

**Artifact A: `harness/pain.md` 씨앗**

Phase 0 Q1-Q3 답변을 인터뷰 기록 형식으로 변환해 저장한다.

```
## 가설 인터뷰 #1 (AI 생성 — 실제 인터뷰로 검증 필요)
인터뷰 대상: [Q1 답변에서 추출한 페르소나]
날짜: [오늘 날짜]
형식: AI 합성 (실제 인터뷰 아님)

**Push (문제/불편):**
- [Q1-Q2에서 추출]

**Workaround:**
- [Q2 답변]

**기대하는 변화:**
- [Q3 답변]

⚠️ 이 항목은 AI 생성 가설입니다. 실제 Signal Gate 통과를 위해서는
   실제 사람과의 인터뷰 5건으로 교체하거나 보강하세요.
```

**Artifact B: `docs/brainstorm-assumptions.md` (가정 목록)**

Phase 0-1 대화에서 암묵적 가정을 추출해 4축으로 분류한다.

```
## 핵심 가정 (brainstorm 기반, 검증 필요)

### Value 가정 (사용자가 이것을 원할 것이다)
- [Phase 1 설계에서 추출]

### Feasibility 가정 (기술적으로 가능할 것이다)
- [Phase 1 접근 방식에서 추출]

### Reliability 가정 (충분히 잘 작동할 것이다)
- [Phase 1 품질 관련 논의에서 추출]

### Viability 가정 (지속 가능한 방식으로 전달 가능할 것이다)
- [Phase 1 범위·비용 관련 논의에서 추출]

다음 단계: discover/assumptions 스킬로 우선순위 부여 및 실험 설계 권장
```

**Artifact C: `docs/PRD-draft-section1.md` (§1 ICP 초안)**

Phase 0-1 대화에서 페르소나 정보를 추출해 PRD §1 구조로 변환한다.

```
## PRD §1 초안 — ICP / 타겟 사용자 (brainstorm 기반)

### Beachhead ICP
[Q1 답변 기반 — 가장 구체적인 첫 번째 타겟 사용자 정의]

### 주요 사용 시나리오
[Phase 1 설계 대화 기반]

### ICP 핵심 목표
[Q3 답변 기반]

⚠️ 이 초안은 brainstorm 대화 기반입니다.
   deliver/prd 스킬 실행 시 §1에 이 내용을 참고해 보강하세요.
```

파일 저장 전 `harness/` 및 `docs/` 디렉토리 존재 여부를 확인하고 없으면 생성한다.

파일 저장 후 요약 출력:

```
✅ Signal Gate Bootstrap 완료
   A. harness/pain.md 씨앗 생성 (AI 가설 — 실제 인터뷰 필요)
   B. docs/brainstorm-assumptions.md 가정 목록 생성
   C. docs/PRD-draft-section1.md §1 ICP 초안 생성

다음 단계: /deliver:prd 를 실행하면 위 초안을 참고해 14섹션 PRD를 작성합니다.
발견 단계를 더 깊이 하려면: /harness-discover --mode opp 를 먼저 실행하세요.
```

---

## Failure Handling

| 상황 | 감지 | 대응 |
|---|---|---|
| Phase 0 답변이 너무 추상적 | 페르소나 미특정, workaround 없음 | WARN 출력 후 계속 진행 (강제 차단 아님) |
| Phase 1에서 접근 방식 합의 실패 | 사용자가 어떤 접근도 선택 안 함 | "지금 결정하지 않아도 됩니다. PRD에서 §4 결정 옵션으로 다시 탐색할 수 있습니다." |
| harness/ 디렉토리 없음 | mkdir 필요 | `mkdir -p harness docs` 후 진행 |
| Phase 2 artifact 생성 시 기존 파일 있음 | 파일 존재 확인 | 덮어쓰기 전 사용자에게 확인 |

---

## Output Format

Phase 0 완료 시:

```
Worth-Building Check 결과: PROCEED / WARN / WARN(강)
근거: [3문 답변 요약]
```

Phase 1 완료 시:

```
설계 합의:
  접근 방식: [선택된 방식]
  핵심 사용자 흐름: [요약]
  범위: 포함 [X] / 제외 [Y]
```

Phase 2 완료 시:

```
Signal Gate Bootstrap 완료:
  harness/pain.md ✅
  docs/brainstorm-assumptions.md ✅
  docs/PRD-draft-section1.md ✅
  
다음: /deliver:prd [제품명]
```
