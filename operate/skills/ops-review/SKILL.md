---
name: ops-review
description: "주간/월간 운영 리뷰 + 이해관계자 업데이트 보고. 비용 추적(burn-rate)·주간 롤업(weekly-rollup)·실제 LLM 비용 vs COGS 대조·이상 감지·예산 권고. 추가로 이해관계자 보고서 4종: exec-summary(임원 1-pager), weekly-update(팀 주간), partner-brief(외부 파트너), confluence-export(사내 위키 포맷 변환). 수치 집계=결정론, 산문 생성만 LLM. Use when running regular operational reviews or communicating project status to stakeholders."
argument-hint: "[--mode cost|weekly|full|exec-summary|weekly-update|partner-brief|confluence-export] [--source exec-summary|weekly-update|partner-brief]"
allowed-tools: ["Read", "Write", "mcp__notion__notion-create-pages", "mcp__notion__notion-fetch"]
model: inherit
---

# Ops Review

> 주간/월간 운영 리뷰 — 비용 추적과 주간 지표 롤업 통합

## Core Goal

- **에이전트 토큰 비용을 가시화하고 제어** — 선형 증가하는 비용을 데이터 기반으로 최적화하는 기초 구축
- **주간 지표를 단일 롤업으로 압축** — 운영팀이 5분 안에 신호만 받게 함
- **비용-성능 트레이드오프 의식화** — 모델 선택, 프롬프트, 컨텍스트 전략의 경제학적 영향 정량화
- **예산 중심의 운영 틀 수립** — 월간 비용 상한선과 알림 전략으로 재정 예측 가능성 확보

---

## Trigger Gate

### Use This Skill When

- 에이전트의 월간 토큰 비용을 추적하거나 최적화해야 할 때 (`--mode cost`)
- 주간 지표 요약과 운영 신호를 빠르게 확인해야 할 때 (`--mode weekly`)
- 비용 리뷰 + 주간 롤업을 한 번에 수행해야 할 때 (`--mode full`)
- 모델 선택(Claude Sonnet vs Haiku vs Opus)이 비용에 미치는 영향을 정량화해야 할 때
- 월간 예산을 초과했거나 초과할 위험이 있을 때
- "진행 상황 임원 보고서 만들어줘" → `--mode exec-summary`
- "이번 주 팀 업데이트 작성해줘" → `--mode weekly-update`
- "파트너에게 진행상황 요약 보내야 해" → `--mode partner-brief`
- "Confluence/사내 위키에 올릴 수 있는 형식으로 변환해줘" → `--mode confluence-export`

### Route to Other Skills When

- **incident** → 일일 비용이 갑자기 2배 이상 폭등했을 때 (즉시 긴급 대응)
- **metrics-design** → 비용 효율(Cost per Execution)을 North Star/KPI에 통합할 때
- **portfolio** → 비용 데이터를 에이전트 포트폴리오 헬스 스코어로 집계할 때
- **sprint --step status** → 보고서에 필요한 진행 데이터 수집
- **ticket-bridge --mode status** → 티켓에 상태 코멘트
- **ask-team** → 팀원에게 보고서 직접 전달 (ops-review는 산문 생성까지, 발송은 ask-team)

### Boundary Checks

- **일반 비용 추적과의 구분** — 서버, 인프라 비용은 별도. 토큰 비용(API 호출 기반)에만 집중
- **최적화 과도** — 품질 저하 없이 비용 절감이 가능한 범위 확인 (Guardrail 지표 확인 필요)
- 배포 *전* COGS 예측 → `cogs-sentinel` (hplan plugin). 이 스킬은 배포 *후* 추적.

---

## 개념

에이전트 비용의 60-90%는 LLM 토큰 비용이다. 토큰 사용을 가시화하고 최적화하지 않으면 비용이 사용량에 비례해 선형 증가하며, 비즈니스 모델을 파괴할 수 있다.

주간 롤업은 비용 데이터를 포함하여 운영 신호를 5분 안에 소화하는 단일 브리프다.

## Instructions

