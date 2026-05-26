from .generic import parse_generic


def parse_ost_viewer(md: str) -> dict:
    return {**parse_generic(md), "template": "ost-viewer"}
