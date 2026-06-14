---
name: ost
description: "Generate a Teresa Torres-style Opportunity Solution Tree as docs/OPPORTUNITY_TREE.md with auto-rendered Mermaid diagram. Forces the discipline: opportunities are unmet user needs (not solutions), each solution links to exactly one experiment with a decision rule, and opportunities backed by fewer than 3 strong-Push interviews are flagged or pruned. Use as the Product Gate's primary artifact, after interview-synthesis has tagged enough strong-push quotes."
argument-hint: "[path to ost.json]"
allowed-tools: ["Read", "Write", "Bash"]
model: inherit
---

# Opportunity Solution Tree — Product Gate Primary Artifact

Running for: **$ARGUMENTS**

## Core Goal

- Teresa Torres OST를 PM 라이프사이클의 1급 artifact로 승격 — `docs/OPPORTUNITY_TREE.md` + Mermaid 자동 생성.
- "opportunities ≠ solutions" 규율 강제 — 미충족 사용자 니즈로만 표현.
- 각 solution은 정확히 1개의 experiment + 1개의 decision_rule 가져야 함 → no orphan ideas.

## Trigger Gate

### Use This Skill When

- `interview-synthesis`에서 5/3 패턴 PROCEED 통과 후
- Product Gate 진입 시 첫 산출물
- Opportunity 우선순위 재검토 시
- Stakeholder에게 "왜 이걸 만드는지" 시각화 필요할 때

### Route to Other Skills When

- 탐색 자체가 부족할 때 → `discover/opp-tree` (exploration mode)
- OST 완성 후 PRD shape 정의 → `deliver/prd`
- 가설 깊이 검증 → `discover/assumptions` (V/F/R/E 4축)
- 운영 메트릭 정의 → `operate/metrics-design --step north-star`

### Boundary Checks

- ❌ Solutions를 opportunities로 작성 금지 — 자동 검출은 못 함, 명시적 규율.
- ❌ Evidence count < 3인 opportunity는 "parking lot"으로 표시되거나 pruned.
- ❌ Solution 없이 opportunity만 나열하는 건 OST 아님 — 그건 problem list.

## Inputs

```json
{
  "outcome": "Solo PM closed-won rate +25% within 90 days",
  "opportunities": [
    {
      "name": "솔로 PM이 미팅 직후 결과물을 못 만든다",
      "evidence_count": 3,
      "solutions": [
        {
          "name": "60초 액션 아이템 초안",
          "experiment": "Concierge for 5 ICP",
          "decision_rule": "5/5가 그대로 사용"
        }
      ]
    }
  ]
}
```

## Steps

1. `interview-synthesis audit` 결과의 `persons_with_strong_push`를 opportunity의 evidence로 사용.
2. opportunity는 "X가 Y를 못 한다" 형태 — solution 아님.
3. 각 solution마다 `experiment` + `decision_rule` 명시.
4. `python3 hplan/scripts/ost_generator.py ost.json --out docs/OPPORTUNITY_TREE.md`.
5. 생성된 Mermaid diagram을 stakeholder review에 사용.

## Outputs

- `docs/OPPORTUNITY_TREE.md` — Mermaid + table + rules
- (선택) `harness/product-gate/ost.json` — input 보존

## Verification

- [ ] outcome 1개 (measurable, time-bounded)
- [ ] opportunity 2+ — 각각 "사용자가 무엇을 못 한다"
- [ ] 모든 solution은 opportunity 하나에 연결 + experiment + decision_rule
- [ ] evidence_count < 3 opportunity는 "parking lot" 표시 또는 제거
