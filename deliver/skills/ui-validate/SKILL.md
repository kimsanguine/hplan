---
name: ui-validate
description: "Unified UI validation skill — hierarchy (Playwright DOM saliency + WCAG AA), motion (CSS transition vs RESPECT.md drift), drift (pHash N-screen consistency), mobile (375/768/1440px breakpoint). Each check is independently runnable and independently failable. --check 인자 미명시 시 에러 출력 후 사용 가능한 check 목록 안내 — auto-run 절대 금지."
argument-hint: "--check hierarchy|motion|drift|mobile [url or path or src dir]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

4종 UI 검증 check를 단일 인터페이스로 통합한다:

| check | 책임 | 출력 파일 | LLM |
|---|---|---|---|
| `--check hierarchy` | Playwright + DOM saliency + WCAG AA 시각 계층 측정 | `.design/hierarchy-report.json` | ❌ |
| `--check motion` | CSS transition vs RESPECT.md motion_language 일관성 | `.design/motion-drift.md` | ❌ |
| `--check drift` | N 화면 pHash + DOM 구조 시각 drift 감지 | `.design/ui-drift-report.md` | ❌ |
| `--check mobile` | 375/768/1440px 브레이크포인트 Playwright 검증 | `mobile-check-report.md` | ❌ |

> ⚠️ **`--check` 인자 필수**: 미명시 시 에러 출력 후 사용 가능한 check 목록 안내. auto-run 절대 금지.

---

## Rule 5 준수 — 모든 측정이 결정론

| 검증 | 도구 | LLM |
|---|---|---|
| fold_density, type_hierarchy, color_60_30_10, whitespace, cta_count | Playwright DOM + pixel | ❌ |
| WCAG AA contrast | WebAIM relative luminance 알고리즘 | ❌ |
| CSS transition duration/easing 추출 | 정규식 + CSSOM | ❌ |
| framer-motion props | AST 파서 | ❌ |
| pHash 비교 | imagehash library | ❌ |
| 색상 palette | KMeans on screenshot | ❌ |
| 브레이크포인트 Playwright | npx playwright test | ❌ |

---

## 실패 처리 원칙

- **각 check는 독립 실패 가능** — 한 check 실패가 다른 check를 막지 않음
- **baseline 없으면 SKIP** (FAIL 아님) — baseline 부재는 데이터 미비이지 위반이 아님
- **타임아웃**: 30초/check — 초과 시 해당 check SKIP + warning
- **respect-checkpoint·respect-brief**는 이 스킬에 통합하지 않음

---

## Trigger Gate

### Use This Skill When
- craft-lint 정적 검증 통과 후 런타임 측정 → `--check hierarchy`
- 리디자인 후 motion 일관성 검증 → `--check motion`
- 5+ 화면 생성 후 일관성 확인 → `--check drift`
- ship 직전 모바일 브레이크포인트 검증 → `--check mobile`

### Route to Other Skills When
- RESPECT.md 갱신 → `craft/respect-brief`
- ship 직전 종합 게이트 → `craft/respect-checkpoint`
- 디자인 토큰 갱신 → 프로젝트 DESIGN.md

### Boundary Checks
- `--check` 미명시 → 즉시 에러 + 사용 가능한 check 목록 출력 (auto-run 금지)
- Playwright 미설치 → fail loud + 설치 안내
- RESPECT.md 부재 시 hierarchy/motion → fail loud + "respect-brief 먼저"
- DESIGN.md 부재 시 mobile → fail loud + "design-token 먼저"

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--check` | `$ARGUMENTS` | hierarchy/motion/drift/mobile 분기 |
| target (URL/path/dir) | `$ARGUMENTS` (check 이후 나머지) | 각 check 내부 처리 |
| RESPECT.md | `.design/RESPECT.md` | hierarchy/motion 기준 |
| DESIGN.md | 프로젝트 루트 또는 `.design/DESIGN.md` | mobile 브레이크포인트 |

---

## Instructions

You are running ui-validate with arguments: **$ARGUMENTS**

### 공통 Step 0 — check 파싱

```
args = parse("$ARGUMENTS")
check = args.get("--check", None)
target = args remainder after --check value
```

`--check` 미명시 시:
```
❌ 에러: --check 인자가 필요합니다.

