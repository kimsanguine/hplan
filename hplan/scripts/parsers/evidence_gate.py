import re
from .generic import parse_generic

_AXIS_NAMES = [
    "ICP", "Recent Painful Event", "Workaround",
    "Repetition", "Economic Pain", "Switching Trigger",
    "MVP Narrowness", "Acquisition Path",
]


def parse_evidence_gate(md: str) -> dict:
    base = parse_generic(md)
    score = _extract_score(md)
    decision = _extract_decision(md)
    axes = _extract_axes(md)
    weak_axes = [a for a in axes if a["score"] < 10]
    return {
        **base,
        "template": "evidence-gate",
        "score": score,
        "decision": decision,
        "verdict_color": _verdict_color(score, decision),
        "verdict_label": _verdict_label(decision),
        "axes": axes,
        "weak_axes": weak_axes,
    }


def _extract_score(md: str) -> int:
    m = re.search(r"(?:score|총점)\s*:\s*(\d+)", md, re.IGNORECASE)
    return int(m.group(1)) if m else 0


def _extract_decision(md: str) -> str:
    m = re.search(r"decision\s*:\s*(\w+)", md, re.IGNORECASE)
    return m.group(1).lower() if m else "unknown"


def _extract_axes(md: str) -> list[dict]:
    axes = []
    for name in _AXIS_NAMES:
        pattern = rf"##\s+{re.escape(name)}.*?\n점수:\s*(\d+)"
        m = re.search(pattern, md, re.IGNORECASE | re.DOTALL)
        score = int(m.group(1)) if m else 0
        axes.append({"name": name, "score": score})
    return axes


def _verdict_color(score: int, decision: str) -> str:
    if decision == "build" or score >= 75:
        return "green"
    if score >= 55:
        return "amber"
    return "red"


def _verdict_label(decision: str) -> str:
    return {
        "build": "BUILD ▶",
        "hold": "HOLD ✋",
        "interview": "INTERVIEW MORE",
    }.get(decision, decision.upper())
