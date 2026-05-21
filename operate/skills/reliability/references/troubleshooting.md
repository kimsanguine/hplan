# Troubleshooting — Reliability

## 1) 신뢰성 기준선이 팀마다 다름

### 증상
- 같은 데이터인데 팀마다 신뢰성 계산이 다름
- "95%"라는 숫자가 팀마다 의미하는 바가 다름

### 확인
- Success 정의가 명확한가? ("응답 받았으면?" vs "정확도 > 80%?")
- Partial success를 따로 추적하는가?
- 실패의 경계가 명확한가? (타임아웃? 에러 반환? 환각?)

### 조치
1. Success/Failure formula 명시화
   ```
   Success = (응답 시간 < Xs) AND (응답 형식 valid) AND (에러 타입 X 미포함)
   Partial = (응답 있음) AND (정확도 < 80%)
   Failure = (응답 미함) OR (에러 반환)
   ```

2. 자동화 계산으로 전환 (수동 분류 배제)
3. 팀 공동 검증 (샘플 100건 기준으로 일치율 > 95% 확인)

## 2) 실패 분류가 너무 세분화됨

### 증상
- Input Error, Input Format Error, Input Encoding Error, Input Parsing Error... (10개 이상)
- 분류 체계가 복잡해서 실제 분석이 안 됨

### 확인
- 분류 개수가 5-7개보다 많은가?
- 유사한 실패들이 다른 카테고리로 분산되었는가?
- 각 카테고리별 대응이 다른가? (같으면 통합 가능)

### 조치
1. 분류 단순화
   ```
   Before: Input Format Error, Input Encoding Error → 통합
   After: Input Error (1가지로 통합)
   ```

2. Sub-category 추가 (필요시만)
   ```
   Input Error
   ├── Format issue
   ├── Encoding issue
   └── Missing field
   ```

3. 대응 전략이 같으면 통합 (분류의 목적은 대응 전략)

## 3) Safeguard 추가로 성능 저하

### 증상
- Confidence Gate 추가 → 정확도는 올랐지만 응답 불가율 15% 증가
- 사용자가 "왜 응답이 없는 거야?"라고 불평

### 확인
- Confidence threshold가 너무 높은가?
- Fallback path가 있는가? (거절된 요청을 어디로 보내나?)
- 트레이드오프 분석이 되었는가?

### 조치
1. Threshold 조정 (단계적)
   ```
   Current: 0.7 (응답 불가 15%)
   Adjust: 0.5 (응답 불가 8% 예상) → 테스트
   Monitor: 정확도/응답율 2주 추이 확인
   ```

2. Fallback 경로 개선
   - Reject 대신 "Lower confidence mode" 제공
   - 사람에게 에스컬레이션 (HITL)
   - 캐시된 응답 제공

3. 트레이드오프 명시
   - "정확도 98% (신뢰) but 응답 가능 95%"
   - 비즈니스와 합의

## 4) 특정 입력에서만 실패

### 증상
- 대부분의 요청은 성공하는데 특정 패턴에서만 오류
- 예: 특수문자 포함, 길이 > 1000자, 특정 도메인 용어 사용

### 확인
- 실패 입력의 공통점이 있는가?
- 그 패턴의 발생 빈도는? (흔한가? 드문가?)
- 이미 해당 카테고리의 Safeguard가 있는가?

### 조치
1. 패턴 분석
   ```
   특수문자 포함 요청 → 100건 중 50건 실패 (50% 실패율)
   → 높은 우선순위
   ```

2. Safeguard 추가 또는 강화
   ```
   Input Validation: 특수문자 정규화 또는 거절
   또는 Model: 특수문자 처리 능력 높은 모델로 라우팅
   ```

3. 별도 모니터링 설정
   - 해당 패턴 요청의 주간 트렌드 추적
   - 개선 효과 측정

## 5) Safeguard 비용이 너무 높음

### 증상
- Retry with exponential backoff 추가 → 토큰 비용 20% 증가
- 리더: "이 정도 비용 증가는 정당화될 수 있나?"

