import os
import subprocess
from pathlib import Path
import sys

RENDERER = Path(__file__).parent.parent / "md_renderer.py"
SCRIPTS_DIR = Path(__file__).parent.parent


class TestRendererIntegration:
    def test_generic_md_creates_html(self, tmp_path):
        md_file = tmp_path / "harness" / "market.md"
        md_file.parent.mkdir(parents=True)
        md_file.write_text("# Market Analysis\n\nContent here.", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(RENDERER), str(md_file)],
            capture_output=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode == 0
        html_file = md_file.with_suffix(".html")
        assert html_file.exists()
        content = html_file.read_text()
        assert "Market Analysis" in content
        assert "<!DOCTYPE html>" in content

    def test_excluded_md_does_not_create_html(self, tmp_path):
        md_file = tmp_path / "CLAUDE.md"
        md_file.write_text("# Claude instructions", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(RENDERER), str(md_file)],
            capture_output=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode == 0
        html_file = md_file.with_suffix(".html")
        assert not html_file.exists()

    def test_nonexistent_file_exits_cleanly(self):
        result = subprocess.run(
            [sys.executable, str(RENDERER), "/nonexistent/path/file.md"],
            capture_output=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode == 0

    def test_no_args_exits_cleanly(self):
        result = subprocess.run(
            [sys.executable, str(RENDERER)],
            capture_output=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode == 0

    def test_unmatched_path_does_not_create_html(self, tmp_path):
        """harness/docs/specs 외 경로는 HTML 생성 안 함."""
        md_file = tmp_path / "src" / "utils.md"
        md_file.parent.mkdir(parents=True)
        md_file.write_text("# Utils\n\nSome content.", encoding="utf-8")

        result = subprocess.run(
            [sys.executable, str(RENDERER), str(md_file)],
            capture_output=True,
            env={**os.environ, "PYTHONPATH": str(SCRIPTS_DIR)},
        )
        assert result.returncode == 0
        html_file = md_file.with_suffix(".html")
        assert not html_file.exists()
