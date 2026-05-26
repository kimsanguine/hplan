---
name: moat
description: "Analyze and design competitive moats for AI agent products — data flywheel, workflow lock-in, network effects, and switching costs. Use when evaluating competitive positioning, planning long-term defensibility, or identifying what makes your agent product hard to replicate."
argument-hint: "[agent product to analyze]"
allowed-tools: ["Read", "Write", "WebSearch", "WebFetch"]
model: sonnet
---

# Agent Moat

> AI 에이전트 제품의 경쟁 우위(Moat) 분석 및 설계

## Core Goal

- 모델 성능이 commodity화되는 시장에서 데이터, 워크플로우, 네트워크 차원의 경쟁 우위를 설계하여 지속 가능한 방어선 구축
- 6가지 moat 유형을 평가하여 제품에 가장 강한 1-2개 우위를 명확히 하고 장기 투자 전략 수립
- 경쟁사가 모방 불가능하거나 시간이 많이 걸리는 구조를 설계하여 시장 진입 장벽 높임

## Trigger Gate

### Use This Skill When

- 에이전트 제품의 장기 경쟁력을 평가하거나 설계하는 경우
- 초기 시장 우위(빠른 성장)와 장기 방어(모방 방지)의 균형을 맞춰야 하는 상황
- 투자자나 이해관계자에게 "왜 우리 제품이 어렵나?"를 설명해야 하는 경우

### Route to Other Skills When

- Data Flywheel moat를 구현하려면 → growth-loop (플라이휠 설계)
- Workflow Lock-in을 위한 기술 설계 → orchestration (Hierarchical pattern 포함, 아키텍처)
- Moat 구축을 위한 비용 계산 → biz-model (단위 경제), burn-rate (투자 기간)
- 현재 시장 포지셔닝 평가 → discover의 competitor (경쟁사 분석)

### Boundary Checks

- 아직 제품-시장 적합도(PMF)가 없으면 → 먼저 growth-loop로 기본 가치 검증
- "우리의 moat는 기술 우수성"이라고만 하면 → 안 됨, 기술은 모두 구현 가능
- 초기 고객 소수일 때 network effect moat 추구 → 너무 성급함, 먼저 workflow lock-in부터

## 개념

AI 에이전트 시장에서 모델 성능은 commodity화되고 있다. 지속 가능한 경쟁 우위는 모델 바깥에서 만들어진다 — 데이터, 워크플로우, 네트워크에서.

## Instructions

You are analyzing and designing **competitive moats** for: **$ARGUMENTS**

### Step 1 — Moat Type Assessment & Maturity Positioning

Evaluate each moat type (1-5 score):

| Moat Type | Description | Your Score | Evidence |
|-----------|-------------|------------|----------|
| **Data Flywheel** | Usage → better data → better product → more usage | /5 | |
| **Workflow Lock-in** | Deep integration into user's daily process | /5 | |
| **Network Effects** | More users = more value for each user | /5 | |
| **Switching Cost** | Pain of moving to competitor | /5 | |
| **Proprietary Knowledge** | Unique domain expertise encoded | /5 | |
| **Speed/UX Moat** | 10x better experience than alternatives | /5 | |

Then determine current **Maturity Stage** (see `context/domain.md` Section 8-e):
```
Stage 1 (Pre-PMF): Moat 없음, 기능만으로 경쟁 → Copy-Time 3~6개월
Stage 2 (Growth): 단일/이중 moat 형성 중 → Copy-Time 12~18개월
Stage 3 (Expansion): 3+ moat 시너지 작동 → Copy-Time 24~36개월
Stage 4 (Dominance): Core Power 극강 → Copy-Time 36~60개월+
```
Current Stage: ___ → Target Stage: ___

### Step 2 — Data Flywheel Design

The most powerful moat for agent products:
```
Data Flywheel Blueprint:
1. Collect: What data do you uniquely capture through usage?
2. Aggregate: How does combined data create new value?
3. Learn: How does the agent improve from this data?
4. Deliver: How do users experience the improvement?
5. Retain: Why does this make users stay?
```

Key questions:
- What data is generated that competitors cannot access?
- How many executions until the flywheel produces visible improvement?
- Is the improvement per-user or across-all-users?

### Step 3 — Workflow Integration Depth