### 확인
- 비용 증가가 실제로 측정되었는가?
- 신뢰성 개선 효과는 얼마인가? (비용 대비)
- 더 저비용 대안이 있는가?

### 조치
1. 비용-효과 분석
   ```
   비용 증가: +$100/월 (20%)
   신뢰성 개선: 95% → 97% (+2%)
   ROI: 신뢰성 1%당 $50/월

   의사결정: 비즈니스 가치가 $50/월 이상이면 Ship
   ```

2. 더 저비용 대안 검토
   ```
   Retry (current): +$100, +2% improvement
   Confidence Gate: +$10, +1.5% improvement
   Input Validation: +$0, +0.5% improvement

   Sequential: Validation → Gate → Retry 순으로 추가
   ```

3. 선택적 적용
   - 중요한 요청만 Retry (프리미엄 사용자)
   - 일반 요청은 단순한 Fallback

## 6) 신뢰성 목표 달성 불가능

### 증상
- 99% 목표는 설정했는데 현재 95%
- 4% gap을 좁히기 위해 개선해야 할 것들이 너무 많음

### 확인
- 목표가 현실적인가? (비교값: 이전 버전, 경쟁사, 업계 표준)
- gap을 나누는 요인들이 파악되었는가?
  - Model Error가 60개 중 40개 개선 가능 (2%)
  - Tool Error가 20개 중 15개 복구 가능 (0.5%)
  - 나머지 1.5%는?

### 조치
1. Gap 분석
   ```
   현재 95% → 목표 99% (4% gap)

   가능한 개선:
   - Model Error 개선: +2% (Confidence Gate)
   - Tool Error 개선: +0.5% (Retry)
   - Input Validation: +0.5%
   - Output Length Limit: +0.3%
   ──────────────────
   총 개선 예상: +3.3% → 98.3%

   남은 0.7%: 아키텍처 변경 필요 (Long term)
   ```

2. 단계적 목표 설정
   ```
   Phase 1 (1개월): 97% (빠른 개선 항목)
   Phase 2 (3개월): 98% (중간 난이도)
   Phase 3 (6개월): 99% (아키텍처 개선)
   ```

3. 목표 현실화 (필요시)
   - 업계 표준 검토 (고객 지원 챗봇 95-98%가 일반적)
   - 비즈니스 요구와 재합의

## 7) 신뢰성 개선이 다른 지표를 악화

### 증상
- Accuracy 개선 위해 Confidence gate 추가
- → Accuracy 98% ↑ (개선)
- → Latency 1.2s → 2.5s ↑ (악화, 검증 오버헤드)
- → Cost per task +30% (악화)

### 확인
- Anti-metrics가 설정되었는가? (신뢰성 개선 과정에서 뭘 지켜야 하는가?)
- 트레이드오프 분석이 되었는가?
- 다른 지표가 정말 중요한가?

### 조치
1. Anti-metrics 명시화
   ```
   신뢰성 목표: 99%
   Anti-metrics:
   - Latency > 3초 안 됨 (사용자 경험)
   - Cost per task > 1.5× 안 됨 (비즈니스)
   ```

2. 트레이드오프 관리
   ```
   Option A: Confidence Gate (Accuracy ↑, Latency ↑, Cost ↑)
   Option B: Retry (Accuracy ↑, Latency ↑↑, Cost ↑↑)
   Option C: Model upgrade (Accuracy ↑, Latency ↔, Cost ↑)

   선택: Option C (latency 유지, 비용 증가만 감수)
   ```

3. 의사결정 기록
   - 선택한 전략과 이유
   - 포기한 anti-metrics와 이유
   - 리뷰 시점 (3개월 후 재검토)

## 8) 실전 트러블슈팅 사례

### 증상 1: 에이전트 모드 Flap 발생 (Open↔Closed 반복)

