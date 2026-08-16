#!/usr/bin/env python3
"""Export an approved hplan Build Gate as an AI PM Handoff Profile v0."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import tempfile


EXPORT_ROOT = Path("harness") / "exports" / "ai-pm"
FORWARD_DECISIONS = {"build", "CONDITIONAL_GO"}
RFC3339_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?P<offset>Z|[+-]\d{2}:\d{2})?$"
)


class ExportError(ValueError):
    """Raised when source records cannot produce a valid handoff."""


def _required_text(record: dict, key: str, label: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ExportError(f"{label} must be a non-empty string")
    return value


def _read_json_object(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ExportError(f"{label} is malformed JSON") from exc
    except UnicodeDecodeError as exc:
        raise ExportError(f"{label} is not valid UTF-8") from exc
    except OSError as exc:
        raise ExportError(f"unable to read {label}: {exc.strerror or exc}") from exc
    if not isinstance(value, dict):
        raise ExportError(f"{label} must contain a JSON object")
    return value


def _read_decisions(path: Path) -> list[dict]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError as exc:
        raise ExportError("decisions.jsonl is not valid UTF-8") from exc
    except OSError as exc:
        raise ExportError(
            f"unable to read decisions.jsonl: {exc.strerror or exc}"
        ) from exc

    decisions = []
    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ExportError(
                f"decisions.jsonl line {line_number} is malformed JSON"
            ) from exc
        if not isinstance(value, dict):
            raise ExportError(f"decisions.jsonl line {line_number} must be a JSON object")
        decisions.append(value)
    return decisions


def build_profile(root: Path) -> dict:
    checkpoint = _read_json_object(
        root / "harness" / "build-gate" / "checkpoint.json",
        "checkpoint.json",
    )
    if checkpoint.get("status") != "approved":
        raise ExportError("checkpoint status must be 'approved'")
    if checkpoint.get("gate") != "build":
        raise ExportError("checkpoint gate must be 'build'")
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
    if decision.get("gate") != "build":
        raise ExportError("referenced decision gate must be 'build'")
    checkpoint_decision = _required_text(checkpoint, "decision", "checkpoint decision")
    decision_status = _required_text(decision, "decision", "decision status")
    if checkpoint_decision not in FORWARD_DECISIONS or decision_status not in FORWARD_DECISIONS:
        raise ExportError("decision must be 'build' or 'CONDITIONAL_GO'")
    if checkpoint_decision != decision_status:
        raise ExportError("checkpoint decision does not match referenced decision")
    approved_at_text = _required_text(checkpoint, "approved_at", "approved_at")
    match = RFC3339_PATTERN.fullmatch(approved_at_text)
    if match is None:
        raise ExportError("approved_at must be an RFC 3339 timestamp")
    if match.group("offset") is None:
        raise ExportError("approved_at must include a UTC offset")
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


def _resolve_output_path(root: Path, value: str) -> Path:
    requested = Path(value)
    if requested.is_absolute():
        raise ExportError("output must be a relative path")
    if ".." in requested.parts:
        raise ExportError("output path traversal is not allowed")

    relative_output = EXPORT_ROOT / requested
    if relative_output == EXPORT_ROOT:
        raise ExportError("output must name a file under harness/exports/ai-pm")

    current = root
    for part in relative_output.parts:
        current = current / part
        if current.is_symlink():
            raise ExportError("output path must not contain symlinks")

    export_root = (root / EXPORT_ROOT).resolve(strict=False)
    output_path = (root / relative_output).resolve(strict=False)
    if not output_path.is_relative_to(export_root):
        raise ExportError("output must stay under harness/exports/ai-pm")

    source_paths = {
        (root / "harness" / "build-gate" / "checkpoint.json").resolve(),
        (root / "harness" / "decisions.jsonl").resolve(),
    }
    if output_path in source_paths:
        raise ExportError("output must not target a source ledger")
    return output_path


def _write_output(path: Path, content: str, force: bool) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not force:
        try:
            with path.open("x", encoding="utf-8") as handle:
                handle.write(content)
        except FileExistsError as exc:
            raise ExportError("refusing to overwrite existing output without --force") from exc
        return

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
            temporary_path = Path(handle.name)
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


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
        root = Path(args.root).resolve()
        profile = build_profile(root)
        output_path = _resolve_output_path(root, args.output) if args.output else None
        rendered = json.dumps(profile, ensure_ascii=False, indent=2) + "\n"
        if output_path is not None:
            _write_output(output_path, rendered, args.force)
    except ExportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if output_path is None:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
