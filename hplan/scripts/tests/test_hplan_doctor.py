import os
import shutil
import stat
import subprocess
import json
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
DOCTOR = REPO_ROOT / "scripts" / "hplan-doctor.sh"
ARTIFACTS = (
    "hplan-core.lock",
    "docs/hplan-capability-matrix.json",
    "docs/HPLAN_CAPABILITY_MATRIX.md",
    "docs/hplan-core-adapter.json",
)
PLUGIN_DIRS = ("hplan", "discover", "architect", "deliver", "operate")


def _copy_snapshot(tmp_path):
    root = tmp_path / "hplan"
    for relative_path in ARTIFACTS:
        source = REPO_ROOT / relative_path
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    for plugin_dir in PLUGIN_DIRS:
        (root / plugin_dir).mkdir()
    return root


def _fake_claude(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable = bin_dir / "claude"
    executable.write_text("#!/usr/bin/env bash\necho 'claude 1.0.0'\n", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    return bin_dir


def _launcher_profile(tmp_path, root):
    profile = tmp_path / ".zshrc"
    profile.write_text(
        "alias claude-hplan='claude "
        f"--plugin-dir {root}/hplan "
        f"--plugin-dir {root}/discover "
        f"--plugin-dir {root}/architect "
        f"--plugin-dir {root}/deliver "
        f"--plugin-dir {root}/operate'\n",
        encoding="utf-8",
    )
    return profile


def _run_doctor(root, bin_dir, profile=None):
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
    if profile:
        env["HPLAN_PROFILE"] = str(profile)
    return subprocess.run(
        ["bash", str(DOCTOR), "--root", str(root)],
        text=True,
        capture_output=True,
        env=env,
        check=False,
    )


def test_doctor_reports_normal_for_a_complete_read_only_snapshot(tmp_path):
    root = _copy_snapshot(tmp_path)
    before = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}

    result = _run_doctor(root, _fake_claude(tmp_path), _launcher_profile(tmp_path, root))

    assert result.returncode == 0
    assert "[정상] Claude Code" in result.stdout
    assert "[정상] claude-hplan launcher" in result.stdout
    assert "[정상] Python" in result.stdout
    assert "[정상] hplan-core snapshot" in result.stdout
    assert "읽기 전용 점검" in result.stdout
    after = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
    assert after == before


def test_doctor_escalates_when_a_required_core_artifact_is_missing(tmp_path):
    root = _copy_snapshot(tmp_path)
    (root / "docs" / "hplan-core-adapter.json").unlink()

    result = _run_doctor(root, _fake_claude(tmp_path), _launcher_profile(tmp_path, root))

    assert result.returncode == 1
    assert "[강사 호출] hplan-core snapshot" in result.stdout
    assert "다시 설치" in result.stdout


def test_doctor_marks_missing_quickstart_launcher_as_recoverable(tmp_path):
    root = _copy_snapshot(tmp_path)

    result = _run_doctor(root, _fake_claude(tmp_path))

    assert result.returncode == 0
    assert "[자동 복구 가능] claude-hplan launcher" in result.stdout
    assert "setup.sh" in result.stdout


def test_doctor_marks_missing_launcher_plugin_directory_as_recoverable(tmp_path):
    root = _copy_snapshot(tmp_path)
    (root / "operate").rmdir()

    result = _run_doctor(root, _fake_claude(tmp_path), _launcher_profile(tmp_path, root))

    assert result.returncode == 0
    assert "[자동 복구 가능] claude-hplan launcher" in result.stdout
    assert "operate" in result.stdout


@pytest.mark.parametrize(
    ("relative_path", "mutate"),
    [
        ("hplan-core.lock", lambda value: value.update(source_sha256="z" * 64)),
        (
            "docs/hplan-capability-matrix.json",
            lambda value: value["capabilities"].__setitem__(1, value["capabilities"][0]),
        ),
        ("docs/hplan-capability-matrix.json", lambda value: value.update(rules=[])),
        ("docs/hplan-capability-matrix.json", lambda value: value.update(capabilities={})),
        (
            "docs/hplan-capability-matrix.json",
            lambda value: value["rules"][0].update(rule_id="invented-rule"),
        ),
        (
            "docs/hplan-capability-matrix.json",
            lambda value: value["capabilities"][0].update(
                capability_id="invented-capability",
                entrypoint="capability:invented-capability",
                smoke_fixture_id="smoke.invented-capability",
            ),
        ),
        ("docs/hplan-capability-matrix.json", lambda value: value["capabilities"][0].update(lifecycle="retired")),
        ("docs/hplan-capability-matrix.json", lambda value: value["aliases"][0].update(target="invented-target")),
        ("docs/hplan-capability-matrix.json", lambda value: value["aliases"][0].update(expiry="2099-01-01")),
    ],
)
def test_doctor_escalates_for_declared_contract_integrity_mutations(tmp_path, relative_path, mutate):
    root = _copy_snapshot(tmp_path)
    target = root / relative_path
    value = json.loads(target.read_text(encoding="utf-8"))
    mutate(value)
    target.write_text(json.dumps(value), encoding="utf-8")

    result = _run_doctor(root, _fake_claude(tmp_path), _launcher_profile(tmp_path, root))

    assert result.returncode == 1
    assert "[강사 호출] hplan-core snapshot" in result.stdout
    assert "무결성" in result.stdout
