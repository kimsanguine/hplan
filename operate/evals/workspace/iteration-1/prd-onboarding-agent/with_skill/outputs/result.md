# Agent PRD — 신규 입사자 온보딩 가이드 에이전트

---

## Section 1 — Overview

```
에이전트 이름: Onboard Guide Agent (OGA)
버전: 0.1
작성일: 2026-03-06
작성자: —
상태: Draft

한 줄 정의:
[신규 입사자]를 위해 [입사 첫 주 정보 안내·FAQ 응답·문서 탐색]을
[Slack 채널 내 대화형 인터페이스로] 자동 처리하는 에이전트

배경 / 만드는 이유:
신규 입사자는 첫 주에 반복적이고 유사한 질문(복지, 툴 설정, 조직도,
휴가 정책 등)을 HR·팀 리더에게 쏟아낸다. OGA는 이 반복 질문의 80%를
자동 해소해 HR 부담을 줄이고, 입사자가 24/7 즉시 답을 얻게 한다.
```

---

## Section 2 — Instruction Design

```
Role:
당신은 신규 입사자의 첫 주를 돕는 온보딩 길잡이입니다.
회사 규정·복지·툴 설정·조직 구조에 관한 질문에 친절하고 정확하게
답하며, 필요한 문서를 찾아 직접 링크로 제공합니다.

Primary Goal:
입사자가 첫 주 안에 "누구한테 물어봐야 하지?"라는 막막함 없이
스스로 문제를 해결하도록 돕는다.

Secondary Goals:
1. 반복 질문을 FAQ로 학습·누적해 답변 품질을 점진적으로 개선한다.
2. 자동 해소 불가 질문을 HR 담당자에게 에스컬레이션한다.

Anti-Goals (하면 안 되는 것):
1. 급여·성과 평가·개인 인사 정보 등 기밀 HR 데이터를 직접 조회·노출하지 않는다.
2. "잘 모르겠으니 알아서 찾아보세요"처럼 책임을 회피하는 답변을 하지 않는다.
3. 공식 문서에 없는 내용을 추측으로 답하지 않는다 — 불확실하면 담당자를 연결한다.
4. 입사자 대화 내용을 관리자에게 무단으로 전달하지 않는다.
```

---

## Section 3 — Tools & Integrations

| 도구/API | 용도 | 사용 조건 | 호출 제한 |
|---|---|---|---|
| `slack_read_message` | 입사자 질문 수신 | 멘션 또는 DM 수신 시 | 트리거당 1회 |
| `slack_post_message` | 답변 전송 | 매 응답 | 1회/턴 |
| `slack_post_ephemeral` | 민감 안내 (본인만 보임) | 개인정보 관련 답변 | 상황별 |
| `document_search` | 사내 Wiki·Drive·Notion 검색 | 문서 참조 필요 시 | 최대 3회/질문 |
| `faq_read` | FAQ 데이터베이스 조회 | 질문 분류 후 최우선 시도 | 1회/질문 |
| `faq_write` | 새 Q&A 누적 저장 | HR 승인 후 | 조건부 |
| `escalate_to_hr` | HR 담당자 DM 전달 | 자동 해소 불가 판정 시 | 1회/질문 |
| `user_profile_read` | 입사자 부서·직책 확인 | 맞춤 안내 시 | 1회/세션 |

**최소 권한 원칙**: 급여·평가·계약 관련 DB 접근 없음. 문서 검색은 Read-Only. FAQ 쓰기는 HR 확인 플래그 후 저장.

---

## Section 4 — Memory Strategy

```
Working Memory (컨텍스트):
- 항상 로드:
  · faq_database.json (핵심 FAQ 100건 이내)
  · onboarding_checklist.md (입사 첫 주 체크리스트)
  · hr_escalation_contacts.json (에스컬레이션 담당자 목록)
- 조건부 로드:
  · dept_{dept_name}_guide.md — 입사자 부서 확인 후 로드
  · tool_setup_{tool_name}.md — 툴 설정 질문 감지 시 로드
- 컨텍스트 예산: ~6,000 토큰 (FAQ + 체크리스트 + 부서 가이드)

Long-term Memory (파일):
- 읽기: faq_database.json에서 매칭 Q&A 조회
- 쓰기:
  · unresolved_log.json — 자동 해소 실패 질문 누적 (학습용)
  · faq_database.json — HR 승인 후 신규 Q&A 추가
- 저장 트리거:
  · 에스컬레이션 발생 시 → unresolved_log에 즉시 기록
  · HR이 답변 검토 완료 시 → faq_database 업데이트

Procedural Memory (Skills):
- agent-instruction-design (역할·Anti-Goal 설계)
- agent-kpi (성공 지표 정의)
- failure-mode-analysis (에스컬레이션 판단 로직)
```

---

## Section 5 — Trigger & Execution

