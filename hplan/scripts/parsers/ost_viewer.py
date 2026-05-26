import re
from .generic import parse_generic


def parse_ost_viewer(md: str) -> dict:
    base = parse_generic(md)
    return {
        **base,
        "template": "ost-viewer",
        "mermaid_code": _extract_mermaid_code(md),
        "solutions": _extract_solutions(md),
    }


def _extract_mermaid_code(md: str) -> str:
    """```mermaid ... ``` 펜스 사이의 내용을 반환. 없으면 빈 문자열."""
    m = re.search(r"```mermaid\n(.*?)```", md, re.DOTALL)
    if not m:
        return ""
    return m.group(1).rstrip("\n")


def _extract_solutions(md: str) -> list[dict]:
    """## Solution 으로 시작하는 섹션마다 name과 status를 추출."""
    solutions = []
    # ## Solution 헤딩과 그 다음 섹션 사이의 텍스트를 캡처
    sections = re.split(r"^(?=##\s)", md, flags=re.MULTILINE)
    for section in sections:
        header_match = re.match(r"^##\s+(.+)$", section, re.MULTILINE)
        if not header_match:
            continue
        name = header_match.group(1).strip()
        if not name.startswith("Solution"):
            continue
        status = _extract_status(section)
        solutions.append({"name": name, "status": status})
    return solutions


_VALID_STATUSES = {"running", "pending", "done", "cancelled"}


def _extract_status(section_text: str) -> str:
    """섹션 텍스트에서 'status: <value>' 패턴을 찾아 반환. 없으면 'pending'."""
    m = re.search(r"^status:\s*(\S+)", section_text, re.MULTILINE)
    if m:
        value = m.group(1).strip().lower()
        if value in _VALID_STATUSES:
            return value
    return "pending"
