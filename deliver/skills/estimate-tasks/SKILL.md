---
name: estimate-tasks
description: "Alias for delivery-plan --step estimate — PRD to WBS decomposition with deterministic complexity 1-5 scoring. Deprecated: use delivery-plan --step estimate directly."
argument-hint: "[--prd PATH]"
alias_for: "delivery-plan --step estimate"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `delivery-plan --step estimate` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: PRD를 입력받아 WBS로 분해하고 태스크별 복잡도를 1-5로 평가합니다.
velocity-baseline 결과를 참조해 예상 소요 시간을 계산합니다.
기존 `estimate-tasks` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `delivery-plan --step estimate $ARGUMENTS` 와 동일하게 동작합니다.
`delivery-plan --step estimate` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
