# Test Cases — cost-sim

## 1) Trigger Tests

### Should Trigger (5)

1. **Customer Support Agent (GPT-4o)**
   - Query: "고객 응대 에이전트를 GPT-4o로 만들려는데, 하루 1000건 처리 기준으로 월 비용이 얼마나 나올지 시뮬레이션해줘. 평균 대화 턴은 5회 정도야."
   - Reason: 명확한 모델, 호출 빈도, 입출력 정보 제공
   - Expected: 토큰 비용 + 스케일 시나리오

2. **Document Analysis Agent (Claude Sonnet)**
   - Query: "We want to estimate the token costs for our document analysis agent before getting budget approval. Each doc is ~10 pages, we process 200/day, using Claude Sonnet."
   - Reason: 페이지 기반 입력량 명확, 모델 선택 완료
   - Expected: 월간/연간 비용 + 예산 근거

3. **News Monitoring Agent with Search API**
   - Query: "매일 30건의 뉴스 소스를 모니터링하는 에이전트를 Haiku로 만들려는데, Brave Search API 비용도 포함해서 월간 예상 비용을 계산해줄 수 있어?"
   - Reason: 모델 + 외부 API 조합 비용 추정

4. **Marketing Copywriting Agent (Model Routing)**
   - Query: "마케팅 카피 생성 에이전트 비용을 추정하는데, 분류 작업은 Haiku, 창의적 작성은 Sonnet으로 라우팅하려고 해. 일간 500건 처리 기준으로."
   - Reason: 모델 라우팅 전략의 비용 영향 분석

5. **Scale Planning**
   - Query: "현재 고객사가 5곳인데, 향후 50곳으로 확장할 때 에이전트 토큰 비용이 어떻게 증가할지 시나리오를 보여줄 수 있어? 인프라 비용도 선형으로 증가할까?"
   - Reason: 스케일링 시나리오별 비용 곡선 필요

---

### Should NOT Trigger (5)

1. **Reliability 개선**
   - Query: "에이전트 reliability를 개선하고 싶어. 에러율이 높아."
   - Reason: 성능 최적화 (비용 관계 없음) → 별도 스킬
   - Correct Route: reliability/error-handling 스킬

2. **경쟁사 분석**
   - Query: "경쟁사 분석 좀 해줘. 우리 에이전트 제품의 경쟁 우위가 뭔지 알고 싶어."
   - Reason: 비용이 아닌 경쟁 포지셔닝 → agent-gtm 스킬
   - Correct Route: discover/agent-gtm [예정]

3. **이미 배포된 에이전트 비용 리뷰**
   - Query: "이번 달 에이전트 토큰 비용 리뷰해줘. 예산 대비 초과된 것 같아."
   - Reason: 사전 시뮬레이션이 아닌 실시간 추적 → burn-rate 스킬
   - Correct Route: measure/burn-rate

4. **가격 책정**
   - Query: "에이전트 제품 가격을 얼마로 책정하면 좋을까? 경쟁사는 월 $50~$100인데."
   - Reason: 가격 모델/GTM → agent-gtm 스킬
   - Correct Route: discover/agent-gtm [예정]

5. **모델 성능 비교**
   - Query: "Claude Opus vs GPT-4o 성능 비교해줄 수 있어? 어떤 게 더 나아?"
   - Reason: 비용만이 아닌 기술 성능 검토 필요 → router 스킬
   - Correct Route: routing/model-comparison 스킬

---

## 2) Functional Tests (Given-When-Then)

### Test 2-1: 외부 API 가격 정보 변동

**Given:**
- 요청: "Brave Search API 비용을 포함한 월간 비용 추정"
- 알려진 가격: 2025-12월 기준 $3/1,000쿼리
- 실제 현재 가격: 2026-03 기준 $3.50/1,000쿼리 (가격 인상됨)

**When:**
- cost-sim 스킬에서 최신 가격 조회

**Then:**
- ✓ "2026-03 기준 추정치" 명시
- ✓ 공식 가격 링크 제공 (Brave 공식 가격 페이지)
- ✓ "가격은 변동될 수 있으니 구현 시 재확인 필수" 경고

---

### Test 2-2: 스케일 시나리오에서 비선형 비용 증가

**Given:**
- 사용자 1명: 100건/일 처리 → $10/월
- 사용자 10명: 1,000건/일 처리 → $100/월 (선형)
- 사용자 100명: 10,000건/일 처리 → ???

**Scenario:**
- 단순 선형 계산: $1,000/월
- 실제: $2,500/월 (Orchestrator 오버헤드, 중복 호출 증가)

**When:**
- 비선형 증가 감지

**Then:**
- ✓ "100명 규모에서 예상보다 비용 폭증" 경고
- ✓ 원인 분석: "오케스트레이션 레이어 호출 폭증 가능성"
- ✓ 즉시 모델 라우팅/캐싱 전략 제안

---

### Test 2-3: 모든 단가에 기준일 명시

