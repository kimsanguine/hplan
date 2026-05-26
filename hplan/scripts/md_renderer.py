#!/usr/bin/env python3
"""
hplan MD → HTML 자동 렌더러
PostToolUse.sh에서 호출됨. 실패 시 항상 조용히 exit 0.
사용법: python3 md_renderer.py <file_path>
"""

import sys
import re
import json
from pathlib import Path

# ── 경로 상수 ─────────────────────────────────────────────
TEMPLATE_DIR = Path(__file__).parent.parent / "templates"

# ── 제외 패턴 ─────────────────────────────────────────────
_EXCLUDE_PATTERNS = [
    r"(?:^|/)CLAUDE\.md$",
    r"(?:^|/)README\.md$",
    r"(?:^|/)PLUGIN\.md$",
    r"(?:^|/)SKILL\.md$",
    r"(?:^|/)CHANGELOG\.md$",
    r"(?:^|/)CONTRIBUTING\.md$",
    r"(?:^|/)GUIDE.*\.md$",
    r"/references/.*\.md$",
    r"/examples/.*\.md$",
]

# ── 경로→템플릿 매핑 (순서 중요 — 위에서 먼저 매칭) ────────
_TEMPLATE_MAP = [
    (r"harness/evidence/report\.md$",           "evidence-gate"),
    (r"harness/build-gate/cogs_report\.md$",    "cogs-sentinel"),
    (r"harness/STATE\.md$",                     "gate-state"),
    (r"harness/pain\.md$",                      "pain-board"),
    (r"docs/OPPORTUNITY_TREE\.md$",             "ost-viewer"),
    (r"harness/competitors\.md$",               "market-intel"),
    (r"harness/ARCHITECTURE\.md$",              "architecture-blueprint"),
    (r"harness/PROGRESS\.md$",                  "sprint-tracker"),
    (r"docs/PRD\.md$",                          "prd-reader"),
    (r"(?:docs/DESIGN\.md|\.design/RESPECT\.md)$", "design-system"),
    # generic fallback — harness, docs, specs 하위 나머지
    (r"(?:harness|docs|specs)/.*\.md$",         "generic"),
]


def should_exclude(file_path: str) -> bool:
    """True이면 변환하지 않는다."""
    for pattern in _EXCLUDE_PATTERNS:
        if re.search(pattern, file_path):
            return True
    return False


def select_template(file_path: str) -> str | None:
    """경로 패턴 매칭으로 템플릿 이름 반환. 매칭 없으면 None."""
    for pattern, template_name in _TEMPLATE_MAP:
        if re.search(pattern, file_path):
            return template_name
    return None


def _load_template(template_name: str) -> str | None:
    """템플릿 HTML 파일을 읽는다. 없으면 None."""
    template_path = TEMPLATE_DIR / f"{template_name}.html"
    if not template_path.exists():
        # 전용 템플릿 없으면 generic으로 폴백
        if template_name != "generic":
            return _load_template("generic")
        return None
    return template_path.read_text(encoding="utf-8")


def _escape_json_for_script(json_str: str) -> str:
    """<script> 블록 내 JSON 삽입 시 스크립트 태그 탈출 방지.

    브라우저 HTML 파서는 JS 문자열 파싱보다 먼저 실행되므로
    JSON 문자열 안의 </script> 만으로도 스크립트 블록이 닫힌다.
    """
    return (
        json_str
        .replace("</", "<\\/")          # </script> 탈출 방지
        .replace("<!--", "<\\!--")      # HTML 주석 삽입 방지
        .replace(" ", "\\u2028")   # JS 줄 구분자 (일부 엔진 오작동)
        .replace(" ", "\\u2029")   # JS 단락 구분자
    )


def render(template_name: str, data: dict) -> str | None:
    """템플릿에 data dict를 __DATA_JSON__ 자리에 주입한 HTML 반환."""
    html = _load_template(template_name)
    if html is None:
        return None
    json_str = json.dumps(data, ensure_ascii=False, indent=None)
    return html.replace("__DATA_JSON__", _escape_json_for_script(json_str))


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(0)

    file_path = sys.argv[1]

    if should_exclude(file_path):
        sys.exit(0)

    template_name = select_template(file_path)
    if template_name is None:
        sys.exit(0)

    try:
        md_path = Path(file_path)
        if not md_path.exists():
            sys.exit(0)

        md_content = md_path.read_text(encoding="utf-8")

        # 파서는 Task 2~14에서 추가됨. 지금은 generic 데이터로 처리.
        from parsers import parse  # noqa: E402 (Task 2에서 생성)
        data = parse(md_content, template_name)

        html = render(template_name, data)
        if html is None:
            sys.exit(0)

        output_path = md_path.with_suffix(".html")
        output_path.write_text(html, encoding="utf-8")

    except Exception:
        pass  # 실패 시 조용히 종료 — Claude Code 흐름 비차단

    sys.exit(0)


if __name__ == "__main__":
    main()
