---
name: incident
description: "Respond to and learn from AI agent incidents — triage severity, coordinate response, contain blast radius, and write postmortems. Use when an agent produces harmful outputs, costs spike unexpectedly, accuracy drops suddenly, or users report critical failures."
argument-hint: "[incident description or agent name]"
allowed-tools: ["Read", "Write"]
model: sonnet
---

# Agent Incident Response

> 에이전트 장애 대응 프로토콜 — 발견, 분류, 대응, 복구, 학습

## Core Goal

- **에이전트 장애를 신속하게 감지하고 대응** — 침묵의 실패(Silent Failure)를 조기에 찾아내고 격리
- **블래스트 반경을 제한하고 영향 최소화** — 영향받은 사용자/비용 범위를 정확히 파악 후 신속 복구
- **장애 경험을 암묵지로 추출** — TK로 기록해서 비슷한 실패의 재발 방지

---

## Trigger Gate

### Use This Skill When

- 에이전트 정확도가 급락(> 10% 한 번에)했을 때
- 비용이 갑자기 폭증(2배 이상)했을 때
- PII 또는 민감 정보 유출 신호가 있을 때
- 사용자 신고 또는 SNS 부정적 언급이 들어왔을 때
- 내부 QA/모니터링에서 에러율 급증을 탐지했을 때

### Route to Other Skills When

- **premortem** → 장애 원인 분석 후 유사 실패 예방 메커니즘 설계
- **burn-rate** → 비용 폭증이 토큰 사용량 이상이라면 (비용 최적화 필요)
- **reliability** → 장애 복구 후 신뢰성 개선 계획 수립
- **cohort** → 특정 버전/세그먼트만 장애를 겪었다면 (코호트 분석)

### Boundary Checks

- **실제 장애 vs 정상 변동** — Accuracy 1-2% 변화는 정상 범위, > 5% 이상이면 조사
- **원인 판단 과정** — 5 Whys를 최소 3단계 이상 실행해야 근본 원인 파악 가능
- **영향도 산정 정확성** — 추정이 아닌 실제 영향받은 사용자/트래잭션 로그 기반 확인

---

## 개념

에이전트 장애는 일반 소프트웨어 장애와 다르다. "서버가 죽었다"는 명확하지만, "에이전트가 환각으로 잘못된 답을 줬다"는 발견 자체가 어렵다. 침묵의 실패(Silent Failure)가 에이전트 장애의 가장 위험한 유형이다.

## Instructions

You are running **incident response** for: **$ARGUMENTS**

### Step 1 — Incident Detection & Classification

```
발견 시각: [timestamp]
발견 방법:
  □ 자동 모니터링 알림
  □ 사용자 신고
  □ 내부 QA 발견
  □ 비용 이상 감지
  □ 외부 보고 (SNS, 언론)
```

**Severity Classification:**

| SEV | 정의 | 예시 | 대응 시간 |
|-----|------|------|----------|
| **SEV-1** | 전체 서비스 중단 또는 데이터 유출 | 에이전트가 PII를 외부에 노출 | 15분 이내 |
| **SEV-2** | 핵심 기능 장애, 다수 유저 영향 | 정확도 50% 이하로 급락, 비용 10배 폭등 | 1시간 이내 |
| **SEV-3** | 일부 기능 저하, 소수 유저 영향 | 특정 입력에서 환각 반복 | 4시간 이내 |
| **SEV-4** | 경미한 품질 저하, 우회 가능 | 응답 속도 저하, 포맷 깨짐 | 24시간 이내 |

### Step 2 — Immediate Response

**에이전트 장애 유형별 긴급 대응:**

