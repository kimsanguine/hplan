from .generic import parse_generic


def parse_design_system(md: str) -> dict:
    return {**parse_generic(md), "template": "design-system"}
