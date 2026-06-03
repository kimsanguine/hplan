---
description: "End-to-end discovery workflow — opportunity mapping, assumption analysis, cost simulation, build/buy decision, and assumption validation. Use when exploring a new product or agent idea, stress-testing an agent concept, or running a full discovery pass before any gate decision."
argument-hint: "[idea] [--mode socratic|opp|assumptions|cost|build-or-buy|validate]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /harness-discover

> 기회 발굴 전체 워크플로우 — 아이디어 → 검증된 기회 + 비용 추정 + 빌드/바이 결정 + 가정 검증

## Phase 0 — 가정 심문 (선택적 진입점)

> 아이디어가 있지만 "만들 가치가 있나"라는 가정이 불분명할 때 **먼저** 이 단계를 거치세요.
> Phase 1(Opportunity Mapping)은 가정이 어느 정도 정리된 상태에서 시작할 때 더 유효합니다.

**진입 조건:** 다음 중 하나라도 해당되면 Phase 0부터 시작합니다.
- 아이디어는 있지만 "왜 이게 필요한가"에 대한 가정이 불분명함
- 이전에 비슷한 아이디어를 시도했다가 실패한 경험이 있음
- "사람들이 쓸 것 같다"는 직관 외에 근거가 약함

**Phase 0 실행:** `/socratic-question [아이디어]`

`socratic-question`은 6가지 질문 유형(명료화·가정·증거·관점·함의·메타질문)으로
당신의 가정을 심문하고, "사고 검증 질문 세트" 1장을 만듭니다.

**Phase 0 완료 기준:** *"누구의 / 무슨 문제를 / 무엇으로 / 무엇은 빼고 푼다"* 가 한 문장으로 나오면
→ Phase 1으로 넘어가세요 (`/harness-discover [아이디어]`)

**Phase 0 생략:** 가정이 이미 명확하거나 빠른 탐색이 목적이라면 바로 Phase 1부터 시작해도 됩니다.

---

## Routing

Parse `$ARGUMENTS` for a `--mode` flag before proceeding:

| Flag | Execution |
|------|-----------|
| `--mode socratic` | Phase 0 — socratic-question 실행 후 종료 |
| `--mode opp` | Phase 1만 실행 후 종료 |
| `--mode assumptions` | Phase 2만 실행 후 종료 |
| `--mode cost` | Phase 3만 실행 후 종료 |
| `--mode build-or-buy` | Phase 4만 실행 후 종료 |
| `--mode validate` | Phase 5만 실행 후 종료 |
| 플래그 없음 | Phase 1 → 2 → Checkpoint → 3 → 4 전체 실행 (Phase 5 제외) |

The remaining text after the flag is the target idea. If no flag is present, the entire `$ARGUMENTS` string is the idea.

---

## Instructions

You are running the **Discovery Workflow** for: **$ARGUMENTS**

Follow the Routing table above to determine which phases to execute. Each phase is self-contained and independently readable.

**`--mode socratic` 선택 시**: `/socratic-question [아이디어]`를 먼저 실행하세요. 사고 검증 질문 세트가 완성되면 `/harness-discover [아이디어]`로 돌아오세요. (socratic-question을 직접 실행하지 않고 안내만 합니다.)

---

### Interview Discipline (Phase 전반에 적용)

> **왜**: 인터뷰는 가설을 확인하는 자리가 아니라 모르는 것을 발견하는 자리입니다.
> 질문이 많을수록, AI가 생성한 페르소나를 쓸수록 발견의 질이 낮아집니다.

모든 Phase에서 고객·사용자와 대화할 때 아래 4가지 규칙을 따른다:

**규칙 1 — 질문 1개씩**
복합 질문 금지.
- ✅ "언제 마지막으로 이 문제를 겪었나요?"
- ❌ "이 문제가 언제, 어디서, 왜 발생하나요?"

**규칙 2 — Multiple choice 우선**
열린 질문보다 선택지를 먼저 제시한다.
- ✅ "A: 직접 해결 / B: 담당자에게 위임 / C: 그냥 넘어감 — 가장 가까운 것은?"
- ❌ "이 상황에서 어떻게 하시나요?"

