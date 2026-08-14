---
description: "Use when 사용자·JTBD·결정·스코프·에이전트 사양·지표·가설·§15 QA Pool을 포함한 15-section PRD가 필요합니다. deliver/prd wrapper는 design-shotgun과 roadmap sub-mode도 지원합니다."
argument-hint: "[product or agent name] | --mode design-shotgun | --mode roadmap [generate|rice|prioritize]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /prd — Unified 15-section PRD Writer

Running for: **$ARGUMENTS**

이 커맨드는 `deliver/skills/prd/SKILL.md` 스킬을 즉시 호출합니다.

## Instructions

1. `deliver/prd` 스킬을 `$ARGUMENTS`로 invoke.
2. 스킬이 Phase 1~5(Section 1-15)를 순차 작성.
3. 결과 산출물:
   - `docs/PRD.md` — 15-section PRD
   - `harness/QA_POOL.json` — §15 QA Pool (dev_roles 결정론 매핑)

## 모드 (sub-mode)

- 기본: 15-section PRD 작성.
- `--mode design-shotgun`: 기존 PRD의 §1+§11을 읽어 `harness/design-variants/`에 HTML 변형 4개 + comparison.md 생성.
- `--mode roadmap [generate|rice|prioritize]`: §6 Now/Next/Later 기반 로드맵. prd가 §6 canonical 소유자이며 roadmap은 그 sub-mode 다. generate=Mermaid gantt(`docs/ROADMAP.md`), rice=RICE 결정론 계산(`docs/rice-scores.md`), prioritize=Now/Next/Later 재분류 제안.

## 입력 가이드

- `$ARGUMENTS` 가 없으면 스킬이 product name을 묻습니다.
- `interview-synthesis audit` 결과로 `harness/PERSONA_SPECS.json` 이 있으면 §15 QA Pool 작성에 자동 활용됩니다.

## 후속

- `harness/QA_POOL.json` 생성 후 `qa-checklist --mode adversarial` 실행 가능.
- §15 QA Pool 생성을 다음 단계로 미루고 PRD 본문(Section 1-14)만 빨리 작성하려면 `harness-build --step prd` 단축 경로 사용. (단, `qa-checklist --mode adversarial`은 §15가 있어야 진입 가능 — 사후 `/prd` 재호출 필요)

## Output Format

기본 모드는 `docs/PRD.md`와 필요한 경우 `harness/QA_POOL.json`을 생성합니다. sub-mode는 해당 roadmap 또는 design-variant artifact와 다음 실행 경로를 반환합니다.
