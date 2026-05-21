---
description: "Run the full craft-lint chain — validate-craft-lint.py (정적 메타데이터·cross-ref) → hierarchy-rules (런타임 픽셀 측정 via Playwright) → motion-language (CSS / framer-motion 일관성) → ui-drift-detect (5+ 화면 시각 diff). Single command for pre-ship design integrity. Use when committing UI code, before push, or as a CI gate."
argument-hint: "[url or src directory]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /craft-lint — Full Design Integrity Chain

Single command chaining all craft validation. Stops early if any layer fails.

## Instructions

You are running craft-lint for: **$ARGUMENTS**

### Step 1 — 정적 검증 (validate-craft-lint.py --strict)

```bash
python3 scripts/validate-craft-lint.py --strict
```

`--strict` 명시 — DESIGN.md 누락 등 warning 도 exit 1 로 차단 (defense in depth, v0.8.2 Codex 검수 반영).

- RESPECT.md 필수 필드 검증
- DESIGN.md cross-reference
- three_second_rule 금지어 + 단어 수
- hierarchy_rules color_ratio 합 = 100
- next_action.primary 1개
- exit 0 → 다음 단계, exit 1 → fail loud

### Step 2 — hierarchy-rules 런타임 측정

`hierarchy-rules` 호출:
- Playwright 1440×1080 캡처
- 5 룰 + WCAG AA 측정
- 모두 pass → 다음, 1개 fail → fix 권유

### Step 3 — motion-language 스캔

`motion-language` 호출:
- src 디렉터리 transition/easing 추출
- RESPECT 명세와 비교
- drift 0 → 다음, drift ≥ 1 → fix 권유

### Step 4 — ui-drift-detect (5+ 화면 있을 때만)

`ui-drift-detect` 호출 (선택):
- 5+ 화면 시각 diff
- baseline 대비 drift 측정
- multi-dim drift 화면 식별

### Step 5 — 종합 verdict

- 모두 pass → craft-lint OK → respect-checkpoint 권유
- 1개 fail → fix 권유 + 어느 레이어 / 어느 element

## Output Format

```
VERDICT: PASS / FAIL

[1/4] validate-craft-lint.py     <pass / N errors>
[2/4] hierarchy-rules (runtime)  <pass / [fold|type|color|whitespace|cta|wcag] fail>
[3/4] motion-language            <drift 0 / N drift in M files>
[4/4] ui-drift-detect            <skip (<3 화면) / pass / drift in M screens>

Next: <ship 권유 + /respect-check 호출 / 어느 레이어 fix>
```

## Failure Handling

| 실패 | 대응 |
|---|---|
| RESPECT.md 부재 | /craft-init 권유 fail loud |
| Playwright 미설치 | Step 2/4 skip + warning, 1/3 만 진행 |
| URL 입력 안 됨 (Step 2 필요) | 정적 검증 (Step 1+3) 만 진행 |
| Step 1 exit 1 | 즉시 fail, 다음 단계 skip |
