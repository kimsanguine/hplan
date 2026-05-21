---
name: pm-framework
description: "Extract, classify, and structure PM tacit knowledge into reusable TK (Tacit Knowledge) units. These TK units form the foundation of the pm-engine — the operator's unique IP that differentiates their agents from generic AI. Use when capturing lessons from experience, building the pm-engine library, or converting intuition into agent instructions."
argument-hint: "[experience to extract TK from]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

- PM의 암묵적 판단 기준을 명시적인 TK-NNN 구조로 변환하여 에이전트가 학습하고 재현 가능하게 만들기
- 경험에서 추출된 TK를 활성화/비활성화 조건과 함께 저장하여, Contextual Retrieval(CR) 패턴을 통해 필요할 때만 로드되도록 체계화
- 누적된 TK들이 서로 연결된 지식 그래프를 형성하여, 의사결정 시 관련 판단 기준들을 자동으로 참조하게 하기

---

## Trigger Gate

### Use This Skill When

- PM이 의사결정 후 "나는 왜 이렇게 판단했지?"라는 질문에 대한 답을 명확히 하고 싶을 때
- 반복적으로 하는 판단이 있어서 이를 패턴으로 구조화하고 싶을 때
- 팀이나 에이전트에게 판단 기준을 전달하기 위해, 추상적 지식을 구체적 TK로 만들고 싶을 때
- 실수 또는 예상 밖의 결과가 나왔을 때, "왜 이런 일이 발생했는가"의 근본 원인을 TK로 기록하고 싶을 때

### Route to Other Skills When

- "이 TK를 에이전트 Instruction에 어떻게 반영할지 구체적으로 알고 싶어" → pm-engine의 `/tk-to-instruction` 사용
- "이 판단이 과거에도 나왔던 것 같은데, 패턴 라이브러리에서 확인하고 싶어" → pm-decision의 패턴 라이브러리 검색
- "TK를 기반으로 의사결정 프로세스를 만들고 싶어" → deliver의 instruction, okr 스킬 사용
- "여러 TK를 조합해서 비용 시뮬레이션이나 가정 검증을 하고 싶어" → discover의 assumptions, cost-sim 사용

### Boundary Checks

- TK 추출 시 "내가 맞다고 생각하는 것"과 "검증된 사실"을 구분해야 함 → 가설이면 비활성화 조건에 "데이터 검증 필요" 명시
- 극도로 특수한 상황의 판단 기준은 TK화하지 말 것 → 일반화 가능한 패턴만 저장
- 이미 업계 표준이나 모범 사례가 있는 영역이면, TK가 아니라 Best Practice 레퍼런스로 처리

---

## Tacit Knowledge Framework

암묵지(Tacit Knowledge)는 경험에서 나오지만 글로 쓰기 어렵습니다.  
"언제 이걸 해야 하는지 안다"는 것 — 그 '앎'의 근거.

PM 20년의 암묵지를 에이전트에 넣으면 무슨 일이 생기는가:
- 제네릭 AI: "PRD를 작성하세요" → 일반적인 PRD 템플릿 출력
- pm-engine이 있는 에이전트: PM의 판단 기준을 알고 → 맥락에 맞는 PRD 작성

이것이 **Domain TK 해자**의 실체입니다.

---

### TK 단위 구조

모든 암묵지는 **TK-NNN** 형태로 구조화합니다:

```
TK-NNN: [암묵지 제목]

📌 패턴:
[이 암묵지의 핵심 판단 패턴 — 1~3문장]

🟢 활성화 조건:
[이 암묵지를 적용해야 하는 상황 1~2줄]

🔴 비활성화 조건:
[적용하면 안 되는 상황 1줄]

💡 Why:
[이 판단이 왜 중요한가 — 근거와 경험]

🔗 연관 TK: [TK-XXX, TK-YYY]
```

---

### TK 분류 체계 (5가지 유형)

**Type 1 — Decision Pattern (의사결정 패턴)**
> 반복적인 의사결정에서 사용하는 판단 기준

