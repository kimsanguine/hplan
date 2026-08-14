import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
RUNTIME_CORE = REPO_ROOT / "runtime" / "hplan-core"
CORE_ARTIFACTS = {
    "hplan-core.lock",
    "hplan-capability-matrix.json",
    "HPLAN_CAPABILITY_MATRIX.md",
    "hplan-core-adapter.json",
}


def load_validator_module():
    module_path = REPO_ROOT / "validate_plugins.py"
    spec = importlib.util.spec_from_file_location("hplan_validate_plugins", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_public_repository_excludes_private_document_and_archive_directories():
    """Public source must not track or package the local/private content roots."""
    assert not (REPO_ROOT / "docs").exists()
    assert not (REPO_ROOT / ".archive").exists()

    ignore_rules = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "/docs/" in ignore_rules
    assert "/.archive/" in ignore_rules

    policy = (REPO_ROOT / "PUBLIC_SURFACE.md").read_text(encoding="utf-8")
    assert "`docs`" in policy
    assert "`.archive`" in policy
    assert "runtime/hplan-core/" in policy

    workflow = (REPO_ROOT / ".github" / "workflows" / "publish-hplan-package.yml").read_text(encoding="utf-8")
    assert '"runtime/hplan-core/**"' in workflow
    assert '"docs/**"' not in workflow
    assert '".archive/**"' not in workflow


def test_runtime_core_snapshot_is_the_only_public_core_artifact_location():
    assert {path.name for path in RUNTIME_CORE.iterdir() if path.is_file()} == CORE_ARTIFACTS
    assert (RUNTIME_CORE / "hplan-core.lock").is_file()


def test_public_surface_validator_rejects_nested_docs_and_archive_directories(tmp_path):
    validator = load_validator_module()
    (tmp_path / ".hplan-core-snapshot" / "docs").mkdir(parents=True)
    (tmp_path / "nested" / ".archive").mkdir(parents=True)

    assert validator.public_surface_violations(tmp_path) == {
        ".hplan-core-snapshot/docs",
        "nested/.archive",
    }
