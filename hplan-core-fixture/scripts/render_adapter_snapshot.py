#!/usr/bin/env python3
"""Render a deterministic adapter snapshot from the hplan core contract."""

import argparse
import hashlib
import json
from pathlib import Path

from validate_core import ROOT, load_contracts, validate_contracts


OUTPUT_FILES = ("hplan-core.lock", "hplan-capability-matrix.json", "HPLAN_CAPABILITY_MATRIX.md", "hplan-core-adapter.json")
CONTRACT_SOURCE_FILES = ("rules.json", "capabilities.json", "aliases.json")


def canonical_json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def source_digest(contracts_dir):
    digest = hashlib.sha256()
    for filename in CONTRACT_SOURCE_FILES:
        digest.update(filename.encode("utf-8"))
        digest.update(b"\0")
        digest.update((Path(contracts_dir) / filename).read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_snapshot(target, contracts_dir=ROOT / "contracts"):
    rules, capabilities_doc, aliases_doc = load_contracts(contracts_dir)
    errors = validate_contracts(rules, capabilities_doc, aliases_doc)
    if errors:
        raise ValueError("; ".join(errors))
    capabilities = []
    for capability in sorted(capabilities_doc["capabilities"], key=lambda item: item["capability_id"]):
        target_support = capability["support"][target]
        capabilities.append({
            "capability_id": capability["capability_id"],
            "lifecycle": capability["lifecycle"],
            "canonical_owner": capability["canonical_owner"],
            "support_state": target_support["state"],
            "entrypoint": target_support["entrypoint"],
            "smoke_fixture_id": target_support["smoke_fixture_id"],
            "fallback_artifact": capability["fallback_artifact"],
        })
    return {
        "contract_version": capabilities_doc["contract_version"],
        "target": target,
        "rules": sorted(rules["rules"], key=lambda item: item["rule_id"]),
        "capabilities": capabilities,
        "aliases": sorted(aliases_doc["aliases"], key=lambda item: item["alias_id"]),
    }


def markdown(snapshot):
    lines = [
        "# HPLAN Capability Matrix",
        "",
        f"Contract version: `{snapshot['contract_version']}`",
        f"Target: `{snapshot['target']}`",
        "",
        "| Capability | Lifecycle | Owner | Support | Entrypoint | Smoke fixture | Fallback artifact |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for capability in snapshot["capabilities"]:
        values = (
            capability["capability_id"], capability["lifecycle"], capability["canonical_owner"],
            capability["support_state"], capability["entrypoint"] or "-",
            capability["smoke_fixture_id"] or "-", capability["fallback_artifact"],
        )
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in values) + " |")
    lines.extend(["", "## Compatibility aliases", "", "| Alias | Canonical target | Expiry |", "| --- | --- | --- |"])
    for alias in snapshot["aliases"]:
        lines.append(f"| {alias['alias_id']} | {alias['target']} | {alias['expiry']} |")
    return "\n".join(lines) + "\n"


def render(target, output_dir, contracts_dir=ROOT / "contracts"):
    snapshot = build_snapshot(target, contracts_dir)
    _, capabilities_doc, _ = load_contracts(contracts_dir)
    source_sha256 = source_digest(contracts_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    lock = {
        "contract_version": snapshot["contract_version"],
        "target": target,
        "source_sha256": source_sha256,
        "core_source_sha256": source_sha256,
        "files": list(OUTPUT_FILES),
    }
    adapter = {
        "target": target,
        "core_version": snapshot["contract_version"],
        "core_source_sha256": source_sha256,
        **capabilities_doc["adapter_policy"],
    }
    (output_dir / "hplan-core.lock").write_text(canonical_json(lock), encoding="utf-8")
    (output_dir / "hplan-capability-matrix.json").write_text(canonical_json(snapshot), encoding="utf-8")
    (output_dir / "HPLAN_CAPABILITY_MATRIX.md").write_text(markdown(snapshot), encoding="utf-8")
    (output_dir / "hplan-core-adapter.json").write_text(canonical_json(adapter), encoding="utf-8")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", choices=("claude", "codex"), required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        render(args.target, args.output_dir)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
