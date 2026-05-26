import re
from .generic import parse_generic

_AXES = [
    {"name": "ICP",                  "max": 15},
    {"name": "Recent Painful Event", "max": 15},
    {"name": "Workaround",           "max": 10},
    {"name": "Repetition",           "max": 10},
    {"name": "Economic Pain",        "max": 15},
    {"name": "Switching Trigger",    "max": 15},
    {"name": "MVP Narrowness",       "max": 10},
    {"name": "Acquisition Path",     "max": 10},
]


def parse_evidence_gate(md: str) -> dict:
    base = parse_generic(md)
    score = _extract_score(md)
    decision = _extract_decision(md)
    axes = _extract_axes(md)
    weak_axes = [a for a in axes if a["score"] < a["max"] * 0.7]
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
    for ax in _AXES:
        name = ax["name"]
        pattern = rf"##\s+{re.escape(name)}[^#]*?\n점수:\s*(\d+)"
        m = re.search(pattern, md, re.IGNORECASE)
        score = int(m.group(1)) if m else 0
        axes.append({"name": name, "score": score, "max": ax["max"]})
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
