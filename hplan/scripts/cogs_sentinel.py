#!/usr/bin/env python3
"""COGS Sentinel — executable economic gate for hplan.

Why this exists:
- Replit went from ~$2M ARR to $144M ARR while gross margin dropped to single
  digits before pricing changes lifted it back to 20-30%. The lesson is that
  AI SaaS COGS is a build blocker, not a finance afterthought.
- competitive-landscape doc identifies COGS as hplan's signature differentiator
  vs Superpowers/GStack/Spec-Kit. Words are not enough — hplan needs to
  *calculate* the margin envelope.

This module accepts a JSON or CLI input describing provider pricing + usage
patterns and emits:
- p50 / p90 / worst-case COGS per paid user / month
- gross margin scenarios at the configured ARPU
- free-user abuse breakeven multiplier
- decision: GREEN / CONDITIONAL_GO / RED

Pricing snapshots are intentionally kept in `references/provider_pricing.json`
so they can be updated without code changes. CLI overrides win over snapshot.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import sys
from datetime import date
from pathlib import Path


# Currency guardrail: this tool is USD-only. A monthly SaaS ARPU above this
# threshold is almost never a real USD price — it is the classic "typed KRW into
# a USD field" mistake (e.g. --arpu 19000 meaning ₩19,000 ≈ $14). We surface a
# warning instead of blocking, so legitimate enterprise pricing still runs.
ARPU_USD_SANITY_CEILING = 1000.0

# An override per-MTok rate this much cheaper than the cheapest snapshot rate is
# treated as suspicious (possible fabricated price to force GREEN). Warn only.
OVERRIDE_CHEAP_RATIO = 0.1


PRICING_FALLBACK = {
    "anthropic": {
        "claude-opus-4-7": {"input_per_mtok": 15.0, "output_per_mtok": 75.0},
        "claude-sonnet-4-6": {"input_per_mtok": 3.0, "output_per_mtok": 15.0},
        "claude-haiku-4-5": {"input_per_mtok": 0.80, "output_per_mtok": 4.0},
    },
    "openai": {
        "gpt-5": {"input_per_mtok": 5.0, "output_per_mtok": 20.0},
        "gpt-5-mini": {"input_per_mtok": 0.25, "output_per_mtok": 1.5},
    },
    "google": {
        "gemini-2.5-pro": {"input_per_mtok": 1.25, "output_per_mtok": 10.0},
        "gemini-2.5-flash": {"input_per_mtok": 0.10, "output_per_mtok": 0.40},
    },
}


def load_pricing(skill_root: Path | None = None) -> dict:
    if skill_root is None:
        skill_root = Path(__file__).resolve().parent.parent
    snap = skill_root / "references" / "provider_pricing.json"
    if snap.exists():
        try:
            return json.loads(snap.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return PRICING_FALLBACK


def cost_per_call(prices: dict, tokens_in: int, tokens_out: int) -> float:
    return (tokens_in / 1_000_000) * prices["input_per_mtok"] + (
        tokens_out / 1_000_000
    ) * prices["output_per_mtok"]


def lognormal_samples(median: float, p90: float, n: int = 1000, seed: int = 7) -> list[float]:
    """Approximate per-call cost spread with a lognormal distribution.

    Median and p90 anchor the shape. We use a deterministic seed so the sentinel
    output is reproducible across runs (no `random` module needed for that).
    """
    import random

    if median <= 0:
        return [0.0] * n
    if p90 <= median:
        p90 = median * 1.5
    mu = math.log(median)
    sigma = (math.log(p90) - mu) / 1.2816  # 90th percentile z-score
    rng = random.Random(seed)
    return [math.exp(rng.gauss(mu, sigma)) for _ in range(n)]


def _validate_params(params: dict) -> None:
    """Fail loud on inputs that would produce nonsense COGS decisions.

    Any invalid param raises SystemExit with a clear message — consistent with
    the existing 'unknown provider/model' error pattern. The gate must refuse
    to emit GREEN/CONDITIONAL_GO/RED for corrupted or nonsensical inputs.
    """
    errors: list[str] = []

    tokens_in = int(params.get("tokens_in", 4000))
    tokens_out = int(params.get("tokens_out", 1000))
    calls = float(params.get("calls_per_user_month", 60))
    arpu = float(params.get("arpu", 19))
    paid_conversion = float(params.get("paid_conversion", 0.05))
    payment_fee_pct = float(params.get("payment_fee_pct", 0.03))
    free_abuse_mult = float(params.get("free_abuse_multiplier", 5))
    target_margin = float(params.get("target_gross_margin", 0.70))

    if tokens_in < 0:
        errors.append(f"tokens_in={tokens_in} must be >= 0")
    if tokens_out < 0:
        errors.append(f"tokens_out={tokens_out} must be >= 0")
    if tokens_in == 0 and tokens_out == 0:
        errors.append("tokens_in and tokens_out are both 0 — no meaningful COGS calculation possible")
    if calls <= 0:
        errors.append(f"calls_per_user_month={calls} must be > 0")
    if arpu <= 0:
        errors.append(f"arpu={arpu} must be > 0")
    if not (0 < paid_conversion <= 1):
        errors.append(f"paid_conversion={paid_conversion} must be in (0, 1]")
    if not (0 <= payment_fee_pct < 1):
        errors.append(f"payment_fee_pct={payment_fee_pct} must be in [0, 1)")
    if free_abuse_mult < 1:
        errors.append(f"free_abuse_multiplier={free_abuse_mult} must be >= 1")
    if not (0 < target_margin <= 1):
        errors.append(f"target_gross_margin={target_margin} must be in (0, 1]")

    # v2 optional inputs — validated only when supplied (absent → legacy unchanged).
    if params.get("arppu") is not None:
        arppu = float(params["arppu"])
        if arppu <= 0:
            errors.append(f"arppu={arppu} must be > 0")
    if params.get("cac") is not None:
        cac = float(params["cac"])
        if cac <= 0:
            errors.append(f"cac={cac} must be > 0")
    if params.get("monthly_churn") is not None:
        monthly_churn = float(params["monthly_churn"])
        if not (0 < monthly_churn <= 1):
            errors.append(f"monthly_churn={monthly_churn} must be in (0, 1]")
    if params.get("mau") is not None:
        mau = float(params["mau"])
        if mau <= 0:
            errors.append(f"mau={mau} must be > 0")
    if params.get("free_usage_ratio") is not None:
        free_usage_ratio = float(params["free_usage_ratio"])
        if free_usage_ratio < 0:
            errors.append(f"free_usage_ratio={free_usage_ratio} must be >= 0")

    if errors:
        msg = (
            "COGS Sentinel: invalid parameters — refusing to produce economic verdict:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
        raise SystemExit(msg)


def _warn_currency(arpu: float) -> None:
    """Surface (not block) a likely USD/KRW unit mix-up.

    The sentinel is USD-only with no FX conversion. A user typing --arpu 19000
    meaning ₩19,000/month would otherwise read as $19,000/month and emit a false
    GREEN at ~100% margin. We cannot know intent, so we warn loudly on stderr and
    let the run continue.
    """
    if arpu > ARPU_USD_SANITY_CEILING:
        suggested = arpu / 1350.0  # rough KRW→USD, illustrative only
        print(
            f"⚠️  통화 단위 확인 — 본 도구는 USD 기준이며 환율 변환을 하지 않습니다.\n"
            f"    입력한 arpu={arpu:g}이(가) 월 구독가로는 비정상적으로 큽니다.\n"
            f"    원화(예: ₩{arpu:,.0f})를 그대로 넣은 것이라면 USD로 환산해 "
            f"입력하세요 (대략 ${suggested:,.0f}).\n"
            f"    (예: ₩19,000/월 → --arpu 14)",
            file=sys.stderr,
        )


def _audit_pricing_override(params: dict, prices: dict) -> str:
    """Flag and audit a user-supplied pricing override.

    The `pricing` key in --params replaces the provider snapshot wholesale, so a
    fabricated low rate could manufacture a GREEN verdict. Override is a
    documented feature (TC-005, SKILL.md), so we do NOT remove it — instead we
    return an audit tag and warn on stderr when the override is in play, plus a
    sharper warning when the rate is implausibly cheap vs the snapshot floor.

    Returns "user_override" or "snapshot".
    """
    if not params.get("pricing"):
        return "snapshot"

    print(
        "⚠️  pricing override 사용 중 — provider 스냅샷 대신 사용자 지정 단가로 "
        "계산합니다. 결과의 pricing_source=user_override로 감사됩니다.",
        file=sys.stderr,
    )

    # Compare the override rate against the cheapest rate in the snapshot/fallback.
    snapshot = load_pricing()
    snapshot_rates: list[float] = []
    for provider_models in snapshot.values():
        if not isinstance(provider_models, dict):
            continue  # skip _meta and other non-model keys
        for model_prices in provider_models.values():
            if isinstance(model_prices, dict):
                for key in ("input_per_mtok", "output_per_mtok"):
                    if isinstance(model_prices.get(key), (int, float)):
                        snapshot_rates.append(float(model_prices[key]))

    override_rates = [
        float(prices[k])
        for k in ("input_per_mtok", "output_per_mtok")
        if isinstance(prices.get(k), (int, float))
    ]
    if snapshot_rates and override_rates:
        floor = min(r for r in snapshot_rates if r > 0)
        cheapest_override = min(override_rates)
        if cheapest_override < floor * OVERRIDE_CHEAP_RATIO:
            print(
                f"⚠️  override 단가 ${cheapest_override:g}/MTok가 스냅샷 최저가 "
                f"${floor:g}/MTok의 {OVERRIDE_CHEAP_RATIO:.0%} 미만입니다 — "
                f"단가 위조로 인한 거짓 GREEN 가능성을 검토하세요.",
                file=sys.stderr,
            )

    return "user_override"


def run_realtime(params: dict, baseline_path: Path | None = None) -> dict:
    """Compare actual operational data against the Build Gate prediction.

    Reads the previous cogs_input.json (or baseline_path) for the predicted
    calls_per_user_month/tokens_in/tokens_out and replaces them with actuals
    before re-running the model, then appends a delta block.
    """
    if baseline_path is None:
        baseline_path = Path("harness/build-gate/cogs_input.json")

    predicted_params: dict = {}
    if baseline_path.exists():
        try:
            predicted_params = json.loads(baseline_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass

    merged = {**predicted_params, **params}
    merged.pop("mode", None)

    predicted_calls = float(predicted_params.get("calls_per_user_month", merged.get("calls_per_user_month", 60)))
    actual_calls = float(params.get("actual_calls_per_user_month", merged.get("calls_per_user_month", predicted_calls)))
    merged["calls_per_user_month"] = actual_calls

    if "actual_tokens_in" in params:
        merged["tokens_in"] = int(params["actual_tokens_in"])
    if "actual_tokens_out" in params:
        merged["tokens_out"] = int(params["actual_tokens_out"])

    result = run(merged)

    predicted_merged = {**merged, "calls_per_user_month": predicted_calls}
    if "actual_tokens_in" in params:
        predicted_merged["tokens_in"] = int(predicted_params.get("tokens_in", merged["tokens_in"]))
    if "actual_tokens_out" in params:
        predicted_merged["tokens_out"] = int(predicted_params.get("tokens_out", merged["tokens_out"]))
    predicted_result = run(predicted_merged)

    delta_p90 = result["gross_margin"]["p90"] - predicted_result["gross_margin"]["p90"]
    result["mode"] = "realtime"
    result["realtime"] = {
        "actual_calls_per_user_month": actual_calls,
        "predicted_calls_per_user_month": predicted_calls,
        "predicted_margin_p90": round(predicted_result["gross_margin"]["p90"], 4),
        "actual_margin_p90": round(result["gross_margin"]["p90"], 4),
        "delta_pp": round(delta_p90 * 100, 1),
        "threshold_exceeded": abs(delta_p90) >= 0.15,
    }
    if result["realtime"]["threshold_exceeded"]:
        sign = "+" if delta_p90 >= 0 else ""
        result["reasons"].insert(0,
            f"[realtime] p90 margin delta {sign}{delta_p90*100:.1f}pp vs Build Gate prediction — PMF Gate threshold ±15pp exceeded.")
    return result


def run(params: dict) -> dict:
    _validate_params(params)
    pricing = params.get("pricing") or load_pricing()
    provider = params.get("provider", "anthropic")
    model = params.get("model", "claude-sonnet-4-6")
    try:
        prices = pricing[provider][model]
    except KeyError:
        raise SystemExit(f"unknown provider/model: {provider}/{model}")

    pricing_source = _audit_pricing_override(params, prices)

    tokens_in = int(params.get("tokens_in", 4000))
    tokens_out = int(params.get("tokens_out", 1000))
    calls_per_user_month = float(params.get("calls_per_user_month", 60))
    arpu = float(params.get("arpu", 19))
    _warn_currency(arpu)
    paid_conversion = float(params.get("paid_conversion", 0.05))
    free_abuse_multiplier = float(params.get("free_abuse_multiplier", 5))
    target_margin = float(params.get("target_gross_margin", 0.70))
    payment_fee_pct = float(params.get("payment_fee_pct", 0.03))

    median_call = cost_per_call(prices, tokens_in, tokens_out)
    p90_call = median_call * 2.2  # realistic variance for token-heavy calls
    samples = lognormal_samples(median_call, p90_call)
    samples.sort()

    def pct(values, p):
        idx = max(0, min(len(values) - 1, int(p * len(values))))
        return values[idx]

    cogs_p50 = pct(samples, 0.5) * calls_per_user_month
    cogs_p90 = pct(samples, 0.9) * calls_per_user_month
    cogs_worst = pct(samples, 0.99) * calls_per_user_month

    net_revenue = arpu * (1 - payment_fee_pct)
    margin_p50 = (net_revenue - cogs_p50) / net_revenue if net_revenue else -1
    margin_p90 = (net_revenue - cogs_p90) / net_revenue if net_revenue else -1

    free_user_cost = median_call * calls_per_user_month * free_abuse_multiplier
    free_load_per_paid = (1 - paid_conversion) / paid_conversion if paid_conversion > 0 else 999
    blended_cogs = cogs_p50 + free_user_cost * free_load_per_paid * 0.3  # 30% of free users active
    blended_margin = (net_revenue - blended_cogs) / net_revenue if net_revenue else -1

    if margin_p90 >= target_margin and blended_margin >= target_margin * 0.7:
        decision = "GREEN"
    elif margin_p50 >= target_margin * 0.6:
        decision = "CONDITIONAL_GO"
    else:
        decision = "RED"

    reasons = []
    if margin_p90 < target_margin:
        reasons.append(
            f"p90 gross margin {margin_p90:.0%} below target {target_margin:.0%} — tighten usage caps or downgrade model."
        )
    if blended_margin < target_margin * 0.7:
        reasons.append(
            f"free-user blended margin {blended_margin:.0%} too low — abuse cap or paywall first call."
        )
    if not reasons:
        reasons.append("All scenarios within target margin.")

    # --- v2 additive (backward-compatible): ARPPU/ARPU, count-based blended,
    #     unit economics (LTV/CAC/Payback), report totals. All optional inputs;
    #     when absent the legacy fields above are unchanged. ---
    arppu = float(params.get("arppu", arpu))           # paid-user revenue (alias of arpu)
    net_arppu = arppu * (1 - payment_fee_pct)
    arpu_all_users = arppu * paid_conversion           # revenue per ALL users (incl. free)
    free_usage_ratio = float(params.get("free_usage_ratio", 0.3))
    free_cogs_per_user = median_call * calls_per_user_month * free_usage_ratio * free_abuse_multiplier

    report_block = None
    mau = params.get("mau")
    if mau is not None:
        mau = float(mau)
        paid_users = round(mau * paid_conversion)
        free_users = max(0.0, mau - paid_users)
        gross_revenue = paid_users * arppu
        total_net_revenue = paid_users * net_arppu
        total_cogs = paid_users * cogs_p50 + free_users * free_cogs_per_user
        blended_margin_by_count = (total_net_revenue - total_cogs) / total_net_revenue if total_net_revenue else -1
        cost_ratio = (total_cogs / gross_revenue) if gross_revenue else -1
        report_block = {
            "mau": mau,
            "paid_users": paid_users,
            "free_users": free_users,
            "arppu_usd": round(arppu, 4),
            "arpu_all_users_usd": round(arpu_all_users, 6),
            "gross_revenue_usd": round(gross_revenue, 2),
            "net_revenue_usd": round(total_net_revenue, 2),
            "total_cogs_usd": round(total_cogs, 2),
            "gross_profit_usd": round(gross_revenue - total_cogs, 2),
            "blended_margin_by_count": round(blended_margin_by_count, 4),
            "cost_ratio": round(cost_ratio, 4),
        }

    unit_economics = None
    cac = params.get("cac")
    monthly_churn = params.get("monthly_churn")
    if cac is not None and monthly_churn is not None:
        cac = float(cac); monthly_churn = float(monthly_churn)
        lifetime = (1.0 / monthly_churn) if monthly_churn > 0 else 0.0
        # Monthly net contribution = net revenue per paid user − COGS. Use net_arppu
        # (payment-fee adjusted) so LTV/payback are fee-consistent. Computed directly
        # rather than as net_arppu*margin_p90 because margin_p90 is anchored on arpu,
        # not arppu, so the product would mix revenue bases when arppu != arpu.
        monthly_net_contribution = net_arppu - cogs_p90
        ltv = monthly_net_contribution * lifetime
        ltv_cac = (ltv / cac) if cac > 0 else 0.0
        payback = (cac / monthly_net_contribution) if monthly_net_contribution > 0 else float("inf")
        unit_economics = {
            "cac_usd": round(cac, 2),
            "monthly_churn": round(monthly_churn, 4),
            "avg_lifetime_months": round(lifetime, 2),
            "ltv_usd": round(ltv, 2),
            "ltv_cac": round(ltv_cac, 2),
            "payback_months": (round(payback, 2) if payback != float("inf") else None),
            "ltv_cac_verdict": "PASS" if ltv_cac >= 3 else ("WATCH" if ltv_cac >= 1 else "FAIL"),
        }

    overall_verdict = None
    if unit_economics is not None:
        _pb = unit_economics["payback_months"]
        company_in_deficit = report_block is not None and (
            report_block["gross_profit_usd"] < 0 or report_block["blended_margin_by_count"] < 0
        )
        if company_in_deficit:
            # Paid-unit economics may look fine, but a company-wide loss overrides
            # any BUILD/INVESTIGATE — hold until the blended picture turns positive.
            overall_verdict = "HOLD"
        elif decision == "GREEN" and unit_economics["ltv_cac"] >= 3 and (_pb is not None and _pb <= 12):
            overall_verdict = "BUILD"
        elif decision == "RED" or unit_economics["ltv_cac"] < 1:
            overall_verdict = "HOLD"
        else:
            overall_verdict = "INVESTIGATE"

    return {
        "generated": date.today().isoformat(),
        "provider": provider,
        "model": model,
        "pricing_source": pricing_source,
        "inputs": {
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "calls_per_user_month": calls_per_user_month,
            "arpu": arpu,
            "paid_conversion": paid_conversion,
            "free_abuse_multiplier": free_abuse_multiplier,
            "target_gross_margin": target_margin,
        },
        "per_call_cost_usd": {
            "p50": round(median_call, 6),
            "p90": round(p90_call, 6),
        },
        "monthly_cogs_per_paid_user_usd": {
            "p50": round(cogs_p50, 4),
            "p90": round(cogs_p90, 4),
            "worst": round(cogs_worst, 4),
        },
        "gross_margin": {
            "p50": round(margin_p50, 4),
            "p90": round(margin_p90, 4),
            "with_free_user_load": round(blended_margin, 4),
        },
        "decision": decision,
        "reasons": reasons,
        "arppu_arpu": {
            "arppu_usd": round(arppu, 4),
            "arpu_all_users_usd": round(arpu_all_users, 6),
            "paid_conversion": paid_conversion,
        },
        "report": report_block,
        "unit_economics": unit_economics,
        "overall_verdict": overall_verdict,
    }


def markdown_report(result: dict) -> str:
    mode = result.get("mode", "predict")
    lines = [
        f"# COGS Sentinel Report",
        "",
        f"Generated: {result['generated']}",
        f"Mode: {mode}",
        f"Provider: {result['provider']} / {result['model']}",
        f"Pricing source: {result.get('pricing_source', 'snapshot')}",
        "",
        "## Decision",
        f"**{result['decision']}**",
        "",
        *[f"- {r}" for r in result["reasons"]],
        "",
        "## Per-Call Cost (USD)",
        f"- p50: ${result['per_call_cost_usd']['p50']}",
        f"- p90: ${result['per_call_cost_usd']['p90']}",
        "",
        "## Monthly COGS per Paid User (USD)",
        f"- p50: ${result['monthly_cogs_per_paid_user_usd']['p50']}",
        f"- p90: ${result['monthly_cogs_per_paid_user_usd']['p90']}",
        f"- worst: ${result['monthly_cogs_per_paid_user_usd']['worst']}",
        "",
        "## Gross Margin",
        f"- p50: {result['gross_margin']['p50']:.0%}",
        f"- p90: {result['gross_margin']['p90']:.0%}",
        f"- with free-user load: {result['gross_margin']['with_free_user_load']:.0%}",
        "",
        "## Inputs",
        *[f"- {k}: {v}" for k, v in result["inputs"].items()],
    ]
    if result.get("report"):
        rp = result["report"]
        lines += [
            "",
            "## Business Report (전체 기준)",
            f"- MAU: {rp['mau']:,.0f}  (paid {rp['paid_users']:,.0f} / free {rp['free_users']:,.0f})",
            f"- ARPPU: ${rp['arppu_usd']}  ·  ARPU(all users): ${rp['arpu_all_users_usd']}",
            f"- Gross revenue: ${rp['gross_revenue_usd']:,.2f}  ·  Total COGS: ${rp['total_cogs_usd']:,.2f}",
            f"- Gross profit: ${rp['gross_profit_usd']:,.2f}  ·  Cost ratio (COGS/revenue): {rp['cost_ratio']:.1%}",
            f"- Blended margin (by user count): {rp['blended_margin_by_count']:.1%}",
        ]
    if result.get("unit_economics"):
        ue = result["unit_economics"]
        pb = ue["payback_months"]
        lines += [
            "",
            "## Unit Economics",
            f"- CAC: ${ue['cac_usd']}  ·  Monthly churn: {ue['monthly_churn']:.1%}  ·  Avg lifetime: {ue['avg_lifetime_months']} mo",
            f"- LTV: ${ue['ltv_usd']}  ·  LTV:CAC: {ue['ltv_cac']}x ({ue['ltv_cac_verdict']})  ·  Payback: {pb if pb is not None else 'n/a'} mo",
        ]
    if result.get("overall_verdict"):
        lines += ["", f"## Overall Verdict", f"**{result['overall_verdict']}**  (COGS {result['decision']} + LTV:CAC + Payback)"]

    if mode == "realtime" and "realtime" in result:
        rt = result["realtime"]
        threshold_label = "⚠️ EXCEEDED (±15pp threshold)" if rt["threshold_exceeded"] else "✅ within threshold"
        lines += [
            "",
            "## Realtime Comparison",
            f"- Actual calls/user/month: {rt['actual_calls_per_user_month']}",
            f"- Predicted calls/user/month: {rt['predicted_calls_per_user_month']}",
            f"- Predicted p90 margin: {rt['predicted_margin_p90']:.0%}",
            f"- Actual p90 margin: {rt['actual_margin_p90']:.0%}",
            f"- Delta: {rt['delta_pp']:+.1f}pp — {threshold_label}",
        ]
    return "\n".join(lines)


def parse_args():
    p = argparse.ArgumentParser(description="hplan COGS sentinel")
    p.add_argument("--mode", choices=["predict", "realtime"], default="predict",
                   help="predict: model future COGS from usage params; "
                        "realtime: compare actual operational data against Build Gate prediction")
    p.add_argument("--params", help="Path to JSON params file (overrides CLI flags)")
    p.add_argument("--provider", default="anthropic")
    p.add_argument("--model", default="claude-sonnet-4-6")
    p.add_argument("--tokens-in", type=int, default=4000)
    p.add_argument("--tokens-out", type=int, default=1000)
    p.add_argument("--calls-per-user-month", type=float, default=60)
    p.add_argument("--arpu", type=float, default=19)
    p.add_argument("--paid-conversion", type=float, default=0.05)
    p.add_argument("--free-abuse-multiplier", type=float, default=5)
    p.add_argument("--target-gross-margin", type=float, default=0.70)
    p.add_argument("--payment-fee-pct", type=float, default=0.03)
    p.add_argument("--mau", type=float, help="[report] total monthly active users (enables business report block)")
    p.add_argument("--arppu", type=float, help="paid-user revenue (alias of --arpu); ARPU(all)=ARPPU*paid_conversion")
    p.add_argument("--free-usage-ratio", type=float, help="free user's call fraction vs paid (default 0.3)")
    p.add_argument("--cac", type=float, help="[unit-econ] customer acquisition cost per paid user")
    p.add_argument("--monthly-churn", type=float, help="[unit-econ] monthly paid churn (enables LTV/CAC/Payback)")
    p.add_argument("--actual-calls-per-user-month", type=float,
                   help="[realtime mode] Measured calls/user/month from production logs")
    p.add_argument("--actual-tokens-in", type=int,
                   help="[realtime mode] Measured average input tokens per call")
    p.add_argument("--actual-tokens-out", type=int,
                   help="[realtime mode] Measured average output tokens per call")
    p.add_argument("--baseline", help="[realtime mode] Path to Build Gate cogs_input.json "
                   "(default: harness/build-gate/cogs_input.json)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--out", help="Write markdown report to path")
    return p.parse_args()


def main():
    args = parse_args()
    if args.params:
        params = json.loads(Path(args.params).read_text(encoding="utf-8"))
    else:
        params = {
            "provider": args.provider,
            "model": args.model,
            "tokens_in": args.tokens_in,
            "tokens_out": args.tokens_out,
            "calls_per_user_month": args.calls_per_user_month,
            "arpu": args.arpu,
            "paid_conversion": args.paid_conversion,
            "free_abuse_multiplier": args.free_abuse_multiplier,
            "target_gross_margin": args.target_gross_margin,
            "payment_fee_pct": args.payment_fee_pct,
        }
        for _k, _v in (("mau", args.mau), ("arppu", args.arppu),
                       ("free_usage_ratio", args.free_usage_ratio),
                       ("cac", args.cac), ("monthly_churn", args.monthly_churn)):
            if _v is not None:
                params[_k] = _v

        # LTV/Payback needs both --cac and --monthly-churn. If exactly one is given,
        # skip the calc (run() already requires both) and warn so the user knows why
        # unit economics is absent from the report.
        if (args.cac is None) != (args.monthly_churn is None):
            print("[warn] LTV/Payback 생략 — --cac 와 --monthly-churn 둘 다 필요",
                  file=sys.stderr)

    if args.mode == "realtime":
        if args.actual_calls_per_user_month is not None:
            params["actual_calls_per_user_month"] = args.actual_calls_per_user_month
        if args.actual_tokens_in is not None:
            params["actual_tokens_in"] = args.actual_tokens_in
        if args.actual_tokens_out is not None:
            params["actual_tokens_out"] = args.actual_tokens_out
        baseline = Path(args.baseline) if args.baseline else None
        result = run_realtime(params, baseline_path=baseline)
    else:
        result = run(params)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        report = markdown_report(result)
        print(report)
        if args.out:
            Path(args.out).write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
