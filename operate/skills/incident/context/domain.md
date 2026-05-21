# Domain Context — Incident

## 1) Domain Scope

**에이전트 장애의 신속한 대응, 격리, 복구 및 학습 추출**

- Incident 검출 및 심각도 분류 (SEV-1/2/3/4)
- Immediate response: 격리, hotfix/rollback, 통보
- Blast radius assessment: 영향받은 사용자, 기간, 데이터, 비용
- Root cause analysis: 5 Whys로 근본 원인 파악
- Postmortem: Timeline, 근본 원인, What Went Well/Wrong, 액션 아이템
- TK Extraction: 이 장애에서 배운 판단 기준을 TK로 추출

## 2) Primary Users

- **On-call 엔지니어**: 즉시 대응, 격리, hotfix
- **에이전트 팀 리더**: 심각도 판단, 에스컬레이션, 통신
- **PM/리더**: 비즈니스 영향도 파악, 의사결정
- **Post-incident 리더**: Postmortem 진행, 학습 추출

## 3) Required Inputs

- **장애 신고 정보**: 발견 시각, 발견 방법, 초기 증상
- **에이전트 상태**: 현재 코드/모델/프롬프트 버전
- **운영 환경**: 트래픽, 의존성, 최근 배포 이력
- **모니터링 데이터**: 에러율, 응답시간, 비용 급증 그래프
- **사용자 피드백** (있다면): SNS 언급, 고객 신고, 내부 리포팅

## 4) Output Contract

- **Incident 분류**: SEV-1/2/3/4 명확화 (근거 포함)
- **Immediate response 결과**: 격리 완료 여부, Hotfix/Rollback 상태
- **Blast radius 정량화**: N명 사용자, $X 비용, N시간 기간
- **Root cause**: 5 Whys 적용해 최소 3단계 이상 분석
- **Postmortem 문서**: Timeline, 근본 원인, 액션 아이템, TK 추출
- **후속 추적**: 액션 아이템별 Owner/Deadline, premortem 연결

## 5) Guardrails

- **심각도 분류 착오**: SEV-3으로 분류했으나 실제는 SEV-2 → 재조정 및 인력 증원
- **원인 분석 불완전**: 직접 원인만 파악("API timeout") → 근본 원인까지 추진(5 Whys 3단계 이상)
- **블래스트 반경 과소 평가**: "100명"이라고 보고 → 실제 1000명 → 재산정 및 추가 공지
- **롤백 불가능**: 이전 버전 없거나 경로 불명확 → hotfix 대안 즉시 검토
- **커뮤니케이션 지연**: 12시간 후 통보 → 신뢰도 추락 (1시간 내 1차 공지 필수)

## 6) Working Facts (TO BE UPDATED by reviewer)

- **SEV 정의**: SEV-1 전체 중단/데이터 유출, SEV-2 핵심 기능 장애, SEV-3 일부 저하, SEV-4 경미
- **대응 시간**: SEV-1 15분, SEV-2 1시간, SEV-3 4시간, SEV-4 24시간
- **Silent failure**: 환각이 "그럴듯해서" 사용자가 장애를 모르는 케이스 (높은 위험)
- **Postmortem 참석**: On-call, 팀 리더, PM, 관련 엔지니어 필수
- **TK 추출**: 장애 유형별 판단 기준 (예: "시스템 프롬프트 변경은 A/B 테스트 경유")

## 7) Fill-in Checklist

- [ ] 장애 발견 시각, 방법, 초기 증상 기록
- [ ] 심각도 분류 (SEV-1/2/3/4) 및 근거 명시
- [ ] 즉시 대응 실행 (격리, hotfix/rollback, 1차 통보)
- [ ] 블래스트 반경 정량화 (사용자, 기간, 데이터, 비용)
- [ ] 5 Whys로 근본 원인 파악 (최소 3단계)
- [ ] Postmortem 미팅 진행 및 기록
- [ ] 액션 아이템 Owner/Deadline 명시
- [ ] TK 추출 (이 장애에서 배운 판단 기준)
- [ ] Premortem과 연결 (이 유형의 실패 방지 메커니즘 설계)
- [ ] 후속 모니터링 강화 (새로운 alert 추가)

---

## 8) 참고 사례: 작업 관리 플랫폼의 Preflight 체계

### Top10 Painpoint → Preflight Check 매핑

**Preflight (사전 차단) 체계는 사후 대응이 아닌 사전 예방**으로 인시던트 발생 가능성을 근본적으로 차단합니다.

아래 Top10은 특정 작업 관리 플랫폼에서 식별한 항목입니다. 다른 도메인(문서 생성, 이메일 분류, 결제 처리 등)의 에이전트에는 다른 항목이 필요합니다.

