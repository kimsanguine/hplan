---
name: delivery-plan
description: "Unified delivery planning skill — estimate (PRD → WBS task decomposition, complexity 1-5 classification, deterministic velocity lookup) and baseline (N prior projects → personal velocity percentile table). Default --step both: baseline 계산 후 estimate 조정. estimate 단계의 (loc/tokens/minutes) p50/p90 예측은 LLM 호출 0 — baseline lookup 전용(Rule 5 준수). Outputs .track/predicted.json."
argument-hint: "[--step estimate|baseline|both] [PRD path, feature description, or 'last 5']"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

두 단계를 단일 인터페이스로 통합한다:

| step | 책임 | LLM |
|---|---|---|
| `--step estimate` | PRD → WBS 분해, complexity 1-5 분류, 결정론 velocity lookup → `.track/predicted.json` | ✅ WBS/분류만, 수치 예측 ❌ |
| `--step baseline` | N 과거 프로젝트 git log + token usage → complexity별 p50/p90 lookup table | ❌ 전체 결정론 |
| `--step both` | baseline 먼저 계산, 그 결과로 estimate 조정 (기본값) | ✅ estimate 분류만 |

> **Rule 5 핵심**: estimate 단계의 (loc, tokens, minutes) p50/p90 **수치 예측은 LLM 호출 0**. baseline.jsonl percentile lookup만 사용. LLM 호출 시 Rule 5 위반 즉시 fail.

---

## Rule 5 준수 경계

| 작업 | LLM 사용 | 근거 |
|---|---|---|
| WBS 분해 | ✅ 분류 | 텍스트 → sub-task 분류 |
| complexity 1-5 분류 | ✅ 분류 | description 텍스트 기반 분류 허용 |
| 의존성 그래프 분류 | ✅ 분류 | 관계 분류 허용 |
| **loc/tokens/minutes 수치 예측** | ❌ **lookup 전용** | baseline percentile 직접 인용, hallucination 방지 |
| complexity 1-5 결정론 분류 (baseline) | ❌ 결정론 | 파일 수 + LOC delta + commit 메시지 길이 휴리스틱 |
| p50/p90 집계 | ❌ 결정론 | numpy percentile |
| 의존성 cycle 검증 | ❌ 결정론 | DFS 그래프 알고리즘 |

---

## Trigger Gate

### Use This Skill When
- track-init 첫 흐름 — PRD 받자마자 예측치 lock → `--step both`
- 새 feature 스코핑 (parallel-team 분배 전) → `--step estimate`
- hplan 처음 도입 또는 직전 프로젝트 완료 후 baseline 갱신 → `--step baseline`
- estimate vs actual deviation 50% 초과 → `--step baseline` 후 `--step estimate`

### Route to Other Skills When
- 비용 시뮬레이션 (lognormal) → `discover/cost-sim`
- phase gate 정의 → `track/gate-checkpoint`
- WBS 30 task 초과 → `deliver/parallel-team`으로 분할 위임
- 팀 단위 velocity → `operate/scorecard-5axis`

