---
description: "Full build pipeline — evidence gate, product gate, COGS gate, PRD writing, OKR design, sprint planning, design system setup, spec compliance review (--step spec-review), quality gate (--step quality-gate), progress tracking, and scope guard. Use when committing to building a product or agent, running individual gate steps, checking spec compliance after implementation, or managing the full build lifecycle."
argument-hint: "[brief] [--step evidence|product|cogs|prd|okr|sprint|craft-init|craft-lint|track-init|track-status|track-retro|scope|spec-review|quality-gate]"
allowed-tools: ["Read", "Write", "Bash"]
---

# /harness-build

> 빌드 전체 파이프라인 — 게이트 → PRD → 스프린트 → 설계 → 추적

## Routing

`$ARGUMENTS`에서 `--step` 플래그를 파싱한다.

| 플래그 | 실행 범위 |
|--------|-----------|
| `--step evidence` | Evidence Gate만 실행 |
| `--step product` | Product Gate만 실행 |
| `--step cogs` | COGS Sentinel만 실행 |
| `--step prd` | PRD 작성만 실행 (checkpoint 승인 필요) |
| `--step okr` | OKR 설계만 실행 |
| `--step sprint` | Sprint 플래닝만 실행 |
| `--step craft-init` | 디자인 시스템 초기화만 실행 |
| `--step craft-lint` | 디자인 품질 검사만 실행 |
| `--step track-init` | 진척 추적 초기화만 실행 |
| `--step track-status` | 라이브 진척 현황만 실행 |
| `--step track-retro` | 회고 및 TK 추출만 실행 |
| `--step scope` | 범위 가드 검사만 실행 |
| `--step spec-review` | Phase 7(Spec Compliance Review)만 실행 |
| `--step quality-gate` | Phase 8(Quality Gate)만 실행 |
| 플래그 없음 | Phase 1(evidence) → 2(product) → 3(COGS) → 4(PRD+sprint) → 7(spec-review) → 8(quality-gate) 전체 실행 |

플래그 뒤의 나머지 텍스트가 대상 브리프입니다.

---

## Instructions

You are running the **hplan Build Pipeline** for: **$ARGUMENTS**

---

### Phase 1 — Evidence Gate (`--step evidence`)

> **왜**: 아이디어를 코드로 만들기 전, 실제 고객 고통이 존재하는지 먼저 확인합니다.
> 이 단계를 건너뛰면 아무도 원하지 않는 것을 완벽하게 만드는 문제가 생깁니다.

#### Step 1-1: Exclusion Collision Check

```bash
python3 hplan/scripts/exclusions_registry.py check "$TARGET"
```

- **COLLISION** (reopen_trigger 미충족) → 즉시 STOP. COLLISION 상세 + reopen_trigger 조건 출력.
- CLEAR → 다음 단계 진행.

#### Step 1-2: Input 구조화

다음 항목을 수집한다: `idea`, `icp_segment`, `recent_event`, `workaround_tool`, `monthly_cost_estimate`, `alternatives`, `interview_notes` (줄당 1개), `interview_count`.

#### Step 1-3: 100-Point Evidence Rubric

`evidence-rubric` 스킬 적용 — `scripts/generate_report.py` 실행. 점수 + 취약 축 캡처.
> **Evidence Rubric**: 아이디어 신뢰도를 8개 축·100점으로 채점하는 기준표.
> GO(75+) / INVESTIGATE(55-74) / HOLD(55 미만) 3단계로 판정합니다.

#### Step 1-4: Interview Synthesis

`interview_notes`가 부족하거나 `decision == "interview"`이면 `interview-synthesis` 스킬 적용. AI export 인제스트 또는 신규 인터뷰 계획. 5/3 strong-Push 룰 감사.

#### Step 1-5: Evidence Decision

