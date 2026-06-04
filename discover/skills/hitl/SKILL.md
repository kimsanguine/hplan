---
name: hitl
description: "Design where and how humans should intervene in agent workflows. Define automation boundaries, escalation triggers, and approval gates. Use when building agents that make consequential decisions, handle sensitive data, or operate in domains where errors have high impact. Prevents the 'fully autonomous' default trap."
argument-hint: "[agent workflow to design]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

## Core Goal

- 에이전트의 각 작업마다 적절한 자동화 레벨(1~5)을 결정하고, 인간이 개입해야 할 트리거 조건을 명시하여 신뢰성과 안전성을 확보
- 가역성(되돌릴 수 있는가)과 오류 영향도(피해 범위)의 2축 매트릭스를 통해 객관적으로 자동화 경계를 결정
- Approval Gate, Confidence Threshold, Periodic Audit, Escalation Chain, Shadow Mode 등 5가지 HITL 패턴 중 업무 특성에 맞는 것을 선택

---

## Trigger Gate

### Use This Skill When
- 에이전트가 의사결정, 송금, 고객 대면, 데이터 삭제 등 "중요한 작업"을 할 때
- "충분히 정확할까?"보다는 "100% 자율이어도 될까?"라는 고민이 있을 때
- 에이전트의 오류가 고객 손실, 법적 책임, 평판 손상으로 이어질 수 있을 때
- 초기 배포 또는 새로운 에이전트를 출시할 때 (사용자 신뢰 구축 전)

### Route to Other Skills When
- HITL 설계가 완료된 후 에이전트 프롬프트와 인스트럭션을 작성해야 할 때 → `deliver/agent-setup` — Failure Handling에 HITL 전략 반영
- 에이전트의 신뢰도를 측정하고 Full Autonomous로 전환할지 판단해야 할 때 → `operate/metrics-design`
- 에이전트 제품을 외부에 출시할 때 신뢰 구축 시퀀스를 설계해야 할 때 → `architect/strategy`
- *빌드 시점* PreToolUse 차단 (PRD/spec 파일 작성을 게이트 미통과 시 막기) → `hooks/gate_guard.py` (hplan plugin). 이 skill의 hitl은 *agent 런타임* — 시점이 다름.

### Boundary Checks
- **설계 vs 운영**: HITL은 "어디에 인간이 개입할지를 설계"하는 것이지, 실제로 인간을 배치하거나 모니터링 대시보드를 만드는 것은 아님 — 구현은 팀이 담당
- **모든 작업에 필수**: HITL은 선택이 아니라 필수 — 완전 자율 에이전트(Level 5)는 극히 제한적인 경우에만 정당화됨 (낮은 오류 영향도 + 높은 가역성)

---

## Human-in-the-Loop Design

에이전트의 가장 위험한 기본값: **"전부 자동화하자"**

완전 자율 에이전트는 이론적으로 매력적이지만, 현실에서는:
- 할루시네이션이 조용히 실행됨 → 잘못된 결정이 누적
- 에러가 발생해도 아무도 모름 → 피해가 증폭
- 사용자 신뢰 상실 → 에이전트 전체를 불신

Human-in-the-Loop(HITL)은 **어디에 인간 판단을 넣을지** 의도적으로 설계하는 것입니다.

---

### 자동화 스펙트럼 (5단계)

모든 에이전트 작업은 이 스펙트럼 위에 놓입니다:

```
Level 1: Manual          — 에이전트가 정보 제공, 인간이 모든 판단 + 실행
Level 2: Suggest          — 에이전트가 추천, 인간이 승인 후 실행
Level 3: Act-and-Report   — 에이전트가 실행 후 결과 보고, 인간이 검토
Level 4: Act-and-Escalate — 에이전트가 실행, 이상 시에만 인간 개입
Level 5: Full Autonomous  — 에이전트가 판단 + 실행 + 모니터링 전부
```

> ⚠️ Level 5는 에이전트 오류의 영향이 극히 낮은 경우에만 적용.
> 대부분의 에이전트는 Level 2~4가 적합합니다.

---

### 개입 지점 결정 매트릭스

작업별로 자동화 레벨을 결정하는 2축 매트릭스:

```
              오류 영향도
              낮음  →  높음
가  높음  │ Level 4  │ Level 2   │
역         │ (자동+  │ (인간     │
성         │  이상    │  승인     │
           │  감지)   │  필수)    │
   낮음  │ Level 5  │ Level 3   │
           │ (완전    │ (실행후   │
           │  자동)   │  보고)    │
```

**가역성**: 에이전트의 행동을 되돌릴 수 있는가?
- 높음: 파일 수정(되돌리기 가능), 알림 전송, 정보 수집
- 낮음: 이메일 발송, 결제, 데이터 삭제, 외부 API 호출

**오류 영향도**: 에이전트가 틀렸을 때 피해 범위는?
- 낮음: 내부 메모, 로그 기록, 참고 자료 정리
- 높음: 고객 대면, 금전 관련, 법적 영향, 대외 커뮤니케이션

