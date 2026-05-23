---
name: progress-report
description: "Alias for track --mode report — event-triggered status report that forces a snapshot of .track/actual_log.jsonl. Deprecated: use track --mode report directly."
argument-hint: "[--format brief|full]"
alias_for: "track --mode report"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `track --mode report` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: 이벤트 트리거 시 `.track/actual_log.jsonl` 스냅샷 기반 강제 상태 보고를 생성합니다.
Read-only 오퍼레이션. detect 실행 이후에 순차 호출하세요.
기존 `progress-report` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `track --mode report $ARGUMENTS` 와 동일하게 동작합니다.
`track --mode report` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
