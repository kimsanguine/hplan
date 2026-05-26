from .generic import parse_generic


def parse_pain_board(md: str) -> dict:
    return {**parse_generic(md), "template": "pain-board"}
