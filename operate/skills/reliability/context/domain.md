# Domain Context — Reliability

## 1) Domain Scope

**에이전트의 신뢰성을 체계적으로 측정, 분석, 개선**

- 현재 신뢰성 기준선 측정 (Success Rate, Error Rate, P95 응답시간)
- 실패 패턴을 5가지 카테고리로 분류 (Input/Model/Tool/Logic/Output)
- 각 실패별 Safeguard 설계 (Validation, Confidence Gate, Retry, Fallback, Circuit Breaker)
- 신뢰성 목표 수준 설정 (Basic/Standard/High/Critical)
- 개선 로드맵 수립 (Quick Wins, Medium Term, Long Term)

## 2) Primary Users

- **AI 에이전트 팀 리더**: 신뢰성 목표 설정 및 리뷰 책임
- **에이전트 엔지니어**: Safeguard 구현 담당
- **QA/테스트**: 신뢰성 기준선 측정 및 검증
- **PM**: 신뢰성 목표를 비즈니스 SLA와 정렬

## 3) Required Inputs

- **에이전트 명**: 분석 대상
- **운영 기간 데이터**: 최소 1주일 이상 (일일 변동성 흡수)
- **실패 로그**: 분류 가능한 형태 (카테고리, 타입, 시점)
- **성공/실패 정의**: 팀이 합의한 formula (모호함 제거)
- **비즈니스 요구**: SLA 목표 (예: 99.5% uptime)

## 4) Output Contract

- **신뢰성 기준선**: Success Rate, Error Rate, 실패 분포 (%) 명시
- **실패 분류**: 5가지 카테고리별 Count, Severity, 영향도
- **패턴 분석**: 각 실패 카테고리별로 Frequency, Root Cause, Impact, Detection, Recovery 정의
- **Safeguard 설계**: 높은 영향도 실패 각각에 대해 구체적 방어책 (유형, 구현 방법, 예상 효과)
- **신뢰성 목표 로드맵**: 현재 → 목표 수준까지의 단계적 개선 계획 (Timeline, 우선순위)

## 5) Guardrails

- **기준선 데이터 충분성**: 최소 1주일 이상 데이터 필요 (일일 변동성 흡수) → 부족하면 기간 연장
- **실패 정의 표준화**: 팀마다 "에러"를 다르게 정의하면 신뢰성 측정 불가 → formula 명시화
- **Safeguard 과도화 방지**: 모든 가능한 실패에 방어책을 세우면 성능 저하 → 영향도 × 발생 확률로 우선순위화
- **목표 현실성**: 달성 불가능한 높은 목표는 팀 사기 저하 → 비교값(이전 버전, 경쟁사, 업계 표준) 기반 설정
- **비용-신뢰성 트레이드오프 명시화**: Safeguard 추가로 인한 토큰 비용 증가를 정량화하고 의사결정

## 6) Working Facts (TO BE UPDATED by reviewer)

- **신뢰성 수준 기준**: Basic 90%, Standard 95%, High 99%, Critical 99.9%
- **Safeguard 유형 6가지**: Input Validation, Output Validation, Confidence Gate, Retry with Backoff, Fallback Path, Circuit Breaker
- **P95/P99**: 평균이 아닌 백분위수로 측정 ("최악의 경우" 신뢰도 파악)
- **실패 분류**: Input, Model, Tool, Logic, Output 5가지 기본 (도메인별 추가 분류 가능)
- **모니터링 주기**: Daily (Error Rate, Latency), Weekly (Trend, Pattern), Monthly (Strategic Review)

## 7) Fill-in Checklist

- [ ] 분석 대상 에이전트 명 및 분석 기간(최소 1주) 확인
- [ ] 성공/실패의 정의를 formula로 명시화 (이상 해석 방지)
- [ ] 실제 운영 데이터 수집 (로그, 모니터링, 사용자 피드백)
- [ ] 실패를 5가지 카테고리로 분류 (Input/Model/Tool/Logic/Output)
- [ ] 각 카테고리별 패턴 분석 (Frequency, Root Cause, Impact, Detection, Recovery)
- [ ] 높은 영향도 실패별로 Safeguard 설계 (유형, 구현 방법, 예상 효과)
- [ ] 신뢰성 목표 수준 선택 (Basic/Standard/High/Critical)
- [ ] 현재 수준 → 목표 수준까지의 로드맵 수립 (Quick Wins, Medium Term, Long Term)
- [ ] 각 Safeguard의 비용(토큰) 임팩트 평가
- [ ] 팀 공유 및 구현 Owner/Deadline 명시

## 8) 참고 사례: Linear Quality Gate 시스템의 설계 패턴

아래는 프로덕션 에이전트에서 적용한 설계 패턴 사례입니다. 조직과 도메인에 따라 다르게 설계할 수 있습니다.

### Fail-Open Resilience 패턴

Linear의 Quality Gate 시스템은 외부 의존성 실패 시에도 서비스를 제공하기 위해 fail-open resilience를 단계별로 설계했습니다.

**의존성 실패 분류:**
- 외부 API 5xx 에러
- 요청 타임아웃 급증
- 정책엔진(Policy Engine) 장애
- 계약 검증 불일치
- 보안/컴플라이언스 정책 위반

