from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.prd_reader import parse_prd_reader

FIXTURE = (Path(__file__).parent / "fixtures" / "prd_reader.md").read_text()

# 모든 테스트에서 재사용할 파싱 결과 (모듈 로드 시 1회)
_DATA = parse_prd_reader(FIXTURE)


class TestPrdReaderParser:
    def test_extracts_evidence_score(self):
        assert _DATA["evidence_score"] == 87

    def test_extracts_cogs_verdict(self):
        assert _DATA["cogs_verdict"] == "GREEN"

    def test_extracts_state(self):
        assert _DATA["state"] == "1/3"

    def test_extracts_sections(self):
        assert len(_DATA["sections"]) == 3
        assert all(s["level"] == 2 for s in _DATA["sections"])

    def test_section_names(self):
        names = [s["text"] for s in _DATA["sections"]]
        assert "1. 개요" in names
        assert "3. JTBD" in names

    def test_extracts_mermaid_code(self):
        assert "flowchart LR" in _DATA["mermaid_code"]
        assert "```mermaid" not in _DATA["mermaid_code"]

    def test_missing_metadata_defaults(self):
        data2 = parse_prd_reader("# PRD\n\n## Section A\nContent.")
        assert data2["evidence_score"] == 0
        assert data2["cogs_verdict"] == ""
        assert data2["state"] == ""
        assert data2["mermaid_code"] == ""

    def test_html_contains_title(self):
        from md_renderer import render
        html = render("prd-reader", _DATA)
        assert html is not None
        assert "PRD" in html
