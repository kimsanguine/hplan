#!/usr/bin/env python3
"""Validate the versioned, platform-neutral hplan core contract."""

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_RULE_IDS = {
    "think-before-coding", "simplicity-first", "surgical-changes",
    "goal-driven-execution", "models-for-judgment-only", "tests-verify-intent",
    "checkpoint-after-significant-step", "fail-loud", "agent-scope-declaration",
}
EXPECTED_CAPABILITY_IDS = {
    "agent-setup", "ask-team", "assumptions", "brainstorm", "build-loop",
    "cogs-sentinel", "conductor", "cost-sim", "customer-reach", "decision-log",
    "design-token", "evidence-rubric", "exclusions", "handoff", "hitl", "incident",
    "interview-synthesis", "memory-arch", "metrics-design", "opp-tree", "ops-review",
    "orchestration", "ost", "pm-engine", "portfolio", "prd", "qa-checklist",
    "reliability", "respect", "socratic-question", "sprint", "strategy", "ticket-bridge",
    "ui-validate",
}
EXPECTED_ALIAS_IDS = {"roadmap", "router", "stakeholder-update"}
TARGETS = ("claude", "codex")
SUPPORT_STATES = {"native", "adapter-required", "unavailable"}
REQUIRED_ADAPTER_POLICY = {
    "capability_status_source": "hplan-capability-matrix.json",
    "native_execution_policy": "entrypoint-and-smoke-fixture-required",
    "non_native_fallback": "fallback_artifact",
    "external_connector_writes": "disabled",
}
FORBIDDEN_PLATFORM_TOKENS = (
    "Claude" + " Code", "Codex" + " tool",
    "B" + "ash", "R" + "ead", "W" + "rite", "E" + "dit", "M" + "ultiEdit",
    "G" + "lob", "G" + "rep", "T" + "ask", "Web" + "Fetch", "Web" + "Search",
    "Todo" + "W" + "rite", "Notebook" + "E" + "dit", "Exit" + "PlanMode", "S" + "kill",
    "Ask" + "User" + "Question",
    "functions" + "." + "exec", "exec" + "_" + "command", "write" + "_" + "stdin",
    "view" + "_" + "image", "apply" + "_" + "patch", "read" + "_" + "file",
    "write" + "_" + "file", "web" + "_" + "search", "web" + "_" + "fetch",
    "$" + "ARGUMENTS", "allowed" + "-" + "tools",
    "context" + ":" + " fork",
    "Pre" + "ToolUse", "Post" + "ToolUse", "Session" + "Start", "Session" + "End",
    "User" + "PromptSubmit", "Permission" + "Request", "Subagent" + "Stop",
    "/" + "Users/", "/" + "private/", "/" + "home/", "~" + "/",
)
STRUCTURAL_DECLARATIONS = (
    ("adapter tool declaration", re.compile(r"(?im)^\s*" + "allowed" + r"-" + "tools" + r"\s*:")),
    ("fork context declaration", re.compile(r"(?im)^\s*" + "context" + r"\s*:" + r"\s*" + "fork" + r"\b")),
    ("MCP declaration", re.compile(r"\b" + "mcp" + r"__" + r"[A-Za-z0-9_]+")),
)


def load_contracts(contract_dir):
    contract_dir = Path(contract_dir)
    return tuple(
        json.loads((contract_dir / filename).read_text(encoding="utf-8"))
        for filename in ("rules.json", "capabilities.json", "aliases.json")
    )


def validate_platform_neutrality(contracts_dir, scripts_dir):
    """Reject platform-specific integration tokens in core data and code."""
    errors = []
    paths = sorted(Path(contracts_dir).rglob("*.json")) + sorted(Path(scripts_dir).rglob("*.py"))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_PLATFORM_TOKENS:
            is_path_token = token.startswith(("/", "~"))
            starts_with_word = token[0].isalnum() or token[0] == "_"
            contains_token = token in text if is_path_token or not starts_with_word else bool(re.search(r"\b" + re.escape(token) + r"\b", text))
            if contains_token:
                errors.append(f"{path}: platform-specific token {token!r} is forbidden")
        for label, pattern in STRUCTURAL_DECLARATIONS:
            if pattern.search(text):
                errors.append(f"{path}: structural declaration {label} is forbidden")
    return errors


def validate_input_directory(path, label, suffix):
    path = Path(path)
    if not path.exists():
        return f"--{label}-dir must name an existing directory: {path}"
    if not path.is_dir():
        return f"--{label}-dir must name a directory, not a file: {path}"
    if not any(path.rglob(suffix)):
        return f"--{label}-dir directory must contain at least one {suffix} scan file: {path}"
    return None


def _ids(entries, field):
    return [entry.get(field) for entry in entries if isinstance(entry, dict)]


def _require_fields(entry, fields, label, errors):
    for field in fields:
        if field not in entry:
            errors.append(f"{label} is missing required field {field}")


