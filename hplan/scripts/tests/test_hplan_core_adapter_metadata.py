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


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


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
