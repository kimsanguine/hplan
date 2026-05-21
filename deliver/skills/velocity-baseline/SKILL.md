---
name: velocity-baseline
description: "Extract a deterministic personal velocity baseline from N prior projects — git log + token usage logs → complexity 1-5 × (loc, tokens, minutes) p50/p90 lookup table. Resolves Rule 5 violation of estimate-tasks token prediction (lookup, not LLM hallucination). Use when starting a new track-init flow, refreshing baseline after each completed project, or onboarding a new operator to hplan track."
argument-hint: "[project paths or 'last 5']"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- 본인 PM 1인의 **실측 작업 통계**를 단일 lookup table (`baseline.jsonl`) 로 결정론 추출
- complexity 1-5 분류는 결정론 휴리스틱 (변경 파일 수 + LOC delta + commit 메시지 길이)
- estimate-tasks 스킬이 이 baseline을 참조하여 LLM 호출 없이 (loc, tokens, minutes) p50/p90 예측

---

## Trigger Gate

### Use This Skill When
- track 플러그인을 처음 도입 (track-init 첫 단계)
- 직전 프로젝트 완료 후 baseline 갱신 (continuous learning)
- 새 운영자 onboarding — 본인 velocity 시드 확보
- estimate-tasks 가 baseline 부재로 fallback 모드에 들어갔을 때

### Route to Other Skills When
- "예측치만 필요해, baseline 없이도 시작하고 싶다" → estimate-tasks 의 conservative fallback 모드
- "팀 단위 velocity가 필요" → operate/scorecard-5axis (Velocity 축)
- "단일 프로젝트의 실시간 진행률" → progress-probe + progress-report

### Boundary Checks
- baseline 은 **개인 데이터**다 → `profiles/<your-name>/velocity/baseline.jsonl` 격리 ([[feedback_hplan_extension]] 4원칙)
- 표본 수 N < 3 이면 baseline 신뢰 ↓ → warning 출력 + estimate-tasks fallback
- 다른 사람의 baseline 을 본인 estimate 에 쓰지 말 것 (velocity 는 개인 차 큼)

---

## Inputs

| 입력 | 출처 | 결정론 추출 |
|---|---|---|
| commit 정보 | `git log --pretty=format:'%H|%at|%s'` + `git diff --shortstat` | shell |
| 변경 파일 수 | `git show --stat <SHA>` 파싱 | 정규식 |
| LOC delta | `git diff --shortstat` insertions+deletions | 정규식 |
| token usage | `~/.claude/projects/<project>/<session>.jsonl` (있을 때) | jsonl 파싱 |
| 경과 시간 | commit 간 timestamp delta (단 30분 idle gap 컷오프) | 카운터 |

> token usage 가 없는 프로젝트는 tokens 컬럼 N/A — estimate-tasks 가 loc·minutes 만으로 예측.

---

## Instructions

You are extracting a velocity baseline for: **$ARGUMENTS**

**Step 1 — 프로젝트 후보 결정**
- "last 5" 입력 → `~/Documents/3_Code/Vibe/Project/` 의 최근 수정일 기준 5개
- 명시 경로 입력 → 그대로 사용
- 사용자에게 확정 한 번 (자율 모드면 자동 진행)

**Step 2 — 각 프로젝트 git log 결정론 추출**
```bash
git log --pretty=format:'%H|%at|%s' --shortstat
```
- 출력 정규식 파싱 → commit 단위 (SHA, timestamp, files_changed, loc_delta, msg_len)
- merge commit 제외, fixup/revert 제외

**Step 3 — token usage 매칭 (있을 때만)**
- `~/.claude/projects/-<project-path>/*.jsonl` 탐색
- 각 jsonl entry 의 ts 와 가장 가까운 commit 매칭 (±30분 윈도우)
- 매칭 안 되는 commit 은 tokens=null

**Step 4 — complexity 1-5 결정론 분류 (LLM 호출 0)**
```python
score = (files_changed * 2) + (loc_delta // 50) + (msg_len // 100)
complexity = 1 if score <= 2 else (2 if score <= 5 else (3 if score <= 10 else (4 if score <= 20 else 5)))
```
- 임계치는 hplan 기본값. 사용자가 `--thresholds` 로 override 가능.

