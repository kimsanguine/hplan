# 좋은 예제 — Model Routing (orchestration Router 패턴)

## 사용자 요청
"우리 고객 지원 챗봇이 매일 1,000개 질문을 받는데, 간단한 것과 복잡한 것이 섞여 있어. 비용을 절감하면서도 품질을 유지하려면 어떻게 모델을 선택해야 할까?"

## 승인 이유
- 여러 모델을 사용하는 에이전트 시스템의 **비용 최적화**가 필요
- 작업 복잡도별로 모델을 다르게 선택할 수 있는 상황
- 성능(품질)과 비용의 명시적 트레이드오프 필요
- → orchestration의 Router 패턴 중 **Model Routing** 차원에 해당 (에이전트는 동일, LLM 모델만 바뀜)

## 예상 처리
1. 작업 분류: 상태 조회(T1), 진단(T2), 전략 조언(T3)으로 세분화
2. 라우팅 결정 매트릭스: 각 작업의 입력 복잡도, 출력 민감도 평가
3. 비용 비교: "모두 T3" vs "라우팅" vs "모두 T1" 시나리오 계산
4. 폴백 전략: T1 실패 → T2 → T3 체인 설계
5. 모니터링: 주간 라우팅 정확도, 폴백 빈도 추적

## 처리 결과 예시
```
라우팅 테이블:
┌──────────────────┬────┬────────────┬────────┐
│ Task             │Tier│ Model      │ $/run  │
├──────────────────┼────┼────────────┼────────┤
│ FAQ 조회         │T1  │ Haiku      │$0.001 │
│ 문제 진단        │T2  │ Sonnet     │$0.005 │
│ 전략 조언        │T3  │ Opus       │$0.015 │
└──────────────────┴────┴────────────┴────────┘

월간 1,000건 중 600/T1 + 300/T2 + 100/T3 = $3
vs 모두 T3: $15 (80% 절감)
```

## 프로덕션 Model Routing 패턴 Good Example

### 고객 지원 챗봇의 라우팅 설계

매일 1,000개 질문이 들어오는 고객 지원 챗봇에서 프로덕션 라우팅 패턴을 적용한다.

### 1단계: Clarification 미들웨어 활성화

```python
# middleware/clarification.py
class CSMClarificationMiddleware:
    def detect_ambiguities(self, user_input: str) -> list:
        """고객 지원 질문의 모호성 감지"""

        ambiguities = []

        # 패턴 1: 모호한 범주
        if "문제" in user_input and "어디" not in user_input and "무엇" not in user_input:
            ambiguities.append({
                "type": "category",
                "detected": "문제의 구체적 범위 불명확",
                "clarification": "어떤 제품/기능의 문제인가요? "
                                 "(1) 배송, (2) 결제, (3) 앱 버그"
            })

        # 패턴 2: 모호한 우선도
        if "빨리" in user_input or "긴급" in user_input:
            ambiguities.append({
                "type": "priority",
                "detected": "긴급도 불명확",
                "clarification": "현재 사용할 수 없는 상태인가요? "
                                 "(Y/N)"
            })

        # 패턴 3: 모호한 기술 수준
        if "된다" in user_input and "안됨" not in user_input:
            ambiguities.append({
                "type": "technical",
                "detected": "기술 수준 파악 어려움",
                "clarification": "어떤 오류 메시지가 나나요? "
                                 "또는 스크린샷을 올려주세요."
            })

        return ambiguities
```

### 2단계: 작업 분류 및 라우팅 테이블

