---
name: strategy
description: "전략 설계 통합 — 비즈니스 모델 캔버스(biz-model), 경쟁 해자 분석(moat), 성장 루프 설계(growth-loop) 통합. Use when defining business strategy, competitive positioning, or growth mechanics for an AI product."
argument-hint: "[product/agent] [--focus biz-model|moat|growth-loop|all]"
allowed-tools: ["Read", "Write"]
model: inherit
---

# Strategy — 비즈니스 모델 · 경쟁 해자 · 성장 루프 통합 설계

Running for: **$ARGUMENTS**

## Core Goal

- 가치 창출(사용자 절감액/개선도)과 가치 포획(수익 모델) 사이의 균형을 설정하여 지속 가능한 비즈니스 구조 설계
- 모델 성능이 commodity화되는 시장에서 데이터·워크플로우·네트워크 차원의 경쟁 우위를 설계하여 방어선 구축
- 에이전트 사용 데이터가 자동으로 제품을 개선하는 성장 루프를 설계하여 시간이 지날수록 경쟁 격차가 벌어지는 구조 구축

---

## 비즈니스 모델 (biz-model)

### 수익 모델 선택 기준

| 모델 | 언제 적합한가 | 리스크 |
|------|-------------|--------|
| Per-execution | 출력 단위가 명확할 때 | 사용량 불안 |
| Tiered subscription | 예측 가능한 사용 패턴 | 과/저 프로비저닝 |
| Outcome-based | 성과를 직접 측정할 수 있을 때 | 귀인 어려움 |
| Seat-based + usage | 팀 도구, 사용 강도 편차 큼 | 복잡성 |
| Freemium | 네트워크 효과·바이럴 가능성 | 전환율 |

### 가치 창출 분석 체크리스트

- Time Saved: [시간/주] × [시급] = [$/주]
- Error Reduction: [오류율 전] → [후] × [오류당 비용]
- New Capability: 기존에 불가능했던 것
- Scale Factor: 1인이 N인 분량을 처리 가능

### 단위 경제 (Unit Economics)

```
CPE(Cost Per Execution) = 총비용 ÷ 실행 횟수
목표 Gross Margin > 70% (SaaS 기준)

고객당 월 수익: $___
고객당 월 비용:
  - LLM API: $___
  - 인프라: $___
  - 지원: $___
  - CAC 분할상환: $___
```

**가치 포획 원칙**: 생성 가치의 10~20% 청구. 경쟁 대안(사람 처리, 아웃소싱)을 가격 상한 기준으로.

**비용 구조 실패 신호**: CPE가 목표 이윤율 초과 → API 최적화(모델 라우팅), 배치 처리, 또는 가격 인상 검토.

---

## 경쟁 해자 (moat)

### 6가지 Moat 유형 평가 (1~5점)

| Moat 유형 | 설명 | 점수 | 근거 |
|-----------|------|------|------|
| Data Flywheel | 사용 → 데이터 → 제품 개선 → 더 많은 사용 | /5 | |
| Workflow Lock-in | 사용자 일상 프로세스에 깊이 통합 | /5 | |
| Network Effects | 사용자 증가 → 모든 사용자 가치 증가 | /5 | |
| Switching Cost | 경쟁사로 이동하는 데 드는 비용/고통 | /5 | |
| Proprietary Knowledge | 독점 도메인 전문성 | /5 | |
| Speed/UX Moat | 대안 대비 10배 나은 경험 | /5 | |

**Copy-Time 18개월 미만이면 진정한 moat이 아님** — 보강 또는 전환 필요.

### Maturity Stage

```
Stage 1 (Pre-PMF): moat 없음 → Copy-Time 3~6개월
Stage 2 (Growth): 단일/이중 moat 형성 → Copy-Time 12~18개월
Stage 3 (Expansion): 3+ moat 시너지 → Copy-Time 24~36개월
Stage 4 (Dominance): Core Power 극강 → Copy-Time 36~60개월+
```

### Moat 조합 전략

```
Enterprise → Workflow Lock-in + Switching Cost 우선 (통합 깊이)
SMB → Speed/UX + Data Flywheel 우선 (빠른 가치 체감)
Platform → Network Effects + Data 우선 (양면 시장)
```

### False Moat 제거 체크리스트

| 거짓 Moat | Copy-Time |
|----------|-----------|
| "GPT-4/Claude 사용" | ~1주 |
| "프롬프트 비밀" | 1~3개월 |
| "더 많은 데이터" (비독점) | 6~12개월 |
| "기술이 복잡함" | 3~9개월 |
| "먼저 출시함" | 6~18개월 |

### Moat 구축 로드맵

```
Phase 1 (0-3개월): UX/Speed moat — 초기 고객 확보
Phase 2 (3-6개월): Workflow lock-in — 일상 프로세스 통합
Phase 3 (6-12개월): Data flywheel — 복합 우위 축적
Phase 4 (12+개월): Network effects — 해당 시 적용
```

---

## 성장 루프 (growth-loop)

### 루프 유형 선택

