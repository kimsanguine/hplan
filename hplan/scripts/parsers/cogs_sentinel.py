from .generic import parse_generic


def parse_cogs_sentinel(md: str) -> dict:
    return {**parse_generic(md), "template": "cogs-sentinel"}
