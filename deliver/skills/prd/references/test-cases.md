# Test Cases — Unified PRD Quality Gate (15 sections + 4 cross-cutting checks = 19 items)

## 자동 검증 (validate-prd.sh)

PRD 15-section + 4 cross-cutting check 모두 통과해야 release 허용 (총 19개 항목).

| # | 검증 | 통과 기준 |
|---|------|----------|
| 1 | ICP 명시 | beachhead 5-criteria 통과 (좁힘·도달가능·결제의향·확장가능·증거) |
| 2 | 페르소나 수 | 2~3개. 1개면 너무 좁음, 4개+면 beachhead 깨짐 |
| 3 | JTBD Job 수 | 1~3개. Switch 4 Forces 모두 채워짐 |
| 4 | 10배 가치 정량 | 시간·돈·새 가능성 중 1개 이상 수치 명시 |
| 5 | 결정 옵션 매트릭스 | 최소 2개 옵션 × 5개 결정 항목 = 10개 셀 채움 |
| 6 | 제외사항 수 | 5개 이상 |
| 7 | Now/Next/Later 분리 | 3-tier 모두 채움 + 각 tier에 cogs p50/p90 |
| 8 | Role + Anti-Goals | Anti-Goals 최소 3개. 도메인 룰·데이터 정책·법적 책임 포함 |
| 9 | Tools 호출 제한 | Section 8 모든 row에 "호출 제한" 명시 |
| 10 | 3-tier Memory | Working / Long-term / Procedural 모두 작성 |
| 11 | Trigger 명시 | Cron/Event/Manual/Pipeline 중 명시적 체크 |
| 12 | Output 예시 | 실제 출력 샘플 1개 이상 (Markdown / JSON / Plain text) |
| 13 | OKR 구성 | North Star 1 + Business KRs 3~5 + Operational KRs 3~5 (cost KR mandatory) + Anti-Metric 1 |
| 14 | 가설 박스 | Top-3 + 각각 2-day experiment 명시 |
| 15 | HITL 트리거 | Section 14에 최소 1개 + Critical 시나리오 명시 |
| 16 | 디자인 시그니처 | UI/UX 있으면 RESPECT.md commit, 없으면 "N/A" 명시 |
| 17 | §15 QA Pool | `harness/QA_POOL.json` 저장됨 + dev_roles 결정론 매핑 |
| 18 | 일관성 | 섹션 간 충돌·누락 없음 |
| 19 | TK 인용 | `operate/pm-engine`로 관련 TK-NNN 3~5개 인용 |

## 인터뷰 검증 (사람 검증)

5명 사랑 인터뷰 직전 PRD 검증:

- [ ] 페르소나 A를 인터뷰 대상자에게 보여줬을 때 "이거 나야"라고 응답
- [ ] JTBD Job-1을 읽고 본인 일상에서 100% 매칭
- [ ] 10배 가치 정량을 보고 "이만큼 절감되면 결제할 의향 있다"
- [ ] 제외사항을 보고 "그건 굳이 필요 없다"
- [ ] Wave 1 (Now) 기능 목록이 1주일 안에 쓸 만하다고 응답
- [ ] Output 예시를 보고 "이 정도면 신뢰할 만하다"고 응답

6/6 모두 통과해야 5명 사랑 인터뷰 진입 허용.

## 일반 SaaS vs LLM 에이전트 포함 SaaS 구분

Section 7-11 (에이전트·실행 사양)의 적용:

| 케이스 | 적용 |
|--------|------|
| **LLM 에이전트 포함 SaaS** (대부분) | Section 7-11 모두 상세 작성 |
| **일반 SaaS (LLM 없음, drag-and-drop tool 등)** | Section 7-11에 "N/A — 일반 SaaS. AI 기능 없음" 간단 표기 |
| **순수 내부용 LLM 에이전트** | Section 1·3의 페르소나 = 내부 사용자. Section 7-11 상세 작성. Section 2 JTBD = 내부 워크플로우 |