---

### HITL 패턴 라이브러리

**Pattern 1 — Approval Gate (승인 게이트)**
```
용도: 에이전트가 초안을 만들고, 인간이 승인 후 전송
예시: 이메일 자동 작성 → 인간 검토 → 발송
구현: 에이전트 출력 → 임시 파일 저장 → 알림 → 승인 대기
```

**Pattern 2 — Confidence Threshold (신뢰도 임계값)**
```
용도: 에이전트의 판단 신뢰도가 낮을 때만 인간 개입
예시: 이메일 분류 → 신뢰도 80% 이상이면 자동 처리, 미만이면 인간 확인
구현: 에이전트 출력에 confidence score 포함 → 임계값 비교
```

**Pattern 3 — Periodic Audit (주기적 감사)**
```
용도: 에이전트가 자율 실행하되, 주기적으로 인간이 결과 검토
예시: 일일 뉴스 브리핑 → 주 1회 품질 리뷰
구현: 실행 로그 자동 수집 → 주간 리포트 생성 → 인간 리뷰
```

**Pattern 4 — Escalation Chain (에스컬레이션 체인)**
```
용도: 에이전트 → 팀원 → 매니저 단계별 에스컬레이션
예시: 고객 문의 → 자동 응답 시도 → 실패 시 담당자 알림 → 긴급 시 매니저
구현: 에스컬레이션 레벨별 트리거 조건 + 타임아웃 정의
```

**Pattern 5 — Shadow Mode (섀도우 모드)**
```
용도: 에이전트를 배포 전에 인간과 병렬 실행하여 품질 비교
예시: 에이전트가 결정을 내리되 실행 안 함 → 인간 결정과 비교 → 정확도 측정
구현: 2주 shadow period → 90% 이상 일치 시 자동화 전환
```

---

### 설계 체크리스트

에이전트 설계 시 모든 작업에 대해 확인:

```
☐ 이 작업의 자동화 레벨은? (1~5)
☐ 인간 개입 트리거 조건은? (임계값, 에러, 시간)
☐ 개입 방법은? (알림 채널, 승인 방법, 타임아웃)
☐ 개입 후 워크플로우는? (수정 후 재실행? 인간이 완료?)
☐ 에이전트 실행 로그가 감사 가능한가?
☐ Shadow Mode 기간이 계획되어 있는가?
```

---

### 사용 방법

`/human-in-loop-design [에이전트 이름 또는 워크플로우]`

---

### Instructions

You are helping design **Human-in-the-Loop controls** for: **$ARGUMENTS**

**Step 1 — 작업 목록 작성**
에이전트가 수행하는 모든 작업을 나열한다

**Step 2 — 각 작업의 가역성/오류 영향도 평가**
2축 매트릭스를 적용하여 자동화 레벨(1~5) 결정

**Step 3 — HITL 패턴 선택**
각 작업에 적합한 HITL 패턴 매칭:
- 대외 커뮤니케이션 → Approval Gate
- 판단 작업 → Confidence Threshold
- 반복 실행 → Periodic Audit
- 다단계 복잡 작업 → Escalation Chain

💡 **아키텍처 참고**: Supervisor → 조건부 분기 → HITL 패턴은 !domain에서 상세 설명합니다. 위험도별 차등 적용, SLA 설정, 자동 에스컬레이션 등의 실무 구현 사례를 확인하세요.

**Step 4 — 개입 트리거 정의**
각 개입 지점의 구체적 조건:
- 신뢰도 임계값 (%)
- 에러 유형별 대응
- 타임아웃 시간

**Step 5 — Shadow Mode 계획**
배포 전 병렬 실행 기간과 전환 기준 정의

**Step 6 — 설계 체크리스트 확인**
모든 항목이 완료됐는지 검증

**Step 7 — 다음 단계 연결**
- `deliver/agent-setup`의 Failure Handling 섹션에 HITL 설계 반영
- `/agent-prd-template`의 Section 7에 Human-in-the-loop 트리거 명시

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| HITL 설계 후에도 에이전트가 예상치 못한 오류 발생 | "이건 우리가 예상 못 한 상황이었어" 사용자 불평 발생 | Shadow Mode 기간 연장 또는 자동화 레벨 하향 (e.g., Level 3 → Level 2); 새로운 에러 시나리오를 HITL 매트릭스에 추가 |
| Approval Gate를 설치했는데 승인자가 매번 자동으로 승인만 함 | "매번 승인하기만 하면 되네" 승인자 태도 → 실질적 HITL 작동 불함 | 승인 프로세스 재설계: 임계값 기반 필터링 추가 또는 주기적 감사로 전환; 또는 자동화 레벨 상향 고려 |
| Escalation Chain이 너무 깊어져서(팀원 → 매니저 → 임원) 응답 지연 발생 | "에스컬레이션 완료까지 3일 걸린다" 타임아웃 초과 | 체인 단순화: 매니저까지만 (2단계) 또는 신뢰도 임계값으로 필터링해서 에스컬레이션 빈도 자체를 줄임 |
| Shadow Mode 기간이 너무 길어져서 프로덕션 배포 미루어짐 | "어느 정도면 충분하지?" 팀이 계속 Shadow 모드에 머무름 | Shadow Mode 전환 기준을 명확히 정의: "90% 이상 일치 시 전환" 또는 "2주 후 자동 전환" (리스크 재평가 후) |

