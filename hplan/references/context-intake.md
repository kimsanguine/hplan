# hplan Context Intake
# /hplan 실행 전 이 파일을 채우세요.
# 목적: 게이트를 통과할 "자격이 있는 컨텍스트"를 사전에 구조화
# 소요 시간: 30–45분 (처음) / 15분 (재방문)
# 저장 위치: harness/context-intake.md (프로젝트별 작성)
#
# 이 파일이 있으면 /hplan이 자동으로 읽어 evidence rubric에 반영합니다.
# 빈 필드는 해당 rubric 축에서 자동 감점됩니다.

## 메타
idea: ""          # 한 문장 가설. "X를 위한 Y" 형식.
                  # 예: "반복 핸드오프가 많은 3인 이하 팀을 위한 자동 보고서 생성 도구"
submitted_at: ""  # YYYY-MM-DD

---

## Section 1 — ICP (Ideal Customer Profile)
# 규칙: 인구통계(나이·직종·국가) 금지. 반복 행동 + 상황으로 기술.
# ✅ Good: "지난 30일 내 5건 이상의 반복 핸드오프를 스프레드시트로 처리한 3인 이하 팀 운영자"
# ❌ Bad: "바쁜 20–30대 프리랜서"

icp_segment: ""        # 누가 이 문제를 반복적으로 겪는가 (행동 기술)
icp_situation: ""      # 언제·어떤 상황에서 이 문제가 발생하는가
icp_frequency: ""      # 얼마나 자주: weekly / monthly / per-project
icp_anti: ""           # 이 ICP에 포함되지 않는 사람 (명시적 anti-ICP)

---

## Section 2 — Recent Painful Event
# 규칙: 30일 이내 실제 발생 사건. "~할 것 같다"는 weak signal로 분류.
# ✅ Good: "이번 주 화요일, 동일 보고서를 고객사 3곳에 수동 포맷해서 전송 — 건당 45분"
# ❌ Bad: "보고서 작업이 항상 번거롭다"

recent_event: ""       # 언제 / 무슨 일 / 얼마나 걸렸나 (구체적 사건)
event_recency: ""      # within_7d / within_30d / within_90d / older

---

## Section 3 — Current Workaround
# 규칙: 지금 이 문제를 해결하기 위해 돈·시간을 쓰는 방법. "없다"면 demand 없는 것.
# ✅ Good: "Zapier + Airtable + 수동 복사-붙여넣기 3단계, 건당 45분"
# ❌ Bad: "그냥 참는다"

workaround_tool: ""    # 현재 사용 중인 도구 또는 방법
workaround_cost: ""    # 시간(분/건) 또는 금액(월/건)
workaround_pain: ""    # workaround의 가장 큰 불편함 (인터뷰에서 실제 발화)

---

## Section 4 — Economic Pain
# 규칙: 시간만으로는 부족. 돈·리스크·기회비용 중 하나 이상 포함.
# 계산 공식: time_per_instance × frequency_per_month × hourly_rate = monthly_cost

time_per_instance: ""     # 분 단위
frequency_per_month: ""   # 건/월
hourly_rate: ""           # 사용자 시간 단가 (추정 가능)
monthly_cost_estimate: "" # 위 공식 계산값 또는 추정 금액
revenue_risk: ""          # 이 문제가 매출·계약에 영향을 주는가? (Y/N + 설명)

---

## Section 5 — Alternatives & Competitors
# 규칙: hplan exclusions registry와 교차 검증됨. 알려진 대체재 모두 기입.
# 없으면 "없음"으로 명시 (빈칸 = 미조사로 처리)

alternatives:
  - name: ""
    why_inadequate: ""    # 왜 이 대체재로는 부족한가 (사용자 발화 인용 우선)
  - name: ""
    why_inadequate: ""

direct_competitors: ""    # 동일 워크플로우를 직접 해결하는 SaaS (없으면 "없음")

---

## Section 6 — Switching Trigger
# 규칙: "왜 지금인가?" JTBD switch interview의 핵심 질문.
# "sounds useful" 수준은 weak signal. 전환을 결정하게 만드는 사건/상황을 기술.
# ✅ Good: "다음 번에 같은 실수가 한 번 더 생기면 도구를 바꾸겠다고 했음"
# ❌ Bad: "더 편하면 써볼 것 같다"

