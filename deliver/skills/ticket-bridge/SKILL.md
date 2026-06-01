---
name: ticket-bridge
description: "GitHub Issues ⇄ hplan 실행 레이어(sprint/.track)를 잇는 번역기. --mode pull(Issues→WBS 후보), --mode estimate(predicted.json p50/p90 → 이슈 코멘트), --mode status(.track+git/PR 상태 → 이슈 코멘트). 추정치를 직접 계산하지 않고 sprint 산출물을 전달만 한다. Use when syncing GitHub tickets with hplan sprint tracking, or when a PM wants estimates/progress written back onto issues."
argument-hint: "[--mode pull|estimate|status] [issue numbers or filter]"
allowed-tools: ["Read", "Write", "Bash", "mcp__github__list_issues", "mcp__github__issue_read", "mcp__github__list_commits", "mcp__github__pull_request_read", "mcp__github__add_issue_comment", "mcp__github__issue_write"]
model: sonnet
---

## Core Goal

GitHub Issues(system of record)와 hplan의 닫힌 실행 레이어(`sprint`의 `.track/`)를 잇는다.
ticket-bridge는 **번역기**다 — 추정치나 진척을 *생성*하지 않고, sprint/conductor의 산출물을 GitHub 포맷으로 전달하거나 그 반대로 변환만 한다.

| 모드 | 책임 | 입력 → 출력 | LLM |
|---|---|---|---|
| `--mode pull` | GitHub Issues → WBS 태스크 후보 | `list_issues` → `harness/ticket-import.md` | ✅ body 분해만 |
| `--mode estimate` | `predicted.json` p50/p90 → 이슈 코멘트 | `.track/predicted.json` + `ticket-map.json` → `add_issue_comment` | ✅ 산문만 |
| `--mode status` | `.track/` + git/PR 상태 → 이슈 코멘트 | `actual_log.jsonl` + `list_commits`/`pull_request_read` → `add_issue_comment` | ✅ 산문만 |

> **기본값**: `--mode` 미명시 → fail loud + 모드 목록 안내. auto-run 금지.

---

## Rule 5 준수 경계

| 작업 | LLM 사용 | 근거 |
|---|---|---|
| Issue body → 태스크 후보 분해 (pull) | ✅ 분류 | 자연어 → sub-task 분류. sprint WBS와 동일 성격 |
| 코멘트 산문 생성 (estimate/status) | ✅ 자연어 생성 | Rule 5 허용 영역 |
| **size 라벨 → complexity bucket 매핑** | ❌ **결정론 lookup** | §매핑 규칙 순수 테이블 |
| **complexity → baseline percentile 전달** | ❌ **결정론** | predicted.json 값 직접 인용 |
| **태스크 ↔ 이슈 매칭** | ❌ 결정론 | `harness/ticket-map.json` 명시 매핑 lookup |
| **commit/PR ↔ 태스크 매칭** | ❌ 결정론 | ticket-map의 issue 번호 → commit/branch 정규식 |
| **중복 코멘트 감지** | ❌ 결정론 | 마커 문자열 + 태스크 ID grep |

> **자체 점검:** 라벨 매핑·estimate 전달·태스크 매칭에서 LLM 호출이 감지되면 즉시 fail — Rule 5 위반.

---

## Trigger Gate

### Use This Skill When
- "이 이슈들 스프린트 계획에 넣어줘" → `--mode pull`
- "추정치를 이슈에 달아줘" → `--mode estimate`
- "진행 상황을 이슈에 업데이트해줘" → `--mode status`

### Route to Other Skills When
- WBS 수치 예측 *계산* → `deliver/sprint --step plan` (ticket-bridge는 계산 안 함)
- 태스크 실제 실행 → `deliver/conductor`
- 추적 환경 초기화 → `deliver/sprint --step init`

