import json
from pathlib import Path
import subprocess
import sys


SCRIPT = Path(__file__).parent.parent / "export_growth_handoff.py"


def _write_sources(
    root: Path,
    *,
    checkpoint_status: str = "approved",
    checkpoint_project: str = "project-alpha",
    decision_ref: str = "dec-001",
    logged_decision_ref: str | None = None,
    decision_project: str | None = None,
    checkpoint_gate: str = "build",
    checkpoint_decision: str = "CONDITIONAL_GO",
    decision_gate: str = "build",
    decision_status: str = "CONDITIONAL_GO",
    approved_by: str = "portfolio-owner",
    approved_at: str = "2026-08-16T18:30:00+09:00",
) -> None:
    logged_decision_ref = decision_ref if logged_decision_ref is None else logged_decision_ref
    decision_project = checkpoint_project if decision_project is None else decision_project
    checkpoint_path = root / "harness" / "build-gate" / "checkpoint.json"
    checkpoint_path.parent.mkdir(parents=True)
    checkpoint_path.write_text(
        json.dumps(
            {
                "status": checkpoint_status,
                "project": checkpoint_project,
                "gate": checkpoint_gate,
                "decision": checkpoint_decision,
                "decision_ref": decision_ref,
                "approved_at": approved_at,
                "approved_by": approved_by,
            }
        ),
        encoding="utf-8",
    )
    decisions_path = root / "harness" / "decisions.jsonl"
    decisions_path.parent.mkdir(parents=True, exist_ok=True)
    decisions_path.write_text(
        json.dumps(
            {
                "id": "dec-older",
                "project": checkpoint_project,
                "gate": "build",
                "decision": "hold",
            }
        )
        + "\n"
        + json.dumps(
            {
                "id": logged_decision_ref,
                "project": decision_project,
                "gate": decision_gate,
                "decision": decision_status,
            }
        )
        + "\n",
        encoding="utf-8",
    )


def _run(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), *args],
        text=True,
        capture_output=True,
        check=False,
        cwd=root,
    )


def _source_bytes(root: Path) -> dict[Path, bytes]:
    paths = (
        root / "harness" / "build-gate" / "checkpoint.json",
        root / "harness" / "decisions.jsonl",
    )
    return {path: path.read_bytes() for path in paths}