**Given:**
- 작성된 비용 시뮬레이션

**When:**
- Quality Gate 체크

**Then:**
- ✗ 날짜 없음: "Claude Sonnet $3/1M input" (거절)
- ✓ 날짜 있음: "Claude Sonnet $3/1M input (2026-03 기준)" (승인)

---

## 3) Error Cases

### Error 3-1: 사용자가 모델/트리거 빈도를 모름

**Scenario:**
- Query: "에이전트 비용이 얼마나 될까?"
- 추가 정보 없음

**Expected Error Handling:**
- ✗ 시뮬레이션 불가
- ✓ Step 1 선택지 제시:
  - "에이전트 유형은? (Cron / Monitor / On-demand / Orchestrator)"
  - "사용할 모델은? (Haiku / Sonnet / Opus / GPT-4o)"
  - "일간 호출 수는?"

---

### Error 3-2: 외부 API 가격이 매우 높아짐

**Scenario:**
- Google Search API가 예상보다 비쌈
- 계산: 10,000쿼리/월 × $5/1,000 = $50/월 (예상)
- 실제: 적절한 사용량 관리 없으면 $500+/월

**Expected Error Handling:**
- ✓ "Google Search는 매우 비쌀 수 있다" 경고
- ✓ 대안 제시: "Brave Search ($3/1k) 또는 내부 검색 엔진 고려"
- ✓ 캐싱 전략으로 중복 쿼리 90% 감소 가능성 언급

---

## 3) Edge Cases

| # | 쿼리 | 판정 | 이유 |
|---|------|------|------|
| E1 | "에이전트 비용 시뮬레이션을 하는데, 기준을 뭘로 잡아야 할까? 일일 호출 수가 날마다 다르거든." | ⚠️ 경계 | cost-sim은 "예측" 이지만 입력 가정이 불명확하면 정확도 떨어짐. "평균/피크/저점" 3가지 시나리오 시뮬레이션 권고 |
| E2 | "이미 배포된 에이전트의 실제 비용을 추적하고 싶어. 비용 예측이 아니라 비용 리뷰야." | ❌ Route → measure/burn-rate | 예측(사전) vs 추적(사후) 구분. burn-rate는 실시간 비용 모니터링, cost-sim은 배포 전 시뮬레이션 |
| E3 | "모델을 Haiku에서 Sonnet으로 업그레이드하면 비용이 어떻게 달라질까? 정확도 개선도 고려해서." | ✅ Trigger | 모델 변경의 비용 영향 분석. 하지만 "정확도 개선 → 호출 횟수 감소"까지 계산하면 복잡. 단순 모델 가격 비교가 주 목적 |
| E4 | "캐싱이나 배치 처리로 토큰 비용을 50% 줄일 수 있다면, 비용 시뮬레이션에 이미 반영해야 할까?" | ✅ Trigger | "최적화 전/후" 2개 시나리오 시뮬레이션 가능. cost-sim의 Step 4에서 "모델 라우팅/캐싱 전략" 대안 제시 가능 |
| E5 | "외부 API 가격이 우리 계약에서만 특별 할인돼. 이걸 비용 시뮬레이션에 포함할 수 있을까?" | ⚠️ 경계 | 커스텀 가격은 비용 시뮬레이션의 가정에 영향. 하지만 cost-sim은 "공정한 가격"을 기준으로 하므로 주석으로 "실제 계약 가격 적용 필요" 명시 권고 |

---

## 4) With/Without Skill 비교

### Scenario: Customer Support Agent 비용 추정

**Before (cost-sim 없이):**
- PM: "에이전트로 고객 응대 자동화하면 좋을 것 같은데"
- 기술팀: "가능하긴 한데... 비용이 얼마나 들지 알 수 없네"
- 결정: 불확실한 상태로 진행

**After (cost-sim 스킬 적용):**

1. **프로파일링**
   - 모델: Claude Sonnet
   - 호출: 500건/일, 3턴 평균
   - 예상: 입력 2,000 tokens, 출력 1,500 tokens per call

2. **비용 시뮬레이션**
   - 월간 호출: 500 × 30 = 15,000회
   - 입력: 15,000 × 2,000 × $3/1M = $90
   - 출력: 15,000 × 1,500 × $15/1M = $337.50
   - **월간: $427.50 (또는 $400~$450 범위)**

3. **스케일 시나리오**
   - 1개 고객: $427/월
   - 10개 고객: $4,270/월
   - 100개 고객: $42,700/월 → 높음! 모델 라우팅 검토 필요

4. **최적화 제안**
   - "간단한 인사/FAQ는 Haiku로 라우팅 → 비용 50% 절감 가능"
   - "캐싱으로 중복 응답 80% 감소 → 추가 10% 절감"
   - 예상 절감: $427 → $170/월

**Impact:**
- 구현 전 예산 승인 근거 확보
- 비용 초과 위험 사전 감지
- 모델 라우팅으로 $250+/월 절감 의사 결정
