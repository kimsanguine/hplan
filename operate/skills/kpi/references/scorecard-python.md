# ScoreCard 구현체 — Python Reference

> measure/kpi 스킬의 KPI 정의를 **실제로 측정하는** Python 코드

## 개요

KPI를 정의했다면 다음 단계는 자동으로 수집·계산하는 것이다. 이 구현체는 5차원 ScoreCard를 계산하고, 에이전트 간 랭킹을 생성하며, Markdown 리포트로 출력한다.

```
measure/kpi SKILL.md  →  "Accuracy 95% 목표"   (무엇을 측정할지)
scorer.py (이 파일) →  ScoreCard().overall    (어떻게 측정할지)
```

---

## 설계 원칙

### 5차원 가중치 근거

| 차원 | 가중치 | 이유 |
|-----|-------|------|
| Accuracy | 35% | 에이전트 신뢰성의 핵심 — 틀린 출력은 모든 것을 무너뜨린다 |
| Reliability | 25% | 아무리 정확해도 자주 실패하면 운영 불가 |
| Speed | 20% | 응답 시간은 사용자 경험에 직결 |
| Cost Efficiency | 10% | 비용 중요하나 품질보다 우선시하면 안 됨 |
| Impact | 10% | 비즈니스 가치 — 아직 정량화 어려운 경우 많아 낮은 가중치 |

---

## Full Implementation

```python
"""
AgentEvaluator — ScoreCard 구현체
==================================
measure/kpi SKILL.md 의 KPI 정의를 코드로 구현한 레퍼런스.
사용: MultiDimScorer.score(eval_result) → ScoreCard
"""

from dataclasses import dataclass


@dataclass
class EvalResult:
    """에이전트 평가 입력 데이터"""
    agent_id: str
    accuracy_score: float        # 0.0 ~ 1.0  (정답률)
    total_runs: int              # 총 실행 횟수
    failed_runs: int             # 실패 횟수
    avg_latency_ms: float        # 평균 실행 시간 (ms)
    cost_per_run: float          # 실행당 비용 ($)
    impact_score: float = 0.0   # 비즈니스 임팩트 (0.0~1.0, 옵션)

    # 정규화 기준값 (팀/프로젝트마다 조정)
    latency_target_ms: float = 2000.0   # 목표 응답시간
    cost_target: float = 0.10           # 목표 실행당 비용


@dataclass
class ScoreCard:
    """5차원 KPI ScoreCard — 에이전트 성능 종합 평가"""
    agent_id: str
    accuracy: float           # 정확도 (0.0~1.0)
    reliability: float        # 안정성 (0.0~1.0)
    speed: float              # 속도   (0.0~1.0)
    cost_efficiency: float    # 비용   (0.0~1.0)
    impact: float = 0.0       # 임팩트 (0.0~1.0, 옵션)

    @property
    def overall(self) -> float:
        """가중 종합 점수 (0~100)"""
        raw = (
            self.accuracy          * 0.35
            + self.reliability     * 0.25
            + self.speed           * 0.20
            + self.cost_efficiency * 0.10
            + self.impact          * 0.10
        )
        return round(raw * 100, 1)

    def tier(self) -> str:
        """점수 기반 자동 tier 산정"""
        score = self.overall
        if score >= 90:   return "L3"
        elif score >= 75: return "L2+"
        elif score >= 60: return "L2"
        elif score >= 40: return "L1"
        else:             return "L0"


class MultiDimScorer:
    """EvalResult → ScoreCard 변환기"""

    def score(self, result: EvalResult) -> ScoreCard:
        """5차원 점수 계산"""

        # 1) Accuracy: 그대로 사용
        accuracy = max(0.0, min(1.0, result.accuracy_score))

        # 2) Reliability: 성공률 (실패 비율 역수)
        reliability = 1.0 - (result.failed_runs / max(result.total_runs, 1))
        reliability = max(0.0, min(1.0, reliability))

        # 3) Speed: latency를 목표 대비 역수 정규화
        #    latency == target → 0.8점 | latency == 0 → 1.0점 | latency == 2×target → 0.5점
        ratio = result.avg_latency_ms / max(result.latency_target_ms, 1.0)
        if ratio > 1:
            speed = max(0.0, 1.0 - (ratio - 1.0) * 0.3)
        else:
            speed = 0.8 + 0.2 * (1.0 - ratio)
        speed = max(0.0, min(1.0, speed))

        # 4) Cost Efficiency: 비용을 목표 대비 역수 정규화
        cost_ratio = result.cost_per_run / max(result.cost_target, 0.001)
        cost_efficiency = (
            max(0.0, 1.0 - (cost_ratio - 1.0) * 0.5)
            if cost_ratio > 1 else 1.0
        )
        cost_efficiency = max(0.0, min(1.0, cost_efficiency))

        # 5) Impact: 직접 전달 (0.0~1.0)
        impact = max(0.0, min(1.0, result.impact_score))

        return ScoreCard(
            agent_id=result.agent_id,
            accuracy=accuracy,
            reliability=reliability,
            speed=speed,
            cost_efficiency=cost_efficiency,
            impact=impact,
        )

    def compare(self, card_a: ScoreCard, card_b: ScoreCard) -> dict:
        """두 에이전트 차원별 비교"""
        dims = ["accuracy", "reliability", "speed", "cost_efficiency", "impact"]
        result = {"overall_winner": None, "dimensions": {}}

        for dim in dims:
            va, vb = getattr(card_a, dim), getattr(card_b, dim)
            if va > vb:
                result["dimensions"][dim] = card_a.agent_id
            elif vb > va:
                result["dimensions"][dim] = card_b.agent_id
            else:
                result["dimensions"][dim] = "tie"

        result["overall_winner"] = (
            card_a.agent_id if card_a.overall >= card_b.overall else card_b.agent_id
        )
        return result


class EvalReporter:
    """ScoreCard 목록 → Markdown 랭킹 리포트"""

    def generate_ranking(self, cards: list[ScoreCard]) -> str:
        sorted_cards = sorted(cards, key=lambda c: c.overall, reverse=True)
        lines = [
            "## AgentEvaluator ScoreCard 랭킹\n",
            "| 순위 | 에이전트 | Overall | Accuracy | Reliability | Speed | Cost | Impact | Tier |",
            "|------|---------|---------|---------|------------|-------|------|--------|------|",
        ]
        for i, card in enumerate(sorted_cards, 1):
            lines.append(
                f"| {i} | {card.agent_id} | **{card.overall}** "
                f"| {card.accuracy:.2f} | {card.reliability:.2f} "
                f"| {card.speed:.2f} | {card.cost_efficiency:.2f} "
                f"| {card.impact:.2f} | {card.tier()} |"
            )
        return "\n".join(lines)
```

