---
name: design-token
description: "2-step 디자인 파이프라인: --step brief (타겟 분석 → DESIGN_BRIEF.md 생성) → --step token (토큰/DESIGN.md 생성). --step all이 기본값."
argument-hint: "[타겟 또는 DESIGN_BRIEF.md 경로] [--step brief|token|all]"
allowed-tools: ["Read", "Write"]
model: inherit
---

# design-token

## 목적
2-step 디자인 파이프라인: Phase A (레퍼런스 수집 → DESIGN_BRIEF.md 생성) → Phase B (토큰/DESIGN.md 생성).

Parse `--step` from `$ARGUMENTS`:
- `--step brief` → Run Phase A only (design-reference 로직)
- `--step token` → Run Phase B only (기존 design-token 로직)
- `--step all` or no flag → Run Phase A then Phase B

---

## Phase A — 레퍼런스 수집 (--step brief)

100개 큐레이션 레퍼런스 기반으로 타겟에 맞는 디자인 방향성을 DESIGN_BRIEF.md로 문서화한다.
AI가 디자인을 생성하지 않는다. AI는 레퍼런스 필터링과 패턴 추출을 구조화한다.

### 게이트 체크 (Phase A 실행 전)
이전 discover 단계 타겟 프로파일을 확인한다.
없으면:
> "타겟 프로파일이 없습니다. discover 단계를 먼저 완료하거나
> 타겟(카테고리/대상/톤)을 직접 입력하시겠습니까? (입력: t)"

### 실행 흐름 (Phase A)

**A1 — 타겟 읽기**
discover 단계 결과에서 카테고리·대상·톤을 추출한다.
없으면 사용자에게 직접 입력 요청.

**A2 — ASCII 미리보기 출력**

레퍼런스 목록을 보여주기 전에 반드시 아래 형식으로 출력:

```
┌─── design-reference 실행 ────────────────────────┐
│  타겟: [카테고리] / [대상] / [톤]                │
│                                                  │
│  [한국] (번호) 사이트명 — 핵심 특징              │
│         ...                                      │
│  [글로벌] (번호) 사이트명 — 핵심 특징            │
│           ...                                    │
│                                                  │
│  번호로 5-7개 선택 / 전체 분석 (a) / 직접 입력 (m)│
└──────────────────────────────────────────────────┘
```

**A3 — 레퍼런스 필터링**
references/site-list-kr.md와 references/site-list-global.md에서
타겟 카테고리 일치 항목을 우선 추출한다.
카테고리 일치 < 6개이면 유사 카테고리로 보완.
타겟 사용자가 자주 쓰는 다른 카테고리 1-2개 추가 권고
(이유: 사용자의 디자인 기대값은 주로 쓰는 모든 앱에서 형성됨).

**A4 — 패턴 추출**
선택된 5-7개에서 references/design-wisdom.md 원칙 적용:
- 레이아웃 패턴
- 컬러 방향성 (헥스코드 + WCAG 대비비 포함 필수)
- 타이포그래피 (스케일 비율 + 기본 px 포함 필수)
- 인터랙션 패턴

패턴마다 design-wisdom.md do/don't 원칙(원칙 3) 적용: ❌/✅ 1쌍 포함.
랜딩/전환 페이지는 LIFT 모델(프레임워크 10) 4개 요소도 체크.

**A5 — DESIGN_BRIEF.md 생성**

아래 구조로 생성. 추상적 표현 금지 — 모든 결론에 수치 또는 레퍼런스 근거.

```markdown
# DESIGN_BRIEF.md

## 타겟 프로파일
- 카테고리:
- 대상:
- 톤:

## 선택된 레퍼런스
| 사이트 | 카테고리 | 적용할 패턴 | 선택 이유 |

## 추출된 디자인 방향성

### 레이아웃
[설명 + ❌/✅ do/don't 1쌍]

### 컬러
[헥스코드 + WCAG 대비비 + ❌/✅ 1쌍]

### 타이포그래피
[스케일 비율 + 기본 px + ❌/✅ 1쌍]

### 인터랙션
[ms + easing + ❌/✅ 1쌍]

## 디자인 방향성 결론
[2-3줄. 구체적 수치와 레퍼런스 사이트로 뒷받침]
```

### 게이트 완료 선언 (Phase A)
DESIGN_BRIEF.md 생성 완료 후:
> "✅ DESIGN_BRIEF.md 생성됨. `--step token`으로 토큰 생성을 계속하세요."

---

## Phase B — 토큰 생성 (--step token)

DESIGN_BRIEF.md 기반으로 의미 기반 CSS 토큰(tokens.md)과 DESIGN.md 초안을 생성한다.
AI가 디자인하지 않는다. BRIEF의 근거를 토큰 구조로 변환한다.

### 게이트 체크 (Phase B 실행 전)
DESIGN_BRIEF.md 존재 여부를 확인한다.
없으면:
> "DESIGN_BRIEF.md가 없습니다.
> `--step brief`를 먼저 실행하거나 직접 토큰 입력을 진행하시겠습니까? (입력: m)"

### 실행 흐름 (Phase B)

### 1. DESIGN_BRIEF.md 읽기
컬러 방향성, 타이포그래피, 인터랙션 패턴을 파싱한다.

### 2. ASCII 미리보기 출력

생성 전 반드시 구조 미리보기 출력:

```
┌─── design-token 생성 예정 ───────────────────────┐
│  BRIEF 기반 방향: [컬러 방향성 1줄]              │
│                                                  │
│  Color:                                          │
│    --color-brand-primary → [추정 헥스코드]       │
│    --color-text-default  → [추정 헥스코드]       │
│  Font:                                           │
│    --font-family-display → [추정 폰트명]         │
│  Space: 4px 배수 xs~2xl                          │
│                                                  │
│  계속 (y) / 직접 수정 후 진행 (m)               │
└──────────────────────────────────────────────────┘
```

### 3. 토큰 생성
references/token-patterns.md 구조와 references/design-wisdom.md 원칙 적용.

필수 규칙:
- 토큰명은 의미 기반 (원칙 1)
- 각 값 옆에 DESIGN_BRIEF.md 레퍼런스 주석 (원칙 2)
- 컬러 토큰에 WCAG 대비비 주석 (원칙 5)
- 타이포 스케일은 1.25 또는 1.333 비율 일관 적용 (원칙 4)

### 4. DESIGN.md 초안 생성
tokens.md 기반으로 DESIGN.md를 생성한다.
`deliver/ui-validate --check mobile`가 파싱할 수 있도록 브레이크포인트 섹션을 반드시 포함:

```markdown
## Breakpoints
- mobile:  375px — 1컬럼, font-size-md 기준, 터치타겟 최소 44px
- tablet:  768px — 2컬럼 전환, 사이드바 표시
- desktop: 1440px — 최대 콘텐츠 너비 1280px, 좌우 여백 균형
```

## 게이트 완료 선언
> "✅ tokens.md + DESIGN.md 생성됨. `ui-validate --check mobile`로 검증을 진행하세요."
