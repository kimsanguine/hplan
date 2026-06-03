#!/usr/bin/env python3
"""hplan gate guard — Claude Code PreToolUse hook.

Why this exists:
- SKILL.md has 22 "Do Not" rules but they live at prompt level. A determined
  agent can rationalize past them.
- This hook intercepts Write/Edit on `**/PRD.md`, `**/AGENTS.md`, `**/ARCHITECTURE.md`,
  `**/IMPLEMENTATION_READINESS.md`, and similar Build Gate artifacts.
- If `harness/build-gate/checkpoint.json` does not have `status: "approved"`,
  the hook BLOCKS the tool call with a clear WAITING_FOR_HUMAN message.

Wire it in `.claude/settings.json`:

  {
    "hooks": {
      "PreToolUse": [
        {
          "matcher": "Write|Edit",
          "hooks": [{
            "type": "command",
            "command": "python3 $CLAUDE_PROJECT_DIR/hooks/gate_guard.py"
          }]
        }
      ]
    }
  }

Claude Code hooks contract (2026): stdin = JSON event, exit 2 = block.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path


# Context freshness thresholds (days). Based on AI market velocity research.
# warn_after / block_after — absent context_dates field = skip (backward-compat).
FRESHNESS_THRESHOLDS: dict[str, dict[str, int]] = {
    "customer_interviews":  {"warn": 60,  "block": 90},
    "competitive_analysis": {"warn": 45,  "block": 90},
    "provider_pricing":     {"warn": 30,  "block": 60},
    "market_size":          {"warn": 90,  "block": 180},
}

_GUARDED_TOKENS = ["PRD", "AGENTS", "ARCHITECTURE", "IMPLEMENTATION_READINESS", "METRICS"]

# Match Build Gate artifact tokens anywhere within the .md *filename* (basename),
# not just as the exact name. This closes the evasion where variants like
# PRD_draft.md / MyPRD.md / PRD_v2.md / architecture_notes.md slipped past the old
# `(^|/)PRD\.md$` exact-name anchors.
#
# Pattern shape (per token, case-insensitive):
#   (^|/)        — start of path OR a path-segment boundary (so the match is on
#                  the basename, not a directory name like `hplan/agents/`)
#   [^/]*        — any leading filename characters (e.g. "My" in MyPRD)
#   <TOKEN>      — the guarded token, appearing as a substring of the filename
#   [^/]*\.md$   — any trailing filename characters, ending in .md
#
# Deliberate scope decision: the token is matched as a bare substring of the
# basename (no separator required) because the task explicitly requires catching
# glued variants such as `MyPRD.md`. README.md is unaffected — it contains none
# of the guarded tokens as a substring. The known cost of substring matching is
# that domain docs embedding a token (e.g. `metrics-capture.md`) become guarded;
# this is the conservative (fail-safe) direction for a *security* gate and these
# are not "common normal files" the way README is. The match is confined to the
# basename via the (^|/) boundary so directory names never trigger it.
GUARDED_PATTERNS = [
    re.compile(
        rf"(^|/)[^/]*{re.escape(token)}[^/]*\.md$",
        re.I,
    )
    for token in _GUARDED_TOKENS
] + [
    re.compile(r"specs/\d{3}-", re.I),       # spec-kit
    re.compile(r"\.kiro/specs/", re.I),        # kiro
]


def is_guarded(path: str) -> bool:
    return any(p.search(path) for p in GUARDED_PATTERNS)


def check_freshness(project_dir: Path) -> tuple[str, list[str], list[str]]:
    """Check context_dates in checkpoint.json against FRESHNESS_THRESHOLDS.

    Returns (verdict, warnings, blocks):
      verdict = 'ok' | 'warn' | 'block'
      warnings = list of warn-level messages
      blocks   = list of block-level messages
    Absent context_dates = 'ok' (backward-compatible with existing checkpoint.json).
    """
    cp = project_dir / "harness" / "build-gate" / "checkpoint.json"
    if not cp.exists():
        return "ok", [], []
    try:
        data = json.loads(cp.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return "ok", [], []

    context_dates = data.get("context_dates")
    if not context_dates:
        return "ok", [], []

    today = date.today()
    warnings: list[str] = []
    blocks: list[str] = []
    for key, thresholds in FRESHNESS_THRESHOLDS.items():
        raw = context_dates.get(key)
        if raw is None:
            continue
        try:
            age = (today - date.fromisoformat(raw)).days
        except ValueError:
            continue
        if age >= thresholds["block"]:
            blocks.append(
                f"{key}: {age}d old — block threshold {thresholds['block']}d exceeded"
            )
        elif age >= thresholds["warn"]:
            warnings.append(
                f"{key}: {age}d old — warn threshold {thresholds['warn']}d exceeded"
            )

    if blocks:
        return "block", warnings, blocks
    if warnings:
        return "warn", warnings, []
    return "ok", [], []


def signal_gate_check(project_dir: Path) -> tuple[str, list[str]]:
    """Check that all 4 Signal Gate documents exist.

    Returns ('ok', []) or ('block', [missing_relative_paths]).
    """
    required = [
        "harness/pain.md",
        "harness/cogs.md",
        "harness/market.md",
        "harness/competitors.md",
    ]
    missing = [doc for doc in required if not (project_dir / doc).exists()]
    if missing:
        return "block", missing
    return "ok", []


PLACEHOLDER_PATTERNS = [
    (r'\bTBD\b', 'TBD'),
    (r'\b미정\b', '미정'),
    (r'\b추후\b', '추후'),
    (r'\b나중에\b', '나중에'),
    (r'다양한\s+사용자', '다양한 사용자'),
    (r'여러\s+\w*층', '여러 ...층'),
    # 비구체적 타겟 표현
    (r'여러\s+고객', '여러 고객'),
    (r'많은\s+사람', '많은 사람'),
    (r'일반\s+사용자', '일반 사용자'),
    (r'(?i)\btarget\s+user\b', 'target user (비구체적)'),
    # 미완료 마커
    (r'(?i)\bTODO\b', 'TODO'),
    (r'\b미기입\b', '미기입'),
    (r'\b검토\s*예정\b', '검토 예정'),
]


def placeholder_gate_check(project_dir: Path) -> tuple[str, list[str]]:
    """Check Signal Gate documents for placeholder expressions.

    Returns ('ok', []) or ('block', [flagged_messages]).
    Only the first match per document is reported.
    """
    docs = [
        "harness/pain.md",
        "harness/cogs.md",
        "harness/market.md",
        "harness/competitors.md",
    ]
    flagged = []
    for doc in docs:
        path = project_dir / doc
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        for pattern, label in PLACEHOLDER_PATTERNS:
            if re.search(pattern, content):
                flagged.append(f"  ❌ {doc}: '{label}' 감지 — 구체적인 내용으로 교체 필요")
                break  # 문서당 첫 번째 매치만 보고
    if flagged:
        return "block", flagged
    return "ok", []


EVIDENCE_PATTERNS = {
    "harness/pain.md": [
        r'\d{4}-\d{2}-\d{2}',           # 날짜 패턴 (인터뷰 날짜)
        r'(?i)##\s*evidence',            # Evidence 섹션
        r'(?i)인터뷰|interview|observed|관찰',
    ],
    "harness/cogs.md": [
        r'(?i)pricing|price|가격|출처',
        r'(?i)##\s*evidence',
        r'(?i)API.*cost|비용.*출처',
    ],
    "harness/market.md": [
        r'(?i)report|리포트|출처|source|TAM|SAM',
        r'(?i)##\s*evidence',
        r'\d{4}.*리포트|\d{4}.*report',
    ],
    "harness/competitors.md": [
        r'(?i)테스트|test|tried|직접|사용자.*말|user.*said',
        r'(?i)##\s*evidence',
        r'(?i)인용|quote|".*"',
    ],
}


def evidence_source_check(project_dir: Path) -> tuple[str, list[str]]:
    missing = []
    for doc_path, patterns in EVIDENCE_PATTERNS.items():
        path = project_dir / doc_path
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        if not any(re.search(p, content) for p in patterns):
            doc_name = doc_path.split("/")[-1]
            missing.append(f"  ⚠️  {doc_name}: evidence source 선언 없음 — 출처·날짜·인용 중 하나 추가 필요")
    if len(missing) >= 4:  # 4개 모두 미충족 시 차단
        return "block", missing
    if missing:
        return "warn", missing
    return "ok", []


def gate_approved(project_dir: Path) -> tuple[bool, str, dict]:
    """Return (approved, reason, data). data is the full checkpoint dict."""
    cp = project_dir / "harness" / "build-gate" / "checkpoint.json"
    if not cp.exists():
        return False, f"missing {cp.relative_to(project_dir)}", {}
    try:
        data = json.loads(cp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return False, f"checkpoint.json is invalid JSON: {e}", {}
    status = data.get("status")
    if status == "approved":
        return True, "", data
    return False, f"checkpoint.json status = {status!r} (need 'approved')", data


def check_conditional_scope(data: dict, target: str) -> tuple[str, str]:
    """Enforce CONDITIONAL_GO write-time restrictions.

    Returns ('ok', '') or ('block', reason).
    Absent decision field = treat as GO (backward-compatible).
    """
    decision = data.get("decision", "GO")
    if decision != "CONDITIONAL_GO":
        return "ok", ""

    # Expiry check
    expires_at = (data.get("expires_at") or "").strip()
    if expires_at:
        try:
            if date.today() > date.fromisoformat(expires_at):
                return "block", (
                    f"CONDITIONAL_GO expired on {expires_at}.\n"
                    "  Re-run /hplan to reassess or obtain full GO approval."
                )
        except ValueError:
            pass

    # Scope check: if allowed_paths is non-empty, target must be in scope
    allowed: list[str] = data.get("allowed_paths") or []
    if allowed:
        norm = target.replace("\\", "/")
        in_scope = any(
            norm.endswith(p.lstrip("/")) or p.lstrip("/") in norm
            for p in allowed
        )
        if not in_scope:
            conditions = data.get("conditions") or []
            cond_str = "\n    ".join(conditions) if conditions else "(none listed)"
            return "block", (
                f"CONDITIONAL_GO: write is outside allowed scope.\n"
                f"  Allowed paths: {allowed}\n"
                f"  Target:        {norm!r}\n"
                f"  Outstanding conditions:\n    {cond_str}\n"
                "  Resolve all conditions first or obtain full GO approval."
            )

    return "ok", ""


def _run_gate(event: dict) -> int:
    """Core gate logic. Raises on unexpected I/O errors so main() can fail-closed."""
    tool_input = event.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("path") or ""
    if not target:
        return 0

    target_norm = target.replace("\\", "/")
    if not is_guarded(target_norm):
        return 0

    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    bypass = os.environ.get("CLAUDE_HPLAN_BYPASS") == "1"

    if bypass:
        print("hplan gate guard: bypass via CLAUDE_HPLAN_BYPASS=1", file=sys.stderr)
        return 0

    # --- Signal Gate check ---
    _SIGNAL_DOCS_HINT: dict[str, str] = {
        "harness/pain.md":        "누가, 어떤 상황에서, 뭘 못하는가",
        "harness/cogs.md":        "p50/p90 단위 경제성 시뮬레이션",
        "harness/market.md":      "시장 규모 + 진입 시점 근거",
        "harness/competitors.md": "직접 경쟁사 2개 + 대체재 1개",
    }
    sg_verdict, sg_missing = signal_gate_check(project_dir)
    if sg_verdict == "block":
        lines = ["hplan gate guard BLOCKED: Signal Gate documents missing."]
        for doc in sg_missing:
            lines.append(f"  ❌ {doc} — {_SIGNAL_DOCS_HINT.get(doc, '')}")
        lines.append(
            "Create the missing document(s) and re-run /hplan before writing Build Gate artifacts."
        )
        print("\n".join(lines), file=sys.stderr)
        return 2

    # --- Placeholder check ---
    pg_verdict, pg_flagged = placeholder_gate_check(project_dir)
    if pg_verdict == "block":
        lines = ["hplan gate guard BLOCKED: Signal Gate 문서에 모호한 표현 감지."]
        lines.extend(pg_flagged)
        lines.append("위 표현을 측정 가능한 구체적 내용으로 교체 후 다시 실행하세요.")
        print("\n".join(lines), file=sys.stderr)
        return 2

    # --- Evidence Source check ---
    es_status, es_issues = evidence_source_check(project_dir)
    if es_status == "block":
        print("hplan Signal Gate — Evidence Source 미선언", file=sys.stderr)
        for issue in es_issues:
            print(issue, file=sys.stderr)
        print("", file=sys.stderr)
        print("4개 Signal Gate 문서 모두 증거 출처가 없습니다.", file=sys.stderr)
        print("각 문서에 인터뷰 날짜, 출처 링크, 또는 ## Evidence 섹션을 추가하세요.", file=sys.stderr)
        return 2
    elif es_status == "warn":
        for issue in es_issues:
            print(issue, file=sys.stderr)
        # warn은 차단하지 않고 계속 진행

    # --- Freshness check ---
    freshness_verdict, fresh_warns, fresh_blocks = check_freshness(project_dir)
    if freshness_verdict == "warn":
        for w in fresh_warns:
            print(f"hplan freshness ⚠️  {w}", file=sys.stderr)
    elif freshness_verdict == "block":
        lines = ["hplan gate guard BLOCKED: context data is stale."]
        for b in fresh_blocks:
            lines.append(f"  🚫 {b}")
        lines.append(
            "Update context_dates in harness/build-gate/checkpoint.json "
            "and re-run /hplan to refresh the gate."
        )
        print("\n".join(lines), file=sys.stderr)
        return 2

    # --- Approval check ---
    ok, reason, cp_data = gate_approved(project_dir)
    if not ok:
        print(
            f"hplan gate guard BLOCKED write to {target_norm}\n"
            f"reason: {reason}\n"
            "This file is a Build Gate artifact. Before editing:\n"
            "  1. Run hplan Evidence Gate + Product Gate.\n"
            "  2. Approve harness/build-gate/checkpoint.json (status='approved').\n"
            "  3. Or set CLAUDE_HPLAN_BYPASS=1 in your shell for one explicit override.\n"
            "Per SKILL.md: WAITING_FOR_HUMAN.",
            file=sys.stderr,
        )
        return 2

    # --- CONDITIONAL_GO scope check (only when approved) ---
    scope_verdict, scope_reason = check_conditional_scope(cp_data, target_norm)
    if scope_verdict == "block":
        print(
            f"hplan gate guard BLOCKED: CONDITIONAL_GO scope violation.\n{scope_reason}",
            file=sys.stderr,
        )
        return 2

    return 0


def main():
    # Parse the PreToolUse event. A malformed/empty stdin is the one intentional
    # fail-open path (Claude Code may probe the hook without a real event); it is
    # not a crash and must not block normal usage.
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    # Fail CLOSED on any unexpected error while running the gate. Previously an
    # I/O exception (e.g. a Signal Gate doc being a directory → IsADirectoryError,
    # or a permission error) crashed the script with exit 1. Claude Code only
    # blocks on exit 2, so an exit-1 crash silently bypassed the gate on guarded
    # files. Converting unexpected failures to exit 2 makes the guard safe-by-default.
    try:
        return _run_gate(event)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — intentional catch-all for fail-closed
        print(
            "hplan gate guard BLOCKED (fail-closed): the guard crashed while "
            "evaluating this write.\n"
            f"  error: {type(e).__name__}: {e}\n"
            "  A Build Gate artifact write is blocked because the gate could not "
            "be verified.\n"
            "  Check harness/ Signal Gate documents (a doc may be a directory, "
            "unreadable, or have a permission error), then retry.",
            file=sys.stderr,
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
