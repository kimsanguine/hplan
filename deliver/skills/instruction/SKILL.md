---
name: instruction
description: "Alias for agent-instructions --level full — complete agent spec including System Prompt, 7-element instruction set, tool list, and memory_config. Deprecated: use agent-instructions --level full directly."
argument-hint: "[--agent-name NAME]"
alias_for: "agent-instructions --level full"
allowed-tools: ["Read", "Write"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `agent-instructions --level full` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: System Prompt + 7요소 instruction set + tool list + memory_config 완전 명세를 작성합니다.
기존 `instruction` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `agent-instructions --level full $ARGUMENTS` 와 동일하게 동작합니다.
`agent-instructions --level full` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
