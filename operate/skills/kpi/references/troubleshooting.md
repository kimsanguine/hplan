# Troubleshooting — kpi 스킬

## 1) KPI 정의 불명확로 인한 팀 간 혼동

**증상:**
- "데이터팀은 Accuracy를 이렇게 계산하고, PM팀은 저렇게 계산한다"
- 같은 메트릭을 다른 값으로 보고
- "어느 것이 맞는 데이터인가?" 논쟁 발생

**확인:**
- Accuracy 정의 확인:
  - 분자: 정답 판정 기준이 무엇인가? (완전 일치? 의미 일치?)
  - 분모: 전체 실행? 승인된 작업만? 특정 카테고리만?
- 데이터 소스:
  - 로그에서 계산? 데이터베이스에서? 수동 평가?
- 계산 주기:
  - 실시간? 일일? 주간? 월간?

**조치:**
1. KPI 정의 표준화:
   ```
   Metric: Accuracy
   Formula: (Correct Outputs) / (Total Executions) × 100%
   - Correct = Human evaluation 또는 자동 검증 기준
   - Total Executions = 모든 실행 (실패 포함)
   Data Source: DB table [logs], field [is_correct]
   Collection: Daily 00:00 UTC
   ```
2. 자동화 계산:
   - 스프레드시트 수동 계산 → SQL 쿼리 또는 자동화 스크립트
   - 단일 소스 of truth 지정
3. 팀 교육:
   - 정의 문서 공유
   - 계산 방법 워크숍
4. 검증:
   - 과거 데이터로 일관성 확인
   - 월간 리뷰 미팅에서 KPI 계산 재검증

---

## 2) 임계값 설정 오류

**증상:**
- "Accuracy > 95% 목표인데 지난달 92%였어"
- 첫 주부터 목표 미달 신호
- 팀 사기 저하, "어차피 못 하니까" 심리

**확인:**
- 기준선(Baseline) 확인: 현재 92%, 경쟁사는? 업계 표준은?
- 목표값의 현실성: 3개월 내 92% → 95% 달성 가능한가?
- 비교 기준 명확한가?

**조치:**
1. 단계적 목표 설정:
   ```
   Month 1: 92% (Baseline, 현상 유지)
   Month 2: 93% (+1% improvement)
   Month 3: 94% (+1% improvement)
   Month 6: 95% (최종 목표)
   ```
2. 비교값 기반 재설정:
   - 이전 버전 v1.0: 89%
   - v2.0 기준선: 92% (+3% 개선)
   - 3개월 목표: 94% (현재 92% + 2%)
3. Leading 지표 추가:
   - Accuracy 95% (Lagging, 뒤따르는 지표)
   - 오류율 추이 (Leading, 앞서는 지표)
   - Week 1에 오류율 감소 신호면 추후 Accuracy 개선 예상
4. 목표 재검토 미팅:
   - 분기별 목표 달성도 리뷰
   - 불가능하면 보수적으로 재설정

---

## 3) Guardrail 부재로 인한 역효과

**증상:**
- "CPE(비용) 최적화에만 집중했더니 Accuracy가 85%로 급락"
- "비용 절감이 제품 품질을 훼손했다"
- 고객 만족도 추락

**확인:**
- 현재 설정된 Anti-metric(반대 지표)이 있는가?
- Primary 최적화로 인한 Secondary 악화 여부
- Guardrail threshold 설정 여부

**조치:**
1. Anti-metric 명시:
   ```
   Primary: CPE < $0.10/execution (비용 최우선)
   Anti-metric 1: Accuracy > 90% (절대 떨어지면 안 됨)
   Anti-metric 2: Error Rate < 5% (안전 기준)
   ```
2. 트레이드오프 관리:
   - CPE 최적화 시 Accuracy 임계값 자동 체크
   - "CPE $0.05이어도 Accuracy < 90%면 STOP" 규칙
3. 최적화 전 A/B 테스트:
   - 비용 절감 방안 사전 검증
   - Accuracy 영향도 미리 확인
4. 대시보드 강화:
   - Primary + Anti-metric을 함께 표시
   - "CPE: $0.08 (목표 달성) / Accuracy: 88% ⚠️ (경고)"

---

## 4) 데이터 수집 및 보고 지연

**증상:**
- "일일 리포트가 2-3일 후에 생성된다"
- 어제 데이터를 오늘 아침 회의에서 봐야 하는데 못 본다
- 의사결정이 뒤처진다

**확인:**
- 현재 데이터 수집 주기 (일일? 주간?)
- 리포트 생성까지의 시간 (자동? 수동?)
- 필요한 리포트 빈도 (일일? 주간? 월간?)

**조치:**
1. 자동화 대시보드 구축:
   - SQL 쿼리 → 자동 일일 계산 (매일 자정)
   - 구글 시트 또는 BI 도구 자동 업데이트
   - 슬랙 봇 자동 알림 (아침 6시)
2. 메트릭 수준별 주기 분리:
   - 실시간: Error rate, Latency (P95)
   - 일일: Accuracy, CPE, Reliability
   - 주간: Business Impact (Time Saved, Cost Saved)
   - 월간: Strategic Review (OKR 연결)
3. 대시보드 우선순위:
   - 티어 1: Daily update (5개 핵심 KPI)
   - 티어 2: Weekly update (보조 지표)
   - 티어 3: Monthly update (전략 지표)
4. 알림 자동화:
   - 임계값 이탈 시 자동 슬랙 알림
   - "Accuracy < 90%: ⚠️ 주의"
   - "Error Rate > 5%: 🔴 긴급"

---

## 5) KPI 정의는 있으나 리뷰 없음

**증상:**
- "대시보드가 있는데 팀이 정기적으로 보지 않는다"
- KPI는 정의했지만 의사결정에 반영 안 됨
- 문제 조기 감지 안 됨

**확인:**
- KPI 리뷰 일정 정해졌는가?
- 담당자 지정되었는가?
- 리뷰 미팅에서 실제로 KPI를 논의하는가?

**조치:**
1. 고정 리뷰 일정 설정:
   ```
   일간: 아침 standup (5분, 긴급 알림만)
   주간: 수요일 오전 10시 (30분, 모든 KPI 검토)
   월간: 첫 주 월요일 (1시간, 전략 리뷰 + OKR 연결)
   ```
2. 담당자 지정:
   - PM: Accuracy, Business Impact (오너)
   - 엔지니어: Latency, Error Rate (오너)
   - Finance: CPE, Cost (오너)
3. 리뷰 아젠다 정형화:
   ```
   1. KPI 현황 (지난주/월 대비 변화)
   2. 이상 신호 (임계값 이탈)
   3. 원인 분석 (있으면)
   4. 액션 아이템 (개선 계획)
   ```
4. 의사결정 기록:
   - 리뷰 결과 → 액션 아이템 → 실행 → 다음 리뷰 확인
   - "OKR과 KPI 연결" 명시