def validate_contracts(rules_doc, capabilities_doc, aliases_doc, today=None):
    errors = []
    today = today or dt.date.today()
    rules = rules_doc.get("rules", []) if isinstance(rules_doc, dict) else []
    capabilities = capabilities_doc.get("capabilities", []) if isinstance(capabilities_doc, dict) else []
    aliases = aliases_doc.get("aliases", []) if isinstance(aliases_doc, dict) else []

    adapter_policy = capabilities_doc.get("adapter_policy") if isinstance(capabilities_doc, dict) else None
    if adapter_policy != REQUIRED_ADAPTER_POLICY:
        errors.append("adapter_policy must contain the required core-driven execution and fallback policy")

    rule_ids = _ids(rules, "rule_id")
    capability_ids = _ids(capabilities, "capability_id")
    alias_ids = _ids(aliases, "alias_id")
    if set(rule_ids) != EXPECTED_RULE_IDS or len(rule_ids) != len(EXPECTED_RULE_IDS):
        errors.append("rule_id set must contain exactly the 9 canonical behavioral rules")
    if set(capability_ids) != EXPECTED_CAPABILITY_IDS or len(capability_ids) != len(EXPECTED_CAPABILITY_IDS):
        errors.append("capability_id set must contain exactly the 34 canonical capabilities")
    if set(alias_ids) != EXPECTED_ALIAS_IDS or len(alias_ids) != len(EXPECTED_ALIAS_IDS):
        errors.append("alias_id set must contain exactly the 3 compatibility aliases")

    for rule in rules:
        if not isinstance(rule, dict):
            errors.append("rule entry must be an object")
            continue
        _require_fields(rule, ("rule_id", "title", "requirement"), "rule", errors)

    for capability in capabilities:
        if not isinstance(capability, dict):
            errors.append("capability entry must be an object")
            continue
        capability_id = capability.get("capability_id", "<unknown>")
        _require_fields(
            capability,
            ("capability_id", "lifecycle", "canonical_owner", "support", "fallback_artifact"),
            f"capability {capability_id}", errors,
        )
        support = capability.get("support")
        if not isinstance(support, dict):
            errors.append(f"capability {capability_id} support must be an object")
            continue
        if set(support) != set(TARGETS):
            errors.append(f"capability {capability_id} must declare support for both targets")
        for target in TARGETS:
            target_support = support.get(target)
            if not isinstance(target_support, dict):
                errors.append(f"capability {capability_id} {target} support must be an object")
                continue
            _require_fields(target_support, ("state", "entrypoint", "smoke_fixture_id"), f"capability {capability_id} {target} support", errors)
            state = target_support.get("state")
            if state not in SUPPORT_STATES:
                errors.append(f"capability {capability_id} {target} has invalid support state {state!r}")
            if state == "native" and (not target_support.get("entrypoint") or not target_support.get("smoke_fixture_id")):
                errors.append(f"capability {capability_id} {target} native support requires entrypoint and smoke_fixture_id")

    canonical_ids = set(capability_ids)
    alias_map = {}
    for alias in aliases:
        if not isinstance(alias, dict):
            errors.append("alias entry must be an object")
            continue
        alias_id = alias.get("alias_id", "<unknown>")
        _require_fields(alias, ("alias_id", "target", "expiry"), f"alias {alias_id}", errors)
        target = alias.get("target")
        alias_map[alias_id] = target
        if target not in canonical_ids:
            errors.append(f"alias {alias_id} target must be a canonical capability")
        try:
            expiry = dt.date.fromisoformat(alias.get("expiry", ""))
            if expiry < today:
                errors.append(f"alias {alias_id} expiry has passed")
        except (TypeError, ValueError):
            errors.append(f"alias {alias_id} expiry must be an ISO date")

    for alias_id in alias_map:
        seen = set()
        cursor = alias_id
        while cursor in alias_map:
            if cursor in seen:
                errors.append(f"alias cycle detected at {cursor}")
                break
            seen.add(cursor)
            cursor = alias_map[cursor]
    return errors


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=(
            "The neutrality check scans complete literal tokens in contract JSON and Python source. "
            "It does not reconstruct runtime-created string fragments; that is outside the literal prose validator scope."
        ),
    )
    parser.add_argument("--contracts-dir", type=Path, default=ROOT / "contracts")
    parser.add_argument("--scripts-dir", type=Path, default=Path(__file__).parent)
    args = parser.parse_args(argv)
    input_errors = (
        validate_input_directory(args.contracts_dir, "contracts", "*.json"),
        validate_input_directory(args.scripts_dir, "scripts", "*.py"),
    )
    if any(input_errors):
        for error in input_errors:
            if error:
                print(f"ERROR: {error}", file=sys.stderr)
        return 1
    try:
        errors = validate_contracts(*load_contracts(args.contracts_dir))
        errors.extend(validate_platform_neutrality(args.contracts_dir, args.scripts_dir))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not load contract: {exc}")
        return 1
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("hplan core contract is valid: 9 rules, 34 canonical capabilities, 3 aliases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
