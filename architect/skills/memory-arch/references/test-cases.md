# Test Cases — memory-arch 스킬

## 1) Trigger Tests

### Should Trigger (5)

1. "고객 상담 에이전트가 이전 상담 기록을 기억해야 한다. 어디에 저장해야 할까?"
   - 이유: 메모리 유형(episodic) 선택과 저장소 아키텍처 설계 필요

2. "Our personal assistant needs to remember user preferences across conversations. How do we structure the memory?"
   - 이유: 사용자 선호도(episodic + semantic)를 여러 세션에 걸쳐 유지하는 메모리 아키텍처

3. "컨텍스트 윈도우가 200K인데 메모리를 얼마나 많이 주입해야 효율적일까?"
   - 이유: 메모리 예산 설계와 검색 전략 수립 필요

4. "에이전트가 실수한 것을 기억해서 다음에는 같은 실수를 하지 않게 하려면?"
   - 이유: 메모리 라이프사이클 관리와 모순 감지 시스템 설계

5. "복수의 사용자가 같은 에이전트를 쓰는데 메모리가 섞이면 안 된다"
   - 이유: 메모리 저장소의 사용자 격리 로직 설계 필수

### Should NOT Trigger (5)

1. "여러 에이전트 간에 메모리를 공유해야 한다. 통신 프로토콜이 뭘까?"
   - 올바른 라우팅: `orchestration` (에이전트 간 데이터 흐름)

2. "메모리 저장소의 비용이 너무 높다. 어떻게 절감할까?"
   - 올바른 라우팅: `strategy --focus biz-model` (인프라 비용 계산 및 최적화)

3. "메모리에 저장한 데이터가 사용자 간에 노출되면 안 되는데, 권한 관리를 어떻게 하지?"
   - 올바른 라우팅: `orchestration` 또는 아키텍처 전문 (시스템 설계 영역)

4. "이전 대화의 정보가 지금 대화와 어떻게 연결되는지 에이전트가 파악하지 못한다"
   - 올바른 라우팅: `pm-engine` (에이전트 판단 로직 개선, TK)

5. "검색된 메모리가 관련성이 없다. 검색 알고리즘을 어떻게 개선하지?"
   - 올바른 라우팅: `memory-arch` (검색 전략 개선) — 하지만 이건 이미 memory-arch 내 Step 4에서 다룸

## 2) Edge Cases

### 경계 사례 (4)

1. **컨텍스트 윈도우 오버플로우**
   - 입력: "메모리 주입 때문에 컨텍스트가 꽉 찬다. 응답이 지연된다"
   - 예상 행동: 메모리 예산 재조정 (30% → 20%), 덜 중요한 기억 제거, 또는 메모리 요약 추가
   - 근거: Failure Handling의 "메모리 주입으로 인한 컨텍스트 오버플로우"

2. **메모리 모순 감지**
   - 입력: "사용자 정보가 바뀌었는데 에이전트가 이전 정보를 먼저 반환했다"
   - 예상 행동: 메모리 버전 관리 시스템 도입 또는 모순 감지 시 사용자 확인 요청
   - 근거: Failure Handling의 "메모리 모순"

3. **세션 간 메모리 검색 실패**
   - 입력: "사용자가 '지난주에 네가 한 말' 참조했는데 에이전트가 못 찾는다"
   - 예상 행동: 검색 알고리즘 개선 (recency weighting, semantic similarity, explicit filtering)
   - 근거: Failure Handling의 "검색 결과가 관련성 없음"

4. **Working Memory와 Long-term Memory 경계**
   - 입력: "현재 대화와 과거 데이터를 구분해야 하는데 어디서부터 Long-term?
   - 예상 행동: Working Memory는 현재 세션만, Episodic은 과거 상호작용 저장 기준 명확화
   - 근거: Memory-arch의 "Step 2 — What to Remember" 구분 기준