Rate integration depth (deeper = stronger moat):
```
Level 1: Tool (용tool) — Agent does a task when asked
Level 2: Assistant — Agent proactively suggests actions
Level 3: Workflow — Agent is embedded in daily process
Level 4: System — Agent manages end-to-end process
Level 5: Infrastructure — Removing agent breaks the workflow
```

Current level: ___
Target level: ___
Path to target: ___

### Step 4 — Moat Vulnerability & Copy-Time Analysis

For each moat you're building:
```
Moat: [name]
├── Strength today: [1-5]
├── Time to build: [months]
├── Competitor Copy-Time: [months] (see domain.md Section 8-c for estimation framework)
│   ├── 경쟁사 자원 수준: [스타트업/대기업] → +/-3~6개월 조정
│   └── "동등함" 기준: 성능/규모/품질에서 80% 이상 일치
├── Depends on: [what must be true]
├── Biggest threat: [what could destroy this moat]
└── Fallback moat: [if this moat fails, pivot to ___]
```

**Copy-Time 18개월 미만이면 "진정한 moat"이 아님** — 보강 또는 다른 moat으로 전환 필요.

### Step 5 — Moat Building Roadmap & Combination Strategy

Prioritize moat investments:
```
Phase 1 (0-3 months): [Quick wins — usually UX/Speed moat]
Phase 2 (3-6 months): [Workflow integration — lock-in]
Phase 3 (6-12 months): [Data flywheel — compound advantage]
Phase 4 (12+ months): [Network effects — if applicable]
```

**Moat 조합 전략** (단일 moat보다 다중 moat의 시너지가 핵심):
```
고객 세그먼트별 우선순위:
├── Enterprise → Workflow Lock-in + Switching Cost 우선 (통합 깊이)
├── SMB → Speed/UX + Data Flywheel 우선 (빠른 가치 체감)
└── Platform → Network Effects + Data 우선 (양면 시장)

실패 시 대체 전략:
├── Data Flywheel 정체 → Workflow Lock-in으로 전환 (통합 깊이 강화)
├── Network Effects 미달 → Proprietary Knowledge로 전환 (도메인 전문성)
└── Switching Cost 약화 → Data Flywheel 가속 (독점 데이터 확대)
```

### Step 6 — Anti-Moat Patterns

Avoid these false moats (see `context/domain.md` Section 8-d for full 10-pattern list):

| False Moat | Why It Fails | Copy-Time |
|-----------|-------------|-----------|
| "We use GPT-4/Claude" | Everyone can use the same models | ~1주 |
| "Our prompts are secret" | Prompts are easily reverse-engineered | 1~3개월 |
| "We were first" | First-mover advantage is weak in AI | 6~18개월 |
| "Our UI is better" | UI is the easiest thing to copy | 6~9개월 |
| "We have more data" (비독점) | 경쟁사도 빠르게 수집 가능 | 6~12개월 |
| "Our technology is complex" | 시간만 있으면 역설계 가능 | 3~9개월 |

**핵심 테스트**: "경쟁사가 같은 자원(시간, 돈, 인력)으로 18개월 이내 복제 가능하면 moat이 아니다."

### Output

Present moat strategy:
```
Primary Moat: [type] — [description]
Secondary Moat: [type] — [description]
Current Strength: [1-5] / Target: [1-5]
Key Investment: [what to build]
Timeline: [when moat becomes defensible]
Risk: [biggest threat to moat]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|-----|-----|
| 의존 조건 부재: 예를 들어 "데이터 모아 moat"인데 사용자가 데이터 공유 거부 | Moat 평가 시 "Depends on" 항목이 실제로 부족 | 해당 moat 포기, 다른 moat 우선순위 상향 (예: workflow lock-in)  |
| Moat 침식: 경쟁사가 빠르게 따라잡음 | 12개월 후에도 경쟁사와의 성능 격차 없음 | 근본 원인 분석 (데이터 부족? 느린 개선? 접근성 차이?), 투자 방향 재조정 |
| Moat 구축 비용이 초과: 예상보다 훨씬 많은 데이터/비용 필요 | 6개월 후 수익으로 moat 비용 회수 불가 | 대체 moat 추구 (예: 빠른 UX로 초기 lock-in), 또는 timeline 재조정 |
| Network Effect moat 실패: 사용자 증가해도 가치 증가 안 함 | 월 사용자 2배 증가했는데 retention rate 변화 없음 | 사실 Network Effect가 아님을 인정, 다른 moat로 전환 |

## Quality Gate

- [ ] Moat 유형 평가: 6가지 유형 각각 1-5점 매김 (전체 합 ___ / 30)
- [ ] Maturity Stage 평가: 현재 Stage(1-4) 및 Target Stage 명시 (Yes/No)
- [ ] 주요 Moat 선정: 가장 강한 1-2개 명확히 선택 (Yes/No)
- [ ] Copy-Time 추정: 주요 moat별 경쟁사 복제 시간 산정 (18개월+ = 진정한 moat) (Yes/No)
- [ ] 취약점 분석: 각 주요 moat의 "Biggest Threat" + Fallback moat 식별 (Yes/No)
- [ ] Moat 조합 전략: 고객 세그먼트별 우선순위 및 실패 시 대체 전략 (Yes/No)
- [ ] 구축 타임라인: Phase 1-4 구체적 달성 목표 및 완료 기한 설정 (Yes/No)
- [ ] False Moat 제거: 10가지 패턴 확인, 해당 항목 제거 (Yes/No)

## Examples

### Good Example

```
제품: "법률 문서 검토 에이전트"

