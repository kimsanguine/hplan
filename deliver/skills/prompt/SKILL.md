---
name: prompt
description: "Alias for agent-instructions --level draft — PM-perspective prompt design using CRISP framework (Context, Role, Intent, Scope, Probe). Deprecated: use agent-instructions --level draft directly."
argument-hint: "[--goal GOAL]"
alias_for: "agent-instructions --level draft"
allowed-tools: ["Read", "Write"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `agent-instructions --level draft` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: PM 관점 CRISP 프레임워크로 프롬프트 초안을 설계합니다.
Context·Role·Intent·Scope·Probe 5요소 + 7가지 실패 패턴 점검 포함.
기존 `prompt` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `agent-instructions --level draft $ARGUMENTS` 와 동일하게 동작합니다.
`agent-instructions --level draft` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
