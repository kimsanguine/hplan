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


def _slugify(text: str) -> str:
    """Python slug — em-dash 정규화 후 공백→'-', 비단어 제거."""
    t = text.lower()
    t = t.replace("—", "-").replace("–", "-")
    t = t.replace(" ", "-")
    t = re.sub(r"[^\w가-힣-]", "", t)
    return t


def _extract_title(md: str) -> str:
    # frontmatter title 우선 (파일 시작에 고정)
    fm = re.search(r"\A---\s*\ntitle:\s*(.+?)\s*\n", md)
    if fm:
        return fm.group(1).strip().strip("\"'")
    # H1 (코드 블록 제외)
    stripped = re.sub(r"```.*?```", "", md, flags=re.DOTALL)
    h1 = re.search(r"^#\s+(.+)$", stripped, re.MULTILINE)
    if h1:
        return h1.group(1).strip()
    return "Untitled"


def _extract_headings(md: str) -> list[dict]:
    # 코드 블록 내의 행을 제외하고 매치
    stripped = re.sub(r"```.*?```", "", md, flags=re.DOTALL)
    headings = []
    for m in re.finditer(r"^(#{1,3})\s+(.+)$", stripped, re.MULTILINE):
        level = len(m.group(1))
        text = m.group(2).strip()
        slug = _slugify(text)
        headings.append({"level": level, "text": text, "slug": slug})
    return headings
