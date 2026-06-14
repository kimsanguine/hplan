---
name: cogs-sentinel
description: "Executable COGS gate for AI products. Runs a deterministic Python sampler (lognormal token-cost distribution) to compute p50/p90 per-paid-user monthly COGS, gross margin scenarios, and free-user abuse blend. Returns GREEN / CONDITIONAL_GO / RED before any paid AI product is greenlit. Use when promising a paid AI feature, comparing providers (Anthropic/OpenAI/Google), or when discover/cost-sim has produced a usage hypothesis and you need real numbers."
argument-hint: "[provider, model, usage params or path to JSON]"
allowed-tools: ["Read", "Write", "Bash"]
model: inherit
hooks:
  Stop:
    - type: command
      command: "python3 hplan/scripts/cogs_sentinel.py --params harness/build-gate/cogs_input.json --out harness/build-gate/cogs_report.md 2>/dev/null || true"
---

# COGS Sentinel — Executable Margin Gate

Running for: **$ARGUMENTS**

## Core Goal

- Token 단가와 사용 패턴으로부터 **p50/p90 월간 COGS와 gross margin을 계산**하여 paid AI product의 경제적 viability를 *PRD 전에* 판단한다.
- Free-user abuse 시나리오를 blend해 "유료 1명당 무료 24명을 감당해야 할 때" 마진이 살아남는지 본다.
- 결정은 **GREEN / CONDITIONAL_GO / RED** + 구체적 mitigation 권고.

## Trigger Gate

### Use This Skill When

- 사용자가 유료 가격을 책정하려 할 때 (`$X/mo`, `per-call`, etc.)
- `discover/cost-sim`이 시나리오를 도출한 후 결정론적 수치가 필요할 때
- Provider 교체(Anthropic ↔ OpenAI ↔ Google)의 영향 측정
- 무료 tier 도입 시 abuse가 마진을 깨지 않는지 사전 검증
- Build Gate 진입 *전*

### Route to Other Skills When

- 비용 시나리오 자체가 아직 명확하지 않을 때 → `discover/cost-sim` 먼저
- 배포 후 실제 추적 → `operate/ops-review`
- 가격 모델 자체를 다시 짤 때 → `architect/strategy`
- COGS RED 결정이 났을 때 → `decision-log` (hold/pivot) 기록 후 routing

### Boundary Checks

- ℹ️ `--cac`와 `--monthly-churn`을 함께 전달하면 LTV/CAC/Payback + overall_verdict(BUILD/HOLD/INVESTIGATE)를 **추가로** 산출한다. 두 인자를 생략하면 무시되어 하위호환이 유지된다. (`--mau` 추가 시 Business Report 블록 — 매출/COGS/cost_ratio/blended — 도 포함됨.)
- ℹ️ 이 skill은 sanity-check(빌드 게이트)이지 회계 보고서가 아니다 — 법인세·감가상각 등 전산 회계 항목은 다루지 않는다.
- ❌ Provider 단가는 `references/provider_pricing.json` 스냅샷 기준이다. 최신 단가는 사용자가 verify해야 함.
- ❌ lognormal sampling이라 결정론적이지만 실제 분포와 다를 수 있다 — sanity check 용도지 회계 보고서 아님.

## Inputs

CLI:

```bash
python3 hplan/scripts/cogs_sentinel.py \
  --provider anthropic --model claude-sonnet-4-6 \
  --tokens-in 3000 --tokens-out 1500 --calls-per-user-month 40 \
  --arpu 29 --paid-conversion 0.08 --free-abuse-multiplier 3
```

또는 JSON:

```json
{
  "provider": "anthropic", "model": "claude-sonnet-4-6",
  "tokens_in": 3000, "tokens_out": 1500,
  "calls_per_user_month": 40, "arpu": 29,
  "paid_conversion": 0.08, "free_abuse_multiplier": 3,
  "target_gross_margin": 0.70
}
```

## Steps

1. Confirm provider + model exists in `references/provider_pricing.json` (or pass `--pricing path`).
2. Estimate usage params from discover/cost-sim output or user input.
3. Run `python3 hplan/scripts/cogs_sentinel.py ...`.
4. Read the markdown report at `harness/build-gate/cogs_report.md`.
5. If decision is `GREEN`, proceed to `decision-log` → `handoff`.
6. If `CONDITIONAL_GO`, list mitigations and require human approval.
7. If `RED`, route to `decision-log` with decision = `pivot` or `hold`.

## Outputs

- `harness/build-gate/cogs_report.md` — readable summary
- `harness/build-gate/cogs_input.json` — preserved input
- Decision: `GREEN` / `CONDITIONAL_GO` / `RED`
- per-call cost p50/p90, monthly COGS p50/p90/worst, gross margin p50/p90/blended

## Verification

- [ ] p90 gross margin ≥ target (default 70%)
- [ ] Free-user blended margin ≥ target × 0.7
- [ ] Worst-case monthly COGS < ARPU × (1 - payment_fee_pct)
- [ ] Provider + model exists in pricing snapshot OR `--pricing` override used

## Why This Exists

`discover/cost-sim`은 LLM이 시나리오를 *생각하는* 단계 — 의미 있지만 LLM은 lognormal 분포를 머릿속에서 정확히 계산하지 못한다. cogs-sentinel은 그 시나리오를 받아 **결정론적으로 측정**한다. 둘은 paired skill이다.

Replit이 ARR $2M→$144M 동안 gross margin이 single digit으로 떨어진 사례 — 가격 4번 변경으로 회복. 그 사고를 사전에 잡는 것이 이 skill의 존재 이유다.
