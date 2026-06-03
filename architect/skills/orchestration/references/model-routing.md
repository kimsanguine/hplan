# Model Routing — 프로덕션 구현 디테일

> orchestration의 Router 패턴 중 **Model Routing(모델 선택)** 차원의 프로덕션 구현 레퍼런스.
> SKILL.md의 "Model Routing 상세 섹션"이 다루는 설계 로직(티어 분류·비용 비교·폴백 전략·실패 처리)의
> 하위 구현 디테일(ModelResolver·timeout override·Subagent Registry·Clarification 미들웨어)을 담는다.
>
> 참고: 여기서 다루는 것은 **에이전트는 동일하고 LLM 모델만 바뀌는** Model Routing이다.
> 에이전트 자체가 바뀌는 Agent Routing은 orchestration의 기본 Router 다이어그램을 참조.

---

## 1) Subagent Registry: 모델과 에이전트의 분리

프로덕션 시스템은 **모델 선택(Model Routing)**과 **에이전트 선택(Agent Routing)**을 명확히 분리한다.

```
사용자 요청
    ↓
[Clarification 미들웨어]
  → 모호성 해소
    ↓
리더 에이전트 (모델 선택 결정)
  → 작업 복잡도 평가
  → Primary 모델 선택
  → 폴백 체인 설정
    ↓
[Registry 쿼리]
  ├─ Subagent 목록 조회 (config.yaml)
  ├─ 선택된 모델로 인스턴스 생성
  └─ Timeout override 적용
    ↓
서브에이전트 실행
  (선택된 모델로 작업 수행)
    ↓
실패 → [폴백 1] → [폴백 2] → 최종 재시도
```

**Registry 패턴의 장점**:
- 모델 변경 시 코드 수정 불필요 (config.yaml만 수정)
- 런타임에 서브에이전트 추가/제거 가능
- 모델 해석력(explainability)을 위해 선택 이유도 기록

---

## 2) Config-Driven Timeout Override

프로덕션 시스템의 timeout 설정 방식:

```yaml
# config.yaml (예시값, 프로젝트에 맞게 조정)
app:
  default_timeout: 30  # 글로벌 기본값 (예시값: 30초)

model:
  timeout_override:
    "gpt-4": 60  # 모델별 override (예시값)
    "gpt-3.5-turbo": 30  # (예시값)
    "claude-3-opus": 120  # Opus는 복잡한 작업용 (예시값)

subagents:
  general:
    class: "agents.GeneralPurposeAgent"
    timeout: 45  # 에이전트별 override (예시값)
    model:
      name: "gpt-4"
      fallback: "gpt-3.5-turbo"

  bash:
    class: "agents.BashAgent"
    timeout: 120  # I/O 작업은 더 길게 (예시값)
    model: null

  specialized:
    class: "agents.SpecializedAnalysisAgent"
    timeout: 180  # 전문 작업용 (예시값)
    model:
      name: "claude-3-opus"
      fallback: "gpt-4"
```

**우선순위 (높음→낮음)**:
1. Subagent-specific timeout (config.yaml의 subagents.{name}.timeout)
2. Model-specific timeout (config.yaml의 model.timeout_override)
3. Global default timeout (config.yaml의 app.default_timeout)

---

## 3) Model Resolution with Fallback (ModelResolver)

프로덕션 시스템의 모델 해석 로직. 요청 모델 → subagent 기본값 → 폴백 체인 → 시스템 기본값 순서로
graceful degradation 하며, 각 단계는 선택 이유(explanation)를 함께 반환한다.

