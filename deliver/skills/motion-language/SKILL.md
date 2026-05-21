---
name: motion-language
description: "Validate CSS transition consistency against RESPECT.md motion_language section — hover_transition_ms / page_transition_easing / scroll_reveal must all match. Scans .css/.scss/.tsx/.vue files for transition / animation / framer-motion props and reports drift. LLM 호출 0 — regex + CSSOM parsing. Use after a redesign or before ship to ensure motion personality stays coherent across all components ('마이크로 인터랙션 = 살아있다는 인상' 영상 4번 원칙)."
argument-hint: "[src directory or component file]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- RESPECT.md motion_language 의 명세를 코드 전체에 강제
- transition / animation / framer-motion 사용처 결정론 스캔
- 일관성 위반 → drift 보고 (어느 컴포넌트가 어디서 명세 어김)
- LLM 호출 0 — 정규식 + CSSOM 파싱

---

## Rule 5 회피 — 모든 검증이 결정론

| 검증 | 방법 | LLM |
|---|---|---|
| CSS `transition: <duration>` 추출 | 정규식 | ❌ |
| Tailwind `duration-<ms>` 추출 | 정규식 | ❌ |
| framer-motion `transition={duration:...}` props | AST 파서 | ❌ |
| easing 함수 (cubic-bezier) 매칭 | 문자열 매칭 | ❌ |
| RESPECT.md hover_transition_ms 와 비교 | 숫자 비교 | ❌ |

---

## 검증 대상 (default — 사용자 override 가능)

1. **hover_transition_ms**: 모든 :hover transition 의 duration
2. **page_transition_easing**: 페이지 전환의 easing 함수
3. **scroll_reveal**: scroll-triggered animation 의 stagger 값
4. **micro_interaction_consistency**: 같은 카테고리 컴포넌트 (button/card/modal) 의 motion 일관성

---

## Trigger Gate

### Use This Skill When
- 디자인 리뷰 후 motion 일관성 검증
- ship 직전 종합 craft-lint 의 motion 섹션
- 새 컴포넌트 추가 후 회귀 검증

### Route to Other Skills When
- 정적 메타데이터 (DESIGN.md + RESPECT.md) 검증 → `scripts/validate-craft-lint.py`
- 런타임 픽셀 측정 → `craft/hierarchy-rules`
- 화면 간 시각 일관성 → `craft/ui-drift-detect`

### Boundary Checks
- src 디렉터리 추정 (default `./src` + `./components`) — 명시 권장
- framer-motion 사용 시 import 자동 감지
- Tailwind JIT 사용 시 generated css 가 아닌 source class 스캔

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| src 경로 | $ARGUMENTS | 재귀 탐색 |
| RESPECT.md motion_language | `.design/RESPECT.md` | yaml 로드 |
| 파일 확장자 필터 | default `[".css",".scss",".tsx",".jsx",".vue",".svelte"]` | grep |

---

## Instructions

You are validating motion-language for: **$ARGUMENTS**

**Step 1 — RESPECT.md motion_language 로드**
- hover_transition_ms / page_transition_easing / scroll_reveal

**Step 2 — 파일 결정론 스캔**
```bash
grep -rn -E "transition:|transition-duration:|duration-[0-9]+|cubic-bezier\(" $src --include="*.css" --include="*.tsx"
```
- 각 hit 의 (파일, 라인, duration_ms, easing) 추출

**Step 3 — framer-motion props 추출 (AST)**
- `transition={{ duration: 0.2, ease: ... }}` 같은 패턴
- 단위 변환 (s → ms)

**Step 4 — RESPECT 명세와 비교**
- hover_transition_ms ± 50ms tolerance
- easing 함수 문자열 완전 일치
- 위반 사항 리스트

**Step 5 — drift 보고 출력**
- `.design/motion-drift.md` 작성:
```markdown
# Motion Drift Report

## hover_transition_ms (spec: 200ms ±50)
| 파일 | 라인 | 실측 | drift |
|---|---|---|---|
| src/Button.tsx | 14 | 150ms | -50 (within tolerance) ✅ |
| src/Card.tsx | 22 | 300ms | +100 ❌ |
| src/Modal.tsx | 8 | 0ms | -200 ❌ |

## page_transition_easing (spec: cubic-bezier(0.4, 0, 0.2, 1))
- src/routes/+layout.svelte: cubic-bezier(0.4, 0, 0.2, 1) ✅
- src/App.tsx: ease-in-out ❌ (spec mismatch)
```

**Step 6 — 통과/실패 판정**
- drift 0 → pass
- drift ≥ 1 → fail + 사용자에게 fix 권유

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| RESPECT.md motion_language 부재 | yaml key 누락 | `craft/respect-brief` 갱신 권유 |
| src 디렉터리 부재 | path not found | `--src` 명시 권유 |
| framer-motion AST 파싱 실패 | TSX 파서 에러 | 정규식 fallback + warning |
| Tailwind generated css 만 있음 | source class 0 | "source 파일 스캔 권유" warning |

---

## Quality Gate

- [ ] 5 motion 명세 모두 검증됨
- [ ] motion-drift.md 작성됨
- [ ] LLM 호출 0
- [ ] 실패 시 파일·라인 명시

---

## Examples

### Good Example
**입력:** "./src/components"

**기대 동작:** 12 컴포넌트 스캔, hover transition 11개 spec 일치, 1개 drift 발견 → motion-drift.md 1줄 보고

### Bad Example
**입력:** (인자 없음, RESPECT.md 없음)

**기대 동작:** fail loud

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Tailwind Duration Mapping
!`cat references/tailwind-duration.md 2>/dev/null || echo ""`

### Framer-motion Patterns
!`cat references/framer-patterns.md 2>/dev/null || echo ""`
