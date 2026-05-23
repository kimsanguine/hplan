---
name: scorecard-5axis
description: "Alias for portfolio-report --view scorecard — 5-axis weighted rubric scoring for agent portfolio comparison. Deprecated: use portfolio-report --view scorecard directly."
argument-hint: "[--agents LIST]"
alias_for: "portfolio-report --view scorecard"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `portfolio-report --view scorecard` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: 정확도·속도·비용·신뢰도·사용자 만족 5축 가중 루브릭으로 에이전트 팀을 채점합니다.
기존 `scorecard-5axis` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `portfolio-report --view scorecard $ARGUMENTS` 와 동일하게 동작합니다.
`portfolio-report --view scorecard` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