```python
class ModelResolver:
    def resolve_model(self, requested_model: str, subagent_name: str) -> str:
        """
        요청 모델 → 기본값 → None 순서로 폴백

        반환값은 (model_name, timeout, explanation)의 튜플
        """

        # Step 1: 요청된 모델 확인
        if requested_model and is_available(requested_model):
            timeout = config.model.timeout_override.get(
                requested_model,
                config.app.default_timeout
            )
            return (requested_model, timeout, "User requested")

        # Step 2: Subagent 설정의 기본값 확인
        subagent_config = config.subagents[subagent_name]
        if subagent_config.model and subagent_config.model.name:
            primary_model = subagent_config.model.name
            timeout = subagent_config.timeout  # subagent override 우선
            return (primary_model, timeout, "Subagent config")

        # Step 3: 폴백 체인
        if subagent_config.model and subagent_config.model.fallback:
            fallback_model = subagent_config.model.fallback
            timeout = config.model.timeout_override.get(
                fallback_model,
                config.app.default_timeout
            )
            logger.warning(f"Primary model unavailable. Using fallback: {fallback_model}")
            return (fallback_model, timeout, "Fallback chain")

        # Step 4: 시스템 기본값
        default = "gpt-3.5-turbo"
        timeout = config.app.default_timeout
        logger.error(f"No model configured for {subagent_name}. Using system default.")
        return (default, timeout, "System default")

    def create_subagent(self, name: str, requested_model: str = None) -> object:
        """
        1. 모델 해석
        2. 타임아웃 설정
        3. 폴백 준비
        """
        model, timeout, reason = self.resolve_model(requested_model, name)

        subagent_class = import_class(config.subagents[name].class_path)
        subagent = subagent_class(
            model=model,
            timeout=timeout,
            fallback_models=self.get_fallback_chain(name),
            explanation=f"Model selection reason: {reason}"
        )

        logger.info(f"Created {name} with model={model}, timeout={timeout}s ({reason})")
        return subagent
```

---

## 4) Clarification 미들웨어 — 라우팅 전 모호성 해소

라우팅 결정의 정확도는 입력 모호성에 좌우된다. 모호한 요청은 라우팅 전에 미들웨어로 해소한다.

```python
class ClarificationMiddleware:
    """요청이 모호하면 리더 에이전트가 명확히 하도록 강제"""

    def process(self, thread_state: ThreadState) -> ThreadState:
        user_input = thread_state.messages[-1].content

        # 모호성 감지 (정규식, 키워드 분석)
        ambiguities = self.detect_ambiguities(user_input)

        if len(ambiguities) > 0:
            # Clarification 질문 생성
            clarification_prompt = self.generate_questions(ambiguities)

            # 리더 에이전트에게 의도 전달
            thread_state.metadata["needs_clarification"] = {
                "questions": clarification_prompt,
                "detected_ambiguities": ambiguities
            }

            # 시스템 프롬프트에 추가
            system_prompt += f"""
사용자 요청에 다음 모호성이 있습니다:
{clarification_prompt}

먼저 사용자에게 확인한 후 작업을 진행하세요.
"""

        return thread_state
```

**예시**:
```
사용자: "보고서 만들어줘"
↓
[Clarification]
  감지된 모호성:
  - 보고서 종류? (기술, 비즈니스, 성과 등)
  - 대상 청중? (임원진, 팀, 클라이언트)
  - 분석 범위? (월간, 분기, 연간)
↓
Clarification 질문 반환:
"어떤 보고서가 필요하신가요? (1) 기술보고서, (2) 비즈니스보고서..."
↓
사용자: "기술보고서, 최근 3개월"
↓
명확해진 요청으로 라우팅 실행
```

---

## 5) 총 비용 계산 프레임워크

API 단가만으로는 라우팅 경제성을 정확히 평가할 수 없다. 지연시간·재처리 비용까지 포함한다.

**단일 모델 (항상 T3 사용) 시나리오 (예시값)**:
```
월간 작업 수: 10,000개
T3 평균 비용/작업: $0.02 (예시값)
월간 총 비용 = 10,000 × $0.02 = $200/월
```

**라우팅 시나리오 (예시값)**:
```
T1 (40%): 4,000개 × $0.005/작업 = $20
T2 (35%): 3,500개 × $0.01/작업 = $35
T3 (20%): 2,000개 × $0.02/작업 = $40
T4 (5%): 500개 × $0.05/작업 = $25
라우팅 오버헤드: $10 (보통 전체 비용의 1-5%, 예시값)
월간 총 비용 = $20 + $35 + $40 + $25 + $10 = $130/월
```

**비용 절감 = ($200 - $130) / $200 = 35% (예시값)**

