---
name: weekly-rollup
description: "Alias for portfolio-report --view rollup — weekly portfolio aggregation with tier averages, top movers, and anomaly detection. Deprecated: use portfolio-report --view rollup directly."
argument-hint: "[--week YYYY-WNN]"
alias_for: "portfolio-report --view rollup"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

> ⚠️ **Deprecated alias** — 이 스킬은 `portfolio-report --view rollup` 로 통합되었습니다.
> 신규 스킬을 직접 사용하면 동일한 결과를 얻습니다.

**동작**: 주간 포트폴리오 집계 보고서를 생성합니다.
T1~T5 티어 평균·상위 이동자·이상치 감지 포함.
기존 `weekly-rollup` 와 완전히 동일한 결과를 반환합니다.

## 실행

이 스킬은 `portfolio-report --view rollup $ARGUMENTS` 와 동일하게 동작합니다.
`portfolio-report --view rollup` 스킬의 전체 워크플로우를 수행하세요.

$ARGUMENTS
