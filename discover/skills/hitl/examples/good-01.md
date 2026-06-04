# Good Example — hitl

## 사용자 요청
"계약서 검토 에이전트를 만드는데, 어디까지 자동으로 하고 어디서 사람이 개입해야 할지 경계를 설계해줘. 법적 리스크가 있어서 완전 자동은 안 돼."

## 승인 이유
- 에이전트가 법적 영향이 있는 중요한 작업 수행 (고오류 영향도)
- "완전 자동화 불가"라는 명확한 인식
- 인간 개입 지점과 자동화 레벨을 설계해야 할 구체적 필요

## 예상 처리
1. 작업 목록 작성 (계약서 수신, 검토, 의견 생성, 발송)
2. 각 작업의 가역성/오류 영향도 평가
3. 2축 매트릭스로 자동화 레벨(1~5) 결정
4. 각 작업에 HITL 패턴 매칭 (Approval Gate, Threshold, Audit 등)
5. 구체적 개입 트리거 정의 (신뢰도 임계값, 에러 카운트 등)
6. Shadow Mode 계획 (기간, 전환 기준)
7. 다음 단계 (agent-setup에 HITL 설계 반영)

---

## Linear Quality Gate HITL Good Example

### 배경: Task 생성 에이전트의 Quality Gate 설계

**에이전트:** Linear Task Creator
**목표:** PM의 요청 사항을 자동으로 Task로 변환 (제목, 설명, 담당자, 우선순위)
**도전:** 법적/규제 리스크 낮음, 하지만 팀의 Task 구조가 명확해야 함 (형식 오류 방지)

### 타임라인: 전체 HITL 플로우

#### Phase 1: Preflight 검증 (10:15 AM)

```
PM 요청: "Security audit 고객 계약서 검토 완료했으니,
         Linear에 Task 만들어 줄 수 있어?
         제목: '[계약서] acme-corp.pdf 검토',
         담당자: @legal-team,
         우선순위: High"

에이전트 분석:
  ├─ payload_schema_valid → 제목/담당자/우선순위 모두 명시됨 ✓
  ├─ scope_target_valid → @legal-team이 유효한 팀인가? ✓
  └─ private_access_valid → 에이전트가 legal-team private 팀에 접근 가능? ❌ (권한 없음)

결과: BLOCK — "에이전트가 Private Team legal-team에 접근할 수 없습니다."
```

#### Phase 2: HITL Gate 개입 (10:20 AM)

```
시스템 알림: "Task 생성 요청이 차단됨 (Tier B - High importance)"

승인자 선택:
  • Requester: PM
  • Approver: Team Lead (독립적 검증자 원칙)
  • SLA: 48시간

승인 게이트 요청 자동 생성:
  ├─ 요청 ID: TG-2024-03-07-001
  ├─ 요청 내용:
  │  ├─ Task 제목: "[계약서] acme-corp.pdf 검토"
  │  ├─ 담당자: @legal-team
  │  ├─ 우선순위: High
  │  └─ 차단 사유: "에이전트 private team 접근 권한 부재"
  └─ 승인 선택지:
      ├─ ALLOW: 에이전트에 임시 권한 부여 (TTL: 1시간)
      ├─ BLOCK: Task 생성 거절 (사유 기록)
      └─ MODIFY: 요청 수정 후 재제출 (예: 담당자 변경)

Team Lead의 검토:
  "아, legal-team이 private 팀인데 에이전트가 아직 권한이 없었네.
   이 Task는 law firm과의 계약서 검토고, legal-team만 접근 가능한 게 맞다.
   에이전트에 1시간만 권한 주고 Task 생성 허용하자."

액션: ALLOW (with TTL: 1시간)
```

#### Phase 3: Task 생성 실행 (10:25 AM)

```
시스템 액션:
  ├─ 에이전트에 legal-team 접근 권한 임시 부여 (TTL: 10:25 + 1시간 = 11:25)
  ├─ Task 생성 승인 → 에이전트가 Linear API 호출
  ├─ Linear에 Task 생성됨:
  │  ├─ 제목: "[계약서] acme-corp.pdf 검토"
  │  ├─ 팀: legal-team
  │  ├─ 담당자: @legal-team
  │  ├─ 우선순위: High
  │  └─ 설명: "[HITL 승인] Team Lead 승인으로 생성됨"
  └─ 감시추적 (audit log) 기록:
      - 시각: 10:25 AM
      - 요청자: PM
      - 승인자: Team Lead
      - 승인 사유: "Legal team contract review, temporary permission"
      - 권한 TTL: 1시간
```