```
🔴 환각/오정보 장애:
  1. 해당 에이전트 기능 즉시 비활성화
  2. 영향 범위 확인 (몇 명이 잘못된 정보를 받았는가?)
  3. 영향받은 유저에게 정정 통보
  4. 원인 분석 (프롬프트 문제? 모델 변경? 입력 데이터 오염?)

🔴 비용 폭등 장애:
  1. API 호출 rate limit 즉시 설정
  2. 비용 발생 원인 추적 (무한 루프? 토큰 폭발? 잘못된 모델 라우팅?)
  3. 비용 캡 설정
  4. 영향받은 기간의 비용 산출

🔴 데이터 유출 장애:
  1. 에이전트 즉시 중단
  2. 유출 범위 파악 (어떤 데이터, 누구에게, 어디로)
  3. 법무팀 즉시 통보
  4. 규제 보고 필요 여부 판단 (GDPR, 개인정보보호법)

🔴 연쇄 실패 장애 (멀티에이전트):
  1. 오케스트레이터 에이전트 중단
  2. 하위 에이전트 상태 확인
  3. 실패 전파 경로 추적
  4. 격리 후 개별 에이전트 순차 재시작
```

### Step 3 — Blast Radius Assessment

```
영향 범위:
  유저 수: [N]명
  기간: [start] ~ [end]
  데이터 영향: [none / read / write / delete]
  비용 영향: $[amount]
  평판 영향: [none / internal only / external / media]

영향받은 시스템:
  □ 에이전트 자체
  □ 연동 API/서비스
  □ 데이터 저장소
  □ 하위 에이전트 (멀티에이전트)
  □ 사용자 데이터
```

### Step 4 — Recovery

```
단기 복구:
  ├── Rollback: 이전 안정 버전으로 복구 [Y/N]
  ├── Hotfix: 긴급 수정 배포 [내용]
  ├── Workaround: 임시 우회 방법 [내용]
  └── Communication: 유저/이해관계자 통보 [완료 여부]

장기 복구:
  ├── Root Cause Fix: 근본 원인 해결 [계획]
  ├── Monitoring: 재발 감지 알림 추가 [내용]
  ├── Testing: 회귀 테스트 추가 [내용]
  └── TK Extraction: 이 장애에서 배운 판단 기준 → TK로 추출
```

### Step 5 — Postmortem

```
Postmortem: [incident title]
Date: [date]
Severity: [SEV-1/2/3/4]
Duration: [detection] ~ [recovery] = [N]시간

Timeline:
  [T+0]  [발견]
  [T+Nm] [1차 대응]
  [T+Nh] [원인 파악]
  [T+Nh] [복구 완료]

Root Cause:
  [근본 원인 — "5 Whys" 적용]
  1. Why: [direct cause]
  2. Why: [underlying cause]
  3. Why: [systemic cause]
  4. Why: [process gap]
  5. Why: [cultural/structural root]

What Went Well:
  - [잘 대응한 것]

What Went Wrong:
  - [개선할 것]

Action Items:
  □ [action 1] — Owner: [name] — Due: [date]
  □ [action 2] — Owner: [name] — Due: [date]
  □ [action 3] — Owner: [name] — Due: [date]

TK Extracted:
  TK-[NNN]: [이 장애에서 추출한 암묵지]
```

### Output

```
Incident Report: [title]
──────────────────────────
Severity: [SEV-N]
Status: [Active / Mitigated / Resolved]
Blast Radius: [N] users, $[cost], [duration]
Root Cause: [one-line]
Recovery: [rollback / hotfix / workaround]
Action Items: [N] items, [N] completed
TK Extracted: [TK-NNN title]
```

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| **심각도 분류 착오** | SEV-3로 분류했으나 실제 영향은 다수 유저(SEV-2 수준) | 심각도 재조정, 대응 인력 증원, 에스컬레이션 |
| **원인 분석 불완전** | 직접 원인만 파악(e.g., "API timeout") → 근본 원인까지 못 미침 | 5 Whys를 최소 3단계 이상 진행, 시스템 레벨 원인 추출 |
| **블래스트 반경 과소 평가** | "100명 영향받았다"고 보고 → 나중에 1000명 발견 | 영향도 재산정, 추가 공지, TK 추출 내용 확대 |
| **롤백 불가능** | 이전 버전이 없거나 복구 경로 불명확 → 복구 시간 지연 | 향후 버전 관리 강화, 즉시 hotfix 대안 검토 |
| **커뮤니케이션 지연** | 영향받은 유저에게 12시간 후 통보 → 신뢰도 추락 | 초기 상황 인식 후 1시간 이내 1차 공지, 이후 4시간 주기 업데이트 |