| Top10 Painpoint | Preflight Check | 차단 조건 | 효과 |
|---|---|---|---|
| **T01** 대상 범위 오류 (잘못된 사용자/팀 대상) | `scope_target_valid` | 요청 대상이 실제 접근 권한 보유 확인 | 의도하지 않은 영향도 발생 방지 |
| **T02** Private Team 권한 누락 | `private_access_valid` | Private Team 쓰기 시 팀 멤버십 확인 | 무권한 접근 차단 (403) |
| **T03** 미지원 플랜 기능 (Free plan에서 Enterprise 기능 시도) | `plan_capability_valid` | 기능-플랜 매트릭스 검증 | 지원되지 않는 기능 실행 방지 |
| **T04** 필수 필드 누락 (payload 검증 실패) | `payload_schema_valid` | JSON schema validation | 불완전한 데이터 입수 방지 |
| **T05** 상태전이 규칙 위반 (예: Completed → Draft) | `transition_rule_valid` | 상태 머신 규칙 검증 | 불가능한 상태 변화 방지 |
| **T06** 중복 생성 (동일 요청 재전송으로 중복 task 생성) | `idempotency_valid` | Idempotency token/key 검증 | 같은 데이터 중복 입수 방지 |
| **T07** Jira Sync 불일치 (선형과 Jira 상태 동기화 오류) | `jira_sync_health_valid` | Sync 레이턴시/실패율 모니터 | 외부 시스템 불일치 감지 |
| **T08** Rate Limit 초과 (과도한 요청으로 API 부하) | `quota_budget_valid` | 사용량 % 기반 경고·큐잉·차단 | 서비스 과부하 방지 |
| **T09** Webhook 위변조/Replay (서명 검증 미흡, 재생 공격) | `webhook_trust_valid` | HMAC 서명 검증 + replay drop | 신뢰할 수 없는 이벤트 차단 |
| **T10** 감시추적 부재 (누가 언제 무엇을 했는지 기록 없음) | `audit_trace_valid` | 모든 쓰기 작업의 audit log 기록 | 사후 추적 불가 상황 방지 |

### Gate Rule 적용 원칙

**1) Private Team 가드레일**
- 규칙: Private Team에 대한 무권한 쓰기는 **즉시 403 차단**
- 예외: 만료형(TTL) 임시 권한만 인정 (시간 제한 필수)
- 정기 감시: Private Team 무권한 시도 반복 패턴 추적

**2) Plan Gating 매트릭스**
- 규칙: 지원되지 않는 기능-플랜 조합은 차단
- 예시: Free 플랜이 "Custom Field" 생성 시도 → BLOCK
- 우회 신호: 미지원 plan 기능이 성공하는 징후 발생 시 즉시 조사

**3) Rate Limit 3단계 전략**
- **80% 도달**: 자동 경고 (로그 + 대시보드 알림)
- **95% 도달**: 자동 큐잉 (요청 버퍼링, 순차 처리)
- **100% 도달**: 차단 + 운영팀 에스컬레이션

**4) Webhook 신뢰 검증**
- 규칙: 모든 webhook 수신 시 HMAC-SHA256 서명 검증
- Replay 방지: 이미 처리된 webhook ID는 Drop
- 실패 처리: 서명 검증 실패 → 403 거부 + alert

### 우회 위험 신호 5가지 모니터링

Preflight 체계가 제대로 작동하려면, 우회 시도를 지속적으로 감시해야 합니다:

1. **Preflight 누락 쓰기 비율 증가**
   - 신호: "preflight 스킵하고 바로 쓰기" 요청이 전일 대비 >10% 증가
   - 대응: 즉시 로그 분석 + 요청 출처 추적

2. **Private Team 무권한 시도 반복**
   - 신호: 같은 팀에 대한 403 거부가 시간당 >5회
   - 대응: 해당 요청자 계정 감사 (탈취 의심) + 임시 차단

3. **미지원 Plan 기능 성공 징후**
   - 신호: Free 플랜에서 Enterprise 기능이 성공적으로 실행됨
   - 대응: Plan Gating 로직 재검증 (버그?) + 이미 생성된 데이터 감사

4. **Jira Mismatch/Lag 악화**
   - 신호: 선형과 Jira 상태 불일치가 지난주 대비 >20% 증가, 또는 sync 지연 >5분
   - 대응: Webhook 상태 확인 + Jira API 응답시간 분석

5. **Webhook 서명 실패/Replay 급증**
   - 신호: 서명 검증 실패가 시간당 >10건, 또는 replay 감지가 >3회/일
   - 대응: 외부 이벤트 소스 신원 확인 + Secret rotation 검토

### 자체 Preflight 설계 가이드

다른 도메인의 에이전트를 위해 맞춤형 Preflight 체계를 설계하려면:

**1) 과거 장애 이력에서 Top 원인 추출**
   - 지난 3개월~1년 incident postmortem 검토
   - 각 incident의 "실제 근본 원인" 파악 (표면 원인 아님)
   - 반복되는 패턴 식별 (예: "데이터 누락 검증 실패"가 3회 이상)
   - 상위 10개 항목 선정

**2) 각 원인별 사전 검증 가능 여부 판단**
   - "이 원인을 배포/실행 전에 자동으로 감지할 수 있는가?"
   - 가능 → Preflight check로 설계
   - 불가능 → 모니터링/alert로 전환

**3) 자동 차단 vs 경고 기준 설정**
   - **자동 차단 (Fail-Closed)**: 보안, 데이터 무결성, SLA 위반 위험
   - **경고 (Warning/Alert)**: 의심스럽지만 비즈니스 영향 낮음, 수동 검토 가능
   - 각 check별로 심각도 정의

### 적용 교훈: 사전 차단의 효과

**인시던트 대응에서 사전 차단(preflight)이 사후 대응보다 효과적인 이유:**

- **비용**: 사후 대응(SEV-2 인시던트) 평균 비용 $50K vs. preflight 구현 $5K → **10배 절감**
- **속도**: 발생 후 대응(평균 2시간) vs. 발생 전 차단(0초) → **무한 개선**
- **신뢰도**: 장애 후 신뢰 회복 기간 2주 vs. 장애 없음 → **고객 만족도 유지**
- **팀 소모**: 야간 호출(oncall) 제거 → 엔지니어 번아웃 감소
- **추적**: 사후 "뭐가 잘못됐나?" vs. 사전 "왜 차단했나?" → 더 명확한 근본 원인

**따라서 인시던트 대응 설계 시, 위 가이드에 따라 도메인별 Top10 Preflight 체계를 사전 구축하고, 우회 신호를 자동 감시하는 것이 필수입니다.**
