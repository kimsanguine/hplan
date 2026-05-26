# Good Example — 전자상거래 체크아웃 기능

**입력:** "checkout 기능 4개 태스크를 conductor로 실행해줘. 플랜: docs/PRD.md"

---

## Phase 1 — 플랜 파싱

`docs/PRD.md` 섹션 3.2 "결제 플로우" 추출 결과:

```
[ ] T1: 결제 API 연동 — src/api/checkout.ts, src/lib/stripe.ts
[ ] T2: 에러 핸들링 — src/api/checkout.ts, src/components/ErrorBanner.tsx
[ ] T3: 테스트 작성 — tests/checkout.test.ts, tests/e2e/purchase.spec.ts
[ ] T4: 배포 설정 — .github/workflows/deploy.yml, wrangler.toml
```

사용자 확인 후 실행 시작.

---

## Phase 2 — 태스크별 루프

### T1: 결제 API 연동

**디스패치:**
```
## 태스크: 결제 API 연동

### 목표
Stripe Checkout Session API를 연동한다. 금액·통화·상품명을 파라미터로 받아
세션 URL을 반환하는 createCheckoutSession() 함수를 구현한다.

### 허용 파일 범위
- src/api/checkout.ts (신규 생성)
- src/lib/stripe.ts (신규 생성)

### 완료 기준
- createCheckoutSession() 호출 시 Stripe 세션 URL 반환
- STRIPE_SECRET_KEY는 환경 변수에서 로드

### 반환 형식
STATUS: DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED
요약: [한 줄]
변경 파일: [목록]
```

**에이전트 응답:**
```
STATUS: DONE
요약: createCheckoutSession() 구현 완료, STRIPE_SECRET_KEY 환경 변수 로드
변경 파일: src/api/checkout.ts, src/lib/stripe.ts
```

**Spec Compliance:**
```
[x] ICP 정합성: 결제 세션 생성 → 사용자 결제 완료 플로우 직결
[x] 비기능 요건: 타임아웃 30s, 실패 시 에러 코드 반환
[x] 실패 모드 커버: Stripe API 오류 → StripeError 타입으로 throw
```
→ PASS

**Quality Gate:**
```
[x] 기술 부채 마커: 없음
[x] 테스트 커버리지: createCheckoutSession 단위 테스트 미포함
[ ] 보안 기본: 통과
```
→ FAIL — 테스트 누락

수정 요청 → 에이전트가 `src/lib/stripe.test.ts` 추가 → 재실행 PASS

**완료:**
```
[x] T1: 결제 API 연동 — 완료 증거: src/api/checkout.ts, src/lib/stripe.ts, src/lib/stripe.test.ts
```

---

### T2: 에러 핸들링

**디스패치:** T1 컨텍스트 전달 없이 fresh 디스패치.

**에이전트 응답:**
```
STATUS: DONE_WITH_CONCERNS
요약: ErrorBanner 컴포넌트 추가, StripeError 처리 분기 구현
변경 파일: src/api/checkout.ts, src/components/ErrorBanner.tsx
우려사항:
- card_declined 에러 코드 외에 insufficient_funds, expired_card 코드도 존재하나
  현재 구현은 generic 메시지로 처리함. 세분화된 메시지 필요 여부 미결정.
```

우려사항 검토: PRD 섹션 3.2에 "에러 코드별 메시지 분기" 요건 명시 없음 → generic 처리 허용, 주석으로 개선 여지 기록.

**Spec Compliance:**
```
[x] ICP 정합성: 결제 실패 시 사용자에게 명확한 피드백 제공
[x] 비기능 요건: ErrorBanner는 aria-live="polite" 적용
[x] 실패 모드 커버: network timeout, card error, server error 3경로 처리
```
→ PASS

**Quality Gate:**
```
[x] 기술 부채 마커: // TODO: 에러 코드 세분화 1건 — 우려사항 검토에서 허용 결정
[x] 테스트 커버리지: ErrorBanner 렌더 테스트 포함
[x] 보안 기본: 에러 메시지에 내부 스택 트레이스 노출 없음
```
→ WARNING (TODO 1건, 허용된 것) → PASS 처리

**완료:**
```
[x] T2: 에러 핸들링 — 완료 증거: src/api/checkout.ts (수정), src/components/ErrorBanner.tsx
```

---

### T3: 테스트 작성

**에이전트 응답:**
```
STATUS: DONE
요약: e2e 구매 플로우 테스트 3시나리오 작성
변경 파일: tests/checkout.test.ts, tests/e2e/purchase.spec.ts
```

**Spec Compliance:**
```
[x] ICP 정합성: 정상 구매·결제 실패·세션 만료 3시나리오 커버
[x] 비기능 요건: e2e 테스트 실행 시간 < 30s
[x] 실패 모드 커버: Stripe mock으로 카드 오류 시나리오 포함
```
→ PASS

**Quality Gate:**
```
[x] 기술 부채 마커: 없음
[x] 테스트 커버리지: 테스트 파일 자체의 유효성 — playwright test 실행 성공 확인
[x] 보안 기본: 테스트 코드에 실제 API 키 없음 (mock 사용)
```
→ PASS

**완료:**
```
[x] T3: 테스트 작성 — 완료 증거: tests/checkout.test.ts, tests/e2e/purchase.spec.ts
```

---

### T4: 배포 설정

**디스패치:**

**에이전트 응답:**
```
STATUS: BLOCKED
요약: GitHub Actions workflow 작성에 필요한 Cloudflare API token secret name 미확인
블로커: repo secrets에 CF_API_TOKEN 키명 확인 필요
```

컨텍스트 보완: `.env.example`에서 `CLOUDFLARE_API_TOKEN` 키명 확인 → 에이전트에 전달 후 재디스패치.

**재디스패치 응답:**
```
STATUS: DONE
요약: GitHub Actions deploy workflow + wrangler.toml 작성, CLOUDFLARE_API_TOKEN 사용
변경 파일: .github/workflows/deploy.yml, wrangler.toml
```

**Spec Compliance:**
```
[x] ICP 정합성: main 브랜치 push 시 자동 배포 트리거
[x] 비기능 요건: deploy job 타임아웃 10분 설정
[x] 실패 모드 커버: deploy 실패 시 Slack 알림 step 포함
```
→ PASS

**Quality Gate:**
```
[x] 기술 부채 마커: 없음
[x] 테스트 커버리지: CI lint + test step이 deploy 앞에 배치됨
[x] 보안 기본: API token은 GitHub Secret 참조, 하드코딩 없음
```
→ PASS

**완료:**
```
[x] T4: 배포 설정 — 완료 증거: .github/workflows/deploy.yml, wrangler.toml
```

---

## Phase 3 — 최종 리뷰

**전체 체크리스트:**
```
[x] T1: 결제 API 연동 — src/api/checkout.ts, src/lib/stripe.ts
[x] T2: 에러 핸들링 — src/api/checkout.ts, src/components/ErrorBanner.tsx
[x] T3: 테스트 작성 — tests/checkout.test.ts, tests/e2e/purchase.spec.ts
[x] T4: 배포 설정 — .github/workflows/deploy.yml, wrangler.toml
```

**완료 리포트:**
- 총 태스크: 4 / 완료: 4
- 게이트 지연: T1 (Quality Gate 1회 재실행), T2 (DONE_WITH_CONCERNS 검토), T4 (BLOCKED → 컨텍스트 보완 후 재디스패치)
- 미완료 태스크: 없음
- 주목할 개선 여지: T2 에러 코드 세분화 (TODO 주석으로 기록, PRD 요건 외)
