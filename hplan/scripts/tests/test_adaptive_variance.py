"""Intent tests for the adaptive cost-variance + caching layer (backward-compatible)."""
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from cogs_sentinel import run, cost_per_call, _resolve_p90_ratio  # noqa: E402


def _base(**kw):
    p = {"model": "claude-haiku-4-5", "tokens_in": 1200, "tokens_out": 500,
         "calls_per_user_month": 60, "arpu": 19}
    p.update(kw)
    return p


def test_fallback_ratio_is_legacy_2_2():
    # WHY: no workload/ratio given must reproduce the legacy constant — existing
    # verdicts must not shift just because the resolver exists.
    ratio, source = _resolve_p90_ratio({})
    assert ratio == 2.2 and source == "fallback"
    r = run(_base())
    assert r["variance"] == {"p90_p50_ratio": 2.2, "source": "fallback"}


def test_workload_prior_drives_p90():
    ratio, source = _resolve_p90_ratio({"workload": "agent"})
    assert ratio == 5.0 and source == "workload:agent"
    r = run(_base(workload="agent"))
    pc = r["per_call_cost_usd"]
    assert round(pc["p90"], 6) == round(pc["p50"] * 5.0, 6)


def test_distribution_ratio_beats_workload():
    # WHY: a directly-measured ratio is more trustworthy than an archetype prior.
    ratio, source = _resolve_p90_ratio({"workload": "agent", "p90_p50_ratio": 3.3})
    assert ratio == 3.3 and source == "distribution"


def test_cached_input_bills_at_tenth():
    prices = {"input_per_mtok": 1.0, "output_per_mtok": 5.0}
    full = cost_per_call(prices, 1000, 0)
    cached = cost_per_call(prices, 1000, 0, cached_tokens_in=1000)
    assert cached == full * 0.1


def test_batch_halves_total():
    prices = {"input_per_mtok": 1.0, "output_per_mtok": 5.0}
    assert cost_per_call(prices, 1000, 1000, batch=True) == cost_per_call(prices, 1000, 1000) * 0.5


def test_default_cost_per_call_is_legacy_formula():
    # WHY: backward compatibility — defaults must equal the old two-term formula.
    prices = {"input_per_mtok": 3.0, "output_per_mtok": 15.0}
    assert cost_per_call(prices, 1500, 800) == (1500 / 1_000_000) * 3.0 + (800 / 1_000_000) * 15.0