---

## Quality Gate

- [ ] 심각도가 정확히 분류되었는가? (SEV-1/2/3/4 명확한 증거 기반) (Yes/No)
- [ ] 블래스트 반경(영향받은 사용자, 기간, 데이터)이 정량화되었는가? (Yes/No)
- [ ] 긴급 대응 단계(격리, hotfix 또는 rollback)가 명확한가? (Yes/No)
- [ ] 5 Whys 분석으로 근본 원인을 최소 3단계 이상 파악했는가? (Yes/No)
- [ ] 영향받은 이해관계자에게 1시간 이내 1차 공지를 했는가? (Yes/No)
- [ ] TK로 추출된 학습 내용이 기록되었으며 premortem과 연결되었는가? (Yes/No)

---

## Examples

### Good Example

```
장애 대응: 고객 지원 에이전트 "환각 오정보" 장애

발견: 2026-03-05 14:23 (자동 모니터링 알림)
심각도: SEV-2 (정확도 48% → 급락, 다수 유저 영향)

초기 대응 (T+0 ~ T+30분):
1. 에이전트 기능 즉시 비활성화
2. 영향도 파악: 2,340명이 잘못된 정보 수신 (2시간 기간)
3. 사용자에게 1차 공지 (정정 메시지 발송)

원인 분석 (T+30분 ~ T+2시간):
- Why 1: 정확도 급락 → 모델 응답 형식 오류 감지
- Why 2: 형식 오류 → 새로운 시스템 프롬프트 적용 후 발생
- Why 3: 프롬프트 변경 → QA 테스트 없이 배포됨
- Why 4: 배포 절차 우회 → 긴급 배포 프로세스 부재
- Why 5: 프로세스 부재 → 자동화된 QA 게이트 미설정

복구 (T+2시간):
- Rollback: 이전 프롬프트 버전 배포
- 검증: 정확도 복구 확인 (94% 회복)
- 재배포: QA 자동화 추가 후 신규 프롬프트 재배포

TK 추출:
- TK-042: 프롬프트 변경 시 QA 자동화 게이트 필수
- TK-043: 시스템 프롬프트 변경은 A/B 테스트 경유
```

### Bad Example

```
"정확도가 떨어졌는데 나중에 원인을 찾자"

❌ 문제점:
- 즉시 대응 없음 (사용자 계속 잘못된 정보 받음)
- 심각도 분류 안 함
- 영향도 파악 미루기
- "아마 모델 문제인 것 같다"는 추측 (근본 원인 분석 안 함)
- 이용자에게 공지 안 함 (신뢰도 추락)
- 이 장애로부터 배운 게 없음

→ 재작업: 즉시 대응 체크리스트 → 블래스트 반경 파악 → 5 Whys → TK 추출
```

---

### 참고
- 설계자: AI PM Skills Contributors, 2026-03
- 에이전트 장애 유형 분류: production agent 운영 장애 대응 경험 기반
- Silent Failure 패턴: 환각이 "그럴듯한 답"이라 유저가 장애를 인지 못 하는 케이스
- premortem 스킬과 상호 보완 (사전 예방 vs 사후 대응)

---

## Further Reading
- Google SRE Book, "Managing Incidents" — Incident response process and postmortem culture
- Anthropic, "Building Effective Agents" (2024) — Agent error handling and recovery patterns

---

## Test Cases

!`cat references/test-cases.md 2>/dev/null || echo ""`

## Troubleshooting

!`cat references/troubleshooting.md 2>/dev/null || echo ""`

---

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
