---
name: estimate-tasks
description: "Decompose a PRD or feature into a WBS, classify each task complexity 1-5 (LLM classification, Rule 5 허용 영역), then resolve (expected_loc, tokens_p50/p90, minutes_p50/p90) by deterministic percentile lookup from profiles velocity baseline — NOT by LLM token hallucination. Outputs .track/predicted.json that locks the baseline for progress-probe to measure deviation against. Use at the start of any track-init flow or when scoping a new feature for parallel-team."
argument-hint: "[PRD path or feature description]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- PRD/feature → WBS (Work Breakdown Structure) 분해
- 각 task: complexity 1-5 **분류** (LLM, Rule 5 분류 허용)
- 각 task: (loc, tokens, minutes) p50/p90 **추정** (LLM 호출 0, velocity-baseline lookup만)
- 출력 lock 된 `.track/predicted.json` 가 progress-probe 의 deviation 측정 기준선

---

## Rule 5 위반 회피 메커니즘 (핵심)

| 영역 | LLM 사용 | 이유 |
|---|---|---|
| WBS 분해 (1 task → N sub-task) | ✅ 분류 | "이 task가 어떤 sub-task로 나뉘는가" = 카테고리 분류 |
| complexity 1-5 분류 | ✅ 분류 | 결정론 휴리스틱은 description 텍스트에서 score 추출 불가 — LLM 분류가 더 정확 |
| 의존성 그래프 (T-001 blocks T-003) | ✅ 분류 | "이 task가 어떤 다른 task를 막는가" = 관계 분류 |
| **loc / tokens / minutes 추정** | ❌ **결정론 lookup 만** | baseline.jsonl percentile 직접 인용. LLM 호출 시 hallucination 위험 (Rule 5 핵심 위반) |
| 신뢰구간 계산 | ❌ 결정론 | p50/p90 자체가 lookup, 추가 계산 없음 |
| 의존성 위반 검증 | ❌ 결정론 | cycle detection = graph 알고리즘 |

> **만약 baseline 부재**: estimate-tasks 는 conservative fallback 모드로 진입 (모든 task 의 추정치를 baseline 의 max + 50% padding). 절대 LLM 으로 토큰 수 추측하지 않음.

---

## Trigger Gate

### Use This Skill When
- track-init 첫 흐름 — PRD 받자마자 분해 + 예측치 lock
- 새 feature 스코핑 (parallel-team 분배 전 사전 사이즈 측정)
- estimate vs actual deviation 이 50% 넘어 baseline 갱신 필요할 때
- forge/prd 의 Section 6 (Now/Next/Later) 정량화 보조

### Route to Other Skills When
- baseline 자체가 없거나 신뢰 등급 C → `track/velocity-baseline` 먼저 실행
- 비용 시뮬레이션 (lognormal) 필요 → `discover/cost-sim`
- task별 phase gate 정의 필요 → `track/gate-checkpoint` (Phase 5 스킬)
- WBS 가 너무 크면 (>30 task) → `deliver/parallel-team` 으로 분할 위임

### Boundary Checks
- 입력 PRD 가 vague하면 (Section 6 누락) → fail loud, 사용자에게 PRD 보강 요청
- complexity 분류 confidence 낮은 task (LLM 응답 "unsure") → 보수적으로 +1 올림
- baseline.jsonl 의 source_projects 가 현재 프로젝트와 도메인 다르면 → warning

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| PRD 또는 feature description | `$ARGUMENTS` | LLM WBS 분해 |
| velocity baseline | `profiles/<operator>/velocity/baseline.jsonl` | 결정론 lookup |
| 의존성 hint (optional) | PRD Section 6/10 | LLM 분류 → graph |
| padding policy (optional) | `--padding 0.2` 같은 인자 | 결정론 ×(1+padding) |

---

## Instructions

You are estimating tasks for: **$ARGUMENTS**

**Step 1 — baseline 로드 + 신뢰 등급 확인**
- `profiles/<operator>/velocity/baseline.jsonl` 읽기
- meta 줄의 trust_grade 확인 (A/B/C)
- C 또는 부재 → "baseline 없음, conservative fallback 진입" warning + 진행

**Step 2 — PRD WBS 분해 (LLM 분류)**
- PRD 의 Section 6 (Now/Next/Later) 또는 feature 설명에서 task 후보 추출
- 각 task: 1줄 description + 의존성 (있으면)
- 일반적으로 5~20 task. 30 초과 시 parallel-team 라우팅

**Step 3 — 각 task complexity 분류 (LLM 1회/task)**
- 입력: task description + (선택) 변경 예상 파일 카테고리
- 출력: 1/2/3/4/5 중 하나 + 짧은 이유
- LLM 응답이 "unsure" 또는 confidence 낮으면 +1 보수적 올림

