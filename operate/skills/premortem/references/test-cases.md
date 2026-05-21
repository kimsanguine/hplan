# Test Cases — Premortem

## 1) Trigger Tests (5 Should Trigger + 5 Should NOT Trigger)

### Should Trigger ✓

| 번호 | 입력 쿼리 | 트리거 이유 |
|-----|---------|----------|
| T1 | "다음 주에 에이전트를 프로덕션에 배포하는데, 실패할 수 있는 모든 시나리오를 사전에 분석해줘. FMEA 방법론으로." | FMEA + pre-mortem exercise 명시적 요청 |
| T2 | "Before we launch this agent to 10,000 users, I want to run a pre-mortem. What could go wrong? Help me identify failure modes, assess severity, and plan mitigations." | 배포 전 사전 실패 분석 요청 |
| T3 | "멀티에이전트 오케스트레이터의 위험 프로파일을 검토하고 싶어. 연쇄 실패, 비용 폭등, 환각 등 가능한 실패 모드를 RPN으로 우선순위화해줘." | 위험도 정량화 + RPN 계산 |
| T4 | "이번 분기 premortem 재검토를 진행해야 해. 지난 premortem 결과를 바탕으로 새로운 위험들을 찾아줄 수 있어?" | 분기별 재premortem 명시 |
| T5 | "에이전트 신뢰성 개선 계획 전에 리스크 분석을 해야 해. Prevention 메커니즘을 설계하기 전에 어떤 실패들을 방어해야 할지 파악하고 싶어." | Prevention 전략 설계 기반의 실패 분석 |

### Should NOT Trigger ✗

| 번호 | 입력 쿼리 | 트리거 불필요 이유 |
|-----|---------|------------------|
| N1 | "에이전트 토큰 비용을 추적하고 최적화해줘." | burn-rate 스킬로 라우팅 |
| N2 | "에이전트 System Prompt를 CRISP로 리팩토링해줘." | 프롬프트 최적화는 premortem 범위 외 |
| N3 | "에이전트 OKR을 설계해줘." | PM 전략 수립, 위험 분석과 무관 |
| N4 | "코호트 분석을 통해 버전별 성능 차이를 추적하고 싶어." | cohort 스킬로 라우팅 |
| N5 | "incident가 발생했어. 원인을 파악하고 대응해줄 수 있어?" | incident 스킬로 라우팅 (사후 분석) |

## 2) Functional Tests (Given-When-Then)

### Test Case 1: FMEA 테이블 생성
```
Given:
  - 멀티에이전트 오케스트레이터 배포 예정
  - 5개 하위 에이전트 의존성 있음

When:
  - Pre-mortem exercise 실행 ("3개월 후 실패했다면?")
  - FMEA 테이블 작성

Then:
  - 최소 10-15개 실패 모드 식별됨
  - 각 모드별 Severity(1-10), Probability(1-10), Detection(1-10) 평가됨
  - RPN(Severity × Probability × Detection) 계산됨
  - RPN 상위 10개가 명확히 우선순위화됨
```

### Test Case 2: Prevention/Detection/Response/Recovery 전략
```
Given:
  - FMEA 테이블에서 RPN > 100인 실패 모드 5개

When:
  - 각 고위험 모드별로 Prevention/Detection/Response/Recovery 설계

Then:
  - Prevention: 어떻게 실패를 예방할지 명시
  - Detection: 실패를 감지하는 모니터링 방법 정의
  - Response: 감지 후 즉시 대응 프로세스
  - Recovery: 정상 상태로 복구하는 절차
```

### Test Case 3: 모니터링 트리거 설정
```
Given:
  - Prevention 전략이 설계된 상태

When:
  - 모니터링 트리거 정의 (Yellow alert, Red alert)

Then:
  - Yellow alert: 조사 필요 수준의 임계값 설정됨 (예: "에러율 > 3%")
  - Red alert: 즉시 대응 필요 임계값 설정됨 (예: "에러율 > 10% 또는 비용 2배 폭등")
  - 각 alert이 자동 감지 가능한 메트릭 기반임
```

## 3) Error Cases

