---
name: kpi
description: "Alias for metrics-design --step kpi — defines and tracks AI agent KPI set derived from the North Star metric. Deprecated: use metrics-design --step kpi directly."
argument-hint: "[--north-star METRIC]"
alias_for: "metrics-design --step kpi"
allowed-tools: ["Read", "Write"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `metrics-design --step kpi` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: North Star 메트릭에서 파생된 AI 에이전트 KPI 세트를 정의합니다.
응답 정확도·처리 속도·비용 효율·사용자 만족 기준 포함.
기존 `kpi` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `metrics-design --step kpi $ARGUMENTS` 와 동일하게 동작합니다.
`metrics-design --step kpi` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
