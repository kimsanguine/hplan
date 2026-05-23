---
name: track
description: "Unified progress tracking skill — probe (append-only PostToolUse hook), detect (deterministic blocker pattern scan), and report (event-driven status report). Consolidates progress-probe, blocker-detect, and progress-report into a single --mode interface. LLM 호출은 report 모드의 자연어 렌더링에만 허용(Rule 5 준수). 공유 파일 .track/actual_log.jsonl에 동시 쓰기 금지 — detect/report는 read-only."
argument-hint: "[--mode probe|detect|report] [probe: install|status|replay <id>] [detect: since <ISO>|task <id>|live] [report: live|trigger <name>|after <task-id>]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

세 모드를 단일 인터페이스로 통합한다:

| 모드 | 책임 | 파일 접근 | LLM |
|---|---|---|---|
| `--mode probe` | `.track/actual_log.jsonl` append-only 기록 | 쓰기 (atomic append) | ❌ |
| `--mode detect` | jsonl 블로커 패턴 결정론 스캔 | 읽기 전용 | ❌ |
| `--mode report` | 이벤트 트리거 시 진행 상태 강제 보고 | 읽기 전용 | ✅ (자연어 렌더링만) |

> ⚠️ **동시 실행 금지**: probe만 `.track/actual_log.jsonl`에 쓴다. detect·report는 동 파일을 read-only로 읽는다. 두 모드를 동시에 실행하면 jsonl 손상 위험.

---

## Rule 5 준수 경계

| 작업 | LLM 사용 | 근거 |
|---|---|---|
| Hook 콜백 → jsonl append | ❌ | 결정론 shell |
| 정규식·카운터·임계치 블로커 감지 | ❌ | Rule 5: routing/policy는 결정론 |
| 트리거 조건 검출 (7종) | ❌ | 카운터·임계치 비교 |
| 자연어 보고 문구 생성 | ✅ | Rule 5 허용: 자연어 생성 |

---

## Trigger Gate

### Use This Skill When
- "작업 진행 상황 추적하고 싶어" → `--mode probe install`
- "블로커 감지해줘" → `--mode detect live`
- "진행 보고서 만들어줘" → `--mode report live`
- estimate-tasks가 `.track/predicted.json`을 lock한 직후 → `--mode probe install`
- context 70% 임박 알림 → `--mode detect`
- gate-checkpoint 통과 직후 → `--mode report trigger phase_transition`

### Route to Other Skills When
- 코드 리뷰 요청 → 이 스킬 범위 밖
- UI 디자인 확인 → `deliver/ui-validate`
- 주간 운영 회고 → `operate/weekly-rollup`
- 비용 시뮬레이션 → `discover/cost-sim`

