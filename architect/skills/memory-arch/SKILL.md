---
name: memory-arch
description: "Design an agent memory system — working memory, episodic memory, semantic memory, and procedural memory. Use when building agents that need to remember context across sessions, learn from interactions, or maintain persistent knowledge. Covers storage strategy, retrieval patterns, and context management."
argument-hint: "[agent requiring persistence]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# Memory Architecture

> 에이전트 메모리 시스템 설계 — 단기 컨텍스트, 장기 저장, 검색 전략

## Core Goal

- 단일 실행의 컨텍스트 윈도우를 넘어 실행 간 학습과 기억을 유지하는 메모리 아키텍처 설계하여 에이전트의 진화 가능하게 함
- 4가지 메모리 유형(Working, Episodic, Semantic, Procedural)을 각각 적절한 저장소에 배치하여 검색 효율성과 비용을 최적화
- 제한된 컨텍스트 윈도우 내에서 가장 관련성 높은 메모리만 주입하는 검색 및 랭킹 전략 수립

## Trigger Gate

### Use This Skill When

- 에이전트가 여러 실행(세션)에서 일관된 동작을 해야 하는 경우
- 사용자 선호도, 과거 상담 내용, 또는 도메인 지식을 기억해야 하는 에이전트
- 에이전트가 각 상호작용에서 학습하고 개선되어야 하는 경우

### Route to Other Skills When

- 메모리가 플라이휠(사용 → 개선)의 일부인 경우 → growth-loop (데이터 구조 설계)
- 멀티 에이전트 간 메모리 공유 필요 → orchestration (에이전트 간 데이터 흐름)
- 3-tier 시스템에서 workers 간 컨텍스트 전달 → orchestration (Hierarchical pattern 통신 프로토콜)
- 메모리 저장소의 비용 구조 최적화 → biz-model (인프라 비용 계산)

### Boundary Checks

- 단일 실행 내에서만 메모리 필요 (세션 간 학습 없음) → Working Memory만 구현, 장기 저장소 불필요
- 컨텍스트 윈도우가 충분히 크면 (1M 이상) → Vector DB 대신 in-context learning으로 단순화 가능
- 메모리 저장소가 프라이빗이 아니면 (공유됨) → 사용자 격리 로직 추가 필수

## 개념

에이전트의 지능은 메모리에서 나온다. 단일 실행의 컨텍스트 윈도우를 넘어서, 실행 간 학습과 기억을 유지하는 메모리 아키텍처가 에이전트의 진화를 가능하게 한다.

## Instructions

You are designing a **memory architecture** for: **$ARGUMENTS**

### Step 1 — Memory Type Classification

| Memory Type | Scope | Storage | Example |
|------------|-------|---------|---------|
| **Working Memory** | Single execution | Context window | Current task instructions, user input |
| **Episodic Memory** | Across executions | File/DB | "Last time user X asked about Y, they preferred Z format" |
| **Semantic Memory** | Permanent knowledge | Embeddings/DB | Domain knowledge, best practices, TK entries |
| **Procedural Memory** | How-to knowledge | Instructions/Skills | Workflow patterns, prompt templates |

### Step 2 — What to Remember

For each agent interaction, decide:
```
Always Store:
- User preferences and corrections
- Successful output patterns
- Error cases and resolutions
- Key decisions and reasoning

Never Store:
- Sensitive personal data (unless explicitly needed)
- Temporary calculation artifacts
- Redundant information already in semantic memory
```

### Step 3 — Storage Architecture

Choose the storage layer:

| Approach | Best For | Complexity | Cost |
|----------|----------|------------|------|
| **File-based** (Markdown) | Simple agents, personal use | Low | Free |
| **Vector DB** (Pinecone, Chroma) | Semantic search over large corpus | Medium | $$ |
| **Structured DB** (PostgreSQL) | Relational data, complex queries | Medium | $ |
| **Hybrid** (File + Vector) | Best retrieval + human-readable | High | $$ |

### Step 4 — Retrieval Strategy

Design how the agent finds relevant memories:

```
Retrieval Pipeline:
1. Extract query from current context
2. Search relevant memory stores:
   - Recency: recent interactions first
   - Relevance: semantic similarity
   - Importance: priority-tagged memories
3. Rank and select top-K memories
4. Inject into context window (within budget)
```

### Step 5 — Memory Budget

Allocate context window for memory:
```
Total Context Window: [tokens]
├── System Prompt: [tokens] (fixed)
├── Memory Injection: [tokens] (variable)
│   ├── User preferences: [tokens]
│   ├── Relevant past interactions: [tokens]
│   └── Domain knowledge: [tokens]
├── Current Input: [tokens] (variable)
└── Output Reserve: [tokens] (fixed)
```

**Rule**: Memory injection should not exceed 30% of available context

### Step 6 — Memory Lifecycle

Define how memories age:
```
New Memory → Active (immediate access)
  → after 30 days unused → Archive (lower priority retrieval)
  → after 90 days unused → Cold Storage (manual retrieval only)
  → contradicted by newer info → Deprecated (flagged, not deleted)
```

### Output

