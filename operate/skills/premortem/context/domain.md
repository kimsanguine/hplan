# Domain Context — Premortem

## 1) Domain Scope

**에이전트 배포 전 사전 실패 분석**

- 새로운 에이전트 아키텍처의 위험 요소를 사전에 식별
- FMEA (Failure Mode and Effects Analysis) 방법론으로 체계적 분석
- RPN (Risk Priority Number) 기반 우선순위화
- Prevention/Detection/Response/Recovery 전략 설계
- 분기별 재premortem으로 지속적 위험 관리

## 2) Primary Users

- **AI 에이전트 팀 리더**: 배포 전 리스크 검토 책임
- **PM/기술 리더**: 위험도 평가 및 의사결정
- **엔지니어**: Prevention 메커니즘 구현 담당
- **Compliance/Risk 팀**: 규제 요구사항 문서화

## 3) Required Inputs

- **에이전트 명**: 분석 대상 (예: "다국어 고객 지원 에이전트 v2.0")
- **배포 규모**: 영향받을 사용자 수 및 중요도
- **의존성 맵**: 연동 API, 하위 에이전트, 데이터 소스
- **이전 장애 기록** (있다면): 유사 실패 패턴 분석에 활용
- **제약 조건**: 규제, 컴플라이언스, 비용 제약 등

## 4) Output Contract

- **FMEA 테이블**: 최소 10-15개 실패 모드, RPN 상위 10개 우선순위화
- **Prevention 전략**: RPN > 100인 각 모드별로 Prevention/Detection/Response/Recovery 명시
- **모니터링 트리거**: Yellow alert (조사), Red alert (즉시 대응) 정의
- **액션 아이템**: Owner, Deadline, 완료 여부 추적 가능한 형태
- **재premortem 일정**: 분기별 또는 중요 변화(모델 업그레이드, 사용자 2배) 시점

## 5) Guardrails

- **과도한 悲觀主義 방지**: 모든 가능한 실패 나열 후 분석 마비 → RPN으로 상위 10-15개만 우선화
- **기술 중심 편향 방지**: 모델 오류만 초점 → 데이터, 통합, 비즈니스 실패도 포함
- **일회성 분석 방지**: 처음 premortem 후 방치 → 분기별 재검토 필수
- **Prevention 실행 추적**: FMEA 완성이 끝이 아니라 액션 아이템 완료까지 책임
- **새로운 위험 도입 모니터링**: Prevention 구현 중 새로운 실패 모드 감지 시 incremental premortem 실행

## 6) Working Facts (TO BE UPDATED by reviewer)

- **RPN 임계값**: RPN > 100은 고위험, 50-100은 중위험, < 50은 저위험 (조직 표준에 맞춰 조정)
- **FMEA 카테고리**: 모델, 데이터, 통합, 비즈니스 4가지 기본 (산업/도메인별 추가 카테고리 고려)
- **Detection 척도**: 1 = 쉽게 감지, 10 = 감지 불가능 (자동화 모니터링 인프라 의존)
- **Prevention 역량**: 팀의 엔지니어링 리소스와 구현 난이도를 고려한 현실적 planning
- **재premortem 주기**: 기본 분기별, 단 모델 업그레이드, 사용자 규모 2배 등 주요 변화는 즉시 실행

## 7) Fill-in Checklist

- [ ] 분석 대상 에이전트 명 및 배포 시점 확인
- [ ] 의존성 맵 수집 (API, 데이터 소스, 하위 에이전트)
- [ ] 이전 장애 기록 조회 (있다면 유사 패턴 식별)
- [ ] Pre-mortem exercise 실행 ("3개월 후 실패했다면...")
- [ ] FMEA 테이블 작성 (Severity, Probability, Detection 평가)
- [ ] RPN 계산 및 우선순위 정렬
- [ ] 모델/데이터/통합/비즈니스 4가지 카테고리 검토 완료
- [ ] RPN > 100 모드별 Prevention/Detection/Response/Recovery 설계
- [ ] 모니터링 트리거 (Yellow/Red alert) 정의
- [ ] 액션 아이템 Owner/Deadline 명시
- [ ] 분기별 재premortem 일정 등록
- [ ] 팀 공유 및 비준 (리더, 엔지니어, 규제 담당자)