### Boundary Checks
- `.track/actual_log.jsonl` 부재 시 detect/report → "probe install 먼저" fail loud
- `predicted.json` 부재 시 report → 실측 데이터만 출력, deviation 컬럼 N/A
- 모드 미명시 → `--mode probe` 기본값으로 진입 + 사용자 안내

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--mode` | `$ARGUMENTS` | probe/detect/report 분기 |
| sub-args | `$ARGUMENTS` (모드 이후 나머지) | 각 모드 내부 파라미터 |
| `.track/actual_log.jsonl` | probe가 작성 | detect/report가 읽음 |
| `.track/predicted.json` | estimate-tasks | detect/report 비교 기준 |
| `profiles/<op>/velocity/baseline.jsonl` | velocity-baseline | report ETA 계산 |

---

## Instructions

You are running track skill with arguments: **$ARGUMENTS**

### 공통 Step 0 — 모드 파싱

```
args = parse("$ARGUMENTS")
mode = args.get("--mode", "probe")   # 기본값: probe
sub_args = args remainder after --mode value
```

모드 미명시 시 사용자에게 안내:
> "모드 미명시 — `--mode probe` 기본값으로 진입합니다. 사용 가능: `--mode probe|detect|report`"

---

### Mode: probe

**probe의 역할**: Claude Code 매 tool call마다 `.track/actual_log.jsonl`에 이중 메커니즘으로 기록.

`sub_args` 가능 값: `install`, `status`, `replay <session-id>`

#### probe install

**Step 1 — .track/ 디렉터리 + .gitignore 등록**
- `mkdir -p .track`
- `.gitignore`에 `.track/` 없으면 append

**Step 2 — Hook 등록**
- `.claude/settings.json`의 hooks 필드에 PostToolUse 항목 추가:
```json
{"hooks": {"PostToolUse": [{"command": "scripts/track-probe.sh hook --tool $TOOL --file $FILE --exit $EXIT"}]}}
```
- 기존 hooks가 있으면 array append (덮어쓰기 금지)

**Step 3 — fallback shell 작성**
- `scripts/track-probe.sh` 신규 (없으면)
- `chmod +x`
- 내용: shell argparse + ISO8601 timestamp + JSON line write

**Step 4 — Hook smoke test**
- `bash scripts/track-probe.sh hook --tool test --file noop --exit 0`
- jsonl 마지막 줄에 test entry 확인 → pass

**Step 5 — 사용자 안내**
- Hook이 PostToolUse에 등록됐음
- silent fail 의심 시 `--mode probe status`로 점검
- jsonl 위치: `.track/actual_log.jsonl`

#### probe status

**Step 1 — Hook 활성 점검**
- 직전 5분의 `actual_log.jsonl` entry 수
- `source: "hook"` vs `source: "shell"` 비율
- Hook 비율 < 80% 또는 entry 0 → warning

**Step 2 — 보고**
- 지난 1h / 24h jsonl entry 수
- Hook silent fail 의심 여부
- `predicted.json` lock 이후 경과 시간

#### probe replay \<session-id\>

**Step 1 — Claude Code session jsonl 로드**
- `~/.claude/projects/<encoded>/<session-id>.jsonl`

**Step 2 — tool_use entry만 필터**

**Step 3 — actual_log.jsonl에 누락분 append**
- 기존 actual_log의 ts와 비교, 빠진 것만 추가
- source: "shell"로 표기

**Step 4 — 보고**
- 추가된 entry 수, 가장 오래된/최근 ts

---

### Mode: detect

**detect의 역할**: `.track/actual_log.jsonl` 스캔 → 5종 결정론 블로커 패턴 감지. LLM 호출 0.

`sub_args` 가능 값: `since <ISO>`, `task <id>`, `live` (기본값: live, 30분 window)

**Step 1 — jsonl 로드 + 윈도우 필터**
- `since <ISO>`: ts >= since인 entry만
- `task <id>`: task_id == id인 entry만
- `live`: 직전 30분 (default window)

**Step 2 — 5종 신호 결정론 스캔 (LLM 호출 0)**

| 신호 | 감지 | 임계 | 가중치 |
|---|---|---|---|
| self_doubt | 정규식 사전 50 패턴 | ≥1 hit / 5min | 3 |
| retry_loop_file | 같은 file str_replace 카운터 | ≥3 / 10min | 5 |
| test_fail_repeat | bash + test exit_code != 0 | ≥2 / 5min | 5 |
| context_pressure | tokens_total / max_context | ≥0.70 | 4 |
| stall | 직전 tool_call ts 간격 | ≥90s | 2 |

부가 신호: cycle_dependency (가중치 10), token_overrun (4), time_overrun (3)

총 score ≥ 8 → blocker alert
총 score ≥ 15 → critical blocker (report 강제 트리거)

**Step 3 — Severity 점수 합산 + 랭킹**
- 각 task별 score 누적, evidence (file/cmd) 같이 저장

**Step 4 — `.track/blockers.md` 출력**

```markdown
# Blockers (scanned <ISO>)

