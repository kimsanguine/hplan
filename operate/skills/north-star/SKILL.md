---
name: north-star
description: "Alias for metrics-design --step north-star — defines a single North Star metric that captures agent success in one number. Deprecated: use metrics-design --step north-star directly."
argument-hint: "[--agent-name NAME]"
alias_for: "metrics-design --step north-star"
allowed-tools: ["Read", "Write"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `metrics-design --step north-star` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: 에이전트 성공을 단일 숫자로 표현하는 North Star 메트릭을 정의합니다.
측정 공식·데이터 소스·갱신 주기·anti-gaming 조건 포함.
기존 `north-star` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `metrics-design --step north-star $ARGUMENTS` 와 동일하게 동작합니다.
`metrics-design --step north-star` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
