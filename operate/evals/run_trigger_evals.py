#!/usr/bin/env python3
"""
run_trigger_evals.py — Trigger eval runner for hplan skills.

각 SKILL.md의 description을 카탈로그로 모은 뒤, trigger-evals.json의 모든 쿼리에
대해 Claude API를 호출하여 "이 쿼리에 어떤 skill이 발동되어야 하는가"를 판단하고,
ground truth(should_trigger)와 비교해 정확도를 산출한다.

사용:
    export ANTHROPIC_API_KEY=...
    pip install anthropic
    python3 evals/run_trigger_evals.py
    python3 evals/run_trigger_evals.py --model claude-haiku-4-5-20251001  # 빠른 평가
    python3 evals/run_trigger_evals.py --output evals/baseline-results-v0.7.json

산출물:
    evals/baseline-results-v0.7.json (덮어쓰기 가능)
    표준 출력: skill별 pass rate + 총합 summary

비결정성 주의:
    - LLM 응답은 비결정적이므로 같은 쿼리도 재실행 시 결과가 다를 수 있다.
    - 안정 평가를 위해 --runs-per-query 3 같이 다회 실행 후 다수결 권장.

사상:
    이 러너는 Claude Code의 실제 skill auto-load 메커니즘을 100% 재현하지 않는다.
    대신 SKILL.md의 description 매칭이라는 기본 신호를 측정한다.
    v0.6 baseline(97.9%)과 비교 가능하도록 동일한 방식을 따른다.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ["hplan", "discover", "architect", "deliver", "measure", "learn", "operate"]


def load_skill_catalog() -> dict[str, str]:
    """Collect skill name → description from every SKILL.md across plugins."""
    catalog: dict[str, str] = {}
    for plugin in PLUGINS:
        skills_dir = REPO_ROOT / plugin / "skills"
        if not skills_dir.exists():
            continue
        for skill_md in skills_dir.glob("*/SKILL.md"):
            text = skill_md.read_text(encoding="utf-8")
            name_m = re.search(r"^name:\s*(\S+)", text, re.MULTILINE)
            desc_m = re.search(r"^description:\s*\"(.+?)\"\s*$", text, re.MULTILINE | re.DOTALL)
            if name_m and desc_m:
                catalog[name_m.group(1)] = desc_m.group(1).replace("\n", " ").strip()
    return catalog


PROMPT_TEMPLATE = """You are simulating the Claude Code skill auto-loading mechanism.

Given a user query and a catalog of available skills, decide WHICH SKILL (if any) should be auto-loaded to handle the query.

Available skills (name → description):
{catalog}

User query:
{query}

Reply with exactly ONE line in this format:
SKILL: <skill_name>

If no skill matches, reply:
SKILL: none

Do not explain. Just one line."""


def call_claude(client, model: str, query: str, catalog_block: str) -> str:
    msg = client.messages.create(
        model=model,
        max_tokens=64,
        messages=[
            {
                "role": "user",
                "content": PROMPT_TEMPLATE.format(catalog=catalog_block, query=query),
            }
        ],
    )
    raw = msg.content[0].text.strip()
    m = re.search(r"SKILL:\s*([A-Za-z0-9_\-]+)", raw)
    return m.group(1) if m else "none"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-haiku-4-5-20251001")
    ap.add_argument("--input", default=str(REPO_ROOT / "evals" / "trigger-evals.json"))
    ap.add_argument("--output", default=str(REPO_ROOT / "evals" / "baseline-results-v0.7.json"))
    ap.add_argument("--runs-per-query", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true", help="catalog만 출력하고 종료")
    args = ap.parse_args()

    catalog = load_skill_catalog()
    catalog_block = "\n".join(f"- {n}: {d}" for n, d in sorted(catalog.items()))
    print(f"📚 Loaded {len(catalog)} skill descriptions")

    if args.dry_run:
        print(catalog_block)
        return 0

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY 환경 변수 필요", file=sys.stderr)
        return 2

    try:
        import anthropic
    except ImportError:
        print("❌ anthropic 패키지 필요: pip install anthropic", file=sys.stderr)
        return 2

    eval_data = json.loads(Path(args.input).read_text())
    client = anthropic.Anthropic()

    results = []
    total_q = 0
    total_pass = 0
    t0 = time.time()

    for skill_entry in eval_data:
        skill = skill_entry["skill"]
        skill_results = {"skill": skill, "description": catalog.get(skill, ""), "passed": 0, "total": 0, "results": []}

        for q in skill_entry["queries"]:
            query = q["query"]
            should = q["should_trigger"]

            triggers = 0
            for _ in range(args.runs_per_query):
                predicted = call_claude(client, args.model, query, catalog_block)
                if (predicted == skill and should) or (predicted != skill and not should):
                    triggers += 1

            trigger_rate = triggers / args.runs_per_query
            passed = trigger_rate >= 0.5

            skill_results["total"] += 1
            total_q += 1
            if passed:
                skill_results["passed"] += 1
                total_pass += 1

            skill_results["results"].append({
                "query": query,
                "should_trigger": should,
                "trigger_rate": trigger_rate,
                "triggers": triggers,
                "runs": args.runs_per_query,
                "pass": passed,
            })

        results.append(skill_results)
        print(f"  {skill}: {skill_results['passed']}/{skill_results['total']}")

    elapsed = time.time() - t0
    out = {
        "summary": {
            "total_skills": len(results),
            "total_queries": total_q,
            "total_passed": total_pass,
            "pass_rate": f"{total_pass}/{total_q} ({100*total_pass/max(1,total_q):.1f}%)",
            "elapsed_seconds": round(elapsed, 1),
            "model": args.model,
            "runs_per_query": args.runs_per_query,
        },
        "skills": results,
    }
    Path(args.output).write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"\n{out['summary']['pass_rate']} (elapsed {elapsed:.1f}s) → {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
