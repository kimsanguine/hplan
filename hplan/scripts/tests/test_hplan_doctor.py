import os
import shutil
import stat
import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DOCTOR = REPO_ROOT / "scripts" / "hplan-doctor.sh"
ARTIFACTS = (
    "hplan-core.lock",
    "docs/hplan-capability-matrix.json",
    "docs/HPLAN_CAPABILITY_MATRIX.md",
    "docs/hplan-core-adapter.json",
)


def _copy_snapshot(tmp_path):
    root = tmp_path / "hplan"
    for relative_path in ARTIFACTS:
        source = REPO_ROOT / relative_path
        target = root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return root


def _fake_claude(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable = bin_dir / "claude"
    executable.write_text("#!/usr/bin/env bash\necho 'claude 1.0.0'\n", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    return bin_dir


def _run_doctor(root, bin_dir):
    env = os.environ.copy()
    env["PATH"] = f"{bin_dir}:{env['PATH']}"
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

    result = _run_doctor(root, _fake_claude(tmp_path))

    assert result.returncode == 0
    assert "[정상] Claude Code" in result.stdout
    assert "[정상] Python" in result.stdout
    assert "[정상] hplan-core snapshot" in result.stdout
    assert "읽기 전용 점검" in result.stdout
    after = {path.relative_to(root): path.read_bytes() for path in root.rglob("*") if path.is_file()}
    assert after == before


def test_doctor_escalates_when_a_required_core_artifact_is_missing(tmp_path):
    root = _copy_snapshot(tmp_path)
    (root / "docs" / "hplan-core-adapter.json").unlink()

    result = _run_doctor(root, _fake_claude(tmp_path))

    assert result.returncode == 1
    assert "[강사 호출] hplan-core snapshot" in result.stdout
    assert "다시 설치" in result.stdout
