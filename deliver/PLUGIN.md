# deliver Plugin — Skills

> **공식 매니페스트**: `deliver/.claude-plugin/plugin.json`
> 이 파일은 사람이 읽기 위한 스킬 목록이다.

## Skills (8)

| 스킬 | 설명 | 주요 파라미터 |
|---|---|---|
| `agent-setup` | 에이전트 환경 설정 통합 — 7요소 인스트럭션 작성 + CLAUDE.md/AGENTS.md 구성 | `--focus instructions\|claude-md\|both` |
| `build-loop` | 빌드-테스트-수정 자율 반복 루프 | `[task brief]` |
| `conductor` | 태스크별 fresh subagent 디스패치 + 2단계 게이트(spec→quality) 반복 실행 | `[PRD path or delivery brief]` |
| `prd` | 15-section 통합 PRD 작성 — 사용자/JTBD/결정/스코프/에이전트 사양/지표/가설/QA Pool | `[product or agent name]` |
| `qa-checklist` | QA 체크리스트 실행 — 기능/성능/보안/접근성 검증 | `[target or scope]` |
| `respect` | UI/UX 디자인 시그니처 적용 — RESPECT.md 기반 3초 룰/다음 행동/social proof | `--mode brief\|full\|audit` |
| `sprint` | 스프린트 계획-실행-추적 통합 — WBS 분해, predicted.json 초기화, 진척 추적, 회고 | `--step plan\|init\|status\|retro` |
| `ui-validate` | UI 컴포넌트 및 화면 검증 — 디자인 토큰, 접근성, 모바일 레이아웃 | `[component or page]` |

## 통합 이력

- `agent-setup` ← agent-instructions + claude-md (2026-05-26)
- `sprint` ← delivery-plan + track (2026-05-26)
- `conductor` ← parallel-team 8역할 로스터 흡수 + agent-plan-review 4축 검증 참조 추가 (2026-05-26)
- `prd` ← ctx-budget 토큰 예산 가이드 + stakeholder-map 영향도 매트릭스 흡수 (2026-05-26)
- 삭제: agent-plan-review, ctx-budget, harness-design, parallel-team, stakeholder-map (내용 흡수 후)