#### 현상
```
14:00 - Open mode 전환 (외부 API 장애 감지)
14:05 - 잠시 정상화 → Closed mode 복구
14:08 - 다시 API 타임아웃 → Open mode
14:12 - 다시 정상 → Closed mode
... (계속 반복) ...
```
- 결과: 사용자 경험 매우 나쁨 (자주 정책 우회)
- 감시 시스템이 혼란 (모니터링 신호 신뢰도 하락)

#### 원인 분석
- 외부 API가 "깜깜이" 상태 (간헐적 실패, 일관성 없음)
- Healthy window 설정이 너무 짧음 (최근 10분 데이터만 참고)
- 모니터링이 세분화되지 않음 (5xx 에러와 timeout을 구분 안 함)

#### 조치: Flap 감지 로직 + Cooldown 설계
```python
# Flap 감지: 24시간 내에 같은 방향 전환이 3회 이상인가?
flap_count = count_transitions_last_24h()
if flap_count >= 3:
    # 강제 상태 고정
    force_mode("CLOSED")  # 또는 조직 정책에 따라 OPEN
    alert_level = "RED"   # 즉시 대응 필요
    escalate_to_oncall()

# Cooldown: 모드 전환 후 최소 대기 시간 설정
# (예: Closed → Open 전환 후 2시간은 다시 전환하지 않음)
last_transition_time = get_last_transition()
if now() - last_transition_time < cooldown_duration:
    log("Cooldown 중. 전환 유보")
    skip_transition()
else:
    evaluate_condition_and_transition()
```

#### 학습
- Flap 감지 카운터를 모니터링 메트릭에 포함할 것
- 상태 전이의 "거리"를 명시화 (Open → Closed 전환 비용이 높음 = 신중한 판단)
- 외부 의존성이 불안정한 경우 "회색 영역" 상태 추가 고려 (DEGRADED)

---

### 증상 2: Bypass 우회권한 Overdue 누적

#### 현상
```
검사 리스트 조회:
- bypass_001: expires_at = 2026-02-28, remediation_due = 2026-03-05 (현재 2026-03-07) ⚠️ OVERDUE
- bypass_002: expires_at = 2026-02-25, remediation_due = 2026-03-04 (현재 2026-03-07) ⚠️ OVERDUE
- bypass_003: expires_at = 2026-03-01, remediation_due = 2026-03-06 (현재 2026-03-07) ⚠️ OVERDUE
...

누적된 overdue bypass: 12개 (지난주 발급분)
```

#### 원인 분석
- Bypass 발급은 되었으나 remediation task가 생성되지 않음
- 담당자가 reminder를 못 받거나 우선순위 떨어짐
- 자동 만료 메커니즘 부재

#### 조치: TTL 자동만료 + 자동 Remediation Task 생성

**자동 만료 프로세스:**
```python
# Cron job: 매시간 실행
def expire_overdue_bypasses():
    overdue = query("""
        SELECT id, requester, approver, remediation_due
        FROM bypass_audit
        WHERE state = 'APPROVED_ACTIVE'
          AND remediation_due <= now()
    """)

    for bypass in overdue:
        # 1) 상태 전이 기록 (append-only)
        insert_audit_record({
            "bypass_id": bypass.id,
            "state_from": "APPROVED_ACTIVE",
            "state_to": "EXPIRED",
            "timestamp": now(),
            "reason": "TTL 자동만료",
            "hash": compute_hash(prev_record)
        })

        # 2) 자동 remediation task 생성
        create_task({
            "title": f"Bypass {bypass.id} 자동만료 - 재검증 필요",
            "assignee": bypass.approver,  # 원래 승인자가 remediation 담당
            "priority": "HIGH",
            "due_date": now() + timedelta(days=3),
            "description": "만료된 우회권한. 정책 위반 여부 검증 후 CLOSED로 전이",
            "linked_bypass": bypass.id
        })

        # 3) Slack 알림
        notify(f"Bypass {bypass.id} 만료됨. 담당자: {bypass.approver}")
```

**개선 효과:**
- Overdue bypass 자동 정리 (수동 추적 불필요)
- 감사 선순환: 만료 → task 생성 → 재검증 → CLOSED
- 보안 강화: 우회권한의 생명주기가 명확해짐

