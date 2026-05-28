# Unified PRD — 1인 변호사용 한국 판례 RAG SaaS (LLM Wiki Legal v0.1)

> 15-section 통합 PRD 예시. 1인 빌더 60일 사이클의 모범 PRD.
> 고객 향 SaaS (Section 1-6) + LLM 에이전트 사양 (Section 7-11) + 지표·가설·실패 (Section 12-14) + 부록 §15 QA Pool 통합.

---

## Section 1 — 사용자 / ICP / 페르소나

**ICP**: 한국 1-5인 변호사 사무소 (7년차 이상 변호사, 매출 정체 단계)

**페르소나**

### 페르소나 A. 박재훈 (45세, 9년차 형사 전문 단독 변호사)
- 하루: 9시 출근 → 의뢰인 미팅 2건 → 판례 검색 2~3시간 → 서면 작성 → 퇴근 9시
- 핵심 고통 (top 3):
  1. 판례 검색에 매일 2시간 — 한국어 판례명·인명·법조문이 정확히 매칭 안 됨
  2. 의뢰인에게 비슷한 사건 결과를 즉답 못 함
  3. 신규 판례·법령 변동 추적 시간 부족
- 현재 대안: 케이스노트·로앤B·구글 (각각 불완전)
- 도달 채널 (verified): 변호사회 카페 / 법무법인 단톡방 / 페이스북 변호사 그룹

### 페르소나 B. 김혜정 (38세, 5년차 가사 전문 사무소 대표)
- 하루: 의뢰인 상담 → 서면·소장 작성 → 가족법 판례 리서치 → 직원 1명 관리
- 핵심 고통: 가사 판례 비공개 사례 많아 검색 어려움 / 의뢰인 메시지 응답 시간 부족
- 현재 대안: 동료 변호사 단톡방 질문

---

## Section 2 — JTBD (Jobs To Be Done)

### Job-1: 변호사가 의뢰인 미팅 직전, 유사 사건 결과를 5분 안에 정리하고 싶다 → 미팅에서 즉답 + 의뢰인 신뢰
- Push: 케이스노트 검색이 한국어 판례명을 매번 틀림. 30분~2시간 소요
- Pull: 자연어 "유사 사건 결과 알려줘" 한 줄로 정리됨
- Anxiety: 새 도구가 정확한가? 잘못된 정보로 의뢰인 말하면 위험
- Habit: 케이스노트 검색이 익숙. 이동 비용 큼

### Job-2: 매일 아침 신규 판례·법령 변동을 5분에 파악하고 싶다 → 의뢰인 응대에 즉시 활용
- Push: 법령정보센터·대법원 사이트 매일 직접 확인 시간 없음
- Pull: 매일 아침 "내 도메인 영역" 변동만 요약 메일
- Anxiety: 중요 판례 놓치면 책임 문제
- Habit: 안 보고 지나가는 경우 많음

---

## Section 3 — 핵심 문제 + 해결할 가치

**문제 (절실히 이해)**
1. 한국 1-5인 변호사는 매일 판례 검색 2시간 — 검색 도구의 한국어 정확도 한계. 매일 ₩200K 시간 손실
2. 의뢰인 미팅 시 유사 사건 즉답 불가 → 신뢰도 저하 → 수임률 감소

**해결 방식 (워크플로우)**
- 자연어로 의뢰인 사건 요약 입력 → 한국어 판례명·인명·법조문 정확 매칭 → 유사 사건 5개 + 판결 결과 + 변호 전략 5분 안에 정리
- 매일 아침 본인 도메인 신규 변동 5분 요약 메일

**10배 가치 (정량)**
- 시간: 검색 2시간 → 30분 (4배). 월 40시간 절감 = ₩4M 가치 (시간당 ₩100K)
- 새로 가능: 의뢰인 미팅 유사 사건 즉답 → 수임률 30%↑ 예상

---

