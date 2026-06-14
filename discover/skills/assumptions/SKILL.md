---
name: assumptions
description: "Identify and prioritize the riskiest assumptions in an agent idea across four axes: Value, Feasibility, Reliability, and Ethics. Use after defining an agent opportunity and before starting implementation. Prevents building agents that work technically but fail operationally or cause unintended harm. Includes build-or-buy vendor decision framework."
argument-hint: "[agent idea to analyze] [--mode validate|build-or-buy]"
allowed-tools: ["Read", "Write"]
model: inherit
---

## Core Goal

- 구현 전에 에이전트의 숨겨진 가정을 발굴하고 리스크를 수치화하여 팀이 무엇을 먼저 검증해야 하는지 명확히 함
- 4축(Value/Feasibility/Reliability/Ethics) 분석을 통해 기술적 가능성과 실제 운영 가능성의 갭을 조기에 발견
- 우선순위 점수(위험도 × 검증 난이도)를 기준으로 2일 이내에 실행 가능한 최소 검증 실험을 설계

---

## Trigger Gate

### Use This Skill When
- `opp-tree` 스킬로 기회를 선택한 후, 구현하기 전에 핵심 가정을 빠르게 검증하고 싶을 때
- 에이전트 아이디어가 있는데 "정말 작동할 것 같나"에 대한 우려가 있을 때
- 기술 팀은 구현 가능하다고 하는데 비즈니스 팀이 의심스러워할 때
- 윤리/안전 위험(예: 잘못된 판단이 고객에게 영향)이 있을 수 있다고 생각할 때

### Route to Other Skills When
- 검증 실험 설계 후 실제로 프롬프트/API를 테스트해야 할 때 → `hitl` 스킬 (Human-in-the-Loop으로 초기 신뢰도 측정) 또는 본 스킬 `--mode build-or-buy`
- 가정 검증 결과 위험도가 매우 높으면 → `hitl` 스킬로 에스컬레이션 전략 설계
- 검증 통과 후 에이전트 설계 및 프롬프트/인스트럭션을 작성해야 할 때 → `deliver/agent-setup`
- 8축 100점 evidence 루브릭으로 정량 채점이 필요할 때 → `evidence-rubric` (hplan plugin). V/F/R/E 4축과 상보적.

### Boundary Checks
- **검증의 범위**: Assumptions는 가정을 "정의"하고 "우선순위"를 정하는 것이지, 실제로 검증 실험을 끝까지 실행하지는 않음 — 실험 실행은 팀이 직접 담당
- **이미 검증됨**: 기술 스택이 프로덕션에서 이미 검증되었다면(예: 우리 팀이 동일 모델로 다른 에이전트를 성공했다면) 그 가정의 점수는 내려야 함

---

## Agent Assumption Map

에이전트 아이디어에는 수십 개의 숨겨진 가정이 있습니다.
그 중 단 하나만 틀려도 에이전트는 조용히 잘못된 방향으로 실행됩니다.

일반 제품과 다른 점:
- 일반 제품: 사용자가 결과를 보고 판단 → 오류 발견 즉시 가능
- 에이전트: 자율 실행 → 오류가 쌓일 때까지 발견 어려움

Agent Assumption Map은 **4축 분석**으로 핵심 가정을 사전에 발굴합니다.

---

### 4축 정의

**Axis 1 — Value (가치 가정)**
> "이 에이전트가 실제로 의미 있는 문제를 해결하는가?"

검토 질문:
- 자동화 후 실제로 시간/비용/오류가 줄어드는가?
- 사용자가 에이전트의 결과를 실제로 사용하는가?
- 에이전트 없이도 충분히 빠르게/잘 할 수 있지 않은가?
- 자동화로 해결되는 불편함이 진짜 불편함인가, 아니면 낮은 빈도의 사소한 불편인가?

**Axis 2 — Feasibility (실현 가능성 가정)**
> "이 에이전트를 실제로 구현할 수 있는가?"

검토 질문:
- 필요한 데이터에 접근 가능한가? (API 권한, 인증, 비용)
- 필요한 툴이 안정적으로 작동하는가?
- 기술 스택 (모델, 프레임워크) 이 요구사항을 지원하는가?
- 개발 리소스와 타임라인이 현실적인가?
- 외부 의존성 (API 변경, 서비스 중단) 리스크는?

