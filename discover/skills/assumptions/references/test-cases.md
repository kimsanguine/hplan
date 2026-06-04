# Test Cases — assumptions

## 1) Trigger Tests

### Should Trigger (5)

1. **고객 문의 분류 + 자동 응답**
   - Query: "고객 문의를 자동 분류하는 에이전트를 만들려고 하는데, 이 아이디어의 핵심 가정들을 분석해줘. LLM이 우리 도메인 용어를 이해할 수 있을지 확신이 없어."
   - Reason: 구현 전 가정 검증 필요; 팀의 구체적 우려 표현
   - Expected: 4축 가정 맵 + 우선순위 + 실험 설계

2. **마케팅 카피 자동 생성**
   - Query: "We're planning to build an agent that auto-generates marketing copy. Before we invest, help me identify what assumptions we're making about quality, brand consistency, and user acceptance."
   - Reason: 구현 투자 전 가정 위험도 평가
   - Expected: Value/Reliability/Ethics 축 가정 발굴

3. **경영 지표 대시보드 자동 브리핑**
   - Query: "매일 아침 CEO에게 경영 지표 대시보드를 이메일로 자동 발송하는 에이전트를 만들려는데, 정말 필요한 정보인지, 프롬프트가 일관된 품질의 요약을 만드는지, 오류 발생 시 고객 신뢰 영향이 클지 모르겠어."
   - Reason: Value/Reliability/Ethics 다층 검토 필요

4. **내부 문서 검토 워크플로우**
   - Query: "우리 회사의 모든 신규 계약을 에이전트가 자동으로 검토하고 피드백을 주려고 해. 하지만 법적 리스크가 있을 수 있고, 에이전트가 중요한 조항을 놓칠 수도 있어. 이 아이디어의 가정을 분석해줄 수 있을까?"
   - Reason: Feasibility/Reliability/Ethics 우려가 높음

5. **소셜 미디어 콘텐츠 자동 생성 및 발행**
   - Query: "우리 팀이 매일 SNS에 올릴 콘텐츠를 에이전트가 생성하고 발행하도록 자동화하려는데, 브랜드 톤이 유지되는지, 부적절한 콘텐츠가 발행될 위험은 없는지, 비용 효율이 있는지 확신이 안 서."
   - Reason: Value/Reliability/Ethics 복합 평가 필요

---

### Should NOT Trigger (5)

1. **기존 에이전트 비용 리뷰**
   - Query: "이번 달 에이전트 토큰 비용 리뷰해줘. 예산 대비 초과된 것 같아."
   - Reason: 이미 실행 중인 에이전트의 비용 추적 → ops-review 스킬
   - Correct Route: operate/ops-review --mode cost

2. **에이전트 아키텍처 설계**
   - Query: "에이전트 아키텍처를 3-tier로 설계하고 싶어. Prometheus-Atlas-Worker 패턴 적용해줘."
   - Reason: 기술 스택 설계 문제 → 구현 방식, 가정 검증 아님
   - Correct Route: architecture/infrastructure 스킬 (별도)

3. **프롬프트 최적화**
   - Query: "이 프롬프트를 CRISP 프레임워크로 다시 작성해줘. 더 명확하게."
   - Reason: 이미 기존 에이전트의 성능 개선 → agent-setup 스킬
   - Correct Route: deliver/agent-setup

4. **비즈니스 모델 설계**
   - Query: "에이전트 비즈니스 모델을 설계하고 싶어. 가격 전략이랑 수익 구조를 잡아줘."
   - Reason: 비즈니스 모델 설계 → strategy 스킬
   - Correct Route: architect/strategy --focus biz-model

5. **기회 탐색**
   - Query: "우리 회사에서 에이전트로 자동화할 수 있는 기회가 뭐가 있을까? 대략적인 아이디어만 줘."
   - Reason: 에이전트 기회를 아직 선택하지 않음 → opp-tree 스킬
   - Correct Route: discover/opp-tree

---

## 2) Functional Tests (Given-When-Then)

### Test 2-1: Value 축 가정이 누락되는 경우

**Given:**
- 에이전트 아이디어: "고객 문의 자동 응답"
- 팀의 초기 우려: "기술적으로 가능할까?" (Feasibility/Reliability만 언급)

**When:**
- assumptions 스킬 Step 2 실행 (4축 가정 브레인스토밍)

**Then:**
- ✓ Value 축 가정 최소 3개 발굴
  - 예: "고객이 자동 응답을 실제로 사용하는가?"
  - 예: "자동 응답이 고객 만족도를 높이는가?"
  - 예: "응답 시간 단축이 고객 이탈 감소로 이어지는가?"
- ✓ "기술팀이 Feasibility만 검토하고 Value를 놓치기 쉽다" 경고 메시지 포함

---

### Test 2-2: 점수 계산이 불합리한 경우

**Given:**
- 5개 가정 모두 점수 "위험도 5 × 난이도 5 = 25점"

**When:**
- 점수 검증 (Quality Gate)