**Tier별 Fail-Open 동작:**
```
Tier A (핵심 결제/보안):
  ├─ 상태: Fail-Closed 강제
  ├─ 복구: Last Known Good (LKG) 정책 또는 거절
  └─ 조건: 의존성 장애 → 거래 즉시 중단

Tier B (준핵심 의사결정):
  ├─ 상태: Fail-Open (제한적) + 재검증
  ├─ 복구: 캐시된 정책 사용 + 나중에 검증
  └─ 조건: Healthy window 충족(최근 99.9% 정상) → 일시적 Open

Tier C (보조 기능):
  ├─ 상태: Fail-Open + Replay
  ├─ 복구: 즉시 응답 + 나중에 로그 재검증
  └─ 조건: 비즈니스 영향 미미 → 관대한 정책
```

**복구 조건:**
- Healthy window: 마지막 장애 발생 후 24시간 동안 오류율 < 0.5% (예시값, 도메인에 따라 조정)
- Canary mismatch 감지: 1% 트래픽 샘플에서 정책 불일치 발생 → Open mode 중단
- Backlog 안정화: 재검증 대기 큐가 SLA 이내로 감소

**강제 Fail-Closed 전환 트리거:**
1. 보안 이벤트 감지 (정책 위반, 인증 실패)
2. LKG 데이터 만료 (> 7일; 예시값, 도메인에 따라 조정)
3. 모드 flap 과다 (같은 날 3회 이상 Open↔Closed 전환)
4. Degraded 상태 지속 초과 (> 4시간; 예시값, 도메인에 따라 조정)

**Retry 전략:**
- Exponential backoff: 1s → 2s → 4s → 8s (최대 cap: 8s; 예시값, 도메인에 따라 조정)
- Jitter 추가: ±30% randomization (cascading 방지)
- Idempotency key 기반 replay: 중복 요청 필터링

### Bypass-Audit 정책 엔진의 상태머신 (프로젝트 설계 패턴)

AI 에이전트 시스템에서 일시적으로 보안 정책을 우회해야 할 때(예: 기술 지원, 긴급 대응) 감시되는 우회권한 관리가 필수입니다. 아래는 이 프로젝트에서 적용한 설계입니다. 다른 조직에서는 다른 상태머신을 설계할 수 있습니다.

**상태 전이도:**
```
REQUESTED
  ├─ (승인) → APPROVED_ACTIVE
  │           ├─ (TTL 만료) → EXPIRED
  │           ├─ (조기 취소) → REVOKED
  │           └─ (재검증 필요) → REMEDIATION
  │
  ├─ (거절) → DENIED
  │
  └─ (시간초과) → EXPIRED (자동)

REMEDIATION
  ├─ (수정 완료) → CLOSED
  └─ (수정 미흡) → REVOKED
```

**필수 정책:**
1. Requester ≠ Approver (권한 분리)
2. TTL 상한선 (Tier별; 예시값, 조직 정책에 따라 조정):
   - 보안 우회: 최대 1시간
   - 기술 지원: 최대 4시간
   - 긴급 대응: 최대 24시간
3. Remediation deadline: expires_at보다 반드시 이후여야 함 (사후 검증 시간 확보)

**Append-Only 감사 추적:**
- 모든 상태 변화는 INSERT-only (UPDATE/DELETE 금지)
- 해시체인: 각 레코드는 이전 레코드의 hash 참조
  ```json
  {
    "id": "bypass_123",
    "state": "APPROVED_ACTIVE",
    "expires_at": "2026-03-07T12:00:00Z",
    "hash": "sha256(id+state+timestamp+prev_hash)",
    "prev_hash": "sha256(...)"
  }
  ```
- 무결성 검증: 전체 체인을 순회하며 hash 일치 확인

**TTL 만료 자동 보정:**
- Cron job: 매시간(또는 조직 정책상 주기) 만료된 bypass 권한 감지
- 자동 상태 전이: APPROVED_ACTIVE → EXPIRED
- 자동 task 생성: remediation task 자동 생성, 담당자에게 할당

### AI 에이전트 신뢰성 설계의 3가지 필수 교훈

**1. 외부 의존성 실패는 필연적 → Fail-Open 정책이 아닌 fail-open **전략**을 설계하라**
- 모든 의존성을 동등하게 취급하지 말 것 (Tier 분류)
- 각 Tier별 실패 시 동작을 사전에 명시하고 테스트할 것
- "최악의 경우"를 가정하되 (LKG, 캐시), 사후 재검증 절차는 필수

**2. 신뢰성 개선은 보안과 감시(Audit)를 동반해야 한다**
- Safeguard 추가 → 정책 우회 및 예외 처리 증가
- 모든 예외는 append-only 감사 추적으로 기록할 것
- 모드 전환(Open↔Closed) 자체가 지표가 되어야 함

**3. 정성적 판단을 정량적 임계치로 변환하고 자동화하라**
- "대략 안정적"이라는 판단 → Healthy window, Backlog SLA 등 명확한 수치
- 모든 상태 전이는 자동화된 로직으로 → 사람의 개입 최소화
- 자동 복구(Healthy window) + 자동 보정(TTL 만료) + 자동 알림(flap 감지)
