---
name: sprint
description: "스프린트 계획-실행-추적 통합 — 딜리버리 플랜 작성(delivery-plan)과 진척 추적(track) 통합. PRD → WBS 분해, predicted.json 초기화, probe/detect/report/checkpoint 실행. Use when planning or tracking a delivery sprint."
argument-hint: "[brief] [--step plan|init|status|retro]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

네 스텝을 단일 인터페이스로 통합한다:

| step | 책임 | LLM | 출력 |
|---|---|---|---|
| `--step plan` | PRD → WBS 분해, complexity 1-5 분류, velocity lookup → `.track/predicted.json` | ✅ WBS/분류만, 수치 예측 ❌ | predicted.json |
| `--step init` | `.track/` 생성, probe hook 등록, 추적 초기화 | ❌ 결정론 | `.track/actual_log.jsonl` + hook |
| `--step status` | jsonl 블로커 패턴 결정론 스캔 + 이벤트 트리거 현황 보고 | ✅ 자연어 렌더링만 | 진행 보고 |
| `--step retro` | 완료 후 실측 vs 예측 deviation 분석 + TK 추출 | ✅ 분류/자연어 | retro report |

> **기본값**: `--step plan` — 첫 진입은 항상 계획부터.

---

## Rule 5 준수 경계

| 작업 | LLM 사용 | 근거 |
|---|---|---|
| WBS 분해 | ✅ 분류 | 텍스트 → sub-task 분류 |
| complexity 1-5 분류 | ✅ 분류 | description 텍스트 기반 분류 허용 |
| **loc/tokens/minutes 수치 예측** | ❌ **lookup 전용** | baseline percentile 직접 인용, hallucination 방지 |
| 블로커 패턴 감지 | ❌ 결정론 | 정규식·카운터·임계치 비교 |
| 7종 트리거 검출 | ❌ 결정론 | 카운터·임계치 비교 |
| 자연어 보고 문구 생성 | ✅ | Rule 5 허용: 자연어 생성 |

---

## Trigger Gate

### Use This Skill When
- PRD 받자마자 WBS + 예측치 lock → `--step plan`
- plan 완료 후 추적 환경 세팅 → `--step init`
- "지금 어디까지 왔어?" / "블로커 있어?" → `--step status`
- 스프린트 완료 후 회고 + TK 추출 → `--step retro`
- estimate vs actual deviation 50% 초과 → `--step plan` 재실행

### Route to Other Skills When
- 비용 시뮬레이션 (lognormal) → `discover/cost-sim`
- WBS 30 task 초과 → `deliver/conductor`로 태스크 순차 실행
- UI 디자인 확인 → `deliver/ui-validate`
- 주간 운영 회고 → `operate/weekly-rollup`

### Boundary Checks
- PRD vague (Section 6 누락) → fail loud, PRD 보강 요청
- baseline 부재 → conservative fallback (모든 task complexity 5 추정치 × 1.5) + warning
- `.track/actual_log.jsonl` 부재 시 status → "init 먼저" fail loud

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--step` | `$ARGUMENTS` | plan/init/status/retro 분기 |
| target | `$ARGUMENTS` (step 이후 나머지) | PRD 경로 또는 feature 설명 |
| `profiles/<op>/velocity/baseline.jsonl` | velocity-baseline 또는 plan step | estimate lookup 기준 |
| `.track/predicted.json` | plan step 출력 | status/retro 비교 기준 |
| `.track/actual_log.jsonl` | init + probe hook | status/retro 실측 데이터 |

---

## Instructions

You are running sprint skill with arguments: **$ARGUMENTS**

### 공통 Step 0 — step 파싱

```
args = parse("$ARGUMENTS")
step = args.get("--step", "plan")   # 기본값: plan
target = args remainder after --step value
```

step 미명시 시:
> "--step 미명시 — `--step plan` 기본값으로 진입합니다. 사용 가능: `--step plan|init|status|retro`"

---

### step: plan

**plan의 역할**: PRD → WBS 분해, complexity 분류 (LLM), 수치 예측 (결정론 lookup), `.track/predicted.json` 저장.

**Step 1 — baseline 로드 + 신뢰 등급 확인**
- `profiles/<operator>/velocity/baseline.jsonl` 읽기
- C 또는 부재 → "conservative fallback 진입" warning + 진행

**Step 2 — PRD WBS 분해 (LLM 분류)**
- PRD Section 6 (Now/Next/Later) 또는 feature 설명에서 task 후보 추출
- 각 task: 1줄 description + 의존성
- 5~20 task 권장. 30 초과 시 `deliver/conductor` 라우팅 권유

**Step 3 — 각 task complexity 분류 (LLM)**
- 입력: task description
- 출력: 1/2/3/4/5 + 짧은 이유
- LLM "unsure" 또는 confidence 낮으면 +1 보수적 올림

**Step 4 — 수치 예측 결정론 lookup (LLM 호출 0)**
```python
for task in tasks:
    cx = task.complexity
    row = baseline[cx]
    task.loc_p50 = row["loc_p50"]
    task.loc_p90 = row["loc_p90"]
    task.tokens_p50 = row["tokens_p50"]
    task.tokens_p90 = row["tokens_p90"]
    task.minutes_p50 = row["minutes_p50"]
    task.minutes_p90 = row["minutes_p90"]
