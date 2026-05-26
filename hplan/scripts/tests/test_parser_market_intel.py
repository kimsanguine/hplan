from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.market_intel import parse_market_intel

FIXTURE = (Path(__file__).parent / "fixtures" / "market_intel.md").read_text()

_DATA = parse_market_intel(FIXTURE)


class TestMarketIntelParser:
    def test_extracts_table_headers(self):
        assert _DATA["table_headers"] == ["제품", "가격", "핵심 기능", "취약점", "우리 우위"]

    def test_extracts_table_rows(self):
        assert len(_DATA["table_rows"]) == 3

    def test_first_row_values(self):
        assert _DATA["table_rows"][0][0] == "ProductA"
        assert _DATA["table_rows"][0][1] == "$29/mo"

    def test_our_product_row(self):
        row = _DATA["table_rows"][2]
        assert row[0] == "우리 제품"

    def test_no_table_returns_empty(self):
        data2 = parse_market_intel("# Analysis\n\nNo table here.")
        assert data2["table_headers"] == []
        assert data2["table_rows"] == []

    def test_html_contains_competitor(self):
        from md_renderer import render
        html = render("market-intel", _DATA)
        assert html is not None
        assert "ProductA" in html

    def test_html_contains_header(self):
        from md_renderer import render
        html = render("market-intel", _DATA)
        assert "제품" in html

    def test_template_key(self):
        assert _DATA["template"] == "market-intel"

    def test_all_row_cells_count(self):
        # 각 행은 헤더 수(5)와 동일한 셀 수를 가져야 함
        for row in _DATA["table_rows"]:
            assert len(row) == len(_DATA["table_headers"])

    def test_second_row_values(self):
        assert _DATA["table_rows"][1][0] == "ProductB"
        assert _DATA["table_rows"][1][1] == "$49/mo"
        assert _DATA["table_rows"][1][2] == "기능 C"