| 점수 | 추가 조건 | 결정 | 의미 |
|------|----------|------|------|
| ≥ 75 | interview_lines ≥ 2 AND economic pain 있음 | `build` | Product Gate로 진행 |
| ≥ 75 | interview_lines < 2 OR economic pain 없음 | `interview` | 점수 강하지만 증거 부족 |
| 55–74 | — | `interview` | 인터뷰 추가 필요 |
| 35–54 | — | `pivot` | 문제 정의 재검토 |
| < 35 | — | `hold` | STOP — 증거 불충분 |

**Anti-gaming**: `build` 판정에는 독립적인 인터뷰 라인 2개 + economic pain 키워드 필수.

**결정별 다음 3 액션**:
- `build` → Phase 2(Product Gate) 진행 · COGS 확인 · `decision-log` 스킬로 기록
- `interview` → 최저 점수 축 기반 인터뷰 질문 3개 도출 → interview-synthesis → 재점수
- `pivot` → ICP 재정의 (pain이 구체적·최근·경제적인가?) → 문제 재프레이밍
- `hold` → `decision-log` 기록 → exclusions에 `reopen_trigger` 추가 → 하위 작업 중단

**출력**: 제외 판정 / 루브릭 점수 N/100 / 인터뷰 감사 / 결정 / 다음 게이트

*`--step evidence` 선택 시 여기서 종료.*

---

### Phase 2 — Product Gate (`--step product`)

> **왜**: 기술적으로 만들 수 있는지(Feasibility)가 아니라
> 만들어야 하는 이유(Desirability)를 확인하는 단계입니다.

<HARD-GATE name="evidence">
Evidence Gate PASS 없이 이 게이트 진입 금지.
아래 중 하나가 없으면 즉시 STOP:
  - `harness/build-gate/decision_log.jsonl` 에 gate=evidence 항목
  - 또는 인터뷰 3건 이상 / 행동 증거가 이 대화에 이미 제시됨

검증:
```bash
python3 hplan/scripts/decision_log.py list | grep '"gate": "evidence"' | grep '"decision"' | tail -1
```
비어 있으면 STOP — "`--step evidence [idea]` 먼저 실행하세요." 출력.
</HARD-GATE>

#### Step 2-1: Outcome 확인

측정 가능하고 기한 있는 결과를 명시한다. 예: "Solo PM 클로즈율 +25% (90일 내)". "돈을 번다" 같은 모호한 결과 금지.

#### Step 2-2: Opportunity Solution Tree

`ost` 스킬 적용 — `docs/OPPORTUNITY_TREE.md`를 Mermaid로 생성. 각 기회에 `evidence_count ≥ 3` strong-Push 인터뷰 확인.

#### Step 2-3: User Journey + Sitemap

`hplan/references/product-planning.md` 참조. 여정이 Discover → Start → Core → Review → Pay를 포함하고, empty/loading/failed/blocked/paid/review 상태가 정의되어 있는지 확인.

#### Step 2-4: Design Pointer

`hplan/references/design-gate.md` 참조. `DESIGN.md` 방향성(mood, hierarchy, component rules, state rules, mobile checklist)이 존재하는지 확인.

#### Step 2-5: Hypothesis Tree

OST의 모든 솔루션에 experiment + decision_rule이 있는지 확인.

**출력**: OST 상태 / Journey+sitemap 확인 / Design pointer 확인 / 다음 게이트

*`--step product` 선택 시 여기서 종료.*

---

### Phase 3 — COGS Gate (`--step cogs`)

> **왜**: 기능이 좋아도 비용 구조가 맞지 않으면 지속 불가능합니다.
> 이 단계에서 API 비용 대비 수익 마진을 사전에 검증합니다.

> **COGS (Cost of Goods Sold)**: 서비스 1건을 제공하는 데 드는 직접 비용.
> AI 에이전트에서는 주로 LLM API 호출 비용을 의미합니다.

#### Step 3-1: Input 수집

Provider, model, tokens_in, tokens_out, calls_per_user_month, ARPU, paid_conversion, free_abuse_multiplier, target_gross_margin (기본값 0.70).

