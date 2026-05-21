---
description: "Post-completion retrospective — extract predicted-vs-actual deviation patterns from .track/actual_log.jsonl, then route to learn/pm-engine /pm-tacit-from-retro for auto-promote of qualifying patterns (deviation_pct ≥ 50% OR recurrence ≥ 3) to PM-ENGINE-MEMORY as TK candidates. Use when a feature completes (all tasks event=complete) and you want to close the data flywheel — turning execution data into reusable PM tacit knowledge."
argument-hint: "[feature-name or path/to/predicted.json]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /track-retro — Predicted vs Actual Retrospective

Closes the track data flywheel: actual deviations → TK candidates → next baseline.

## Instructions

You are running retro for: **$ARGUMENTS**

### Step 1 — predicted vs actual 결정론 비교

로드:
- `.track/predicted.json` (estimate-tasks lock)
- `.track/actual_log.jsonl` (progress-probe accumulated)

계산 (결정론):
- 각 task 의 actual_loc / actual_tokens / actual_minutes
- deviation_pct = (actual - predicted_p50) / predicted_p50 * 100
- recurrence: 같은 blocker_pattern 의 발생 횟수 (across multiple tasks)

### Step 2 — auto-promote 후보 필터링

결정론 기준 (LLM 호출 0):
- deviation_pct ≥ 50%
- OR recurrence_count ≥ 3

후보 산출 → `.track/retro-deviation.jsonl` 작성.

### Step 3 — learn/pm-engine /pm-tacit-from-retro 라우팅

`learn/pm-engine` 의 retro-extract 트리거 호출 (Phase 2 에서 추가된 라우터):
- jsonl 로드
- TK-NNN 시드 구조로 자동 변환 (패턴 한 줄 요약만 LLM 분류)
- 사용자에게 promote 후보 검토 한 번에 요청 (pending_inputs 묶음)
- 승인된 TK만 PM-ENGINE-MEMORY.md append

### Step 4 — velocity-baseline 갱신 권유

이번 feature 의 (loc/tokens/minutes) 실측을 다음 baseline 에 포함시키려면:
- `velocity-baseline last 5` 재실행 권유 (rolling baseline 갱신)

### Step 5 — 최종 보고

- promote 후보 수 / 승인 수
- 다음 baseline 갱신 권유 여부
- 데이터 flywheel 완결: 실측 → TK → 다음 예측 정확도 ↑

## Output Format

```
VERDICT: PROMOTED / NO_CANDIDATES / FAILED

Deviation:     <N tasks scanned · X 후보 식별>
Auto-promote:  <Y 후보 (deviation ≥ 50% OR recurrence ≥ 3)>
TK approved:   <Z TK PM-ENGINE-MEMORY append>
Next:          <velocity-baseline 갱신 권유 또는 다음 feature>
```

## Failure Handling

| 실패 | 대응 |
|---|---|
| feature 미완료 (event=complete 수 < total_tasks) | "완료 후 재시도" fail loud |
| deviation_pct 모두 < 50% AND recurrence < 3 | "promote 후보 0건 — feature 가 예측 안에 잘 들어옴" 보고만 |
| pm-engine 호출 실패 (TK 추출 안 됨) | 수동 promote 안내 (deviation jsonl 인용) |
