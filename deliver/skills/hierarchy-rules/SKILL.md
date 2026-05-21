---
name: hierarchy-rules
description: "Measure visual hierarchy rules at runtime via Playwright + DOM saliency + WCAG AA — fold_density (count of elements above 1080px viewport fold), type_hierarchy (unique font sizes + consecutive size ratios ≥ 1.25), color_60_30_10 (pixel-level color distribution clustered to 3 primary colors), whitespace_ratio (empty pixels / content pixels ≥ RESPECT.md threshold), cta_count_above_fold (exactly 1 per RESPECT.md). All thresholds are loaded from RESPECT.md — this skill is the runtime enforcement arm. Doubles as data supplier for track/respect-checkpoint γ gate."
argument-hint: "[url or path/to/page.html]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- RESPECT.md 의 hierarchy_rules 섹션을 런타임 측정 + 통과/실패 판정
- Playwright (headless browser) + pixel analysis + DOM 측정 — LLM 호출 0
- 5개 룰 모두 결정론 임계치 비교
- track/respect-checkpoint γ 게이트의 데이터 공급원 (재사용)

---

## Rule 5 회피 — 모든 측정이 결정론

| 측정 | 도구 | LLM |
|---|---|---|
| fold_density (above 1080px viewport) | Playwright DOM bounding box + count | ❌ |
| type_hierarchy (font sizes + ratio) | CSSOM 파싱 + numpy ratio | ❌ |
| color_60_30_10 (pixel distribution) | Playwright screenshot + KMeans clustering | ❌ |
| whitespace_ratio (empty/content pixels) | screenshot + pixel mask | ❌ |
| cta_count_above_fold (button/link role) | Playwright accessibility tree | ❌ |
| WCAG AA contrast (text/background) | WebAIM 알고리즘 (relative luminance) | ❌ |

LLM 사용 0 — 모두 결정론.

---

## 5 룰 측정 알고리즘 (의사코드)

```python
async def measure(url, respect_md):
    page = await browser.new_page(viewport={"width": 1440, "height": 1080})
    await page.goto(url)
    rules = yaml.safe_load(respect_md)["hierarchy_rules"]
    results = {}

    # Rule 1 — fold_density
    elements = await page.eval("[...document.querySelectorAll('*')]"
                               ".filter(e => e.getBoundingClientRect().top < 1080 && "
                               "  e.offsetWidth > 0 && e.offsetHeight > 0).length")
    results["fold_density"] = elements <= rules["max_elements_above_fold"]

    # Rule 2 — type_hierarchy
    sizes = await page.eval("[...new Set([...document.querySelectorAll('*')]"
                            ".map(e => getComputedStyle(e).fontSize))]")
    sizes_px = sorted([float(s.replace("px","")) for s in sizes], reverse=True)
    ratios = [sizes_px[i] / sizes_px[i+1] for i in range(len(sizes_px)-1)]
    results["type_hierarchy"] = (
        len(sizes_px) <= rules["max_type_scale_per_screen"] and
        all(r >= 1.25 for r in ratios)
    )

    # Rule 3 — color_60_30_10
    screenshot = await page.screenshot(clip={"x":0,"y":0,"width":1440,"height":1080})
    pixels = np.frombuffer(screenshot, dtype=np.uint8).reshape(-1, 4)[:, :3]
    kmeans = KMeans(n_clusters=3).fit(pixels)
    pct = sorted(np.bincount(kmeans.labels_) / len(pixels) * 100, reverse=True)
    target = sorted(rules["color_ratio"], reverse=True)
    results["color_60_30_10"] = all(abs(pct[i] - target[i]) <= 10 for i in range(3))

    # Rule 4 — whitespace_ratio
    light_mask = np.all(pixels > 240, axis=1)
    ratio = light_mask.sum() / len(pixels)
    results["whitespace"] = ratio >= rules["whitespace_to_content_min"]

    # Rule 5 — cta_count_above_fold
    ctas = await page.locator("button, a[role='button'], .cta").all()
    above_fold = [c for c in ctas if (await c.bounding_box())["y"] < 1080]
    results["cta_count"] = len(above_fold) == rules["cta_count_above_fold"]

    return results
```

---

## Trigger Gate

### Use This Skill When
- craft-lint 의 정적 검증 통과 후 런타임 측정
- track/respect-checkpoint γ 게이트 호출
- RESPECT.md 갱신 후 회귀 검증

