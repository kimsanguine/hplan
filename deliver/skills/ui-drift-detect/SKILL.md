---
name: ui-drift-detect
description: "Alias for ui-validate --check drift — pHash comparison across N screenshots to detect visual drift between sessions. Deprecated: use ui-validate --check drift directly."
argument-hint: "[--baseline PATH]"
alias_for: "ui-validate --check drift"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `ui-validate --check drift` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: N개 스크린샷의 pHash 비교로 시각적 drift를 감지합니다.
baseline 없으면 SKIP (FAIL 아님). 타임아웃 30초.
기존 `ui-drift-detect` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `ui-validate --check drift $ARGUMENTS` 와 동일하게 동작합니다.
`ui-validate --check drift` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
