---
name: blocker-detect
description: "Scan .track/actual_log.jsonl for deterministic blocker patterns — 50+ regex/counter/threshold signals (same-file edit ≥3, test_fail repeat ≥2, context token ≥70%, silence ≥90s, self-doubt regex like 'not sure', cycle dependencies). LLM 호출 0 — all detection is pattern matching + counters per Rule 5 (LLM은 분류만, routing/policy decisions은 결정론). Outputs .track/blockers.md ranked by severity for progress-report and human review."
argument-hint: "[since <ISO-ts> | task <id> | live]"
allowed-tools: ["Read", "Write", "Bash"]
model: sonnet
---

## Core Goal

- progress-probe 가 쌓는 jsonl 에서 **결정론 신호 5종** 감지 → blocker 후보 랭킹
- LLM 호출 0 — 모든 감지가 정규식 / 카운터 / 임계치
- 출력 `.track/blockers.md` 가 progress-report 의 자동 보고 트리거 신호 공급
- 가짜 양성 (false positive) 줄이기 위해 신호별 가중치 + 누적 점수 통과만 alert

---

## Rule 5 위반 회피 — "Don't use LLM as if statement"

CLAUDE.md Rule 5 사례: "에러 메시지로 재시도 여부 결정 → 금지(정규식·코드 처리). 에러 메시지를 사용자 친화 문구로 변환 → OK". blocker-detect 는 정확히 같은 카테고리 — **신호 감지는 정규식·카운터, 사용자 보고 문구는 progress-report 가 변환**.

| 영역 | LLM 사용 |
|---|---|
| 정규식 매칭 (self-doubt 50 패턴) | ❌ |
| 카운터 (same-file edit, test_fail, context tokens) | ❌ |
| 임계치 비교 (>= 3, >= 0.7) | ❌ |
| graph cycle detection (dependency loop) | ❌ |
| severity ranking (가중치 합) | ❌ |
| 사용자에게 "이 blocker는 어떻게 풀어야 하나" 자연어 조언 | (별도 스킬, blocker-detect 책임 X) |

---

## 5종 결정론 신호

| # | 신호 | 감지 방법 | 임계 | 가중치 |
|---|---|---|---|---|
| 1 | **self_doubt** | 정규식 사전 50 패턴 매칭 ("I'm not sure", "this might not work", "확실하지 않", "잘 모르겠" 등) | ≥1 hit / 5min window | 3 |
| 2 | **retry_loop_file** | 같은 file 에 str_replace/edit tool_call 카운터 | ≥3 / 10min | 5 |
| 3 | **test_fail_repeat** | bash tool + cmd_summary 에 "test/spec" 포함 + exit_code != 0 카운터 | ≥2 / 5min | 5 |
| 4 | **context_pressure** | tokens_total 의 max_context 대비 비율 | ≥0.70 | 4 |
| 5 | **stall** | 직전 tool_call ts 와 현재 ts 간격 | ≥90s 무 tool_call | 2 |

부가 신호:
- **cycle_dependency**: predicted.json 의 task dependency 가 cycle 형성 → 가중치 10 (immediate fail)
- **token_overrun**: 누적 tokens > predicted_p90 → 가중치 4
- **time_overrun**: 누적 minutes > predicted_p90 → 가중치 3

총 score ≥ 8 → blocker alert (false positive 줄임)
총 score ≥ 15 → critical blocker (progress-report 가 강제 보고 트리거)

---

## Trigger Gate

### Use This Skill When
- progress-probe 가 jsonl 작성 중 — 주기적 (e.g., 매 5분) 또는 progress-report 호출 직전
- 사용자가 "지금 막혔어?" 명시 호출 (`/blocker-detect live`)
- 특정 task 의 후행 진단 (`/blocker-detect task T-007`)

### Route to Other Skills When
- blocker 가 디자인 위반 (UI 파일에서 craft-lint 실패) → `craft/craft-lint` 결과 참조
- blocker 의 자연어 보고 문구 생성 → `track/progress-report` (Phase 5)
- blocker 패턴이 반복 → `learn/pm-engine` 의 retro-extract 라우터 (Phase 2 기존 확장) 로 TK 후보 promote

### Boundary Checks
- jsonl 자체 없음 → "progress-probe install 먼저" fail loud
- 패턴 사전 (`references/blocker-patterns.yaml`) 누락 → 빌트인 fallback (덜 정확)
- score < 8 인 신호도 stdout debug 로는 표시, blockers.md 에는 alert 만

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| .track/actual_log.jsonl | progress-probe | append-only stream 파싱 |
| .track/predicted.json | estimate-tasks | task 메타데이터 + dependency graph |
| references/blocker-patterns.yaml | 스킬 동봉 | 50+ 정규식 사전 |
| max_context (모델 종속) | hardcoded (예: 200000) | context_pressure 비율 계산 |

