from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from decision_log import append, audit  # noqa: E402


def _root_with(tmp_path, decisions):
    root = tmp_path
    for d in decisions:
        append(root, d)
    return root


class TestAuditConditionalGo:
    def test_conditional_go_shipped_counts_as_correct(self, tmp_path):
        # Regression: CONDITIONAL_GO had no branch and always fell to `wrong`,
        # even when the gate's own promise (build with mitigations) came true.
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "build", "decision": "CONDITIONAL_GO",
             "outcome": "shipped"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 1.0

    def test_conditional_go_killed_counts_as_wrong(self, tmp_path):
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "build", "decision": "CONDITIONAL_GO",
             "outcome": "killed"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 0.0


class TestAuditPivot:
    def test_pivot_shipped_counts_as_correct(self, tmp_path):
        # Regression: only decision=pivot + outcome=="pivoted" counted as a
        # hit, so a pivoted direction that later shipped was scored wrong.
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "evidence", "decision": "pivot",
             "outcome": "shipped"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 1.0

    def test_pivot_pivoted_still_counts_as_correct(self, tmp_path):
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "evidence", "decision": "pivot",
             "outcome": "pivoted"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 1.0

    def test_pivot_killed_counts_as_wrong(self, tmp_path):
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "evidence", "decision": "pivot",
             "outcome": "killed"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 0.0


class TestAuditUnaffectedPaths:
    def test_hold_pivoted_still_correct(self, tmp_path):
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "evidence", "decision": "hold",
             "outcome": "pivoted"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 1.0

    def test_build_shipped_still_correct(self, tmp_path):
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "build", "decision": "build",
             "outcome": "shipped"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 1.0

    def test_mixed_set_matches_expected_hit_rate(self, tmp_path):
        # 3 correct (interview->shipped, build->shipped, build->shipped),
        # 1 wrong (CONDITIONAL_GO->... no branch matches an unmapped
        # outcome, e.g. alive_no_revenue, so it still falls to wrong).
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "evidence", "decision": "interview",
             "outcome": "shipped"},
            {"project": "p", "gate": "build", "decision": "build",
             "outcome": "shipped"},
            {"project": "p", "gate": "build", "decision": "build",
             "outcome": "shipped"},
            {"project": "p", "gate": "build", "decision": "CONDITIONAL_GO",
             "outcome": "alive_no_revenue"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 0.75
