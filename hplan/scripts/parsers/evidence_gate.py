from .generic import parse_generic


def parse_evidence_gate(md: str) -> dict:
    return {**parse_generic(md), "template": "evidence-gate"}
