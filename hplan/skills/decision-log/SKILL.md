---
name: decision-log
description: "Append-only build/interview/pivot/hold/CONDITIONAL_GO decision log with 3-6 month self-eval audit. Records every gate decision with score + reasons; later backfilled with outcome (shipped, killed, alive_no_revenue, pivoted, external_success) to compute hit_rate, false_holds, and missed_builds. The only PM gate skill that measures its own accuracy over time."
argument-hint: "[log|update|audit] <args>"
allowed-tools: ["Read", "Write", "Bash"]
model: inherit
---

# Decision Log — Self-Calibrating Build Gate

Running for: **$ARGUMENTS**

## Core Goal

- 모든 gate 결정을 `harness/decisions.jsonl`에 append-only로 기록 → **3-6개월 뒤 audit으로 hit_rate 측정**.
- false_hold (hold 했는데 외부에서 성공함) + missed_build (build 했는데 죽음)을 자동 추출 → rubric 보정 데이터.
- "내 게이트가 정확한가?"라는 질문에 답할 수 있는 유일한 PM skill.

## Trigger Gate

### Use This Skill When

- 매 build/interview/pivot/hold/CONDITIONAL_GO 결정 시 즉시 호출 (의무)
- 3-6개월 뒤 outcome이 확정됐을 때 backfill
- 분기별 self-review — "지난 분기 결정 중 정확했던 비율은?"

### Route to Other Skills When

- audit 결과 false_hold 다수 → `evidence-rubric`의 threshold 검토
- missed_build 다수 → Evidence Gate 통과 기준 강화
- decision = `hold` + 영구 사유 → `exclusions` add 같이 호출
- decision = `build` → `handoff` 로 라우팅

### Boundary Checks

- ❌ 영구 삭제 불가 (append-only). 잘못된 entry는 새 entry로 supersede.
- ❌ outcome backfill 없으면 audit이 의미 없음 — 잊지 말 것.
- ❌ `--from-hitl`은 이미 기록된 HITL id만 허용. 없는 id를 주면 거부된다 (끊어진 승격 링크 방지).
- ⚠️ `--root`는 `harness/` 자체가 아니라 그 **부모 디렉터리**를 가리킨다.

## Inputs

```bash
# Log a decision
python3 hplan/scripts/decision_log.py log \
  --project alpha-app --gate build --decision build --score 78 \
  --reason "5/5 강한 신호" --reason "COGS GREEN"

# Promote an earlier HITL decision into a gate decision
python3 hplan/scripts/decision_log.py log \
  --project alpha-app --gate build --decision build --score 78 \
  --from-hitl hitl-2026-07-28-ab12c

# Backfill outcome (3-6 months later)
python3 hplan/scripts/decision_log.py update --id dec-XXX --outcome shipped

# Audit — single project
python3 hplan/scripts/decision_log.py audit

# Audit — aggregate calibration across several projects
python3 hplan/scripts/decision_log.py audit --root ../alpha --root ../beta
```

## Steps

1. 결정이 내려진 직후 `log` 호출 (`--reason` 다중 사용 권장).
2. project name + gate (evidence/product/build) + decision 명시.
3. 매주/매월 `audit` 호출 — pending decisions 확인.
4. outcome이 확정되면 즉시 `update --id <id> --outcome <state>`.
5. 분기별 audit으로 hit_rate trend 점검.

## Outputs

- `harness/decisions.jsonl` (append-only)
- audit returns: `total, resolved, pending, by_decision, by_decision_outcome, hit_rate, false_holds, missed_builds, guidance`

## Decision vocabulary

| Decision | When |
|---|---|
| `build` | All gates credible |
| `CONDITIONAL_GO` | COGS CONDITIONAL + mitigations defined |
| `interview` | Evidence thin |
| `pivot` | Real problem, wedge broken |
| `hold` | Differentiation + economics both weak |

## Outcome vocabulary

| Outcome | Meaning |
|---|---|
| `shipped` | Product is live and used |
| `killed` | Project officially stopped |
| `alive_no_revenue` | Live but no paid users (signal trouble) |
| `pivoted` | Direction changed mid-flight |
| `external_success` | Someone else built it and succeeded — our hold was wrong |

## PMF 측정 연계

출시 후 30일 경과, 유료 전환 10명 도달, 또는 실측 p90 margin이 Build Gate 예측 대비 ±15pp 이상 차이날 때 다음 판정 기준을 decision-log에 함께 기록한다.

| 조건 | 판정 | 다음 action |
|------|------|------------|
| Day-30 retention ≥ 30% + COGS GREEN + strong_push ≥ 3 | PMF_SIGNAL | `evidence-rubric` 다음 사이클로 |
| 실측 p90 margin < 20% | ECONOMICS_MISS | `cogs-sentinel` 재산정 후 pricing 조정 |
| Day-7 retention < 20% | RETENTION_MISS | `ost` 재검토 (opportunities 재우선순위) |
| strong_push_quotes < 3 | EVIDENCE_THIN | 인터뷰 추가 수집 |
| 위 조건 복합 | PIVOT | decision-log pivot 기록 후 Evidence Gate 재시작 |

PMF 측정 결과를 `decision-log update --id <id> --outcome <verdict>` 로 backfill하면 hit_rate 계산에 포함된다.