```
트리거 유형:
☑ Event-Driven — 이벤트: Slack 멘션(@onboard-guide) 또는 DM 수신

실행 흐름:
Step 1: [질문 수신]
  - Slack webhook → 메시지 파싱
  - user_profile_read로 입사자 부서·직책 확인

Step 2: [의도 분류]
  - 카테고리 분류:
    · FAQ (복지/규정/휴가/급여일 등)
    · 문서 탐색 (특정 양식, 정책 파일)
    · 툴 설정 (Slack, Notion, GitHub, VPN 등)
    · 일정/조직 안내 (OT 일정, 팀원 소개)
    · 해소 불가 (기밀·개인정보·분쟁 관련)

Step 3: [답변 생성]
  - FAQ 매칭 시 → faq_database에서 즉시 응답
  - 문서 필요 시 → document_search (최대 3회) → 링크 포함 응답
  - 불확실 (신뢰도 < 0.75) → 에스컬레이션 판단

Step 4: [전달]
  - 일반 답변 → slack_post_message (스레드 유지)
  - 개인정보 관련 → slack_post_ephemeral
  - 해소 불가 → escalate_to_hr + 입사자에게 "담당자 연결 완료" 안내

Step 5: [학습 기록]
  - 미해소 질문 → unresolved_log.json 저장

예상 실행 시간: 5~15초
타임아웃 설정: 30초 (초과 시 "잠시 후 다시 시도" 안내)
```

---

## Section 6 — Output Specification

```
출력 채널: Slack (스레드 답변 기본, DM 에스컬레이션)
출력 형식: Markdown (Slack mrkdwn 호환)
출력 길이: 최대 500자 / 3개 항목 이내 (더 길면 문서 링크로 대체)
언어: 한국어 기본 (외국인 입사자 감지 시 영어 전환)
톤: 친근하고 간결 — "~해요" 체, 이모지 최소화 (1개 이내/메시지)
```

**출력 예시 1 — FAQ 즉답:**
```
안녕하세요! 연차 관련 질문이시군요 🙂

*연차 발생 기준*
• 입사 후 1년 미만: 매월 1일씩 최대 11일 발생
• 1년 이상: 15일 일괄 부여 (이후 2년마다 1일 추가)

*신청 방법*
→ [그룹웨어 휴가 신청 바로가기](링크)

추가 궁금한 점 있으시면 언제든지 물어보세요!
```

**출력 예시 2 — 에스컬레이션:**
```
말씀하신 내용은 제가 직접 안내드리기 어려운 부분이에요.
HR 담당자(@hr-contact)에게 전달했으니, 오늘 중으로 연락 드릴 예정입니다.
불편을 드려 죄송합니다!
```

---

## Section 7 — Failure Handling & Success Metrics

**실패 시나리오:**

| 시나리오 | 감지 방법 | 대응 행동 |
|---|---|---|
| FAQ 미매칭 | 유사도 점수 < 0.75 | document_search 시도 → 그래도 없으면 에스컬레이션 |
| 문서 검색 실패 | 검색 결과 0건 | "현재 문서에서 찾기 어려워요 — HR 연결" 안내 |
| Slack API 타임아웃 | 30초 초과 | 재시도 1회 → 실패 시 관리자 알림 채널 기록 |
| 기밀 질문 감지 | 급여·평가·계약 키워드 | ephemeral로 "HR 직접 문의" 안내, 대화 기록 안 함 |
| 컨텍스트 초과 | 토큰 85%+ | 핵심 FAQ만 유지, 나머지 문서 참조 링크로 대체 |
| 연속 에스컬레이션 | 동일 유저 3회 연속 | HR 담당자에게 "집중 지원 필요" 플래그 DM |

**Human-in-the-loop 트리거:**
- 자동 분류 신뢰도 < 0.75 → HR에 에스컬레이션
- 감정적 표현 감지 (혼란, 불만, 불안 키워드) → HR 담당자에게 즉시 알림
- 동일 질문 3회 반복 → 에이전트 한계 인정 + HR 연결

**성공 지표:**

| 지표 | 목표값 | 측정 방법 |
|---|---|---|
| FAQ 자동 해소율 | ≥ 80% | (에스컬레이션 없이 종료된 대화 / 전체 대화) |
| 평균 응답 레이턴시 | ≤ 10초 | Slack 수신 → 답변 전송 시간 |
| 입사자 만족도 | ≥ 4.0 / 5.0 | 첫 주 종료 시 Slack 설문 (5점 척도) |
| HR 에스컬레이션 감소율 | 기존 대비 60% 감소 | 월별 HR 수동 응답 건수 비교 |
| 월 운영 비용 | ≤ $20 | LLM API 토큰 + Slack API 비용 합산 |
| 서비스 가용성 | ≥ 99% | 평일 업무시간 기준 응답 성공률 |

---

## 다음 단계 (구현 우선순위)

```
MVP (2주):
  1. Slack Bot 등록 + webhook 연동
  2. FAQ 데이터베이스 초안 작성 (HR 협업 필요)
  3. 의도 분류 + FAQ 매칭 로직
  4. 에스컬레이션 플로우

Phase 2 (4주):
  5. document_search (Notion/Drive 연동)
  6. 부서별 맞춤 가이드 로드
  7. unresolved_log 기반 FAQ 자동 학습 루프

모델 선택: claude-haiku-4-5 (응답 속도 + 비용 최적화)
에스컬레이션은 claude-sonnet-4-6 (복잡한 의도 판단 시)
```

---

**검토 체크리스트**

- [x] Anti-Goals가 기밀 데이터·추측 답변·무단 전달을 구체적으로 차단
- [x] 실패 시나리오 5개 이상, 각각 감지·대응 명시
- [x] 성공 지표 모두 측정 가능한 수치로 정의
- [x] 최소 권한 원칙 적용 (급여·평가 DB 접근 없음)
- [x] Human-in-the-loop 트리거 3개 명시