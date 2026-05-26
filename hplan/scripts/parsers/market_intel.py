from .generic import parse_generic


def parse_market_intel(md: str) -> dict:
    return {**parse_generic(md), "template": "market-intel"}
