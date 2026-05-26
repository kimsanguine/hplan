import re
from .generic import parse_generic


def parse_gate_state(md: str) -> dict:
    base = parse_generic(md)
    verdict = _field(md, "verdict") or "UNKNOWN"
    gate = _field(md, "gate") or "unknown"
    generated = _field(md, "generated") or ""
    decision_id = _field(md, "decision_id") or ""
    conditions = _extract_conditions(md)
    pass_count = sum(1 for c in conditions if c["status"])
    blockers = _extract_blockers(md)
    return {
        **base,
        "template": "gate-state",
        "verdict": verdict.upper(),
        "verdict_color": _color(verdict),
        "gate": gate,
        "generated": generated,
        "decision_id": decision_id,
        "conditions": conditions,
        "pass_count": pass_count,
        "total_count": len(conditions),
        "blockers": blockers,
    }


def _field(md: str, key: str) -> str | None:
    m = re.search(rf"^{re.escape(key)}\s*:\s*(.+)$", md, re.MULTILINE | re.IGNORECASE)
    return m.group(1).strip() if m else None


def _extract_conditions(md: str) -> list[dict]:
    conditions = []
    for m in re.finditer(r"\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([✅❌][^|]*?)\s*\|", md):
        name = m.group(1).strip()
        verified_by = m.group(2).strip()
        status_raw = m.group(3).strip()
        # 헤더 행 및 구분 행 건너뜀
        if name in ("조건", "---", ":---", "---:") or set(name) <= set("-:"):
            continue
        conditions.append({
            "name": name,
            "verified_by": verified_by,
            "status": "✅" in status_raw,
        })
    return conditions


def _extract_blockers(md: str) -> list[str]:
    blockers = []
    in_blockers = False
    for line in md.splitlines():
        if re.match(r"##\s+블로커", line):
            in_blockers = True
            continue
        if in_blockers and re.match(r"##", line):
            break
        if in_blockers and line.startswith("- "):
            blockers.append(line[2:].strip())
    return blockers


def _color(verdict: str) -> str:
    v = verdict.upper()
    if v == "GO":
        return "green"
    if v == "CONDITIONAL_GO":
        return "amber"
    return "red"
