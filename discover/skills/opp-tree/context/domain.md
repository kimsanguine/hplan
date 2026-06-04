# Domain Context — opp-tree

## 1) Domain Scope

Agent Opportunity Discovery — 조직의 반복 업무, 병목 지점, 자동화 기회를 체계적으로 탐색하고 우선순위를 정하는 도메인

**적용 범위:**
- 에이전트 도입을 고려 중인 조직/팀의 기회 탐색
- 여러 자동화 기회 중 최고 우선순위 찾기
- 빠르게 시작할 수 있는 에이전트 1개 선택
- 도메인별 기회 매핑 (CS, 마케팅, HR, 운영 등)

**제외 범위:**
- 이미 선택된 에이전트의 가정 검증 (assumptions 스킬)
- 특정 에이전트의 구현 방식 결정 (assumptions --mode build-or-buy)
- 제품 전체의 전략 기획 (별도 스킬)

---

## 2) Primary Users

- **PM / Product Manager**: 자동화 기회를 발굴하고 우선순위 정하기
- **Team Lead / Operations**: 팀의 반복 업무 분석 및 효율화 기회
- **Startup Founder**: 초기 에이전트 도입 시 어디서부터 시작할지 결정
- **Enterprise**: 여러 팀의 에이전트 기회 포트폴리오 구축

---

## 3) Required Inputs

- **자동화 대상**: 팀/부서 또는 구체적 업무 영역
  - 예: "CS팀", "마케팅 콘텐츠 제작", "재무 리포팅"
- **현재 프로세스 개요**: 어떤 업무를 수동으로 하고 있는가?
- **통증점**: 시간 낭비, 오류, 병목 지점이 뭔가?
- **비즈니스 맥락**: 이 부서의 우선순위, 예산, 인력 현황

---

## 4) Output Contract

**Step-by-Step Deliverables:**

1. **Automation Outcome** (1개, 측정 가능)
   - 현재: X시간/월
   - 목표: Y시간/월 (수치로 명시)
   - 예: "PM이 뉴스 수집에 쓰는 시간 주 8시간 → 0.5시간"

2. **Opportunities** (3~5개)
   - 각 기회마다 Opportunity Score 계산
     - 반복빈도(1~5) × 자동화가능성(1~5) × 판단의존도역수(5=저판단)
   - Score 상위 3개 선택
   - 제외된 기회의 이유 명시

3. **Agent Solutions** (기회당 2~3개)
   - 에이전트 유형 (Trigger/Pipeline/Research/Monitor/Orchestrator)
   - 각 후보의 트리거/도구/종료조건 명시
   - 구현 난이도 (Low/Medium/High)

4. **4축 Assumptions** (최우선 솔루션 1~2개)
   - Value / Feasibility / Reliability / Ethics
   - 각 축 최소 2~3개 가정

5. **Experiments** (2일 이내 가능)
   - 각 가정의 검증 방법 설계
   - 예: "API 테스트 10회", "수동 실행 5일 + 피드백"

6. **다음 권장 액션**
   - "가장 높은 Score + 가장 낮은 구현 난이도" 조합 추천
   - assumptions 스킬로 연결 또는 assumptions --mode build-or-buy 결정

---

## 5) Guardrails

**필수 체크사항:**

- ✓ Automation Outcome이 측정 가능한가?
  - "업무를 자동화한다" (X)
  - "PM이 뉴스 수집에 쓰는 시간 주 8시간 → 0.5시간으로" (O)

- ✓ Opportunities가 다양한가?
  - 모두 같은 카테고리 (정보 수집만) → 재발굴 필수
  - 정보수집 / 판단 / 물리작업 등 다층 포함 → 양호

- ✓ Opportunity Score가 합리적인가?
  - 점수가 모두 높음(20점 이상) → 팀의 낙관 바이어스 의심
  - 점수 분포가 5~20 범위 → 양호

- ✓ 판단 의존도가 높은 기회는 제외했는가?
  - Score 점수는 높지만 판단 의존도 4~5점 → 에이전트 부적합 (Rule-based or 인간이 나음)

---

## 6) Working Facts

**에이전트 기회 발굴의 일반적 특성:**

| 항목 | 특징 | 참고 |
|------|------|------|
| **평균 기회 수** | 팀당 5~10개 | 작은 팀: 3~5개 / 대규모 팀: 10~20개 |
| **상위 기회** | Score 상위 1~3개만 1차 구현 | 나머지는 백로그로 보류 |
| **판단 의존도** | 높으면 에이전트 부적합 | HITL 설계가 필요하거나, Rule-based 자동화로 전환 |
| **Value 축** | 가장 자주 무시됨 | "기술적으로 가능하니까" 하지만 실제로 아무도 안 쓸 수 있음 |
| **시작 기간** | 평균 2~4주 MVP | 검증 포함 시 1~3개월 |

**TO BE UPDATED by reviewer:**
- 우리 팀의 평균 반복빈도 (일간 vs 주간 vs 월간)
- 자동화가 실제로 가능한 업무의 특성 (도메인별)
- 에이전트 도입 후 실제 시간 절감 효과 (측정 데이터)

---

## 7) Fill-in Checklist

구현 팀이 opp-tree 스킬 실행 후 다음을 확인:

- [ ] Automation Outcome이 수치와 함께 측정 가능하게 정의되었는가?
- [ ] Opportunities가 3개 이상이고, 서로 다른 카테고리(정보/판단/작업)를 포괄하는가?
- [ ] 상위 3개 Opportunity의 점수 계산이 명확하고, 제외 이유가 명시되었는가?
- [ ] 각 Opportunity마다 2개 이상의 Agent Solutions 후보가 있고, 트리거/도구/종료조건이 정의되었는가?
- [ ] 최우선 솔루션의 Value/Feasibility/Reliability/Ethics 4축 가정이 명시되었는가?
- [ ] 검증 실험이 2일 이내에 가능한 수준으로 설계되었는가?
- [ ] 다음 단계 연결(assumptions 또는 assumptions --mode build-or-buy)이 명확한가?