### Error Case 1: RPN 계산 오류 (평가 표준 불일치)
```
Symptom: 같은 실패 모드의 RPN을 팀마다 다르게 책정 (Alice: RPN 120, Bob: RPN 80)

Root Cause: Severity, Probability, Detection의 평가 기준이 모호함

Fix:
  1. RPN 계산 워크숍 진행
  2. 각 척도 정의 표준화 (예: Severity 8 = "1000명 이상 영향")
  3. 팀 공동 평가로 일관성 확보
```

### Error Case 2: Prevention 액션 미실행
```
Symptom: FMEA 테이블은 완성했으나 Prevention 액션 실행 안 됨 → 같은 실패 반복

Root Cause: Owner/Deadline 미명시, 추적 체계 부재

Fix:
  1. 각 액션 아이템별로 Owner, Deadline 명시
  2. 월간 추적 리뷰 설정
  3. 완료 여부 기록 및 차단 아이템 에스컬레이션
```

## 4) With/Without Skill 비교

### Scenario: 새로운 에이전트 배포 전

| 상황 | Without Premortem | With Premortem |
|-----|------------------|-----------------|
| 배포 전 계획 | 대충 리스크 회의만 진행 (정성적) | FMEA로 체계적 분석 → RPN 우선순위화 |
| 위험도 파악 | "뭔가 위험할 것 같은데..." (정량화 X) | RPN > 100 고위험 모드 10개 명시 |
| 방어책 | "각 에러 발생 시 대응" (사후) | Prevention/Detection/Response/Recovery 사전 설계 |
| 배포 후 결과 | 상치 못한 실패 발생 → 서둘러 대응 (비용↑, 신뢰도↓) | 대부분의 고위험 모드가 사전 차단 → 평온한 배포 |
| 학습 | 사후 포스트모템만 가능 | 배포 전 이미 위험 완화 → 포스트모템 간단 |

## 3) Edge Cases

| # | 쿼리 | 판정 | 이유 |
|---|------|------|------|
| E1 | "이미 배포된 에이전트의 premortem을 지금 해야 할까? 아니면 다음 버전부터 하면 되지 않을까?" | ⚠️ 경계 | premortem은 "배포 전" 일반적 권고이지만, 기존 에이전트의 "새로운 기능 추가" 또는 "위험도 높은 변경"이면 수행 가치 있음 |
| E2 | "premortem 결과로 RPN 100 이상인 위험이 5개가 나왔어. 모두 prevention을 설계해야 할까?" | ✅ Trigger | "시간/리소스 제약"이 있으면 RPN 상위 3개부터 우선 처리. 하지만 "위험을 알고 있다"는 것이 중요 |
| E3 | "기술팀이 "우리는 이 위험들을 이미 생각해봤다"고 해. premortem을 따로 할 필요가 있을까?" | ✅ Trigger | "비공식 논의" vs "FMEA 문서화"는 다름. 비공식 아이디어는 체계적이지 않고 추적 불가능. FMEA 작성 권고 |
| E4 | "RPN 계산할 때, Severity와 Probability를 구분하기 어려워. 둘 다 높으면 어떻게?" | ✅ Trigger | Severity = "얼마나 심한가", Probability = "얼마나 자주 일어나는가"를 분명히 구분. 둘 다 높으면 RPN이 높아서 우선순위 높음 |
| E5 | "예상하지 못한 위험이 배포 후 발생했어. 이건 premortem 실패인가?" | ⚠️ 경계 | premortem은 "알려진 범위 내 위험"을 분석. "완전히 예상 밖" 위험도 있을 수 있음. 다만 "배포 후 빠른 감지 + 롤백 트리거"를 통해 피해 최소화 |

---

## 4) Error Cases

### Error Case 1: RPN 계산 오류 (평가 표준 불일치)

AI 에이전트 배포 의사결정을 KPI 기반으로 판정하기 위한 Given-When-Then 테스트 케이스입니다.

### Test Case 1: GO 경계값 (모든 KPI 충족)

