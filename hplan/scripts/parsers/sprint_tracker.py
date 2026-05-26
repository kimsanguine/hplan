from .generic import parse_generic


def parse_sprint_tracker(md: str) -> dict:
    return {**parse_generic(md), "template": "sprint-tracker"}