## Section 4 — 결정 옵션 매트릭스

| 결정 항목 | 옵션 A | 옵션 B | 옵션 C | 선택 | 트레이드오프 | 재검토 |
|---------|--------|--------|--------|------|-------------|------|
| RAG 인프라 | Supabase pgvector | ChromaDB | Pinecone | A | Cloud 한 스택 vs 로컬 자유도 | 100명 |
| 결제 | Paddle MoR | Stripe | Lemon Squeezy | A | 사업자 등록 vs 직접 통합 | 1,000명 |
| Orchestration | Sequential | Parallel | Router | A | 디버깅 vs 속도 | Wave 2 |
| HITL 레벨 | L2 (suggest) | L3 (approve) | L4 (autonomous) | L3 | 안전성 vs 속도 | 5명 사랑 후 |
| 임베딩 모델 | OpenAI 3-small | OpenAI 3-large | 한국어 특화 | A | 비용 vs 한국어 정확도 | 충실성 측정 후 |

---

## Section 5 — 제외사항 (Out-of-Scope)

1. ❌ 변호사 외 일반인 소비자 — 신뢰성 책임 부담 큼
2. ❌ 자동 서면 작성 (생성 X, 검색·정리만) — 변호사 법적 책임 회피
3. ❌ 의뢰인 직접 응대 챗봇 — 변협 규정·hallucination 위험
4. ❌ 다국어 (영어·중국어) — 한국어 정확도 우선 (beachhead 좁히기)
5. ❌ 무료 plan — 1년+ 운영 비용 회수 안 됨
6. ❌ 모바일 앱 (웹만) — 60일 MVP에 모바일 추가 비용 큼

**재검토 신호**: 사용자 100명 도달 시 모바일·다국어 재검토

---

## Section 6 — MVP 범위 / Full vision

### Now (Wave 1, Day 1~60) — 5명 사랑 도달
- 핵심 기능 5개:
  1. 한국어 자연어 판례 검색
  2. 유사 사건 top 5 정리 + 판결 결과
  3. 매일 아침 도메인 변동 요약 메일
  4. 의뢰인 사건 별 검색 history
  5. PDF export
- cogs p50: $8 / 사용자 / 월
- cogs p90: $15 / 사용자 / 월
- Live URL: Day 60

### Next (Wave 2, Day 61~120) — 5명 → 30명
- 변호 전략 추천 / 의뢰인 사건 일지 자동화 / Notion·Slack 연동
- cogs p50: $10 / 사용자 / 월

### Later (Wave 3, Day 121+) — 30명 → 100명+
- 변호사 단톡방 RPA / 사무소 직원 협업 / 한국어 OCR
- cogs p50: $12 / 사용자 / 월

---

## Section 7 — Role + Primary Goal + Anti-Goals

**Role**: 1인 변호사를 위한 한국 판례 RAG agent — 정확한 한국어 판례명 매칭으로 유사 사건 검색·정리

**Primary Goal**: 자연어 입력 → 유사 사건 top 5 + 판결 결과 + 출처 URL 30초 안에 제공

**Secondary Goals**:
1. 매일 아침 도메인 변동 요약 메일 자동 발송
2. 변호사별 검색 history 누적 → 패턴 발견

**Anti-Goals (하면 안 되는 것)**:
1. 판례에 없는 내용 생성 금지 (hallucination)
2. 변호사 법적 판단 대체 금지 — 검색·정리만
3. 한국어 판례명·법조문 번역 금지 — 원문 그대로
4. 의뢰인 개인정보 외부 전송 금지

---

## Section 8 — Tools & Integrations

