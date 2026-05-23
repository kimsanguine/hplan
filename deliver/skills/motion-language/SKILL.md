---
name: motion-language
description: "Alias for ui-validate --check motion — CSS transition analysis against RESPECT.md motion language spec. Deprecated: use ui-validate --check motion directly."
argument-hint: "[--url URL]"
alias_for: "ui-validate --check motion"
allowed-tools: ["Read", "Write", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `ui-validate --check motion` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: CSS transition/animation을 RESPECT.md motion language 규칙과 비교합니다.
easing 함수·duration·delay 일관성 점검 포함.
기존 `motion-language` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `ui-validate --check motion $ARGUMENTS` 와 동일하게 동작합니다.
`ui-validate --check motion` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