## 🚨 T-008 — score 17 (critical)
- retry_loop_file: middleware/jwt.ts edits 5회 / 10min (weight 5)
- suggested: spawn subagent OR human review
```

**Step 5 — Rule 5 자체 점검**
- 이 스캔에서 LLM 호출 수 = ? (반드시 0)
- 0 아니면 즉시 fail + error report

---

### Mode: report

**report의 역할**: 7종 결정론 트리거 발화 시 현재 상태 강제 보고. 트리거 검출은 결정론, 자연어 렌더링만 LLM.

`sub_args` 가능 값: `live`, `trigger <name>`, `after <task-id>` (기본값: live)

**7개 결정론 트리거**

| # | 트리거 | 검출 | LLM |
|---|---|---|---|
| 1 | phase_transition | gate-checkpoint 통과 파일 write 시그널 | ❌ |
| 2 | blocker_count_threshold | blocker score ≥ 8인 블로커 ≥ 2개 | ❌ |
| 3 | context_token_pct_threshold | tokens_total / max_context ≥ 0.70 | ❌ |
| 4 | human_approval_needed | gate-checkpoint human 승인 게이트 도달 | ❌ |
| 5 | cumulative_token_overrun | 실측 token > predicted_p90 | ❌ |
| 6 | elapsed_overrun | 경과 minutes > eta_p90_minutes | ❌ |
| 7 | explicit_user_ask | "상태?", "어디까지?", "status" 정규식 | ❌ |

**Step 1 — trigger 식별 (결정론)**
- live: 직전 30분 + 7 트리거 발화 여부 점검
- trigger \<name\>: 명시된 트리거 조건 충족 여부 검증
- after \<task-id\>: 해당 task complete event 직후

**Step 2 — predicted.json 로드 + actual_log.jsonl 집계 (결정론)**
- predicted: total_tasks, total_loc_p50/p90, total_tokens_p50/p90, eta_p50/p90_minutes
- actual: completed_tasks, total_loc, tokens_total, elapsed

**Step 3 — deviation 계산 (결정론)**
```python
loc_delta_pct = (actual_loc - predicted_loc_p50) / predicted_loc_p50 * 100
velocity_actual = completed_tasks / elapsed_hours
eta_remaining_p50 = predicted_total_minutes_p50 - elapsed_minutes
```

**Step 4 — blocker-detect 결과 인용**
- `.track/blockers.md`에서 score ≥ 8인 blocker만 인용
- 없으면 `--mode detect live` 선행 실행 권유

**Step 5 — next gate 식별 (결정론)**
- 가장 가까운 다음 gate-checkpoint → arrival time 계산

**Step 6 — 자연어 보고 생성 (LLM, Rule 5 자연어 영역)**
- Step 2-5의 결정론 메트릭을 6섹션 보고 문구로 변환
- 보고 톤: 간결, 사실 위주, 30줄 이내

**보고 포맷 (필수 6 섹션)**
```
─── progress-report ─── <feature> ─── triggered by: <trigger>
Predicted scope:  X tasks · ~Y LOC · ~Z tokens · ~T hours
Actual progress:  X/Y tasks complete (P%)
Velocity:         R tasks/hour (baseline: B) +/-Δ%
ETA (p50): +X hours   ETA (p90): +Y hours
🚨 Blockers (N): ...
Next gate: <name> — <human approval required | auto>
```

**Step 7 — 출력 + 다음 보고 시점 안내**
- stdout 또는 `.track/reports/<ts>.md`
- 다음 7 트리거 중 어느 것이 다음 발화 후보인지 명시

---

## jsonl 포맷 (append-only 스키마)

```jsonl
{"ts":"2026-05-17T10:14:22Z","task":"T-001","event":"start","tokens_in":0,"source":"hook"}
{"ts":"2026-05-17T10:18:41Z","task":"T-001","event":"tool_call","tool":"str_replace","file":"middleware/jwt.ts","loc_delta":47,"exit_code":0,"source":"hook"}
{"ts":"2026-05-17T10:22:09Z","task":"T-001","event":"tool_call","tool":"bash","cmd_summary":"npm test","exit_code":1,"source":"hook"}
{"ts":"2026-05-17T10:41:55Z","task":"T-001","event":"complete","loc_actual":138,"tokens_total":11200,"minutes_elapsed":27,"source":"hook"}
```

필수 필드: `ts` (ISO8601 UTC), `event`, `source` (hook/shell)

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 모드 미명시 | --mode 없음 | probe 기본값 진입 + 안내 |
| jsonl 없음 (detect/report) | file not found | "probe install 먼저" fail loud |
| Hook silent fail (probe) | status entry 수 0 | `--mode probe install --force` 재등록 권유 |
| predicted.json 없음 | file not found | 실측만 출력 모드 (deviation N/A) |
| detect에서 LLM 호출 감지 | Step 5 자체 점검 | **즉시 fail, Rule 5 위반** |
| report Step 6에서 숫자 변경 | 결과 검토 | 즉시 fail (LLM은 표현만) |
| .track/ .gitignore 미등록 | git status 노출 | gitignore append + 사용자 알림 |

---

## Quality Gate

- [ ] 모드 파싱 결과가 안내 메시지에 명시됨
- [ ] probe: .track/ .gitignore 등록, scripts/track-probe.sh chmod+x, smoke test 1줄 통과
- [ ] detect: LLM 호출 수 = 0 (Rule 5 자체 점검), blockers.md score 내림차순 정렬
- [ ] report: 6섹션 모두 포함, 30줄 이내, trigger 명시, 다음 트리거 후보 명시
- [ ] 동시 실행 금지 규칙이 사용자에게 안내됨

---

## Examples

### Good Example
**입력:** `--mode probe install`

**기대 동작:**
1. `.track/` mkdir + `.gitignore` append
2. `scripts/track-probe.sh` 작성 + chmod+x
3. `.claude/settings.json` hooks.PostToolUse 항목 append
4. smoke test → jsonl 1줄 추가 → 통과
5. "Hook 등록 완료. `--mode probe status`로 silent fail 점검 권장" 안내

### Good Example
**입력:** `--mode detect live`

**기대 동작:**
1. 직전 30분 actual_log.jsonl 스캔
2. 5종 신호 결정론 스캔 (LLM 0)
3. score ≥ 8인 blocker → blockers.md 출력
4. LLM 호출 수 = 0 자체 확인

### Good Example
**입력:** `--mode report live`

**기대 동작:**
1. 7 트리거 발화 여부 결정론 점검
2. predicted.json + actual_log 비교
3. 6섹션 보고 (LLM 자연어 렌더링)
4. 다음 트리거 후보 명시

### Bad Example
**입력:** `--mode detect` (jsonl 없음)

**기대 동작:** "`--mode probe install` 먼저 실행하세요" fail loud

### Bad Example
**입력:** "코드 리뷰해줘"

**기대 동작:** 이 스킬은 진행 추적 전용. 코드 리뷰 요청은 라우팅 대상 아님 — 해당 스킬로 직접 호출 권유.

---

## Contextual Knowledge (auto-loaded)

### Hook Diagnostics
!`cat references/hook-diagnostics.md 2>/dev/null || echo ""`

### Blocker Pattern Dictionary
!`cat references/blocker-patterns.yaml 2>/dev/null || echo ""`

### Trigger Definitions
!`cat references/trigger-definitions.md 2>/dev/null || echo ""`

### Report Tone Guide
!`cat references/report-tone.md 2>/dev/null || echo ""`