| 도구/API | 용도 | 사용 조건 | 호출 제한 |
|---------|------|---------|---------|
| OpenAI text-embedding-3-small | 한국어 판례 임베딩 | 새 판례 ingest | 1회/판례 |
| Supabase pgvector | 유사도 검색 | 사용자 쿼리 | 무제한 |
| Claude Sonnet | 사건 요약 생성 | 검색 결과 정리 | 1회/쿼리 |
| 법령정보센터 API | 신규 판례·법령 수집 | 매일 새벽 6시 | 1회/일 |
| Paddle API | 구독·결제 | 가입·해지 | 이벤트 기반 |
| Channel Talk API | CS 응대 | 사용자 메시지 | 1회/메시지 |

---

## Section 9 — Memory & Context Design

```
Working Memory:
- 항상 로드: 시스템 프롬프트 (변호사 윤리·hallucination 금지) + 사용자 도메인 (형사·가사·민사 등)
- 조건부 로드: 관련 판례 top-5 (RAG 검색 후 inject)
- 컨텍스트 예산: 최대 10K tokens

Long-term Memory:
- Supabase: 사용자별 검색 history, 즐겨찾기 판례, 의뢰인별 사건 일지
- 매일 ingest: 신규 판례 / 법령 변동

Procedural Memory:
- skills/legal-citation.md (한국 판례 인용 표준)
- skills/case-similarity.md (유사 사건 매칭 룰)
- skills/lawyer-ethics.md (변호사 윤리 — Anti-Goals 강제)
```

---

## Section 10 — Trigger & Execution Flow

**트리거 유형**:
- ✅ Manual — 사용자가 자연어 쿼리 입력
- ✅ Cron — 매일 새벽 6시 신규 판례·법령 ingest, 매일 아침 7시 사용자별 요약 메일 발송
- ❌ Event-Driven — 사용 X
- ❌ Pipeline — 사용 X

**실행 흐름 (검색 쿼리)**:
- Step 1: 사용자 자연어 쿼리 입력 → 의도 파싱 (검색 / 요약 / 비교)
- Step 2: Supabase pgvector로 top 20 후보 추출
- Step 3: Claude Sonnet으로 의뢰인 사건 vs 후보 판례 적합도 재정렬 → top 5
- Step 4: top 5에 대한 판결 결과·인용 위치·출처 URL 정리
- Step 5: 응답 렌더링 + 검색 history 저장

**예상 실행 시간**: 5-15초
**타임아웃**: 30초

---

## Section 11 — Output Specification

**출력 채널**: Web UI (메인) + 매일 아침 이메일 (Cron)
**출력 형식**: Markdown 카드 (Web) / HTML 이메일 (Cron)
**출력 길이**: 검색 응답 최대 2000자 / 일일 요약 최대 1000자
**언어**: 한국어
**톤**: 변호사 전문 (격식·정확·간결)

**출력 예시 (검색 응답)**:
```markdown
## 유사 사건 Top 5 (사용자 쿼리: "30대 직원의 임금체불 + 사용자 폐업 직전")

### 1. 대법원 2023다12345 (2023.4.15)
- **결과**: 임금체불 인정. 사용자 폐업 의도 입증되어 임금 우선변제권 행사 가능.
- **핵심 인용 부분**: "사용자의 폐업 의사가 객관적으로 입증된 시점부터..."
- **출처**: [원문 보기](https://www.law.go.kr/판례/...)
- **유사도**: 92%

### 2~5. ...

### 변호 전략 제안
1. 사용자의 폐업 의사 객관 입증 자료 우선 확보 (대법원 2023다12345 참조)
2. 임금 우선변제권 행사 신청 (근로기준법 38조)
3. ...
```

---

## Section 12 — 성공 지표 통합 (Dual-axis)

**North Star Metric**: 변호사 1인당 주당 검색 횟수 (D7 리텐션의 leading indicator)

**Business KRs**:
1. MRR — Day 60에 ₩2M, Day 120에 ₩10M
2. 리텐션 D7 ≥ 60% / D30 ≥ 40%
3. Sean Ellis 40% — "더 이상 못 쓰면 매우 실망" 응답 비율
4. NPS ≥ 50
5. 사용자 수 — Day 60에 5명, Day 120에 30명

