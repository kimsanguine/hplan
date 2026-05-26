import re
from .generic import parse_generic


def parse_design_system(md: str) -> dict:
    base = parse_generic(md)
    return {
        **base,
        "template": "design-system",
        "colors": _extract_colors(md),
        "typography": _extract_typography(md),
        "tailwind_tokens": _extract_tailwind_tokens(md),
    }


def _section(md: str, heading: str) -> str:
    """## <heading> 섹션 텍스트 반환. 다음 ## 헤딩 전까지. 없으면 빈 문자열.

    주의: [^#]+ 정규식은 HEX 컬러값 '#...'의 # 문자에서 끊기므로
    splitlines 방식으로 섹션을 수집한다.
    """
    lines = md.splitlines()
    pattern = re.compile(rf"^##\s+{re.escape(heading)}\s*$")
    in_section = False
    section_lines: list[str] = []
    for line in lines:
        if pattern.match(line):
            in_section = True
            continue
        if in_section:
            if re.match(r"^##", line):
                break
            section_lines.append(line)
    return "\n".join(section_lines)


def _extract_colors(md: str) -> list[dict]:
    section = _section(md, "Color Palette")
    if not section:
        return []

    colors = []
    # HEX 색상 매칭 (태스크 명세 정규식)
    for m in re.finditer(r"-\s+([^:]+):\s+(#[0-9A-Fa-f]{3,8})\b", section):
        colors.append({
            "name": m.group(1).strip(),
            "hex": m.group(2),
            "rgb": None,
        })
    # RGB 색상 매칭 (태스크 명세 정규식)
    for m in re.finditer(r"-\s+([^:]+):\s+(rgb\([^)]+\))", section):
        colors.append({
            "name": m.group(1).strip(),
            "hex": None,
            "rgb": m.group(2),
        })
    return colors


def _extract_typography(md: str) -> list[dict]:
    section = _section(md, "Typography")
    if not section:
        return []

    typography = []
    pattern = r"-\s+([^:]+):\s+(\d+px)\s*/\s*font-weight\s+(\d+)"
    for m in re.finditer(pattern, section):
        typography.append({
            "name": m.group(1).strip(),
            "size": m.group(2),
            "weight": m.group(3),
        })
    return typography


def _extract_tailwind_tokens(md: str) -> list[str]:
    section = _section(md, "Tailwind Tokens")
    if not section:
        return []

    tokens = []
    for m in re.finditer(r"`([a-z][a-z0-9-]+)`", section):
        tokens.append(m.group(1))
    return tokens