#### Phase 4: TTL 만료 및 Remediation (11:30 AM)

```
시스템 자동 처리:
  ├─ 11:25 AM: 에이전트 legal-team 접근 권한 자동 철회
  ├─ 기록: "Temporary permission revoked after TTL expiry"
  └─ Remediation 체크:
      • 방금 만료된 1시간 동안 에이전트가 다른 작업 시도? → 없음 ✓
      • Task 생성됨? → 예, 1개 (감시추적에 남음) ✓
      • 권한 남용 징후? → 없음 ✓

결과: "정상 작동. HITL 게이트가 의도대로 작동함."
```

#### Phase 5: 사후 분석 및 TK 추출 (11:40 AM)

```
Team Lead의 사후 검토:
  "좋은 사례다. 우리가 했던 일:

  1️⃣ Preflight 검증으로 위험 조기 감지
     → 에이전트가 무작정 legal-team에 접근하지 않음

  2️⃣ HITL 게이트로 인간이 판단
     → 'Team Lead가 OK 한다' = 비즈니스 논리 확인

  3️⃣ 임시 권한 (TTL)으로 위험 제한
     → 1시간만 유효 → 자동 철회

  4️⃣ 감시추적(audit log)로 책임 기록
     → 누가 승인했고, 언제, 왜?

  TK 추출:
  - Private Team 권한은 절대 자동으로 부여하면 안 된다
  - 반드시 HITL로 거쳐야 한다
  - 권한을 부여해도, TTL로 제한한다
  - 모든 권한 부여/철회는 audit log에 기록된다
  "
```

---

### 이 Good Example이 보여주는 HITL 패턴

#### 1. Requester ≠ Approver

| 역할 | 담당자 | 역할 |
|---|---|---|
| **Requester** | PM | Task 생성 요청 제시 |
| **Approver** | Team Lead | "private team 권한 부여, 맞나?" 독립적 검증 |

✓ **왜 이게 중요?** PM이 자기가 승인하면, gate가 무의미함.

#### 2. Tier 기반 SLA

- **작업 유형:** Private Team 권한 변경 = Tier B (High)
- **SLA:** 48시간 (이 사례에서는 5분 내에 승인)
- **초과 시:** 자동 에스컬레이션 (예: VP/Chief로 이관)

✓ **왜 이게 중요?** 승인자가 바쁘면, "며칠 대기"하는 걸 방지.

#### 3. TTL을 통한 리스크 제한

- **권한 부여:** 1시간만 유효
- **자동 철회:** 11:25 자동으로 revoke
- **Remediation:** 만료 후 이상 사항 없는지 확인

✓ **왜 이게 중요?** "한 번 권한을 주면 영구적"이 아니라, "꼭 필요한 기간만".

#### 4. Audit Log (감시추적)

모든 액션 기록:
```
[APPROVED] TG-2024-03-07-001
  Requester: PM (@alice)
  Approver: Team Lead (@bob)
  Action: Grant legal-team access to agent
  Duration: 1h (10:25 AM - 11:25 AM)
  Resource: Linear Task
  Reason: Contract review automation
  Status: COMPLETED
```

✓ **왜 이게 중요?** 나중에 "누가 이 권한을 줬어?"라고 물어보면, 즉시 답변 가능.

---

### 핵심 교훈

**이 사례가 Good HITL Example인 이유:**

1. **Preflight로 조기 차단** → "에이전트가 무작정 private team 접근 안 함"
2. **HITL로 인간 판단 추가** → "Team Lead가 OK, 하지만 1시간만"
3. **TTL로 위험 시간 제한** → "영구가 아니라 1시간, 그 후 자동 철회"
4. **Audit로 책임 추적** → "누가 언제 뭘 승인했는지" 기록
5. **SLA로 프로세스 정체 방지** → "48시간 SLA, 초과 시 자동 에스컬레이션"

**다음 단계:**

이제 이 설계를 agent-setup에 반영:
- 에이전트가 "이건 private team 권한 필요해" 감지하면, 자동으로 HITL gate 요청
- Gate 승인 시 임시 권한(TTL) 자동 부여
- TTL 만료 시 자동 철회 + remediation 체크
- 모든 과정이 audit log에 기록
