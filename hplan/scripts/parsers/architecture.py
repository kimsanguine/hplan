import re
from .generic import parse_generic


def parse_architecture(md: str) -> dict:
    base = parse_generic(md)
    return {
        **base,
        "template": "architecture-blueprint",
        "mermaid_code": _extract_mermaid_code(md),
        "routing_table": _extract_routing_table(md),
        "memory_short": _extract_memory_field(md, "단기"),
        "memory_long": _extract_memory_field(md, "장기"),
    }


def _extract_mermaid_code(md: str) -> str:
    """```mermaid ... ``` 펜스 사이의 내용을 반환. 없으면 빈 문자열."""
    m = re.search(r"```mermaid\n(.*?)```", md, re.DOTALL)
    if not m:
        return ""
    return m.group(1).rstrip("\n")


def _parse_table_row(line: str) -> list[str]:
    """파이프로 구분된 테이블 행을 파싱해 셀 리스트로 반환."""
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    """구분자 행 여부 확인 (각 셀이 --- 패턴)."""
    return all(re.fullmatch(r"[-: ]+", cell) for cell in cells if cell)


def _extract_routing_table(md: str) -> dict:
    """## Routing 섹션의 첫 번째 테이블을 파싱. 없으면 빈 테이블 반환."""
    # ## Routing 섹션 범위 추출
    routing_section = _extract_section(md, "Routing")
    target = routing_section if routing_section else md

    lines = target.splitlines()
    table_lines = [l for l in lines if l.strip().startswith("|")]

    if not table_lines:
        return {"headers": [], "rows": []}

    headers = _parse_table_row(table_lines[0])
    rows: list[list[str]] = []
    for line in table_lines[1:]:
        cells = _parse_table_row(line)
        if _is_separator_row(cells):
            continue
        rows.append(cells)

    return {"headers": headers, "rows": rows}


def _extract_section(md: str, heading: str) -> str | None:
    """## <heading> 으로 시작하는 섹션을 반환. 다음 ## 헤딩 직전까지."""
    pattern = rf"^##\s+{re.escape(heading)}\s*$"
    lines = md.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(pattern, line, re.IGNORECASE):
            start = i + 1
            break
    if start is None:
        return None

    # 다음 ## 헤딩까지 수집
    section_lines = []
    for line in lines[start:]:
        if re.match(r"^##\s+", line):
            break
        section_lines.append(line)
    return "\n".join(section_lines)


def _extract_memory_field(md: str, label: str) -> str:
    """## Memory 섹션에서 '<label>: <value>' 패턴의 값을 반환. 없으면 빈 문자열."""
    memory_section = _extract_section(md, "Memory")
    if not memory_section:
        return ""
    pattern = rf"^{re.escape(label)}:\s*(.+)"
    m = re.search(pattern, memory_section, re.MULTILINE)
    if not m:
        return ""
    return m.group(1).strip()
