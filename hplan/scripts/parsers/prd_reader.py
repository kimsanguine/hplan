import re
from .generic import parse_generic


def parse_prd_reader(md: str) -> dict:
    base = parse_generic(md)
    sections = [h for h in base["headings"] if h["level"] == 2]
    return {
        **base,
        "template": "prd-reader",
        "evidence_score": _extract_int_comment(md, "evidence_score", 0),
        "cogs_verdict": _extract_str_comment(md, "cogs_verdict", "").upper(),
        "state": _extract_str_comment(md, "state", ""),
        "sections": sections,
        "mermaid_code": _extract_mermaid_code(md),
    }


def _extract_int_comment(md: str, key: str, default: int) -> int:
    """<!-- key: N --> 패턴에서 정수 추출."""
    m = re.search(rf"<!--\s*{key}:\s*(\d+)\s*-->", md)
    if m:
        return int(m.group(1))
    return default


def _extract_str_comment(md: str, key: str, default: str) -> str:
    """<!-- key: value --> 패턴에서 문자열 추출."""
    m = re.search(rf"<!--\s*{key}:\s*(\S+)\s*-->", md)
    if m:
        return m.group(1).strip()
    return default


def _extract_mermaid_code(md: str) -> str:
    """```mermaid ... ``` 펜스 사이의 내용을 반환. 없으면 빈 문자열."""
    m = re.search(r"```mermaid\n(.*?)```", md, re.DOTALL)
    if not m:
        return ""
    return m.group(1).rstrip("\n")
