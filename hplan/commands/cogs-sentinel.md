---
description: "Use when AI 기능의 단가·사용량·가격으로 p50/p90 월간 마진을 결정해야 합니다. hplan/cogs-sentinel wrapper는 lognormal sampler와 free-user abuse blend로 GREEN/CONDITIONAL_GO/RED를 판정합니다."
argument-hint: "--provider <name> --model <id> --tokens-in <N> --calls <N> --arpu <USD>"
allowed-tools: ["Read", "Write", "Bash"]
---

# /cogs-sentinel — COGS p50/p90 결정론 게이트

Running for: **$ARGUMENTS**

이 커맨드는 `hplan/cogs-sentinel` 스킬을 즉시 호출합니다.

## Instructions

1. `hplan/cogs-sentinel` 스킬을 `$ARGUMENTS`로 invoke.
2. 스킬이 lognormal Monte Carlo 시뮬레이션 (provider 단가 × 예상 사용량 × free-abuse blend).
3. 결과:
   - p90 margin ≥ 70% → GREEN (build 가능)
   - p90 margin 50~70% → CONDITIONAL_GO (가격 인상 또는 모델 라우팅 필요)
   - p90 margin < 50% → RED (단가 구조 재설계 필수)

## 예시

```
/cogs-sentinel --provider anthropic --model claude-sonnet-4-6 \
               --tokens-in 3000 --calls 40 --arpu 29
```

## Output Format

`p50 margin`, `p90 margin`, free-user abuse 영향, 그리고 `GREEN` / `CONDITIONAL_GO` / `RED` 판정과 다음 조치를 반환합니다.