### Route to Other Skills When
- 메타데이터·cross-ref 검증 (런타임 측정 전) → `scripts/validate-craft-lint.py`
- ship 직전 종합 게이트 → `track/respect-checkpoint` (γ 호출 포함)
- 디자인 토큰 갱신 → Google DESIGN.md

### Boundary Checks
- Playwright 미설치 → fail loud + `npm install playwright @playwright/test` 권유
- viewport 다중 (mobile/tablet/desktop) 검증 필요 → `--viewport mobile|tablet|desktop|all`
- 동적 콘텐츠 (스피너·skeleton) — wait_for_load_state("networkidle") 필수

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| URL 또는 HTML 경로 | $ARGUMENTS | Playwright navigate |
| RESPECT.md | `.design/RESPECT.md` | yaml hierarchy_rules 로드 |
| viewport spec | `--viewport` 인자 | 기본 1440×1080 |
| WCAG level | hardcoded "AA" (사용자 override 가능) | 4.5:1 / 3:1 임계 |

---

## Instructions

You are measuring hierarchy rules for: **$ARGUMENTS**

**Step 1 — Playwright + RESPECT.md 로드**
- `npx playwright install` 확인
- RESPECT.md yaml 파싱

**Step 2 — 5 룰 + WCAG 결정론 측정**
- 위 의사코드 그대로 실행
- 각 룰 pass/fail + 측정값 기록

**Step 3 — WCAG AA contrast 측정**
- 모든 text element 의 foreground/background contrast
- 4.5:1 (normal) / 3:1 (large 18pt+) 임계
- 미달 항목 element selector + ratio 기록

**Step 4 — γ 게이트 데이터 출력**
- `.design/hierarchy-report.json` 작성:
```json
{
  "url": "...",
  "viewport": "1440x1080",
  "fold_density": {"pass": true, "actual": 5, "max": 7},
  "type_hierarchy": {"pass": false, "actual_count": 6, "max": 4, "ratios": [1.3, 1.1, ...]},
  "color_60_30_10": {"pass": true, "actual": [58, 32, 10], "target": [60, 30, 10]},
  "whitespace": {"pass": true, "actual": 0.43, "min": 0.4},
  "cta_count": {"pass": true, "actual": 1, "target": 1},
  "wcag_aa": {"pass": false, "violations": [{"selector": ".subtitle", "ratio": 3.8}]}
}
```

**Step 5 — 통과/실패 판정**
- 모두 pass → respect-checkpoint γ pass 신호
- 1개라도 fail → fix 권유 + 실패 element selector 명시

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| Playwright 미설치 | which playwright 실패 | `npm install playwright && npx playwright install` 권유 |
| URL 로드 실패 (네트워크) | 30s timeout | fail loud + 재시도 옵션 |
| KMeans 클러스터링 실패 (단색 화면) | n_clusters > unique colors | 색 수 ≤ 3 인 화면은 60/30/10 skip + warning |
| WCAG 측정 시 텍스트 elements 0 | querySelector empty | "텍스트 없는 화면 — WCAG skip" |
| viewport mismatch (mobile RESPECT 인데 desktop 측정) | 사용자 명시 안 됨 | default desktop + warning |

---

## Quality Gate

- [ ] 5 룰 모두 측정됨
- [ ] WCAG AA contrast 측정됨
- [ ] hierarchy-report.json 작성됨
- [ ] LLM 호출 0 (모든 측정이 Playwright + pixel + DOM 결정론)
- [ ] 실패 시 element selector 명시 (fix 가능)

---

## Examples

### Good Example
**입력:** "https://habix.ai"

**기대 동작:**
1. Playwright 1440×1080 navigate
2. fold_density 5 ≤ 7 ✅
3. type_hierarchy 4 sizes, ratios all ≥ 1.25 ✅
4. color 62/30/8 within ±10 of [60,30,10] ✅
5. whitespace 0.43 ≥ 0.4 ✅
6. cta_count 1 == 1 ✅
7. WCAG AA pass
8. respect-checkpoint γ pass 신호

### Bad Example
**입력:** RESPECT.md 없이 임의 URL

**기대 동작:** "RESPECT.md 부재 — craft/respect-brief 먼저" fail loud

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Playwright Setup
!`cat references/playwright-setup.md 2>/dev/null || echo ""`

### WCAG Algorithm
!`cat references/wcag-algorithm.md 2>/dev/null || echo ""`