#### Step 3-2: COGS Sentinel 실행

```bash
python3 hplan/scripts/cogs_sentinel.py \
  --provider <p> --model <m> \
  --tokens-in <ti> --tokens-out <to> \
  --calls-per-user-month <c> \
  --arpu <a> --paid-conversion <pc> \
  --free-abuse-multiplier <fa>
```

#### Step 3-3: 결정 해석

| 결정 | 의미 | 다음 행동 |
|------|------|----------|
| **GREEN** | p90 마진 목표 달성 | Phase 4(PRD)로 진행 |
| **CONDITIONAL_GO** | 조건부 통과 — 명시된 경감 조치 필요 | 경감 조치 나열 → 사용자 승인 요청 |
| **RED** | 경제 모델 불성립 | `exclusions` 스킬로 실패한 pricing wedge 기록 |

> **CONDITIONAL_GO**: "지금 진행하되, 명시된 조건을 반드시 해소하며 진행"을 의미합니다.
> 조건이 해소되지 않으면 다음 게이트에서 차단됩니다.

#### Step 3-4: Checkpoint 작성

> **Checkpoint**: `harness/build-gate/checkpoint.json`이 존재해야 PRD 작성이 허용됩니다.
> hook이 이 파일의 유무로 다음 단계 진입을 물리적으로 제어합니다.

`build` 또는 `CONDITIONAL_GO`이면 `harness/build-gate/checkpoint.json` 작성 → `gate_guard.py` 해제:

**GO 스키마**:
```jsonc
{
  "status": "approved",
  "decision": "GO",
  "decision_id": "dec-YYYY-MM-DD-XXXXX"
}
```

**CONDITIONAL_GO 스키마**:
```jsonc
{
  "status": "approved",
  "decision": "CONDITIONAL_GO",
  "decision_id": "dec-YYYY-MM-DD-XXXXX",
  "conditions": ["조건1", "조건2"],
  "allowed_paths": ["specs/NNN-", "docs/DESIGN.md"],
  "expires_at": "YYYY-MM-DD"
}
```

CONDITIONAL_GO 시 `harness/STATE.md` 자동 생성 (게이트 상태 anchor) + `harness/PROGRESS.md` 마일스톤 템플릿 작성.

**출력**: 호출당 비용 p50/p90 / 월간 COGS/유저 / Gross margin / GREEN·CONDITIONAL_GO·RED 판정

*`--step cogs` 선택 시 여기서 종료.*

---

### Phase 4 — PRD + Sprint (`--step prd`, `--step sprint`, `--step okr`, 또는 전체 플로우 자동 실행)

> **왜**: 게이트를 통과한 아이디어를 팀이 실행할 수 있는 형태로 변환합니다.
> PRD는 "무엇을 만들 것인가"의 약속, Sprint Plan은 "첫 주에 무엇을 할 것인가"의 계획입니다.

> **PRD Living Document**: PRD는 단계별로 발전하는 살아있는 문서다.
> - `v0.1` — Signal Gate + harness-build (이 단계): 사용자·문제·범위·에이전트 사양 초안
> - `v0.2` — harness-plan 완료 후: 오케스트레이션·Tier·메모리·라우팅 결정 반영
> - `v0.3` — harness-operate 피드백 후: KPI·실패 모드·개선 계획 반영
>
> 각 버전은 파일 첫 줄 헤더 `<!-- hplan PRD | vX.X | ... -->` 으로 추적된다.

<HARD-GATE>
`--step prd`, `--step okr`, `--step sprint` 또는 Phase 4 전체 자동 실행 전에 아래를 반드시 확인한다.

