---
description: "deliver/prd 스킬 wrapper — 15-section 통합 PRD 작성 (사용자/JTBD/결정/스코프/에이전트 사양/지표/가설/§15 QA Pool 포함)"
argument-hint: "[product or agent name]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /prd — Unified 15-section PRD Writer

Running for: **$ARGUMENTS**

이 커맨드는 `deliver/skills/prd/SKILL.md` 스킬을 즉시 호출합니다.

## 호출 흐름

1. `deliver/prd` 스킬을 `$ARGUMENTS`로 invoke.
2. 스킬이 Phase 1~5(Section 1-15)를 순차 작성.
3. 결과 산출물:
   - `docs/PRD.md` — 15-section PRD
   - `harness/QA_POOL.json` — §15 QA Pool (dev_roles 결정론 매핑)

## 입력 가이드

- `$ARGUMENTS` 가 없으면 스킬이 product name을 묻습니다.
- `interview-synthesis audit` 결과로 `harness/PERSONA_SPECS.json` 이 있으면 §15 QA Pool 작성에 자동 활용됩니다.

## 후속

- `harness/QA_POOL.json` 생성 후 `qa-checklist --mode adversarial` 실행 가능.
- 14-section만 필요하고 §15 QA Pool 미필요 시 `harness-build --step prd` 단축 경로 사용.
