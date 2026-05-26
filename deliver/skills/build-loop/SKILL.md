---
name: build-loop
description: "Run a full product build loop in one orchestrated session — discover → research → design → PRD → task decomposition → team-based implementation. Use when the user invokes /build, when an idea needs end-to-end execution from problem to shipped change, or when a feature crosses discover/architect/deliver boundaries that would otherwise require manual hand-offs."
argument-hint: "[idea or feature to build]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
model: sonnet
---

## Core Goal

- "/build" 한 번으로 **발견 → 리서치 → 설계 → PRD → 태스크 분해 → 팀 구현**을 한 루프에서 완성한다.
- 단계 간 hand-off 마찰 0건 — 각 단계의 산출물이 다음 단계의 입력으로 직결.
- 하네스 + 병렬 팀 + Ralph Loop 자율 모드를 자동 결합.

---

## 전체 루프 (6 단계)

```
1. Discover  (discover/opp-tree, assumptions, build-or-buy)
2. Research  (web/internal research, competitor 분석)
3. Design    (architect/orchestration (Hierarchical pattern 포함), memory-arch)
4. PRD       (deliver/prd + mermaid 정합성 게이트)
5. Decompose (deliver/parallel-team — 작업 분해 + worktree)
6. Implement (deliver/harness-design — 자율 모드 + 검증)
```

각 단계는 hplan 기존 스킬을 직렬 호출한다. 단계 간 산출물은 표준 경로에 저장.

---

## Trigger Gate

### Use This Skill When
- 사용자가 `/build` 또는 "발견부터 구현까지" 요청
- 아이디어가 PRD/스펙으로 정리되지 않은 초기 상태
- 단계 간 결정을 사용자가 매번 내리기보다 자동 진행을 원할 때
- 4명+ 팀 + 자율 모드를 사용한 큰 스코프 작업

### Route to Other Skills When
- 이미 PRD 있으면 → 5단계부터 시작 → `deliver/parallel-team`
- 빌드 게이트 통과 안 한 상태면 → `hplan/evidence-rubric` 먼저
- 한 단계만 필요하면 해당 스킬 직접 호출

### Boundary Checks
- 빌드 게이트(`hplan/evidence-rubric`) 미통과 시 자동 중단 — Stage 0 우선
- 자율 모드 진입 시 사용자 명시 승인 필요 ("ralph loop로 진행" 등)

---

## Instructions

You are running build-loop for: **$ARGUMENTS**

**Step 1 — Discover**
- `discover/opp-tree`로 기회 정의
- `discover/assumptions`로 리스크 가정 추출
- `discover/build-or-buy`로 자체 빌드 정당성 확인

**Step 2 — Research**
- 도메인 문서 / 경쟁사 / 기존 유사 시도 조사
- 산출물: `research/<idea>.md`

**Step 3 — Design**
- `architect/orchestration` (Hierarchical pattern 포함)으로 역할 설계 및 조율 패턴
- `architect/memory-arch`로 메모리 계층

**Step 4 — PRD**
- `deliver/prd`로 7섹션 PRD
- mermaid workflow + userflow 두 다이어그램 의무
- `scripts/validate-mermaid.py`로 정합성 검증 (P0-1 게이트)

**Step 5 — Decompose**
- `deliver/parallel-team`로 작업 분해
- 독립 작업 ≥2면 worktree 격리

**Step 6 — Implement**
- `deliver/harness-design`로 하네스 구성
- 자율 모드 승인 받았으면 Ralph Loop 활성
- 백업 + dry-run + pending_inputs 표준

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| 빌드 게이트 미통과 | hplan checkpoint != approved | 즉시 중단 → `/hplan-evidence` 안내 |
| PRD mermaid 정합성 실패 | validate-mermaid.py exit≠0 | Step 4 재실행, missing requirements 보강 |
| 작업 분해 시 파일 충돌 | parallel-team Step 2 fail | 직렬 처리로 fallback |
| 자율 모드 미승인인데 진입 | "ralph loop" 키워드 부재 | 사용자 확인 필요 → 단계별 컨펌 모드 |

---

## Quality Gate

- [ ] 6단계 모두 산출물이 표준 경로에 저장되었는가
- [ ] PRD mermaid 정합성 통과
- [ ] 빌드 게이트(hplan) 승인 상태
- [ ] 자율 모드 사용 시 사용자 명시 승인 기록
- [ ] 최종 산출물(코드 변경) + 변경 요약 제공

---

## Examples

### Good Example
**입력:** "/build 데일리 비용 모니터링 에이전트 만들어. ralph loop로 진행."

**기대 흐름:**
1. Discover: 비용 추적 OST → opp 1개 선정
2. Research: 기존 burn-rate 스킬 + GCP/Anthropic billing API 조사
3. Design: orchestration Hierarchical(트리거→집계→리포트), Cron 트리거, Telegram 출력
4. PRD: workflow + userflow 다이어그램 정합성 통과
5. Decompose: API 어댑터 / 집계 / 리포트 3개 worktree
6. Implement: 자율 모드, Ralph Loop, 백업, pending_inputs 누적 후 종료 시 일괄 전달

### Bad Example
**입력:** "/build 뭔가 만들어줘."

**왜 나쁜가:**
- 아이디어 미정 → Discover 진입 불가
- 사용자 의도 추정 위험

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Loop Stage Map
!`cat references/loop-stage-map.md 2>/dev/null || echo ""`
