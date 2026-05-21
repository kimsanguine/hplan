---
name: evidence-rubric
description: "Score a product idea against the 100-point evidence rubric before any PRD work. Eight axes: ICP specificity, recent painful event, current workaround, repetition, economic pain, switching trigger, MVP narrowness, and acquisition path to first 5 users. Returns build/interview/pivot/hold decision plus the specific axes that are weak. Use when a founder or PM is excited about an idea but evidence is thin, or before approving any spec-driven coding workflow (Spec-Kit, Kiro, GStack, Superpowers)."
argument-hint: "[idea to score]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
hooks:
  Stop:
    - type: command
      command: "python3 hplan/scripts/generate_report.py harness/evidence/last_input.json --json 2>/dev/null | tail -50 || true"
---

# Evidence Rubric — 100-Point Idea Scoring

Running for: **$ARGUMENTS**

## Core Goal

- 아이디어를 100점 루브릭으로 측정하여 "PRD 쓰기 전에 인터뷰가 더 필요한지" 명확한 신호를 만든다.
- 8개 축 각각의 점수 + 부족한 axis 목록을 반환해서, 다음 인터뷰에서 어떤 신호를 들어야 하는지 좁힌다.
- LLM의 직감 평가가 아닌 결정론적 스크립트(`generate_report.py`)로 점수화해 hand-wave를 차단한다.

## Trigger Gate

### Use This Skill When

- 사용자가 아이디어 한 문장 + 타깃 + 가설 + 대체재 + 기능 후보를 제시했을 때
- Spec-Kit / Kiro / GStack / Superpowers 워크플로우 진입 *전*
- 이미 인터뷰 노트가 있어 evidence strength를 객관적으로 측정하고 싶을 때
- "build로 가야 할까 interview를 더 해야 할까" 고민이 등장했을 때

### Route to Other Skills When

- 점수가 낮고 인터뷰 자체가 부족할 때 → `interview-synthesis` (hplan plugin)
- 이미 점유된 영역으로 보일 때 → `exclusions` (hplan plugin) check
- 점수는 충분한데 비용 구조가 불확실할 때 → `cogs-sentinel` (hplan plugin)
- 아이디어 발굴 단계로 돌아가야 할 때 → `opp-tree` (discover plugin)

### Boundary Checks

- ❌ 이 skill은 *아이디어 발굴*이 아니다 (그건 `discover/opp-tree`). 이미 아이디어가 있을 때만 호출.
- ❌ 이 skill은 PRD 작성을 *허락하지 않는다*. 점수가 충분해도 Product Gate + Build Gate를 거쳐야 한다.
- ❌ 점수만 높고 인터뷰가 0건이면 `interview` 결정이 강제된다.

## Inputs

JSON 파일 또는 인라인 입력:

```json
{
  "idea": "한 문장 가설",
  "target": "ICP 행동 기술 (인구통계 금지)",
  "hypothesis": "현재 상황",
  "alternatives": "대체재 콤마 구분",
  "features": "MVP 기능 후보 콤마 구분",
  "interview_notes": "인터뷰 발화 한 줄당 하나"
}
```

## Steps

1. Read `examples/good-01.md` to internalize the rubric.
2. If user input is freeform, structure it into the 6 fields above.
3. Save to `harness/evidence/last_input.json`.
4. Run `python3 hplan/scripts/generate_report.py <path> --json`.
5. Report score + decision + breakdown + missing axes.
6. If `decision == "interview"`, immediately route to `interview-synthesis` skill.
7. If `decision == "build"`, write the report to `harness/evidence/report.md` and route to `cogs-sentinel`.

## Outputs

- `harness/evidence/report.md` — markdown diagnosis
- `harness/evidence/last_input.json` — preserved input
- Decision: `build` (≥75 + interview_lines ≥ 2 + economic pain) / `interview` (≥55, or ≥75 without required conditions) / `pivot` (35–54) / `hold` (<35) — `build` requires mandatory `economic_pain` + 2+ interview lines; score alone is not sufficient

## Verification

- [ ] Score is a number 0–100.
- [ ] `missing` array lists axes scoring < 55% of max.
- [ ] If decision == `build`, `interview_notes` has ≥ 2 lines AND `combined` contains economic-pain keywords.

## Rubric (locked, 100 pts)

| Axis | Max | Why |
|---|---:|---|
| ICP specificity (behavior, not demographics) | 20 | Generic personas survive any pivot — they are noise |
| Recent painful event (last 30 days) | 15 | "I would use" → noise. "It happened yesterday" → signal |
| Current workaround | 15 | The cheapest sign of real demand: people pay time/money already |
| Repetition / frequency | 10 | One-time problems don't pay |
| Economic pain (money/risk/opportunity) | 15 | Time alone is too cheap to monetize |
| Switching trigger | 10 | "What would make you stop using your current tool?" |
| MVP narrowness | 10 | More than 3 features = no MVP |
| Acquisition path to first 5 users | 5 | If you can't name the next 5, build delay |
