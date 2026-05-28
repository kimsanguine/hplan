# Domain Context — Unified PRD 15-section

## PRD = 단일 진입점

본 PRD skill은 **단일 통합 양식**. customer-facing SaaS + 내부 LLM 에이전트 spec을 분리 없이 15-section으로 통합.

- 분리하지 않는 이유: 2026년 모든 SaaS는 LLM 에이전트 포함. 두 PRD 분리는 인위적
- 통합의 본질: 상단 (1-6) = 사람 / 중단 (7-11) = 에이전트·실행 / 하단 (12-14) = 지표·가설·실패 / 부록 (15) = QA Pool
- PM은 PRD 1개를 가지고 매 주 갱신

## 1인 빌더 60일 사이클

본 PRD는 1인 빌더 60일 사이클에 최적화.

- Day 1~14: Discovery + PRD v0.1 (Section 1-6 상세, 7-11 간단)
- Day 15~30: MVP Wave 1 빌드 (Section 7-11 상세화)
- Day 31~45: 5명 인터뷰 + PRD v0.2 (Section 12-14 추가)
- Day 46~60: Live URL + 첫 매출 (PRD v0.3 — 15개 섹션 모두 작성)
- Day 61~90: 5명 사랑 검증 (Sean Ellis 40% — Section 13 가설 결과 갱신)

## 도메인별 적용

### 법률 (1인 변호사)
- 핵심 가설: 한국어 판례 정확도 ≥ 0.88
- HITL: L3 default (변호사 책임)
- Anti-Goal: Hallucination 0건

### 교육 (1인 강사)
- 핵심 가설: 콘텐츠 도메인 충실성 ≥ 0.85
- HITL: L2 default
- Anti-Goal: 잘못된 학습 정보 X

### 의료 (가정의·치과)
- 핵심 가설: 도메인 충실성 ≥ 0.9
- HITL: L3 default
- Anti-Goal: 의학적 진단 대체 X

## 관련 1차 출처
- Marty Cagan, *INSPIRED* (2017): Discovery vs Delivery 분리
- Bob Moesta, *Demand-Side Sales* (2020): Switch Interview 4 Forces
- Sean Ellis, *Hacking Growth* (2017): 40% PMF Rule
- Andreessen, "The Only Thing That Matters" (Pmarchive 2007)

## 마이그레이션 (v0.6 → v0.7)

v0.6 이전: Agent PRD 7-section (Section 1=Overview / 2=Instruction / 3=Tools / 4=Memory / 5=Trigger / 6=Output / 7=Failure)

v0.7+ 통합: 위 7-section이 새 15-section의 어디에 매핑되는가
- v0.6 Section 1 (Overview) → v0.7 Section 1·3 (페르소나·문제)
- v0.6 Section 2 (Instruction) → v0.7 Section 7 (Role + Anti-Goals)
- v0.6 Section 3 (Tools) → v0.7 Section 8 (Tools)
- v0.6 Section 4 (Memory) → v0.7 Section 9 (Memory)
- v0.6 Section 5 (Trigger) → v0.7 Section 10 (Trigger)
- v0.6 Section 6 (Output) → v0.7 Section 11 (Output)
- v0.6 Section 7 (Failure + Success) → v0.7 Section 12 (Success) + 14 (Failure) 분리

기존 v0.6 PRD를 v0.7로 마이그레이션 시: Section 1·3·4·5·6 (사람·결정·범위·가설) 신규 추가 + 기존 내용을 위 매핑대로 재배치.
