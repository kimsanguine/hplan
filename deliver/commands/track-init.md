---
description: "Initialize track plugin for a new feature — chain velocity-baseline (load or extract) → estimate-tasks (lock predicted.json) → progress-probe install (Hook + shell fallback) → gate-checkpoint install (PreToolUse). Single entry point. Use when starting any new feature implementation that needs PM-grade visibility into actual vs predicted scope."
argument-hint: "[PRD path or feature description]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /track-init — track Plugin Bootstrap

Single entry point for setting up track on a new feature. Chains 4 setup steps. Stops early if any fails.

## Instructions

You are initializing track for: **$ARGUMENTS**

### Step 1 — velocity-baseline 확인 또는 추출

Check `profiles/<operator>/velocity/baseline.jsonl`:
- 존재 + trust_grade ≥ B → 사용
- 부재 또는 grade C → `velocity-baseline` 스킬 실행 (last 5 projects)

### Step 2 — estimate-tasks 호출

PRD/feature description 으로 `estimate-tasks` 호출:
- WBS 분해 (LLM 분류 영역)
- complexity 1-5 분류
- baseline lookup 으로 (loc/tokens/minutes) p50/p90 결정 (Rule 5 준수)
- 출력: `.track/predicted.json` (lock)

### Step 3 — progress-probe install

`progress-probe install` 호출:
- `.track/` 디렉터리 + `.gitignore` 등록
- `.claude/settings.json` 의 hooks.PostToolUse 에 track-probe.sh 추가
- `scripts/track-probe.sh` 작성 + chmod +x
- smoke test 1줄

### Step 4 — gate-checkpoint install

`gate-checkpoint install` 호출:
- `.track/current-phase.txt` = "requirements" 초기화
- PreToolUse Hook 에 gate-block.sh 등록
- 6 phase 통과 조건 yaml 로드 (default 또는 사용자 override)

### Step 5 — 최종 보고

출력:
- predicted scope summary (X tasks · Y LOC · Z tokens · T hours)
- 다음 진입 phase (requirements → design)
- Hook silent fail 의심 시 `/track-status` 권장

## Output Format

```
VERDICT: READY / NEEDS_BASELINE / FAILED

Baseline:   <trust_grade A/B/C 또는 fallback>
Predicted:  <X tasks · Y LOC · Z tokens · T hours>
Hooks:      <PostToolUse + PreToolUse 등록 상태>
Next phase: requirements → design
Next ask:   <첫 작업 안내 또는 fix 권유>
```

## Failure Handling

| 실패 | 대응 |
|---|---|
| baseline 부재 + velocity-baseline 실패 (직전 프로젝트 0) | conservative fallback 모드 + warning |
| PRD 입력 없음 | "PRD path 또는 feature 한 줄 명시" fail loud |
| Hook 등록 실패 (settings.json 손상) | 백업 복원 권유 |
