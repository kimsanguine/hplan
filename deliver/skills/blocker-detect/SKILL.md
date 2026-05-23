---
name: blocker-detect
description: "Alias for track --mode detect — scans .track/actual_log.jsonl for blocker patterns and surfaces risks. Deprecated: use track --mode detect directly."
argument-hint: "[--threshold N]"
alias_for: "track --mode detect"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `track --mode detect` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: `.track/actual_log.jsonl`을 스캔하여 블로커 패턴을 감지합니다.
Read-only 오퍼레이션. 파일 쓰기 없음. probe 실행 이후에 순차 호출하세요.
기존 `blocker-detect` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `track --mode detect $ARGUMENTS` 와 동일하게 동작합니다.
`track --mode detect` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
