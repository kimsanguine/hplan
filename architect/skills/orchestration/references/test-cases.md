# Test Cases — orchestration 스킬

## 1) Trigger Tests

### Should Trigger (5)

1. "우리는 Research, Analysis, Writing, Review 4개의 에이전트가 순서대로 작동해야 한다. 어떤 패턴을 써야 할까?"
   - 이유: Sequential chain 패턴 선택 및 의존성 설계

2. "We have 5 competitors to analyze simultaneously. Can we run all 5 agents in parallel?"
   - 이유: Parallel fan-out/fan-in 패턴 선택과 aggregation 전략

3. "사용자 입력을 보고 영업용/기술용 에이전트 중 하나로 라우팅하려 한다"
   - 이유: Router 패턴 설계와 misclassification 처리

4. "현재 오케스트레이션이 느리다. 뭔가 바꿔야 할까?"
   - 이유: 패턴 재평가 및 성능 최적화

5. "에이전트 1개가 느리면 전체가 밀린다. 타임아웃을 어떻게 설정할까?"
   - 이유: 에러 처리 및 scaling 전략

### Should NOT Trigger (5)

1. "라우팅 결정을 에이전트로 만들고 싶은데 복잡해 보인다"
   - 올바른 라우팅: `orchestration --pattern router` (모델 선택 및 라우팅 규칙)

2. "에이전트 간에 메모리를 공유해야 한다"
   - 올바른 라우팅: `memory-arch` (메모리 저장소 및 검색)

3. "여러 에이전트를 조합했을 때 비용이 얼마나 드나?"
   - 올바른 라우팅: `strategy --focus biz-model` (비용 계산)

4. "Master-worker 계층 구조를 만들려면 통신 프로토콜이 뭘까?"
   - 올바른 라우팅: `harness-plan --mode 3-tier` (기술 구현 아키텍처)

5. "각 에이전트가 다른 모델을 써야 한다"
   - 올바른 라우팅: `orchestration --pattern router` (모델 선택)

## 2) Edge Cases

### 경계 사례 (4)

1. **Sequential vs Parallel 경계: 의존성이 약할 수도, 강할 수도**
   - 입력: "Analysis는 Research가 완료되어야 하지만, 동시에 다른 준비 작업도 할 수 있다"
   - 예상 행동: Hybrid 패턴 제안 (부분 parallel, 부분 sequential) 또는 의존성 재검토
   - 근거: Orchestration의 "Step 5 — Complexity Check" — 가장 간단한 패턴 우선

2. **Fan-in 병목: 가장 느린 agent 때문에 지연**
   - 입력: "3개 agent 병렬 (1초, 0.8초, 3초), aggregation이 느린 agent 대기"
   - 예상 행동: Timeout 설정 (2초), 또는 aggregator가 부분 결과로도 작동하도록 설계
   - 근거: Failure Handling의 "병렬 패턴에서 느린 agent 병목"

3. **Router 분류 오류: 모호한 입력**
   - 입력: "이 질문이 영업인지 기술인지 불명확한 경우 어떻게?"
   - 예상 행동: Fallback (둘 다 시도) 또는 사용자에게 재확인 요청
   - 근거: Failure Handling의 "라우터 분류 오류"

4. **계층 오케스트레이션 과도함**
   - 입력: "우리는 Hierarchical 패턴이 필요하다고 생각했는데 지연이 심해졌다"
   - 예상 행동: "가장 간단한 패턴부터" 원칙 위반 확인, Sequential/Parallel로 롤백 제안
   - 근거: Failure Handling의 "계층 오케스트레이션 오버헤드"