사용 가능한 check:
  --check hierarchy   Playwright DOM saliency + WCAG AA 시각 계층 측정
  --check motion      CSS transition vs RESPECT.md motion 일관성
  --check drift       N 화면 pHash 비교 시각 drift 감지
  --check mobile      375/768/1440px 브레이크포인트 검증

예시: ui-validate --check hierarchy https://habix.ai
     ui-validate --check mobile http://localhost:3000
```

---

### check: hierarchy

**대상**: URL 또는 HTML 경로

**Step 1 — Playwright + RESPECT.md 로드**
- `npx playwright install` 확인
- `.design/RESPECT.md` yaml 파싱 → hierarchy_rules 섹션
- RESPECT.md 부재 시 fail loud

**Step 2 — 5 룰 + WCAG 결정론 측정 (LLM 0)**

```python
# 측정 알고리즘 (의사코드)
page = playwright.new_page(viewport={"width": 1440, "height": 1080})
page.goto(target)

# Rule 1 — fold_density
elements = page.eval("...above-fold elements count...")
fold_pass = elements <= rules["max_elements_above_fold"]

# Rule 2 — type_hierarchy
sizes_px = sorted(unique font sizes from CSSOM, reverse=True)
ratios = [sizes_px[i] / sizes_px[i+1] for i]
type_pass = len(sizes_px) <= rules["max_type_scale"] and all(r >= 1.25 for r)

# Rule 3 — color_60_30_10
screenshot → KMeans(3) → percentages
color_pass = all(abs(pct[i] - target[i]) <= 10 for i in range(3))

# Rule 4 — whitespace_ratio
light_mask = pixels > 240; ratio = light_mask.sum() / total
whitespace_pass = ratio >= rules["whitespace_min"]

# Rule 5 — cta_count_above_fold
ctas_above = [c for c in page.locator("button, a[role='button'], .cta").all() if y < 1080]
cta_pass = len(ctas_above) == rules["cta_count_above_fold"]

# WCAG AA contrast
all text elements → (foreground, background) → relative luminance ratio
wcag_violations = [e for e if ratio < 4.5 (normal) or < 3.0 (large 18pt+)]
```

**Step 3 — `.design/hierarchy-report.json` 출력**

**Step 4 — 통과/실패 판정**
- 모두 pass → "hierarchy check PASS"
- 실패 시 element selector + fix 권유

---

### check: motion

**대상**: src 디렉터리 또는 컴포넌트 파일 경로

**Step 1 — RESPECT.md motion_language 로드**
- hover_transition_ms / page_transition_easing / scroll_reveal
- 부재 시 fail loud

**Step 2 — 파일 결정론 스캔 (LLM 0)**
```bash
grep -rn -E "transition:|duration-[0-9]+|cubic-bezier\(" $target \
  --include="*.css" --include="*.scss" --include="*.tsx" --include="*.jsx" --include="*.vue"
```

**Step 3 — framer-motion props 추출 (AST)**
- `transition={{ duration: N }}` 패턴 → 단위 변환 (s → ms)

**Step 4 — RESPECT 명세와 비교**
- hover_transition_ms ± 50ms tolerance
- easing 함수 문자열 완전 일치
- 위반 사항 리스트

**Step 5 — `.design/motion-drift.md` 출력**

**Step 6 — 통과/실패 판정**
- drift 0 → PASS
- drift ≥ 1 → FAIL + 파일·라인 명시

---

### check: drift

**대상**: URL 리스트 (쉼표 구분) 또는 스크린샷 디렉터리 경로

**Step 1 — 화면 캡처 또는 스크린샷 로드**
- URL 입력 → Playwright 다중 navigate + screenshot
- 디렉터리 입력 → PNG 파일 로드

**Step 2 — 각 화면 메트릭 결정론 추출**
- pHash (16-bit perceptual hash)
- color palette top 5 (KMeans)
- font-family set (DOM scrape)
- spacing 모드값 (margin/padding 빈도 top 3)
- DOM tree depth + node count

**Step 3 — baseline 대비 drift score 계산 (LLM 0)**
```python
drift = {
    "phash": hamming_distance(baseline.phash, current.phash),
    "color": palette_distance(baseline.palette, current.palette),
    "font": jaccard_distance(baseline.fonts, current.fonts),
    "spacing": rmse(baseline.spacing, current.spacing),
    "structure": tree_edit_distance(baseline.dom, current.dom),
}
```

**Step 4 — drift 임계치 비교**
- phash > 40: drift
- color: palette 변경 1개 이상 + 비중 > 10%: drift
- font: 기존 family 외 새 font: drift
- spacing: rmse > 4px: drift
- structure: edit_distance > 30: drift

**Step 5 — `.design/ui-drift-report.md` 출력**

**Step 6 — 종합 verdict**
- drift 0 → PASS
- drift ≥ 1 화면 → fix 권유 + design-system 회귀 의심

---

### check: mobile

**대상**: URL 또는 기본값 `http://localhost:3000`

