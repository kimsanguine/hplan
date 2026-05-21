# mobile-check — 자주 발생하는 문제

## 문제 1: DESIGN.md가 없다
해결: 이 게이트는 우회 없음.
> "DESIGN.md가 없습니다. `/design-token`을 먼저 실행하세요."
이유: 기준 없는 검증은 의미 없음.

## 문제 2: TARGET_URL에 접근할 수 없다
체크:
1. 로컬 서버가 실행 중인지 확인 (npm run dev / bun run dev)
2. 포트 확인 (기본 3000, Astro 4321 등)
해결: `TARGET_URL=http://localhost:4321 npx playwright test ...`

## 문제 3: 터치타겟 실패인데 코드에서 찾기 어렵다
방법:
1. `npx playwright test --project=mobile --reporter=html`
2. HTML 리포트에서 스크린샷과 element 위치 시각 확인
3. 브라우저 개발자도구 → Elements → 해당 요소 크기 확인

## 문제 4: 가로 스크롤이 특정 페이지만 발생
방법: TARGET_URL을 해당 페이지 경로로 지정해 재실행
`TARGET_URL=http://localhost:3000/about npx playwright test ...`
