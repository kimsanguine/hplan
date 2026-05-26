import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from md_renderer import select_template, should_exclude


class TestExcludePatterns:
    def test_claude_md_excluded(self):
        assert should_exclude("CLAUDE.md") is True

    def test_readme_excluded(self):
        assert should_exclude("README.md") is True

    def test_plugin_md_excluded(self):
        assert should_exclude("hplan/PLUGIN.md") is True

    def test_skill_md_excluded(self):
        assert should_exclude("hplan/skills/evidence-rubric/SKILL.md") is True

    def test_references_excluded(self):
        assert should_exclude("hplan/references/market-research.md") is True

    def test_examples_excluded(self):
        assert should_exclude("hplan/skills/cogs-sentinel/examples/good-01.md") is True

    def test_harness_md_not_excluded(self):
        assert should_exclude("harness/evidence/report.md") is False

    def test_docs_md_not_excluded(self):
        assert should_exclude("docs/PRD.md") is False

    def test_changelog_excluded(self):
        assert should_exclude("CHANGELOG.md") is True

    def test_contributing_excluded(self):
        assert should_exclude("CONTRIBUTING.md") is True

    def test_guide_excluded(self):
        assert should_exclude("GUIDE.md") is True

    def test_guide_prefixed_excluded(self):
        assert should_exclude("GUIDE-ko.md") is True


class TestTemplateSelection:
    def test_evidence_report(self):
        assert select_template("harness/evidence/report.md") == "evidence-gate"

    def test_cogs_report(self):
        assert select_template("harness/build-gate/cogs_report.md") == "cogs-sentinel"

    def test_state_md(self):
        assert select_template("harness/STATE.md") == "gate-state"

    def test_pain_md(self):
        assert select_template("harness/pain.md") == "pain-board"

    def test_opportunity_tree(self):
        assert select_template("docs/OPPORTUNITY_TREE.md") == "ost-viewer"

    def test_competitors_md(self):
        assert select_template("harness/competitors.md") == "market-intel"

    def test_architecture_md(self):
        assert select_template("harness/ARCHITECTURE.md") == "architecture-blueprint"

    def test_progress_md(self):
        assert select_template("harness/PROGRESS.md") == "sprint-tracker"

    def test_prd_md(self):
        assert select_template("docs/PRD.md") == "prd-reader"

    def test_design_md(self):
        assert select_template("docs/DESIGN.md") == "design-system"

    def test_respect_md(self):
        assert select_template(".design/RESPECT.md") == "design-system"

    def test_other_harness_md_gets_generic(self):
        assert select_template("harness/market.md") == "generic"

    def test_other_docs_md_gets_generic(self):
        assert select_template("docs/DESIGN_SYSTEM.md") == "generic"

    def test_specs_md_gets_generic(self):
        assert select_template("specs/001-auth/spec.md") == "generic"

    def test_unrelated_path_returns_none(self):
        assert select_template("src/main.py") is None


from parsers import parse as parse_md


class TestGenericParser:
    def test_extracts_title_from_h1(self):
        md = "# My Document\n\nSome content here."
        data = parse_md(md, "generic")
        assert data["title"] == "My Document"

    def test_extracts_title_from_frontmatter(self):
        md = "---\ntitle: Test Title\n---\n# Ignored H1"
        data = parse_md(md, "generic")
        assert data["title"] == "Test Title"

    def test_extracts_headings(self):
        md = "# Title\n## Section A\n### Sub\n## Section B"
        data = parse_md(md, "generic")
        assert "Section A" in [h["text"] for h in data["headings"]]
        assert "Section B" in [h["text"] for h in data["headings"]]

    def test_detects_mermaid_blocks(self):
        md = "```mermaid\nflowchart LR\nA --> B\n```"
        data = parse_md(md, "generic")
        assert data["has_mermaid"] is True

    def test_no_mermaid_when_absent(self):
        md = "# Title\n\nPlain text."
        data = parse_md(md, "generic")
        assert data["has_mermaid"] is False

    def test_extracts_body_md(self):
        md = "# Title\n\nContent with **bold** text."
        data = parse_md(md, "generic")
        assert data["body_md"] == md

    def test_empty_md_returns_safe_defaults(self):
        data = parse_md("", "generic")
        assert data["title"] == "Untitled"
        assert data["headings"] == []
        assert data["has_mermaid"] is False

    def test_code_block_hash_not_extracted_as_heading(self):
        md = "# Real Heading\n\n```python\n# not a heading\n```"
        data = parse_md(md, "generic")
        heading_texts = [h["text"] for h in data["headings"]]
        assert "not a heading" not in heading_texts
        assert "Real Heading" in heading_texts
