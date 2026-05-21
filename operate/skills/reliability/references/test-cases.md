# Test Cases — Reliability

## 1) Trigger Tests (5 Should Trigger + 5 Should NOT Trigger)

### Should Trigger ✓

| 번호 | 입력 쿼리 | 트리거 이유 |
|-----|---------|----------|
| T1 | "에이전트가 간헐적으로 이상한 응답을 내고 있어. 체계적으로 reliability를 리뷰하고 개선 방안을 도출해줘. 에러 패턴 분석부터." | 신뢰성 기준선 측정 + 실패 패턴 분석 명시 |
| T2 | "Our agent's success rate dropped from 95% to 87% last week. Help me systematically assess what's failing and design safeguards to prevent similar regressions." | 신뢰성 저하 진단 + Safeguard 설계 |
| T3 | "에이전트를 프로덕션에 배포하기 전에 신뢰성 목표를 설정하고 싶어. 99% 신뢰성을 달성하려면 어떤 safeguard가 필요할까?" | 신뢰성 목표 설정 + 개선 계획 |
| T4 | "특정 입력 패턴에서만 에러가 발생하는 것 같아. 실패 원인별로 분류하고 각각의 방어책을 설계해줄 수 있어?" | 실패 분류 + 카테고리별 Safeguard |
| T5 | "SLA 99.5% uptime을 보장해야 하는데, 현재 reliability가 부족해. 목표 달성까지의 로드맵을 만들어줄 수 있어?" | 신뢰성 로드맵 설계 |

### Should NOT Trigger ✗

| 번호 | 입력 쿼리 | 트리거 불필요 이유 |
|-----|---------|------------------|
| N1 | "에이전트 기회 발굴을 해줘. OST로 분석." | 기회 발굴은 별도 스킬 |
| N2 | "에이전트 OKR을 설계해줘." | PM 전략 수립, 신뢰성 분석과 무관 |
| N3 | "프롬프트 최적화로 정확도를 높이고 싶어." | 프롬프트 튜닝은 reliability 범위 외 |
| N4 | "에이전트가 지금 실패 상태에 있어. 빠르게 복구해줄 수 있어?" | incident 스킬로 라우팅 (긴급 대응) |
| N5 | "다음 버전 배포 시 A/B 테스트를 해야 하는데 샘플 크기를 계산해줄 수 있어?" | agent-ab-test 스킬로 라우팅 |

## 2) Functional Tests (Given-When-Then)

### Test Case 1: 신뢰성 기준선 측정
```
Given:
  - 에이전트 운영 기간: 30일
  - 로그: 총 2,400건 실행, 2,280 성공, 120 실패

When:
  - Success Rate 계산
  - 실패 타입별 분포 도출

Then:
  - Success Rate: 95% (명확히 정의)
  - Error Rate: 5%
  - Partial Success: 0%
  - 기준선이 팀 전체가 공유하는 명확한 formula 기반
```

### Test Case 2: 실패 분류 및 패턴 분석
```
Given:
  - 120개 실패 사례

When:
  - 5가지 카테고리(Input/Model/Tool/Logic/Output)로 분류
  - 각 카테고리별 Frequency, Root Cause, Impact, Detection, Recovery 분석

Then:
  - Input Error: 30건 (Low severity)
  - Model Error: 60건 (Medium severity) — 환각, 형식 오류
  - Tool Error: 20건 (High severity) — API timeout
  - Logic Error: 8건 (High severity) — 조건 검사 누락
  - Output Error: 2건 (Low severity) — 응답 길이 초과
```

### Test Case 3: Safeguard 설계 및 우선순위화
```
Given:
  - 실패 분류 완료
  - High impact 실패 3가지 식별

When:
  - 각 실패에 대해 Safeguard 유형 선택
  - 예상 효과(실패율 감소) 계산

Then:
  - Model Error (60개) → Confidence Gate (threshold 0.7)
    - Expected: 60 → 40 (33% 개선)
  - Tool Error (20개) → Retry with Exponential Backoff
    - Expected: 20 → 5 (75% 복구)
  - Input Error (30개) → JSON Schema Validation
    - Expected: 30 → 2 (거의 전부 사전 차단)
```

