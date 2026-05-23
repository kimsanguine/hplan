---
name: velocity-baseline
description: "Alias for delivery-plan --step baseline — extracts personal velocity percentile from N past project records. Deprecated: use delivery-plan --step baseline directly."
argument-hint: "[--projects N]"
alias_for: "delivery-plan --step baseline"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `delivery-plan --step baseline` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: N개의 과거 프로젝트 기록을 분석해 개인 속도 백분위 기준선을 추출합니다.
기존 `velocity-baseline` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `delivery-plan --step baseline $ARGUMENTS` 와 동일하게 동작합니다.
`delivery-plan --step baseline` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
