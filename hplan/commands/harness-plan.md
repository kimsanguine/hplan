---
description: "Full technical architecture and strategy planning — orchestration pattern, 3-tier design, memory architecture, model routing, architecture doc, and strategy review. Use when a product has passed the evidence gate and needs a complete technical and strategic blueprint before build."
argument-hint: "[system] [--mode orchestration|3-tier|memory|routing|review]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /harness-plan

> 에이전트 시스템 기술 아키텍처 전체 설계 + 전략 리뷰

## Routing

`$ARGUMENTS`에서 `--mode` 플래그를 파싱한다.

| 플래그 | 실행 범위 |
|--------|-----------|
| `--mode orchestration` | Phase 1만 실행 |
| `--mode 3-tier` | Phase 2만 실행 |
| `--mode memory` | Phase 3만 실행 |
| `--mode routing` | Phase 4만 실행 |
| `--mode review` | Phase 5(Strategy Review)만 실행 |
| 플래그 없음 | Phase 1 → 2 → Checkpoint → 3 → 4 → Architecture Doc 전체 실행 (Phase 5는 별도 호출) |

---

## Instructions

You are designing **Technical Architecture and Strategy Plan** for: **$ARGUMENTS**

플래그가 있으면 해당 Phase만 실행한다. 플래그가 없으면 아래 전체 플로우를 순서대로 실행한다.

---

### Planning Disciplines (v0.9.6)

Phase 진입 전 아래 3개 규율을 명시적으로 적용한다.

**G2 — Named Artifacts**: Phase 시작 직후, 이 Phase의 산출물 파일명·섹션명을 먼저 선언한다.  
→ 파일명 없이 "설계를 진행하겠습니다"라고 시작하면 규율 위반.

**G3 — Decision Commit**: 모든 HITL 결정 지점에서 옵션 3개 이상 제시 → 정확히 1개에 커밋.  
→ "A 또는 B 방향으로 갈 수 있습니다" 같은 미결 처리 금지. `decision_log.py hitl` 기록 필수.

**G4 — Phase Context Budget**: 각 Phase는 해당 Phase에 필요한 파일만 로드한다 (최대 3개).  
→ Phase 시작 전 전체 프로젝트 파일 일괄 Read 금지. 필요한 것만 Just-in-Time 로드.

| Phase | Named Artifact | Context Budget (최대) |
|-------|---------------|----------------------|
| 1 Orchestration | `decisions/orchestration-choice.md` 또는 decision_log 항목 | 없음 (신규 설계) |
| 2 3-Tier | `harness/ARCHITECTURE.md` — Tier 섹션 | Phase 1 결정 1개 |
| 3 Memory | `harness/ARCHITECTURE.md` — Memory 섹션 | Tier 설계 1개 |
| 4 Routing | `harness/ARCHITECTURE.md` — Routing 섹션 | Memory 설계 1개 |
| Architecture Doc | `harness/ARCHITECTURE.md` 완성본 | Phase 1–4 결정 요약 |

---

### Phase 1 — Orchestration Pattern Selection
*`--mode orchestration` 또는 전체 플로우*

> **왜**: 에이전트 여러 개를 어떻게 연결할지는 나중에 바꾸기 어렵습니다.
> 시작 전에 Sequential·Parallel·Router·Hierarchical 중 어떤 패턴이 맞는지 결정합니다.

4가지 오케스트레이션 패턴을 사용 사례에 대입해 평가한다.
> **Orchestration (오케스트레이션)**: 여러 에이전트가 어떤 순서와 방식으로
> 협력할지 설계하는 것입니다. 사람 조직의 업무 프로세스 설계와 같은 개념입니다.

| Pattern | Best When | Drawback |
|---------|-----------|----------|
| **Sequential** | 각 스텝이 이전 결과에 의존하고 순서가 고정된 경우 | 느림; 단일 장애 지점 |
| **Parallel** | 독립적인 서브태스크를 동시에 실행할 수 있는 경우 | 결과 집계가 복잡해짐 |
| **Router** | 입력 유형에 따라 서로 다른 처리 경로가 필요한 경우 | 라우터 자체가 병목이 됨 |
| **Hierarchical** | 복잡한 태스크에 계획 레이어와 실행 레이어 분리가 필요한 경우 | 복잡도·비용 최고 |

위 4가지 패턴을 이 시스템에 대입해 간략히 평가하고 사용자에게 제시한다. 불확실하면 Sequential을 기본 추천으로 제안한다. 사용자 선택을 기다린다.