```
Type A — Data Quality Loop (가장 강력)
  사용 → 피드백 데이터 축적 → 모델/프롬프트 개선 → 더 좋은 결과 → 더 많은 사용

Type B — Content Loop
  사용 → 콘텐츠 생성 → 콘텐츠가 새 유저 유입 → 더 많은 사용

Type C — Network Loop
  유저 A 사용 → 유저 B에게 가치 → 유저 B 가입 → 유저 A에게 더 큰 가치

Type D — TK Accumulation Loop
  PM 판단 경험 → TK 추출 → 에이전트 인스트럭션 개선 → 더 나은 판단
```

### Loop Strength 평가 (총점 20+ = 강한 플라이휠)

| 요소 | 질문 | 강도(1-5) |
|------|------|-----------|
| Data Uniqueness | 경쟁사가 동일 데이터를 얻을 수 있는가? | |
| Improvement Speed | 데이터 → 개선까지 소요 시간 | |
| User Perception | 유저가 개선을 체감하는가 | |
| Switching Cost | 축적 데이터 때문에 이탈이 어려운가 | |
| Compounding | 시간이 지날수록 격차가 벌어지는가 | |

### Anti-Loop 체크리스트

- [ ] Data Decay: 시간 지나면 데이터 무효화?
- [ ] Privacy Barrier: 유저가 데이터 수집 거부?
- [ ] Cost Escalation: 처리 비용 > 개선 가치?
- [ ] Quality Ceiling: 일정 수준 이상 개선 불가?
- [ ] Cold Start: 초기 데이터 부족으로 루프 미시작?

### Cold Start 해결 전략

```
Seed Data: 초기 데이터 수동 확보
Manual Override: 초기 사람이 직접 채움
Transfer Learning: 유사 도메인 데이터 활용
TK Injection: PM 암묵지로 초기 품질 확보
```

---

## Instructions

You are designing the **strategy** (biz-model + moat + growth-loop) for: **$ARGUMENTS**

`--focus` 파라미터에 따라 해당 섹션만 실행:
- `--focus biz-model` → 비즈니스 모델 섹션만
- `--focus moat` → 경쟁 해자 섹션만
- `--focus growth-loop` → 성장 루프 섹션만
- `--focus all` (기본값) → 세 섹션 순서대로 전체 실행

**Step 1 — 제품 개요 파악**
- 에이전트/제품명, 목적, 타겟 고객, 현재 단계(Pre-PMF/Growth/Expansion)

**Step 2 — 비즈니스 모델 설계** (biz-model 섹션)
- 가치 창출 정량화 (시간/비용/오류 절감)
- 비용 구조 및 CPE 계산
- 가격 모델 3개 이상 검토 후 선택
- 이윤율 > 70% 달성 가능 여부 확인

**Step 3 — 경쟁 해자 분석** (moat 섹션)
- 6가지 moat 유형 각각 점수
- 현재 Maturity Stage 판정
- 주요 moat 1-2개 선정 + Copy-Time 추정
- False moat 제거
- 4-Phase 구축 로드맵

**Step 4 — 성장 루프 설계** (growth-loop 섹션)
- 루프 유형 (Type A/B/C/D) 선택 및 근거
- Loop Strength 5요소 점수 (총점 목표 20+)
- Anti-loop 위험 식별 및 완화
- Cold Start 전략

**Step 5 — 통합 전략 요약**
```
비즈니스 모델: [가격 모델] — 목표 ACV $___
주요 Moat: [유형] — Copy-Time [N]개월
성장 루프: Type [X] — 자립 루프까지 [N]주
핵심 투자 우선순위: [1순위] → [2순위] → [3순위]
```

---

## Quality Gate

- [ ] 비즈니스 모델: CPE 계산 완료, 목표 Gross Margin > 70% 검토 (Yes/No)
- [ ] 해자 분석: 6가지 moat 유형 점수 매김, Copy-Time 18개월+ 주요 moat 선정 (Yes/No)
- [ ] 성장 루프: Loop Strength 총점 계산, Anti-loop 5개 체크 완료 (Yes/No)
- [ ] False moat 제거: 5가지 패턴 확인 (Yes/No)
- [ ] 통합 전략 요약: 세 섹션 결과가 서로 일관성 있게 연결됨 (Yes/No)

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---------|------|------|
| CPE가 목표 이윤율 초과 | Gross Margin < 50% | API 비용 최적화, 배치 처리, 또는 가격 인상 |
| Copy-Time < 18개월인 moat만 존재 | 모든 moat 점수 낮음 | Data Flywheel 또는 Workflow Lock-in 우선 투자 |
| Loop Strength < 15점 | 플라이휠이 약함 | Seed data 주입, 개선 주기 단축, 또는 루프 유형 재선택 |
| Cold Start 미해결 | 3개월 후 데이터 < 100건 | Transfer Learning 또는 TK 전문가 수동 투입 |

---

## Further Reading
- Alexander Osterwalder, *Business Model Generation* — Business Model Canvas
- Hamilton Helmer, *7 Powers* — Strategic power and competitive advantage
- Andrew Chen, *The Cold Start Problem* — Network effects and growth loops

## Contextual Knowledge (auto-loaded)

> 보조 파일이 존재할 때만 자동 로드됩니다. 파일이 없으면 건너뜁니다.

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
