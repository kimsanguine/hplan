---
description: "hplan/cogs-sentinel 스킬 wrapper — lognormal sampler로 p50/p90 월간 마진 계산 + free-user abuse blend + GREEN/CONDITIONAL_GO/RED 결정"
argument-hint: "--provider <name> --model <id> --tokens-in <N> --calls <N> --arpu <USD>"
allowed-tools: ["Read", "Write", "Bash"]
---

# /cogs-sentinel — COGS p50/p90 결정론 게이트

Running for: **$ARGUMENTS**

이 커맨드는 `hplan/cogs-sentinel` 스킬을 즉시 호출합니다.

## 호출 흐름

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