### Boundary Checks
- `--mode` 미명시 → fail loud, 모드 목록 출력
- GitHub MCP 미연결 → fail loud (대체 API client 만들지 않음)
- write-back 전 항상 **사용자 확인 게이트** 통과 (자동 코멘트 금지)

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--mode` | `$ARGUMENTS` | pull/estimate/status 분기 |
| issue 번호/필터 | `$ARGUMENTS` 나머지 | 대상 이슈 선택 |
| `.track/predicted.json` | sprint plan 산출 | estimate 전달 소스 |
| `.track/actual_log.jsonl` | sprint init+probe | status 전달 소스 |
| `harness/ticket-map.json` | pull 산출 또는 수동 | 태스크 ID ↔ 이슈 번호 매핑 |

`$ARGUMENTS`를 파싱해 mode와 대상을 분리한다.

---

## 결정론적 매핑 규칙

### size 라벨 → complexity bucket (순수 lookup, LLM 0)

| GitHub 라벨 | complexity bucket |
|---|---|
| `size/XS` | 1 |
| `size/S` | 2 |
| `size/M` | 3 |
| `size/L` | 4 |
| `size/XL` | 5 |

- 매핑되는 `size/*` 라벨이 **0개** → ambiguous, fail loud (LLM 추론으로 fallback 금지).
- `size/*` 라벨이 **2개 이상** → ambiguous, fail loud (임의 선택 금지).

### 태스크 ↔ 이슈 매칭 — `harness/ticket-map.json`

```json
{ "T-001": 42, "T-002": 43 }
```

- estimate/status는 이 매핑으로 predicted.json 태스크 ↔ 이슈 번호를 연결한다.
- 매핑 항목이 없으면 해당 태스크는 "매칭 불가"로 표시하고 나머지는 진행 (부분 성공 명시 — Rule 8).
- commit/PR 매칭(status)은 ticket-map의 이슈 번호를 commit message·branch명에서 정규식으로 찾는다.

---

## Instructions

You are running ticket-bridge with arguments: **$ARGUMENTS**

### 공통 Step 0 — mode 파싱

```
args = parse("$ARGUMENTS")
mode = args.get("--mode")   # 없으면 fail loud
```

mode 미명시 시:
> "--mode 미명시 — 사용 가능: `--mode pull|estimate|status`. auto-run하지 않습니다."

GitHub MCP 도구 가용성을 먼저 확인한다. 미연결이면 fail loud.

---

### mode: pull

1. `mcp__github__list_issues`로 대상 이슈를 읽는다 (필드: `number`, `title`, `body`, `labels[].name`, `state`).
2. 각 이슈 body를 WBS 태스크 후보로 분해한다 (LLM 분류 — sprint WBS와 동일).
3. 각 이슈의 `size/*` 라벨 → complexity bucket (결정론 매핑).
4. `harness/ticket-import.md`에 태스크 후보 + complexity + 원본 이슈 번호를 기록한다.
5. `harness/ticket-map.json`에 태스크 ID ↔ 이슈 번호 매핑을 append (덮어쓰기 금지).
6. 다음 단계 안내: "`sprint --step plan harness/ticket-import.md`로 추정치를 계산하세요. ticket-bridge는 추정을 계산하지 않습니다."

> pull은 GitHub에 **아무것도 쓰지 않는다** (read-only).

---

### mode: estimate

1. `.track/predicted.json` 로드. 없으면 fail loud ("`sprint --step plan` 먼저").
2. `harness/ticket-map.json`으로 각 태스크 ↔ 이슈 번호 매칭.
3. 각 매칭 태스크에 대해 predicted.json의 p50/p90 값을 **그대로 인용**해 코멘트 본문을 만든다 (계산 금지, 전달만).
4. 코멘트 형식:

```markdown
<!-- hplan:ticket-bridge -->
## hplan estimate (T-003 ↔ #43)
- complexity: 3 (label `size/M`)
- LOC p50/p90: 76 / 106
- tokens p50/p90: <predicted 값 또는 N/A>
- minutes p50/p90: <predicted 값 또는 N/A>
- baseline_ref: <ISO> (trust_grade: B)
> 출처: .track/predicted.json — sprint --step plan 산출. ticket-bridge는 전달만 함.
```

5. **확인 게이트**: 작성할 코멘트 전문을 사용자에게 보여주고 명시적 승인을 받는다. 승인 전 `add_issue_comment` 호출 금지.
6. 승인 후 `mcp__github__add_issue_comment`로 작성. `<!-- hplan:ticket-bridge -->` 마커 + 같은 태스크 ID 코멘트가 이미 있으면 skip + 안내.

---

### mode: status

1. `.track/actual_log.jsonl` 로드. 없으면 fail loud ("`sprint --step init` 먼저").
2. `harness/ticket-map.json`으로 태스크 ↔ 이슈 매칭.
3. 각 태스크의 진척을 결정론 집계 (complete 이벤트 유무, 경과, 블로커 수). 수치 생성 금지 — actual_log 값 인용.
4. ticket-map의 이슈 번호로 `list_commits`/`pull_request_read`를 조회해 관련 commit/PR 상태를 매칭 (정규식).
5. 진척 코멘트 본문을 만든다 (마커 포함).
6. **확인 게이트**: 코멘트 전문 + (선택) `--close` 플래그 시 상태 전환 후보를 사용자에게 보여주고 승인받는다.
7. 승인 후 `add_issue_comment`. `--close` 플래그가 있고 모든 매칭 태스크가 complete면 `issue_write`로 `state=closed` 전환 (본문/제목 편집 금지).

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| `--mode` 미명시 | 미입력 | fail loud + 모드 목록 |
| GitHub MCP 미연결 | `mcp__github__*` 미등록/실패 | fail loud — 대체 client 안 만듦, silent degrade 금지 |
| `size/*` 라벨 0개 (pull/estimate) | 라벨 매핑 결과 없음 | fail loud + 해당 이슈 번호 — "size/* 라벨 하나 지정 필요". LLM 추론 금지 |
| `size/*` 라벨 2개+ | 라벨 매핑 충돌 | fail loud + 충돌 라벨 나열. 임의 선택 금지 |
| `predicted.json` 없음 (estimate) | file not found | fail loud — "sprint --step plan 먼저, 전달할 추정치 없음" |
| `actual_log.jsonl` 없음 (status) | file not found | fail loud — "sprint --step init 먼저" |
| ticket-map 매핑 누락 | 태스크 ID 키 없음 | 해당 태스크 "매칭 불가" 표시, 나머지 진행 (부분 성공 명시) |
| write-back 권한 없음 | `add_issue_comment` 403 | fail loud — "issue write 권한 없음. 계산 결과는 stdout으로 출력하니 수동 첨부 가능" — 거짓 done 금지 |
| 중복 코멘트 | 마커+태스크 ID 존재 | skip + 안내 (덮어쓰기 금지) |
| 확인 게이트 거부 | 사용자 미승인 | write-back 취소, 본문은 stdout 보존 |

원칙: **계산 단계와 write-back 단계 분리**. write-back이 실패/거부돼도 계산 결과는 stdout으로 surface — "complete"로 거짓 보고하지 않는다 (Rule 8).

---

## Quality Gate

### pull
- [ ] GitHub에 write 0회 (read-only)
- [ ] 모든 이슈 size/* → complexity 매핑됨 (LLM 매핑 0)
- [ ] `harness/ticket-map.json` append (덮어쓰기 0)

### estimate
- [ ] 모든 수치 = predicted.json 인용값 (계산 0)
- [ ] write-back 전 확인 게이트 통과
- [ ] 마커 + 중복 코멘트 감지 동작

### status
- [ ] 진척 수치 = actual_log 인용 (생성 0)
- [ ] commit/PR 매칭 = 정규식 (LLM 0)
- [ ] write-back 전 확인 게이트 통과

---

## Examples

### Good Example
**입력:** `--mode pull #42 #43`

**기대 동작:**
1. 이슈 2개 read → body 분해 (LLM) → size/* → complexity (결정론)
2. `harness/ticket-import.md` + `harness/ticket-map.json` 기록
3. GitHub write 0회, "sprint --step plan으로 추정 계산" 안내

### Good Example
**입력:** `--mode estimate`

**기대 동작:**
1. predicted.json + ticket-map 로드 → p50/p90 인용 코멘트 생성
2. 코멘트 전문 표시 → 사용자 승인 → add_issue_comment

### Bad Example
**입력:** `--mode estimate` (predicted.json 없음)

**기대 동작:** "predicted.json 없음 — sprint --step plan 먼저. ticket-bridge는 추정을 계산하지 않습니다." fail loud

### Bad Example
**입력:** `--mode pull #99` (size/* 라벨 없는 이슈)

**기대 동작:** "#99: size/* 라벨 없음 — 하나 지정하세요. LLM 추론으로 complexity를 추측하지 않습니다." fail loud