**Then:**
- ✗ 승인 거절
- ✓ "모든 가정이 최고 위험도로 평가되었으므로, 팀의 낙관 바이어스 의심"
- ✓ 점수 재평가 유도: "악의적 질문으로 재검토해보세요. 이 가정 중 틀릴 확률이 낮은 것은?"

---

### Test 2-3: Ethics 위험이 높은데 미감지

**Given:**
- 에이전트 아이디어: "자동 대금 청구 에이전트"
- 초기 분석: Value/Feasibility 축만 분석, Ethics 누락

**When:**
- Quality Gate 체크

**Then:**
- ✗ 승인 거절
- ✓ "이 에이전트는 금전 거래를 자동 실행합니다. Ethics 축 가정 최소 3개 필요"
- ✓ 리마인더: "위험도 4점 이상 Ethics 항목은 hitl 스킬 검토 강제"

---

## 3) Error Cases

### Error 3-1: 검증 실험이 불가능한 경우

**Scenario:**
- Assumption: "시장에서 이 에이전트가 받아들여질 것인가?"
- Proposed Experiment: "출시 후 6개월 동안 시장 반응 모니터링"

**Expected Error Handling:**
- ✗ 실험 설계 거절 (2일 이내 불가능)
- ✓ 재정의 제안:
  - "3일간 5명의 타겟 사용자와 사용성 테스트"
  - 또는 "2주 Shadow Mode로 내부 사용자 정확도 측정"

---

### Error 3-2: 가정이 너무 일반적인 경우

**Scenario:**
- Assumption: "에이전트가 작동할 것이다"
- Problem: 검증 불가능, 위험도 측정 불가능

**Expected Error Handling:**
- ✗ 가정 거절
- ✓ 세분화 유도:
  - "대신 다음과 같이 구체화해보세요:"
  - "Claude Sonnet 모델이 (구체적 도메인) 을/를 80% 이상 정확히 분류할 것이다"
  - "API 응답 시간이 평균 < 2초일 것이다"

---

## 3) Edge Cases

| # | 쿼리 | 판정 | 이유 |
|---|------|------|------|
| E1 | "우리 에이전트 가정을 리뷰하고 싶은데, 이미 기술적으로 구현이 다 돼있고 유저도 사용 중이야. 지금 가정 분석이 의미가 있을까?" | ⚠️ 경계 | 이미 배포된 에이전트는 assumptions보다 reliability/ops-review 스킬이 맞을 수 있음. 하지만 "새로운 기능 추가"라면 trigger 가능 |
| E2 | "가정 3개만 분석하면 되지 않을까? 전부 다 검증할 여유가 없어." | ✅ Trigger | 사용자의 리소스 제약이 있어도 기술적으로는 assumptions 스킬. 단, Step 3에서 "Top 1" 가정만 선정 옵션 제시 |
| E3 | "기술 스택 선택(Claude vs GPT-4)에 대한 가정을 검증하고 싶어. 어느 모델이 더 나을까?" | ❌ Route → architect/orchestration --pattern router 또는 assumptions --mode build-or-buy | 모델 선택은 기술 성능 비교 영역. assumptions는 "이 에이전트가 정말 필요한가"에 답함 |
| E4 | "Competitor가 우리보다 빨리 만들어서 시장을 선점할 위험이 있어. 이것도 가정 위험도에 포함돼야 하지 않을까?" | ✅ Trigger | 경쟁 시간 압박은 Feasibility 축(개발 리소스 부족) 또는 Value 축(실제 고객이 존재하는가)과 연계 가능. 유효한 가정 |
| E5 | "우리 팀이 이 에이전트를 만들 기술이 없어. 그래서 외부 팀에 아웃소싱하려고 하는데, 이 경우에도 assumptions 분석이 필요해?" | ✅ Trigger | Feasibility 축의 "인력 확보" 가정으로 유효. 아웃소싱 위험도(질 관리, 소유권, 일정) 모두 assumptions 범위 내 |

---

## 4) With/Without Skill 비교

### With assumptions 스킬

**Scenario: 고객 문의 자동 분류 에이전트**

**Before:**
- 팀: "기술적으로 충분히 구현할 수 있고, 비용도 괜찮으니까 해보자"
- 리스크 평가: 불충분 (기술만 검토)

**After (assumptions 스킬 적용):**
- Value 위험도 4점: "고객이 자동 응답을 신뢰할지 불확실"
  → 실험: "5일간 자동 응답 + 고객 재문의율 측정"
- Reliability 위험도 5점: "분류 정확도가 불균형 (urgent=90%, general=60%)"
  → 실험: "카테고리별 정확도 측정 (각 20회 반복)"
- Ethics 위험도 3점: "잘못된 분류 시 고객 불만"
  → HITL 설계 필요 (hitl 스킬로 연결)

**Impact:**
- 구현 전 3가지 리스크 조기 발견
- 검증 실험 2주 실행 후, 정확도 문제 판명 → 모델 업그레이드 결정
- 무의미한 구현 투자 방지, 예상 비용 50% 절감
