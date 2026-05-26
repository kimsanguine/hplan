---
name: orchestration
description: "Select and design the right orchestration pattern for multi-agent systems. Evaluate Sequential, Parallel, Router, and Hierarchical patterns against your use case requirements. Use when deciding how multiple agents should coordinate, share context, or delegate tasks to each other."
argument-hint: "[multi-agent scenario]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# Orchestration Pattern

> 멀티 에이전트 오케스트레이션 패턴 선택 및 설계

## Core Goal

- 에이전트 간 협력 방식(순차, 병렬, 라우팅, 계층)을 요구사항에 맞게 선택하여 불필요한 복잡성 제거하고 성능 최적화
- 각 패턴의 장단점을 명확히 이해하고 지연시간, 에러율, 비용을 예측하는 의사결정 프레임워크 제공
- "가장 간단한 패턴부터 시작"하는 점진적 업그레이드 원칙 적용

## Trigger Gate

### Use This Skill When

- 2개 이상의 에이전트가 협력해야 하는 시스템 설계 또는 평가
- 기존 오케스트레이션이 성능 문제(지연, 비용)를 보이는 경우
- 패턴 선택의 의사결정을 문서화하고 정당화해야 하는 경우

### Route to Other Skills When

- 선택한 패턴의 세부 구현 (3-tier 위계 구조) → orchestration (Hierarchical pattern 상세 섹션 참조)
- 입력 분류를 통한 agent 라우팅 로직 구현 → router (모델 선택 확장)
- 멀티 에이전트 간 메모리 공유 → memory-arch (저장소 전략)
- 패턴의 경제성 분석 → biz-model (비용 모델)

### Boundary Checks

- 단일 에이전트로 충분하면 → 오케스트레이션 패턴 불필요, 단일 prompt 또는 routing만 고려
- 패턴이 너무 복잡하면 → "가장 간단한 패턴"으로 시작 원칙 위반, 재평가 필요
- 에러 복구 전략이 없으면 → 선택한 패턴을 안전하게 구현 불가, 먼저 에러 처리 정의

## 개념

에이전트 시스템의 복잡도와 요구사항에 따라 적절한 오케스트레이션 패턴을 선택한다. 잘못된 패턴 선택은 불필요한 복잡성이나 성능 병목을 만든다.

## Instructions

You are selecting and designing an **orchestration pattern** for: **$ARGUMENTS**

### Step 1 — Assess Requirements

Answer these questions to determine pattern fit:
- How many distinct tasks are involved?
- Are tasks dependent on each other's outputs?
- Is the workflow deterministic or dynamic?
- What is the latency tolerance?
- What is the error tolerance?

### Step 2 — Pattern Selection Matrix

| Pattern | When to Use | Complexity | Latency |
|---------|------------|------------|---------|
| **Sequential Chain** | Tasks have strict dependencies | Low | High (sum of all) |
| **Parallel Fan-out** | Independent tasks, same input | Medium | Low (max of all) |
| **Router** | Input determines which agent | Medium | Low (single path) |
| **Hierarchical** | Complex, multi-level workflows | High | Variable |
| **Event-Driven** | Reactive, async workflows | High | Variable |

### Step 3 — Pattern Deep Dive

#### Sequential Chain
```
Input → Agent A → Agent B → Agent C → Output
```
- Best for: pipelines where each step transforms data
- Risk: single point of failure, high total latency
- PM Example: Research → Analysis → Report Draft → Review

#### Parallel Fan-out / Fan-in
```
         ┌→ Agent A ─┐
Input ───┤→ Agent B ──┤→ Aggregator → Output
         └→ Agent C ─┘
```
- Best for: same task on different data segments
- Risk: aggregation complexity, slowest worker bottleneck
- PM Example: Analyze 5 competitors simultaneously

#### Router (Classifier → Specialist)
```
Input → Router → Agent A (if type X)
              → Agent B (if type Y)
              → Agent C (if type Z)
```
- Best for: varied input types needing different expertise
- Risk: router misclassification
- PM Example: Triage user feedback by category

#### Hierarchical (Prometheus-Atlas)
```
Orchestrator → Sub-orchestrator A → Workers
             → Sub-orchestrator B → Workers
```
- Best for: complex, multi-phase projects
- Risk: over-engineering, communication overhead
- PM Example: Full product launch planning

##### Hierarchical 패턴 상세 — Prometheus-Atlas-Worker

3-tier 구조의 표준 구현. 각 계층의 역할:

| Tier | Role | Decision Type | Example |
|------|------|---------------|---------|
| Prometheus | Strategic direction | What & Why | "Q2 경쟁 분석 필요" |
| Atlas | Task orchestration | How & When | "5개 경쟁사 분배, 워커 할당, 결과 통합" |
| Workers | Task execution | Do | "경쟁사 X 가격 페이지 수집" |

**Atlas 레이어 설계 (핵심)**:
1. Task Decomposition — 목표를 워커 단위로 분해
2. Worker Selection — 작업 유형에 최적 워커 매칭
3. Dependency Management — 작업 순서 관리
4. Result Aggregation — 워커 출력 통합
5. Quality Gate — 상위로 전달 전 검증
6. Error Recovery — 재시도 또는 에스컬레이션

**워커 설계 4원칙**: 단일 책임 · Stateless 실행 · 구조화된 출력 · 명확한 실패 반환

**안티패턴**:
| 패턴 | 문제 | 해결 |
|------|------|------|
| God Atlas | Atlas가 실행 작업도 직접 수행 | Atlas + Workers 분리 |
| Worker Chaining | 워커가 다른 워커 직접 호출 | Atlas를 통해 라우팅 |
| Missing Prometheus | 전략 계층 없이 Workers만 동작 | 항상 전략 계층 유지 |
| Over-orchestration | 단순 태스크에 3-tier 적용 | 단일 에이전트 먼저 검토 |

