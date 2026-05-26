import re
from .generic import parse_generic


def parse_sprint_tracker(md: str) -> dict:
    base = parse_generic(md)
    milestones = _extract_milestones(md)
    total_done = sum(m["done"] for m in milestones)
    total_items = sum(m["total"] for m in milestones)
    cogs_ceiling = _parse_cogs(md, "ceiling")
    cogs_current = _parse_cogs(md, "current")
    return {
        **base,
        "template": "sprint-tracker",
        "milestones": milestones,
        "total_done": total_done,
        "total_items": total_items,
        "cogs_ceiling": cogs_ceiling,
        "cogs_current": cogs_current,
        "cogs_ok": cogs_current <= cogs_ceiling,
    }


def _extract_milestones(md: str) -> list[dict]:
    """## 섹션별로 체크리스트 아이템을 수집한다."""
    milestones = []
    current_name: str | None = None
    current_items: list[dict] = []

    for line in md.splitlines():
        # ## 헤딩 감지 (### 이상은 제외 — ## 만)
        h2 = re.match(r"^##\s+(.+)$", line)
        if h2:
            if current_name is not None:
                milestones.append(_make_milestone(current_name, current_items))
            current_name = h2.group(1).strip()
            current_items = []
            continue

        # # 헤딩 (H1) — 새 섹션이 아니지만 현재 섹션 종료 불필요
        if re.match(r"^#\s+", line) and not re.match(r"^##", line):
            continue

        # 체크리스트 아이템
        if current_name is not None:
            done_match = re.match(r"^-\s+\[x\]\s+(.+)$", line, re.IGNORECASE)
            todo_match = re.match(r"^-\s+\[ \]\s+(.+)$", line)
            if done_match:
                text = done_match.group(1).strip()
                current_items.append({
                    "text": text,
                    "done": True,
                    "is_blocker": "블로커" in text.lower(),
                })
            elif todo_match:
                text = todo_match.group(1).strip()
                current_items.append({
                    "text": text,
                    "done": False,
                    "is_blocker": "블로커" in text.lower(),
                })

    # 마지막 섹션 플러시
    if current_name is not None:
        milestones.append(_make_milestone(current_name, current_items))

    return milestones


def _make_milestone(name: str, items: list[dict]) -> dict:
    done = sum(1 for i in items if i["done"])
    total = len(items)
    pct = round(done / total * 100) if total > 0 else 0
    return {
        "name": name,
        "done": done,
        "total": total,
        "pct": pct,
        "items": items,
    }


def _parse_cogs(md: str, kind: str) -> int:
    """'COGS p90 ceiling' 또는 'COGS p90 current' 값 추출. 없으면 0."""
    pattern = rf"COGS p90 {kind}:\s*(\d+)%?"
    m = re.search(pattern, md, re.IGNORECASE)
    return int(m.group(1)) if m else 0
