from .generic import parse_generic


def parse_gate_state(md: str) -> dict:
    return {**parse_generic(md), "template": "gate-state"}
