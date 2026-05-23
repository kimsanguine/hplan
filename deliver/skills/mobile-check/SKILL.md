---
name: mobile-check
description: "Alias for ui-validate --check mobile — DESIGN.md breakpoint validation at 375/768/1440px using Playwright viewport resize. Deprecated: use ui-validate --check mobile directly."
argument-hint: "[--url URL]"
alias_for: "ui-validate --check mobile"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `ui-validate --check mobile` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: Playwright viewport 375/768/1440px에서 DESIGN.md 브레이크포인트 규칙을 검증합니다.
레이아웃 깨짐·overflow·tap-target 크기 점검 포함.
기존 `mobile-check` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `ui-validate --check mobile $ARGUMENTS` 와 동일하게 동작합니다.
`ui-validate --check mobile` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