---

## Instructions

You are scanning blockers for: **$ARGUMENTS** (since <ISO> | task <id> | live)

**Step 1 — jsonl 로드 + 윈도우 필터**
- since <ISO>: ts >= since 인 entry 만
- task <id>: task_id == id 인 entry 만
- live: 직전 30분 (default window)

**Step 2 — 5종 신호 결정론 스캔 (LLM 호출 0)**
```python
# pseudocode
for entry in window:
    if event == "tool_call" and matches_self_doubt(entry.payload):
        accumulate("self_doubt", weight=3)
    if event == "tool_call" and tool in ("str_replace","write") and file == prev_file:
        same_file_edits[file] += 1
        if same_file_edits[file] >= 3:
            accumulate("retry_loop_file", weight=5, evidence=file)
    # ... 나머지 3종
```

**Step 3 — 부가 신호 (cycle / token_overrun / time_overrun)**
- predicted.json 로드, dependency graph DFS → cycle 검증
- 누적 tokens vs predicted_p90 비교
- 경과 minutes vs predicted_p90 비교

**Step 4 — Severity 점수 합산 + 랭킹**
- 각 task 별 score 누적
- score ≥ 8 → blocker, score ≥ 15 → critical
- evidence (어느 file, 어느 cmd) 같이 저장

**Step 5 — `.track/blockers.md` 출력**
```markdown
# Blockers (scanned 2026-05-17T10:30Z)

## 🚨 T-008 — score 17 (critical)
- retry_loop_file: middleware/jwt.ts edits 5회 / 10min (weight 5)
- test_fail_repeat: npm test exit 1 × 4 (weight 5)
- self_doubt: "let me try a different approach" 1회 (weight 3)
- context_pressure: tokens 162K / 200K = 81% (weight 4)
- **Suggested action**: spawn subagent OR human review

## ⚠️ T-005 — score 9
- stall: 직전 tool_call 후 145s 무응답 (weight 2)
- time_overrun: 47min vs predicted_p90 38min (weight 3)
- ... (다른 신호 점수 합)
```

**Step 6 — Rule 5 자체 점검**
- 이 스캔에서 LLM 호출 수 = ? (반드시 0)
- 0 아니면 즉시 fail + error report

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| jsonl 없음 | file not found | "progress-probe install 먼저" fail loud |
| jsonl 파싱 에러 (broken JSON 줄) | json.loads 실패 | 깨진 줄 skip + warning, 나머지 진행 (append-only 보존) |
| 패턴 사전 yaml 없음 | references 누락 | 빌트인 fallback 사용 + warning |
| score 계산 overflow (10000+) | sum > 1000 | predicted.json 누락 의심, 진단 권유 |
| LLM 호출 감지 | Step 6 self check | **즉시 fail, Rule 5 위반** |

---

## Quality Gate

- [ ] .track/blockers.md 가 score 내림차순 정렬
- [ ] 각 blocker 에 evidence (file/cmd/시간) 명시
- [ ] critical blocker 는 suggested action 포함
- [ ] **LLM 호출 수 = 0** (Rule 5 자체 점검)
- [ ] false positive 줄이기 위해 score ≥ 8 만 blocker 로 표시

---

## Examples

### Good Example
**입력:** "live"

**기대 출력:** (.track/blockers.md)
```markdown
# Blockers (scanned 2026-05-17T10:30Z, window=30min)

## 🚨 T-008 "OAuth callback handler" — score 17 (critical)
- retry_loop_file: src/auth/oauth.ts edits 5회 (weight 5)
- test_fail_repeat: npm test exit 1 × 3 (weight 5)
- context_pressure: 142K/200K = 71% (weight 4)
- self_doubt: "let me try" 1회 (weight 3)
- **Action**: spawn subagent OR human review

## ⚠️ T-011 "Email verification" — score 8
- blockedBy T-008 (transitive blocker)
- stall: 145s 무 tool_call (weight 2)
- + transitive weight from T-008: 6
```

### Bad Example
**입력:** (인자 없음)

**왜 나쁜가:**
- since / task / live 중 어느 모드인지 모호
- 전체 jsonl 스캔 = 비효율 (raw 카운터 폭주 → false positive 증가)

**기대 동작:** "live 로 default 진입, 30분 윈도우 적용" + 사용자 알림

---

## Contextual Knowledge (auto-loaded)

### Good Example
!`cat examples/good-01.md 2>/dev/null || echo ""`

### Bad Example
!`cat examples/bad-01.md 2>/dev/null || echo ""`

### Pattern Dictionary
!`cat references/blocker-patterns.yaml 2>/dev/null || echo ""`

### Severity Weight Tuning
!`cat references/weight-tuning.md 2>/dev/null || echo ""`
