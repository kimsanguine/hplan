---
name: mobile-check
description: DESIGN.md의 브레이크포인트 스펙을 기반으로 Playwright로 375/768/1440px
  세 뷰포트를 검증한다. 실패 시 파일:라인 형식으로 이슈를 출력하며 반복 실행 가능.
argument-hint: "[TARGET_URL 또는 생략 시 localhost:3000]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

# mobile-check

## 목적
DESIGN.md 기준으로 세 뷰포트(375/768/1440px)에서 레이아웃이 정상인지 Playwright로 검증한다.
build 중 반복 실행 가능. 통과 전까지 빌드 완료 선언 금지.

## 게이트 체크 (실행 전)
DESIGN.md 존재 여부를 확인한다.
없으면:
> "DESIGN.md가 없습니다. `/design-token`을 먼저 실행하세요."
※ 이 게이트는 우회 없음 — 기준 없는 검증은 의미 없음.

## 실행 흐름

### 1. DESIGN.md 읽기
Breakpoints 섹션에서 뷰포트 기준과 최대 콘텐츠 너비를 파싱한다.

### 2. Playwright 환경 확인
```bash
npx playwright --version 2>/dev/null || echo "not installed"
```
없으면 references/playwright-setup.md의 설치 가이드를 안내한다.

### 3. 테스트 파일 생성/확인
`tests/design/mobile-check.spec.ts` 없으면 references/playwright-setup.md의
spec 코드를 그대로 생성한다.

### 4. Playwright 실행
```bash
TARGET_URL=${ARG:-http://localhost:3000} \
  npx playwright test tests/design/mobile-check.spec.ts \
  --reporter=line 2>&1
```

### 5. ASCII 결과 출력 (항상)

```
┌─── mobile-check 결과 ────────────────────────────┐
│  375px   ✅/❌ N/3                               │
│  768px   ✅/❌ N/3                               │
│  1440px  ✅/❌ N/1                               │
│                                                  │
│  이슈: (있을 때만)                               │
│  [실패 테스트명]: [실측값] → [파일 추적 힌트]    │
│                                                  │
│  수정 후 재실행: /mobile-check                   │
└──────────────────────────────────────────────────┘
```

### 6. 리포트 저장
이슈 1개 이상이면 `mobile-check-report.md` 생성.
이슈 없으면 파일 생성하지 않음.

## 게이트 완료 선언
통과: > "✅ 모바일 검증 통과. 빌드 계속 진행 가능합니다."
실패: > "❌ [n]개 뷰포트 실패. mobile-check-report.md를 확인하고 수정 후 재실행하세요."