You are running an ops review for: **$ARGUMENTS**

Parse `--mode` from the arguments:
- `--mode cost` → Run Cost Review only
- `--mode weekly` → Run Weekly Rollup only
- `--mode full` or no `--mode` flag → Run both (default)
- `--mode exec-summary` → 임원 1-pager 보고서 (Stakeholder Updates 섹션)
- `--mode weekly-update` → 팀 주간 업데이트 보고서
- `--mode partner-brief` → 외부 파트너 요약 보고서
- `--mode confluence-export` → 기존 보고서를 Confluence/사내 위키 포맷으로 변환 (`--source` 필요)

---

### Cost Review (`--mode cost` or `--mode full`)

#### C1 — Cost Baseline

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

#### C2 — Cost Breakdown by Component

| Component | Tokens/exec | % of Total | Cost/exec | Optimizable? |
|-----------|------------|------------|-----------|-------------|
| System prompt | | | | Compression |
| Memory injection | | | | Retrieval tuning |
| User input | | | | Summarization |
| Tool calls | | | | Caching |
| Output generation | | | | Length control |

#### C3 — Optimization Strategies

| Strategy | Effort | Savings | Risk |
|----------|--------|---------|------|
| **Prompt compression** | Low | 10-30% | Quality drop |
| **Response caching** | Medium | 20-50% | Stale results |
| **Model downgrade** (router) | Medium | 40-70% | Quality drop |
| **Batch processing** | Medium | 10-20% | Latency increase |
| **Context pruning** | Low | 15-25% | Missing context |
| **Output length limits** | Low | 10-20% | Truncated info |

#### C4 — Budget Framework

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

#### C5 — Cost Anomaly Detection

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

#### Cost Review Output

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

### Weekly Rollup (`--mode weekly` or `--mode full`)

#### W1 — 데이터 적재

이번 주 운영 지표 로드:
- 에이전트별 실행 건수, 성공률, 비용
- 누락 에이전트 명시

#### W2 — 주간 지표 요약

| 에이전트 | 실행수 | 성공률 | CPE | 주간 비용 | 전주 대비 |
|---------|--------|--------|-----|---------|---------|
| | | | | | Δ |

#### W3 — 이상 감지

- 성공률 < 90% 에이전트 명단
- 비용이 전주 대비 50% 이상 증가한 에이전트
- 실행 건수가 전주 대비 50% 이상 급감한 에이전트

#### W4 — 다음 스프린트 예산 권고

전주 실제 비용 × 예상 트래픽 변화율 기반으로 다음 주 예산 산출

#### Weekly Rollup Output

```
주차: [week-id]

주간 요약:
  총 실행: [N]건
  총 비용: $[N]
  평균 성공률: [%]
  전주 대비 비용: Δ[+/-$N]

이상 감지:
  비용 급증: [에이전트명] (+[%])
  성공률 저하: [에이전트명] ([%])

다음 주 예산 권고: $[N]
운영 주의 사항:
1. [사항 1]
2. [사항 2]
```

---

## Stakeholder Updates (`--mode exec-summary|weekly-update|partner-brief|confluence-export`)

> PM이 이해관계자(임원/팀/외부 파트너)에게 보내는 업데이트 보고서를 생성한다.
> `PROGRESS.md` + `decision_log` + sprint `actual_log`를 소비해 각 대상에 맞는 산문을 생성한다.
> **수치 집계 = 결정론, 서술 생성만 LLM** (Rule 5 경계 아래 참조).

### Rule 5 준수 경계

| 작업 | LLM | 근거 |
|---|---|---|
| 완료/진행중/블로커 수 집계 | ❌ 결정론 | actual_log grep, PROGRESS.md 파싱 |
| Gate 색상 결정 | ❌ 결정론 | 아래 lookup table |
| 보고서 산문 생성 | ✅ | Rule 5 허용: 자연어 생성 |
| 수치 수정·조정 | ❌ 금지 | 원본 데이터 인용만 |