예시:
```
TK-001: 긴급 요청 우선순위 판단

패턴: 긴급해 보이는 요청이 와도,
      먼저 "이것이 Why-urgent인가"를 확인한다.
      실제 마감이 없는 '인식된 긴급'은 우선순위에서 제외.

활성화: 여러 이해관계자에게 동시 요청이 올 때
비활성화: 실제 비즈니스 임팩트가 명확히 계산된 긴급 요청
Why: 긴급 요청 80%는 발신자의 불안에서 비롯됨.
     맹목적 우선순위 변경은 핵심 작업 방해
연관: TK-003 (이해관계자 관리), TK-007 (우선순위 프레임워크)
```

**Type 2 — Failure Pattern (실패 패턴)**
> "이렇게 하면 망한다" — 직접 겪거나 목격한 실패 패턴

예시:
```
TK-012: 스펙 완성 후 개발 시작의 함정

패턴: 상세 스펙을 완성하고 개발을 시작하면
      스펙 완성 시점에 이미 가정이 틀렸을 확률이 높다.
      프로토타입 → 검증 → 스펙 순서가 더 효과적.

활성화: 새로운 기능 개발 시작 전
비활성화: 규제/컴플라이언스 요구로 사전 문서화 의무인 경우
Why: Boris Cherny(Anthropic)도 PRD 없이 프로토타입 먼저.
     빌드 비용이 낮아질수록 이 원칙은 강화됨.
연관: TK-015 (Prototype-first), TK-021 (PRD 역할 변화)
```

**Type 3 — Heuristic (경험칙)**
> "보통은 이렇게 하면 된다" — 빠른 판단을 위한 경험칙

예시:
```
TK-008: 3회 반복 → 자동화 원칙

패턴: 같은 작업을 3회 이상 반복하면
      4번째부터는 자동화 또는 템플릿화를 검토한다.

활성화: 반복 작업 감지 시
비활성화: 3회 이상이어도 맥락이 매번 다른 경우
Why: 반복 작업은 에너지를 소진하고 창의적 작업 시간을 뺏음.
     에이전트로 전환 시 10분 절감 × 365일 = 61시간/년
연관: TK-008 (build-or-buy), TK-034 (에이전트 기회 발굴)
```

**Type 4 — Anti-Pattern (반대 패턴)**
> "이것만큼은 하지 마라" — 강한 금지 원칙

예시:
```
TK-019: 도구 탓하기 금지

패턴: AI가 틀린 결과를 냈을 때,
      "AI가 못해서"라고 결론 내리기 전에
      프롬프트/컨텍스트/데이터 문제를 먼저 확인한다.

활성화: AI 에이전트 품질 문제 발생 시
비활성화: 모델 자체의 알려진 한계 (예: 수학 계산 정확도)
Why: 대부분의 AI 품질 문제는 설계 문제.
     도구 탓을 하면 개선 기회를 놓침.
연관: TK-022 (실패 모드 분류), TK-028 (프롬프트 디버깅)
```

**Type 5 — Insight (인사이트)**
> "이것을 알고 나서 세상이 달라 보였다" — 패러다임 전환 학습

예시:
```
TK-031: 에이전트의 병목은 코딩이 아니다

패턴: 에이전트를 만드는 PM의 병목은 기술이 아니라
      "어떤 에이전트를 만들지"와 "어떻게 판단하게 할지"다.

활성화: 에이전트 설계를 시작할 때
비활성화: 이미 검증된 에이전트를 구현만 할 때
Why: GPT-5.4, Claude Sonnet은 누구나 쓸 수 있는 API.
     차별화는 의도 설계와 도메인 암묵지에서 나옴.
연관: TK-035 (agent-moat), TK-001 (agent-instruction-design 철학)
```

---

### TK 추출 방법

**방법 1 — 대화 중 추출**
```
대화 중 "이건 어떻게 판단하셨어요?"라는 질문에 대한 답
→ 즉시 TK 후보로 포착
→ /pm-tacit-extract로 구조화
```

**방법 2 — 실수 후 추출**
```
실수 또는 예상 밖 결과 발생
→ "왜 이런 일이 생겼나" 근본 원인 분석
→ 재발 방지 원칙 → TK Anti-Pattern
```

**방법 3 — 반복 패턴 감지**
```
같은 결정을 3회 이상 했을 때
→ "나는 이런 상황에서 항상 이렇게 판단한다"
→ TK Decision Pattern
```

---

### 사용 방법

