---
name: exclusions
description: "Append-only Do-Not-Build registry. Each exclusion carries a reason, an owning competitor, and a reopen_trigger that says what evidence would unblock it. Future runs auto-check new ideas against the registry with Korean-aware char-bigram fuzzy match. Use when an idea overlaps with an established competitor (any established competitor in your space), when a previous pivot was killed, or when you want a project's institutional memory to survive across PMs."
argument-hint: "[add|check|list] <idea or phrase>"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

# Exclusions Registry — Do Not Build, with Reason

Running for: **$ARGUMENTS**

## Core Goal

- "지금 만들지 않는다"의 *영구 메모리*를 구축한다. 매 hplan run마다 휘발되지 않도록 `harness/exclusions.jsonl` append-only.
- 각 exclusion에 `reopen_trigger`를 명시 — 어떤 evidence가 잠금을 푸는지 사전 정의 → 같은 아이디어를 6개월 뒤에 다시 들고 와도 같은 자리로 도달.
- 새 아이디어가 들어오면 token Jaccard + char-bigram Jaccard 최대값으로 collision detect (한국어 형태소 미분리에도 강함).

## Trigger Gate

### Use This Skill When

- `evidence-rubric` 점수가 낮은데 영역이 이미 점유된 것 같을 때
- 명시적으로 "이건 안 만들 거다"를 기록하고 싶을 때
- 새 아이디어가 과거 pivot/hold와 겹치는지 확인하고 싶을 때
- 팀 onboarding — 새 PM이 들어왔을 때 "이건 왜 안 만들었나" 답변 제공

### Route to Other Skills When

- COLLISION 감지 + reopen_trigger 충족 가능 → `evidence-rubric` 재실행 (수정된 wedge로)
- COLLISION 감지 + reopen_trigger 충족 불가 → `decision-log` 에 `hold` 또는 `pivot` 기록
- CLEAR 결과 → Evidence Gate 정상 진행
- 경쟁 자체를 깊이 분석해야 할 때 → `architect/strategy --focus moat` 또는 `references/competitive-landscape-superpowers-gstack.md`

### Boundary Checks

- ❌ 영구 삭제 없음 (append-only). 잘못 추가하면 새 항목으로 supersede.
- ❌ Jaccard 0.40 threshold는 보수적 default. 한국어 1-2 단어 차이로 miss 가능 — verify 권장.

## Inputs

```bash
# Add
python3 hplan/scripts/exclusions_registry.py add "AI marketing copy generator" \
  --why "the existing incumbents 점유" \
  --reopen "엔터프라이즈 컴플라이언스 인터뷰 3건+" \
  --competitor "Incumbent A" --competitor "Incumbent B"

# Check
python3 hplan/scripts/exclusions_registry.py check "generic AI marketing copy tool"

# List
python3 hplan/scripts/exclusions_registry.py list
```

## Steps

1. Always `check` first when a new idea arrives — even before evidence-rubric.
2. If COLLISION + reopen unmet → STOP, route to decision-log (hold).
3. If COLLISION + reopen met → log the meeting evidence, proceed with caveat.
4. After every `pivot` or `hold` decision, call `add` so future runs don't repeat the mistake.

## Outputs

- `harness/exclusions.jsonl` (append-only)
- check returns `{verdict: "COLLISION"|"CLEAR", matches: [...]}` JSON

## Verification

- [ ] `add` returns an entry with `id`, `ts`, `reopen_trigger` non-empty.
- [ ] `check` returns COLLISION when overlap ≥ 0.40, CLEAR otherwise.
- [ ] `harness/exclusions.jsonl` is valid JSONL (one JSON object per line).
