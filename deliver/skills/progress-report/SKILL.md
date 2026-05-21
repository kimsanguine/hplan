---
name: progress-report
description: "Force a current-status report to the user at event-driven trigger points — NOT weekly cadence (operate/weekly-rollup handles that). 7 deterministic triggers (phase_transition, blocker_count≥2, context_token_pct≥0.7, human_approval_needed, cumulative_token_overrun, elapsed_overrun, explicit_user_ask) all detected without LLM. The report itself (current_phase / completion_pct / remaining / blockers / next_decision / eta) uses LLM for natural language rendering only — trigger logic and metric computation are 100% deterministic per Rule 5."
argument-hint: "[live | trigger <name> | after <task-id>]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- 사용자에게 **주요 시점마다 강제 보고** — weekly 가 아니라 event-driven
- 트리거 검출·메트릭 계산은 결정론 (LLM 호출 0)
- 자연어 보고 문구 생성만 LLM (Rule 5 의 "자연어 생성" 허용 영역)
- AI 코딩 최초의 event-driven 진행률 보고 시스템 (operate/weekly-rollup 와 cadence 차별화)

---

## operate/weekly-rollup 와 차별화 (왜 별도 스킬인가)

| 축 | operate/weekly-rollup | track/progress-report |
|---|---|---|
| Cadence | 시간 기반 (매주) | **Event-driven (주요 시점)** |
| Scope | 다중 에이전트 운영 통계 | 단일 프로젝트 실시간 진행 |
| 목적 | 회고·집계 | **실시간 강제 동기화** |
| Trigger | cron / 매주 정기 | phase 전환·blocker·임계치 |

> 둘을 하나로 합치면 trigger 정의가 흐려져 양쪽 가치 모두 깎임. v0.7 operate 그대로 두고 track 에 별도 신규.

---

## 7개 결정론 트리거

| # | 트리거 | 검출 | LLM |
|---|---|---|---|
| 1 | **phase_transition** | gate-checkpoint 통과 직후 (file write 시그널) | ❌ |
| 2 | **blocker_count_threshold** | blocker-detect 가 score ≥ 8 인 blocker ≥ 2개 누적 | ❌ |
| 3 | **context_token_pct_threshold** | actual_log.jsonl 의 tokens_total / max_context ≥ 0.70 | ❌ |
| 4 | **human_approval_needed** | gate-checkpoint 가 human 승인 게이트 도달 | ❌ |
| 5 | **cumulative_token_overrun** | 실측 token 누적 > predicted.json 의 total_tokens_p90 | ❌ |
| 6 | **elapsed_overrun** | 경과 minutes > predicted.json eta_p90_minutes | ❌ |
| 7 | **explicit_user_ask** | 사용자가 "상태?", "어디까지 됐어?", "status" 입력 (정규식) | ❌ |

7개 모두 카운터·임계치·정규식. LLM 호출 0.

---

## Trigger Gate

### Use This Skill When
- 7개 트리거 중 하나가 발화 (자동) 또는 사용자가 명시 호출
- gate-checkpoint 통과 직후 자동 (progress-probe Hook 연계)
- live 모드 — 사용자가 지금 상태 묻기

### Route to Other Skills When
- 보고 자체가 아니라 패턴 분석이 필요 → `track/blocker-detect`
- 주간 운영 회고 → `operate/weekly-rollup`
- 디자인 위반 보고 → `craft/craft-lint`

### Boundary Checks
- predicted.json 부재 시 fallback (실측 데이터만 출력, 비교 없음)
- 보고 자체에 trigger 가 명시되지 않으면 fail loud (왜 지금 보고하는가)
- 보고 분량 ≤ 30 줄 (사용자 인지 부담)

---

## 보고 포맷 (필수 6 섹션)

```markdown
─── progress-report ─── <feature-name> ─── triggered by: <trigger-name>
Predicted scope:  X tasks · ~Y LOC · ~Z tokens · ~T hours
Actual progress:  X/Y tasks complete (P%)
                  L LOC written (predicted L0, +/-Δ%)
                  T tokens spent (predicted T0, +/-Δ%)
                  E hours elapsed

Velocity:         R tasks/hour (baseline: B) +/-Δ%
ETA (p50):        +X hours    ETA (p90): +Y hours

🚨 Blockers (N):
  T-XXX "<title>" — score S
        → suggested: <action from blocker-detect>

Next gate:        <gate-name> — <human approval required | auto>
                  Estimated arrival: <ISO ts>
```

> 위 포맷은 결정론 — 메트릭은 actual_log + predicted.json 비교. 자연어 일부 (suggested action 문구) 만 LLM 생성.

---

## Instructions

You are generating a progress-report for trigger: **$ARGUMENTS**

