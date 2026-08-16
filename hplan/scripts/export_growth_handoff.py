#!/usr/bin/env python3
"""Export an approved hplan Build Gate as an AI PM Handoff Profile v0."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


class ExportError(ValueError):
    """Raised when source records cannot produce a valid handoff."""


def _required_text(record: dict, key: str, label: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ExportError(f"{label} must be a non-empty string")
    return value


def _read_decisions(path: Path) -> list[dict]:
    return [
        json.loads(line)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def build_profile(root: Path) -> dict:
    checkpoint = json.loads(
        (root / "harness" / "build-gate" / "checkpoint.json").read_text(
            encoding="utf-8"
        )
    )
    if checkpoint.get("status") != "approved":
        raise ExportError("checkpoint status must be 'approved'")
    project = _required_text(checkpoint, "project", "project")
    decision_ref = checkpoint.get("decision_ref")
    if (
        not isinstance(decision_ref, str)
        or not decision_ref
        or any(character.isspace() for character in decision_ref)
    ):
        raise ExportError("decision_ref must be an opaque reference token")
    owner = _required_text(checkpoint, "approved_by", "approved_by")
    decisions = _read_decisions(root / "harness" / "decisions.jsonl")
    decision = next(
        (item for item in decisions if item.get("id") == decision_ref),
        None,
    )
    if decision is None:
        raise ExportError(f"decision_ref not found: {decision_ref}")
    if decision.get("project") != project:
        raise ExportError("decision project does not match checkpoint project")
    decision_status = _required_text(decision, "decision", "decision status")
    approved_at_text = _required_text(checkpoint, "approved_at", "approved_at")
    try:
        approved_at = datetime.fromisoformat(approved_at_text)
    except ValueError as exc:
        raise ExportError("approved_at must be an RFC 3339 timestamp") from exc
    if approved_at.utcoffset() is None:
        raise ExportError("approved_at must include a UTC offset")

    return {
        "profile_version": "0.1",
        "project_id": project,
        "source_system": "hplan",
        "source_record_ref": f"hplan://checkpoint/{decision_ref}",
        "handoff_kind": "build_gate_to_growth",
        "status": decision_status,
        "evidence_refs": [],
        "metric_refs": [],
        "owner": owner,
        "review_at": approved_at.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Export an approved hplan Build Gate as AI PM Handoff Profile v0."
    )
    parser.add_argument("--root", default=".", help="Project root (defaults to cwd)")
    parser.add_argument("--output", help="Write the profile to this local JSON file")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output file")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        profile = build_profile(Path(args.root).resolve())
    except ExportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    rendered = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        output_path = Path(args.output)
        if output_path.exists() and not args.force:
            print("error: refusing to overwrite existing output without --force", file=sys.stderr)
            return 1
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