**총 비용 계산 프레임워크**:
```
총 비용 = API 호출 비용 + (지연시간 비용) + (재처리 비용)

세부 항목:
1. API 호출 비용 = Σ(모델별 토큰 단가 × 예상 호출 수)
2. 지연시간 비용 = 평균 지연시간(초) × 시간당 비용 × 월간 요청 수
   - 사용자가 기다리는 시간이 비용으로 환산됨 (생산성 손실)
3. 재처리 비용 = 오류율 × 재처리 모델 비용 × 월간 요청 수
   - 폴백 발동 시 추가 비용 발생
```

**예시 계산**:
```
조건:
- 월간 요청 수: 1,000개
- 오류율: 5% (50개 재처리)
- 시간당 비용: $100 (사용자 시간 가치)

API 비용: $130 (위 시나리오)
지연시간 비용: 평균 2초 × ($100/3600) × 1,000 = $55
재처리 비용: 50개 × $0.02 (T3 모델) = $1

총 비용 = $130 + $55 + $1 = $186/월
```

**체크리스트:**
- [ ] 절감액 > 라우팅 오버헤드 (일반적으로 절감이 10배 이상일 때 도입 가치)
- [ ] T1 작업 비율이 30% 이상일 때 경제성 최대화
- [ ] 정확도 90% 이상 확보 후 폴백 비용 고려
- [ ] 지연시간 비용도 포함하여 총 비용 평가

---

## 6) 2단계 품질 게이트

라우팅 결정의 신뢰성을 검증하기 위한 2단계 게이트 설계:

**Stage 1: Confidence Threshold Check (라우팅 전)**
- 라우터가 작업 분류를 정하기 전에 신뢰도 점수 계산
- 신뢰도 > 85% (예시값)이면 선택 모델로 라우팅
- 신뢰도 ≤ 85%이면 Clarification 미들웨어 실행 (사용자 확인)
- 목표: 오분류율 <10%

**Stage 2: Output Validation (라우팅 후)**
- 모델의 응답 품질을 검증 (길이, 형식, 컨텍스트 관련성)
- 품질 점수 < 80% (예시값)이면 폴백 모델로 재시도
- 폴백 모델도 실패 시 T3 모델로 최종 재시도
- 목표: 최종 품질 점수 > 90%

**효과:**
- 잘못된 라우팅 조기 감지
- 사용자 만족도 유지 (품질 저하 최소화)
- 비용과 품질의 균형 유지

---

## 7) 라우터 설계의 핵심 원칙 3가지

| 원칙 | 설계 | 프로덕션 구현 |
|-----|------|-------------|
| **명시성** | 선택 기준을 명시적으로 정의 | Config-driven timeout + explanation 기록 |
| **폴백성** | 모든 경로에 대안 있음 | Primary → Fallback 1 → Fallback 2 체인 |
| **확장성** | 새 모델/에이전트 추가 용이 | Registry 패턴 + config 기반 (코드 수정 불필요) |

**실무 적용 체크리스트**:

1. **Timeout 설정**
   - [ ] 기본값 설정했는가? (보통 30초)
   - [ ] I/O 작업은 더 길게? (bash 60초+)
   - [ ] 전문 작업은? (complex analysis 120초+)
   - [ ] 모니터링 중 자주 timeout나는 에이전트 없는가?

2. **폴백 체인**
   - [ ] Primary 모델이 unavailable이면? (명시적 fallback)
   - [ ] Fallback도 실패하면? (최종 에러 처리)
   - [ ] 폴백 발동 빈도 추적하는가? (>10% = 문제 신호)

3. **Clarification 활성화**
   - [ ] 사용자 요청이 모호할 가능성 높은가? → 미들웨어 활성화
   - [ ] 자동 분류 정확도 낮은가? (90% 미만) → Clarification 필수
   - [ ] 모호성을 줄일 프롬프트 엔지니어링 했는가?

4. **모니터링**
   - [ ] 각 모델별 호출 수 추적
   - [ ] 라우팅 정확도 (올바른 모델 선택 비율)
   - [ ] 폴백 빈도 (낮을수록 좋음, <5% 목표)
   - [ ] 최종 응답 품질 점수 (≥90% 목표)

