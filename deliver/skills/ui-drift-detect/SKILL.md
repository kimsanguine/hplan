---
name: ui-drift-detect
description: "Detect visual drift across N screens — Playwright screenshots + pHash perceptual hashing + structural diff (DOM tree similarity) to ensure new screens preserve decisions made in earlier screens (color palette, spacing rhythm, typography, component shapes). Flags screens where the design language quietly diverges. LLM 호출 0 — all comparisons are pixel + DOM. Use after generating 5+ screens in a sprint, or before ship to verify the design system held."
argument-hint: "[urls or dir of screenshots]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- 5+ 화면을 시각·DOM 결정론 비교
- color palette / spacing / typography / component shape 의 drift 감지
- 가장 일관성 떨어지는 화면 + 어느 차원에서 drift 명시
- LLM 호출 0 — pHash + DOM tree edit distance

---

## Rule 5 회피 — 모든 비교가 결정론

| 차원 | 측정 | LLM |
|---|---|---|
| perceptual hash (pHash) | imagehash library | ❌ |
| color palette extraction | KMeans on screenshot | ❌ |
| spacing rhythm | computed margin/padding 모드값 | ❌ |
| typography drift | font-family / size 집합 차이 | ❌ |
| DOM structural similarity | tree edit distance (zhang-shasha) | ❌ |

---

## Trigger Gate

### Use This Skill When
- 5+ 새 화면 생성 후 일관성 검증
- ship 직전 craft-lint 종합 패스
- 디자인 시스템 회귀 의심 (예: 새 컴포넌트가 기존 스타일 깸)

### Route to Other Skills When
- 단일 화면의 hierarchy 측정 → `craft/hierarchy-rules`
- motion 일관성 → `craft/motion-language`
- 정적 토큰 검증 → `scripts/validate-craft-lint.py`

### Boundary Checks
- 화면 수 < 3 → drift 측정 의미 ↓ + warning
- 화면이 의도적으로 다른 카테고리 (랜딩 vs 대시보드) → `--cluster-by-screen-type` 옵션
- 다국어 화면 비교 시 텍스트 길이 차이 무시 모드

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| URL 리스트 | $ARGUMENTS (쉼표 구분) | Playwright 다중 navigate |
| 또는 스크린샷 디렉터리 | $ARGUMENTS (path) | imghdr 자동 감지 |
| viewport | `--viewport` (default 1440×1080) | Playwright option |
| baseline 화면 | 첫 입력 또는 `--baseline` | 비교 기준 |

---

## Instructions

You are detecting UI drift across: **$ARGUMENTS**

**Step 1 — 화면 캡처 (URL 입력 시)**
- Playwright 다중 navigate + screenshot
- 또는 입력 디렉터리에서 PNG 로드

**Step 2 — 각 화면 메트릭 결정론 추출**
- pHash (16-bit perceptual hash)
- color palette top 5 (KMeans)
- font-family set (DOM scrape)
- spacing 모드값 (margin/padding 빈도 top 3)
- DOM tree depth + node count

**Step 3 — baseline 대비 drift score 계산**
```python
def drift_score(baseline, current):
    return {
        "phash": hamming_distance(baseline.phash, current.phash),  # 0-256
        "color": palette_distance(baseline.palette, current.palette),  # 0-1
        "font": jaccard_distance(baseline.fonts, current.fonts),  # 0-1
        "spacing": rmse(baseline.spacing, current.spacing),  # 0-N
        "structure": tree_edit_distance(baseline.dom, current.dom),  # 0-N
    }
```

**Step 4 — drift 임계치 비교 (default — 사용자 override)**
- phash > 40: 너무 다름 (의도적인가?)
- color: palette 변경 1개 이상 + 비중 > 10% → drift
- font: 기존 family 외 새 font 등장 → drift
- spacing: rmse > 4px → drift
- structure: edit_distance > 30 → drift

**Step 5 — 보고서 작성**
- `.design/ui-drift-report.md`:
```markdown
# UI Drift Report (baseline: landing.html)

| 화면 | pHash | color | font | spacing | structure | verdict |
|---|---|---|---|---|---|---|
| dashboard | 18 | 0.05 | 0 | 2px | 22 | ✅ within tolerance |
| pricing | 56 | 0.18 | 1 (Roboto 추가) | 12px | 45 | ❌ multi-dim drift |
| about | 22 | 0.08 | 0 | 3px | 19 | ✅ |

## 🚨 pricing.html — multi-dim drift
- color: brand teal 30% → 18%, 새 muted gray 추가
- font: Roboto 등장 (spec: Inter only)
- spacing: 16px 모드 → 24px (rhythm 깨짐)
- 권고: design system token 강제 + craft-lint 통과 확인
```

**Step 6 — 종합 verdict**
- drift 0 → pass
- drift ≥ 1 화면 → fix 권유 + design-system 회귀 의심

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 화면 수 < 3 | argument count | "drift 측정 의미 낮음" warning + skip |
| baseline 명시 안 됨 | --baseline default | 첫 입력 자동 baseline + 사용자 알림 |
| 스크린샷 캡처 실패 | Playwright timeout | retry 1회 + fail loud |
| pHash 라이브러리 미설치 | import error | `pip install imagehash` 권유 |
| DOM tree 추출 실패 (정적 HTML) | innerHTML empty | 정적 mode (pHash + color 만) fallback |

---

## Quality Gate

- [ ] 5 차원 모두 측정됨 (pHash / color / font / spacing / structure)
- [ ] baseline 명시 + 각 화면 drift score 출력
- [ ] LLM 호출 0
- [ ] drift 발견 시 fix 권유 (어느 차원, 어떻게)
- [ ] ui-drift-report.md 작성

---

## Examples

### Good Example
**입력:** "https://habix.ai, https://habix.ai/pricing, https://habix.ai/about, https://habix.ai/blog, https://habix.ai/contact"

**기대 동작:** 5 화면 캡처, baseline = habix.ai, 1 화면 (pricing) 에서 multi-dim drift 발견 → 보고서

### Bad Example
**입력:** "https://habix.ai" (1개)

**기대 동작:** "최소 3 화면 필요" warning + skip

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### pHash Calibration
!`cat references/phash-tuning.md 2>/dev/null || echo ""`

### Tree Edit Distance Tuning
!`cat references/tree-edit-tuning.md 2>/dev/null || echo ""`
