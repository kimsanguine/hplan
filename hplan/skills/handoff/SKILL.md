---
name: handoff
description: "Export an approved Build Gate brief to a downstream coding ecosystem, or emit a read-only AI PM Handoff Profile v0 for growth planning. Use only after the Build Gate checkpoint and referenced decision agree."
argument-hint: "[brief.json] [--target spec-kit|kiro|gstack|claude|all] | [--root <project> [--output <file>] [--force]]"
allowed-tools: ["Read", "Write", "Bash"]
model: inherit
---

# Handoff — Build Gate → Downstream Coding Ecosystem

Running for: **$ARGUMENTS**

## Core Goal

- hplan은 단독 도구가 아니라 *전처리기*. Build Gate가 통과하면 결과물을 spec-kit / kiro / gstack / claude code 어느 곳으로든 export.
- 단일 brief JSON → 4개 생태계 동시 export 가능 (`--target all`).
- 각 생태계의 네이티브 컨벤션 (spec-kit의 `specs/NNN-slug/`, Kiro의 `.kiro/specs/`) 그대로 따름.
- AI PM Handoff Profile v0는 checkpoint와 decision log를 읽기만 하고 source-owned 상태와 opaque reference만 전달.

## Trigger Gate

### Use This Skill When

- Evidence + Product + Build Gate 모두 approved
- COGS sentinel GREEN 또는 CONDITIONAL_GO with mitigations
- 사용자가 명시적으로 "이제 Spec-Kit으로 가자" / "Kiro에서 구현" / "GStack /office-hours로"
- 팀 전체 onboarding — AGENTS.md + CLAUDE.md를 새 repo에 박을 때

### Route to Other Skills When

- Build Gate 미통과 → 거꾸로 가서 `cogs-sentinel`, `decision-log` 확인
- Export 후 spec-kit/kiro 안에서의 개별 task 분해 → 각 생태계 native tool
- Export 후 PRD shape 정교화 → `deliver/prd`

### Boundary Checks

- ❌ `hooks/gate_guard.py`가 활성화된 프로젝트에서 Build Gate 미승인 → handoff 호출 차단 (의도된 동작).
- ❌ 단일 target만 지정해도 다른 target은 영향 받지 않음 (idempotent per target).

## Inputs

```bash
python3 hplan/scripts/export_handoff.py brief.json --target all --root .
```

AI PM Handoff Profile v0를 stdout으로 내보내기:

```bash
python3 hplan/scripts/export_growth_handoff.py --root .
```

검증을 모두 통과한 뒤 저장하려면 `--output growth-handoff.json`처럼 상대 경로를 사용한다. 결과는 project root의 `harness/exports/ai-pm/` 아래에만 생성된다. absolute path, `..` traversal, symlink는 거부하며, 기존 안전 출력 파일을 의도적으로 교체할 때만 `--force`를 함께 사용한다.

```json
{
  "product_name": "SocialDraft",
  "problem": "1인 마케터가 SNS 게시글당 30-45분을 쓰는데 캠페인 데드라인을 자주 놓친다",
  "icp": "주 10건+ SNS 콘텐츠 직접 작성하는 1인 마케터 (현재 범용 AI 챗봇 수동 사용)",
  "jtbd": "When 미팅 끝나자마자, I want 액션 + 메일, so I can 같은 날 답신",
  "functional_requirements": [...],
  "acceptance_criteria": [...],
  "cogs_ceiling": "$2.70/paid user/month",
  "latency_budget": "p95 < 90초",
  "counter_position": "범용 AI 챗봇은 단발성 답변, SocialDraft는 브랜드 톤 학습 + 5개 동시 생성",
  "not_build": ["일반 음성 받아쓰기", "CRM first-class"],
  "mvp_slice": "Zoom 종료 → 1분 안에 액션 + 메일",
  "decision": "build"
}
```

## Steps

1. Confirm Build Gate decision is `build` or `CONDITIONAL_GO` in `decision-log`.
2. Confirm `cogs-sentinel` result is GREEN (or CONDITIONAL_GO with mitigations).
3. Run `export_handoff.py <brief.json> --target <target>`.
4. Verify generated files at `harness/exports/<target>/`.
5. Copy or symlink to actual project directory (spec-kit at repo root, kiro at `.kiro/`, etc.).

## Outputs

| Target | Path |
|---|---|
| spec-kit | `harness/exports/spec-kit/specs/NNN-slug/{spec,plan,tasks}.md` |
| kiro | `harness/exports/kiro/.kiro/specs/<slug>/{requirements,design,tasks}.md` |
| gstack | `harness/exports/gstack/office-hours-brief.md` |
| claude | `harness/exports/claude/AGENTS.md` + `CLAUDE.md` |
| AI PM Profile v0 | stdout (또는 `harness/exports/ai-pm/<output>` JSON 파일) |

## Verification

- [ ] All requested target files exist after run
- [ ] spec-kit `specs/NNN-slug/` uses auto-incremented NNN
- [ ] Kiro `.kiro/specs/<slug>/` exists with 3 files
- [ ] GStack brief includes "Next GStack Steps" section
- [ ] Claude AGENTS.md mentions COGS sentinel as build gate
- [ ] AI PM Profile는 approved checkpoint의 `decision_ref`가 같은 project의 decision을 가리킬 때만 생성
- [ ] AI PM Profile의 `status`는 decision log 원문을 유지하고 checkpoint/decision 원본 파일은 불변