```
Given:
  - 신규 에이전트 배포 준비 완료
  - 초기 Experiment 단계 (10% 트래픽)
  - 7일간 운영 데이터 수집 완료

Metrics (현재 상태):
  ┌─────────────────────────────────────┐
  │ Core Metrics                        │
  │ CCR: 99.3% (threshold ≥98.5%) ✓    │
  │ ECR: 99.1% (threshold ≥98.5%) ✓    │
  │ FBR: 2.3% (threshold ≤2.5%)  ✓    │
  │ GL95: 1800ms (threshold ≤2500ms) ✓ │
  │                                     │
  │ Extended Metrics                    │
  │ ASR: 91% (threshold ≥90%) ✓         │
  │ BR: 4.2% (threshold ≤5%) ✓         │
  │ BOR: 0.8% (threshold ≤1%) ✓        │
  │ RCR: 96% (threshold ≥95%) ✓        │
  │                                     │
  │ Trend (7일):                         │
  │ CCR: 99.1→99.3% (안정) ✓           │
  │ FBR: 2.8→2.3% (개선) ✓            │
  │ GL95: 1900→1800ms (개선) ✓        │
  └─────────────────────────────────────┘

When:
  - Go-NoGo 의사결정 회의 개최
  - PM, 엔지니어, 리더가 메트릭 검토
  - Rollback plan 확인 (5분 내 가능)

Then:
  - 의사결정: GO
  - 근거:
    1) 모든 Core KPI가 임계치 충족
    2) 모든 Extended KPI가 임계치 충족
    3) 7일 trend가 안정하거나 개선
    4) 신규 critical incident 없음
  - 액션:
    1) Enforcement 단계로 진행 (100% 트래픽)
    2) 모니터링 대시보드 활성화 (Red alert 설정)
    3) On-call 팀 배치 (첫 72시간)
    4) Rollback 커맨드 준비 (1명이 30초 내 실행 가능)
```

---

### Test Case 2: CONDITIONAL (1-2개 경계 이탈, 보정 가능)

```
Given:
  - 에이전트 배포 중기 (30% 트래픽)
  - 3주 운영 데이터

Metrics (현재 상태):
  ┌─────────────────────────────────────┐
  │ Core Metrics                        │
  │ CCR: 98.7% (threshold ≥98.5%) ✓    │
  │ ECR: 98.2% (threshold ≥98.5%) ⚠️   │
  │   → 임계치 미달, 하지만 95% 경계값  │
  │   → Expected: 98.4% (margin 0.2%) │
  │ FBR: 2.4% (threshold ≤2.5%) ✓      │
  │ GL95: 2100ms (threshold ≤2500ms) ✓ │
  │                                     │
  │ Extended Metrics                    │
  │ ASR: 89% (threshold ≥90%) ⚠️        │
  │   → 임계치 미달, 하지만 95% 경계값  │
  │ BR: 3.8% (threshold ≤5%) ✓         │
  │ BOR: 0.9% (threshold ≤1%) ✓        │
  │ RCR: 94% (threshold ≥95%) ~        │
  │   → 경계값 근처, 추이 관찰 필요    │
  │                                     │
  │ Trend (7일):                         │
  │ ECR: 98.4→98.2% (소폭 악화) ↘     │
  │ ASR: 90→89% (악화) ↘              │
  │ 하지만 rate of decline 둔화: 가능   │
  └─────────────────────────────────────┘

Root Cause 분석 완료:
  - ECR 저하: Strict policy rule 추가 → validation 거절 증가
  - ASR 저하: Tool timeout 간헐적 발생 (외부 API 불안정)
  - 개선 계획: Policy rule 임계값 조정 + timeout retry 추가

When:
  - 개선 아이템이 명확하고 구현 가능
  - 예상 개선 효과: ECR +0.5%, ASR +1.5%
  - 리더가 "2주 내 개선" 약속
  - 비즈니스 임팩트: 30%→60% 확대 배포 가능하지만 제한적

Then:
  - 의사결정: CONDITIONAL
  - 조건:
    1) 트래픽을 30%→50%로만 확대 (전체 확대 X)
    2) 매일 ECR/ASR 모니터링 (임계치 복귀 확인)
    3) 2주 내 개선 로드맵 실행
    4) 2주 후 재판정: GO 또는 NO-GO
  - 액션:
    1) Slack channel에서 daily standup (ECR/ASR 리뷰)
    2) 개선 아이템 JIRA 생성 (우선순위: HIGH)
    3) Rollback threshold 낮춤 (ASR < 88% → 즉시 rollback)
    4) Policy rule 변경과 retry logic 배포 (5일 내)
```

