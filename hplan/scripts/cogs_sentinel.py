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
from datetime import date
from pathlib import Path


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

    if errors:
        msg = (
            "COGS Sentinel: invalid parameters — refusing to produce economic verdict:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )
        raise SystemExit(msg)


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

    tokens_in = int(params.get("tokens_in", 4000))
    tokens_out = int(params.get("tokens_out", 1000))
    calls_per_user_month = float(params.get("calls_per_user_month", 60))
    arpu = float(params.get("arpu", 19))
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

    return {
        "generated": date.today().isoformat(),
        "provider": provider,
        "model": model,
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
    }


def markdown_report(result: dict) -> str:
    mode = result.get("mode", "predict")
    lines = [
        f"# COGS Sentinel Report",
        "",
        f"Generated: {result['generated']}",
        f"Mode: {mode}",
        f"Provider: {result['provider']} / {result['model']}",
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
