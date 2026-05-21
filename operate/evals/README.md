# hplan evals

## Trigger eval (v0.7)

Trigger eval은 각 SKILL.md의 description이 "이 쿼리에는 이 skill이 발동해야 한다"는 자연어
판정을 얼마나 정확하게 유도하는지 측정한다. Claude Code의 skill auto-load 정확도 대리 지표.

### 데이터셋

- `trigger-evals.json` — 31 skills / 124 queries (should_trigger 62 + should_not 62)
  - v0.7 추가: harness-design, parallel-team, build-loop, agent-portfolio, scorecard-5axis,
    weekly-rollup, cross-team-routing (각 4 queries)
- `baseline-results.json` — v0.6 측정 (24 skills / 96 queries / 97.9% pass rate, Haiku 4.5)

### 실행 방법

```bash
# 사전 준비
export ANTHROPIC_API_KEY=...
pip install anthropic

# 카탈로그 확인 (LLM 호출 없음)
python3 evals/run_trigger_evals.py --dry-run

# 전체 평가 (Haiku 4.5, 1 run per query, 약 2~3분 소요)
python3 evals/run_trigger_evals.py

# 안정 평가 (다회 실행 후 다수결 — 비결정성 제어)
python3 evals/run_trigger_evals.py --runs-per-query 3 --output evals/baseline-results-v0.7.json
```

### 평가 모델 권고

| 모델 | 용도 | 비용 |
|---|---|---|
| `claude-haiku-4-5-20251001` (기본) | 빠른 회귀 평가, CI용 | 매우 저렴 |
| `claude-sonnet-4-6` | 정밀 평가, 분기 단위 | 중간 |
| `claude-opus-4-7` | 최종 검증, 신규 스킬 도입 시 | 비쌈 |

### 산출물 해석

```jsonc
{
  "summary": {
    "total_skills": 31,
    "total_queries": 124,
    "total_passed": 121,
    "pass_rate": "121/124 (97.6%)",
    "elapsed_seconds": 158.3,
    "model": "claude-haiku-4-5-20251001",
    "runs_per_query": 1
  },
  "skills": [ /* skill별 results 배열 */ ]
}
```

- `pass_rate`가 v0.6 baseline(97.9%) 대비 큰 폭으로 떨어지면 신규 스킬 description이
  기존 스킬과 겹치는지 점검 (특히 `agent-portfolio` ↔ `kpi`, `harness-design` ↔ `orchestration`)
- 한 스킬에서 should_trigger=true 쿼리가 모두 실패하면 description이 너무 추상적
- should_trigger=false 쿼리가 자주 false-positive하면 description이 너무 넓음

### v0.7 평가 일정 (pending)

- 본 release는 runner와 시드만 제공한다. 실제 baseline-results-v0.7.json 산출은
  운영자가 본인 ANTHROPIC_API_KEY로 실행 후 PR/commit으로 추가한다.
- baseline 격차(±2%p 이상)가 발견되면 v0.7.1 patch로 description 수정.

## 기타 평가 자료

- `evals.json` — Phase 3 representative eval 정의 (5 skills × 2 prompts, with_skill vs without_skill 비교)
- `pm-framework-baseline.json` — pm-framework 특화 평가
- `workspace/` — Phase 3 실측 산출물 (iteration-1)
