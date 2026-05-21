# design-token — tokens.md 좋은 예시

## 예시: 핀테크 앱 토큰 (DESIGN_BRIEF.md 기반)

```css
/* ========================================
   tokens.md — FinApp Design Tokens
   DESIGN_BRIEF.md: 핀테크/2030직장인/신뢰+심플
   ======================================== */

/* Color */
:root {
  --color-brand-primary: #3B82F6;    /* 토스 레퍼런스 — 신뢰감, WCAG AA 4.6:1 */
  --color-text-default: #111827;     /* 대비비 16.1:1 AAA 통과 */
  --color-text-muted: #6B7280;       /* 대비비 4.7:1 AA 통과 */
  --color-surface-default: #FFFFFF;
  --color-surface-elevated: #F9FAFB;
  --color-border-default: #E5E7EB;
}

/* Typography — 1.25 스케일 */
:root {
  --font-family-display: 'Pretendard', -apple-system, sans-serif;
  --font-family-body: 'Pretendard', -apple-system, sans-serif;
  --font-size-md: 16px;   /* base */
  --font-size-lg: 20px;   /* ×1.25 */
  --font-size-xl: 25px;   /* ×1.25 */
  --font-size-2xl: 31px;  /* ×1.25 */
  --font-size-sm: 14px;
  --font-size-xs: 12px;
  --font-weight-regular: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 700;
  --line-height-normal: 1.5;
  --line-height-tight: 1.25;
}

/* Spacing — 4px 배수 */
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-6: 24px;
  --space-8: 32px;
  --space-12: 48px;
}
```

**검증 기준:**
- 모든 컬러에 대비비 주석 ✅
- 모든 토큰에 DESIGN_BRIEF.md 레퍼런스 근거 ✅
- 타이포 스케일 비율 일관성 (1.25) ✅
- 간격 4px 배수 준수 ✅
