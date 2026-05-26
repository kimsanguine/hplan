from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.gate_state import parse_gate_state

FIXTURE = (Path(__file__).parent / "fixtures" / "gate_state.md").read_text()


class TestGateStateParser:
    def test_extracts_verdict(self):
        assert parse_gate_state(FIXTURE)["verdict"] == "CONDITIONAL_GO"

    def test_extracts_gate(self):
        assert parse_gate_state(FIXTURE)["gate"] == "build"

    def test_extracts_conditions(self):
        data = parse_gate_state(FIXTURE)
        assert len(data["conditions"]) == 3

    def test_condition_pass_count(self):
        data = parse_gate_state(FIXTURE)
        assert data["pass_count"] == 1
        assert data["total_count"] == 3

    def test_condition_details(self):
        data = parse_gate_state(FIXTURE)
        cond = data["conditions"][0]
        assert cond["name"] == "API 연동 검증"
        assert cond["status"] is True

    def test_extracts_blockers(self):
        data = parse_gate_state(FIXTURE)
        assert len(data["blockers"]) == 1
        assert "외부 API 키" in data["blockers"][0]

    def test_verdict_color_conditional_go(self):
        assert parse_gate_state(FIXTURE)["verdict_color"] == "amber"

    def test_verdict_color_go(self):
        md = FIXTURE.replace("verdict: CONDITIONAL_GO", "verdict: GO")
        assert parse_gate_state(md)["verdict_color"] == "green"

    def test_html_contains_verdict(self):
        from md_renderer import render
        html = render("gate-state", parse_gate_state(FIXTURE))
        assert html is not None
        assert "CONDITIONAL_GO" in html