### 공통 Step 0 — 데이터 수집 (결정론)
```bash
# 완료 태스크 수
DONE=$(grep -c "complete" .track/actual_log.jsonl 2>/dev/null || echo 0)
# 블로커 수
BLOCKED=$(grep -c "blocker" .track/actual_log.jsonl 2>/dev/null || echo 0)
# PRD §1 목표
grep -A3 "^## 1" harness/PRD.md 2>/dev/null | head -5 || echo "PRD 없음"
```

### mode: exec-summary
임원용 1페이지 요약. 포맷:
- 제품명 + 현재 단계 (1줄)
- 완료된 것 (bullet 3개 이하)
- 다음 2주 계획 (bullet 3개 이하)
- 리스크/의사결정 필요 항목 (있는 경우만)
- Gate 상태: GREEN/CONDITIONAL_GO/RED

#### Gate 상태 결정 (결정론 — LLM 0)

harness 파일에서 수치를 읽어 Gate 색상을 자동 계산한다:

```bash
# Gate 상태 결정 — actual_log.jsonl 이벤트 기반
# 주의: probe가 기록하는 event는 "tool_call" 뿐입니다.
# "blocker", "task_start", "complete" 이벤트는 conductor/sprint이 명시적으로 기록해야 합니다.
# 해당 이벤트가 없으면 UNKNOWN fallback을 사용합니다.

BLOCKERS=$(grep -c '"event":"blocker"' .track/actual_log.jsonl 2>/dev/null || echo 0)
TASK_START=$(grep -c '"event":"task_start"' .track/actual_log.jsonl 2>/dev/null || echo 0)
TASK_DONE=$(grep -c '"event":"complete"' .track/actual_log.jsonl 2>/dev/null || echo 0)
COGS_STATUS=$(python3 -c "import json; d=json.load(open('harness/build-gate/cogs_result.json')); print(d.get('status','UNKNOWN'))" 2>/dev/null || echo "UNKNOWN")

# 이벤트 존재 여부 확인
HAS_TRACKING_DATA=$([[ "$TASK_START" -gt 0 ]] && echo "yes" || echo "no")

if [[ "$HAS_TRACKING_DATA" == "no" ]]; then
  # probe만 있고 conductor 이벤트가 없는 경우: tool_call 수로 대체 추정
  TOOL_CALLS=$(grep -c '"event":"tool_call"' .track/actual_log.jsonl 2>/dev/null || echo 0)
  EXIT_ERRORS=$(python3 -c "
import json
errors = 0
for line in open('.track/actual_log.jsonl'):
    try:
        d = json.loads(line)
        if d.get('exit_code', 0) != 0:
            errors += 1
    except: pass
print(errors)
" 2>/dev/null || echo 0)
  # tool_call 데이터 기반 근사: 에러 비율로 BLOCKERS 추정
  BLOCKERS=$EXIT_ERRORS
  TOTAL=$TOOL_CALLS
  DONE=$(( TOOL_CALLS - EXIT_ERRORS ))
else
  TOTAL=$TASK_START
  DONE=$TASK_DONE
fi

COMPLETION=$([ "$TOTAL" -gt 0 ] && echo "$((DONE * 100 / TOTAL))" || echo 0)
```

> **데이터 요건**: BLOCKERS/완료율이 정확하려면 conductor가 actual_log.jsonl에
> `{"event":"blocker"}`, `{"event":"task_start"}`, `{"event":"complete"}` 이벤트를 기록해야 합니다.
> 이 이벤트가 없으면 probe의 exit_code 기반 근사값을 사용합니다 (정확도 낮음).
> probe-errors.log에 에러 로그가 없다면 GREEN 가능성이 높습니다.

**Gate 결정 규칙** (우선순위 순서, 결정론 lookup):

| 조건 | Gate |
|---|---|
| BLOCKERS ≥ 3 | 🔴 RED |
| COGS_STATUS = RED | 🔴 RED |
| BLOCKERS ≥ 1 OR COGS_STATUS = CONDITIONAL_GO OR COMPLETION < 50 | 🟡 CONDITIONAL_GO |
| COMPLETION ≥ 80 AND BLOCKERS = 0 AND COGS_STATUS = GREEN | 🟢 GREEN |
| 그 외 | 🟡 CONDITIONAL_GO |

