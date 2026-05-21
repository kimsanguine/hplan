---
name: progress-probe
description: "Append every Claude Code tool call to .track/actual_log.jsonl via PostToolUse Hook (primary) and a fallback shell script (defensive — Hook may silently fail per claude-code issue #17688). Captures (timestamp, task_id, tool, file, loc_delta, exit_code, tokens) per cycle so blocker-detect and progress-report can run deterministic analysis without LLM. Use right after estimate-tasks locks .track/predicted.json — the probe writes the actual log that predicted is measured against."
argument-hint: "[install | status | replay <session-id>]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- 매 prompt-cycle 의 (timestamp, task_id, tool, file, loc_delta, exit_code, tokens) 를 append-only jsonl 에 기록
- Hook 등록 (primary path) + shell fallback (defensive path) 이중 메커니즘
- LLM 호출 0 — 모든 데이터 수집이 결정론 (Rule 5 준수)
- 출력은 분석용 raw 데이터만. 해석은 blocker-detect / progress-report 가 담당

---

## 이중 메커니즘 (Hook 위험 대응)

[[claude-code issue #17688]] — PreToolUse / PostToolUse Hook 이 silent fail 가능. 단일 메커니즘에 의존하면 데이터 누락이 침묵 사고로 이어짐.

| 경로 | 트리거 | 장점 | 단점 |
|---|---|---|---|
| **Primary — Hook** | Claude Code 자동 | 자동, 누락 0 (정상 시) | issue #17688 silent fail 가능 |
| **Fallback — shell** | 사용자가 `track-probe.sh tool ...` 수동 호출 또는 cron | Hook 안 돌아도 작동 | 수동 / 주기적 호출 필요 |

> 두 경로 모두 같은 jsonl 포맷 → blocker-detect 가 출처 구분 없이 처리.
> Hook 작동 점검은 `/track-probe-status` 가 마지막 N 분의 Hook entry 수를 출력.

---

## jsonl 포맷 (append-only 스키마)

```jsonl
{"ts":"2026-05-17T10:14:22Z","task":"T-001","event":"start","tokens_in":0,"source":"hook"}
{"ts":"2026-05-17T10:18:41Z","task":"T-001","event":"tool_call","tool":"str_replace","file":"middleware/jwt.ts","loc_delta":47,"exit_code":0,"source":"hook"}
{"ts":"2026-05-17T10:22:09Z","task":"T-001","event":"tool_call","tool":"bash","cmd_summary":"npm test","exit_code":1,"source":"hook"}
{"ts":"2026-05-17T10:41:55Z","task":"T-001","event":"complete","loc_actual":138,"tokens_total":11200,"minutes_elapsed":27,"source":"hook"}
{"ts":"2026-05-17T10:42:10Z","task":"T-001","event":"fallback_audit","reason":"hook_gap","source":"shell"}
```

필수 필드: `ts` (ISO8601 UTC), `event` (start/tool_call/complete/blocker_candidate/fallback_audit), `source` (hook/shell)
조건부 필드: task_id (active session 있을 때), file (tool 이 str_replace/write 일 때), loc_delta (변경 LOC), exit_code (bash tool), tokens_total (complete event)

---

## Trigger Gate

### Use This Skill When
- estimate-tasks 가 `.track/predicted.json` lock 직후 — actual_log 시작
- 기존 세션 Hook 가 깨졌을 때 (`/track-probe install --force`)
- 종료 후 누락 점검 (`/track-probe replay <session-id>`)

### Route to Other Skills When
- jsonl 의 패턴 분석 → `track/blocker-detect`
- jsonl + predicted.json 의 burn-up 시각화 → `track/progress-report`
- Hook 자체가 자주 silent fail → 사용자 환경 진단 (claude-code 버전, OS 권한)

### Boundary Checks
- jsonl 파일이 .gitignore 의 `.track/` 패턴에 포함됐는가 (개인 데이터)
- predicted.json 의 task id 와 actual_log 의 task id 가 매칭 가능한가
- fallback shell 이 PATH 에 있고 실행 권한 있는가 (`chmod +x`)

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| Claude Code Hook 콜백 | PostToolUse Hook | 자동 jsonl append |
| shell 수동 호출 | `scripts/track-probe.sh tool <name> --file <path> --exit <code>` | shell jsonl append |
| session-id (replay 모드) | `~/.claude/projects/<encoded>/<session>.jsonl` | jsonl 파싱 → append |

---

## Instructions

You are operating progress-probe in mode: **$ARGUMENTS** (install | status | replay)

### Mode: install

**Step 1 — .track/ 디렉터리 + .gitignore 등록**
- `mkdir -p .track`
- `.gitignore` 에 `.track/` 없으면 append

**Step 2 — Hook 등록**
- `.claude/settings.json` 의 hooks 필드에 PostToolUse 항목 추가:
```json
{"hooks": {"PostToolUse": [{"command": "scripts/track-probe.sh hook --tool $TOOL --file $FILE --exit $EXIT"}]}}
```
- 기존 hooks 가 있으면 array append (덮어쓰기 금지)

**Step 3 — fallback shell 작성**
- `scripts/track-probe.sh` 신규 (없으면)
- chmod +x
- 내용: argparse 같은 shell parser + ISO8601 timestamp + JSON line write

**Step 4 — Hook smoke test**
- `bash scripts/track-probe.sh hook --tool test --file noop --exit 0`
- jsonl 마지막 줄에 test entry 확인 → pass

**Step 5 — 사용자 안내**
- Hook 가 PostToolUse 에 등록됐음
- silent fail 의심 시 `/track-probe status` 로 점검
- jsonl 위치: `.track/actual_log.jsonl`

### Mode: status

**Step 1 — Hook 활성 점검**
- 직전 5 분의 actual_log.jsonl entry 수
- `source: "hook"` vs `source: "shell"` 비율
- Hook 비율 < 80% 또는 entry 0 → warning

**Step 2 — 보고**
- 지난 1h / 24h jsonl entry 수
- Hook silent fail 의심 여부
- predicted.json lock 이후 경과 시간

### Mode: replay <session-id>

**Step 1 — Claude Code session jsonl 로드**
- `~/.claude/projects/<encoded>/<session-id>.jsonl`

**Step 2 — tool_use entry 만 필터**
- type=tool_use 인 entry 만

**Step 3 — actual_log.jsonl 에 누락 분 append**
- 기존 actual_log 의 ts 와 비교, 빠진 것만 추가
- source: "shell" 로 표기

**Step 4 — 보고**
- 추가된 entry 수, 가장 오래된/최근 ts

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| Hook 등록했는데 jsonl 0줄 (silent fail) | `/track-probe status` 결과 entry 수 0 | `/track-probe install --force` 로 재등록 + shell fallback 으로 임시 대응 |
| .claude/settings.json 손상 | JSON 파싱 실패 | 백업 (settings.json.bak) 복원 권유 — 자동 덮어쓰기 금지 |
| .track/ 가 .gitignore 에 없음 | git status 에 .track 노출 | `.gitignore` append + 사용자 알림 |
| jsonl 파일 크기 > 100MB | append 전 size check | `.track/archive/<date>.jsonl` 로 rotate |
| Hook 와 shell 양쪽에서 같은 event 중복 기록 | ts ±100ms 같은 tool_call 2건 | dedup 시 hook source 우선 |

---

## Quality Gate

- [ ] .track/ 가 .gitignore 에 등록됨
- [ ] scripts/track-probe.sh 가 chmod +x
- [ ] .claude/settings.json 의 hooks.PostToolUse 에 track-probe 등록
- [ ] jsonl smoke test entry 1줄 확인
- [ ] LLM 호출 0 (Hook callback / shell script / replay 모두 결정론)
- [ ] 사용자에게 "Hook silent fail 시 `/track-probe status` 호출" 안내됨

---

## Examples

### Good Example
**입력:** "install"

**기대 동작:**
1. `.track/` mkdir + `.gitignore` append (`.track/`)
2. `scripts/track-probe.sh` 작성 + chmod +x
3. `.claude/settings.json` 의 hooks.PostToolUse 에 track-probe 명령 append
4. smoke test: shell 호출 → jsonl 1줄 추가 → 통과
5. "✅ Hook 등록 완료. 1시간 후 `/track-probe status` 로 silent fail 점검 권장" 안내

### Bad Example
**입력:** "그냥 install"

**왜 나쁜가:**
- 모드 명시 없음 (install | status | replay 중 어느 것인지 모호)
- predicted.json 없이 install → task_id 매칭 불가능, jsonl 의 가치 ↓

**기대 동작:** "estimate-tasks 로 predicted.json 먼저 lock 권유 후 install" fail loud

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Hook Silent Fail Diagnostics
!`cat references/hook-diagnostics.md 2>/dev/null || echo ""`

### Fallback Shell Reference
!`cat references/fallback-shell-spec.md 2>/dev/null || echo ""`
