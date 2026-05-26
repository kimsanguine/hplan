from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.architecture import parse_architecture

FIXTURE = (Path(__file__).parent / "fixtures" / "architecture_blueprint.md").read_text()

# 모든 테스트에서 재사용할 파싱 결과 (모듈 로드 시 1회)
_DATA = parse_architecture(FIXTURE)


class TestArchitectureParser:
    def test_extracts_mermaid_code(self):
        assert "flowchart TD" in _DATA["mermaid_code"]

    def test_mermaid_no_fences(self):
        assert "```mermaid" not in _DATA["mermaid_code"]

    def test_routing_table_headers(self):
        assert _DATA["routing_table"]["headers"] == ["태스크", "모델", "이유"]

    def test_routing_table_rows(self):
        assert len(_DATA["routing_table"]["rows"]) == 2
        assert _DATA["routing_table"]["rows"][0][0] == "planning"

    def test_memory_short(self):
        assert _DATA["memory_short"] == "Redis TTL 1h"

    def test_memory_long(self):
        assert _DATA["memory_long"] == "pgvector"

    def test_missing_fields_return_defaults(self):
        data2 = parse_architecture("# Architecture\n\nNo details here.")
        assert data2["mermaid_code"] == ""
        assert data2["routing_table"] == {"headers": [], "rows": []}
        assert data2["memory_short"] == ""
        assert data2["memory_long"] == ""

    def test_html_renders_mermaid(self):
        from md_renderer import render
        html = render("architecture-blueprint", _DATA)
        assert html is not None
        assert "mermaid" in html.lower()