**규칙 3 — AI 생성 페르소나 ≠ 인터뷰 증거**
이 커맨드에서 생성된 기회 분석, 가정 감사, 비용 시뮬레이션 결과는 **연구 가설**입니다.
실제 Signal Gate 증거(`harness/pain.md` 등)로 사용하려면 실제 인터뷰·관찰·데이터가 필요합니다.
> **Signal Gate**: 4개 증거 문서(pain.md · cogs.md · market.md · competitors.md)가
> 실제 출처를 갖춰야 통과하는 체크포인트입니다. 다음 단계(하네스 플랜) 진입 조건입니다.

**규칙 4 — 인터뷰 기록 포맷**
`harness/pain.md`에 인터뷰 내용을 기록할 때 아래 형식을 사용한다:
```
- Source: [역할/직군, 회사 규모 또는 맥락]
- Date: YYYY-MM-DD
- Quote: "[실제 발언 또는 직접 관찰 내용]"
```

Phase 5(Assumption Validation) 실행 전 `harness/pain.md`에 위 형식의 기록이 **최소 3건** 있어야 한다.

---

### Phase 1 — Opportunity Mapping

> **왜**: 해결하고 싶은 문제를 바로 정하지 않고, 먼저 어디에 문제가 가장 많이 쌓여 있는지
> 지도를 그립니다. 첫 번째로 보이는 문제가 가장 중요한 문제가 아닐 수 있기 때문입니다.

> Entry point for `--mode opp`. Maps the agent opportunity landscape for the given idea.

Build an **Agent Opportunity Solution Tree** (opp-tree pattern):

**Layer 1 — Desired Outcome**
- 사용자가 달성하려는 비즈니스 결과는 무엇인가? (예: "이탈률 20% 감소")
- 측정 가능하고 기한이 있는 형태로 명시한다.

**Layer 2 — Jobs to Be Done**
- 이 결과를 달성하기 위해 사람이 반복 수행하는 작업 3–5개를 도출한다.
- 프레임: "When [상황], I want to [행동], so I can [결과]."

**Layer 3 — Pain Points**
- 각 Job에 대해: 무엇이 느리고, 비용이 높으며, 오류가 잦고, 확장을 막는가?
- 각 Pain에 태그 부여: `Time-sink` / `Cost-heavy` / `Error-prone` / `Scale-blocker`

**Layer 4 — Agent Opportunity**
- 각 Pain에 대해: 어떤 에이전트 능력이 이를 해결하는가?
- **Automation Fit** 점수(1–5) 산정: 반복적인가? 구조화되어 있는가? 대량 처리 가능한가?
- `Automation Fit × Pain Severity` 점수 계산 후 **Top 3** 기회 선별

**Output**: 순위별 기회 트리 (Top 3)

*`--mode opp` 선택 시 여기서 종료.*

---

### Phase 2 — Assumption Analysis

> **왜**: 우리가 당연하다고 생각하지만 실제로는 틀릴 수 있는 전제들을 꺼내놓습니다.
> 검증되지 않은 가정 위에 쌓인 기획은 나중에 전부 다시 써야 하는 위험이 있습니다.

> Entry point for `--mode assumptions`. Phase 1의 Top 1 기회에 대한 4축 가정 감사.

**Top 1 기회**를 대상으로 4축 가정 분석을 수행한다.

**Interview Discipline (질문 규율)**
- 각 가정의 검증 질문을 한 번에 하나씩 도출한다 — 여러 가정이 있어도 가장 위험 높은 것부터 하나씩.
- 가능하면 yes/no 또는 객관식 형태로 설계한다 (답변이 쉬울수록 더 많은 증거가 모인다).
- 이전 답변을 바탕으로 다음 질문을 조정한다 — 대화형 탐색이 목표다.

**Axis 1 — Value Assumptions**
- 사용자가 현재 우회책에서 실제로 전환할 것인가?
- 에이전트가 제거하는 비용이 측정 가능한가?

**Axis 2 — Feasibility Assumptions**
- 필요한 데이터 소스가 API/파일로 접근 가능한가?
- 작업이 LLM이 안정적으로 수행할 만큼 충분히 구조화되어 있는가?

**Axis 3 — Reliability Assumptions**
- 허용 가능한 오류율은 얼마인가? 실패 시 어떻게 되는가?
- 모든 출력을 사람이 검토해야 하는가 (HITL)?

**Axis 4 — Ethics / Risk Assumptions**
- PII, 규제 데이터, 또는 책임 노출이 있는가?
- 에이전트 스펙에 명시해야 할 금지 목표(anti-goals)가 있는가?