**Axis 3 — Reliability (신뢰성 가정)** ← 에이전트 특화 축
> "이 에이전트가 충분히 정확하고 안정적으로 반복 실행 가능한가?"

검토 질문:
- 정확도 기준은 무엇인가? (90%? 99%? 100%?)
- 오류 발생 시 자동 감지 및 복구 가능한가?
- 컨텍스트 길이 / 모델 응답 일관성이 보장되는가?
- 외부 API 장애 시 에이전트가 어떻게 반응하는가?
- 장기 실행 시 성능 저하 (컨텍스트 오염, 비용 증가) 없는가?

> ⚠️ 신뢰성 기준은 용도에 따라 다릅니다.
> 뉴스 요약 에이전트 (90% 충분) vs 금융 거래 에이전트 (99.9% 이상 필요)

**Axis 4 — Ethics (윤리/안전 가정)** ← 에이전트 특화 축
> "이 에이전트를 자동화해도 괜찮은가? 오류 발생 시 영향은?"

검토 질문:
- 에이전트가 잘못된 판단을 내릴 때 영향 범위는?
- 개인정보 / 민감 데이터를 다루는가?
- 에이전트의 행동이 역추적 가능한가? (감사 로그)
- 에이전트가 인간을 대신해 의사결정하는 영역인가?
- 사용자가 에이전트의 판단을 검토하고 거부할 수 있는가?

> ⚠️ Ethics 축 점수가 낮으면 (위험 높음): Human-in-the-loop 설계 필수

---

### 가정 발굴 방법

**1단계: 브레인스토밍 (제한 없이)**
각 축에 대해 "~라고 가정하고 있다" 형태로 가정을 최대한 많이 나열.

예시 (AI 뉴스 브리핑 에이전트):
- Value: "PM이 AI 뉴스를 매일 읽고 싶어한다고 가정"
- Value: "요약된 뉴스가 원문보다 유용하다고 가정"
- Feasibility: "RSS 피드가 안정적으로 최신 뉴스를 제공한다고 가정"
- Feasibility: "Brave API 없이도 충분한 정보를 수집 가능하다고 가정"
- Reliability: "Haiku 모델이 뉴스 요약을 일관되게 잘 한다고 가정"
- Ethics: "AI가 요약한 뉴스가 원의도를 왜곡하지 않는다고 가정"

**2단계: 우선순위 매핑**
각 가정에 대해 2개 기준으로 점수 부여:

```
위험도 (1~5): 이 가정이 틀렸을 때 에이전트가 얼마나 망가지는가?
검증 난이도 (1~5): 이 가정을 검증하는 것이 얼마나 어려운가?

Priority Score = 위험도 × 검증 난이도
```

매트릭스:
```
             검증 난이도
             낮음  →  높음
위  높음  │ 즉시 검증  │ 최우선 검증 │
험       │            │             │
도  낮음  │ 나중에     │ 모니터링    │
```

**3단계: Top 3 가정 선정**
Priority Score 상위 3개 가정 → 실험 설계로 연결

---

### 가정 검증 실험 유형

| 가정 유형 | 권장 실험 |
|---|---|
| Value | 5일 수동 실행 후 실제 사용 여부 관찰 |
| Feasibility | API 직접 호출 10회 테스트 |
| Reliability | 동일 입력 20회 반복 → 출력 일관성 측정 |
| Ethics | 오류 시나리오 시뮬레이션 + 영향 범위 계산 |

---

### 사용 방법

`/agent-assumptions [에이전트 아이디어 또는 이름]`

---

### Instructions

You are helping identify and prioritize the riskiest assumptions for: **$ARGUMENTS**

**Step 1 — 에이전트 개요 파악**
- 에이전트 목적, 주요 기능, 타겟 사용자 확인
- 이미 정의된 Automation Outcome 확인 (agent-opportunity-tree와 연계)

**Step 2 — 4축 가정 브레인스토밍**
- 각 축 (Value / Feasibility / Reliability / Ethics)에 대해
  최소 3개 이상의 가정을 "~라고 가정하고 있다" 형태로 추출
