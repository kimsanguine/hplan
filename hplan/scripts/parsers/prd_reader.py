from .generic import parse_generic


def parse_prd_reader(md: str) -> dict:
    return {**parse_generic(md), "template": "prd-reader"}
