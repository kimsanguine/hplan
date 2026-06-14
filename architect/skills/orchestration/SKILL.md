---
name: orchestration
description: "Select and design the right orchestration pattern for multi-agent systems. Evaluate Sequential, Parallel, Router, and Hierarchical patterns against your use case requirements. The Router pattern covers both agent selection (classify input to the right specialist) and model selection (route tasks to the right LLM by complexity to balance cost, latency, quality, and fallback chains). Use when deciding how multiple agents should coordinate, share context, delegate tasks, or which model each task should run on."
argument-hint: "[multi-agent scenario] [--pattern router]"
allowed-tools: ["Read", "Write"]
model: inherit
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
- 작업별 LLM 모델 선택/비용 최적화 → orchestration --pattern router (Model Routing 상세 섹션 참조)
- 멀티 에이전트 간 메모리 공유 → memory-arch (저장소 전략)
- 패턴의 경제성 분석 → strategy --focus biz-model (비용 모델)

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

##### Router 패턴 상세 — 두 가지 라우팅 차원

> **중요**: "Router 패턴"에는 두 가지 직교(orthogonal) 차원이 있다. 둘은 함께 쓸 수 있으며 혼동하면 안 된다.
>
> | 차원 | 무엇이 바뀌나 | 목적 | 사용 시점 |
> |------|-------------|------|----------|
> | **Agent Routing (에이전트 선택)** | 에이전트 자체 (도구/전문성) | 전문성 향상 (정확도 ↑) | 다른 전문성/도구가 필요한 작업으로 분기 |
> | **Model Routing (모델 선택)** | 에이전트는 동일, LLM 모델만 | 비용 최적화 (30-60% 절감) | 같은 작업을 다양한 LLM으로 처리 가능 |
>
> **함께 사용 (권장)**:
> ```
> Input → [Agent Router]: 어떤 에이전트? (General vs Bash vs Custom)
>           ↓
>       선택된 에이전트 내에서:
>       [Model Router]: 어떤 모델? (T1 vs T2 vs T3)
>           ↓
>       최종 응답
> ```
> 이 구조로 **에이전트 전문성 + 모델 비용 최적화**를 동시에 달성한다.

위의 "Router (Classifier → Specialist)" 기본 다이어그램은 **Agent Routing**에 해당한다. 아래는 **Model Routing**의 상세 설계로, `router` 스킬에서 흡수한 내용이다.

###### Model Routing — 모델 선택 전략

작업 복잡도에 따라 T1(저비용 경량) ~ T4(고성능 전문) 모델을 선택하여 비용 40-80% 절감하면서 품질(>90%)을 유지한다. 모든 작업에 최고 성능 모델을 쓰는 것은 비용 낭비다.

**Trigger Gate (Model Routing을 쓸 때)**:
- 여러 모델을 쓰는 에이전트 시스템의 비용 최적화 필요
- 간단한 작업에 비싼 모델을 쓰고 있는 경우
- 성능과 비용의 트레이드오프를 의도적으로 설정해야 하는 경우

**Boundary Checks (Model Routing 건너뛰기)**:
- 단일 모델만 사용 → 라우팅 불필요
- 모든 작업이 고복잡도 → T3 고정 (라우팅 복잡도보다 이득 적음)
- 라우팅 오버헤드 > 저가 모델 절감 → 라우팅 건너뛰기

**Step 1 — Task Classification**: 각 작업을 복잡도로 분류

| Tier | Complexity | Examples | Recommended Model Class |
|------|-----------|----------|----------------------|
| T1 | Simple extraction | Data parsing, formatting, classification | Small/Fast (Haiku, GPT-4o-mini) |
| T2 | Standard reasoning | Summarization, comparison, basic analysis | Mid (Sonnet, GPT-4o) |
| T3 | Complex reasoning | Strategy, creative, multi-step analysis | Large (Opus, o1) |
| T4 | Specialized | Code generation, math, domain-specific | Specialist (Claude Code, Codex) |

**Step 2 — Routing Decision Matrix**: 워크플로우의 각 작업에 대해
```
Task: [name]
├── Input complexity: Low / Medium / High
├── Output quality sensitivity: Low / Medium / High
├── Latency requirement: <1s / <5s / <30s / Flexible
├── Cost tolerance: $ / $$ / $$$
└── Recommended tier: T1 / T2 / T3 / T4
```