## 8) 참고 사례: 결제 게이트웨이의 Go-NoGo 체계

> **TL;DR**: 사전검시 결과를 3단계 배포 의사결정(Go/Conditional/No-Go)으로 연결하는 프레임워크입니다.
> RPN 점수 → KPI 임계값 → Go/NoGo 게이트 순서로 매핑합니다.

### Go-NoGo 의사결정 프레임워크

AI 에이전트 배포에서 신뢰성을 정량적으로 판정하기 위해 선제 검시(premortem) 결과를 KPI 대시보드와 연결합니다. Linear의 Quality Gate 시스템(결제 게이트웨이)에서 사용하는 2단계 프레임워크를 참고합니다.

아래 KPI는 결제 시스템에서 사용한 예시입니다. 일반 에이전트에서는 도메인에 맞는 KPI를 정의해야 합니다.

**2단계 의사결정 체계:**
```
Stage 1: Init → Experiment (개발 및 초기 검증)
  ├─ 내부 테스트, 엔지니어 검증
  ├─ 작은 스케일 실험 (1-10% 트래픽)
  └─ 의사결정: "충분히 테스트했나?" (심사 기준: 기본 안정성)

Stage 2: Enforcement → Evaluation (점진적 확대 배포)
  ├─ 대량 사용자 노출 (50-100%)
  ├─ 실제 운영 메트릭 수집
  └─ 의사결정: "프로덕션 수준의 신뢰성을 달성했나?" (심사 기준: KPI 목표)
```

**GO 경로 (진행) 조건:**
```
모든 Core KPI ≥ 임계치 AND
모든 Extended KPI ≥ 임계치 AND
False block rate ≤ 2.5% AND
지난 7일 trend가 안정 또는 개선

→ 배포 진행, 다음 단계 해금
```

**CONDITIONAL 경로 (조건부) 조건:**
```
1-2개 KPI가 경계값(임계치의 95%) 이탈 AND
명확한 개선 로드맵 존재 AND
비즈니스 영향 제한적

→ 제한된 범위 확대 배포, 모니터링 강화
(예: 특정 지역 또는 사용자 그룹만)
```

**NO-GO 경로 (중단) 조건:**
```
다음 중 하나 이상:
- Core KPI 중 하나 이상 임계치 미달
- False block rate > 5% (설정값의 2배)
- 지난 3일 trend가 악화
- 신규 critical incident 발생
- 규제/보안 compliance 위반

→ 배포 즉시 중단, 롤백, 원인 분석
```

### 핵심 KPI 8개와 임계치 (결제 시스템 사례)

Linear 시스템(결제 게이트웨이)의 실제 KPI를 참고합니다. 일반 에이전트 대체 KPI 예시는 아래 표 후에 제시합니다.

| KPI 코드 | 지표명 | 정의 | 임계치 | 카테고리 |
|---------|------|------|-------|---------|
| **CCR** | Covered Conversion Rate | 정책 엔진이 평가 가능한 거래의 비율 | ≥ 98.5% (이 사례의 기준값 — 도메인에 따라 95%~99.9% 범위에서 설정) | Core |
| **ECR** | Effective Conversion Rate | 정책 검증을 통과한 거래의 비율 | ≥ 98.5% (이 사례의 기준값 — 도메인에 따라 조정) | Core |
| **FBR** | False Block Rate | 정상 거래를 오탐지한 비율 | ≤ 2.5% (이 사례의 기준값 — 도메인에 따라 조정) | Core |
| **GL95** | Gate Latency P95 | 정책 평가의 95 percentile 응답시간 | ≤ 2500ms (예시값 — 도메인에 따라 조정) | Core |
| **ASR** | Agent Success Rate | 에이전트가 성공한 작업의 비율 | ≥ 90% (이 사례의 기준값 — 도메인에 따라 조정) | Extended |
| **BR** | Bypass Rate | 우회권한으로 처리된 거래의 비율 | ≤ 5% (이 사례의 기준값 — 도메인에 따라 조정) | Extended |
| **BOR** | Bypass Overdue Rate | TTL 초과된 우회권한의 비율 | ≤ 1% (이 사례의 기준값 — 도메인에 따라 조정) | Extended |
| **RCR** | Remediation Completion Rate | 우회권한 remediation 작업 완료율 | ≥ 95% (이 사례의 기준값 — 도메인에 따라 조정) | Extended |