**Step 1 — trigger 식별 (결정론)**
- live: 직전 30분 윈도우 + 7 트리거 중 발화 여부 점검
- trigger <name>: 명시된 트리거가 실제 조건 충족하는지 검증
- after <task-id>: 해당 task complete event 직후

**Step 2 — predicted.json 로드 + actual_log.jsonl 집계 (결정론)**
- predicted: total_tasks, total_loc_p50/p90, total_tokens_p50/p90, eta_p50/p90_minutes, critical_path
- actual: completed_tasks (event=complete 카운터), total_loc (loc_delta 합), tokens_total, elapsed (start→now)

**Step 3 — deviation 계산 (결정론)**
```python
loc_delta_pct = (actual_loc - predicted_loc_p50) / predicted_loc_p50 * 100
token_delta_pct = (actual_tokens - predicted_tokens_p50) / predicted_tokens_p50 * 100
velocity_actual = completed_tasks / elapsed_hours
velocity_baseline = baseline.jsonl meta (이전 평균)
eta_remaining_p50 = (predicted_total_minutes_p50 - elapsed_minutes) - completed_minutes
eta_remaining_p90 = (predicted_total_minutes_p90 - elapsed_minutes) - completed_minutes
```

**Step 4 — blocker-detect 결과 인용 (이미 결정론 결과)**
- `.track/blockers.md` 에서 score ≥ 8 인 blocker 만 인용
- score, evidence, suggested action 그대로

**Step 5 — next gate 식별 (결정론)**
- gate-checkpoint 의 정의된 gate 중 가장 가까운 다음 → arrival time = elapsed + remaining_p50

**Step 6 — 자연어 보고 생성 (LLM, Rule 5 자연어 영역)**
- Step 2-5 의 결정론 메트릭을 받아 6 섹션 보고 문구로 변환
- 보고 톤: 간결, 사실 위주, 30줄 이내
- suggested action 의 자연어 변환은 OK (예: blocker-detect 의 "spawn subagent OR human review" → "T-008 에 sub agent 분배 또는 본인 직접 진단 권유")

**Step 7 — 출력 + 다음 보고 시점 안내**
- stdout 또는 `.track/reports/<ts>.md`
- 다음 7 트리거 중 어느 것이 다음 발화 후보인지 명시

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| trigger 명시 안 됨 | $ARGUMENTS 빈 값 | "live 로 default 진입, 트리거 자동 감지" |
| predicted.json 없음 | file not found | 실측만 출력 모드 (deviation 컬럼 N/A) + warning |
| actual_log.jsonl 비어 있음 | wc -l = 0 | progress-probe install 권유 fail loud |
| trigger 검증 실패 (조건 미충족인데 호출) | Step 1 검증 | "트리거 조건 미충족, live 모드로 전환 또는 cancel" |
| Step 6 에서 LLM 호출이 메트릭 변경 | code review | 즉시 fail (LLM 은 표현만, 숫자 변경 금지) |

---

## Quality Gate

- [ ] 6 섹션 모두 포함 (predicted / actual / velocity / ETA / blockers / next gate)
- [ ] 보고 분량 ≤ 30 줄
- [ ] trigger 명시 (보고 첫 줄에)
- [ ] Step 6 의 LLM 호출이 숫자·메트릭 변경하지 않음 (결정론 메트릭 보존)
- [ ] 7 트리거 중 어느 것이 다음 후보인지 명시

---

## Examples

### Good Example
**입력:** "live"

**기대 출력:**
```
─── progress-report ─── user-auth-v2 ─── triggered by: blocker_count_threshold (T-008, T-011 누적)

Predicted scope:  12 tasks · ~1,400 LOC · ~42K tokens · ~5.2h
Actual progress:   7 / 12 tasks complete (58%)
                   980 LOC written (predicted 820, +19%)
                   31K tokens spent (predicted 24K, +29% — bloat alert)
                   3h 41m elapsed

Velocity:         1.9 tasks/hour (baseline: 2.4) -21%
ETA (p50):        +2h 10m   ETA (p90): +4h 30m

🚨 Blockers (2):
  T-008 "OAuth callback handler" — score 17
        → T-008 에 sub agent 분배 또는 본인 직접 진단 권유
  T-011 "Email verification" — score 8 (blockedBy T-008)

Next gate:        impl-complete → human approval required
                  Estimated arrival: 2026-05-17T14:50 KST

Next trigger candidate: cumulative_token_overrun (현재 31K vs predicted_p90 35K, 89%)
```

### Bad Example
**입력:** (인자 없음, predicted.json 없음, actual_log 없음)

**왜 나쁜가:** 보고 기반 데이터 0건

**기대 동작:** "estimate-tasks + progress-probe install 먼저 수행, 그 후 progress-report live" fail loud

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Trigger Definitions
!`cat references/trigger-definitions.md 2>/dev/null || echo ""`

### Report Tone Guide
!`cat references/report-tone.md 2>/dev/null || echo ""`
