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
import sys
from datetime import date
from pathlib import Path


def parse_checklist(checklist_path: str) -> list[dict]:
    """
    Parse harness/QA_CHECKLIST.md and return TC entries.
    Table row format (7 columns, last column = severity):
    | TC-001 | 시나리오 | 환경 | 전제조건 | 기대결과 | PRD출처 | critical |

    Optional 8-column format with Expected State assertion:
    | TC-001 | 시나리오 | 환경 | 전제조건 | 기대결과 | PRD출처 | Expected State | critical |

    Uses split-based parser (not regex) so pipe chars inside cells don't break parsing.
    TC-ID is always column 0 (starts with TC-), severity is always last column.
    """
    tcs = []
    path = Path(checklist_path)
    if not path.exists():
        print(f"ERROR: {checklist_path} not found", file=sys.stderr)
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            # Split on | and strip each cell; filter empty strings (leading/trailing |)
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) < 7:
                continue
            tc_id = parts[0]
            severity = parts[-1].lower()  # severity is always the last column
            if not tc_id.startswith("TC-"):
                continue
            if severity not in ("critical", "major", "minor"):
                continue
            expected_state = parts[-2].strip() if len(parts) >= 8 else "—"
            tcs.append(
                {
                    "id": tc_id,
                    "scenario": parts[1],
                    "environment": parts[2],
                    "severity": severity,
                    "expected_state": expected_state,
                }
            )

    if not tcs:
        print(
            f"ERROR: No valid TC rows found in {checklist_path}.\n"
            "  Expected format: | TC-NNN | 시나리오 | 환경 | 전제조건 | 기대결과 | PRD출처 | critical/major/minor |\n"
            "  Run /qa-checklist to regenerate.",
            file=sys.stderr,
        )
        sys.exit(1)

    severity_order = {"critical": 0, "major": 1, "minor": 2}
    tcs.sort(key=lambda t: severity_order.get(t["severity"], 3))
    return tcs


def run_assertion(page, expected: str) -> dict:
    """
    Run a single Playwright assertion against the current page state.
    Supports 3 assertion types:
      url_contains:<path>
      element_exists:<selector>
      element_text:<selector>:<text>
    Returns {"passed": bool, "type": str, "detail": str}
    """
    if not expected or expected in ("—", "-", ""):
        return {"passed": True, "type": "none", "detail": "no assertion defined"}

    try:
        if expected.startswith("url_contains:"):
            path = expected[len("url_contains:"):]
            current_url = page.url
            passed = path in current_url
            return {
                "passed": passed,
                "type": "url_contains",
                "detail": f"expected '{path}' in '{current_url}'",
            }

        elif expected.startswith("element_exists:"):
            selector = expected[len("element_exists:"):]
            count = page.locator(selector).count()
            passed = count > 0
            return {
                "passed": passed,
                "type": "element_exists",
                "detail": f"selector='{selector}' count={count}",
            }

        elif expected.startswith("element_text:"):
            rest = expected[len("element_text:"):]
            parts = rest.split(":", 1)
            if len(parts) != 2:
                return {
                    "passed": False,
                    "type": "element_text",
                    "detail": f"invalid format (expected 'element_text:<selector>:<text>'): {expected}",
                }
            selector, text = parts
            content = page.locator(selector).text_content(timeout=5000) or ""
            passed = text in content
            return {
                "passed": passed,
                "type": "element_text",
                "detail": f"selector='{selector}' expected='{text}' got='{content[:80]}'",
            }

        else:
            return {
                "passed": False,
                "type": "unknown",
                "detail": f"unknown assertion type: {expected}",
            }

    except Exception as e:
        return {"passed": False, "type": "error", "detail": str(e)[:120]}


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

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    results = []
    counts = {s: {"total": 0, "screenshots": 0} for s in ("critical", "major", "minor")}
    critical_assertion_fails = 0  # critical TC assertion 실패 수

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
                    counts[sev]["screenshots"] += 1
                print(f"    ✅ saved → {screenshot_path}")

                # Assertion 실행 (expected_state가 정의된 TC만)
                assertion_result = None
                exp_state = tc.get("expected_state", "—")
                if exp_state and exp_state not in ("—", "-", ""):
                    assertion_result = run_assertion(page, exp_state)
                    if sev == "critical" and not assertion_result["passed"]:
                        critical_assertion_fails += 1
                        print(
                            f"    ⚠️  assertion FAIL: {assertion_result['detail']}",
                            file=sys.stderr,
                        )
                    elif assertion_result["passed"]:
                        print(f"    ✅ assertion PASS: {assertion_result['type']}")

                results.append(
                    {
                        "id": tc_id,
                        "severity": sev,
                        "screenshot": str(screenshot_path),
                        "status": "captured",
                        "assertion": assertion_result,
                    }
                )
            except Exception as e:
                results.append(
                    {
                        "id": tc_id,
                        "severity": sev,
                        "screenshot": None,
                        "status": "error",
                        "error": str(e)[:120],
                        "assertion": None,
                    }
                )
                print(f"    ❌ error: {e}", file=sys.stderr)

        browser.close()

    summary = {
        "generated": str(date.today()),
        "evidence_type": "screenshot_only",
        "url": url,
        "total": len(tcs),
        "critical_screenshots": counts["critical"]["screenshots"],
        "critical_total": counts["critical"]["total"],
        "major_screenshots": counts["major"]["screenshots"],
        "major_total": counts["major"]["total"],
        "minor_screenshots": counts["minor"]["screenshots"],
        "minor_total": counts["minor"]["total"],
        "critical_assertion_fails": critical_assertion_fails,
        "tc_results": results,
    }

    summary_path = output_path / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2))

    print(f"\n✅ harness/ui-evidence/ 생성 완료")
    print(
        f"   Total: {summary['total']} | "
        f"Critical: {summary['critical_screenshots']}/{summary['critical_total']} | "
        f"Major: {summary['major_screenshots']}/{summary['major_total']} | "
        f"Minor: {summary['minor_screenshots']}/{summary['minor_total']}"
    )

    if critical_assertion_fails > 0:
        print(
            f"   ⚠️  Critical assertion 실패: {critical_assertion_fails}건 "
            f"— harness/ui-evidence/summary.json tc_results 확인 후 수정",
            file=sys.stderr,
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