**Step 3 — Cost Comparison (비용)**: 라우팅 vs 단일 모델 비용 영향 계산

| Approach | Monthly Cost | Quality Score |
|----------|-------------|---------------|
| All T3 (premium) | $____ | 95/100 |
| Routed (mixed) | $____ | 92/100 |
| All T1 (budget) | $____ | 70/100 |

**Target**: Routed 접근이 premium 비용의 <40%로 >90% 품질 달성.

총 비용 계산 프레임워크 (정확한 경제성 평가):
```
총 비용 = API 호출 비용 + 지연시간 비용 + 재처리 비용
1. API 호출 비용 = Σ(모델별 토큰 단가 × 예상 호출 수)
2. 지연시간 비용 = 평균 지연시간(초) × 시간당 비용 × 월간 요청 수
   (사용자 대기 시간 = 생산성 손실로 환산)
3. 재처리 비용 = 오류율 × 재처리 모델 비용 × 월간 요청 수
   (폴백 발동 시 추가 비용)
```

**Step 4 — Fallback Strategy (fallback-chain)**: graceful degradation 설계
```
Primary: [preferred model]
  ↓ if failed/timeout
Fallback 1: [alternative model]
  ↓ if failed/timeout
Fallback 2: [minimum viable model]
  ↓ if all fail
Error: [return structured error to user]
```
- 폴백 체인 다양화: 다른 제공자의 동급 모델 (Anthropic Sonnet → OpenAI GPT-4o) → 한 등급 낮은 모델(품질 저하 수용) → 캐시된 답변 → 사용자 재시도 요청
- 폴백 발동 빈도 추적 (>10% = 라우팅 규칙 재검토 신호)

**Step 5 — Quality Gate (2단계)**:
- Stage 1 (라우팅 전): 라우터 분류 신뢰도 > 85%이면 선택 모델로 라우팅, ≤85%이면 clarification 실행. 목표 오분류율 <10%.
- Stage 2 (라우팅 후): 출력 품질 점수 <80%이면 폴백 모델로 재시도, 그래도 실패 시 T3로 최종 재시도. 목표 최종 품질 >90%.

**Step 6 — Monitoring Plan**: 주 1회 추적
- 모델 티어별 비용
- 라우팅 정확도 (올바른 티어 선택 비율)
- 폴백 발동 빈도 (<5% 목표)
- 티어별 품질 점수

**Output — 라우팅 테이블**:
```
┌─────────────┬──────┬──────────┬───────┐
│ Task         │ Tier │ Model    │ $/run │
├─────────────┼──────┼──────────┼───────┤
│ [task 1]    │ T1   │ [model]  │ $0.01 │
│ [task 2]    │ T2   │ [model]  │ $0.05 │
│ [task 3]    │ T3   │ [model]  │ $0.15 │
└─────────────┴──────┴──────────┴───────┘
Monthly estimate: $____  vs all-premium: $____ (___% savings)
```

**Model Routing Failure Handling (latency/fallback 포함)**:

| 실패 상황 | 감지 | 대응 |
|---------|-----|-----|
| 라우팅 오분류: T1 모델이 충분치 않은 작업으로 갈림 | 출력 품질 점수 <70%, "부정확함" 피드백 | 즉시 T2로 재실행(폴백), 라우팅 규칙 업데이트 |
| 비용 절감 미달: 고비용 모델 호출 비율 높음 | 실제 T1 사용률 10% (예상 50%) | 라우팅 threshold 낮춤, 또는 T1 능력 강화 |
| 모델 API 장애: T2 모델 다운 (latency timeout) | T2 호출 timeout | 폴백 1: T3 재시도, 모두 실패 시 사용자 보고 |
| 품질-비용 균형 붕괴: 비용↓ 품질<80% | 만족도 95% → 82% | 라우팅 회귀, 더 높은 티어로 보수적 조정 |

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

### Model Routing — 구현 레퍼런스 (router 패턴 통합)
!`cat references/model-routing.md 2>/dev/null || echo ""`

### Model Routing — Good Example
!`cat examples/model-routing-good.md 2>/dev/null || echo ""`

### Model Routing — Bad Example
!`cat examples/model-routing-bad.md 2>/dev/null || echo ""`