- 억지로 좋게 보려 하지 말 것 — 부정적 가정도 적극 발굴

**Step 3 — 우선순위 매핑**
- 각 가정에 위험도(1~5) × 검증 난이도(1~5) = Priority Score 계산
- 상위 5개를 표로 정리

**Step 4 — Top 3 가정 심층 분석**
- 각 가정이 틀렸을 때 시나리오 서술
- 검증 실험 설계 (2일 이내 가능한 수준)
- 검증 결과에 따른 피벗 옵션

**Step 5 — Ethics 체크**
- Ethics 축 가정 중 위험도 4 이상인 항목 별도 강조
- Human-in-the-loop 설계가 필요한지 판단

**Step 6 — 다음 단계 연결**
- 검증 실험이 통과되면 `deliver/agent-setup`으로 연결
- Ethics 위험이 높으면 `/human-in-loop-design`으로 먼저 연결
- 검증 결과 실패 시 `agent-opportunity-tree`로 되돌아가 기회 재탐색

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 모든 가정이 "위험도 1~2점"으로 평가됨 | 팀이 에이전트를 너무 긍정적으로 평가 | 악의적 질문("이게 망할 확률은?") 추가; 반대편 입장에서 가정 재검토 |
| Top 3 가정이 모두 Feasibility인데 Value/Ethics가 없음 | 기술 검증만 계획되고 실제 사용자 가치/윤리 검토 누락 | Value 축 가정 재검토 필요; 사용자 인터뷰 또는 5일 수동 실행 추가 |
| 검증 실험 결과 Top 1 가정이 틀렸음 (예: API 없음) | 실험 실행 후 "우리 예상이 틀렸다" 판명 | 해당 가정 기반 피벗 옵션 검토 (다른 데이터소스? 다른 API?) 또는 기회 재탐색 |
| Ethics 위험을 감지했는데 팀이 "괜찮을 거야" 무시 | 리뷰 미팅에서 위험도 4~5점 가정이 논의 안 됨 | 위험도 4점 이상 가정은 반드시 `hitl` 스킬 검토 강제; 서명 기록 남기기 |

---

## Quality Gate

- 4축(Value/Feasibility/Reliability/Ethics) 각각에 3개 이상의 가정이 브레인스토밍되어 있는가? (Yes/No)
- Top 5 가정이 우선순위 점수(위험도 × 검증 난이도)와 함께 정렬되어 있고, 각 점수 계산 근거가 명시되어 있는가? (Yes/No)
- Top 3 가정 각각에 대해 "틀렸을 시나리오"와 "피벗 옵션"이 구체적으로 서술되어 있는가? (Yes/No)
- 검증 실험이 2일 이내에 실행 가능한 수준으로 설계되어 있는가 (e.g., "5회 API 테스트", "3일 수동 실행")? (Yes/No)
- Ethics 위험도가 4점 이상인 가정이 있을 경우, `hitl` 스킬 검토 또는 Human-in-the-Loop 설계가 예정되어 있는가? (Yes/No)

---

## Examples

### Good Example

```
Agent Idea: "매일 아침 CEO에게 경영 지표 대시보드를 자동으로 이메일 발송"

Value Assumptions:
1. "CEO가 대시보드 이메일을 매일 열어본다" (위험도: 4, 난이도: 1) → Priority: 4
   → 실험: 지난 3개월 CEO 대시보드 이메일 오픈율 확인

2. "자동 요약이 원본 대시보드보다 유용하다" (위험도: 3, 난이도: 2) → Priority: 6
   → 실험: 5일간 마크다운 요약본 + 대시보드 원본 함께 발송 → 어느 것을 더 보는지 추적

Feasibility Assumptions:
1. "BI 플랫폼 API에 인증 권한이 있다" (위험도: 5, 난이도: 1) → Priority: 5
   → 실험: API 문서 확인 + 테스트 호출 10회 실행 → 성공/실패 기록

2. "하루 5분 이내에 대시보드 데이터를 수집 가능하다" (위험도: 3, 난이도: 2) → Priority: 6
   → 실험: 프로토 스크립트로 수집 → 소요 시간 측정

Reliability Assumptions:
1. "프롬프트가 매일 일관된 품질의 요약을 생성한다" (위험도: 4, 난이도: 3) → Priority: 12
   → 실험: 동일 데이터로 프롬프트 20회 반복 → 요약 일관성 평가

2. "수치 오류(오차)가 1% 이하다" (위험도: 5, 난이도: 2) → Priority: 10
   → 실험: 에이전트 요약 vs 수동 검증 오차 측정

Ethics Assumptions:
1. "CEO가 에이전트 판단을 신뢰한다" (위험도: 3, 난이도: 2) → Priority: 6
   → 실험: Shadow Mode 1주 → 에이전트 요약 vs CEO 최종 판단 비교

Top 3 우선순위:
1. "수치 오류가 1% 이하인가?" (Priority: 10)
2. "프롬프트 일관성이 충분한가?" (Priority: 12)
3. "API 권한이 있는가?" (Priority: 5)

선택 근거: 신뢰성과 실현가능성의 위험이 최고
```

