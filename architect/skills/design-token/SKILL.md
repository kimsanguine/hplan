---
name: design-token
description: DESIGN_BRIEF.md를 읽어 의미 기반 디자인 토큰(tokens.md)과 DESIGN.md 초안을 생성한다.
  craft/mobile-check 스킬의 필수 입력이 됨.
argument-hint: "[프로젝트명 또는 DESIGN_BRIEF.md 경로]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# design-token

## 목적
DESIGN_BRIEF.md 기반으로 의미 기반 CSS 토큰(tokens.md)과 DESIGN.md 초안을 생성한다.
AI가 디자인하지 않는다. BRIEF의 근거를 토큰 구조로 변환한다.

## 게이트 체크 (실행 전)
DESIGN_BRIEF.md 존재 여부를 확인한다.
없으면:
> "DESIGN_BRIEF.md가 없습니다.
> `/design-reference`를 먼저 실행하거나 직접 토큰 입력을 진행하시겠습니까? (입력: m)"

## 실행 흐름

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
craft/mobile-check가 파싱할 수 있도록 브레이크포인트 섹션을 반드시 포함:

```markdown
## Breakpoints
- mobile:  375px — 1컬럼, font-size-md 기준, 터치타겟 최소 44px
- tablet:  768px — 2컬럼 전환, 사이드바 표시
- desktop: 1440px — 최대 콘텐츠 너비 1280px, 좌우 여백 균형
```

## 게이트 완료 선언
> "✅ tokens.md + DESIGN.md 생성됨. `/mobile-check`로 검증을 진행하세요."
