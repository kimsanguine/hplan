from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.cogs_sentinel import parse_cogs_sentinel

FIXTURE = (Path(__file__).parent / "fixtures" / "cogs_sentinel.md").read_text()


class TestCogsSentinelParser:
    def test_extracts_verdict(self):
        assert parse_cogs_sentinel(FIXTURE)["verdict"] == "GREEN"

    def test_extracts_gross_margin(self):
        assert parse_cogs_sentinel(FIXTURE)["gross_margin"] == 68

    def test_extracts_p50(self):
        assert parse_cogs_sentinel(FIXTURE)["p50_margin"] == 72

    def test_extracts_p90(self):
        assert parse_cogs_sentinel(FIXTURE)["p90_margin"] == 61

    def test_extracts_break_even(self):
        assert parse_cogs_sentinel(FIXTURE)["break_even_users"] == 312

    def test_extracts_scenarios(self):
        data = parse_cogs_sentinel(FIXTURE)
        assert len(data["scenarios"]) == 4
        assert data["scenarios"][0] == {"label": "0:1", "margin": 72}

    def test_verdict_color_green(self):
        assert parse_cogs_sentinel(FIXTURE)["verdict_color"] == "green"

    def test_verdict_color_red(self):
        md = FIXTURE.replace("verdict: GREEN", "verdict: RED")
        assert parse_cogs_sentinel(md)["verdict_color"] == "red"

    def test_html_contains_verdict(self):
        from md_renderer import render
        html = render("cogs-sentinel", parse_cogs_sentinel(FIXTURE))
        assert html is not None
        assert "GREEN" in html
