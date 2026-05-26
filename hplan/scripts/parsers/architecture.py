from .generic import parse_generic


def parse_architecture(md: str) -> dict:
    return {**parse_generic(md), "template": "architecture-blueprint"}