```bash
python3 -c "
import json, sys
from pathlib import Path
cp = Path('harness/build-gate/checkpoint.json')
if not cp.exists():
    print('BLOCKED: harness/build-gate/checkpoint.json 없음 — /harness-build --step product 로 Gate 심사 먼저 실행')
    sys.exit(1)
data = json.loads(cp.read_text())
if data.get('status') != 'approved':
    print(f'BLOCKED: Gate 상태 {data.get(\"status\")} — approved 상태 필요')
    sys.exit(1)
print('Gate OK:', data.get('decision'), '|', data.get('project', ''))
"
```

위 스크립트가 exit 0으로 끝나야만 PRD 작성을 진행한다. exit 1이면 즉시 중단하고 안내 메시지를 출력한 후 멈춘다.
</HARD-GATE>

Gate 승인 후 checkpoint.json이 작성되면 자동으로 Phase 4로 진행한다.

#### Pre-Step 4-0: Criteria First (G1) — PRD 작성 전 필수

**PRD 섹션 작성 전에 성공 기준(Section 12 초안)을 먼저 정의한다.**

> 기능을 먼저 쓰면 기능이 목표를 정의한다. 기준이 먼저여야 기능이 기준을 섬긴다.

1. **North Star Metric 초안** — 측정 가능·기한 있는 한 문장. 예: "Solo PM의 클로즈율 +25% (90일)"
2. **Business KR 1–2개 초안** — `지표 · 현재 기준값 → 목표값` 형식
3. **Anti-Metric 1개** — "이 지표가 올라가면 목표를 잘못 추구하는 것"
4. 사용자 확인 후 Phase A (Section 1–3) 작성 시작

이 기준은 Section 4 (결정 옵션 매트릭스)와 Section 5 (Out-of-Scope)의 **필터**로 작동한다.  
"이 기능이 North Star에 기여하는가?" 질문에 Yes인 것만 Phase B에 포함한다.

---

#### Step 4-1: PRD 작성 (`--step prd`)

`docs/PRD.md`를 아래 15섹션으로 작성한다. 각 섹션은 3–8개 bullet 기준.

**PRD 버전 헤더** — 파일 첫 줄에 반드시 추가한다:

```
<!-- hplan PRD | v0.1 | {YYYY-MM-DD} | Signal Gate 통과 -->
```

이후 architect 결정이 반영될 때마다 헤더의 버전(v0.2, v0.3…)과 날짜를 업데이트한다.

**Phase A — 사용자·문제·가치 (Section 1-3)**

| # | 섹션 | 필수 내용 |
|---|------|---------|
| 1 | ICP + 페르소나 | 페르소나 2–3개: 이름·역할·고통·도달 채널 |
| 2 | JTBD | Switch Interview 4 Forces (Push/Pull/Anxiety/Habit), Job 1–3개 |
| 3 | 핵심 문제 + 10배 가치 | 정량화: 절감 시간/비용 또는 새로운 가능성 |

*Checkpoint A — "5명 사랑 인터뷰에 갈 수 있는가?" 확인 후 사용자 승인 대기.*

**Phase B — 결정·범위 (Section 4-6)**

| # | 섹션 | 필수 내용 |
|---|------|---------|
| 4 | 결정 옵션 매트릭스 | 최소 5개 결정 × 옵션 A/B/C + 재검토 시점 |
| 5 | Out-of-Scope | 최소 5개 — "절대 안 만드는 것" + 이유 + 재검토 신호 |
| 6 | Now/Next/Later | Wave 1 (Day 1–60) · Wave 2 · Wave 3 + COGS p50/p90 |

*Checkpoint B — "Wave 1이 60일 안에 가능한가? COGS가 감당 가능한가?" 확인.*

**Phase C — 에이전트·실행 사양 (Section 7-11)**

| # | 섹션 | 필수 내용 |
|---|------|---------|
| 7 | Role + Goal + Anti-Goals | Anti-Goals 최소 3개 (도메인 룰/데이터 정책/법적 책임) |
| 8 | Tools & Integrations | 호출 제한 mandatory |
| 9 | Memory & Context | 3-tier (Working/Long-term/Procedural) |
| 10 | Trigger & Execution Flow | Cron/Event/Manual/Pipeline 명시 + Step-by-Step |
| 11 | Output Specification | 채널/형식/길이/언어/톤 + 실제 출력 샘플 1개 |

