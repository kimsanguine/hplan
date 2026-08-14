import json
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
LOCK_PATH = REPO_ROOT / "hplan-core.lock"
MATRIX_PATH = REPO_ROOT / "docs" / "hplan-capability-matrix.json"
ADAPTER_PATH = REPO_ROOT / "docs" / "hplan-core-adapter.json"
CLAUDE_MD_PATH = REPO_ROOT / "CLAUDE.md"

EXPECTED_RULE_IDS = {
    "think-before-coding",
    "simplicity-first",
    "surgical-changes",
    "goal-driven-execution",
    "models-for-judgment-only",
    "tests-verify-intent",
    "checkpoint-after-significant-step",
    "fail-loud",
    "agent-scope-declaration",
}
EXPECTED_ALIASES = {
    "roadmap": "prd",
    "router": "orchestration",
    "stakeholder-update": "ops-review",
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_claude_adapter_snapshot_has_the_complete_core_contract():
    lock = load_json(LOCK_PATH)
    matrix = load_json(MATRIX_PATH)
    adapter = load_json(ADAPTER_PATH)

    assert lock["target"] == "claude"
    assert lock["files"] == [
        "hplan-core.lock",
        "hplan-capability-matrix.json",
        "HPLAN_CAPABILITY_MATRIX.md",
    ]
    assert re.fullmatch(r"[0-9a-f]{64}", lock["source_sha256"])

    assert matrix["target"] == "claude"
    assert {rule["rule_id"] for rule in matrix["rules"]} == EXPECTED_RULE_IDS
    assert len(matrix["capabilities"]) == 34
    assert len({capability["capability_id"] for capability in matrix["capabilities"]}) == 34
    assert {alias["alias_id"]: alias["target"] for alias in matrix["aliases"]} == EXPECTED_ALIASES

    for capability in matrix["capabilities"]:
        assert capability["support_state"] == "native"
        assert capability["entrypoint"] == f"capability:{capability['capability_id']}"
        assert capability["smoke_fixture_id"] == f"smoke.{capability['capability_id']}"

    assert adapter["target"] == "claude"
    assert adapter["core"]["version"] == matrix["contract_version"]
    assert adapter["core"]["contract_version"] == matrix["contract_version"] == lock["contract_version"]
    assert re.fullmatch(r"[0-9a-f]{40}", adapter["core"]["commit"])
    assert adapter["core"]["source_sha256"] == lock["source_sha256"]
    assert adapter["snapshot"] == {
        "lock_file": "../hplan-core.lock",
        "matrix_file": "hplan-capability-matrix.json",
        "markdown_file": "HPLAN_CAPABILITY_MATRIX.md",
        "canonical_capability_count": 34,
        "compatibility_alias_count": 3,
        "support_state_counts": {"native": 34},
    }


def test_claude_md_declares_the_synced_rule_contract_and_adapter_boundary():
    claude_md = CLAUDE_MD_PATH.read_text(encoding="utf-8")

    assert "hplan Core Contract Sync" in claude_md
    assert "docs/hplan-capability-matrix.json" in claude_md
    assert "adapter-required is not execution permission or external-write permission" in claude_md
    for rule_id in EXPECTED_RULE_IDS:
        assert rule_id in claude_md
