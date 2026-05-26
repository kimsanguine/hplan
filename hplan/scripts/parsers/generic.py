import re


def parse_generic(md: str) -> dict:
    """범용 MD 파서. 제목·헤딩·Mermaid 블록 감지."""
    title = _extract_title(md)
    headings = _extract_headings(md)
    has_mermaid = bool(re.search(r"```mermaid", md))
    return {
        "title": title,
        "headings": headings,
        "has_mermaid": has_mermaid,
        "body_md": md,
        "template": "generic",
    }


def _extract_title(md: str) -> str:
    # frontmatter title 우선
    fm = re.search(r"^---\s*\ntitle:\s*(.+?)\s*\n", md, re.MULTILINE)
    if fm:
        return fm.group(1).strip()
    # H1
    h1 = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
    if h1:
        return h1.group(1).strip()
    return "Untitled"


def _extract_headings(md: str) -> list[dict]:
    headings = []
    for m in re.finditer(r"^(#{1,3})\s+(.+)$", md, re.MULTILINE):
        level = len(m.group(1))
        text = m.group(2).strip()
        slug = re.sub(r"[^\w가-힣-]", "", text.lower().replace(" ", "-"))
        headings.append({"level": level, "text": text, "slug": slug})
    return headings
