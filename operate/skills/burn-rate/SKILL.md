---
name: burn-rate
description: "Track, analyze, and optimize token costs for AI agent operations. Break down costs by model, task type, and user segment. Use when reviewing monthly agent spending, planning cost reduction, comparing model economics, or setting token budgets for new agents."
argument-hint: "[agent to track costs for]"
allowed-tools: ["Read", "Write", "WebSearch", "WebFetch"]
model: sonnet
---

# Token Cost Tracking

> 에이전트 토큰 비용 추적, 분석, 최적화

## Core Goal

- **에이전트의 토큰 비용을 가시화하고 제어** — 선형 증가하는 비용을 데이터 기반으로 최적화하는 기초 구축
- **비용-성능 트레이드오프 의식화** — 모델 선택, 프롬프트, 컨텍스트 전략의 경제학적 영향 정량화
- **예산 중심의 운영 틀 수립** — 월간 비용 상한선과 알림 전략으로 재정 예측 가능성 확보

---

## Trigger Gate

### Use This Skill When

- 에이전트의 월간 토큰 비용을 처음 추적하거나 기존 추적을 최적화해야 할 때
- 모델 선택(Claude Sonnet vs Haiku vs Opus)이 비용에 미치는 영향을 정량화해야 할 때
- 프롬프트 압축, 캐싱, 배치 처리 등 최적화 전략의 비용 효과를 계산해야 할 때
- 월간 예산을 초과했거나 초과할 위험이 있을 때

### Route to Other Skills When

- **agent-ab-test** → 모델 다운그레이드(Sonnet → Haiku) A/B 테스트의 비용 변수 분석
- **kpi** → 비용 효율(Cost per Execution)을 KPI 대시보드에 통합하는 경우
- **incident** → 일일 비용이 갑자기 2배 이상 폭등했을 때 (즉시 긴급 대응)
- **north-star** → 비용 효율을 North Star 지표 분해의 일부로 포함하는 경우
- 배포 *전* COGS 예측이 필요할 때 → `cogs-sentinel` (hplan plugin). 이 skill의 burn-rate는 배포 *후* 추적.

### Boundary Checks

- **일반 비용 추적과의 구분** — 서버, 인프라 비용은 별도 관리, 토큰 비용(API 호출 기반)에만 집중
- **예산 책정 시의 보수성** — 예상 비용의 1.5배를 버퍼로 설정 (스파이크 대비)
- **최적화 과도** — 품질 저하 없이 비용 절감이 가능한 범위 확인 (Guardrail 지표 확인 필요)

---

## 개념

에이전트 비용의 60-90%는 LLM 토큰 비용이다. 토큰 사용을 가시화하고 최적화하지 않으면 비용이 사용량에 비례해 선형 증가하며, 이는 비즈니스 모델을 파괴할 수 있다.

## Instructions

You are setting up **token cost tracking** for: **$ARGUMENTS**

### Step 1 — Cost Baseline

Map current token usage:
```
Agent: [name]
Period: [last 30 days]

Per Execution:
├── Input tokens (avg): ___
├── Output tokens (avg): ___
├── Total tokens (avg): ___
├── Model: [name]
├── Price: $___/1K input, $___/1K output
└── Cost per execution: $___

Monthly:
├── Total executions: ___
├── Total tokens: ___
├── Total cost: $___
└── Cost per user: $___
```

### Step 2 — Cost Breakdown by Component

| Component | Tokens/exec | % of Total | Cost/exec | Optimizable? |
|-----------|------------|------------|-----------|-------------|
| System prompt | | | | Compression |
| Memory injection | | | | Retrieval tuning |
| User input | | | | Summarization |
| Tool calls | | | | Caching |
| Output generation | | | | Length control |

### Step 3 — Optimization Strategies

| Strategy | Effort | Savings | Risk |
|----------|--------|---------|------|
| **Prompt compression** | Low | 10-30% | Quality drop |
| **Response caching** | Medium | 20-50% | Stale results |
| **Model downgrade** (router) | Medium | 40-70% | Quality drop |
| **Batch processing** | Medium | 10-20% | Latency increase |
| **Context pruning** | Low | 15-25% | Missing context |
| **Output length limits** | Low | 10-20% | Truncated info |

### Step 4 — Budget Framework

```
Monthly Budget: $___

Allocation:
├── Core operations: ___% ($___) 
│   └── Alert at: ___% of allocation
├── Experimentation: ___% ($___) 
│   └── Hard cap, no overage
├── Spike buffer: ___% ($___) 
│   └── Auto-scale threshold
└── Reserve: ___% ($___) 
    └── Emergency use only

Daily burn rate target: $___
Daily burn rate alert: >$___
```

