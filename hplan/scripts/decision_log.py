#!/usr/bin/env python3
"""Decision Log — append-only record of hplan gate decisions + self-eval audit.

Why:
- hplan should be measurable. If it tells you "hold", was it right?
- A 6-month audit ("hold 12건 중 8건 실제로 죽었고 4건은 false hold") is the
  only way hplan can demonstrate calibration over time.

Schema (one JSON object per line in `harness/decisions.jsonl`):

  {
    "id": "dec-2026-05-11-...",
    "ts": "2026-05-11T...",
    "project": "alpha-app",
    "gate": "evidence" | "product" | "build",
    "decision": "build" | "interview" | "pivot" | "hold" | "CONDITIONAL_GO",
    "score": 78,
    "reasons": ["...", "..."],
    "outcome": null            // back-filled later: "shipped" | "killed" | "alive_no_revenue" | "pivoted" | "external_success"
  }

Subcommands:
- log:     append a gate decision (build/interview/pivot/hold)
- hitl:    append a HITL decision (options → chosen, any phase)
- list:    print decisions (optionally filtered by --phase or --project)
- update:  back-fill outcome on an existing gate decision (id-keyed)
- audit:   print hit/miss/false-hold counts and reopen suggestions

HITL schema (type=hitl):
  {"id": ..., "ts": ..., "type": "hitl", "phase": "discover|architect|build|operate",
   "project": ..., "q": "결정 질문", "options": ["A", "B", "C"], "chosen": "A", "why": "..."}
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


VALID_DECISIONS = {"build", "interview", "pivot", "hold", "CONDITIONAL_GO"}
VALID_OUTCOMES = {"shipped", "killed", "alive_no_revenue", "pivoted", "external_success", None}


def log_path(root: Path) -> Path:
    return root / "harness" / "decisions.jsonl"


def append(root: Path, entry: dict) -> dict:
    path = log_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    seed = f"{now}{entry.get('project','')}{entry.get('decision','')}".encode("utf-8")
    payload = {
        "id": entry.get("id") or f"dec-{now[:10]}-{hashlib.sha1(seed).hexdigest()[:5]}",
        "ts": entry.get("ts") or now,
        "project": entry.get("project", "unknown"),
        "gate": entry.get("gate", "build"),
        "decision": entry.get("decision", "interview"),
        "score": entry.get("score"),
        "reasons": entry.get("reasons", []),
        "outcome": entry.get("outcome"),
    }
    if payload["decision"] not in VALID_DECISIONS:
        raise SystemExit(f"invalid decision: {payload['decision']}")
    if payload["outcome"] not in VALID_OUTCOMES:
        raise SystemExit(f"invalid outcome: {payload['outcome']}")
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return payload


def append_hitl(root: Path, entry: dict) -> dict:
    path = log_path(root)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    seed = f"{now}{entry.get('phase','')}{entry.get('q','')}".encode("utf-8")
    payload: dict = {
        "id": f"hitl-{now[:10]}-{hashlib.sha1(seed).hexdigest()[:5]}",
        "ts": now,
        "type": "hitl",
        "phase": entry["phase"],
        "project": entry.get("project", ""),
        "q": entry["q"],
        "options": entry.get("options", []),
        "chosen": entry["chosen"],
        "why": entry.get("why", ""),
    }
    if entry.get("prd_version"):
        payload["prd_version"] = entry["prd_version"]
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return payload


def read_all(root: Path) -> list[dict]:
    path = log_path(root)
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def update_outcome(root: Path, entry_id: str, outcome: str) -> dict:
    if outcome not in VALID_OUTCOMES or outcome is None:
        raise SystemExit(f"invalid outcome: {outcome}")
    entries = read_all(root)
    found = None
    for entry in entries:
        if entry["id"] == entry_id:
            entry["outcome"] = outcome
            found = entry
            break
    if not found:
        raise SystemExit(f"id not found: {entry_id}")
    path = log_path(root)
    path.write_text(
        "\n".join(json.dumps(e, ensure_ascii=False) for e in entries) + "\n",
        encoding="utf-8",
    )
    return found


def audit(root: Path) -> dict:
    all_entries = read_all(root)
    entries = [e for e in all_entries if e.get("type") != "hitl"]
    by_decision = Counter(e["decision"] for e in entries)
    resolved = [e for e in entries if e.get("outcome")]
    by_decision_outcome = Counter(
        (e["decision"], e["outcome"]) for e in resolved
    )

    correct = 0
    wrong = 0
    pending = len(entries) - len(resolved)

    for entry in resolved:
        d, o = entry["decision"], entry["outcome"]
        if d == "hold" and o in {"killed", "alive_no_revenue", "pivoted"}:
            correct += 1
        elif d == "hold" and o in {"shipped", "external_success"}:
            wrong += 1
        elif d == "build" and o == "shipped":
            correct += 1
        elif d == "build" and o == "killed":
            wrong += 1
        elif d == "pivot" and o == "pivoted":
            correct += 1
        elif d == "interview" and o in {"shipped", "killed", "pivoted"}:
            correct += 1
        else:
            wrong += 1

    hit_rate = (correct / (correct + wrong)) if (correct + wrong) else None

    false_holds = [
        e for e in resolved if e["decision"] == "hold" and e["outcome"] in {"shipped", "external_success"}
    ]
    missed_builds = [
        e for e in resolved if e["decision"] == "build" and e["outcome"] == "killed"
    ]

    return {
        "total": len(entries),
        "resolved": len(resolved),
        "pending": pending,
        "by_decision": dict(by_decision),
        "by_decision_outcome": {f"{d}->{o}": n for (d, o), n in by_decision_outcome.items()},
        "hit_rate": round(hit_rate, 3) if hit_rate is not None else None,
        "false_holds": [
            {"id": e["id"], "project": e["project"], "reasons": e.get("reasons", [])}
            for e in false_holds
        ],
        "missed_builds": [
            {"id": e["id"], "project": e["project"], "reasons": e.get("reasons", [])}
            for e in missed_builds
        ],
        "guidance": _audit_guidance(hit_rate, false_holds, missed_builds, pending),
    }


def _audit_guidance(hit_rate, false_holds, missed_builds, pending) -> list[str]:
    out = []
    if pending and not (false_holds or missed_builds):
        out.append(f"{pending} decisions still pending — back-fill outcomes to enable calibration.")
    if hit_rate is None:
        out.append("No resolved decisions yet. Hit rate will become measurable once outcomes are back-filled.")
        return out
    if hit_rate >= 0.75:
        out.append(f"Hit rate {hit_rate:.0%} — calibration is healthy.")
    elif hit_rate >= 0.5:
        out.append(f"Hit rate {hit_rate:.0%} — re-examine rubric thresholds.")
    else:
        out.append(f"Hit rate {hit_rate:.0%} — gate calibration is failing; consider rubric overhaul.")
    if false_holds:
        out.append(f"{len(false_holds)} false-hold(s) detected — review reasons for systematic bias against shippable ideas.")
    if missed_builds:
        out.append(f"{len(missed_builds)} build-then-killed — Evidence Gate is letting weak ideas through.")
    return out


def parse_args():
    p = argparse.ArgumentParser(description="hplan decision log")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_log = sub.add_parser("log", help="Append a decision")
    p_log.add_argument("--project", required=True)
    p_log.add_argument("--gate", choices=["evidence", "product", "build"], default="build")
    p_log.add_argument("--decision", choices=sorted(VALID_DECISIONS), required=True)
    p_log.add_argument("--score", type=int, default=None)
    p_log.add_argument("--reason", action="append", default=[])
    p_log.add_argument("--root", default=".")

    p_up = sub.add_parser("update", help="Back-fill an outcome")
    p_up.add_argument("--id", required=True, dest="entry_id")
    p_up.add_argument(
        "--outcome",
        required=True,
        choices=[o for o in VALID_OUTCOMES if o],
    )
    p_up.add_argument("--root", default=".")

    p_hitl = sub.add_parser("hitl", help="Log a HITL decision (options → chosen)")
    p_hitl.add_argument("--phase", required=True,
                        choices=["signal", "discover", "architect", "build", "operate"])
    p_hitl.add_argument("--q", required=True, help="Decision question")
    p_hitl.add_argument("--options", required=True,
                        help="Options separated by | (e.g. 'A: desc|B: desc|C: desc')")
    p_hitl.add_argument("--chosen", required=True, help="Chosen option")
    p_hitl.add_argument("--why", default="", help="Reason for choosing")
    p_hitl.add_argument("--project", default="")
    p_hitl.add_argument("--prd-version", default="", dest="prd_version",
                        help="PRD version this decision belongs to (e.g. v0.1)")
    p_hitl.add_argument("--root", default=".")

    p_list = sub.add_parser("list", help="List decisions")
    p_list.add_argument("--phase", default=None, help="Filter by gate (evidence|product|build)")
    p_list.add_argument("--project", default=None, help="Filter by project name")
    p_list.add_argument("--root", default=".")

    p_audit = sub.add_parser("audit", help="Calibration audit")
    p_audit.add_argument("--root", default=".")

    return p.parse_args()


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    if args.cmd == "hitl":
        entry = append_hitl(root, {
            "phase": args.phase,
            "q": args.q,
            "options": [o.strip() for o in args.options.split("|")],
            "chosen": args.chosen,
            "why": args.why,
            "project": args.project,
            "prd_version": args.prd_version,
        })
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    elif args.cmd == "log":
        entry = append(root, {
            "project": args.project,
            "gate": args.gate,
            "decision": args.decision,
            "score": args.score,
            "reasons": args.reason,
        })
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    elif args.cmd == "update":
        entry = update_outcome(root, args.entry_id, args.outcome)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    elif args.cmd == "list":
        entries = read_all(root)
        if args.phase:
            entries = [
                e for e in entries
                if (e.get("type") == "hitl" and e.get("phase") == args.phase)
                or (e.get("type") != "hitl" and e.get("gate") == args.phase)
            ]
        if args.project:
            entries = [e for e in entries if e.get("project") == args.project]
        print(json.dumps(entries, ensure_ascii=False, indent=2))
    elif args.cmd == "audit":
        print(json.dumps(audit(root), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