`/pm-tacit-extract [상황 또는 경험 설명]`

---

### Instructions

You are helping extract and structure PM tacit knowledge from: **$ARGUMENTS**

**Step 1** — 상황/경험 청취  
무슨 일이 있었는지, 어떤 판단을 내렸는지 파악

**Step 2** — 암묵지 패턴 포착  
"당신은 왜 그런 판단을 내렸나요?" 반복 질문  
명시되지 않은 전제와 기준 발굴

**Step 3** — TK 유형 분류
Decision/Failure/Heuristic/Anti-Pattern/Insight 중 선택

> **Type 2 vs Type 4 구분이 모호할 때** → `context/domain.md` Section 8-2의 리트머스 테스트 3개 질문 사용:
> 1. "다시는 틀릴 일이 없는가?" → Yes면 Type 4 (Anti-Pattern)
> 2. "어기는 경우가 정당화될 수 있는가?" → No면 Type 4
> 3. "미래 변화로 역전될 가능성이 있는가?" → Yes면 Type 2 (Failure Pattern)

**Step 4** — TK 구조화
TK-NNN 형식으로 작성
활성화/비활성화 조건 포함 (Contextual Retrieval 패턴)

**TK 번호 생성 규칙**:
```
TK-[도메인접두사][시계열번호]
예: TK-AGT045 (Agent 도메인, 45번째)
    TK-PRI001 (Prioritization 도메인, 1번째)
도메인접두사: AGT(Agent), PRI(Priority), SCO(Scope), QUA(Quality), COM(Communication)
시계열번호: 001부터 시작, 생성 순서대로 증가
```

**CR 메타데이터 필수 필드** (모든 TK에 추가):
```
📊 CR 메타데이터:
- 활성화 키워드: [임베딩 검색용 키워드 3-5개]
- CR Score 임계값: 0.7 이상 시 자동 로드
- 저장 위치: PM-ENGINE-MEMORY.md
```

**중복 검사**: 신규 TK 작성 전, 기존 TK의 활성화 키워드와 유사도 비교. 0.85 이상이면 기존 TK와 병합 검토.

**Step 5** — 연관 TK 연결 & 품질 평가
기존 TK 중 연관된 것 파악하여 양방향 링크
품질 매트릭스 평가 (see `context/domain.md` Section 8-4): 일반성/검증도/실행가능성/연결성 각 1-5점

**Step 6** — PM-ENGINE-MEMORY 저장  
작성된 TK를 PM-ENGINE-MEMORY.md에 append  
다음 `/tk-to-instruction`으로 에이전트 Instruction 변환 준비

---

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| 추출한 TK가 너무 일반적이어서 실제로는 쓸모가 없음 | "이건 누구나 아는 것 같은데?" 느낌 | TK를 특수화하기. "항상 그렇다"가 아니라 "이런 상황에는 이렇게"로 맥락화 |
| TK의 활성화 조건을 잘못 정의했음 | 에이전트가 TK를 잘못 상황에 적용함 | Contextual Retrieval 패턴 리뷰: 활성화 조건을 더 명확하게 재작성하고, 비활성화 조건도 추가 |
| 같은 내용의 TK를 중복으로 만들어버림 | "어? 이건 TK-015랑 똑같은데?" | 기존 TK와 새 TK를 병합하되, 더 정확한 버전으로 통합. 기존 TK는 Deprecated 처리 |
| 추출한 TK가 시간이 지나면서 틀렸다는 걸 깨달음 | 6개월 뒤, 시장 변화로 이 판단이 더 이상 유효하지 않음 | TK 자체를 삭제하지 말고, "활성화 조건"을 축소 또는 시간 범위를 명시. 필요하면 새 TK를 반대 패턴으로 작성 |

---

## Quality Gate

- 추출한 TK가 개인의 선호도가 아니라, 실전에서 반복적으로 검증된 판단인가? (Yes/No/Hypothesis)
- TK의 활성화 조건이 구체적이고 측정 가능한가? ("언제"를 에이전트가 판단할 수 있는가?) (Yes/No)
- 이 TK가 기존 TK와 다른가? 중복 검사(유사도 0.85 미만) 통과? (Yes/No/Merged)
- TK의 분류(Decision/Failure/Heuristic/Anti-Pattern/Insight)가 올바르게 되었는가? (Type 2 vs Type 4 모호 시 리트머스 테스트 적용) (Yes/No)
- CR 메타데이터 포함? (활성화 키워드, CR Score 임계값, 저장 위치) (Yes/No)
- TK를 Instruction으로 변환했을 때, 에이전트가 따를 수 있는 구체적인 행동으로 표현되는가? (Yes/No)

