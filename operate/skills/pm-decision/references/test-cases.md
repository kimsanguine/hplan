# Test Cases — pm-decision 스킬

## 1) Trigger Tests

### Should Trigger (5)

1. "긴급하다고 요청이 들어왔는데 정말 긴급일까? 어떻게 판단할까?"
   - 이유: "Stakeholder Energy Management" 패턴 적용

2. "We have conflicting priorities from different teams. How should we decide what to build first?"
   - 이유: "Data-Before-Opinion" 및 "Scope Creep Prevention" 패턴 적용

3. "이 의사결정이 이전에 비슷한 상황에서 했던 것과 같은 방식인지 확인하고 싶다"
   - 이유: 패턴 라이브러리 검색 및 일관성 확인

4. "같은 실수를 반복하고 있는 것 같다. 이게 정말 같은 실수인가?"
   - 이유: 패턴 검증을 통한 반복 실수 방지

5. "새로운 의사결정 패턴을 발견했는데, 이걸 팀과 공유하려면?"
   - 이유: 신규 패턴 기록 및 TK 추출 준비

### Should NOT Trigger (5)

1. "이 패턴을 에이전트 Instruction에 어떻게 반영할까?"
   - 올바른 라우팅: `pm-framework`의 `/tk-to-instruction` 또는 pm-engine

2. "우리 팀의 의사결정 프로세스 자체를 만들려고 한다"
   - 올바른 라우팅: deliver의 instruction 또는 okr 스킬

3. "이 판단이 데이터로 맞는지 검증하고 싶다"
   - 올바른 라우팅: discover의 `cost-sim`, `assumptions` 스킬

4. "의사결정의 근거 자료를 수집해야 한다"
   - 올바른 라우팅: `pm-framework` (TK 추출 및 구조화)

5. "우리 기업 정책에 이 결정이 위배되는지 확인하려면?"
   - 올바른 라우팅: 정책/법률 검토 (pm-decision은 정책 상위)

## 2) Edge Cases

### 경계 사례 (5)

1. **패턴이 현재 맥락과 불일치**
   - 입력: "Stakeholder Energy Management 패턴을 적용했는데 상황이 좀 다른데?"
   - 예상 행동: 패턴을 참고만 하고 "이 상황은 다르니까" 명시, 필요시 새 TK 추출 권유
   - 근거: Boundary Check의 "이미 정해진 정책이 있으면 패턴 참조보다 정책 준수 우선"

2. **패턴을 찾을 수 없음**
   - 입력: "라이브러리를 검색했는데 유사한 패턴이 없다"
   - 예상 행동: "이것은 새 패턴의 가능성" → `/pm-tacit-extract`로 경험 기록
   - 근거: Failure Handling의 "패턴을 찾을 수 없어 판단 기준이 애매함"

3. **패턴을 따랐는데 결과가 나쁨**
   - 입력: "Why-First Decision Making 패턴대로 했는데 고객이 여전히 불만족했다"
   - 예상 행동: 근본 원인 분석 → 패턴 자체 문제인가, 실행 방식 문제인가 구분
   - 근거: Failure Handling의 "패턴을 따랐는데도 결과가 나쁨"

4. **팀원이 패턴을 잘못 이해함**
   - 입력: "팀원이 'Stakeholder Energy Management'를 실행했는데 모두 무시했다"
   - 예상 행동: 패턴의 "활성화/비활성화 조건"을 명확히 다시 설명
   - 근거: Failure Handling의 "팀원이 패턴을 잘못 이해함"

5. **법적/규제 의무가 있는 경우**
   - 입력: "패턴으로는 A를 선택해야 하는데 규제상 B를 선택해야 한다"
   - 예상 행동: "이 경우는 패턴을 무시하고 규제 준수 우선" 명시
   - 근거: Boundary Check의 "법적/규제 의무가 있는 결정은 패턴만으로 판단 금지"