**Phase D — 지표·가설·실패 (Section 12-14)**

| # | 섹션 | 필수 내용 |
|---|------|---------|
| 12 | Dual-axis OKR | North Star 1 + Business KR 3–5 + Operational KR 3–5 (cost KR mandatory) + Anti-Metric 1 |
| 13 | 검증 가능 가설 | Top-3 + 각각 2-day experiment |
| 14 | 실패 모드 + HITL | 시나리오 매트릭스 최소 4개 (감지/대응/사용자 영향) + HITL 트리거 |

**PRD 작성 완료 후 — v0.1 기록:**

```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "build" \
  --q "PRD 초안 작성" \
  --options "Signal Gate 기반 초안" \
  --chosen "Signal Gate 기반 초안" \
  --why "4개 Signal Gate 문서(pain/cogs/market/competitors) 기반 15섹션 초안" \
  --prd-version "v0.1"
```

*`--step prd` 선택 시 여기서 종료.*

#### Step 4-2: OKR 설계 (`--step okr`)

`docs/PRD.md` Section 12를 독립적으로 작성하거나 업데이트한다.

- **North Star 정렬**: 이 에이전트가 제품의 North Star에 어떻게 기여하는가?
- **2-Axis OKR**:
  - Axis 1 — Business Impact: 매출/인게이지먼트/전환/시간 절감
  - Axis 2 — Operational Health: 신뢰성/비용 효율/사용자 만족도
- Objective 2–3개 × Key Result 3–4개씩
- 측정 계획: 데이터 소스 / 기준값 / 목표값 / 리뷰 주기

**출력**: North Star 정렬 문장 + OKR 테이블 (Objective → KR → Baseline → Target) + 측정 계획

*`--step okr` 선택 시 여기서 종료.*

#### Step 4-3: Sprint 플래닝 (`--step sprint`)

`harness/SPRINT-W1.md`를 작성한다.

**Day-by-Day 플랜**:

| Day | 작업 | 스킬/도구 |
|-----|------|---------|
| 1 | 핵심 에이전트 인스트럭션 정의 (Role/Goal/Output 3요소) | agent-instructions |
| 2 | 단일 happy path 수동 테스트 (샘플 입력 5개) | instruction |
| 3 | 에러 처리 + 컨텍스트 예산 설정 | ctx-budget |
| 4 | 프롬프트 최적화 (CRISP 프레임워크 적용) | agent-instructions |
| 5 | 비용 시뮬 재실행 + 테스트 시나리오 3–5개 | cost-sim |
| 6 | PRD 학습 기록 + W2 백로그 작성 | — |
| 7 | W1 Done Criteria 체크 + 실제 사용자 데모 1회 | — |

**Done Criteria**:
- [ ] Happy path end-to-end 실행 완료
- [ ] 최소 1개 실패 케이스 명시적 처리
- [ ] 에이전트 실행을 증명하는 로그 또는 메트릭 1개

**출력**: Sprint 목표 + Day-by-Day 분해 + Done Criteria + W2 백로그

*`--step sprint` 선택 시 여기서 종료.*

---

### Phase 5 — Design & Tracking (`--step craft-init`, `--step craft-lint`, `--step track-init`, `--step track-status`, `--step track-retro`)

#### Design 초기화 (`--step craft-init`)

새 화면 또는 기능의 디자인 시스템 설정. 3단계 체인:

1. **RESPECT.md 인터뷰** — `deliver/respect` 스킬: three_second_rule / next_action / social_proof / hierarchy_rules / motion_language 정의 → `.design/RESPECT.md` 작성
2. **DESIGN.md 확인** — 부재 시 `npx @google/design.md init` 권유; 존재 시 cross-reference 검증
3. **Baseline 측정** (기존 화면 있을 경우) — `deliver/ui-validate --mode layout` 5룰 + WCAG AA 측정 → `.design/hierarchy-baseline.json`

