import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
VENDORED_CORE_ROOT = REPO_ROOT / "hplan-core-fixture"
FIXTURE_PROVENANCE_PATH = VENDORED_CORE_ROOT / "PROVENANCE.json"
LOCK_PATH = REPO_ROOT / "hplan-core.lock"
MATRIX_PATH = REPO_ROOT / "docs" / "hplan-capability-matrix.json"
MARKDOWN_PATH = REPO_ROOT / "docs" / "HPLAN_CAPABILITY_MATRIX.md"
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
EXPECTED_FIXTURE_PROVENANCE = {
    "core_commit": "3055f65e52991e226cc1aabd6fa0f31071aa99d7",
    "core_source_sha256": "aa5a43827a850892d4b3dab4c2520104cbade9529e835b8bd933ae462d7e263d",
    "files": {
        "contracts/aliases.json": "b55560c47d3a50aca0af41b80a2592a8d20b9b88c96b78c241af20ac7bd814ff",
        "contracts/capabilities.json": "9ece4dd6addbb2605ba07058337926b192bea7fa212bdbdda8748c8421af7e5d",
        "contracts/rules.json": "c6369184840c4176af8e0b369dc441dc6909ee9ecd6c373a967f18204ef4cfa1",
        "scripts/render_adapter_snapshot.py": "69d5fd7c5bba7bb68fec44be3e12d74e7ca32197fd9b6f51125adf31f9fa99d7",
        "scripts/validate_core.py": "784224b0c2781cd1a118fcfbc12d878b5c0cbde8b398d18c736ceb4115651477",
    },
}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_vendored_core_fixture_fails_closed_against_independent_provenance_constants():
    provenance = load_json(FIXTURE_PROVENANCE_PATH)

    assert provenance == EXPECTED_FIXTURE_PROVENANCE
    assert {
        relative: sha256(VENDORED_CORE_ROOT / relative)
        for relative in EXPECTED_FIXTURE_PROVENANCE["files"]
    } == EXPECTED_FIXTURE_PROVENANCE["files"]
    assert core_source_sha256(VENDORED_CORE_ROOT) == EXPECTED_FIXTURE_PROVENANCE["core_source_sha256"]
    assert load_json(LOCK_PATH)["source_sha256"] == EXPECTED_FIXTURE_PROVENANCE["core_source_sha256"]


def core_root():
    configured = os.environ.get("HPLAN_CORE_ROOT")
    root = Path(configured).expanduser().resolve() if configured else VENDORED_CORE_ROOT
    if not (root / "scripts" / "render_adapter_snapshot.py").is_file():
        pytest.fail(f"hplan-core renderer fixture is unavailable: {root}")
    return root


def test_renderer_parity_has_a_vendored_core_fixture_without_environment(monkeypatch):
    monkeypatch.delenv("HPLAN_CORE_ROOT", raising=False)

    assert core_root() == VENDORED_CORE_ROOT


def core_source_sha256(root):
    digest = hashlib.sha256()
    for filename in ("rules.json", "capabilities.json", "aliases.json"):
        digest.update(filename.encode("utf-8"))
        digest.update(b"\0")
        digest.update((root / "contracts" / filename).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def test_claude_adapter_artifacts_match_the_current_core_renderer(tmp_path):
    core = core_root()
    renderer = core / "scripts" / "render_adapter_snapshot.py"
    rendered_dir = tmp_path / "claude"
    subprocess.run(
        [sys.executable, str(renderer), "--target", "claude", "--output-dir", str(rendered_dir)],
        cwd=core,
        check=True,
    )

    artifact_paths = {
        "hplan-core.lock": LOCK_PATH,
        "hplan-capability-matrix.json": MATRIX_PATH,
        "HPLAN_CAPABILITY_MATRIX.md": MARKDOWN_PATH,
        "hplan-core-adapter.json": ADAPTER_PATH,
    }
    for filename, target_path in artifact_paths.items():
        assert target_path.read_bytes() == (rendered_dir / filename).read_bytes()

    core_revision = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=core,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()
    core_contract = load_json(core / "contracts" / "capabilities.json")
    adapter = load_json(ADAPTER_PATH)
    assert re.fullmatch(r"[0-9a-f]{40}", core_revision)
    assert adapter["core_version"] == core_contract["contract_version"]
    assert adapter["core_source_sha256"] == core_source_sha256(core)


def test_claude_adapter_snapshot_has_the_complete_core_contract():
    lock = load_json(LOCK_PATH)
    matrix = load_json(MATRIX_PATH)
    adapter = load_json(ADAPTER_PATH)

    assert lock["target"] == "claude"
    assert lock["files"] == [
        "hplan-core.lock",
        "hplan-capability-matrix.json",
        "HPLAN_CAPABILITY_MATRIX.md",
        "hplan-core-adapter.json",
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
    assert adapter["core_version"] == matrix["contract_version"] == lock["contract_version"]
    assert adapter["core_source_sha256"] == lock["source_sha256"]
    assert adapter["capability_status_source"] == "hplan-capability-matrix.json"
    assert adapter["native_execution_policy"] == "entrypoint-and-smoke-fixture-required"
    assert adapter["non_native_fallback"] == "fallback_artifact"
    assert adapter["external_connector_writes"] == "disabled"


def test_claude_md_declares_the_synced_rule_contract_and_adapter_boundary():
    claude_md = CLAUDE_MD_PATH.read_text(encoding="utf-8")

    assert "hplan Core Contract Sync" in claude_md
    assert "docs/hplan-capability-matrix.json" in claude_md
    assert "adapter-required is not execution permission or external-write permission" in claude_md
    for rule_id in EXPECTED_RULE_IDS:
        assert rule_id in claude_md
