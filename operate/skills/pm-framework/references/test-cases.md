# Test Cases — pm-framework 스킬

## 1) Trigger Tests

### Should Trigger (5)

1. "우리가 비슷한 상황에서 반복적으로 같은 판단을 하는데, 이걸 패턴으로 구조화하고 싶다"
   - 이유: 반복 패턴 → TK 추출 및 구조화

2. "이 의사결정이 왜 나쁜 결과를 냈을까? 다시는 안 하려면 이것을 기록해야 한다"
   - 이유: Failure Pattern TK 추출

3. "새로운 기능을 만들 때마다 우리는 '프로토타입 먼저' 하는데, 이게 왜 효과적인지 설명하고 싶다"
   - 이유: Decision/Heuristic Pattern TK 추출

4. "에이전트의 암묵적 판단 기준을 명시적으로 만들어서 다른 에이전트에 반영하려면?"
   - 이유: TK 추출 → 구조화 → 에이전트 instruction으로 변환

5. "우리만의 도메인 지식(tacit knowledge)을 TK-NNN 형태로 정리해서 라이브러리 만들고 싶다"
   - 이유: PM 암묵지 → TK 구조화

### Should NOT Trigger (5)

1. "이 TK를 에이전트 Instruction에 어떻게 반영할까?"
   - 올바른 라우팅: pm-engine의 `/tk-to-instruction` 또는 deliver

2. "이 TK가 과거에도 나왔던 것 같은데, 패턴 라이브러리에서 찾자"
   - 올바른 라우팅: `pm-decision` (패턴 라이브러리 검색)

3. "새로운 의사결정 프로세스를 만들고 싶다"
   - 올바른 라우팅: deliver의 instruction 또는 okr 스킬

4. "이 판단이 데이터로 검증되었는지 확인하려면?"
   - 올바른 라우팅: discover의 `cost-sim`, `assumptions` (가정 검증)

5. "우리 팀의 가치관을 정의하고 싶다"
   - 올바른 라우팅: 기업 문화/가치관 정의 (pm-framework 범위 외)

## 2) Edge Cases

### 경계 사례 (5)

1. **TK 추출이 너무 일반적: 누구나 아는 것**
   - 입력: "우리는 우선순위가 높은 것부터 한다"
   - 예상 행동: "이건 TK가 아니라 상식" → 특수화 필요 지적
   - 근거: pm-framework의 "Failure Handling" — "추출한 TK가 너무 일반적"

2. **TK 중복: 이미 있는 것과 같은 내용**
   - 입력: "TK-003 긴급 요청 판단을 또 만들려고 함"
   - 예상 행동: 기존 TK와 병합 또는 더 정확한 버전으로 통합
   - 근거: Failure Handling의 "같은 내용의 TK를 중복으로 만들어버림"

3. **TK의 활성화 조건이 모호함**
   - 입력: "언제 이 TK를 사용할까?" → "음... 대부분의 경우?"
   - 예상 행동: Contextual Retrieval 패턴 미충족 → 활성화/비활성화 조건 명확화
   - 근거: pm-framework Step 4의 "CR 메타데이터" — 활성화 키워드와 CR Score 필수

4. **TK가 시간이 지나면서 틀렸다는 걸 깨달음**
   - 입력: "6개월 뒤, 시장 변화로 이 판단이 더 이상 유효하지 않다"
   - 예상 행동: TK 삭제 금지 → "활성화 조건"을 시간 범위로 축소, 또는 반대 패턴 TK 작성
   - 근거: Failure Handling의 "추출한 TK가 시간이 지나면서 틀렸다"

5. **TK 유형 분류 애매: Type 2 vs Type 4**
   - 입력: "우리는 '도구 탓하지 말고 먼저 프롬프트를 본다'는데, 이게 Decision Pattern인가 Anti-Pattern인가?"
   - 예상 행동: Step 3의 리트머스 테스트 3가지 질문으로 판단
   - 근거: pm-framework Step 3 — "Type 2 vs Type 4 리트머스 테스트"