**사용자 선택 후 결정을 기록한다:**

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "architect" \
  --q "오케스트레이션 패턴 선택" \
  --options "Sequential|Parallel|Router|Hierarchical" \
  --chosen "[선택된 패턴]" \
  --why "[이유]"
```

출력:
- 선택된 패턴
- 3문장 근거 (왜 이 시스템에 최적인가 / 다른 패턴을 배제한 이유 / 예상 trade-off)

---

### Phase 2 — 3-Tier Agent Design
*`--mode 3-tier` 또는 전체 플로우*

> **왜**: 하나의 에이전트가 모든 것을 하면 복잡도가 급격히 증가합니다.
> 전략·조율·실행을 분리하면 각 역할이 명확해지고 교체·확장이 쉬워집니다.

**Prometheus → Atlas → Worker** 스택을 설계한다.
> **3-Tier (Prometheus/Atlas/Worker)**: 전략 결정자(Prometheus) →
> 조율자(Atlas) → 실행자(Worker) 3역할 분리 구조입니다.
> 사람 조직의 임원-중간관리자-실무자 구조와 동일한 원리입니다.

**Tier 1: Prometheus (Strategic)**
- 역할: 목표 분해, 태스크 우선순위 결정, 컨텍스트 예산 관리
- 트리거: 사용자 요청 또는 cron 이벤트
- 출력: Atlas에 전달할 태스크 목록

**Tier 2: Atlas (Tactical)**
- 역할: Worker 선택·라우팅, 에러 처리, 상태 추적
- Worker 실패 시 fallback: 재시도 → 대체 Worker → Prometheus에 에스컬레이션
- 출력: 결과 집계 후 Prometheus에 반환

**Tier 3: Worker (Execution)**
- 1 Worker = 1개의 명확한 태스크 타입
- 각 Worker 정의 필수 항목: 이름 / 툴 목록 / 출력 스키마 / max retries
- 예시 네이밍: `research-worker`, `formatter-worker`, `validator-worker`

단일 에이전트인 경우: tier 없이 에이전트의 역할·툴·범위 경계를 직접 정의한다.

---

### 🔍 Checkpoint — Architecture Review
*전체 플로우에서만 실행*

다음 3가지를 제시한다:

1. **패턴 + Tier 텍스트 다이어그램** — 컴포넌트와 데이터 흐름을 ASCII로 표현
2. **위험 질문**: "단일 컴포넌트가 전체 시스템을 망가뜨리는 병목인가?"
3. **계속 진행 옵션** — 3가지 중 하나를 선택:
   - A) "메모리 + 라우팅 설계로 계속"
   - B) "오케스트레이션 패턴 재검토"
   - C) "단일 에이전트로 단순화 후 tier 추가 재검토"

**사용자 선택 후 결정을 기록하고 진행한다:**

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "architect" \
  --q "Architecture 방향 선택" \
  --options "A: 메모리+라우팅으로 계속|B: 오케스트레이션 재검토|C: 단일 에이전트 단순화" \
  --chosen "[사용자가 선택한 옵션 (A/B/C)]" \
  --why "[이유]"
```

**사용자 확인을 대기한다.** 확인 없이 Phase 3으로 진행하지 않는다.

---

### Phase 3 — Memory Architecture
*`--mode memory` 또는 전체 플로우*

> **왜**: 에이전트가 이전 대화, 과거 결정, 운영 규칙을 어떻게 기억하느냐에 따라
> 응답의 일관성이 달라집니다. 메모리 설계가 없으면 매 호출마다 처음부터 시작합니다.

4개 메모리 레이어를 설계한다.

| Layer | Storage | Contents | Lifetime | Eviction Policy |
|-------|---------|----------|----------|-----------------|
| **Working** | In-context | 현재 태스크 상태, 중간 결과 | 단일 세션 | 세션 종료 시 소멸 |
| **Episodic** | 파일 / DB | 과거 인터랙션, 이전 의사결정 기록 | 프로젝트 수명 | LRU 또는 중요도 기반 |
| **Semantic** | Vector DB / 문서 | 도메인 지식, 제품 규칙, 참조 데이터 | 영속 | 버전 관리 기반 교체 |
| **Procedural** | 코드 / 프롬프트 | How-to 패턴, 툴 사용 규칙, 워크플로우 | 버전 관리 | PR 리뷰 기반 |

각 레이어별로 다음을 정의한다:
- **What** — 무엇이 들어가는지 (추상 타입이 아닌 구체적 예시)
- **When** — 언제 쓰여지는지 (이벤트 트리거)
- **How** — 어떻게 검색하는지 (정확한 쿼리 또는 조회 패턴)
- **Max size** — 레이어별 최대 크기 및 eviction 정책