#### 학습
- Remediation task 자동 생성이 compliance의 핵심
- 각 상태 전이는 단순히 업데이트가 아닌 append-only 기록
- Task SLA(due_date)를 remediation_due보다 앞당길 것 (버퍼 필요)

---

### 증상 3: Audit 무결성 깨짐 (해시체인 검증 실패)

#### 현상
```
검증 결과:
bypass_123 레코드 체인:
  Record 1: hash = "abc123", prev_hash = null ✓
  Record 2: hash = "def456", prev_hash = "abc123" ✓
  Record 3: hash = "ghi789", prev_hash = "xyz999" ✗ MISMATCH!

감지 사항: Record 3의 prev_hash가 Record 2의 hash와 불일치
→ 누군가 Record 3을 수정했거나 삭제했을 가능성 높음
```

#### 원인 분석
- 감사 테이블이 UPDATE 쿼리를 허용함 (설계 실수)
- 또는 DELETE + INSERT로 레코드를 "교체"한 시도
- 또는 데이터베이스 복제 오류로 체인이 깨짐

#### 조치: 해시체인 검증 + INSERT-Only 정책 강화

**해시체인 검증 로직:**
```python
def verify_audit_chain(bypass_id):
    """
    전체 감사 체인의 무결성을 검증하고,
    위반 사항을 자동 보고한다.
    """
    records = query(f"SELECT * FROM bypass_audit WHERE bypass_id = ? ORDER BY timestamp ASC")

    prev_hash = None
    violations = []

    for record in records:
        # 1) 현재 레코드의 hash 재계산
        computed_hash = compute_hash({
            "id": record.id,
            "state": record.state,
            "timestamp": record.timestamp,
            "prev_hash": record.prev_hash
        })

        # 2) 저장된 hash와 일치하는가?
        if computed_hash != record.hash:
            violations.append({
                "record_id": record.id,
                "issue": "Hash mismatch (레코드 변조)",
                "expected": computed_hash,
                "actual": record.hash
            })

        # 3) 이전 레코드와 체인이 연결되는가?
        if prev_hash is not None and record.prev_hash != prev_hash:
            violations.append({
                "record_id": record.id,
                "issue": "Chain broken (레코드 누락 또는 재배열)",
                "expected_prev": prev_hash,
                "actual_prev": record.prev_hash
            })

        prev_hash = record.hash

    if violations:
        # 보안 이벤트 발생
        security_alert({
            "severity": "CRITICAL",
            "bypass_id": bypass_id,
            "violations": violations,
            "action": "Bypass 즉시 REVOKED, 조사팀 호출"
        })

        # 강제 상태 전이
        revoke_bypass(bypass_id)
        escalate_to_security_team()

    return len(violations) == 0
```

**INSERT-Only 정책 강화:**
```sql
-- 감사 테이블 접근 제어
-- 1) INSERT만 허용하는 role 생성
CREATE ROLE audit_append_only;
GRANT INSERT ON bypass_audit TO audit_append_only;
REVOKE UPDATE, DELETE ON bypass_audit FROM audit_append_only;

-- 2) 트리거: UPDATE/DELETE 시도 시 자동 거부
CREATE TRIGGER prevent_audit_modification
BEFORE UPDATE OR DELETE ON bypass_audit
FOR EACH ROW
BEGIN
  RAISE EXCEPTION 'Audit logs are append-only and cannot be modified';
END;

-- 3) 감사 테이블 백업 (write-once storage에 동기화)
-- (예: S3 Object Lock, 변조 불가능한 스토리지)
```

#### 학습
- 감사 무결성은 "기술"이 아닌 "조직 정책"의 문제
  - INSERT-Only 제약을 데이터베이스 레벨에서 강제
  - 모니터링 dashboard에서 체인 무결성을 주기적 검증
- 위반 감지 시 "조사" 단계를 거치지 말고 즉시 위험 상태로 전이
- Append-only 테이블을 외부 write-once 스토리지(S3, GCS)와 동기화