### Boundary Checks
- PRD vague (Section 6 누락) → fail loud, PRD 보강 요청
- baseline 부재 → conservative fallback (모든 task complexity 5 추정치 × 1.5) + warning
- `--step estimate`로 baseline 없이 시작 시 → fallback 경고 + 사용자 확인
- baseline `profiles/<op>/velocity/` 디렉터리가 `.gitignore`에 있는지 확인 (개인 데이터)

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--step` | `$ARGUMENTS` | estimate/baseline/both 분기 |
| target | `$ARGUMENTS` (step 이후 나머지) | PRD/feature description (estimate) 또는 프로젝트 경로 (baseline) |
| `profiles/<op>/velocity/baseline.jsonl` | velocity-baseline 또는 이 스킬 baseline step | estimate lookup 기준 |
| `.track/predicted.json` | 이 스킬 estimate step 출력 | progress-probe deviation 측정 기준 |

---

## Instructions

You are running delivery-plan with arguments: **$ARGUMENTS**

### 공통 Step 0 — step 파싱

```
args = parse("$ARGUMENTS")
step = args.get("--step", "both")   # 기본값: both
target = args remainder after --step value
```

---

### step: baseline

**baseline의 역할**: N 과거 프로젝트에서 개인 velocity 통계를 결정론으로 추출하여 `profiles/<op>/velocity/baseline.jsonl`에 저장.

**Step 1 — 프로젝트 후보 결정**
- "last 5" 입력 → 최근 수정일 기준 5개
- 명시 경로 → 그대로 사용
- 자율 모드면 자동 진행, 아니면 사용자 확인

**Step 2 — git log 결정론 추출**
```bash
git log --pretty=format:'%H|%at|%s' --shortstat
```
- commit 단위 (SHA, timestamp, files_changed, loc_delta, msg_len) 파싱
- merge commit, fixup/revert 제외

**Step 3 — token usage 매칭 (있을 때만)**
- `~/.claude/projects/<project>/*.jsonl` 탐색
- 각 jsonl ts와 가장 가까운 commit 매칭 (±30분)
- 미매칭 → tokens=null

**Step 4 — complexity 1-5 결정론 분류 (LLM 호출 0)**
```python
score = (files_changed * 2) + (loc_delta // 50) + (msg_len // 100)
complexity = 1 if score <= 2 else (2 if score <= 5 else (3 if score <= 10 else (4 if score <= 20 else 5)))
```

**Step 5 — complexity별 percentile 집계**
- `loc_p50 = np.percentile([c.loc for c in samples if c.cx==k], 50)`
- 마찬가지로 tokens_p50/p90, minutes_p50/p90, n_samples

**Step 6 — baseline.jsonl 저장**
- 위치: `profiles/<operator>/velocity/baseline.jsonl`
- 6줄 (complexity 1~5 + meta)
- meta 줄: `{"meta": true, "extracted_at": "<ISO>", "source_projects": [...], "total_commits": N, "trust_grade": "A/B/C"}`
- 신뢰 등급: A (n≥30), B (n≥10), C (n<10 → warning)

---

### step: estimate

**estimate의 역할**: PRD → WBS 분해, complexity 분류 (LLM), 수치 예측 (결정론 lookup), `.track/predicted.json` 저장.

**Step 1 — baseline 로드 + 신뢰 등급 확인**
- `profiles/<operator>/velocity/baseline.jsonl` 읽기
- C 또는 부재 → "conservative fallback 진입" warning + 진행

**Step 2 — PRD WBS 분해 (LLM 분류)**
- PRD Section 6 (Now/Next/Later) 또는 feature 설명에서 task 후보 추출
- 각 task: 1줄 description + 의존성
- 5~20 task 권장. 30 초과 시 parallel-team 라우팅

**Step 3 — 각 task complexity 분류 (LLM)**
- 입력: task description
- 출력: 1/2/3/4/5 + 짧은 이유
- LLM "unsure" 또는 confidence 낮으면 +1 보수적 올림

**Step 4 — 각 task 수치 예측 결정론 lookup (LLM 호출 0)**
```python
for task in tasks:
    cx = task.complexity                    # Step 3 결과
    row = baseline[cx]                       # jsonl lookup
    task.loc_p50 = row["loc_p50"]
    task.loc_p90 = row["loc_p90"]
    task.tokens_p50 = row["tokens_p50"]
    task.tokens_p90 = row["tokens_p90"]
    task.minutes_p50 = row["minutes_p50"]
    task.minutes_p90 = row["minutes_p90"]
```
> LLM 호출 감지 시 즉시 fail — Rule 5 위반.

**Step 5 — 의존성 graph 검증 (결정론)**
- cycle detection (DFS)
- 최장 critical path 계산 (p50 minutes 합) → 프로젝트 ETA

**Step 6 — `.track/predicted.json` 저장**
```json
{
  "feature_name": "...",
  "baseline_ref": "<ISO>",
  "total_tasks": N,
  "tasks": [
    {"id": "T-001", "title": "...", "complexity": 3,
     "loc_p50": 95, "loc_p90": 240,
     "tokens_p50": 9100, "tokens_p90": 18500,
     "minutes_p50": 17, "minutes_p90": 38}
  ],
  "summary": {
    "total_loc_p50": N, "total_loc_p90": N,
    "total_tokens_p50": N, "total_tokens_p90": N,
    "eta_p50_minutes": N, "eta_p90_minutes": N,
    "critical_path": ["T-001", ...]
  }
}
```

**Step 7 — Quality Gate 보고**
- LLM 호출 수 (WBS 1회 + complexity 분류 N회), 결정론 lookup 수
- baseline trust_grade + padding policy

---

### step: both (기본값)

**Step 1** → baseline Step 1~6 실행하여 `baseline.jsonl` 갱신/생성

**Step 2** → estimate Step 1~7 실행 (방금 갱신된 baseline 사용)

> 두 단계 순서 고정: baseline 먼저, estimate 나중.

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| --step 미명시 | 미입력 | both 기본값 진입 + 안내 |
| baseline 없음 (estimate) | file not found | conservative fallback (complexity 5 × 1.5) + warning |
| baseline trust_grade C | n_samples < 10 | padding 0.3 자동 적용 + 사용자 알림 |
| PRD vague | Section 6 누락 | fail loud, PRD 보강 요청 |
| WBS task 수 > 30 | Step 2 결과 | parallel-team 라우팅 권유 |
| 의존성 cycle 발견 | DFS | fail loud, cycle 표시 + 끊기 권유 |
| estimate Step 4에서 LLM 호출 감지 | 자체 점검 | **즉시 fail, Rule 5 위반** |

---

## Quality Gate

### baseline
- [ ] baseline.jsonl 6줄 (complexity 1~5 + meta) 작성
- [ ] 각 complexity n_samples ≥ 3 (없으면 warning)
- [ ] profiles/<name>/velocity/ .gitignore 패턴 확인
- [ ] LLM 호출 0 (결정론 추출)

### estimate
- [ ] WBS task 수 5~30 범위
- [ ] 모든 task complexity 1-5 분류됨
- [ ] 수치 예측 = baseline lookup 값 (LLM 호출 0)
- [ ] 의존성 graph cycle 없음
- [ ] critical path = total p50 minutes의 max
- [ ] Rule 5 자체 점검: Step 4 LLM 호출 수 = 0

---

## Examples

### Good Example
**입력:** `--step both "PRD: 사용자 인증 v2 — JWT middleware + OAuth callback + email verification"`

**기대 동작:**
1. baseline → 최근 5 프로젝트 git log 추출 → baseline.jsonl 갱신
2. estimate → WBS 8 task → complexity 분류 (LLM) → lookup (결정론) → predicted.json 저장
3. LLM 호출: WBS 1회 + complexity 8회 = 9회, 결정론 lookup = 48회

### Good Example
**입력:** `--step baseline "last 5"`

**기대 동작:**
1. 최근 5 프로젝트 git log + token usage 추출
2. complexity 1-5 결정론 분류
3. p50/p90 percentile 집계 → baseline.jsonl 저장
4. trust_grade 보고 (A/B/C)

### Bad Example
**입력:** `--step estimate "JWT 인증 만들어줘"` (PRD 아닌 한 줄)

**기대 동작:** "PRD/feature description 부족 — PRD 먼저 작성 또는 더 구체적인 feature 설명 필요" fail loud

---

## Contextual Knowledge (auto-loaded)

### Conservative Fallback Policy
!`cat references/conservative-fallback.md 2>/dev/null || echo ""`

### Complexity Heuristic Tuning
!`cat references/complexity-thresholds.md 2>/dev/null || echo ""`

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`