---

### Test Case 3: NO-GO (Critical Breach 발생)

```
Given:
  - 에이전트 배포 초기 (5% 트래픽)
  - 2일 운영 후 문제 발생

Metrics (현재 상태):
  ┌──────────────────────────────────────┐
  │ Core Metrics - 심각                   │
  │ CCR: 94.2% (threshold ≥98.5%) ✗✗✗  │
  │   → 임계치 미달 4.3%!!              │
  │   → 의미: 정책 엔진이 6% 요청을 처리  │
  │   → 영향: 정책 검증 불가 가능성     │
  │                                      │
  │ ECR: 97.1% (threshold ≥98.5%) ✗✗✗  │
  │ FBR: 5.8% (threshold ≤2.5%)  ✗✗✗  │
  │   → False block rate가 2배 이상!   │
  │ GL95: 4500ms (threshold ≤2500ms) ✗ │
  │   → 응답시간이 1.8배 증가!          │
  │                                      │
  │ Extended Metrics                     │
  │ ASR: 72% (threshold ≥90%) ✗✗✗      │
  │   → 에이전트 성공률이 18%p 하락!   │
  │ BR: 22% (threshold ≤5%) ✗✗✗        │
  │   → 우회율이 4배 증가!             │
  │                                      │
  │ Incident:                            │
  │ - SEV2: 고객 10건 블록 민원        │
  │ - SEV1 예측: 배포 12시간 후         │
  │   결제 시스템 먹통 가능성          │
  └──────────────────────────────────────┘

Root Cause (가설):
  - 신규 모델 버전이 정책 엔진과 호환 안 됨
  - 또는 데이터베이스 쿼리 timeout 증가
  - 또는 배포 후 config 설정 오류

When:
  - 상황 보고 (CCR 94%, FBR 5.8%)
  - 리더가 "지금 당장 롤백" 지시
  - Rollback 명령 수행 (3분 소요)

Then:
  - 의사결정: NO-GO (즉시 중단)
  - 액션:
    1) 배포 즉시 롤백 (이전 버전으로)
    2) 롤백 후 모니터링 (메트릭 정상화 확인)
    3) Root cause 심층 분석 (24시간)
    4) Post-mortem 개최 (48시간)
    5) 개선된 배포 계획 (1주일 후 재시도)
  - 커뮤니케이션:
    1) 고객 공지: "배포 일시 중단, 안정성 개선 중"
    2) 내부 공지: "원인 분석 중, 결과는 내일 오후"
    3) Executive report: 영향도, 복구 시간, 재발 방지책
  - 학습:
    1) 모델 호환성 테스트 강화
    2) Canary 배포(5%) 단계에서 모든 KPI 자동 검증
    3) Rollback 시뮬레이션을 매 배포마다 실행
```

---

### Test Case 4: 롤백 트리거 (False Block Rate 2일 연속 초과)