def test_approved_checkpoint_exports_profile_v0_to_stdout(tmp_path):
    _write_sources(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert json.loads(result.stdout) == {
        "profile_version": "0.1",
        "project_id": "project-alpha",
        "source_system": "hplan",
        "source_record_ref": "hplan://checkpoint/dec-001",
        "handoff_kind": "build_gate_to_growth",
        "status": "CONDITIONAL_GO",
        "evidence_refs": [],
        "metric_refs": [],
        "owner": "portfolio-owner",
        "review_at": "2026-08-16T09:30:00Z",
    }


def test_non_approved_checkpoint_is_rejected(tmp_path):
    _write_sources(tmp_path, checkpoint_status="pending")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "checkpoint status must be 'approved'" in result.stderr


def test_dangling_decision_ref_is_rejected(tmp_path):
    _write_sources(
        tmp_path,
        decision_ref="dec-missing",
        logged_decision_ref="dec-other",
    )

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "decision_ref not found: dec-missing" in result.stderr


def test_decision_project_mismatch_is_rejected(tmp_path):
    _write_sources(tmp_path, decision_project="project-beta")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "decision project does not match checkpoint project" in result.stderr


def test_checkpoint_must_be_for_build_gate(tmp_path):
    _write_sources(tmp_path, checkpoint_gate="product")
    before = _source_bytes(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "checkpoint gate must be 'build'" in result.stderr
    assert _source_bytes(tmp_path) == before


def test_referenced_decision_must_be_for_build_gate(tmp_path):
    _write_sources(tmp_path, decision_gate="evidence")
    before = _source_bytes(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "referenced decision gate must be 'build'" in result.stderr
    assert _source_bytes(tmp_path) == before


def test_noncanonical_or_non_forward_checkpoint_decisions_are_rejected(tmp_path):
    for status in ("hold", "interview", "pivot", "build"):
        root = tmp_path / status
        _write_sources(root, checkpoint_decision=status, decision_status=status)
        before = _source_bytes(root)

        result = _run(root)

        assert result.returncode == 1
        assert result.stdout == ""
        assert "checkpoint decision must be 'GO' or 'CONDITIONAL_GO'" in result.stderr
        assert _source_bytes(root) == before


def test_checkpoint_and_referenced_decision_must_agree(tmp_path):
    cases = (
        ("GO", "CONDITIONAL_GO"),
        ("CONDITIONAL_GO", "build"),
    )
    for checkpoint_decision, decision_status in cases:
        root = tmp_path / f"{checkpoint_decision}-{decision_status}"
        _write_sources(
            root,
            checkpoint_decision=checkpoint_decision,
            decision_status=decision_status,
        )
        before = _source_bytes(root)

        result = _run(root)

        assert result.returncode == 1
        assert result.stdout == ""
        assert "checkpoint decision does not map to referenced decision" in result.stderr
        assert _source_bytes(root) == before


def test_build_decision_is_forward_capable(tmp_path):
    _write_sources(tmp_path, checkpoint_decision="GO", decision_status="build")

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "build"


def test_stdout_export_does_not_mutate_source_files(tmp_path):
    _write_sources(tmp_path)
    checkpoint_path = tmp_path / "harness" / "build-gate" / "checkpoint.json"
    decisions_path = tmp_path / "harness" / "decisions.jsonl"
    before = {
        checkpoint_path: checkpoint_path.read_bytes(),
        decisions_path: decisions_path.read_bytes(),
    }

    result = _run(tmp_path)

    assert result.returncode == 0, result.stderr
    assert {path: path.read_bytes() for path in before} == before
    assert sorted(path.relative_to(tmp_path) for path in tmp_path.rglob("*") if path.is_file()) == [
        Path("harness/build-gate/checkpoint.json"),
        Path("harness/decisions.jsonl"),
    ]


def test_named_output_file_is_written_after_source_validation(tmp_path):
    _write_sources(tmp_path)
    output_path = tmp_path / "harness" / "exports" / "ai-pm" / "growth-handoff.json"

    result = _run(tmp_path, "--output", "growth-handoff.json")

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert json.loads(output_path.read_text(encoding="utf-8"))["status"] == "CONDITIONAL_GO"


def test_existing_output_is_not_overwritten_without_force(tmp_path):
    _write_sources(tmp_path)
    output_path = tmp_path / "harness" / "exports" / "ai-pm" / "growth-handoff.json"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("keep-me\n", encoding="utf-8")

    result = _run(tmp_path, "--output", "growth-handoff.json")

    assert result.returncode == 1
    assert result.stdout == ""
    assert "refusing to overwrite existing output" in result.stderr
    assert output_path.read_text(encoding="utf-8") == "keep-me\n"


def test_invalid_source_does_not_create_named_output(tmp_path):
    _write_sources(tmp_path, checkpoint_status="pending")
    output_path = tmp_path / "harness" / "exports" / "ai-pm" / "growth-handoff.json"

    result = _run(tmp_path, "--output", "growth-handoff.json")

    assert result.returncode == 1
    assert "checkpoint status must be 'approved'" in result.stderr
    assert not output_path.exists()
    assert not output_path.parent.exists()


def test_force_allows_replacing_existing_output(tmp_path):
    _write_sources(tmp_path)
    output_path = tmp_path / "harness" / "exports" / "ai-pm" / "growth-handoff.json"
    output_path.parent.mkdir(parents=True)
    output_path.write_text("replace-me\n", encoding="utf-8")

    result = _run(tmp_path, "--output", "growth-handoff.json", "--force")

    assert result.returncode == 0, result.stderr
    assert json.loads(output_path.read_text(encoding="utf-8"))["project_id"] == "project-alpha"


def test_directory_output_error_is_sanitized(tmp_path):
    _write_sources(tmp_path)
    before = _source_bytes(tmp_path)
    output_path = tmp_path / "harness" / "exports" / "ai-pm" / "existing-dir"
    output_path.mkdir(parents=True)

    result = _run(tmp_path, "--output", "existing-dir", "--force")

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.startswith("error: unable to write output:")
    assert "Traceback" not in result.stderr
    assert output_path.is_dir()
    assert list(output_path.parent.glob(".existing-dir.*.tmp")) == []
    assert _source_bytes(tmp_path) == before


def test_non_directory_output_parent_error_is_sanitized(tmp_path):
    _write_sources(tmp_path)
    before = _source_bytes(tmp_path)
    blocked_parent = tmp_path / "harness" / "exports" / "ai-pm" / "blocked"
    blocked_parent.parent.mkdir(parents=True)
    blocked_parent.write_text("keep-me\n", encoding="utf-8")

    result = _run(tmp_path, "--output", "blocked/profile.json", "--force")

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr.startswith("error: unable to write output:")
    assert "Traceback" not in result.stderr
    assert blocked_parent.read_text(encoding="utf-8") == "keep-me\n"
    assert _source_bytes(tmp_path) == before


def test_absolute_output_is_rejected_before_parent_creation(tmp_path):
    root = tmp_path / "root"
    _write_sources(root)
    before = _source_bytes(root)
    output_path = tmp_path / "outside" / "growth-handoff.json"

    result = _run(root, "--output", str(output_path), "--force")

    assert result.returncode == 1
    assert result.stdout == ""
    assert "output must be a relative path" in result.stderr
    assert not output_path.parent.exists()
    assert _source_bytes(root) == before


def test_traversal_output_is_rejected_before_parent_creation(tmp_path):
    root = tmp_path / "root"
    _write_sources(root)
    before = _source_bytes(root)
    escaped_path = tmp_path / "escaped" / "growth-handoff.json"

    result = _run(root, "--output", "../escaped/growth-handoff.json", "--force")

    assert result.returncode == 1
    assert result.stdout == ""
    assert "output path traversal is not allowed" in result.stderr
    assert not escaped_path.parent.exists()
    assert _source_bytes(root) == before


def test_source_ledgers_are_never_valid_output_targets(tmp_path):
    for name, source_path in (
        ("checkpoint", Path("harness/build-gate/checkpoint.json")),
        ("decisions", Path("harness/decisions.jsonl")),
    ):
        root = tmp_path / name
        _write_sources(root)
        before = _source_bytes(root)

        result = _run(root, "--output", str(root / source_path), "--force")

        assert result.returncode == 1
        assert result.stdout == ""
        assert _source_bytes(root) == before


def test_symlink_output_to_decision_ledger_is_rejected(tmp_path):
    _write_sources(tmp_path)
    before = _source_bytes(tmp_path)
    export_root = tmp_path / "harness" / "exports" / "ai-pm"
    export_root.mkdir(parents=True)
    output_path = export_root / "growth-handoff.json"
    output_path.symlink_to(tmp_path / "harness" / "decisions.jsonl")

    result = _run(tmp_path, "--output", "growth-handoff.json", "--force")

    assert result.returncode == 1
    assert result.stdout == ""
    assert "output path must not contain symlinks" in result.stderr
    assert output_path.is_symlink()
    assert _source_bytes(tmp_path) == before


def test_blank_profile_fields_are_rejected(tmp_path):
    cases = (
        ({"checkpoint_project": ""}, "project must be a non-empty string"),
        ({"decision_ref": " "}, "decision_ref must be an opaque reference token"),
        ({"approved_by": "  "}, "approved_by must be a non-empty string"),
        ({"decision_status": ""}, "decision status must be a non-empty string"),
    )

    for index, (source_overrides, expected_error) in enumerate(cases):
        root = tmp_path / str(index)
        _write_sources(root, **source_overrides)

        result = _run(root)

        assert result.returncode == 1
        assert result.stdout == ""
        assert expected_error in result.stderr


def test_approved_at_without_timezone_is_rejected(tmp_path):
    _write_sources(tmp_path, approved_at="2026-08-16T09:30:00")

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "approved_at must include a UTC offset" in result.stderr


def test_non_rfc3339_timestamp_separator_is_rejected(tmp_path):
    _write_sources(tmp_path, approved_at="2026-08-16X18:30:00+09:00")
    before = _source_bytes(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert "approved_at must be an RFC 3339 timestamp" in result.stderr
    assert _source_bytes(tmp_path) == before


def test_malformed_checkpoint_json_has_sanitized_error(tmp_path):
    _write_sources(tmp_path)
    checkpoint_path = tmp_path / "harness" / "build-gate" / "checkpoint.json"
    checkpoint_path.write_bytes(b"{\n")
    before = _source_bytes(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "error: checkpoint.json is malformed JSON\n"
    assert "Traceback" not in result.stderr
    assert _source_bytes(tmp_path) == before


def test_malformed_decision_jsonl_has_sanitized_error(tmp_path):
    _write_sources(tmp_path)
    decisions_path = tmp_path / "harness" / "decisions.jsonl"
    decisions_path.write_text("not-json\n", encoding="utf-8")
    before = _source_bytes(tmp_path)

    result = _run(tmp_path)

    assert result.returncode == 1
    assert result.stdout == ""
    assert result.stderr == "error: decisions.jsonl line 1 is malformed JSON\n"
    assert "Traceback" not in result.stderr
    assert _source_bytes(tmp_path) == before
