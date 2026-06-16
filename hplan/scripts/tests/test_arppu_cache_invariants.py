"""Regression tests for the adversarial-review findings (false-positive paths).

Finding 1: --arppu must drive the margin/decision base (alias of --arpu), not leave
           the gate scoring against the default $19 ARPU.
Finding 2: cached_tokens_in must not exceed tokens_in (impossible cache coverage that
           would understate COGS and manufacture a GREEN).
"""
import sys
import pytest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(SCRIPTS_DIR))

from cogs_sentinel import run, _validate_params  # noqa: E402


def _hi_conv(**kw):
    # paid_conversion high so the free-user blend doesn't mask the margin gate —
    # this is the regime where the arpu/arppu split actually flips the verdict.
    p = {"model": "claude-haiku-4-5", "tokens_in": 2000, "tokens_out": 1500,
         "calls_per_user_month": 150, "paid_conversion": 0.8}
    p.update(kw)
    return p


def test_arppu_drives_decision_like_arpu():
    # WHY: --arppu is documented as an alias of --arpu. Passing --arppu 2 must yield
    # the SAME COGS decision as passing --arpu 2 — not a false GREEN scored at $19.
    via_arppu = run(_hi_conv(arppu=2))
    via_arpu = run(_hi_conv(arpu=2))
    assert via_arppu["decision"] == via_arpu["decision"]
    assert via_arppu["inputs"]["arpu"] == 2.0  # margin base, not the default 19


def test_arppu_low_price_is_not_green():
    # WHY: a $2 paid product with heavy calls is not economically GREEN. The pre-fix
    # bug returned GREEN because margins were scored against the $19 default.
    assert run(_hi_conv(arppu=2))["decision"] != "GREEN"


def test_explicit_arpu_still_wins_over_arppu():
    # WHY: when both are given they may intentionally differ; explicit --arpu governs
    # the margin base while arppu drives ARPU(all users).
    r = run(_hi_conv(arpu=19, arppu=2))
    assert r["inputs"]["arpu"] == 19.0


def test_cached_exceeding_tokens_in_is_rejected():
    # WHY: cached input can't exceed total input. The gate must fail loud, not price
    # an impossible cache state as a discount.
    with pytest.raises(SystemExit):
        _validate_params({"tokens_in": 1000, "tokens_out": 500, "cached_tokens_in": 5000})


def test_cached_within_bounds_is_allowed():
    _validate_params({"tokens_in": 1000, "tokens_out": 500, "cached_tokens_in": 1000})  # no raise


def test_caching_surfaced_in_inputs_only_when_used():
    # WHY: transparency without breaking legacy output — flags appear only when set.
    assert "cached_tokens_in" not in run(_hi_conv(arpu=19))["inputs"]
    used = run(_hi_conv(arpu=19, cached_tokens_in=500))["inputs"]
    assert used["cached_tokens_in"] == 500 and used["batch"] is False