### Step 5 — Cost Monitoring Dashboard

Track these metrics:
```
Real-time:
- Current daily spend vs budget
- Cost per execution (rolling average)
- Token count per component

Weekly:
- Cost trend (week-over-week)
- Top 5 expensive operations
- Optimization opportunity score

Monthly:
- Total cost vs budget
- Cost per user trend
- ROI (value created ÷ cost)
```

### Step 6 — Cost Anomaly Detection

Define alerts:
```
⚠️ Warning:
- Daily cost > 1.5× average
- Single execution > 3× average cost
- New model pricing change detected

🔴 Critical:
- Daily cost > 2× average
- Monthly projection exceeds budget by 20%
- Cost per execution trending up for 5+ days
```

### Output

Cost tracking setup:
```
Agent: [name]
Monthly Budget: $___
Current CPE: $___
Target CPE: $___ (after optimization)
Top Optimization: [strategy] — projected ___% savings
Monitoring: [tool/method]
Alert Owner: [who gets notified]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **비용 이상 폭증** | 일일 비용이 예상의 2배 이상 | 즉시 rate limit 설정, 로그 분석으로 원인 파악 (무한 루프? 토큰 폭발?), incident 스킬로 전환 |
| **추적 데이터 누락** | 일부 API 호출이 로그에 미기록 | 로깅 인프라 점검, 누락 기간 비용 추정치로 보정, 향후 추적 강화 |
| **최적화로 인한 품질 저하** | 비용 절감 후 Accuracy/Hallucination Rate 악화 | 최적화 롤백, Guardrail 수준 재설정, 보수적 절감 전략으로 재계획 |
| **모델 가격 정책 변경** | API 제공자의 가격 인상 발표 | 영향도 계산 (월간 추가 비용), 모델 라우팅/다운그레이드 검토, 예산 재책정 |
| **예산 초과 누적** | 월말에 임계값 200% 초과 발견 | 원인 분석 (예측 오류? 트래픽 급증?), 긴급 최적화, 다음 분기 예산 재협상 |

---

## Quality Gate

- [ ] 현재 비용 기준선이 정확히 계산되었는가? (입출력 토큰 · 모델 · 가격 기반) (Yes/No)
- [ ] 월간 예산이 설정되고 부서별 할당이 명확한가? (Yes/No)
- [ ] 비용 구성 요소별 분해(시스템 프롬프트, 메모리, 출력)가 완료되었는가? (Yes/No)
- [ ] 최적화 전략의 위험도(품질 저하) 평가를 마쳤는가? (Yes/No)
- [ ] 실시간 비용 모니터링과 알림 시스템이 구성되었는가? (Yes/No)
- [ ] 의사결정 기록(Ship/Keep/Iterate)과 비용 효과가 명문화되었는가? (Yes/No)

---

## Examples

### Good Example

```
비용 추적: AI 고객 지원 에이전트

월간 비용 기준선 (지난 30일):
├── 총 실행: 12,000건
├── 평균 토큰: 4,500개/실행
├── 모델: Claude Sonnet
├── 비용: $0.003/1K input, $0.015/1K output
└── 월간 비용: $810

비용 분해 (100건 기준):
├── 시스템 프롬프트: 1,200 tokens (26%)
├── 메모리 주입: 1,500 tokens (33%)
├── 사용자 입력: 800 tokens (18%)
├── 출력 생성: 1,000 tokens (22%)

최적화 계획:
- 프롬프트 압축: 1,200 → 800 tokens = -33% (15분 작업)
- 메모리 루팅: 1,500 → 900 tokens = -40% (1일 작업)
- 결과: 월간 예상 절감 = -30% → $567/월

위험도: 저 (품질 저하 미미)
```

### Bad Example

```
"토큰 비용이 많이 드니까 모델을 다운그레이드하자"

❌ 문제점:
- MDE(최소 감지 차이) 없이 "많다"는 주관적 판단
- 현재 CPE(비용/실행) 계산 없음
- 모델 다운그레이드의 정확도 영향 미평가
- 예산 책정 없이 임시방편으로 대응
- Guardrail 메트릭(Accuracy, Hallucination)을 확인하지 않음

→ 재작업: 비용 기준선 계산 → 분해 분석 → A/B 테스트 → 트레이드오프 평가
```

---

## Further Reading
- Anthropic API Pricing — https://docs.anthropic.com/en/docs/about-claude/models
- Token optimization strategies — Caching, batching, model routing

---

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