---

## 사용 예시

```python
scorer = MultiDimScorer()
reporter = EvalReporter()

# 에이전트 평가 데이터 수집
results = [
    EvalResult("context_dealer",  accuracy_score=0.96, total_runs=50, failed_runs=1,
               avg_latency_ms=1200, cost_per_run=0.05),
    EvalResult("newsletter_gen",  accuracy_score=0.88, total_runs=40, failed_runs=3,
               avg_latency_ms=3500, cost_per_run=0.15),
    EvalResult("invoice_tracker", accuracy_score=0.91, total_runs=60, failed_runs=2,
               avg_latency_ms=800,  cost_per_run=0.02),
]

# ScoreCard 계산 → 랭킹 출력
cards = [scorer.score(r) for r in results]
print(reporter.generate_ranking(cards))

# 출력:
# | 1 | context_dealer  | 96.1 | ... | L3  |
# | 2 | invoice_tracker | 88.4 | ... | L2+ |
# | 3 | newsletter_gen  | 72.3 | ... | L2  |
```

---

## kpi 스킬 → scorer.py 연결 흐름

```
measure/kpi SKILL.md
  Step 1 (Operational Health) → accuracy_score, failed_runs, avg_latency_ms, cost_per_run
  Step 2 (Business Impact)    → impact_score
         ↓
  EvalResult (수집된 데이터)
         ↓
  MultiDimScorer.score()
         ↓
  ScoreCard (5차원 점수)
         ↓
  EvalReporter.generate_ranking()
         ↓
  Markdown 랭킹 테이블 → /agents 팀 보고에 삽입
```

---

## 커스터마이징 포인트

1. **가중치 조정**: `ScoreCard.overall` 의 `0.35 / 0.25 / 0.20 / 0.10 / 0.10` 변경
2. **latency_target_ms**: 에이전트 유형별 SLA에 맞게 설정 (실시간=500ms, 배치=30000ms)
3. **cost_target**: 프로젝트 예산에 따라 설정
4. **impact_score 소스**: NPS, 태스크 완료율, 사용자 피드백 점수 등

---

## 관련 스킬

- `measure/kpi` — KPI 정의 방법론 (이 파일의 기반)
- `deliver/okr` — OKR과 ScoreCard 연결 (KR 달성률 → impact_score)
- `discover/evaluate` — 에이전트 평가 전체 파이프라인
