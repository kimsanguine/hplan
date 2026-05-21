---
description: "Live status snapshot — chain progress-probe status (Hook health) → blocker-detect live (5종 결정론 신호) → progress-report live (6 섹션 보고). Use when asking 'where am I right now?' during active implementation, or after any of the 7 progress-report triggers fires automatically."
argument-hint: "[--since <ISO> | --task <id>]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /track-status — Live Status Pulse

Single command for live progress visibility. Chains 3 deterministic skills, returns a unified report.

## Instructions

You are reporting status: **$ARGUMENTS**

### Step 1 — progress-probe status

Hook silent fail 점검:
- 직전 5min entry 수 + source: "hook" vs "shell" 비율
- Hook 비율 < 80% → warning + `/track-probe install --force` 권유

### Step 2 — blocker-detect live (default window 30min)

5종 결정론 신호 스캔:
- self_doubt / retry_loop_file / test_fail_repeat / context_pressure / stall
- 부가: cycle_dependency / token_overrun / time_overrun
- score ≥ 8 → blocker, ≥ 15 → critical
- 출력: `.track/blockers.md`

### Step 3 — progress-report live

6 섹션 보고:
- Predicted scope vs Actual progress (LOC / tokens / hours)
- Velocity (vs baseline)
- ETA p50 / p90
- Active blockers (blocker-detect 결과 인용)
- Next gate
- Next trigger candidate

### Step 4 — 최종 출력

stdout 또는 `.track/reports/<ts>.md`.

전체 LLM 호출 수: blocker-detect 0 + progress-report 자연어 변환 1회 = **1회만**. 모든 메트릭은 결정론.

## Output Format

```
─── progress-report ─── <feature> ─── triggered by: <trigger-name>
Predicted:  X tasks · Y LOC · Z tokens · T hours
Actual:     X/Y tasks (P%) · L LOC (+Δ%) · T tokens (+Δ%) · E elapsed
Velocity:   R tasks/h (baseline B, +/-Δ%)
ETA:        +Xh (p50)  +Yh (p90)
Blockers:   <N건 score 합산 + suggested action>
Next gate:  <gate-name + arrival ts>
```

## Failure Handling

| 실패 | 대응 |
|---|---|
| .track/actual_log.jsonl 비어 있음 | `/track-init` 먼저 권유 |
| Hook silent fail | shell fallback 안내 + `/track-probe install --force` |
| trigger 모호 (live 인데 발화 없음) | "지금 보고 트리거 미발화, 사용자 명시 ask 로 진행" |