**일반 에이전트 도메인별 KPI 대체 예시:**

| 원본 KPI (결제 시스템) | 일반 에이전트 대체안 | 예시 임계치 |
|---|---|---|
| CCR (Covered Conversion Rate) | **Decision Coverage** - 의사결정 엔진이 작업을 평가/처리할 수 있는 비율 | ≥ 98% |
| ECR (Effective Conversion Rate) | **Task Completion Rate** - 에이전트가 시작한 작업 중 완료한 비율 | ≥ 95% |
| FBR (False Block Rate) | **False Rejection Rate** - 정상 요청을 거절한 비율 (또는 불필요한 에스컬레이션) | ≤ 5% |
| GL95 (Gate Latency P95) | **Response Latency P95** - 에이전트 응답 시간 95 percentile | ≤ 5000ms (도메인에 따라) |
| ASR (Agent Success Rate) | **Task Success Rate** - 에이전트가 완료한 작업 중 사용자 만족 비율 | ≥ 90% |
| BR (Bypass Rate) | **Manual Override Rate** - 자동화를 우회한 수동 개입 비율 | ≤ 10% (목표: 낮을수록 좋음) |
| BOR (Bypass Overdue Rate) | **Escalation Backlog Rate** - 미해결 에스컬레이션 항목의 비율 | ≤ 3% |
| RCR (Remediation Completion Rate) | **Issue Resolution Rate** - 식별된 문제의 해결 완료율 | ≥ 90% |

**측정 수식 (의사코드):**
```python
# CCR: 정책 엔진이 decision을 내린 비율
CCR = count(decisions_made) / count(transactions)

# ECR: CCR 중에서 실제로 conversion으로 이어진 비율
ECR = count(decisions_made AND allowed) / count(decisions_made)

# FBR: allowed 거래 중 false block (거짓 거절) 비율
FBR = count(denied AND later_verified_as_legitimate) / count(allowed)

# GL95: 95th percentile latency
GL95 = percentile(latencies, 95)

# ASR: 에이전트 작업 완료 성공률
ASR = count(successful_completions) / count(task_requests)

# BR: bypass로 처리된 거래의 비율
BR = count(bypass_allowed) / count(transactions)

# BOR: 만료된 bypass 중 remediation 미완료 비율
BOR = count(bypass WHERE state='EXPIRED' AND remediation_status!='CLOSED')
      / count(bypass WHERE expires_at < now())

# RCR: remediation task 완료율
RCR = count(remediation_tasks WHERE status='CLOSED')
      / count(remediation_tasks WHERE due_date < now())
```

**실제 대시보드 layout (결제 시스템 사례):**
```
╔═══════════════════════════════════════════════════════════════╗
║              Go-NoGo 의사결정 대시보드                          ║
║              (도메인에 따라 KPI와 임계치 조정)                   ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  📊 Core Metrics (모두 ≥ 임계치 필수)                          ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ CCR: 99.2% ✓ (≥98.5%)  ECR: 99.1% ✓ (≥98.5%)          │ ║
║  │ FBR: 1.8% ✓ (≤2.5%)    GL95: 1200ms ✓ (≤2500ms)       │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  📈 Extended Metrics                                         ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ ASR: 92% ✓ (≥90%)       BR: 3.2% ✓ (≤5%)               │ ║
║  │ BOR: 0.5% ✓ (≤1%)       RCR: 97% ✓ (≥95%)              │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  📋 7일 Trend (안정성 평가)                                    ║
║  ┌─────────────────────────────────────────────────────────┐ ║
║  │ CCR trend: ↔ 99.1-99.3% (안정)  ✓                      │ ║
║  │ FBR trend: ↘ 2.5-1.8% (개선)    ✓                      │ ║
║  └─────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  🎯 의사결정: GO                                              ║
║  이유: 모든 KPI 임계치 충족, trend 안정/개선                   ║
║  다음 단계: 대량 배포 해금 (100% 트래픽)                        ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### 롤백 트리거 4가지 (결제 시스템 사례)

배포 후 운영 중에 다음 조건을 감지하면 즉시 롤백합니다. 각 조건은 도메인 특성에 맞게 조정됩니다.

**Trigger 1: Core KPI 급락**
```
조건:
- 어느 Core KPI든 하루 만에 5% 이상 하락
- 또는 임계치 미달 전환