각 축당 **구체적인 검증 질문 2개**를 도출한다.

**우선순위 분류**:
- `CRITICAL` — 빌드 전 반드시 검증 필요
- `HIGH` — 초기 빌드 후 검증 가능
- `LOW` — 스케일 단계에서 검증

**각 CRITICAL 가정에 대해 2-day 실험을 설계한다:**
- 실험 방법 (인터뷰 / 프로토타입 / 데이터 조회 / A/B)
- 성공/실패 판단 기준
- 필요한 최소 자원

*`--mode assumptions` 선택 시 여기서 종료.*

---

### Checkpoint — 계속할까요?

> 전체 플로우(`--mode` 없음)에서만 실행. Phase 2 완료 후, Phase 3 진입 전 사용자 확인.

다음 세 항목을 제시하고 사용자 응답을 기다린다:

1. **Top 기회 요약** — 1문장: who + pain + agent role
2. **CRITICAL 가정 목록** — 최대 3개
3. **선택지** — 3가지 중 하나를 선택:
   - A) "비용 시뮬레이션으로 계속 진행"
   - B) "기회 #2 또는 #3 탐색"
   - C) "CRITICAL 가정 먼저 더 깊이 검증"

**사용자 선택 후 결정을 기록하고 진행한다:**

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "discover" \
  --q "Discovery 방향 선택" \
  --options "A: 비용 시뮬레이션으로 계속|B: 기회 #2/#3 탐색|C: CRITICAL 가정 먼저 검증" \
  --chosen "[사용자가 선택한 옵션 (A/B/C)]" \
  --why "[이유]"
```

**사용자 확인 전 Phase 3 진입 금지.**

---

### Phase 3 — Cost Simulation

> **왜**: 아이디어가 매력적이어도 비용 구조가 맞지 않으면 사업이 되지 않습니다.
> 코드 한 줄 쓰기 전에 단위 경제를 대략적으로 검증합니다.

> Entry point for `--mode cost`. Top 1 기회의 단위 경제성 추정.

**Token Model**

| Metric | Estimate |
|--------|----------|
| Tokens in per call | — |
| Tokens out per call | — |
| Calls per user per month | — |
| Model (예: Sonnet 4.6 / Haiku 4.5) | — |

**비용 계산**

월간 토큰 비용/유저 = tokens × (price per 1M) × calls/month

| MAU | p50 (Median) | p90 (Heavy User) |
|-----|-------------|-----------------|
| 100 | — | — |
| 1,000 | — | — |
| 10,000 | — | — |

- p50 / p90는 lognormal 분포 기준으로 별도 산출한다.
- Free tier 남용 안전 마진: ×2 적용.

**vs 현재 프로세스**

| 항목 | 수동 방식 | 에이전트 방식 |
|------|---------|------------|
| 작업당 인건비 (시간 × 시급) | — | — |
| 유저당 월 절감액 | — | — |
| 빌드 비용 대비 Payback 기간 | — | — |

*`--mode cost` 선택 시 여기서 종료.*

---

### Phase 4 — Build vs Buy Decision

> **왜**: 모든 것을 직접 만드는 것이 항상 좋은 선택은 아닙니다.
> 차별화되는 부분에만 집중하고, 나머지는 기존 솔루션을 쓰는 판단이 중요합니다.

> Entry point for `--mode build-or-buy`. 3가지 옵션 × 5축 점수 평가.

| Axis | Custom Build | Buy SaaS | No-Code |
|------|-------------|----------|---------|
| Time to first value | | | |
| Customization fit | | | |
| Long-term COGS | | | |
| Data ownership | | | |
| Team capability | | | |

각 셀에 1–5 점수를 기입한다. 합산 최고점 = 1차 추천 옵션.

**최종 출력**:
- **추천 옵션** + 상위 3가지 근거
- **추천 경로의 최대 위험** 1가지

위 결과를 제시하고 사용자 선택을 기다린다. 선택 후 기록한다:

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "discover" \
  --q "Build vs Buy 결정" \
  --options "Custom Build|Buy SaaS|No-Code" \
  --chosen "[선택된 옵션]" \
  --why "[이유]"
```

- **다음 단계**: `Run /hplan [idea]` to start the evidence gate

*`--mode build-or-buy` 선택 시 여기서 종료.*