> 데이터 파일이 없으면 "UNKNOWN — actual_log 또는 cogs_result.json 없음"으로 표시. 임의 판단 금지.
> PM이 Gate 색상을 수동으로 바꾸고 싶으면 `--gate-override RED|GREEN|CONDITIONAL_GO` 플래그 사용.

### mode: weekly-update
팀 주간 업데이트. 포맷:
- 이번 주 완료 (actual_log 인용)
- 진행 중 (current_task 기준)
- 블로커 (실제 발생한 것만)
- 다음 주 계획 (implementation-plan 기준)

### mode: partner-brief
외부 파트너 요약. 포함 항목: 제품 목적, 현재 단계, 기대하는 것, 다음 연락 시점.
기술 세부사항 제외. 마케팅 문구 제외.

### mode: confluence-export

Confluence 페이지에 붙여넣거나 업로드하기 위한 포맷 변환 모드. **Confluence API를 직접 호출하지 않는다** — 자격증명 불필요.

**사용 방법:**
1. 먼저 다른 모드로 보고서를 생성한다 (exec-summary / weekly-update / partner-brief).
2. 그 다음 `--mode confluence-export --source exec-summary` (또는 weekly-update/partner-brief)를 실행한다.

**Step 1 — 소스 파일 확인 (결정론)**
- `--source` 인자로 지정된 파일 읽기 (기본값: exec-summary → `docs/exec-summary.md`)
- `--source` 미지정 시 fail loud: "어떤 파일을 변환할지 명시하세요 (`--source exec-summary|weekly-update|partner-brief`)"

**Step 2 — Confluence 마크업으로 변환 (LLM)**

Confluence Wiki Markup 또는 Confluence Markdown 형식으로 변환:
- `##` 헤딩 → Confluence `h2.` / `h3.` 형식
- 마크다운 표 → Confluence `||` 테이블 문법
- bullet → `*` (Confluence 목록)
- 코드 블록 → `{code}...{code}` (언어 명시 가능)
- 줄바꿈 규칙: Confluence는 빈 줄 1개 = 단락 구분

**Step 3 — 출력**

`docs/{source}-confluence.md` 에 저장. 원본 파일은 변경하지 않는다.

파일 상단에 업로드 안내를 prepend한다:
```
<!-- Confluence Upload Guide
     1. Confluence 페이지 편집 모드 진입
     2. "..." 메뉴 → Insert → Markup → Confluence Wiki Markup
     3. 아래 내용을 붙여넣기
     4. 저장 후 렌더링 확인
     이 파일은 hplan ops-review --mode confluence-export가 생성한 변환 산출물입니다.
     원본: docs/{source}.md
-->
```

> **정보보안 참고:** hplan은 Confluence 자격증명(API token, username)을 수집하거나 저장하지 않는다. 실제 업로드는 PM이 직접 Confluence UI에서 수행한다.

**대체 경로 — Notion publish**

> Confluence가 없는 환경에서 PRD를 Notion 페이지로 publish하는 대체 경로.
> Confluence MCP가 있는 환경에서는 직접 publish.

1. harness/PRD.md를 읽어 15섹션을 Notion 페이지 계층 구조로 변환 (LLM)
2. **확인 게이트**: 변환 결과 + 대상 Notion 워크스페이스를 보여주고 승인받는다
3. 승인 후 `mcp__notion__notion-create-pages`로 PRD 페이지 생성
4. 팀 공유: 생성된 Notion 페이지 URL을 `harness/prd-share-url.txt`에 기록

Confluence MCP 연결 시 (mcp__confluence__create_page 도구가 있으면):
```
allowed-tools 확인 → Confluence MCP 사용 → Confluence에 직접 publish
```

