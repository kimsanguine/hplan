from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.ost_viewer import parse_ost_viewer

FIXTURE = (Path(__file__).parent / "fixtures" / "ost_viewer.md").read_text()

# 모든 테스트에서 재사용할 파싱 결과 (모듈 로드 시 1회)
_DATA = parse_ost_viewer(FIXTURE)


class TestOstViewerParser:
    def test_extracts_mermaid_code(self):
        assert "flowchart TD" in _DATA["mermaid_code"]

    def test_mermaid_code_no_fences(self):
        # fence 줄이 포함되지 않아야 함
        assert "```mermaid" not in _DATA["mermaid_code"]
        assert _DATA["mermaid_code"].strip().startswith("flowchart")

    def test_extracts_solutions(self):
        assert len(_DATA["solutions"]) == 2

    def test_solution_names(self):
        names = [s["name"] for s in _DATA["solutions"]]
        assert "Solution A — 단계별 가이드" in names

    def test_solution_status_running(self):
        sol = next(s for s in _DATA["solutions"] if "Solution A" in s["name"])
        assert sol["status"] == "running"

    def test_solution_status_pending(self):
        sol = next(s for s in _DATA["solutions"] if "Solution B" in s["name"])
        assert sol["status"] == "pending"

    def test_no_mermaid_returns_empty_string(self):
        data2 = parse_ost_viewer("# OST\n\n## Solution X\nstatus: done")
        assert data2["mermaid_code"] == ""

    def test_html_renders_mermaid(self):
        from md_renderer import render
        html = render("ost-viewer", _DATA)
        assert html is not None
        assert "mermaid" in html.lower()

    def test_template_field(self):
        assert _DATA["template"] == "ost-viewer"

    def test_solution_status_done(self):
        data2 = parse_ost_viewer("# OST\n\n## Solution X\nstatus: done")
        assert data2["solutions"][0]["status"] == "done"

    def test_solution_default_status_pending(self):
        # status 줄이 없으면 pending 기본값
        data2 = parse_ost_viewer("# OST\n\n## Solution X\n\nsome other text")
        assert data2["solutions"][0]["status"] == "pending"

    def test_mermaid_inner_content_preserved(self):
        # 다이어그램 노드 내용이 보존되어야 함
        assert 'DAU +30%' in _DATA["mermaid_code"]

    def test_base_fields_present(self):
        # parse_generic에서 오는 base 필드 확인
        assert "title" in _DATA
        assert "headings" in _DATA
        assert "has_mermaid" in _DATA