**출력**: `VERDICT: READY / NEEDS_DESIGN_MD / DRIFT_FOUND` + RESPECT.md 상태 + 다음 단계

*`--step craft-init` 선택 시 여기서 종료.*

#### Design 품질 검사 (`--step craft-lint`)

커밋 또는 푸시 전 전체 디자인 무결성 체인. 4단계 순차 실행, 실패 시 조기 종료:

```bash
python3 scripts/validate-craft-lint.py --strict   # Step 1: 정적 검증
```

| Step | 검사 | PASS 조건 |
|------|------|---------|
| 1 | validate-craft-lint.py --strict | RESPECT.md 필드 + DESIGN.md cross-ref + hierarchy color_ratio |
| 2 | deliver/ui-validate --mode layout (Playwright 1440×1080) | 5룰 + WCAG AA 모두 통과 |
| 3 | deliver/respect --mode motion 스캔 | drift 0 |
| 4 | deliver/ui-validate --mode drift (5+ 화면 있을 때만) | baseline 대비 drift 없음 |

**출력**: `VERDICT: PASS / FAIL` + 4단계 결과 + 실패 레이어 + 수정 권유

*`--step craft-lint` 선택 시 여기서 종료.*

#### 진척 추적 초기화 (`--step track-init`)

새 기능 구현 시 PM 급 가시성 설정. 4단계 체인:

1. **velocity baseline 추출** — `deliver/sprint --step init`: `profiles/<operator>/velocity/baseline.jsonl` 확인 (trust_grade ≥ B이면 사용, 없으면 추출)
2. **태스크 분해** — `deliver/sprint --step plan`으로 PRD/feature description → WBS 분해 → `.track/predicted.json` 잠금
3. **progress hook 등록** — `.claude/settings.json` PostToolUse에 track-probe.sh 등록
4. **gate-checkpoint 등록** — PreToolUse에 gate-block.sh 등록, 6-phase 통과 조건 로드

**출력**: `VERDICT: READY / NEEDS_BASELINE / FAILED` + 예측 범위 요약 + Hook 등록 상태

*`--step track-init` 선택 시 여기서 종료.*

#### 라이브 진척 현황 (`--step track-status`)

구현 중 현재 상태 스냅샷. 3단계 체인:

1. **Hook 상태 점검** — 직전 5분 항목 수 + hook/shell 비율 (hook < 80% → warning)
2. **blocker 감지** — `deliver/sprint --step status` 5종 결정론 신호: self_doubt / retry_loop / test_fail_repeat / context_pressure / stall (score ≥ 8 → blocker, ≥ 15 → critical)
3. **진척 보고** — `deliver/sprint --step status` Predicted vs Actual (LOC/tokens/hours), Velocity vs baseline, ETA p50/p90, Blockers, Next gate

**출력**: 6섹션 보고 (Predicted/Actual/Velocity/ETA/Blockers/Next gate)

*`--step track-status` 선택 시 여기서 종료.*

#### 회고 + TK 추출 (`--step track-retro`)

기능 완료 후 데이터 flywheel 마감. 3단계:

1. **predicted vs actual 비교** — `.track/predicted.json` + `.track/actual_log.jsonl` 대조 → deviation_pct 계산
2. **auto-promote 후보 필터링** — deviation_pct ≥ 50% OR recurrence ≥ 3 → `.track/retro-deviation.jsonl`
3. **pm-engine TK 변환** — 후보를 TK-NNN 구조로 자동 변환 → 사용자 일괄 검토 → 승인된 TK만 PM-ENGINE-MEMORY.md 추가

**출력**: `VERDICT: PROMOTED / NO_CANDIDATES / FAILED` + deviation 요약 + TK 승인 수 + velocity-baseline 갱신 권유