**Step 1 — DESIGN.md 존재 확인**
- 없으면 fail loud + "design-token 먼저"

**Step 2 — Playwright 환경 확인**
```bash
npx playwright --version 2>/dev/null || echo "not installed"
```

**Step 3 — Playwright 테스트 파일 확인/생성**
- `tests/design/mobile-check.spec.ts` 없으면 references/playwright-setup.md 기반 생성

**Step 4 — 3 뷰포트 실행**
```bash
TARGET_URL=${target:-http://localhost:3000} \
  npx playwright test tests/design/mobile-check.spec.ts --reporter=line 2>&1
```

**Step 5 — ASCII 결과 출력**
```
┌─── mobile-check 결과 ────────────────────────────┐
│  375px   ✅/❌ N/3                               │
│  768px   ✅/❌ N/3                               │
│  1440px  ✅/❌ N/1                               │
│  이슈: (있을 때만)                               │
│  수정 후 재실행: ui-validate --check mobile      │
└──────────────────────────────────────────────────┘
```

**Step 6 — 리포트 저장**
- 이슈 1개 이상 → `mobile-check-report.md` 생성
- 이슈 없음 → 파일 생성 안 함

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| --check 미명시 | 파싱 결과 None | 에러 출력 + check 목록 안내, 실행 중단 |
| Playwright 미설치 | which playwright 실패 | `npm install playwright && npx playwright install` 권유 |
| RESPECT.md 부재 (hierarchy/motion) | file not found | "craft/respect-brief 먼저" fail loud |
| DESIGN.md 부재 (mobile) | file not found | "design-token 먼저" fail loud |
| baseline 없음 (drift) | 화면 수 < 2 | SKIP (FAIL 아님) + warning |
| 타임아웃 30초 초과 | per-check timeout | 해당 check SKIP + warning, 나머지 계속 |
| 화면 수 < 3 (drift) | argument count | "최소 3 화면 필요" warning + SKIP |

---

## Quality Gate

- [ ] --check 인자 미명시 시 에러 + 목록 안내 (auto-run 0)
- [ ] hierarchy: 5 룰 + WCAG AA 모두 측정, LLM 호출 0
- [ ] motion: CSS/framer-motion 모두 스캔, motion-drift.md 출력, LLM 호출 0
- [ ] drift: 5 차원 모두 측정, baseline 명시, LLM 호출 0
- [ ] mobile: 3 뷰포트 모두 검증, ASCII 결과 출력
- [ ] 각 check 독립 실패 가능 (한 check FAIL이 다른 check를 막지 않음)

---

## Examples

### Good Example
**입력:** `--check hierarchy https://habix.ai`

**기대 동작:**
1. Playwright 1440×1080 navigate
2. 5 룰 + WCAG AA 결정론 측정
3. hierarchy-report.json 출력
4. 실패 항목 element selector 명시

### Good Example
**입력:** `--check mobile`

**기대 동작:**
1. DESIGN.md 확인
2. 3 뷰포트 (375/768/1440) Playwright 실행
3. ASCII 결과 출력
4. 실패 시 mobile-check-report.md 생성

### Bad Example
**입력:** `ui-validate` (--check 없음)

**기대 동작:**
```
❌ 에러: --check 인자가 필요합니다.
사용 가능한 check: hierarchy | motion | drift | mobile
```
실행 중단. auto-run 금지.

### Bad Example
**입력:** `--check hierarchy` (RESPECT.md 없음)

**기대 동작:** "RESPECT.md 부재 — craft/respect-brief 먼저" fail loud

---

## Contextual Knowledge (auto-loaded)

### Playwright Setup
!`cat references/playwright-setup.md 2>/dev/null || echo ""`

### WCAG Algorithm
!`cat references/wcag-algorithm.md 2>/dev/null || echo ""`

### pHash Calibration
!`cat references/phash-tuning.md 2>/dev/null || echo ""`

### Tailwind Duration Mapping
!`cat references/tailwind-duration.md 2>/dev/null || echo ""`
