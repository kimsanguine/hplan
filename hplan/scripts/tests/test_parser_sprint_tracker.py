from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from parsers.sprint_tracker import parse_sprint_tracker

FIXTURE = (Path(__file__).parent / "fixtures" / "sprint_tracker.md").read_text()

# 모든 테스트에서 재사용할 파싱 결과 (모듈 로드 시 1회)
_DATA = parse_sprint_tracker(FIXTURE)


class TestSprintTrackerParser:
    def test_extracts_milestones_count(self):
        assert len(_DATA["milestones"]) == 2

    def test_milestone_names(self):
        assert _DATA["milestones"][0]["name"] == "W1 — API 연동"
        assert _DATA["milestones"][1]["name"] == "W2 — 프론트엔드"

    def test_milestone_done_count(self):
        assert _DATA["milestones"][0]["done"] == 3
        assert _DATA["milestones"][0]["total"] == 5

    def test_milestone_pct(self):
        assert _DATA["milestones"][0]["pct"] == 60

    def test_w2_zero_done(self):
        assert _DATA["milestones"][1]["done"] == 0
        assert _DATA["milestones"][1]["total"] == 3
        assert _DATA["milestones"][1]["pct"] == 0

    def test_total_counts(self):
        assert _DATA["total_done"] == 3
        assert _DATA["total_items"] == 8

    def test_blocker_item_flagged(self):
        items = _DATA["milestones"][0]["items"]
        blocker = next(i for i in items if i["is_blocker"])
        assert "외부 API 키" in blocker["text"]

    def test_non_blocker_items(self):
        items = _DATA["milestones"][0]["items"]
        # 블로커가 아닌 항목 확인
        non_blockers = [i for i in items if not i["is_blocker"]]
        assert len(non_blockers) == 4

    def test_cogs_values(self):
        assert _DATA["cogs_ceiling"] == 40
        assert _DATA["cogs_current"] == 28

    def test_cogs_ok(self):
        assert _DATA["cogs_ok"] is True

    def test_cogs_not_ok(self):
        md = FIXTURE.replace("COGS p90 current: 28%", "COGS p90 current: 45%")
        data2 = parse_sprint_tracker(md)
        assert data2["cogs_ok"] is False

    def test_cogs_missing_defaults_to_zero(self):
        md = "# PROGRESS\n\n## W1\n\n- [x] 완료\n"
        data = parse_sprint_tracker(md)
        assert data["cogs_ceiling"] == 0
        assert data["cogs_current"] == 0
        assert data["cogs_ok"] is True

    def test_item_done_field(self):
        items = _DATA["milestones"][0]["items"]
        done_items = [i for i in items if i["done"] is True]
        undone_items = [i for i in items if i["done"] is False]
        assert len(done_items) == 3
        assert len(undone_items) == 2

    def test_item_text_strips_prefix(self):
        items = _DATA["milestones"][0]["items"]
        # 아이템 text에 '- [x] ' 나 '- [ ] ' prefix 없어야 함
        for item in items:
            assert not item["text"].startswith("- [")
            assert not item["text"].startswith("[")

    def test_template_field(self):
        assert _DATA["template"] == "sprint-tracker"

    def test_html_contains_milestone(self):
        from md_renderer import render
        html = render("sprint-tracker", _DATA)
        assert html is not None
        assert "W1" in html
