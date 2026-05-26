import re
from .generic import parse_generic


def parse_cogs_sentinel(md: str) -> dict:
    base = parse_generic(md)
    verdict = _extract_field(md, "verdict") or "UNKNOWN"
    gross_margin = _extract_int(md, "gross_margin")
    p50_margin = _extract_int(md, "p50_margin")
    p90_margin = _extract_int(md, "p90_margin")
    break_even_users = _extract_int(md, "break_even_users")
    scenarios = _extract_scenarios(md)
    return {
        **base,
        "template": "cogs-sentinel",
        "verdict": verdict.upper(),
        "verdict_color": _verdict_color(verdict),
        "gross_margin": gross_margin,
        "p50_margin": p50_margin,
        "p90_margin": p90_margin,
        "break_even_users": break_even_users,
        "scenarios": scenarios,
    }


def _extract_field(md: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}\s*:\s*(\S+)", md, re.IGNORECASE | re.MULTILINE)
    return m.group(1).strip() if m else None


def _extract_int(md: str, key: str) -> int:
    val = _extract_field(md, key)
    if val is None:
        return 0
    return int(re.sub(r"[^\d]", "", val) or "0")


def _extract_scenarios(md: str) -> list[dict]:
    scenarios = []
    for m in re.finditer(r"\|\s*([\d:]+)\s*\|\s*(\d+)%?\s*\|", md):
        label, margin = m.group(1).strip(), int(m.group(2))
        if re.match(r"\d+:\d+", label):
            scenarios.append({"label": label, "margin": margin})
    return scenarios


def _verdict_color(verdict: str) -> str:
    v = verdict.upper()
    if v == "GREEN":
        return "green"
    if v == "CONDITIONAL_GO":
        return "amber"
    return "red"
