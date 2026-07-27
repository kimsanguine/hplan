from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))
from decision_log import append, append_hitl, read_all  # noqa: E402


class TestHitlPromotion:
    def test_log_can_reference_prior_hitl_decision(self, tmp_path):
        hitl = append_hitl(tmp_path, {
            "phase": "build",
            "q": "실섭외 없이 합성 페르소나로 진행할 것인가?",
            "options": ["실섭외 진행", "합성 페르소나로 확정"],
            "chosen": "합성 페르소나로 확정",
        })
        entry = append(tmp_path, {
            "project": "p", "gate": "evidence", "decision": "build",
            "from_hitl": hitl["id"],
        })
        assert entry["from_hitl"] == hitl["id"]

    def test_log_rejects_unknown_hitl_id(self, tmp_path):
        # Regression: without this check, from_hitl could reference a
        # nonexistent or mistyped HITL id and the promotion link would be
        # silently unverifiable.
        try:
            append(tmp_path, {
                "project": "p", "gate": "evidence", "decision": "build",
                "from_hitl": "hitl-does-not-exist",
            })
            assert False, "expected SystemExit for unknown from_hitl id"
        except SystemExit:
            pass
        assert read_all(tmp_path) == []

    def test_log_without_from_hitl_omits_field(self, tmp_path):
        entry = append(tmp_path, {"project": "p", "gate": "evidence", "decision": "build"})
        assert "from_hitl" not in entry
