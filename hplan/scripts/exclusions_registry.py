#!/usr/bin/env python3
"""Exclusions Registry — append-only "Do Not Build" memory.

Why this is different from a one-off "What Not To Build" section in a doc:
- A section in a doc dies when the doc is regenerated or forked.
- A JSONL append-only registry survives every hplan run and lets future runs
  detect that today's idea overlaps with a previously rejected one.
- Each entry carries a `reopen_trigger` — the *evidence* that would justify
  reopening — so an exclusion is not a permanent veto but a parked hypothesis.

Schema (one JSON object per line in `harness/exclusions.jsonl`):

  {
    "id": "ex-2026-05-11-abc12",
    "ts": "2026-05-11T...",
    "exclusion": "AI marketing copy generator",
    "why": "Established incumbents already cover this",
    "reopen_trigger": "3+ enterprise compliance customers explicitly request it",
    "owned_by_competitor": ["Incumbent A", "Incumbent B"],
    "source": "hplan run 001"
  }

CLI:
  python3 exclusions_registry.py add "AI marketing copy generator" --why "Established incumbents cover this" --reopen "3+ enterprise compliance customers ask" --competitor "Incumbent A" --competitor "Incumbent B"
  python3 exclusions_registry.py check "AI meeting note transcription"
  python3 exclusions_registry.py list
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path


def registry_path(root: Path, profile: str | None = None) -> Path:
    if profile and profile != "default":
        return root / "harness" / "profiles" / profile / "exclusions.jsonl"
    return root / "harness" / "exclusions.jsonl"  # backward-compatible default


def normalize(text: str) -> str:
    text = re.sub(r"[^\w가-힣\s]", " ", (text or "").lower())
    return re.sub(r"\s+", " ", text).strip()


def jaccard_overlap(a: str, b: str) -> float:
    """Hybrid overlap: max of token Jaccard and char-bigram Jaccard.

    Korean text without a morphological analyzer fragments badly under simple
    whitespace tokenization ("생성기" vs "생성" become different tokens). Char
    bigrams catch the substring overlap that human readers see immediately.
    """
    sa = set(normalize(a).split())
    sb = set(normalize(b).split())
    token_jac = len(sa & sb) / len(sa | sb) if (sa and sb) else 0.0

    na = re.sub(r"\s+", "", normalize(a))
    nb = re.sub(r"\s+", "", normalize(b))
    ga = {na[i : i + 2] for i in range(len(na) - 1)}
    gb = {nb[i : i + 2] for i in range(len(nb) - 1)}
    bigram_jac = len(ga & gb) / len(ga | gb) if (ga and gb) else 0.0

    return max(token_jac, bigram_jac)


def add(root: Path, exclusion: str, why: str, reopen_trigger: str, competitors: list[str], source: str | None, profile: str | None = None) -> dict:
    path = registry_path(root, profile)
    path.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    seed = f"{now}{exclusion}".encode("utf-8")
    entry_id = f"ex-{now[:10]}-{hashlib.sha1(seed).hexdigest()[:5]}"
    entry = {
        "id": entry_id,
        "ts": now,
        "exclusion": exclusion,
        "why": why,
        "reopen_trigger": reopen_trigger,
        "owned_by_competitor": competitors,
        "source": source or "hplan",
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    return entry


def read_all(root: Path, profile: str | None = None) -> list[dict]:
    path = registry_path(root, profile)
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


def check(root: Path, idea: str, threshold: float = 0.40, profile: str | None = None) -> dict:
    entries = read_all(root, profile)
    matches = []
    for entry in entries:
        overlap = jaccard_overlap(idea, entry.get("exclusion", ""))
        if overlap >= threshold:
            matches.append({
                "id": entry["id"],
                "exclusion": entry["exclusion"],
                "overlap": round(overlap, 2),
                "why": entry.get("why"),
                "reopen_trigger": entry.get("reopen_trigger"),
                "owned_by_competitor": entry.get("owned_by_competitor", []),
            })
    matches.sort(key=lambda x: -x["overlap"])
    return {
        "idea": idea,
        "matches": matches,
        "verdict": "COLLISION" if matches else "CLEAR",
        "guidance": (
            "Prior exclusion matched. Confirm the reopen_trigger is satisfied before continuing, or pivot."
            if matches
            else "No prior exclusion conflict. Continue gates as normal."
        ),
    }


def parse_args():
    p = argparse.ArgumentParser(description="hplan exclusions registry")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_add = sub.add_parser("add", help="Add a new exclusion")
    p_add.add_argument("exclusion")
    p_add.add_argument("--why", required=True)
    p_add.add_argument("--reopen", required=True, dest="reopen_trigger")
    p_add.add_argument("--competitor", action="append", default=[])
    p_add.add_argument("--source", default=None)
    p_add.add_argument("--root", default=".")
    p_add.add_argument("--profile", default=None,
        help="Profile namespace for client isolation (e.g. client-acme). Default: global registry.")

    p_check = sub.add_parser("check", help="Check an idea against the registry")
    p_check.add_argument("idea")
    p_check.add_argument("--threshold", type=float, default=0.40)
    p_check.add_argument("--root", default=".")
    p_check.add_argument("--profile", default=None,
        help="Profile namespace to check against. Default: global registry.")

    p_list = sub.add_parser("list", help="List all exclusions")
    p_list.add_argument("--root", default=".")
    p_list.add_argument("--profile", default=None,
        help="Profile namespace to list. Default: global registry.")

    return p.parse_args()


def main():
    args = parse_args()
    root = Path(args.root).resolve()
    if args.cmd == "add":
        entry = add(root, args.exclusion, args.why, args.reopen_trigger, args.competitor, args.source, args.profile)
        print(json.dumps(entry, ensure_ascii=False, indent=2))
    elif args.cmd == "check":
        print(json.dumps(check(root, args.idea, args.threshold, args.profile), ensure_ascii=False, indent=2))
    elif args.cmd == "list":
        for entry in read_all(root, args.profile):
            print(json.dumps(entry, ensure_ascii=False))


if __name__ == "__main__":
    main()