## 3) Error Cases

### Error Case 1: 신뢰성 기준선 정의 불명확
```
Symptom: "Reliability가 95%"라고 계산했는데 팀마다 정의가 다름
- Alice: "응답 받았으면 성공" (95%)
- Bob: "응답 + 정확도 > 80%" (87%)

Root Cause: 성공/실패 정의가 formula화되지 않음

Fix:
  1. Success 정의 표준화:
     "에이전트가 0초 이내 응답 반환 + 에러 타입 X 미포함"
  2. Partial Success 정의:
     "응답 반환했으나 정확도 < 80% 또는 포맷 미충족"
  3. Failure 정의:
     "응답 미반환 또는 에러 반환"
```

### Error Case 2: Safeguard 성능 저하
```
Symptom: Confidence Gate (threshold 0.7) 추가 후
- 정확도: 92% → 96% ↑ (개선)
- 응답 불가율: 5% → 20% ↑ (악화)

Root Cause: Threshold가 너무 높아 많은 요청 거절

Fix:
  1. Threshold 조정 (0.7 → 0.5)
  2. Fallback path 개선 (거절된 요청을 다른 경로로 처리)
  3. 트레이드오프 명시: "정확도 96% but 응답율 95%"
```

## 3) Edge Cases

| # | 쿼리 | 판정 | 이유 |
|---|------|------|------|
| E1 | "우리 에이전트가 "대부분의 경우" 잘 작동해. 신뢰성 분석이 필요할까?" | ⚠️ 경계 | "대부분" = 정량화 필요. 95%일까 99%일까? reliability 스킬은 "기준선 측정"을 강제하므로 유효 |
| E2 | "에이전트가 부분적으로 성공하는 경우가 있어(예: "응답은 했지만 정확도 60%"). 이것도 "실패"로 봐야 할까?" | ✅ Trigger | Partial Success는 reliability 스킬에서 명시적으로 다뤄짐. "성공/부분성공/실패" 3가지로 분류 가능 |
| E3 | "특정 사용자나 특정 입력 유형에서만 에러가 난다면? reliability를 전체로 계산할 때 대표성이 있을까?" | ✅ Trigger | reliability는 "세분화된 분석"을 권고. "전체 95%, 특정 유형 80%" 같이 카테고리별 측정 가능 |
| E4 | "에이전트 신뢰성을 99%까지 올려야 하는데, 비용이 많이 들 것 같아. 트레이드오프를 어떻게 평가할까?" | ✅ Trigger | reliability와 cost는 별개 스킬. reliability는 "어떻게 99% 달성할지" 로드맵, cost-sim은 "그 비용" 계산 |
| E5 | "reliability 개선을 위해 매번 수동 검증을 추가했는데, 응답 시간이 너무 길어졌어. 이건 reliability 개선의 "부작용"이 아닐까?" | ✅ Trigger | reliability의 Safeguard는 "정확도"와 "응답성" 트레이드오프를 명시해야 함. 두 메트릭을 함께 모니터링하고 임계값 설정 필수 |

---

## 4) With/Without Skill 비교

| 상황 | Without Reliability | With Reliability |
|-----|-------------------|------------------|
| 신뢰성 파악 | "그냥 잘 되는 것 같은데..." (정성적) | Success Rate 95%, Error Rate 5% (정량화) |
| 실패 분석 | "모델이 이상한 것 같다" (추측) | 5가지 카테고리 분류 + 패턴 분석 |
| 개선 전략 | "다시 한 번 해보자" (무작정) | High impact 실패별 Safeguard 우선순위화 |
| 목표 설정 | "좋은 신뢰성이 되도록" (모호) | High 99% (명확, 달성 가능) |
| 로드맵 | "언젠가는 나아질 것" (미정) | Quick Wins 1주, Medium 1개월, Long 1분기 |
| 프로덕션 배포 | 신뢰성이 불확실한 상태로 배포 | 99% 신뢰성 확보 후 배포 |
