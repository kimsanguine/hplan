from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.pain_board import parse_pain_board

FIXTURE = (Path(__file__).parent / "fixtures" / "pain_board.md").read_text()

# 모든 테스트에서 재사용할 파싱 결과 (모듈 로드 시 1회)
_DATA = parse_pain_board(FIXTURE)


class TestPainBoardParser:
    def test_extracts_interview_count(self):
        assert _DATA["interview_count"] == 3

    def test_signal_gate_not_met(self):
        # 3 < 5 이므로 False
        assert _DATA["signal_gate_met"] is False

    def test_signal_gate_met(self):
        # Interview 섹션 5개 + 각 1개 카드 → signal_gate_met True
        lines = [f"## Interview {i}\n[Tag-{i}] \"인터뷰 내용 {i}\"" for i in range(1, 6)]
        md = "# Pain Board\n\n" + "\n\n".join(lines)
        result = parse_pain_board(md)
        assert result["signal_gate_met"] is True

    def test_extracts_pain_cards(self):
        assert len(_DATA["pain_cards"]) == 4

    def test_tag_counts(self):
        assert _DATA["tag_counts"]["Time-sink"] == 1
        assert _DATA["tag_counts"]["Cost-heavy"] == 1
        assert _DATA["tag_counts"]["Error-prone"] == 1
        assert _DATA["tag_counts"]["Scale-blocker"] == 1

    def test_pain_card_structure(self):
        card = _DATA["pain_cards"][0]
        assert card["tag"] == "Time-sink"
        assert card["interview"] == 1
        assert "수작업으로" in card["quote"]

    def test_html_contains_tag(self):
        from md_renderer import render
        html = render("pain-board", _DATA)
        assert "Time-sink" in html

    def test_quote_stripped_of_surrounding_quotes(self):
        # quote 필드에 따옴표 없어야 함
        card = _DATA["pain_cards"][0]
        assert not card["quote"].startswith('"')
        assert not card["quote"].endswith('"')

    def test_interview_attribution(self):
        # Interview 2의 카드들이 interview=2 로 태깅됨
        interview2_cards = [c for c in _DATA["pain_cards"] if c["interview"] == 2]
        assert len(interview2_cards) == 2

    def test_tag_counts_aggregate_correctly(self):
        # 중복 태그 집계 확인
        lines = [
            "# Pain Board",
            "## Interview 1",
            '[Time-sink] "이슈 A"',
            '[Time-sink] "이슈 B"',
            "## Interview 2",
            '[Time-sink] "이슈 C"',
        ]
        md = "\n".join(lines)
        result = parse_pain_board(md)
        assert result["tag_counts"]["Time-sink"] == 3

    def test_template_field(self):
        assert _DATA["template"] == "pain-board"

    def test_empty_md_safe_defaults(self):
        result = parse_pain_board("")
        assert result["interview_count"] == 0
        assert result["signal_gate_met"] is False
        assert result["pain_cards"] == []
        assert result["tag_counts"] == {}
