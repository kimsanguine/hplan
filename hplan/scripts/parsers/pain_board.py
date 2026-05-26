import re
from .generic import parse_generic


def parse_pain_board(md: str) -> dict:
    base = parse_generic(md)
    interview_count = _count_interviews(md)
    pain_cards = _extract_pain_cards(md)
    tag_counts = _aggregate_tags(pain_cards)
    return {
        **base,
        "template": "pain-board",
        "interview_count": interview_count,
        "signal_gate_met": interview_count >= 5,
        "pain_cards": pain_cards,
        "tag_counts": tag_counts,
    }


def _count_interviews(md: str) -> int:
    return len(re.findall(r"^##\s+Interview\s+\d+", md, re.MULTILINE))


def _extract_pain_cards(md: str) -> list[dict]:
    cards = []
    current_interview = 0
    for line in md.splitlines():
        interview_match = re.match(r"^##\s+Interview\s+(\d+)", line)
        if interview_match:
            current_interview = int(interview_match.group(1))
            continue
        card_match = re.match(r'\[([^\]]+)\]\s*"([^"]+)"', line)
        if card_match:
            cards.append({
                "tag": card_match.group(1),
                "quote": card_match.group(2),
                "interview": current_interview,
            })
    return cards


def _aggregate_tags(pain_cards: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for card in pain_cards:
        tag = card["tag"]
        counts[tag] = counts.get(tag, 0) + 1
    return counts