---

## 8) Trigger / Edge Test Cases

### Should Trigger (Model Routing) (5)

1. "우리는 간단한 작업도 하고 복잡한 작업도 한다. 비싼 모델을 모든 작업에 쓰면 비용이 너무 높다"
   - 이유: 작업 복잡도별 모델 분류 및 라우팅 규칙 설계
2. "Claude Haiku는 충분한데 왜 Sonnet을 써야 할까? 비용을 40% 줄일 수 있는 기준이 뭔가?"
   - 이유: T1/T2/T3 경계 정의 및 cost-quality tradeoff
3. "우리 T1 모델 선택이 자주 실패한다. 자동으로 T2로 재시도하려면?"
   - 이유: Fallback 전략 설계
4. "모델 라우팅 후 실제 비용이 예상치와 다르다. 뭐가 잘못됐나?"
   - 이유: 라우팅 정확도 및 비용 실제값 재측정
5. "작업 복잡도를 자동으로 판단하는 프롬프트를 어떻게 만들까?"
   - 이유: 라우팅 decision logic 설계

### Should NOT Trigger (Model Routing) (5)

1. "여러 에이전트 중 어느 것을 호출할지 선택하고 싶다"
   - 올바른 라우팅: orchestration의 **Agent Routing** (Router 기본 다이어그램)
2. "라우팅 결과의 비용 영향을 분석하고 싶다"
   - 올바른 라우팅: `biz-model` (ROI 계산)
3. "모델 성능을 비교하려면 어떤 테스트를 해야 할까?"
   - 올바른 라우팅: measure의 `agent-ab-test` (A/B 테스트)
4. "T1 모델이 충분하지 않은 작업들을 찾으려면?"
   - 올바른 라우팅: measure의 `kpi` (메트릭 정의 및 분석)
5. "우리 API 제공자가 모델 가격을 올렸다"
   - 올바른 라우팅: `biz-model` (비용 재계산)

### Edge Cases (5)

1. **라우팅 오버헤드 > 절감**
   - 입력: "라우팅 판단이 $0.02이고, T1 절감이 $0.001/태스크인데..."
   - 예상 행동: 라우팅 불필요 → T2 고정 추천
   - 근거: Model Routing의 Boundary Check — 라우팅 비용 > 저가 모델 절감
2. **모든 작업이 고복잡도인 경우**
   - 입력: "우리는 고급 전략 분석만 한다. 라우팅이 의미 있나?"
   - 예상 행동: T3 고정, 라우팅 불필요 지적
3. **T1 vs T2 경계 애매**
   - 입력: "이 작업이 T1인지 T2인지 판단 기준이 뭔가?"
   - 예상 행동: 실제 예제로 테스트 후 경계 명확화 필요
4. **품질 저하가 받아들여지지 않음**
   - 입력: "비용을 40% 줄였는데 품질 점수가 95% → 87%로 떨어졌다"
   - 예상 행동: 품질 요구사항 재협상 또는 라우팅 기준 상향 조정
5. **모델 API 장애 시 폴백 부족**
   - 입력: "T2 모델이 다운되면 모두 T3로 가야 하는데 비용이 폭증한다"
   - 예상 행동: Fallback chain 재설계 (다른 제공자 T2 또는 T1 + quality check)

---

## 9) Troubleshooting

### 9.1) 라우팅 오분류: T1 모델로 충분하지 않은 작업

**증상:**
- T1로 라우팅한 작업의 출력 품질: 평균 65% (목표 90% 미달)
- 폴백 발동 빈도: 30%+ (효율성 저하)
- 사용자 피드백: "부정확해요"

**확인:**
- 라우팅 결정 기준: T1 기준이 너무 느슨한가? (T1 기준 "간단한 추출, 분류" → 실제로는?)
- 실제 T1 성능: 정말로 65%인가, 아니면 프롬프트가 부족한가?
- 폴백 발동 패턴: 어떤 유형의 작업이 자주 실패하는가?