```yaml
# config.yaml
router:
  classification_rules:
    # T1: 간단한 조회
    faq:
      keywords: ["배송 조회", "주문 상태", "반품 정책", "가격", "사이즈"]
      model: "gpt-3.5-turbo"  # 경량 모델
      timeout: 15  # 빠른 응답
      subagent: "general"
      confidence_threshold: 0.9  # 높은 신뢰도

    # T2: 진단 및 문제 해결
    troubleshooting:
      keywords: ["안됨", "오류", "작동하지", "못함", "문제"]
      model: "gpt-4"  # 중간 모델
      timeout: 45
      subagent: "general"
      confidence_threshold: 0.8

    # T3: 전략적 조언 및 복잡한 요청
    strategic:
      keywords: ["추천", "최적", "전략", "장기", "비즈니스", "협력"]
      model: "gpt-4-turbo"  # 고성능 모델
      timeout: 120
      subagent: "specialized_csm"
      confidence_threshold: 0.7  # 더 관대 (복잡한 요청)

  # 분류 불확실 시 폴백
  fallback_classification: "troubleshooting"  # T2로 폴백
```

### 3단계: Subagent Registry 구성

```yaml
subagents:
  general:
    class: "agents.GeneralPurposeAgent"
    description: "FAQ 답변 및 기본 진단"
    timeout: 45  # 에이전트별 override
    model:
      name: "gpt-4"
      fallback: "gpt-3.5-turbo"

  specialized_csm:
    class: "agents.SpecializedCSMAgent"
    description: "고객 관계 전략, 복잡한 요청"
    timeout: 120
    model:
      name: "gpt-4-turbo"
      fallback: "gpt-4"

  bash:
    class: "agents.BashAgent"
    description: "주문 조회, DB 쿼리"
    timeout: 60  # I/O 작업이므로 더 길게
    model: null

app:
  default_timeout: 30  # 글로벌 기본값
```

### 4단계: 라우팅 로직 (Python)

```python
class CSMRouter:
    def route(self, user_input: str, thread_state: ThreadState) -> tuple:
        """
        사용자 입력 → (Subagent, Model, Timeout, Reason)
        """

        # Step 1: Clarification 미들웨어 실행
        ambiguities = self.clarification.detect_ambiguities(user_input)
        if ambiguities:
            return self.ask_clarification(ambiguities)

        # Step 2: 작업 분류 (자동)
        classification = self.classify_input(user_input)
        # 예: {"category": "faq", "confidence": 0.95}

        if classification["confidence"] < 0.7:
            # 불확실하면 T2로 폴백
            category = "troubleshooting"
            reason = f"Low confidence ({classification['confidence']:.1%})"
        else:
            category = classification["category"]
            reason = f"Classification: {category}"

        # Step 3: Config에서 라우팅 정보 조회
        routing_config = config.router.classification_rules[category]

        # Step 4: 모델 해석 (ModelResolver 사용)
        model, timeout, model_reason = self.model_resolver.resolve_model(
            requested_model=None,  # 사용자가 모델 요청 안 함
            subagent_name=routing_config["subagent"]
        )

        # Step 5: 폴백 체인 준비
        fallback_chain = [
            model,
            routing_config["fallback"],
            config.app.default_model
        ]

        return {
            "subagent": routing_config["subagent"],
            "model": model,
            "timeout": routing_config["timeout"],
            "fallback_chain": fallback_chain,
            "reason": reason,
            "category": category,
            "confidence": classification["confidence"]
        }
```

### 5단계: 실행 흐름 예시