switch_condition: ""      # 현재 대체재를 버리게 만들 조건 (사건/상황)
urgency_driver: ""        # 지금 당장 해결해야 하는 이유 (없으면 "없음" 명시)

---

## Section 7 — MVP Scope
# 규칙: 하나의 워크플로우, 3개 기능 이하.
# "플랫폼", "AI 기반 종합 솔루션", "~도 되고 ~도 되는" 표현 금지.

mvp_core_workflow: ""     # 해결할 단 하나의 워크플로우 (한 문장)
mvp_features:
  - ""                    # 기능 1 (최대 3개)
  - ""                    # 기능 2
  - ""                    # 기능 3
out_of_scope: ""          # 이번 MVP에 의도적으로 포함하지 않는 것

---

## Section 8 — Acquisition Path
# 규칙: 첫 10명 고객의 이름·채널을 구체적으로 명시.
# "SNS 마케팅", "콘텐츠 마케팅", "입소문"은 인정 안 함.
# ✅ Good: "현재 운영 중인 오픈채팅방 230명, 그 중 반복 핸드오프 언급한 12명에게 DM"
# ❌ Bad: "트위터 / 링크드인으로 홍보"

first_10_customers: ""    # 이름/채널/커뮤니티 구체적으로 (아는 사람이면 이름)
acquisition_channel: ""   # 첫 10명을 어떻게 연결할 것인가
time_to_first_5: ""       # 첫 5명 페이 유저까지 예상 소요 기간

---

## Section 9 — Interview Evidence
# 규칙: /hplan GO 결정에는 최소 2건의 인터뷰 인용 필요.
# AI 요약 금지 — 실제 발화 또는 행동 관찰 그대로 기입.
# 형식: "익명코드 | YYYY-MM-DD | 실제 발화 또는 관찰"

interview_notes: |
  # 예: "고객A | 2026-05-01 | 매주 화요일 오전 이 작업만 2시간 씀. 자동화되면 당장 쓰겠다고."
  # 예: "고객B | 2026-04-28 | Zapier 써봤는데 에러 너무 많아서 포기했다고."

interview_count: 0        # 실제 인터뷰 건수 (AI 대화 제외)
strong_push_count: 0      # 동일 push signal을 반복한 사람 수 (Torres 기준: 3+ = strong)
interview_artifact: ""    # 원본 증거 링크 1개 필수: Zoom 녹화·transcript·Dovetail 링크·노트 파일 경로
                          # 없으면 interview_count 점수 최대 12점 제한 (Dovetail artifact rule)
                          # ✅ Good: "https://dovetail.com/... " / "notes/2026-05-10-interview.md"
                          # ❌ Bad: 빈칸 (인터뷰 수는 높아도 artifact 없으면 신뢰도 상한 제한)
unique_insights: 0        # 인터뷰로 발견한 고유 인사이트 수 (건수와 별개)
                          # 밀도 = unique_insights / interview_count < 0.5이면 페널티 적용
                          # ✅ Good: 인터뷰 5건 → 인사이트 4개 (밀도 0.8)
                          # ❌ Bad: 인터뷰 10건 → 인사이트 2개 (밀도 0.2 — 형식적 인터뷰 의심)

---

## Self-Check (제출 전 필수 확인)
# 모두 체크되지 않으면 /hplan이 낮은 신뢰도 배지 또는 HOLD를 반환합니다.

- [ ] icp_segment가 행동으로 기술되었는가? (인구통계만이면 재작성)
- [ ] recent_event가 30일 이내 실제 사건인가?
- [ ] workaround_cost에 구체적인 시간 또는 금액이 있는가?
- [ ] economic pain에 돈 또는 리스크가 포함되었는가?
- [ ] mvp_features가 3개 이하인가?
- [ ] interview_notes에 실제 발화가 있는가? (AI 요약 금지)
- [ ] first_10_customers가 구체적인가? ("SNS"만이면 재작성)

---

## 다음 단계

이 파일 완성 후:
```bash
/hplan "idea"                            # 풀 게이트 (빠른 verdict)
/evidence-rubric context-intake.md       # 증거 게이트만 (100점 루브릭 전체)
```

context_dates를 checkpoint.json에 기록하는 예시:
```json
{
  "status": "pending",
  "context_dates": {
    "customer_interviews": "2026-05-10",
    "competitive_analysis": "2026-05-01",
    "provider_pricing": "2026-05-14",
    "market_size": "2026-03-01"
  }
}
```