---

## Quality Gate

- 모든 에이전트 작업이 목록화되어 있고, 각 작업에 자동화 레벨(1~5)이 할당되어 있는가? (Yes/No)
- 2축 매트릭스(가역성 × 오류 영향도)를 사용하여 각 작업의 레벨이 객관적으로 결정되었는가? (Yes/No)
- 각 작업의 HITL 패턴(Approval Gate/Confidence Threshold/Periodic Audit/Escalation Chain/Shadow Mode)이 선택되고, 선택 근거가 명시되어 있는가? (Yes/No)
- 각 개입 지점의 구체적인 트리거 조건이 정의되어 있는가? (예: "신뢰도 < 80%", "에러 > 1개/일", "타임아웃 > 2시간") (Yes/No)
- Shadow Mode 기간과 전환 기준이 명확히 정의되어 있는가? (예: "2주, 90% 일치도 달성 시") (Yes/No)

---

## Examples

### Good Example

```
Agent: "자동 고객 이메일 응답 에이전트"

작업 목록:

1. 이메일 수신 및 분류
   - 가역성: 높음 (분류 결과만 파일에 기록, 이메일은 건드리지 않음)
   - 오류 영향도: 낮음 (잘못 분류해도 사용자가 수정 가능)
   - 레벨: 4 (Act-and-Escalate)
   - HITL 패턴: Periodic Audit (주 1회 분류 정확도 리뷰)

2. 자동 응답 이메일 생성
   - 가역성: 낮음 (생성된 이메일을 발송하지 않았더라도 콘텐츠가 한 번 만들어짐)
   - 오류 영향도: 높음 (부정확한 응답 → 고객 신뢰 손실)
   - 레벨: 2 (Suggest)
   - HITL 패턴: Approval Gate
   - 트리거: 에이전트가 응답 초안 생성 → 담당자 검토 → 승인/수정 후 발송

3. 승인된 응답 자동 발송
   - 가역성: 낮음 (발송 후 회수 어려움)
   - 오류 영향도: 높음 (잘못된 내용이 고객에게 즉시 도달)
   - 레벨: 2 (Suggest)
   - HITL 패턴: Confidence Threshold + Approval Gate (자신도 80% 이상일 때만 초안 생성; 초안은 항상 승인 필수)

Shadow Mode:
- 기간: 2주
- 전환 기준:
  - 에이전트 분류 정확도 > 85%
  - 생성된 응답을 사람이 수정 없이 승인하는 비율 > 80%
  - 발송 후 고객 재문의율 < 5%
```

### Bad Example

```
❌ 모든 작업이 Level 5 (완전 자동):
"에이전트가 모든 이메일을 자동으로 분류하고 응답 발송"
→ 위험도 매우 높음; 할루시네이션으로 잘못된 응답 발송 시 고객 손실
→ 최소한 Level 2~3 필요 (Approval Gate 또는 Confidence Threshold)

❌ HITL 패턴이 명확하지 않음:
"사람이 확인하도록 함"
→ 구체성 부족
→ "어떤 방식으로?" (알림? 대시보드? 이메일?)
→ "승인 기준이 뭐지?" (신뢰도 임계값? 에러 카운트?)
→ 패턴명 명시 필수: "Approval Gate" or "Confidence Threshold"

❌ 트리거 조건이 없음:
"오류 발생 시 에스컬레이션"
→ "오류"의 정의가?
→ "에스컬레이션" 경로가?
→ 구체화 필수: "신뢰도 < 60% or 에러 카운트 > 3개/시간 → 팀리더 알림 → 2시간 응답 없으면 매니저"

❌ Shadow Mode 전환 기준이 없음:
"몇 주 동안 Shadow 모드로 감시"
→ "몇 주?" "충분히 정확해지면?"
→ 구체적 기준 명시: "2주 또는 1000개 이메일 처리 후, 90% 이상 일치도 달성 시 Level 4로 전환"

❌ 초기 신뢰도 평가 없음:
"프로덕션 배포 후 모니터링"
→ But: Shadow Mode에서 미리 평가했다면 배포 리스크 사전 감지 가능
→ 배포 전 Shadow Mode 필수
```

---

### 참고
- 설계자: AI PM Skills Contributors, 2026-03
- 자동화 스펙트럼: SAE J3016 자율주행 레벨 분류에서 영감
- Shadow Mode: production cron job 배포 전 검증 프로세스 기반
- Confidence Threshold: 에이전트 오케스트레이션 운영 경험 (2026-02)

---

## Further Reading
- AI Agent Design Patterns — Human-in-the-loop escalation strategies
- Anthropic, "Building Effective Agents" (2024) — Agent autonomy boundaries

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