```
사용자 입력: "배송 조회하고 싶은데 어떻게 하나요?"

1. [Clarification]
   ✓ "배송 조회" 명확함
   ✓ 우선도 없음 (기본)
   → 모호성 없음, 진행

2. [Classification]
   keyword match: "배송 조회" ← faq에 매칭
   confidence: 0.95 (높음)
   → category = "faq"

3. [Routing Decision]
   Config lookup:
   ├─ subagent: "general"
   ├─ model: "gpt-3.5-turbo" (T1용 경량 모델)
   ├─ timeout: 15
   └─ reason: "FAQ with high confidence"

4. [ModelResolver]
   resolve_model("general"):
   ├─ requested_model: null (요청 없음)
   ├─ subagent config: gpt-3.5-turbo
   └─ resolved: (gpt-3.5-turbo, 15s, "Subagent config")

5. [Subagent Execution]
   create_subagent("general", model="gpt-3.5-turbo", timeout=15)
   ↓
   실행: "배송 조회 방법" FAQ 응답
   ↓
   성공 (15초 이내)

6. [Memory 저장]
   ├─ Episodic: "배송 조회 질문"
   └─ Semantic: "배송 프로세스" (재사용)

===========================================

사용자 입력: "결제가 안 되는데 어떻게 해야 할까요?"

1. [Clarification]
   ✓ "결제 안됨" 명확함
   ✓ 오류 가능성 높음 (기술 수준 불명확)
   → "어떤 오류 메시지가 나나요?" 질문

2. 사용자 응답: "카드가 승인되지 않음이라는 메시지가 나와요"

3. [Classification]
   keyword match: "안됨", "오류" ← troubleshooting에 매칭
   confidence: 0.88 (높음)
   → category = "troubleshooting"

4. [Routing Decision]
   Config lookup:
   ├─ subagent: "general"
   ├─ model: "gpt-4" (T2용 중간 모델)
   ├─ timeout: 45 (더 길게, 진단 필요)
   └─ reason: "Troubleshooting with clear symptoms"

5. [Subagent Execution]
   create_subagent("general", model="gpt-4", timeout=45)
   ↓
   실행: "결제 오류 진단 및 해결 단계"
   ├─ 1. 카드 정보 확인
   ├─ 2. 결제 시스템 상태 확인
   └─ 3. 대체 결제 방법 제시
   ↓
   성공 (35초)

===========================================

사용자 입력: "우리 회사와 파트너십 계약을 맺고 싶은데 어떻게 진행해야 할까요?"

1. [Clarification]
   ✓ "파트너십" 명확함
   ✓ 비즈니스 전략 (높은 복잡도)
   → 추가 정보 요청: "현재 상황은?"

2. [Classification]
   keyword match: "파트너십", "전략", "계약" ← strategic에 매칭
   confidence: 0.92 (높음)
   → category = "strategic"

3. [Routing Decision]
   Config lookup:
   ├─ subagent: "specialized_csm"
   ├─ model: "gpt-4-turbo" (T3용 고성능)
   ├─ timeout: 120 (깊은 분석 필요)
   └─ reason: "Strategic partnership inquiry"

4. [Subagent Execution]
   create_subagent("specialized_csm", model="gpt-4-turbo", timeout=120)
   ↓
   실행: "파트너십 전략 수립"
   ├─ 1. 회사 분석
   ├─ 2. 협력 모델 제시
   ├─ 3. 계약 로드맵
   └─ 4. 영업 담당자 연결
   ↓
   성공 (90초)
```

### 6단계: 성과 모니터링

```python
# 일일 리포트
monitoring_report = {
    "date": "2026-03-07",
    "total_requests": 1000,
    "routing_accuracy": {
        "faq": {"count": 600, "accuracy": 0.97, "avg_time": 8.5, "cost": "$0.60"},
        "troubleshooting": {"count": 300, "accuracy": 0.88, "avg_time": 32, "cost": "$1.50"},
        "strategic": {"count": 100, "accuracy": 0.92, "avg_time": 95, "cost": "$1.50"}
    },
    "fallback_triggered": {
        "total": 12,  # 1.2%
        "faq_to_troubleshooting": 8,
        "troubleshooting_to_strategic": 4
    },
    "timeout_incidents": {
        "total": 2,  # 0.2%
        "faq": 0,
        "troubleshooting": 1,
        "strategic": 1
    },
    "cost_comparison": {
        "actual_cost": "$3.60",
        "if_all_t3": "$15.00",
        "savings": "76%"
    }
}
```

### 핵심 특징

| 특징 | 효과 |
|-----|-----|
| **Clarification 미들웨어** | 모호한 요청 사전 차단 (정확도 95%+ 유지) |
| **Registry 패턴** | 모델/에이전트 변경 시 config만 수정 (코드 불필요) |
| **Timeout Override** | 작업 유형별 최적화 (T1 15s, T2 45s, T3 120s) |
| **Fallback 체인** | 실패율 <2% (자동 재시도) |
| **모니터링** | 일일 추적으로 문제 조기 발견 |