**Context window 예산**: 레이어별 요청당 토큰 소비량을 추정한다.

---

### Phase 4 — Model Routing Matrix
*`--mode routing` 또는 전체 플로우*

> **왜**: 모든 요청을 가장 강력한 모델로 처리하면 비용이 급증합니다.
> 태스크 복잡도에 따라 적합한 모델을 자동으로 선택하는 규칙을 설계합니다.

태스크 타입 → 모델 매핑을 정의한다.

| Task Type | Model | Reason | Fallback |
|-----------|-------|--------|---------|
| Complex reasoning / planning | claude-opus-4-7 | 최고 품질 필요 | claude-sonnet-4-6 |
| Standard generation / analysis | claude-sonnet-4-6 | 품질·비용 균형 | claude-haiku-4-5 |
| Simple classification / triage | claude-haiku-4-5 | 비용 최소화 | rule-based 로직 |

라우팅 규칙 3가지를 정의한다:
- **Cost gate**: `tokens_in > X`이면 더 저렴한 모델로 라우팅
- **Quality gate**: 태스크 카테고리가 `["legal", "financial", "medical"]`이면 항상 Opus 사용
- **Fallback chain**: API 에러 또는 타임아웃 발생 시 동작 정의 (재시도 → 하위 모델 → 에러 반환)

---

### Phase 5 — Strategy Review
*`--mode review`일 때만 실행*

**대상 시스템**: `$ARGUMENTS`에서 `--mode review` 플래그를 제외한 나머지 인자

#### 5-1. Business Model Analysis

수익 모델 옵션을 평가한다:
- **Per-use**: API 호출당 과금 — 낮은 진입 장벽, 수익 변동성 높음
- **Subscription**: 월정액 — 예측 가능 수익, 사용량 급증 시 마진 리스크
- **Outcome-based**: 결과 기반 과금 — 높은 신뢰·가치 정렬, 측정 복잡도 높음

정의할 항목:
- 가격 전략 추천 + 근거
- 비용 구조 (LLM API / 인프라 / 인건비)
- Unit economics: 고객당 LTV vs CAC, 손익분기 사용량

#### 5-2. Competitive Moat

현재 moat 소스를 4가지 축으로 평가한다:
> **Moat (해자)**: 경쟁사가 쉽게 따라올 수 없는 구조적 방어선입니다.
> 데이터 축적, 전환 비용, 네트워크 효과 등이 대표적인 예입니다.

| Moat Source | 현재 강도 (1-5) | 지속가능성 | 구축 전략 |
|-------------|----------------|-----------|----------|
| 데이터 (독점 데이터, 학습 데이터) | | | |
| 네트워크 효과 (사용자 증가 → 가치 증가) | | | |
| 전환 비용 (이탈 시 고객이 잃는 것) | | | |
| 브랜드 (신뢰·인지도) | | | |

moat 강도·지속가능성 평가 + 6개월 moat 구축 전략을 작성한다.

#### 5-3. Model Dependency Risk

벤더 lock-in 위험을 평가한다:
- **현재 의존도**: 특정 모델/벤더에 얼마나 종속되어 있는가?
- **마이그레이션 전략**: 다른 모델로 전환 시 필요한 작업 범위
- **비용 궤적**: 모델 API 비용이 스케일에 따라 어떻게 변하는가?
- **완화 방안**: abstraction layer, multi-vendor 전략, 오픈소스 fallback

#### 출력: Strategy Brief

다음 4개 섹션으로 구성된 Strategy Brief를 작성한다:
1. **비즈니스 모델 추천** — 최적 수익 구조 + unit economics 요약
2. **Moat 평가** — 현재 moat 강도 + 6개월 구축 계획
3. **모델 전략** — 의존성 리스크 수준 + 완화 방안
4. **전략 권고** — 3-6개월 구체 액션 아이템 (우선순위 순)

---

### Architecture Doc 생성
*전체 플로우 마지막 단계 (플래그 없음일 때만)*

Checkpoint 이후 사용자 확인을 받은 뒤, `harness/ARCHITECTURE.md`를 작성한다.

파일에 포함할 내용:
- 선택된 오케스트레이션 패턴 + 근거
- Tier 역할 정의 (또는 단일 에이전트 스펙)
- 메모리 설계 테이블 (4 레이어 × 5 컬럼)
- 모델 라우팅 매트릭스 (태스크 → 모델 → fallback)
- W1 Done Criteria 체크리스트:
  - [ ] 핵심 happy path가 end-to-end 실행된다 (툴 호출 → 출력)
  - [ ] 에러 처리: 최소 1개 실패 케이스가 명시적으로 처리된다
  - [ ] 관찰가능성: 에이전트 실행을 증명하는 최소 1개 메트릭 또는 로그가 있다