Present the memory architecture:
```
┌─────────────────────────────────────┐
│ Agent: [name]                        │
├──────────┬──────────────────────────┤
│ Working  │ Context window management │
│ Episodic │ [storage choice]          │
│ Semantic │ [storage choice]          │
│ Procedural│ Skills/Instructions      │
├──────────┴──────────────────────────┤
│ Retrieval: [strategy]                │
│ Budget: [X tokens for memory]        │
│ Lifecycle: [aging policy]            │
└─────────────────────────────────────┘
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|-----|-----|
| 메모리 주입으로 인한 컨텍스트 오버플로우 | 컨텍스트 윈도우 초과 또는 응답 지연 | 메모리 예산 축소 (30% → 20%), 덜 중요한 기억 제거, 또는 메모리 요약 추가 |
| 검색 결과가 관련성 없음 | "최신 정보"를 요청했는데 3개월 전 메모리 반환 | 검색 알고리즘 개선: recency weighting 추가, 키워드 필터링, 또는 명시적 쿼리 작성 |
| 메모리 모순: 새 정보가 기존 정보와 충돌 | 에이전트가 "이전과 다른 답변" → 사용자 혼란 | 메모리 버전 관리 시스템 도입, 또는 모순 감지 시 사용자에게 확인 요청 |
| 개인정보 누수: 공유 메모리에 민감한 데이터 저장됨 | 한 사용자의 메모리가 다른 사용자에게 노출 | 즉시 격리 로직 추가 (user_id 기반 필터링), 기존 메모리 감사 및 정제 |

## Quality Gate

- [ ] 메모리 유형 분류: Working, Episodic, Semantic, Procedural 각각 저장소 지정 (Yes/No)
- [ ] 저장소 선택 정당화: 각 저장소 선택 시 비용, 복잡도, 검색 속도 트레이드오프 평가 (Yes/No)
- [ ] 메모리 예산 계산: 컨텍스트 윈도우 대비 메모리 할당 비율 (30% 이하) (N/N %)
- [ ] 검색 전략 명시: Recency/Relevance/Importance 중 우선순위 정의 (Yes/No)
- [ ] 메모리 라이프사이클: 새 → 활성 → 아카이브 → 콜드 스토리지 단계 및 기간 정의 (Yes/No)

## Examples

### Good Example

```
에이전트: "개인 비서 (사용자별 장기 메모리)"

[메모리 레이어]
1. Working Memory (컨텍스트 윈도우)
   - 현재 작업 내용
   - 현재 대화 컨텍스트
   - 저장소: LLM 컨텍스트 윈도우 (고정)

2. Episodic Memory (사용자 상호작용 기록)
   - "지난주 월요일 회의에서 CEO가 Q2 목표 변경 언급"
   - "고객 X가 항상 CSV 형식 선호"
   - 저장소: PostgreSQL (user_id, timestamp 인덱싱)

3. Semantic Memory (도메인 지식)
   - 회사 조직도, 제품 정보, 정책
   - 경쟁사 분석 자료
   - 저장소: Vector DB (Pinecone, 유사도 검색)

4. Procedural Memory (워크플로우)
   - "월말 마감 프로세스: [단계 1, 2, 3]"
   - 자주 쓰는 템플릿, 스크립트
   - 저장소: Markdown 파일 (버전 관리)

[검색 전략]
사용자 질문: "CEO가 뭐라고 했는데?"
1. Episodic에서 user_id = 123, recent 정렬로 "CEO 언급" 찾기
2. 유사도 순위로 top-3 반환
3. 각 메모리에 신뢰도 점수 (데이터 나이, 정확도) 첨부
4. 모순 감지 시 사용자에게 "다음 중 어떤 것? A/B" 확인

[메모리 예산]
- 컨텍스트 윈도우: 200K 토큰
- Working Memory: 50K (현재 대화)
- 메모리 주입: 40K (30% × 200K에서 일부만)
  - Episodic 최신 3개: 20K
  - Semantic 관련 2개: 15K
  - Procedural 1개: 5K

[라이프사이클]
새 에피소드 → 활성 (즉시 검색)
  → 30일 미사용 후 → 아카이브 (낮은 우선순위)
  → 90일 미사용 후 → 콜드 스토리지 (수동 조회 필요)
  → 모순 발생 → deprecated (플래그만, 삭제 안함)
```

### Bad Example

```
반사례 1: 모든 메모리가 한 곳에
- 모든 정보를 Vector DB에만 저장
- "CEO 언급 찾기" → 수천 개 벡터 유사도 계산 → 느림
- 시간순 검색 필요하지만 구현 안 됨

반사례 2: 메모리 예산 무시
- 검색된 메모리를 다 주입: "200K 토큰 중 100K가 메모리"
- 사용자 새로운 입력 공간 부족
- 응답 지연, 토큰 낭비

반사례 3: 사용자 격리 없음
- 공유 Vector DB에 모든 사용자의 Episodic 저장
- 검색 필터링 안 함
- 사용자 A의 개인 정보가 사용자 B에게 노출 (심각한 버그)

반사례 4: 메모리 모순 미해결
- 사용자가 "이전과 다른 답변 주네?"
- 메모리 시스템이 이전 데이터를 먼저 반환했음
- "신뢰할 수 없는 에이전트" → 이탈
```

---

## Further Reading
- LangChain Memory Documentation — Memory pattern implementations
- Letta (formerly MemGPT) — Long-term memory architecture for agents

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
