# Troubleshooting — Unified PRD 15-section 작성 FAQ

## Q: 15 섹션이 너무 많다. 줄일 수 없나?

A: 모든 섹션이 필요. 다만 적용 강도가 다름.
- 1인 빌더 v0.1: Section 1·2·3·6은 상세, 나머지 간단
- 5명 사랑 직전 v0.3: 모든 섹션 상세
- 외부 전달용 v1.0: 15개 모두 + TK 인용

## Q: 일반 SaaS (LLM 에이전트 없음)이면 Section 7-11을 어떻게 채우나?

A: "N/A — 일반 SaaS. AI 기능 없음"으로 간단 표기. PRD가 15-section을 모두 가지되 적용 안 되는 섹션은 명시. 미래에 AI 기능 추가 시 이 섹션이 빈 자리로 남아 작성 가능.

## Q: ICP가 너무 좁아서 시장이 작다고 느껴진다

A: beachhead 전략. 1-5인 변호사 사무소만 잡아도 4만명 변호사 × 30%(1인 사무소) = 12,000명 / 월 ₩50K → 잠재 ₩7.2B/년. 좁히는 게 정답. 100명 도달 후 인접 시장 확장.

## Q: JTBD vs User Story 차이

A: User Story는 "사용자로서 X를 하고 싶다 → Y를 위해". JTBD는 "[상황]에서 [목표] 달성. Push·Pull·Anxiety·Habit". User Story는 솔루션 가까이, JTBD는 상황·동기 가까이. 본 PRD는 JTBD 강제 — 솔루션 어조 회피.

## Q: 결정 옵션 매트릭스가 너무 많아진다

A: 5~10개 핵심 결정만. RAG 인프라·결제·Orchestration·HITL·임베딩·데이터 마이그레이션·인증·CS 채널·도메인 데이터·hallucination 정책. 그 외는 SPEC.md 결정 이력으로.

## Q: 제외사항이 5개가 안 나온다

A: 다음 카테고리에서 1개씩 찾아라.
- 사용자 확장 (다른 페르소나 안 함)
- 기능 확장 (생성·자동화·다국어 안 함)
- 채널 확장 (모바일·데스크탑 앱 안 함)
- 가격 정책 (무료·평생 라이센스 안 함)
- 통합 (특정 외부 시스템 안 함)
- 비즈니스 모델 (광고·data sale 안 함)

## Q: Now 기능이 5개 넘는다

A: 5명 사랑 도달에 진짜 필요한 것만. "있으면 좋다"는 Next로. 5명에게 1주일 줘서 "이것 없이는 못 쓴다" 응답 받은 것만 Now.

## Q: cogs p50/p90가 추측 같다

A: `discover/cost-sim` skill 호출하면 lognormal 분포로 자동 계산. 입력: 예상 사용자당 monthly API calls + 평균 token/call + 모델별 가격. p50은 중앙값, p90은 worst case.

## Q: Anti-Goals를 어떻게 명확히 쓸까?

A: 3개 카테고리에서 1개씩.
- 도메인 룰 (예: 변호사 책임 영역 hallucination 금지)
- 데이터 정책 (예: 사용자 데이터 외부 전송 금지)
- 법적 책임 (예: 의료 진단·법적 판단 대체 금지)

## Q: OKR Operational에 cost KR을 왜 mandatory?

A: 1인 빌더는 cogs 폭주 시 즉시 망함. cost KR 없으면 사용자 100명에 ₩10M/월 cogs 날 수 있음. mandatory.

## Q: HITL 레벨 결정이 어렵다

A: 도메인별 표.
- L1 (suggest read-only): 검색 결과 보기만
- L2 (suggest action): AI가 제안, 사용자가 클릭
- L3 (approve before): 사용자 승인 후 실행 — 법률·의료·결제 default
- L4 (notify after): 실행 후 알림 — 일반 SaaS
- L5 (autonomous): 알림도 없이 자동 — 단순 자동화만

## Q: Section 7-11이 deliver/instruction과 중복 아닌가?

A: Section 7-11은 PRD 본문 내 요약. 상세 spec이 더 필요하면 `deliver/instruction` [예정]으로 라우팅. 두 산출물이 같은 PRD 내에 inline될 수 있음 (큰 SaaS 의 핵심 에이전트).