### Bad Example

```
❌ 가정이 너무 일반적:
"에이전트가 작동할 것이다"
"사용자가 좋아할 것이다"
→ 구체성 부족; 검증 불가능

❌ Priority 점수 계산 오류:
Assumption: "API가 있으니까 가능하다"
→ 위험도 1, 난이도 1 → Priority: 1
→ But: 실제로는 "권한이 없을 수 있다" (위험도 5), "Rate Limit가 있을 수 있다" (위험도 3)
→ 점수 재평가 필요; 구체적 세부 가정으로 분할

❌ Ethics 위험 무시:
"자동으로 고객 결제 승인하는 에이전트"
→ Value/Feasibility만 검토
→ But: 할루시네이션으로 부정 고객에게 승인하면? 법적 책임? 감사 로그?
→ Ethics 가정 최소 3개 추가; 위험도 5 항목은 `hitl` 검토 강제

❌ 검증 실험이 불가능:
"시장에서 이 에이전트가 받아들여질 것인가?"
→ 2일 이내에 시장 검증 불가능
→ 재정의: "3일간 5명의 타겟 사용자와 인터뷰 → 최소 3명이 '유용하다' 답할 것인가?"

❌ Top 3 가정이 모두 Reliability만:
→ Value 검증이 건너뜀
→ 기술적으로 완벽해도 아무도 안 쓰는 에이전트가 될 위험
```

---

### 참고
- 원본 프레임워크: 일반 PM 가정 검증(8 risk categories) → 에이전트 특화 4축(Value/Feasibility/Reliability/Ethics)으로 재편
- Reliability / Ethics 축: Byeonghyeok Kwak의 엔터프라이즈 에이전트 거버넌스 논의 기반
- 설계자: AI PM Skills Contributors, 2026-03

---

## Build-or-Buy 판단 프레임워크

`--mode build-or-buy`로 호출하거나, Feasibility 가정 검증 후 "직접 만들 것인가" 결정이 필요할 때 이 섹션을 활성화한다.

**핵심 판단 기준 4가지**

1. **차별화 필수 여부** — 이 에이전트가 제품의 핵심 경쟁력인가? YES → Build. NO → 외부 솔루션 탐색 우선.
2. **외부 솔루션 충족도** — 기존 솔루션이 요구사항의 70% 이상을 충족하는가? YES → Buy/No-Code. NO → Build 검토.
3. **도메인 특화 로직** — 우리 데이터나 판단 로직이 반드시 필요한가? YES → Build. NO → No-Code 플랫폼으로 검증 후 결정.
4. **하이브리드 전략** — 오케스트레이션/도메인 레이어는 Build, 외부 연동/UI 레이어는 Buy/No-Code로 분리할 수 있는가? 레이어가 4개 이상이면 단순화(핵심 2개 레이어만 Build).

**결정 재검토 트리거**: 유지보수 시간 > 월 20시간이면 Buy 전환 검토. 외부 솔루션 비용 > 월 $500이면 Build 전환 검토. No-Code로 검증 완료 후 스케일 필요 시 Build 전환.

---

## Further Reading
- Alberto Savoia, *The Right It* — Assumption validation and pretotyping
- Teresa Torres, *Continuous Discovery Habits* — Assumption mapping

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