**Operational KRs (mandatory cost KR)**:
1. TTV (가입 → 첫 검색) ≤ 3분
2. 도메인 충실성 (한국어 판례 정확도) ≥ 0.88 (KDT M12 법률 임계값)
3. 검색 응답 시간 p95 ≤ 5초
4. 월 cogs / 사용자 ≤ $10
5. Hallucination 신고율 ≤ 0.5%

**Anti-Metric**: 평균 세션 시간 > 30분 (사용자가 길을 잃은 신호)

---

## Section 13 — 검증 가능 가설 박스

### 가설 H-1 (Value)
- 가설: 변호사가 매일 2시간 판례 검색 시간 → 본 제품으로 30분으로 단축. 월 ₩4M 가치 인식 → ₩50K/월 결제 의향
- 측정: 5명 인터뷰에서 결제 의향 응답
- 임계값: 4/5 이상이 "₩50K/월에 결제하겠다" 응답
- 2-day experiment: 5명에게 prototype 1주 사용 + 결제 의향 인터뷰
- 결과: 진행 중

### 가설 H-2 (Feasibility)
- 가설: OpenAI text-embedding-3-small + pgvector로 한국 판례 충실성 ≥ 0.85 달성
- 측정: Eval suite — 100개 판례 검색 케이스에서 정확도
- 임계값: ≥ 0.85
- 2-day experiment: 100개 판례 ingest + 50개 검색 쿼리 평가
- 결과: 진행 중

### 가설 H-3 (Reliability)
- 가설: 변호사 5명 모두 hallucination 0건 in 1주
- 측정: 사용자 신고 + 자동 hallucination detector
- 임계값: 0건 / 1주
- 2-day experiment: 5명 1주 사용 + 매일 admin audit
- 결과: 진행 중

---

## Section 14 — 실패 모드 + Human-in-the-loop

| 시나리오 | 감지 | 대응 | 사용자 영향 |
|---------|------|-----|------------|
| 도메인 충실성 < 0.7 | Eval suite | Fallback to "본 판례 검색 불완전합니다. 원문 확인 권장" + admin 알림 | 낮음 |
| 한국어 판례명 잘못 인식 | 사용자 신고 (모달 in-app) | 즉시 admin 알림 + roll back + 사용자 환불 옵션 | 높음 |
| OpenAI API 실패 | HTTPError | 3회 재시도 → 캐시된 결과 반환 + 갱신 시간 안내 | 중간 |
| Paddle 결제 실패 | HTTPError | Retry → 실패 시 사용자 안내 + 7일 유예 | 중간 |
| 데이터 유출 의심 | 비정상 access 패턴 | 즉시 차단 + 사용자 알림 + audit log + 변호사회 알림 | Critical |
| 변협 규정 위반 risk | 규정 변경 자동 감지 | 즉시 admin 알림 + 해당 기능 일시 중단 | Critical |

**Human-in-the-loop 트리거**:
- 도메인 충실성 < 0.7 → 사용자에게 "원문 확인 권장" 메시지 강제
- Hallucination 신고 1건 → admin 즉시 alert
- 변호사 법적 판단 영역 → 항상 "이는 검색·정리이며 법적 판단 아님" 워터마크
- 결제 분쟁 → admin escalation

---

## TK 인용 (operate/pm-engine 자동)

- **TK-041**: 긴급 트리거 규칙 — 변호사 책임 영역 hallucination = Critical
- **TK-018**: 1인 빌더 60일 사이클 — Day 30 MVP / Day 60 Live URL / Day 90 5명 사랑
- **TK-027**: KDT M12 법률 충실성 임계값 0.88 적용
- **TK-005**: Mata v. Avianca 사례 — 변호사 hallucination 책임 명시
- **TK-052**: Build in Public 마케팅 — LinkedIn·X 매주 시리얼 (Maor Shlomo 패턴)
