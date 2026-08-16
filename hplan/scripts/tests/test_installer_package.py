import json
import os
import stat
import subprocess
import tarfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-installer-package.sh"


def _fake_claude(tmp_path):
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable = bin_dir / "claude"
    executable.write_text("#!/usr/bin/env bash\necho 'claude 1.0.0'\n", encoding="utf-8")
    executable.chmod(executable.stat().st_mode | stat.S_IXUSR)
    return bin_dir


def test_installer_package_contains_pinned_core_fixture_and_doctor_runs_after_extract(tmp_path):
    subprocess.run(
        ["bash", str(BUILD_SCRIPT)],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    package = REPO_ROOT / "dist" / "hplan-package.tar.gz"
    version = json.loads((REPO_ROOT / "dist" / "version.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (REPO_ROOT / "hplan" / ".claude-plugin" / "plugin.json").read_text(
            encoding="utf-8"
        )
    )
    assert version["version"] == manifest["version"]
    with tarfile.open(package, "r:gz") as archive:
        archive.extractall(tmp_path, filter="data")

    installed = tmp_path / "hplan"
    assert (installed / "hplan-core-fixture" / "contracts" / "capabilities.json").is_file()
    assert (installed / "hplan-core-fixture" / "scripts" / "render_adapter_snapshot.py").is_file()
    assert (installed / "runtime" / "hplan-core" / "hplan-core.lock").is_file()
    assert not (installed / "docs").exists()
    assert not (installed / ".archive").exists()
    assert not (tmp_path / "hplan-core").exists()

    profile = tmp_path / ".zshrc"
    plugin_args = " ".join(f"--plugin-dir {installed / name}" for name in ("hplan", "discover", "architect", "deliver", "operate"))
    profile.write_text(f"alias claude-hplan='claude {plugin_args}'\n", encoding="utf-8")
    env = {
        **os.environ,
        "PATH": f"{_fake_claude(tmp_path)}:{os.environ['PATH']}",
        "HPLAN_PROFILE": str(profile),
    }
    result = subprocess.run(
        ["bash", str(installed / "scripts" / "hplan-doctor.sh"), "--root", str(installed)],
        cwd=tmp_path,
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "[정상] claude-hplan launcher" in result.stdout
    assert "[정상] hplan-core snapshot" in result.stdout
    assert "[강사 호출]" not in result.stdout
