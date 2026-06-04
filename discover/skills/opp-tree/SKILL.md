---
name: opp-tree
description: "Analyze where AI agents can add value and which tasks to automate — systematically map repetitive workflows, manual processes, and operational bottlenecks to identify the best agent opportunities. Build an Agent Opportunity Tree from desired outcomes to solvable problems, agent solution candidates, and validation experiments. Use when exploring where AI agents could add value to a platform or service, finding automation opportunities in workflows, identifying repetitive tasks worth automating, prioritizing which agent to build first, or mapping the full opportunity space before committing to development. Applicable to any domain — customer support, edtech, SaaS, operations, and more."
argument-hint: "[product or domain to explore]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

- 자동화 기회를 체계적으로 탐색하고 우선순위를 정하여 팀이 가장 값있는 에이전트에 투자하도록 함
- 반복빈도, 자동화가능성, 판단의존도를 기준으로 기술적 가능성과 비즈니스 가치의 균형을 맞춤
- 검증 실험 설계를 통해 구현 전에 핵심 가정(Value/Feasibility/Reliability/Ethics)을 빠르게 테스트

---

## Trigger Gate

### Use This Skill When
- 에이전트 도입을 고려 중인데 어디서부터 시작할지 결정해야 할 때
- 조직의 반복 작업, 병목 지점, 자동화 기회를 체계적으로 매핑해야 할 때
- 여러 개의 에이전트 아이디어가 있는데 어느 것을 먼저 구현할지 우선순위를 정해야 할 때
- 기술 팀과 비즈니스 팀의 의견이 갈려 "에이전트를 만들어야 하는가"를 데이터 기반으로 판단해야 할 때

### Route to Other Skills When
- 선택된 기회의 가정(Value/Feasibility/Reliability/Ethics)을 깊이 있게 검증해야 할 때 → `assumptions` 스킬
- 최우선 기회의 기술 구현 방식(Trigger Agent vs Pipeline Agent vs Research Agent)을 결정해야 할 때 → `discover/assumptions --mode build-or-buy`
- 선택한 에이전트에 인간 개입 지점을 설계해야 할 때 → `hitl` 스킬
- Opportunity Tree를 Mermaid + `docs/OPPORTUNITY_TREE.md`로 영구화하고 5/3 strong-Push 패턴으로 검증할 때 → `ost` (hplan plugin)

### Boundary Checks
- **범위 확인**: AOT는 "어떤 에이전트를 만들 것인가"를 정하는 것이지, "어떻게 만드는가"를 설명하지 않음 — 구현은 `deliver/agent-setup`으로 연결
- **판단 의존도 주의**: 점수가 5점을 넘어가거나 판단 의존도가 높다면(4~5점) AOT 대상이 아닐 수 있음 — 그냥 Rule-based 자동화나 인간 처리가 더 나을 수 있음

---

## Agent Opportunity Tree (AOT)

에이전트를 "만들 수 있냐"가 아니라 "만들어야 하냐"를 결정하는 프레임워크.  
Teresa Torres의 Opportunity Solution Tree를 AI 에이전트 디스커버리에 맞게 재설계했습니다.

---

### 왜 에이전트에는 다른 OST가 필요한가

일반 OST는 제품 기능을 탐색할 때 씁니다.  
에이전트 OST는 다릅니다. 에이전트는 **자율적으로 행동**하기 때문에 잘못된 기회를 선택하면 오류가 조용히 증폭됩니다.

에이전트 디스커버리에서 빠지기 쉬운 함정:
- "기술적으로 가능하니까" 만든다 → 아무도 안 씀
- "반복 작업이니까" 자동화한다 → 판단이 필요한 부분을 건드려 더 큰 문제 발생
- 에이전트 1개로 너무 많은 걸 해결하려 한다 → 실패율 급증

AOT는 이 함정을 피하기 위해 **4개 레이어를 순서대로** 탐색합니다.

---

### 구조 (4 레이어)

```
[Automation Outcome]
        │
   ┌────┴────┐
[Opportunity] [Opportunity] ...
        │
   ┌────┴────┐
[Agent Type] [Agent Type] ...
        │
   ┌────┴────┐
[Experiment] [Experiment] ...
```

**레이어 1 — Automation Outcome (자동화 목표)**

단 하나의 측정 가능한 목표를 정합니다.  
좋은 예: "PM이 뉴스 수집에 쓰는 시간을 주 5시간 → 0시간으로 줄인다"  
나쁜 예: "업무를 AI로 자동화한다" (너무 넓음)

**레이어 2 — Opportunities (기회, 문제 공간)**

자동화로 해결 가능한 반복 작업, 판단 패턴, 병목 지점을 발굴합니다.  
기회 프레이밍 공식:  
`"[누가] [어떤 상황에서] [반복적으로] [무엇을 해야 하는데] [시간/실수/비용이 든다]"`

