from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from decision_log import append, audit, audit_multi  # noqa: E402


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

    def test_conditional_go_external_success_counts_as_correct(self, tmp_path):
        # A conditional GO that went on to external success is a stronger
        # confirmation than plain "shipped" — must not be scored as a miss.
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "build", "decision": "CONDITIONAL_GO",
             "outcome": "external_success"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 1.0

    def test_conditional_go_pivoted_counts_as_correct(self, tmp_path):
        # Consistent with pivot/hold: pivoting away from a conditionally
        # approved direction is a normal learning outcome, not a gate miss.
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "build", "decision": "CONDITIONAL_GO",
             "outcome": "pivoted"},
        ])
        result = audit(root)
        assert result["hit_rate"] == 1.0

    def test_conditional_go_alive_no_revenue_counts_as_wrong(self, tmp_path):
        # Conditions were approved but the project never converted to
        # revenue — treated as a miss, distinct from pivoted/external_success.
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "build", "decision": "CONDITIONAL_GO",
             "outcome": "alive_no_revenue"},
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
        # 1 wrong (CONDITIONAL_GO->alive_no_revenue: conditional approval
        # that stayed alive without revenue counts as a miss).
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


class TestAuditMulti:
    def test_aggregates_across_project_roots(self, tmp_path):
        # Regression: audit() only ever read one project's harness/. There
        # was no way to see organization-wide calibration across projects
        # without manually summing each project's audit output by hand.
        root_a = tmp_path / "project-a"
        root_b = tmp_path / "project-b"
        _root_with(root_a, [
            {"project": "a", "gate": "build", "decision": "build", "outcome": "shipped"},
        ])
        _root_with(root_b, [
            {"project": "b", "gate": "build", "decision": "build", "outcome": "killed"},
        ])
        result = audit_multi([root_a, root_b])
        assert result["total"] == 2
        assert result["hit_rate"] == 0.5
        assert result["missed_builds"][0]["project"] == "b"

    def test_single_root_matches_plain_audit(self, tmp_path):
        root = _root_with(tmp_path, [
            {"project": "p", "gate": "build", "decision": "build", "outcome": "shipped"},
        ])
        assert audit_multi([root]) == audit(root)