```
Given:
  - 에이전트 배포 후 8일 운영 중
  - Enforcement 단계 (100% 트래픽)
  - FBR baseline: 2.0%

Timeline:
  Day 1 (배포 직후):
    FBR = 1.9% ✓ (정상)

  Day 2:
    FBR = 2.1% ✓ (임계치 2.5% 이내)

  Day 3:
    FBR = 3.1% ⚠️ (임계치 2.5% 초과!)
    → Yellow alert 발생
    → 팀: "모니터링 강화, 원인 조사"

  Day 4:
    FBR = 3.4% ⚠️ (계속 초과)
    → Trigger condition 만족: 연속 2일 초과
    → Red alert 발생

Metrics (Day 4):
  ┌─────────────────────────────────────┐
  │ FBR: 3.4% (threshold ≤2.5%) ✗      │
  │   → 정상 거래 3.4%가 오탐지       │
  │   → 영향: 일 10만 건 중 3,400건   │
  │                                     │
  │ 다른 Core KPI:                      │
  │ CCR: 99.0% ✓                       │
  │ ECR: 98.8% ✓                       │
  │ GL95: 2200ms ✓                    │
  │   → 다른 지표는 정상             │
  │   → 원인이 명확: 정책 rule 오버fit │
  └─────────────────────────────────────┘

Root Cause Analysis (Day 4 오후):
  - Feature: "고위험 국가 IP" 차단 규칙 추가
  - 문제: 규칙이 너무 aggressive
  - 영향: VPN/프록시 사용자 70% 차단 (false positive)

When:
  - On-call 엔지니어가 트리거 감지
  - 리더에게 보고
  - 2가지 옵션 검토:
    1) Rollback (완전 철회)
    2) Hotfix (규칙 임계값 조정)

Decision Flow:
  - Hotfix 시간: 2-3시간 (테스트 포함)
  - Rollback 시간: 10분
  - 리더 판단: "FBR 2일 연속 초과 = 자동 rollback 정책"

Then:
  - 액션: Rollback 실행 (자동 정책)
  - 커맨드:
    ```
    $ kubectl rollout undo deployment/agent-v2
    $ verify_metrics FBR < 2.5%  # 확인
    ```
  - 결과 (15분 후):
    FBR = 2.1% (정상 복귀)

  - 이후 조치:
    1) Hotfix 규칙 재설계 (threshold 80% → 90%)
    2) 테스트: 신규 규칙으로 재시뮬레이션
    3) Canary 배포 (5% 트래픽)
    4) 3일 모니터링 후 다시 GO 판정

  - 커뮤니케이션:
    1) 고객: "일시적 오류 수정 완료"
    2) 내부: "Hotfix 결과 FBR 개선 예상"
    3) Post-mortem: "규칙 테스트 강화 필요"

  - Learning (조직 기억):
    - Trigger 기반 자동 rollback의 가치: 토론 중단, 즉시 행동
    - 규칙 변경 시 별도 staging 환경에서 수주일 테스트 필수
    - 규칙 threshold는 "보수적"으로 설정 (aggressive는 금지)
```

---

## 6) 통합 테스트: 의사결정 흐름도

```
배포 시작
  ↓
7일 운영 데이터 수집
  ↓
KPI 계산 (8가지 metrics)
  ↓
Core KPI 검사
  ├─ 모두 임계치 ✓? → Extended KPI 검사
  │
  └─ 1개 이상 미달 ✗? → NO-GO (즉시 rollback)
      ↓
      Root cause 분석 (24-48시간)
      ↓
      Hotfix 또는 설계 개선
      ↓
      최소 3일 재테스트 후 재배포

Extended KPI 검사
  ├─ 모두 임계치 ✓? → Trend 검사
  │
  └─ 1-2개 미달? → Boundary 판단
      ├─ 경계값(95%) 이상? → CONDITIONAL (제한 확대)
      └─ 경계값 미만? → NO-GO (rollback)

Trend 검사 (7일 데이터)
  ├─ 안정 또는 개선? → GO (다음 단계)
  │
  └─ 악화? → CONDITIONAL (모니터링 강화)

GO 의사결정
  ├─ Enforcement: 100% 배포
  ├─ On-call 팀 배치 (72시간)
  └─ 매일 KPI 리뷰 (2주)

CONDITIONAL 의사결정
  ├─ 트래픽 제한 확대 (30%→50%)
  ├─ 개선 로드맵 2주 내 실행
  └─ 2주 후 재판정

운영 중 Rollback Trigger 감지?
  ├─ Trigger 1: Core KPI 급락 (5% 이상)
  ├─ Trigger 2: FBR 2일 연속 초과
  ├─ Trigger 3: Critical incident
  ├─ Trigger 4: Bypass rate 3배 급증
  │
  └─ 즉시 Rollback 실행
```