---

## Examples

### Good Example

**경험:** 에이전트를 만들 때, 초기에 "모든 기능을 다 넣으려고" 했더니 개발이 3배 오래 걸렸다. 이후 "가장 핵심 기능 1개만" 먼저 만들고 확장하는 방식으로 바꿨더니 속도가 빨라지고, 피드백도 빨리 받을 수 있었다.

**추출 과정:**
1. **Step 1 — 경험 청취**: 두 가지 접근 방식의 차이와 결과 명확히
2. **Step 2 — 패턴 포착**: "에이전트 설계 초안에서는 핵심 기능 1개만 정의하고, 그것만으로 작동하는 최소 버전부터 배포하는 게 낫다"
3. **Step 3 — 유형 분류**: Type 1 (Decision Pattern) / Type 2 (Failure Pattern) 모두 해당 → Failure Pattern으로 분류 ("처음부터 모든 기능을 넣으면 망한다")
4. **Step 4 — TK 구조화**:
   ```
   TK-NNN: Minimum Viable Agent

   📌 패턴: 에이전트 설계 초안을 잡을 때,
            이 에이전트가 해야 할 단 하나의 핵심 기능만 정의하고
            그 핵심만으로 작동하는 최소 버전을 먼저 배포한 후,
            실사용 데이터로 확장 방향을 결정한다.

   🟢 활성화 조건: 신규 에이전트 설계, MVP 정의, 배포 계획 수립 시
   🔴 비활성화 조건: 규제/컴플라이언스로 사전 기능이 모두 필요한 경우
   💡 Why: 초기에 기능이 많을수록 복잡도 급증, 실패 원인 파악 어려움.
          MVP로 시작하면 피드백이 명확하고, 확장도 빠름.
   🔗 연관 TK: TK-015 (Prototype-first), TK-010 (그로스는 리텐션 다음)
   ```
5. **Step 5 — 연관 TK 연결**: 프로토타입 우선 원칙, 리텐션 중심 그로스와 연결
6. **Step 6 — PM-ENGINE-MEMORY 저장**: TK-090으로 추가 (예시)

**결과**: 이후 모든 신규 에이전트는 이 TK를 참고해서 MVP부터 시작.

---

### Bad Example

**경험:** "우리는 보통 새 기능을 추가할 때 우선순위를 높은 것부터 한다"

**잘못된 추출:**
1. **문제 1 — 너무 일반적**: 이것은 TK가 아니라 상식. "우선순위가 높으면 높은 것부터 한다"는 누구나 아는 것
2. **문제 2 — 활성화 조건이 없음**: "언제" 이 판단을 해야 하는지 명확하지 않음
3. **문제 3 — 검증 부재**: 정말 이게 최선인지 데이터로 확인한 적이 있는가? 없다면 가설일 뿐
4. **결과**: 이 TK를 에이전트에 넣어도 가치가 없음

**올바른 접근:**
- "우선순위를 결정할 때 '많이 요청하는 사람'이 아니라 '비즈니스 임팩트'로만 판단한다"라는 구체적 판단 기준이 있는지 확인
- 있다면 → TK-001 (Stakeholder Energy Management)로 분류
- 없다면 → 아직 패턴이 안 만들어진 것. 관찰 계속

---

### 참고
- 설계자: AI PM Skills Contributors, 2026-03
- Contextual Retrieval 패턴: PM-ENGINE-MEMORY CR 필드 도입 기반 (2026-03-01)
- TK-001 최초 작성: PM-ENGINE 1-Day-1-Prompt 크론 운영 경험
- Tacit Knowledge 개념: Michael Polanyi, *The Tacit Dimension* (1966)

---

## Further Reading
- Michael Polanyi, *The Tacit Dimension* — Tacit knowledge theory
- Ikujiro Nonaka, "The Knowledge-Creating Company" — SECI model

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