---

### Phase 5 — Assumption Validation

> **왜**: 분석한 가정들을 실제 고객과 대화해서 검증합니다.
> 이 단계의 결과가 Signal Gate(harness/pain.md 등) 증거로 사용됩니다.

> Entry point for `--mode validate`. validate.md 통합 내용. 전체 플로우에서는 기본 제외 — `--mode validate`로 명시 호출 시에만 실행.

**Step 1 — 전체 가정 추출**

`$ARGUMENTS`의 아이디어에서 관련된 모든 가정을 추출한다. 각 가정에 대해:
- **4축 분류**: Value / Feasibility / Reliability / Ethics
- **Confidence** (1–5): 현재 확신 정도 (5 = 확실, 1 = 추측)
- **Impact** (1–5): 가정이 틀렸을 때 프로젝트에 미치는 영향

**가정 위험 맵**

| 가정 | 축 | Confidence | Impact | Risk Score (= Impact × (6–Confidence)) |
|------|---|-----------|--------|----------------------------------------|
| — | — | — | — | — |

Risk Score 내림차순 정렬.

**Step 2 — Top 3 위험 가정에 대한 HITL Boundary 설계**

각 가정별로:

| 항목 | 내용 |
|------|------|
| 가정 | — |
| 자동화 레벨 | Full Auto / Human Review / Human Approve / Manual |
| 에스컬레이션 트리거 | — (예: confidence < 0.7, 금액 > N원, 특정 엔티티 감지) |
| 에스컬레이션 채널 | — (예: Slack DM, 이메일, 대시보드 큐) |
| 복구 절차 | — |

**자동화 레벨 기준**:
- **Full Auto**: 오류 발생 시 영향이 낮고 쉽게 되돌릴 수 있음
- **Human Review**: 출력이 외부에 전달되기 전 인간 확인 필요
- **Human Approve**: 실행 전 명시적 승인 필요 (돈, 법적 영향 등)
- **Manual**: 자동화 부적합 — 인간이 전체 수행

**Step 3 — Go/No-Go 기준 정의**

| 기준 | Threshold | 현재 상태 |
|------|-----------|---------|
| CRITICAL 가정 검증 완료율 | 100% | — |
| Top 3 가정 Confidence 평균 | ≥ 4.0 | — |
| Reliability Assumption 오류율 | ≤ [정의된 허용치] | — |
| Ethics/Risk 가정 클리어런스 | 법무/컴플라이언스 승인 | — |

**Go**: 모든 기준 충족 → Phase 3~4 진행 또는 `/hplan [idea]` 실행
**No-Go**: 미충족 기준 있음 → 해당 가정 재검증 후 재평가

*`--mode validate` 선택 시 여기서 종료.*

---

## Output Format

실행된 Phase에 따라 다음 형식으로 출력한다:

- **`--mode socratic`**: `/socratic-question [아이디어]` 실행 안내 후 종료
- **`--mode opp`**: 기회 트리 (Top 3 순위, Layer 1–4 전체)
- **`--mode assumptions`**: 가정 위험 맵 (CRITICAL / HIGH / LOW) + CRITICAL 항목별 2-day 실험 설계
- **`--mode cost`**: p50/p90 비용 테이블 (100/1K/10K MAU) + vs 수동 비용 비교
- **`--mode build-or-buy`**: 3옵션 × 5축 점수표 + 추천 옵션 + 최대 위험
- **`--mode validate`**: 가정 위험 맵 (Risk Score 정렬) + HITL 설계 + Go/No-Go 기준
- **전체 플로우 (플래그 없음)**: **Discovery Report** — 다음 6개 섹션:
  1. **Opportunity Landscape** — 순위별 기회 트리 (3개)
  2. **Top Opportunity Brief** — 1문단 요약 (ICP, pain, agent role)
> **ICP (Ideal Customer Profile)**: 우리 제품의 문제를 가장 심하게 겪고,
> 해결에 기꺼이 비용을 지불할 의사가 있는 1순위 고객 유형입니다.
  3. **Assumption Risk Map** — CRITICAL / HIGH / LOW 테이블
  4. **Cost Projection** — p50/p90 × 100/1K/10K MAU
  5. **Build/Buy/No-Code Recommendation** — 점수표 + 근거
  6. **Next Steps** — `Run /hplan [idea]` to start the evidence gate