기회 우선순위 점수:  
`Opportunity Score = 반복빈도(1-5) × 자동화가능성(1-5) × 판단의존도 역수(5=저판단)`

> ⚠️ 판단 의존도가 높을수록 에이전트화가 어렵습니다. 점수가 낮은 기회는 Rule-based 자동화나 인간 처리가 더 적합합니다.

**레이어 3 — Agent Solutions (에이전트 솔루션 후보)**

각 기회마다 최소 3가지 에이전트 유형을 탐색합니다:

| 유형 | 설명 | 언제 적합한가 |
|---|---|---|
| **Trigger Agent** | 이벤트 발생 시 단일 작업 실행 | 명확한 입력/출력, 판단 최소 |
| **Pipeline Agent** | 순차 다단계 처리 | 정해진 워크플로우 자동화 |
| **Research Agent** | 정보 수집 후 요약/판단 | 탐색 범위가 동적인 경우 |
| **Monitor Agent** | 주기적 감시 후 알림/액션 | 임계값 기반 반응 필요 |
| **Orchestrator Agent** | 하위 에이전트를 조율 | 복잡한 멀티스텝, 병렬 처리 |

각 솔루션 후보에 대해 반드시 답해야 할 3가지:
1. **트리거**: 무엇이 에이전트를 시작시키는가?
2. **도구**: 어떤 툴/API/파일에 접근해야 하는가?
3. **종료 조건**: 에이전트가 성공적으로 완료됐다는 것을 어떻게 아는가?

**레이어 4 — Experiments (검증 실험)**

에이전트를 구현하기 전에 핵심 가정을 먼저 테스트합니다.

에이전트 가정 4축:
- **Value**: 이 자동화가 실제로 시간/비용을 절감하는가?
- **Feasibility**: 필요한 데이터/API에 접근 가능한가?
- **Reliability**: 충분한 정확도로 반복 실행 가능한가?
- **Ethics**: 자동화해도 괜찮은 판단인가? 오류 발생 시 영향은?

최소 검증 실험 예시:
- "하루 동안 직접 해보며 실제 반복 패턴 기록"
- "API 호출 5회 테스트 → 응답 품질 점검"
- "MVP 프롬프트 + 수동 실행 10회 → 정확도 측정"

---

### 사용 방법

`/agent-opportunity-tree [자동화하려는 업무 또는 문제]`

---

### Instructions

You are helping to build an **Agent Opportunity Tree** for: **$ARGUMENTS**

**Step 1 — Automation Outcome 확정**
- 측정 가능한 자동화 목표 1개를 명확히 정의한다
- "시간 절감", "오류 감소", "비용 절감" 중 하나에 수치를 붙인다

**Step 2 — Opportunities 발굴 (3~5개)**
- 주어진 문제/업무에서 반복 작업, 판단 패턴, 병목을 추출한다
- 각 기회에 Opportunity Score를 계산한다 (반복빈도 × 자동화가능성 × 판단의존도 역수)
- Score 상위 3개를 선택하고, 낮은 기회는 제외 이유를 명시한다

**Step 3 — Agent Solutions 후보 (기회당 2~3개)**
- 각 기회마다 에이전트 유형 2~3개를 제안한다
- 각 후보의 트리거 / 필요 도구 / 종료 조건을 명시한다
- 구현 난이도를 Low/Medium/High로 표시한다

**Step 4 — Experiments 설계 (최우선 솔루션 1~2개)**
- Value / Feasibility / Reliability / Ethics 4축 가정을 나열한다
- 각 가정의 검증 실험을 2일 이내에 할 수 있는 수준으로 설계한다

**Step 5 — 다음 권장 액션**
- 가장 높은 Opportunity Score + 가장 낮은 구현 난이도 조합을 추천한다
- `deliver/agent-setup`으로 연결할 준비가 됐는지 확인한다

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| Opportunity Score가 모두 높게 나옴 (3점 이상이 5개+) | 점수 보정이 과도해 모두가 높게 평가됨 | 팀과 함께 "정말 자동화가 가능한가" 재검토; 판단 의존도를 더 엄격히 평가 |
| 선택한 기회가 실제로 반복되지 않음 (실험 후 판명) | 2주 실험 결과 "이건 일주일에 1번도 안 함"이라는 데이터 발생 | 해당 기회 제외; 다음 순위 기회로 즉시 전환 (재점수 필요 없음) |
| Ethics 위험이 높은데 감지 못함 (배포 후 문제 발생) | 구현 후 고객이 "이건 자동화하면 안 된다"고 지적 | 다음 AOT부터 Ethics 축에 팀 리뷰 미팅 추가; `hitl` 스킬로 재설계 후 배포 |
| 필요 도구/API가 없어서 실현 불가 (실험 중 발견) | API 테스트 10회 결과 "권한이 없다" 또는 "비용이 $5k/month" | Feasibility 점수 즉시 재평가; 다른 기회 탐색 또는 기술 솔루션 재검토 |