**PRD v0.2 업데이트** — `harness/ARCHITECTURE.md` 작성 완료 후 `docs/PRD.md`를 업데이트한다:

1. `docs/PRD.md` Section 7–11 (에이전트·실행 사양)을 architect 결정 내용으로 채운다.
2. 파일 첫 줄 버전 헤더를 업데이트한다:
   ```
   <!-- hplan PRD | v0.2 | {YYYY-MM-DD} | architect 결정 반영 -->
   ```
3. 결정을 기록한다:

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "architect" \
  --q "PRD v0.2 — architect 결정 반영" \
  --options "Architecture Doc 반영" \
  --chosen "Architecture Doc 반영" \
  --why "오케스트레이션·Tier·메모리·라우팅 결정이 PRD Section 7-11에 동기화됨" \
  --prd-version "v0.2"
```

---

### Scope Decomposition Check

`harness/ARCHITECTURE.md` 작성 완료 후, Execution Handoff 진입 전에 아래 체크리스트를 실행한다.

각 태스크에 대해 3가지 질문에 답한다:

| 질문 | PASS 기준 | FAIL 처리 |
|---|---|---|
| 2주(10 영업일) 내 완료 가능한가? | 단일 개발자 기준 | Wave A/B/C로 분할 |
| 다른 태스크 완료 없이 독립 검증 가능한가? | 산출물이 단독 테스트 가능 | 의존 그래프 재설계 |
| 산출물이 구체적 파일명 또는 API 엔드포인트로 표현되는가? | 이름 있는 산출물 | Named Artifacts(G2) 재적용 |

**2주 초과 태스크 분할 패턴**:
- Wave A: 핵심 happy path (1–2주) — 단독 데모 가능해야 함
- Wave B: 에러 처리 + 엣지 케이스 (1주)
- Wave C: 최적화 + 관찰가능성 (1주)

분할 완료 후 `harness/ARCHITECTURE.md`를 업데이트하고 Execution Handoff로 진행한다.

---

## Output Format

**`--mode orchestration`**: 선택 패턴 + 3문장 근거

**`--mode 3-tier`**: Tier별 역할 정의 + Worker 목록 (이름/툴/스키마/max retries)

**`--mode memory`**: 4 레이어 테이블 + 레이어별 What/When/How/Max size + 토큰 예산

**`--mode routing`**: 태스크→모델 매핑 테이블 + 3가지 라우팅 규칙

**`--mode review`**: Strategy Brief (비즈니스 모델 + Moat 평가 + 모델 전략 + 전략 권고)

**플래그 없음 (전체 플로우)**: Architecture Blueprint

1. **시스템 개요** — 텍스트 다이어그램 (컴포넌트 + 데이터 흐름)
2. **오케스트레이션 결정** — 선택 패턴 + 3문장 근거
3. **Tier 역할** — Prometheus/Atlas/Worker 또는 단일 에이전트 스펙
4. **메모리 설계 테이블** — 4 레이어 × 5 컬럼
5. **모델 라우팅 매트릭스** — 태스크 → 모델 → fallback
6. **W1 Done Criteria** — 체크리스트 3개
7. **`harness/ARCHITECTURE.md`** — 디스크에 작성 완료

---

### Execution Handoff — 실행 전략 선택 (HITL)

> **Execution Handoff**: 설계 완료 후 실제 빌드를 누가 어떻게 진행할지
> 결정하는 전환점입니다. 이 선택에 따라 다음 커맨드 실행 방식이 달라집니다.

*전체 플로우 마지막 단계 (플래그 없음일 때만)*

ARCHITECTURE.md 작성 완료. 다음 실행 전략 중 하나를 선택한다:

- A) **단독 실행** — `/harness-build [brief]`로 이 세션에서 직접 진행
- B) **병렬 팀 구성** — `/deliver:parallel-team`으로 에이전트 팀을 배치한 후 병렬 실행
- C) **단계적 실행** — Phase별 HITL 확인하며 `/harness-build --step` 순서대로 진행

**선택 후 결정을 기록한다:**

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "architect" \
  --q "빌드 실행 전략 선택" \
  --options "A: 단독 실행|B: 병렬 팀 구성|C: 단계적 실행" \
  --chosen "[선택된 옵션 (A/B/C)]" \
  --why "[이유]"
```

다음 단계: **`/harness-build [brief]`**