[Moat 유형 평가]
1. Data Flywheel: 4/5
   - 각 검토건마다 법원 판례 데이터 수집
   - 6개월 후: 일반 모델과 달리 한국 법조문 적중률 95% vs 60%
   - 경쟁사가 같은 데이터 얻기: 불가능 (고객 데이터, 기밀)

2. Workflow Lock-in: 3/5
   - 변호사들의 워크플로우 깊이 중간
   - 검토만 하고, 협상이나 체결은 여전히 사람이 함

3. Network Effects: 1/5
   - 법률 에이전트 시장에서 네트워크 효과 약함

4. Switching Cost: 2/5
   - 데이터 내보내기 가능하면 전환 비용 낮음

5. Proprietary Knowledge: 4/5
   - 한국 법조문 + 판례 조합 해석 → 전문성
   - 경쟁사가 구축하려면 법률 전문가 팀 필요

6. Speed/UX: 2/5
   - UI는 경쟁사도 따라 만들 수 있음

[주요 Moat 전략]
Primary: Data Flywheel (1번)
- 강점: 고객 데이터 독점, 시간이 지날수록 격차 증가
- 시간: 12개월

Secondary: Proprietary Knowledge (5번)
- 강점: 법률 전문가 팀이 있어야 경쟁 가능
- 시간: 6개월부터 효과 보임

[현재 강도 → 목표]
전체 moat 강도: 2.4/5 (약함) → 6개월 후 3.5/5 → 12개월 후 4.2/5

[구축 로드맵]
Phase 1 (0-3개월): Speed/UX로 초기 고객 확보 (검토 시간 50% 단축)
Phase 2 (3-6개월): Proprietary Knowledge로 정확도 증가
Phase 3 (6-12개월): Data Flywheel 강화 (고객 피드백 → 프롬프트 개선)
Phase 4 (12+개월): 다른 법적 영역으로 확장, 데이터 복합도 증가

[가장 큰 위협]
- Threat: GPT-5 또는 Claude 4 출시로 기본 성능 급상승
- Response: 우리의 한국법 전문지식으로 차별화 심화, 또는 수직 통합 (변호사 네트워크)
```

### Bad Example

```
반사례 1: Moat가 없는 제품
"우리는 ChatGPT를 더 좋게 래핑했어요"
- 기술: 경쟁사도 즉시 복제 가능
- 데이터: 따로 없음
- 워크플로우: 일반적인 챗 인터페이스
- Moat 점수: 0.5/5 (거의 없음) → 돈 버리는 투자

반사례 2: 거짓 Moat
"우리 UI가 정말 예쁘다"
- UI는 3개월이면 복제 가능
- Moat가 아님

반사례 3: 구축 불가능한 Moat
"Network Effect가 우리 moat"
- 그런데 고객은 경쟁사에 자유롭게 이동 가능
- 네트워크가 sticky하지 않음 → 거짓 moat

반사례 4: 순환 논리
"우리 데이터 moat가 강하다" (근거 제시 안함)
- 실제로는 데이터가 아직 축적 안 됨
- 또는 고객이 데이터 공유 거부
- "의도한 moat" vs "실제 moat" 차이 무시
```

---

## Further Reading
- Hamilton Helmer, *7 Powers* — Strategic power and competitive advantage
- Jerry Chen, "The New Moats" — AI-era defensibility

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
