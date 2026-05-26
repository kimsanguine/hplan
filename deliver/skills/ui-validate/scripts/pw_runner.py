#!/usr/bin/env python3
"""
pw_runner.py — TC Gate Playwright runner for hplan ui-validate --check tc-gate

Usage:
  python3 pw_runner.py --url <URL> --checklist <path> --output <dir>
  python3 pw_runner.py --parse-only <checklist_path>

Requires: pip install playwright && playwright install chromium
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


def parse_checklist(checklist_path: str) -> list[dict]:
    """
    Parse harness/QA_CHECKLIST.md and return TC entries.
    Expected table row format (7 columns):
    | TC-001 | 시나리오 | 환경 | 전제조건 | 기대결과 | PRD출처 | critical |
    """
    tcs = []
    path = Path(checklist_path)
    if not path.exists():
        print(f"ERROR: {checklist_path} not found", file=sys.stderr)
        sys.exit(1)

    row_pattern = re.compile(
        r"^\|\s*(TC-\d+)\s*\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|([^|]+)\|\s*(critical|major|minor)\s*\|",
        re.IGNORECASE,
    )

    with open(path, encoding="utf-8") as f:
        for line in f:
            m = row_pattern.match(line)
            if m:
                tcs.append(
                    {
                        "id": m.group(1).strip(),
                        "scenario": m.group(2).strip(),
                        "environment": m.group(3).strip(),
                        "severity": m.group(7).strip().lower(),
                    }
                )

    # Sort: critical → major → minor
    severity_order = {"critical": 0, "major": 1, "minor": 2}
    tcs.sort(key=lambda t: severity_order.get(t["severity"], 3))
    return tcs


def run_tc_gate(url: str, checklist_path: str, output_dir: str) -> None:
    """Run Playwright screenshots for each TC-ID and write summary.json."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "ERROR: playwright not installed. Run: pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    tcs = parse_checklist(checklist_path)
    if not tcs:
        print(f"WARNING: No TC rows found in {checklist_path}", file=sys.stderr)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    counts = {s: {"total": 0, "captured": 0} for s in ("critical", "major", "minor")}

    for tc in tcs:
        sev = tc["severity"]
        if sev in counts:
            counts[sev]["total"] += 1

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 800})

        for tc in tcs:
            tc_id = tc["id"]
            sev = tc["severity"]
            screenshot_path = output_path / f"{tc_id}.png"
            print(f"  [{sev.upper()}] {tc_id}: {tc['scenario'][:60]}...")

            try:
                page.goto(url, timeout=30000, wait_until="networkidle")
                page.screenshot(path=str(screenshot_path), full_page=True)
                if sev in counts:
                    counts[sev]["captured"] += 1
                results.append(
                    {
                        "id": tc_id,
                        "severity": sev,
                        "screenshot": str(screenshot_path),
                        "status": "captured",
                    }
                )
                print(f"    ✅ saved → {screenshot_path}")
            except Exception as e:
                results.append(
                    {
                        "id": tc_id,
                        "severity": sev,
                        "screenshot": None,
                        "status": "error",
                        "error": str(e)[:120],
                    }
                )
                print(f"    ❌ error: {e}", file=sys.stderr)

        browser.close()

    summary = {
        "generated": str(date.today()),
        "url": url,
        "total": len(tcs),
        "critical_captured": counts["critical"]["captured"],
        "critical_total": counts["critical"]["total"],
        "major_captured": counts["major"]["captured"],
        "major_total": counts["major"]["total"],
        "minor_captured": counts["minor"]["captured"],
        "minor_total": counts["minor"]["total"],
        "tc_results": results,
    }

    summary_path = output_path / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))

    print(f"\n✅ harness/ui-evidence/ 생성 완료")
    print(
        f"   Total: {summary['total']} | "
        f"Critical: {summary['critical_captured']}/{summary['critical_total']} | "
        f"Major: {summary['major_captured']}/{summary['major_total']} | "
        f"Minor: {summary['minor_captured']}/{summary['minor_total']}"
    )

    errors = [r for r in results if r["status"] == "error"]
    if errors:
        print(f"   실패: {', '.join(r['id'] for r in errors)}", file=sys.stderr)

    print(f"   → harness-build --step quality-gate 에서 자동 검사")


def main() -> None:
    parser = argparse.ArgumentParser(description="TC Gate Playwright runner")
    parser.add_argument("--url", help="Target URL to screenshot")
    parser.add_argument(
        "--checklist",
        default="harness/QA_CHECKLIST.md",
        help="Path to QA_CHECKLIST.md",
    )
    parser.add_argument(
        "--output",
        default="harness/ui-evidence",
        help="Output directory for screenshots and summary.json",
    )
    parser.add_argument(
        "--parse-only",
        metavar="CHECKLIST",
        help="Parse and print TC list without running Playwright",
    )
    args = parser.parse_args()

    if args.parse_only:
        tcs = parse_checklist(args.parse_only)
        print(f"Found {len(tcs)} TCs:")
        for tc in tcs:
            print(f"  [{tc['severity'].upper()}] {tc['id']}: {tc['scenario'][:80]}")
        return

    if not args.url:
        print("ERROR: --url is required for tc-gate run", file=sys.stderr)
        sys.exit(1)

    run_tc_gate(args.url, args.checklist, args.output)


if __name__ == "__main__":
    main()