*`--step track-retro` 선택 시 여기서 종료.*

---

### Phase 6 — Scope Guard (`--step scope`)

개발 중 범위 이탈 차단. 새 기능 요청이 현재 게이트 범위 안에 있는지 확인.

#### Step 6-1: Exclusions Registry 확인

```bash
python3 hplan/scripts/exclusions_registry.py check "$TARGET"
```

COLLISION → 즉시 **BLOCK**.

#### Step 6-2: CONDITIONAL_GO 허용 범위 확인

```bash
python3 -c "
import json, pathlib
cp = pathlib.Path('harness/build-gate/checkpoint.json')
if not cp.exists(): print('NO_CHECKPOINT')
else:
    d = json.loads(cp.read_text())
    print(f'DECISION={d.get(\"decision\", \"GO\")}')
    print(f'ALLOWED={d.get(\"allowed_paths\") or []}')
"
```

- `decision == "GO"` → 제약 없음, Step 6-3으로.
- `decision == "CONDITIONAL_GO"` + 허용 경로 있음 → 기능이 허용 범위 내인지 판단. 범위 외 → **DEFER**.

#### Step 6-3: COGS 티어 영향 확인

새 기능이 외부 API 추가, 새 모델, 또는 호출 횟수 증가를 유발하는지 감지. 유발 시 경고 포함 ALLOW 또는 DEFER.

DEFER 판정 시 `harness/v2-backlog.md`에 기록 제안.

**출력**:
```
hplan-scope-guard — [날짜]
대상: [feature]
레지스트리:  CLEAR / COLLISION
허용 범위:  IN_SCOPE / OUT_OF_SCOPE / NO_CONSTRAINT
COGS 티어:  UNCHANGED / WARNING
판정: ALLOW / DEFER / BLOCK
이유: [한 줄]
```

*`--step scope` 선택 시 여기서 종료.*

### Phase 7 — Spec Compliance Review (`--step spec-review`)

> **왜**: 코드가 완성됐다는 것과 PRD를 따랐다는 것은 다릅니다.
> 이 Phase는 구현 후 "우리가 만들려 했던 것을 만들었는가"를 확인합니다.

3개 체크포인트를 순서대로 확인한다:

**① ICP 정합성** — `docs/PRD.md` Section 1 타겟 사용자 정의 vs 실제 구현된 접근 경로
- PRD에 정의된 ICP 조건 목록 추출
- 실제 구현에서 각 조건이 충족되는지 확인
- 미구현 ICP 조건을 수정 태스크로 기록

**② 비기능 요건** — PRD Section 12 (성공 지표 Dual-axis — 레이턴시·에러율·가용성) vs 실제 측정값
- 측정된 항목: 수치 비교 (목표 vs 실측)
- 미측정 항목: 측정 계획 수립 태스크 생성

**③ 실패 모드 커버** — PRD Section 14 실패 시나리오 vs 구현된 fallback
- 각 실패 시나리오별 판정: 구현됨 / 미구현 / N/A

**출력:** 체크포인트별 판정 표 + 미충족 항목 수정 태스크 목록

**결정 기록:**
```bash
python3 hplan/scripts/decision_log.py hitl \
  --phase "build" \
  --q "Spec Compliance Review 판정" \
  --options "통과(전체 충족)|조건부 통과(경미한 미충족)|재작업 필요(핵심 미충족)" \
  --chosen "[판정]" \
  --why "[근거]"
```

*`--step spec-review` 선택 시 여기서 종료.*

---

### Phase 8 — Quality Gate (`--step quality-gate`)

> **왜**: Spec Compliance가 "올바른 것을 만들었는가"라면, Quality Gate는
> "제대로 만들었는가"입니다. 출시 시점의 기술 부채 누적을 막습니다.

3개 항목을 확인한다:

**① 테스트 커버리지** — 핵심 경로(happy path + 주요 실패 시나리오) 테스트 존재 여부
- 없으면: 최소 커버 테스트 작성 태스크 생성