---

## Quality Gate

- 자동화 Outcome이 측정 가능한 수치(시간, 오류율, 비용)를 포함하는가? (Yes/No)
- 발굴된 Opportunity가 3개 이상이고, 각각 다른 카테고리(정보수집/판단/물리작업)를 포괄하는가? (Yes/No)
- 상위 3개 Opportunity의 점수 계산이 명확하고, 제외된 기회의 이유가 명시되어 있는가? (Yes/No)
- 각 기회마다 최소 2개 이상의 에이전트 솔루션 후보가 있고, 트리거/도구/종료조건이 정의되어 있는가? (Yes/No)
- 최우선 솔루션에 대해 Value/Feasibility/Reliability/Ethics 4축 가정이 명시되고, 각 가정의 검증 실험이 2일 이내에 가능한 수준으로 설계되어 있는가? (Yes/No)

---

## Examples

### Good Example

```
Automation Outcome:
"PM이 경쟁사 뉴스 수집에 쓰는 시간을 주 8시간 → 0.5시간으로 줄인다"

Opportunity 1: RSS/웹 뉴스 수집 및 요약
  - Score: 5(빈도) × 5(자동화 가능) × 5(판단 역수) = 125점
  - 이유: 매일 반복, API만으로 가능, 요약은 프롬프트만으로 해결

Opportunity 2: 수집한 뉴스를 Slack에 자동 발송
  - Score: 5(빈도) × 5(자동화 가능) × 4(판단 역수) = 100점
  - 이유: 매일, Slack API + 문서 쓰기 간단, 사람 판단 최소

Opportunity 3: 경쟁사별 뉴스 필터링 및 태깅
  - Score: 4(빈도) × 3(자동화 가능) × 2(판단 역수) = 24점
  - 이유: 경쟁사 판단이 필요(도메인 지식), 자동화 어려움 → 하위 우선순위

선택: Opportunity 1 + Opportunity 2 결합
  → Research Agent (웹 수집) + Pipeline Agent (Slack 발송)

Experiment (Value):
  - 3일간 PM이 직접 뉴스 수집 시간 기록 (기준선)
  - MVP 프롬프트로 동일 뉴스 5개 요약 → 품질 평가
  - "요약이 충분히 유용한가" 판단 기준: 원문보다 5배 이상 빠른가?
```

### Bad Example

```
❌ Automation Outcome이 너무 넓음:
"우리 회사 업무를 AI로 자동화한다"
→ 측정 불가능, 우선순위 불가능

❌ 모든 기회가 높은 점수:
  - Opportunity A: 120점
  - Opportunity B: 115점
  - Opportunity C: 110점
→ 점수 계산 오류 또는 팀이 모든 기회를 좋게 평가하는 바이어스 존재
→ 재평가 필요: 정말 자동화 가능한가? 판단이 필요하지 않나?

❌ Ethics 위험 미감지:
  "고객 이메일 자동 응답 에이전트"
  - 기회: 고객 응답 시간을 2시간 → 5분으로
  - Score 점수는 높음
  - But: 할루시네이션으로 잘못된 응답 발송 시 고객 손실
  - Ethics 축: 위험도 5점, 하지만 AOT에서 미감지
→ `hitl` 스킬과 함께 "Approval Gate 필수" 플래그 필요

❌ 실험 설계 불충분:
  "API가 있으니까 Feasible하다고 가정"
  - But: API에 인증 권한이 없거나 Rate Limit가 있을 수 있음
→ 실험: "API 호출 10회 테스트" 반드시 실행
```

---

### GTM 연계

AOT로 선택된 기회를 실제 시장에 출시할 때: 첫 고객 세그먼트(비치헤드)를 Pain Intensity / Willingness to Trust AI / Data Availability / Budget Authority / Reference Potential 5개 기준(각 1-5점, 총점 20+ 권장)으로 선정한다. 신뢰 구축은 Shadow Mode → Co-pilot → Auto-pilot → Full Delegation 4단계 시퀀스를 따른다. 출시는 Lighthouse(1-3개 고객, 성공 사례 확보) → Wedge(10-30개, 반복 가능한 세일즈 모션) → Expand(100+, 인접 세그먼트 확장) 순으로 진행한다.

### 참고
- 원본 프레임워크: Teresa Torres, *Continuous Discovery Habits* (OST)
- 에이전트 특화 확장: AI PM Skills Contributors, 2026
- Reliability / Ethics 축: Byeonghyeok Kwak의 엔터프라이즈 에이전트 거버넌스 논의에서 영감

---

## Further Reading
- Teresa Torres, *Continuous Discovery Habits* — Opportunity Solution Tree origin
- Marty Cagan, *INSPIRED* — Continuous product discovery

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
