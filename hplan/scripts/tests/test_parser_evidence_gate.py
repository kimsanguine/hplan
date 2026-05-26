from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.evidence_gate import parse_evidence_gate

FIXTURE = (Path(__file__).parent / "fixtures" / "evidence_gate.md").read_text()


class TestEvidenceGateParser:
    def test_extracts_score(self):
        data = parse_evidence_gate(FIXTURE)
        assert data["score"] == 87

    def test_extracts_decision(self):
        data = parse_evidence_gate(FIXTURE)
        assert data["decision"] == "build"

    def test_score_color_build(self):
        data = parse_evidence_gate(FIXTURE)
        assert data["verdict_color"] == "green"

    def test_score_color_hold(self):
        md = FIXTURE.replace("score: 87", "score: 45").replace("decision: build", "decision: hold")
        data = parse_evidence_gate(md)
        assert data["verdict_color"] == "red"

    def test_extracts_axes(self):
        data = parse_evidence_gate(FIXTURE)
        axes = {a["name"]: a["score"] for a in data["axes"]}
        assert axes["ICP"] == 12
        assert axes["Recent Painful Event"] == 13

    def test_identifies_weak_axes(self):
        data = parse_evidence_gate(FIXTURE)
        weak_names = [a["name"] for a in data["weak_axes"]]
        assert "Switching Trigger" in weak_names

    def test_html_contains_score(self):
        from md_renderer import render
        data = parse_evidence_gate(FIXTURE)
        html = render("evidence-gate", data)
        assert html is not None
        assert "87" in html

    def test_html_contains_build_verdict(self):
        from md_renderer import render
        data = parse_evidence_gate(FIXTURE)
        html = render("evidence-gate", data)
        assert "BUILD" in html or "build" in html.lower()

    def test_missing_axis_score_returns_zero_not_adjacent(self):
        """ICP 섹션 점수 없으면 0 반환, 인접 섹션 점수 도용 없음."""
        md = FIXTURE.replace("## ICP\n점수: 12/15", "## ICP\n설명만 있고 점수 없음")
        data = parse_evidence_gate(md)
        axes = {a["name"]: a["score"] for a in data["axes"]}
        assert axes["ICP"] == 0
        assert axes["Recent Painful Event"] == 13  # 인접 섹션 점수 유지