**Step 4 — 각 task 추정치 결정론 lookup (LLM 호출 0)**
```python
for task in tasks:
    cx = task.complexity                    # Step 3 분류 결과
    row = baseline[cx]                       # jsonl lookup
    task.loc_p50 = row["loc_p50"]
    task.loc_p90 = row["loc_p90"]
    task.tokens_p50 = row["tokens_p50"]
    task.tokens_p90 = row["tokens_p90"]
    task.minutes_p50 = row["minutes_p50"]
    task.minutes_p90 = row["minutes_p90"]
    if padding > 0:
        task.loc_p90 *= (1 + padding)
        task.tokens_p90 *= (1 + padding)
        task.minutes_p90 *= (1 + padding)
```
> 이 Step 에 LLM 호출이 들어가면 즉시 fail. Rule 5 위반.

**Step 5 — 의존성 graph 검증 (결정론)**
- cycle detection (DFS)
- T-XXX blocks T-YYY 표기 정합성
- 최장 critical path 계산 (p50 minutes 합) → 프로젝트 ETA

**Step 6 — `.track/predicted.json` 저장**
- top-level: feature_name, prd_ref, baseline_ref, estimated_at, total_tasks
- tasks: 배열 (id, title, complexity, dependencies, loc_p50/p90, tokens_p50/p90, minutes_p50/p90)
- summary: total_loc_p50, total_loc_p90, total_tokens_p50/p90, eta_p50_minutes, eta_p90_minutes, critical_path

**Step 7 — Quality Gate 통과 보고**
- LLM 호출 수 (Step 2 1회 + Step 3 N회), 결정론 lookup 수 (N tasks × 6 metrics)
- baseline trust_grade + padding policy
- 사용자에게 lock 컨펌 (Ralph Loop 자율 모드면 자동 진행)

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| baseline.jsonl 없음 | Step 1 file not found | conservative fallback (모든 task = complexity 5 추정치 × 1.5) + warning |
| baseline trust_grade C | n_samples < 10 per complexity | padding 0.3 자동 적용 + 사용자 알림 |
| WBS task 수 > 30 | Step 2 결과 | parallel-team 라우팅 권유, 사용자 confirm |
| complexity 분류 unsure ratio > 30% | Step 3 통계 | PRD description 보강 권유, +1 padding |
| 의존성 cycle 발견 | Step 5 DFS | fail loud, 사용자에게 cycle 표시 + 끊기 권유 |
| Step 4 에 LLM 호출 시도 감지 | 코드 리뷰 | **즉시 fail, Rule 5 위반** |

---

## Quality Gate

- [ ] WBS task 수 5~30 범위
- [ ] 모든 task 에 complexity 1-5 분류됨
- [ ] 모든 task 의 (loc, tokens, minutes) p50/p90 = baseline lookup 값 (LLM 호출 0)
- [ ] 의존성 graph 에 cycle 없음 (DFS pass)
- [ ] critical path = total p50 minutes 의 max
- [ ] predicted.json 의 baseline_ref 가 실제 baseline.jsonl 의 extracted_at 과 일치
- [ ] **Rule 5 자체 점검**: Step 4 의 LLM 호출 수 = 0

---

## Examples

### Good Example
**입력:** "PRD: 사용자 인증 v2 — JWT middleware + OAuth callback + email verification"

**기대 출력:** `.track/predicted.json`
```json
{
  "feature": "user-auth-v2",
  "baseline_ref": "2026-05-17T10:34:00Z",
  "total_tasks": 8,
  "tasks": [
    {
      "id": "T-001",
      "title": "Create JWT middleware",
      "complexity": 3,
      "blocks": ["T-003", "T-004"],
      "blockedBy": [],
      "loc_p50": 95, "loc_p90": 240,
      "tokens_p50": 9100, "tokens_p90": 18500,
      "minutes_p50": 17, "minutes_p90": 38
    },
    ...
  ],
  "summary": {
    "total_loc_p50": 820, "total_loc_p90": 1850,
    "total_tokens_p50": 78000, "total_tokens_p90": 165000,
    "eta_p50_minutes": 142, "eta_p90_minutes": 315,
    "critical_path": ["T-001", "T-003", "T-007"]
  }
}
```
- LLM 호출: WBS 1회 + complexity 분류 8회 = 9회
- 결정론 lookup: 8 tasks × 6 metrics = 48 lookups
- Rule 5 위반: 0 ✅

### Bad Example
**입력:** "JWT 인증 만들어줘"

**왜 나쁜가:**
- 입력이 PRD가 아니라 한 줄 — WBS 분해 의미 없음
- baseline 없이 들어오면 모두 complexity 5 padding → 무의미한 큰 예측

**기대 동작:**
- "PRD/feature description 부족 — forge/prd 로 먼저 PRD 작성 또는 baseline 확보 후 재시도" fail loud

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`

### Fallback Policy
!`cat references/conservative-fallback.md 2>/dev/null || echo ""`