```
> LLM 호출 감지 시 즉시 fail — Rule 5 위반.

**Step 5 — 의존성 graph 검증 (결정론)**
- cycle detection (DFS)
- 최장 critical path 계산 (p50 minutes 합) → 프로젝트 ETA

**Step 6 — `.track/predicted.json` 저장**
```json
{
  "feature_name": "...",
  "baseline_ref": "<ISO>",
  "total_tasks": N,
  "tasks": [
    {"id": "T-001", "title": "...", "complexity": 3,
     "loc_p50": 95, "loc_p90": 240,
     "tokens_p50": 9100, "tokens_p90": 18500,
     "minutes_p50": 17, "minutes_p90": 38}
  ],
  "summary": {
    "total_loc_p50": N, "total_loc_p90": N,
    "total_tokens_p50": N, "total_tokens_p90": N,
    "eta_p50_minutes": N, "eta_p90_minutes": N,
    "critical_path": ["T-001", ...]
  }
}
```

---

### step: init

**init의 역할**: `.track/` 디렉토리 생성, append-only jsonl 추적 환경 세팅, probe hook 등록.

**Step 1 — .track/ 디렉토리 + .gitignore 등록**
- `mkdir -p .track`
- `.gitignore`에 `.track/` 없으면 append

**Step 2 — Hook 등록**
- `.claude/settings.json`의 hooks.PostToolUse에 추가:
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
- silent fail 의심 시 `--step status`로 점검

---

### step: status

**status의 역할**: 현재 진행 상황 결정론 스캔 + 이벤트 트리거 발화 여부 + 자연어 보고.

**Step 1 — 7종 트리거 결정론 점검**

| # | 트리거 | 검출 |
|---|---|---|
| 1 | phase_transition | gate-checkpoint 통과 파일 write 시그널 |
| 2 | blocker_count_threshold | score ≥ 8인 블로커 ≥ 2개 |
| 3 | context_token_pct | tokens_total / max_context ≥ 0.70 |
| 4 | human_approval_needed | gate-checkpoint human 승인 게이트 도달 |
| 5 | cumulative_token_overrun | 실측 token > predicted_p90 |
| 6 | elapsed_overrun | 경과 minutes > eta_p90_minutes |
| 7 | explicit_user_ask | "상태?", "어디까지?", "status" 정규식 |

**Step 2 — 5종 블로커 결정론 스캔 (LLM 0)**

| 신호 | 감지 | 임계 | 가중치 |
|---|---|---|---|
| self_doubt | 정규식 사전 50 패턴 | ≥1 hit / 5min | 3 |
| retry_loop_file | 같은 file str_replace 카운터 | ≥3 / 10min | 5 |
| test_fail_repeat | bash + test exit_code != 0 | ≥2 / 5min | 5 |
| context_pressure | tokens_total / max_context | ≥0.70 | 4 |
| stall | 직전 tool_call ts 간격 | ≥90s | 2 |

총 score ≥ 8 → blocker alert. ≥ 15 → critical

**Step 3 — deviation 계산 (결정론)**
```python
loc_delta_pct = (actual_loc - predicted_loc_p50) / predicted_loc_p50 * 100
velocity_actual = completed_tasks / elapsed_hours
eta_remaining_p50 = predicted_total_minutes_p50 - elapsed_minutes
```

**Step 4 — 자연어 보고 생성 (LLM, Rule 5 자연어 영역)**

보고 포맷 (필수 6 섹션):
```
─── sprint status ─── <feature> ─── triggered by: <trigger>
Predicted scope:  X tasks · ~Y LOC · ~Z tokens · ~T hours
Actual progress:  X/Y tasks complete (P%)
Velocity:         R tasks/hour (baseline: B) +/-Δ%
ETA (p50): +X hours   ETA (p90): +Y hours
🚨 Blockers (N): ...
Next gate: <name> — <human approval required | auto>
```

---

### step: retro

**retro의 역할**: 스프린트 완료 후 실측 vs 예측 deviation 분석, TK(Tacit Knowledge) 후보 추출.

**Step 1 — 완료 확인**
- `.track/actual_log.jsonl`에서 모든 task complete event 확인
- 미완료 task 있으면 "완료되지 않은 task N개" 경고 후 진행

**Step 2 — Deviation 분석 (결정론)**
```python
for task in predicted_tasks:
    actual = find_actual(task.id)
    loc_deviation = (actual.loc - task.loc_p50) / task.loc_p50 * 100
    token_deviation = (actual.tokens - task.tokens_p50) / task.tokens_p50 * 100
    time_deviation = (actual.minutes - task.minutes_p50) / task.minutes_p50 * 100
