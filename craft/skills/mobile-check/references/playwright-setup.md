# Playwright 설정 가이드

mobile-check 스킬 실행에 필요한 Playwright 설치 및 설정.

## 설치

```bash
npm install -D @playwright/test
npx playwright install chromium
```

## playwright.config.ts

```typescript
import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/design',
  use: { headless: true },
  projects: [
    {
      name: 'mobile',
      use: { viewport: { width: 375, height: 812 } },
    },
    {
      name: 'tablet',
      use: { viewport: { width: 768, height: 1024 } },
    },
    {
      name: 'desktop',
      use: { viewport: { width: 1440, height: 900 } },
    },
  ],
});
```

## tests/design/mobile-check.spec.ts

```typescript
import { test, expect } from '@playwright/test';

const TARGET_URL = process.env.TARGET_URL || 'http://localhost:3000';

test('가로 스크롤 없음', async ({ page }) => {
  await page.goto(TARGET_URL);
  const scrollWidth = await page.evaluate(
    () => document.body.scrollWidth
  );
  const clientWidth = await page.evaluate(
    () => document.documentElement.clientWidth
  );
  expect(scrollWidth).toBeLessThanOrEqual(clientWidth);
});

test('터치타겟 44px 이상 (mobile 전용)', async ({ page, viewport }) => {
  if (!viewport || viewport.width > 768) return;
  await page.goto(TARGET_URL);
  const targets = page.locator('button, a, [role="button"]');
  const count = await targets.count();
  for (let i = 0; i < count; i++) {
    const box = await targets.nth(i).boundingBox();
    if (box && box.width > 0) {
      expect(
        Math.min(box.width, box.height),
        `터치타겟 크기 부족: element ${i}`
      ).toBeGreaterThanOrEqual(44);
    }
  }
});

test('폰트 최소 14px (mobile 전용)', async ({ page, viewport }) => {
  if (!viewport || viewport.width > 768) return;
  await page.goto(TARGET_URL);
  const elements = page.locator('p, span, li, td, label');
  const count = await elements.count();
  for (let i = 0; i < Math.min(count, 20); i++) {
    const fontSize = await elements.nth(i).evaluate(
      (el) => parseFloat(window.getComputedStyle(el).fontSize)
    );
    if (fontSize > 0) {
      expect(fontSize, `폰트 크기 부족: element ${i}`).toBeGreaterThanOrEqual(14);
    }
  }
});
```

## 실행 명령

```bash
# 전체 3개 뷰포트 실행
TARGET_URL=http://localhost:3000 npx playwright test tests/design/mobile-check.spec.ts

# 특정 뷰포트만
TARGET_URL=http://localhost:3000 npx playwright test --project=mobile
```

## 결과 해석
- PASSED: 해당 뷰포트 ✅
- FAILED: 실패 테스트에서 element 번호와 실측값 출력됨 → 파일:라인 추적에 활용