**② 기술 부채 마커** — TODO·FIXME·임시방편 주석 수
- 5개 이하: 통과
- 6–15개: 경고 + 해소 계획 작성
- 16개 이상: 차단 — 마커 정리 후 재실행

**③ 보안 기본 점검** — 하드코딩 시크릿·미검증 외부 입력 여부
- 발견 즉시 차단, 수정 후 재실행

**④ UI Evidence Gate** — `harness/QA_CHECKLIST.md` 존재 여부로 UI 제품 판정:

```bash
# UI 제품 여부 결정론 판정 (QA_CHECKLIST.md 존재 = UI 제품)
if [ -f harness/QA_CHECKLIST.md ]; then
  python3 -c "
import json, sys
try:
    d = json.load(open('harness/ui-evidence/summary.json'))
    total = d.get('total', 0)
    ct = d.get('critical_total', 0)
    cs = d.get('critical_screenshots', 0)
    af = d.get('critical_assertion_fails', 0)
    if total == 0:
        print('BLOCK_EMPTY')
    elif ct > 0 and cs < ct:
        print('BLOCK_INCOMPLETE')
    elif af > 0:
        print('BLOCK_ASSERTION_FAILED')
    else:
        print('PASS')
except Exception:
    print('BLOCK_MISSING')
  " 2>/dev/null
else
  echo "SKIP"
fi
```

- `SKIP` → `harness/QA_CHECKLIST.md` 없음 (백엔드 전용 제품), 통과
- `PASS` → ✅ UI Evidence Gate 통과 (시각 증거 수집 완료)
- `BLOCK_MISSING` → 차단: "`ui-validate --check tc-gate [URL]` 먼저 실행하세요."
- `BLOCK_EMPTY` → 차단: "TC 0개 — QA_CHECKLIST 파싱 오류. `/qa-checklist` 재실행 후 tc-gate 재시도"
- `BLOCK_INCOMPLETE` → 차단: "Critical TC 스크린샷 미완. `ui-validate --check tc-gate [URL]` 재실행"
- `BLOCK_ASSERTION_FAILED` → 차단: "Critical TC assertion 실패 {af}건 — `harness/ui-evidence/summary.json` tc_results 확인 후 수정 + tc-gate 재실행"

> ℹ️ tc-gate는 **시각 증거 수집 + assertion** 도구입니다. 스크린샷은 PM/QA 육안 검토용이며, Expected State 컬럼이 있는 TC는 자동 assertion이 실행됩니다.

**출력:** 3~4개 항목 판정 + 발견된 이슈 목록 + 다음 단계 태스크

*`--step quality-gate` 선택 시 여기서 종료.*

---

## Output Format

**전체 플로우 (플래그 없음)** — 순서대로 출력:

1. **Evidence Gate** — 제외 판정 / 루브릭 점수 N/100 / 결정 (build/interview/pivot/hold)
2. **Product Gate** — OST 상태 / Journey+sitemap / Design pointer / 다음 게이트
3. **COGS Gate** — 비용 p50/p90 / Gross margin / GREEN·CONDITIONAL_GO·RED
4. **Checkpoint 상태** — `harness/build-gate/checkpoint.json` 작성 완료 (gate_guard.py 해제)
5. **`docs/PRD.md`** — 15섹션 PRD 작성 완료
6. **`harness/SPRINT-W1.md`** — W1 스프린트 플랜 작성 완료
7. **다음 단계** — "W1 Day 1: 에이전트 인스트럭션 작성 시작"
8. **Spec Compliance** — ICP·비기능·실패 모드 3 체크포인트 판정 (통과/조건부/재작업)
9. **Quality Gate** — 기술 부채 마커 수 + 발견된 이슈 목록

**개별 --step**: 해당 Phase의 출력 형식으로만 응답. `--step spec-review`, `--step quality-gate` 포함.
