# Design Token Patterns

design-wisdom.md 원칙 기반 토큰 구조 패턴.
design-token 스킬에서 tokens.md 생성 시 이 패턴을 따른다.

## 명명 규칙
형식: --[카테고리]-[역할]-[변형(선택)]
예:  --color-brand-primary
     --color-text-muted
     --space-4
     --font-size-lg

금지: 값을 이름에 포함
  ❌ --color-blue-500
  ❌ --spacing-16px
  ✅ --color-brand-primary
  ✅ --space-4

## 필수 토큰 카테고리 (우선순위 순)

### 1. Color (최소 7개)
--color-brand-primary     /* 주요 CTA, 강조 */
--color-brand-secondary   /* 보조 강조 (선택) */
--color-text-default      /* 본문 텍스트 */
--color-text-muted        /* 보조 텍스트, 플레이스홀더 */
--color-surface-default   /* 기본 배경 */
--color-surface-elevated  /* 카드, 모달 배경 */
--color-border-default    /* 구분선, 인풋 테두리 */

각 컬러 토큰에 반드시 포함:
1. 헥스코드 값
2. WCAG 대비비 (텍스트 컬러만: 배경 대비)
3. DESIGN_BRIEF.md 레퍼런스 근거 주석

### 2. Typography

폰트 패밀리 (2종 원칙: 디스플레이 + 본문)
--font-family-display     /* 헤딩, 큰 텍스트 */
--font-family-body        /* 본문, UI 텍스트 */

폰트 크기 (1.25 비율 스케일 권장)
--font-size-xs:  12px
--font-size-sm:  14px
--font-size-md:  16px   /* base */
--font-size-lg:  20px
--font-size-xl:  25px
--font-size-2xl: 31px
--font-size-3xl: 39px

폰트 굵기
--font-weight-regular: 400
--font-weight-medium:  500
--font-weight-bold:    700

줄 높이
--line-height-tight:   1.25
--line-height-normal:  1.5
--line-height-relaxed: 1.75

### 3. Spacing (4px 배수)
--space-1:  4px
--space-2:  8px
--space-3:  12px
--space-4:  16px
--space-6:  24px
--space-8:  32px
--space-12: 48px
--space-16: 64px

### 4. Radius / Shadow (선택)
--radius-sm:  4px
--radius-md:  8px
--radius-lg:  16px
--radius-full: 9999px

--shadow-sm:  0 1px 2px rgba(0,0,0,0.05)
--shadow-md:  0 4px 6px rgba(0,0,0,0.07)
--shadow-lg:  0 10px 15px rgba(0,0,0,0.1)

## tokens.md 파일 형식

```css
/* ========================================
   tokens.md — [프로젝트명] Design Tokens
   DESIGN_BRIEF.md 기반 생성
   ======================================== */

/* Color */
:root {
  --color-brand-primary: #3B82F6;   /* 토스 레퍼런스 — 신뢰감+AA통과(4.6:1) */
  --color-text-default: #111827;    /* 대비비 16.1:1 (AAA 통과) */
  /* ... */
}
```