> 출력: 팀이 접근 가능한 PRD URL. 로컬 파일 의존 탈피.

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **비용 이상 폭증** | 일일 비용이 예상의 2배 이상 | 즉시 rate limit 설정, 로그 분석으로 원인 파악 (무한 루프? 토큰 폭발?), incident 스킬로 전환 |
| **추적 데이터 누락** | 일부 API 호출이 로그에 미기록 | 로깅 인프라 점검, 누락 기간 비용 추정치로 보정 |
| **최적화로 인한 품질 저하** | 비용 절감 후 Accuracy/Hallucination Rate 악화 | 최적화 롤백, Guardrail 수준 재설정 |
| **모델 가격 정책 변경** | API 제공자의 가격 인상 발표 | 영향도 계산, 모델 라우팅/다운그레이드 검토, 예산 재책정 |
| **주간 데이터 누락** | Rollup 시 일부 에이전트 데이터 없음 | 누락 에이전트 명시 후 가용 데이터 기반 부분 롤업 진행 |
| **보고서 데이터 파일 부재** | actual_log/PROGRESS.md/cogs_result.json 없음 | Gate "UNKNOWN" 표시, 임의 판단 금지 (Rule 8) |
| **confluence-export `--source` 미지정** | `--source` 플래그 없음 | fail loud — "어떤 파일을 변환할지 명시 (exec-summary/weekly-update/partner-brief)" |

---

## Quality Gate

**Cost Review**
- [ ] 현재 비용 기준선이 정확히 계산되었는가? (입출력 토큰 · 모델 · 가격 기반) (Yes/No)
- [ ] 월간 예산이 설정되고 부서별 할당이 명확한가? (Yes/No)
- [ ] 비용 구성 요소별 분해가 완료되었는가? (Yes/No)
- [ ] 최적화 전략의 위험도(품질 저하) 평가를 마쳤는가? (Yes/No)
- [ ] 실시간 비용 모니터링과 알림 시스템이 구성되었는가? (Yes/No)

**Weekly Rollup**
- [ ] 모든 활성 에이전트가 롤업에 포함되었는가? (Yes/No)
- [ ] 이상 감지 기준(성공률 임계값, 비용 급증 임계값)이 명시되었는가? (Yes/No)
- [ ] 다음 스프린트 예산 권고가 포함되었는가? (Yes/No)
- [ ] 운영 주의 사항이 1~3개로 압축되었는가? (Yes/No)

**Stakeholder Updates**
- [ ] 모든 수치 = 파일 인용 (생성 0)
- [ ] Gate 색상 = lookup table 결정론 (LLM 판단 0)
- [ ] exec-summary 1쪽 이하
- [ ] partner-brief에 내부 코드명/기술 용어 미포함
- [ ] confluence-export: 원본 파일 변경 0 (새 파일만 생성)
- [ ] confluence-export: 업로드 안내 주석 포함

---

## Examples

### Good Example — `--mode cost`

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
- 프롬프트 압축: 1,200 → 800 tokens = -33%
- 메모리 루팅: 1,500 → 900 tokens = -40%
- 결과: 월간 예상 절감 = -30% → $567/월
```

### Good Example — `--mode weekly`

```
주차: 2026-W21

주간 요약:
  총 실행: 8,400건
  총 비용: $620
  평균 성공률: 94.2%
  전주 대비 비용: Δ+$45

이상 감지:
  비용 급증: mail-router (+62%) — 재시도 루프 의심
  성공률 저하: news-curator (87%) — 임계값 90% 미달

다음 주 예산 권고: $650
운영 주의 사항:
1. mail-router 재시도 루프 원인 분석
2. news-curator 프롬프트 점검
```

### Bad Example

```
"토큰 비용이 많이 드니까 모델을 다운그레이드하자"

❌ 문제점:
- 현재 CPE 계산 없음
- 모델 다운그레이드의 정확도 영향 미평가
- 예산 책정 없이 임시방편으로 대응
- Guardrail 메트릭 확인 안 함

→ 재작업: 비용 기준선 계산 → 분해 분석 → 최적화 전략 평가
```

---

## Further Reading
- Anthropic API Pricing — https://docs.anthropic.com/en/docs/about-claude/models
- Token optimization strategies — Caching, batching, model routing
