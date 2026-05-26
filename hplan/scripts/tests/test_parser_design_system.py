from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.design_system import parse_design_system

FIXTURE = (Path(__file__).parent / "fixtures" / "design_system.md").read_text()


class TestDesignSystemParser:
    def test_extracts_colors_count(self):
        data = parse_design_system(FIXTURE)
        assert len(data["colors"]) == 3

    def test_color_with_hex(self):
        data = parse_design_system(FIXTURE)
        colors = {c["name"]: c for c in data["colors"]}
        assert colors["Primary"]["hex"] == "#6366F1"
        assert colors["Primary"]["rgb"] is None

    def test_color_with_rgb(self):
        data = parse_design_system(FIXTURE)
        colors = {c["name"]: c for c in data["colors"]}
        assert colors["Surface"]["rgb"] == "rgb(30, 41, 59)"
        assert colors["Surface"]["hex"] is None

    def test_extracts_typography(self):
        data = parse_design_system(FIXTURE)
        typo = {t["name"]: t for t in data["typography"]}
        assert typo["H1"]["size"] == "36px"
        assert typo["H1"]["weight"] == "700"

    def test_extracts_tailwind_tokens(self):
        data = parse_design_system(FIXTURE)
        assert "bg-slate-900" in data["tailwind_tokens"]
        assert "text-indigo-400" in data["tailwind_tokens"]
        assert "rounded-xl" in data["tailwind_tokens"]

    def test_template_field(self):
        data = parse_design_system(FIXTURE)
        assert data["template"] == "design-system"

    def test_empty_md_safe_defaults(self):
        data = parse_design_system("")
        assert data["colors"] == []
        assert data["typography"] == []
        assert data["tailwind_tokens"] == []

    def test_html_renders_color_name(self):
        from md_renderer import render
        data = parse_design_system(FIXTURE)
        html = render("design-system", data)
        assert html is not None
        assert "Primary" in html
