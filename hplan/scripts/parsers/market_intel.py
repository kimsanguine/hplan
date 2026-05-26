import re
from .generic import parse_generic


def parse_market_intel(md: str) -> dict:
    base = parse_generic(md)
    table_headers, table_rows = _extract_table(md)
    return {
        **base,
        "template": "market-intel",
        "table_headers": table_headers,
        "table_rows": table_rows,
    }


def _parse_table_row(line: str) -> list[str]:
    """파이프로 구분된 테이블 행을 파싱해 셀 리스트로 반환."""
    stripped = line.strip().strip("|")
    return [cell.strip() for cell in stripped.split("|")]


def _is_separator_row(cells: list[str]) -> bool:
    """구분자 행 여부 확인 (각 셀이 --- 패턴)."""
    return all(re.fullmatch(r"[-: ]+", cell) for cell in cells if cell)


def _extract_table(md: str) -> tuple[list[str], list[list[str]]]:
    """첫 번째 마크다운 테이블을 파싱해 (headers, rows) 반환."""
    lines = md.splitlines()
    table_lines = [l for l in lines if l.strip().startswith("|")]

    if not table_lines:
        return [], []

    # 첫 행 = 헤더
    headers = _parse_table_row(table_lines[0])

    rows: list[list[str]] = []
    for line in table_lines[1:]:
        cells = _parse_table_row(line)
        if _is_separator_row(cells):
            continue
        rows.append(cells)

    return headers, rows