```

**Step 3 — Velocity 갱신 (결정론)**
- 이번 스프린트 실측 데이터를 baseline.jsonl에 append
- trust_grade 재계산 (A: n≥30, B: n≥10, C: n<10)

**Step 4 — TK 추출 후보 (LLM)**
- deviation이 크거나 반복되는 패턴에서 판단 패턴 추출
- 형식: "TK 후보: [상황] → [판단] 이유: [근거]"

**Step 5 — Retro 보고**
```
─── sprint retro ─── <feature>
Planned: X tasks · Y LOC · Z tokens · T hours
Actual:  X tasks · Y LOC · Z tokens · T hours
Deviations: loc +A%, tokens +B%, time +C%
Velocity trend: baseline 갱신됨 (trust_grade: X)
TK 추출 후보: N개
```

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
| --step 미명시 | 미입력 | plan 기본값 진입 + 안내 |
| baseline 없음 (plan) | file not found | conservative fallback (complexity 5 × 1.5) + warning |
| PRD vague | Section 6 누락 | fail loud, PRD 보강 요청 |
| WBS task 수 > 30 | Step 2 결과 | conductor 라우팅 권유 |
| 의존성 cycle 발견 | DFS | fail loud, cycle 표시 + 끊기 권유 |
| plan Step 4에서 LLM 호출 감지 | 자체 점검 | **즉시 fail, Rule 5 위반** |
| jsonl 없음 (status) | file not found | "init 먼저" fail loud |
| Hook silent fail | status entry 수 0 | `--step init` 재등록 권유 |

---

## Quality Gate

### plan
- [ ] WBS task 수 5~30 범위
- [ ] 모든 task complexity 1-5 분류됨
- [ ] 수치 예측 = baseline lookup 값 (LLM 호출 0)
- [ ] 의존성 graph cycle 없음
- [ ] Rule 5 자체 점검: Step 4 LLM 호출 수 = 0

### init
- [ ] .track/ .gitignore 등록
- [ ] scripts/track-probe.sh chmod+x
- [ ] smoke test 1줄 통과

### status
- [ ] 6섹션 모두 포함, 30줄 이내
- [ ] trigger 명시, 다음 트리거 후보 명시
- [ ] LLM 호출 = 0 (블로커 스캔 단계)

### retro
- [ ] 모든 task deviation 계산됨
- [ ] baseline.jsonl 갱신됨
- [ ] TK 추출 후보 명시됨

---

## Examples

### Good Example
**입력:** `--step plan "PRD: 사용자 인증 v2 — JWT middleware + OAuth callback + email verification"`

**기대 동작:**
1. baseline 로드 → WBS 8 task → complexity 분류 (LLM) → lookup (결정론) → predicted.json 저장
2. LLM 호출: WBS 1회 + complexity 8회 = 9회, 결정론 lookup = 48회

### Good Example
**입력:** `--step init`

**기대 동작:**
1. `.track/` mkdir + `.gitignore` append
2. `scripts/track-probe.sh` 작성 + chmod+x
3. `.claude/settings.json` hooks.PostToolUse 항목 append
4. smoke test → jsonl 1줄 추가 → 통과

### Good Example
**입력:** `--step status`

**기대 동작:**
1. 7 트리거 발화 여부 결정론 점검
2. 5종 블로커 스캔 (LLM 0)
3. predicted.json + actual_log 비교
4. 6섹션 보고 (LLM 자연어 렌더링)

### Bad Example
**입력:** `--step plan "JWT 만들어줘"` (PRD 아닌 한 줄)

**기대 동작:** "PRD/feature description 부족 — PRD 먼저 작성 또는 더 구체적인 feature 설명 필요" fail loud

---

## Contextual Knowledge (auto-loaded)

### Conservative Fallback Policy
!`cat references/conservative-fallback.md 2>/dev/null || echo ""`

### Blocker Pattern Dictionary
!`cat references/blocker-patterns.yaml 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