**조치:**
1. **라우팅 기준 재설정**: T1 임계값 높이기 (예: "명확한 규칙 기반"만 T1, "약간의 판단" 필요하면 T2), 또는 신뢰도 조건 추가 (신뢰도 < 0.7이면 T2)
2. **T1 프롬프트 강화**: T1 성능이 낮으면 few-shot examples 추가
3. **Fallback 자동 기록**: 실패한 작업의 특징을 학습 → 라우팅 규칙 개선
4. **T1 능력 확장**: 단순 추출이 아니라 "기본 추론"까지 가능하게 프롬프트 개선
5. **실제 테스트**: 200개 샘플로 T1/T2/T3 성능 A/B 테스트 → 경계선 명확화

### 9.2) 비용 절감 목표 미달: 예상보다 고비용 모델 호출

**증상:**
- 목표: T1 50%, T2 40%, T3 10%
- 실제: T1 10%, T2 30%, T3 60%
- 비용 절감: 예상 40% → 실제 0% (오히려 증가)

**확인:**
- 라우팅 정확도: 실제로 T1이 10%만 가능한 걸까?
- 폴백 빈도: T1 실패 → T2 재시도 → T2 실패 → T3 재시도 (cascade)
- 작업 분포: 실제 들어오는 작업이 예상보다 복잡한가?

**조치:**
1. **Cascade 폴백 비용 증가 감지**: 폴백으로 인한 추가 비용 계산 (성공 시 1회, 실패 시 3회)
2. **라우팅 기준 보수적 조정**: T1 사용률 낮추고 T2를 기본값으로 → 폴백 감소
3. **T1 능력 강화**: 프롬프트, in-context learning 개선으로 성공률 ↑
4. **작업 분포 재조사**: 실제 들어오는 작업이 복잡한가? 고객 요청 변화?
5. **비용 vs 품질 재협상**: 절감 40%는 너무 높을 수 있음 → 20% 목표로 재설정 (현실적)

### 9.3) 모델 API 장애: T2 모델 다운

**증상:**
- T2 모델(Claude Sonnet) API 다운
- 모든 T2 라우팅이 T3로 폴백 → 비용 3배
- 또는 폴백이 없으면 → 사용자에게 에러

**확인:**
- Fallback strategy: Primary → Fallback 1 → Fallback 2가 정의되어 있는가?
- Fallback 1은 무엇인가? (다른 제공자의 T2? T1으로 품질 저하? 캐시된 답변?)

**조치:**
1. **Fallback chain 다양화**:
   - Primary: Claude Sonnet (T2)
   - Fallback 1: GPT-4o (다른 제공자 T2)
   - Fallback 2: Claude 3.5 Haiku (T1, 품질 저하 수용)
   - Fallback 3: 사용자에게 "재시도 후" 요청
2. **다중 제공자 사용**: Anthropic + OpenAI 동시 계약 → failover
3. **캐싱 전략**: 같은 쿼리는 이전 결과 반환 (1시간 TTL)
4. **모니터링**: API 상태 실시간 확인 → 미리 Fallback 활성화
5. **SLA 기준 재정의**: "T2 불가능 → T1 자동 선택" vs "사용자 대기" 정책

### 9.4) 품질-비용 균형 붕괴: 비용 줄었으나 품질 급락

**증상:**
- 전월 만족도: 95% (T2/T3 혼용)
- 이번달 만족도: 82% (라우팅 도입 후)
- "비용은 줄었는데 고객 만족도가..."

**확인:**
- 실제 품질 저하: T1 비율 증가 때문인가?
- 폴백으로 인한 지연: 사용자가 "느려졌다"고 느끼는가?
- 고객 세그먼트: 만족도 저하가 모든 고객인가, 특정 고객군인가?

**조치:**
1. **라우팅 회귀**: T1 비율을 50% → 30%로 감소, 품질 먼저
2. **보수적 조정**: 비용 절감 40% 목표를 20%로 재설정
3. **고객별 맞춤**: 중요 고객은 T3, 일반 고객은 T2/T1 혼용
4. **품질 게이트 강화**: "만족도 < 85%면 즉시 T2로 상향" 자동 규칙
5. **설명 추가**: 사용자에게 "빠른 응답을 위해 비용 최적화했습니다" 투명성 제공
