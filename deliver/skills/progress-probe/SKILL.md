---
name: progress-probe
description: "Alias for track --mode probe — PostToolUse hook records task events to .track/actual_log.jsonl (atomic append-only). Deprecated: use track --mode probe directly."
argument-hint: "[task_id] [status]"
alias_for: "track --mode probe"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `track --mode probe` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: PostToolUse 훅 이벤트를 `.track/actual_log.jsonl`에 atomic append합니다.
쓰기 전용 오퍼레이션. detect/report 연산 없음. 동시 실행 금지 — 파일 충돌 방지.
기존 `progress-probe` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `track --mode probe $ARGUMENTS` 와 동일하게 동작합니다.
`track --mode probe` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