### Step 4 — Design the Selected Pattern

For the chosen pattern, specify:
1. **Agent Roles**: What each agent does
2. **Data Flow**: Input/output format between agents
3. **Error Handling**: What happens when an agent fails
4. **Scaling Strategy**: How to handle increased load

### Step 5 — Complexity Check

Before finalizing, ask:
- Could a single well-prompted agent do this?
- Is the orchestration overhead justified by the benefit?
- What is the simplest pattern that meets requirements?

**Rule**: Start with the simplest pattern. Upgrade only when proven necessary.

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|-----|-----|
| 선택한 패턴이 실제 요구사항과 안 맞음 | 배포 후 지연시간 초과 또는 에러율 높음 | 요구사항 재분석, 패턴 전환 (예: 순차 → 병렬), 또는 하이브리드 패턴 도입 |
| 병렬 패턴에서 느린 agent 병목 | Fan-in 이후 가장 느린 agent 대기 시간이 전체 지연의 80% | 느린 agent 분해, 타임아웃 설정, 또는 품질 저하하고 빨리 반환 |
| 라우터 분류 오류: 입력이 잘못된 agent로 갈당 | 사용자 질문이 분류 기준과 애매해서 틀린 agent 호출 | 라우터 프롬프트 개선, 또는 라우터 재시도/폴백 전략 추가 |
| 계층 오케스트레이션 오버헤드: 너무 복잡해짐 | 통신 레이어만 해도 전체 지연 50% | 계층 수 감소 (3-tier → 2-tier), 또는 간단한 패턴으로 롤백 |

## Quality Gate

- [ ] 요구사항 명확화: 작업 수, 의존성, 지연시간 허용치, 에러 허용치 문서화 (Yes/No)
- [ ] 패턴 선택 정당화: 평가 행렬에 따라 선택한 패턴의 ranking 확인 (Yes/No)
- [ ] Agent 역할 정의: 각 agent의 입력/출력 형식, 책임 범위 명시 (Yes/No)
- [ ] 에러 처리: 각 agent 실패 시 대응 (재시도, 폴백, 중단) 전략 정의 (Yes/No)
- [ ] 복잡도 검증: "이 패턴이 가장 간단한가?" 재확인 (Yes/No)

## Examples

### Good Example

```
시나리오: "고객 피드백 분석 시스템"
- 사용자가 피드백 제출
- 감정 분석, 카테고리 분류, 우선순위 평가 필요
- 지연시간 <5초, 에러율 <1%

[요구사항 분석]
- 작업 수: 3개 (감정 분석, 분류, 우선순위)
- 의존성: 없음 (동일 입력으로 모두 독립 실행)
- 지연 요구: 낮음 (<5초 여유)
- 에러 허용: 매우 낮음 (<1%)

[패턴 평가]
- Sequential: 불필요 (순서 의존성 없음)
- Parallel Fan-out/Fan-in: 우수함 ✓
  - 3개 agent 동시 실행
  - 지연 = max(3개 agent) ≈ 1.5초 < 5초
  - Aggregator에서 3개 결과 통합
- Router: 부적절 (분류 이전의 문제)
- Hierarchical: 오버엔지니어링

[선택] Parallel Fan-out/Fan-in

[설계]
Input (피드백 텍스트)
    ↓
    ├→ Sentiment Agent (1초)
    ├→ Category Agent (0.8초)
    └→ Priority Agent (1.2초)
         ↓
Aggregator (0.3초)
  - 3개 출력 통합
  - 모순 검사 (예: high priority인데 negative?)
  - JSON으로 정렬
    ↓
Output (json: {sentiment, category, priority})

[에러 처리]
- 단일 agent 실패: timeout 2초 설정 → 해당 항목 null로 반환
- Aggregator 실패: 원본 3개 agent 출력만 반환 (부분 성공)
- 전체 실패: 사용자에게 재시도 권유

[결과]
- 평균 지연: 1.8초 (목표 5초 vs 실제 <2초)
- 에러율: 0.8% (목표 <1% 달성)
- 비용: 3개 agent × $0.05 = $0.15/요청
```

### Bad Example

```
반사례 1: 불필요한 Sequential
"우선 감정 분석을 한 후, 그 결과로 카테고리를 결정"
- 실제로는 독립적
- Sequential로 묶으니까 지연 = 3초 (병렬이면 1.5초)
- 단순히 복잡하게 만든 것

반사례 2: 계층 오버엔지니어링
Sequential:
  Agent A → Agent B → Orchestrator → Agent C → Agent D
- 4개 agent 순차 실행
- Orchestrator도 순차 흐름 관리
- 지연 = 4초 + orchestration overhead = 5초 초과
- 병렬이면 1.5초 가능

반사례 3: 라우터 오류 처리 없음
"사용자 질문을 봐서 영업용/기술용 agent로 라우팅"
- 명확하지 않은 질문 → 라우터가 잘못 선택
- 대체 agent나 재분류 로직 없음
- "역시 AI는 이해 못하네" → 신뢰도 하락

반사례 4: 복잡함 심화
Hierarchical + Router + Sequential 결합
- 비용과 관리 복잡도 증폭
- "왜 이렇게 느려?" 원인 파악 어려움
```

---

## Further Reading
- Anthropic, "Building Effective Agents" (2024) — Workflow vs agent patterns
- LangGraph Documentation — Orchestration pattern implementations

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