예시:
  FBR이 2.5% → 6% (3.5% 급락)
  → False block rate가 갑자기 2배 증가
  → 정상 사용자가 대량 차단됨

대응:
  즉시 롤백, root cause 분석
```

**Trigger 2: False Block Rate 2일 연속 초과**
```
조건:
- FBR > 임계치(2.5%)가 연속 2일 이상
- (충동적 대응 방지, 한 번의 spike는 무시)

예시:
  Day 1: FBR = 3.2% (초과)
  Day 2: FBR = 3.5% (초과)
  → 단순 spike가 아닌 systematic 문제

대응:
  롤백 + FBR 개선 로드맵 재검토
```

**Trigger 3: 신규 Critical Incident 발생**
```
조건:
- SEV1 incident (회사 전체 영향)
- 배포된 변경과의 연관성 > 70% (근인도 분석)

예시:
  배포 2시간 후:
  - 고객 결제 시스템 먹통 (실제 원인: 정책 엔진 timeout)
  - 영향: 1만 건 이상 거래 미처리

대응:
  즉시 롤백, 보상금 책정
```

**Trigger 4: Bypass Rate 과도 증가**
```
조건:
- BR이 baseline의 3배 이상으로 급증
- (우회권한으로 인한 compensating control 많음 = 자동화 부족)

예시:
  BR baseline: 2%
  배포 후: 7% (3.5배 증가)
  → 에이전트가 너무 aggressive해서 bypass로 회피

대응:
  롤백 + 에이전트 정책 조정 (confidence threshold 상향)
```

### 사전검시에서 Go-NoGo 대시보드까지의 연결고리

**연결점 1: 위험 식별 → KPI 매핑**
```
Premortem에서 식별한 위험:
  "정책 엔진이 느려진다" (RPN = 85)

KPI에 매핑:
  GL95 (Gate Latency P95) ≤ 2500ms

의사결정에 반영:
  배포 전: GL95 baseline 측정 (예: 800ms)
  배포 후: GL95 모니터링 (2500ms 초과 금지)
  만약 초과 → CONDITIONAL 경로로 전환
```

**연결점 2: Prevention 메커니즘 → KPI 임계치 설정**
```
Prevention을 설계했음:
  "Rate limiting을 추가해서 policing 오버로드 방지"

효과 측정 KPI:
  ECR (Effective Conversion Rate) = 정책 검증 통과율

임계치 설정의 근거:
  Rate limiting 추가 전: ECR 98.8%
  Rate limiting 추가 후: ECR 98.7% (예상)
  임계치 설정: ≥ 98.5% (버퍼 0.2% 확보)
```

**연결점 3: 모니터링 트리거 → 롤백 의사결정**
```
Premortem에서 정의한 모니터링:
  Yellow alert: FBR > 3%
  Red alert: FBR > 5%

배포 후 운영:
  Day 1 14:00 - FBR = 2.8% (Yellow 미달, 정상)
  Day 1 16:00 - FBR = 3.5% (Yellow alert 발생)
  Day 2 10:00 - FBR = 3.8% (Yellow 계속)

의사결정:
  Yellow가 24시간 이상 지속 → CONDITIONAL 판정
  설정값 FBR > 2.5%가 2일 연속 초과 → 롤백 트리거
```

**연결점 4: 액션 아이템 → KPI 책임 할당**
```
Premortem 액션 아이템:
  "정책 엔진 latency 모니터링 대시보드 구축"
  Owner: Alice
  Deadline: 배포 1주일 전

배포 후 책임:
  - 대시보드에서 GL95를 매일 리뷰
  - threshold 위반 시 Alice가 first responder
  - 이탈 원인을 분류 (진짜 문제 vs false alarm)
```