**Step 5 — complexity × percentile 집계**
- complexity 1-5 각각 numpy percentile 계산:
  - `loc_p50 = np.percentile([c.loc for c in samples if c.cx==k], 50)`
  - 마찬가지로 tokens_p50/p90, minutes_p50/p90
- 표본 수 (n_samples) 도 함께 기록

**Step 6 — baseline.jsonl 저장**
- 위치: `profiles/<operator-name>/velocity/baseline.jsonl`
- 6 줄 (complexity 1~5 + meta)
- meta 줄: `{"meta": true, "extracted_at": "<ISO>", "source_projects": ["...", ...], "total_commits": N}`

**Step 7 — Quality Gate 통과 보고**
- 표본 수 / complexity 분포 / 데이터 누락 비율
- 신뢰 등급: A (n≥30 per complexity), B (n≥10), C (n<10 → warning)

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| git log 빈 결과 | `wc -l < log` = 0 | 경로 잘못 — 사용자 재확인 요청 |
| 30분 idle gap 없음 (밤샘 코딩 1세션) | timestamp delta 모두 < 1800s | minutes 컬럼 N/A 표시 + warning |
| token jsonl 매칭 0건 | 모든 commit 에 tokens=null | tokens 컬럼 생략 + estimate-tasks 가 loc만 사용 |
| complexity 분포 편향 (모두 1) | 단순 fixup 프로젝트 | 다른 프로젝트 1-2개 추가 권유 |
| profiles/ 디렉터리 부재 | path not found | 자동 mkdir + .gitignore 검증 |

---

## Quality Gate

- [ ] baseline.jsonl 6 줄 (complexity 1~5 + meta) 모두 작성
- [ ] 각 complexity 의 n_samples ≥ 3 (없으면 warning)
- [ ] meta 줄의 extracted_at·source_projects·total_commits 모두 있음
- [ ] profiles/<name>/velocity/ 디렉터리가 .gitignore 의 profiles/* 패턴에 포함됨
- [ ] LLM 호출 0 — 모든 추출이 결정론 (Rule 5 준수)

---

## Examples

### Good Example
**입력:** "last 5"

**기대 출력:**
```jsonl
{"complexity": 1, "loc_p50": 12, "loc_p90": 35, "tokens_p50": 1800, "tokens_p90": 4200, "minutes_p50": 4, "minutes_p90": 11, "n_samples": 23}
{"complexity": 2, "loc_p50": 45, "loc_p90": 120, "tokens_p50": 5200, "tokens_p90": 9800, "minutes_p50": 9, "minutes_p90": 21, "n_samples": 18}
{"complexity": 3, "loc_p50": 95, "loc_p90": 240, "tokens_p50": 9100, "tokens_p90": 18500, "minutes_p50": 17, "minutes_p90": 38, "n_samples": 14}
{"complexity": 4, "loc_p50": 210, "loc_p90": 480, "tokens_p50": 18200, "tokens_p90": 35400, "minutes_p50": 32, "minutes_p90": 71, "n_samples": 9}
{"complexity": 5, "loc_p50": 520, "loc_p90": 1150, "tokens_p50": 41000, "tokens_p90": 78000, "minutes_p50": 65, "minutes_p90": 140, "n_samples": 4}
{"meta": true, "extracted_at": "2026-05-17T10:34:00Z", "source_projects": ["260514_hplan", "260403_ppt_agent", "260208_meetflow", "260207_shortform_agent", "260203_longform_agent"], "total_commits": 68, "trust_grade": "B"}
```

### Bad Example
**입력:** "그냥 추정해줘 baseline 없이"

**왜 나쁜가:**
- baseline 없이 LLM 추정 = Rule 5 위반 (estimate-tasks 의 회피해야 할 경로)
- 이 스킬은 baseline 추출 전담 — 추정은 estimate-tasks 책임

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Domain Context
!`cat context/domain.md 2>/dev/null || echo ""`

### Complexity Heuristic Tuning
!`cat references/complexity-thresholds.md 2>/dev/null || echo ""`
