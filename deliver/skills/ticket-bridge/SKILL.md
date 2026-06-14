---
name: ticket-bridge
description: "GitHub Issues / Linear / Jira ⇄ hplan 실행 레이어(sprint/.track) 번역기. --mode pull(Issues→WBS 후보), --mode estimate(predicted.json p50/p90 → 이슈 코멘트), --mode status(.track+git/PR 상태 + CI/CD + PR review → 이슈 코멘트), --mode push(WBS 태스크 → 이슈 생성). --system github|linear|jira로 대상 시스템 선택. --batch 플래그: write-back 확인 게이트를 전체 요약 1회로 묶음 (개별 게이트 스킵). 추정치를 직접 계산하지 않고 sprint 산출물을 전달만 한다. Use when syncing GitHub/Linear/Jira tickets with hplan sprint tracking, or when a PM wants estimates/progress written back onto issues."
argument-hint: "[--mode pull|estimate|status|push] [--system github|linear|jira] [--batch] [issue numbers or filter]"
allowed-tools: ["Read", "Write", "Bash",
  "mcp__github__list_issues", "mcp__github__issue_read", "mcp__github__list_commits",
  "mcp__github__pull_request_read", "mcp__github__add_issue_comment", "mcp__github__issue_write",
  "mcp__github__get_pull_request_reviews", "mcp__github__get_pull_request_status",
  "mcp__github__create_issue",
  "mcp__linear__list_issues", "mcp__linear__get_issue", "mcp__linear__create_comment",
  "mcp__linear__update_issue", "mcp__linear__create_issue",
  "mcp__jira__list_issues", "mcp__jira__add_comment", "mcp__jira__create_issue"]
model: inherit
---

## Core Goal

GitHub Issues / Linear / Jira(system of record)와 hplan의 닫힌 실행 레이어(`sprint`의 `.track/`)를 잇는다.
ticket-bridge는 **번역기**다 — 추정치나 진척을 *생성*하지 않고, sprint/conductor의 산출물을 티켓 시스템 포맷으로 전달하거나 그 반대로 변환만 한다.

| 모드 | 책임 | 입력 → 출력 | LLM |
|---|---|---|---|
| `--mode pull` | 이슈 → WBS 태스크 후보 | `list_issues` → `harness/ticket-import.md` | ✅ body 분해만 |
| `--mode estimate` | `predicted.json` p50/p90 → 이슈 코멘트 | `.track/predicted.json` + `ticket-map.json` → `add_comment` | ✅ 산문만 |
| `--mode status` | `.track/` + git/PR/CI/review 상태 → 이슈 코멘트 | `actual_log.jsonl` + `list_commits`/`pull_request_read` → `add_comment` | ✅ 산문만 |
| `--mode push` | WBS 태스크 → 이슈 생성 | `harness/ticket-import.md` + `ticket-map.json` → `create_issue` | ✅ 제목/설명 생성만 |

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
- 지정한 `--system`의 MCP 미연결 → fail loud (대체 API client 만들지 않음)
- write-back 전 항상 **사용자 확인 게이트** 통과 (자동 코멘트 금지)

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--mode` | `$ARGUMENTS` | pull/estimate/status 분기 |
| `--system` | `$ARGUMENTS` | github(기본)/linear/jira 선택 |
| issue 번호/필터 | `$ARGUMENTS` 나머지 | 대상 이슈 선택 |
| `.track/predicted.json` | sprint plan 산출 | estimate 전달 소스 |
| `.track/actual_log.jsonl` | sprint init+probe | status 전달 소스 |
| `harness/ticket-map.json` | pull 산출 또는 수동 | 태스크 ID ↔ 이슈 번호 매핑 |

`$ARGUMENTS`를 파싱해 mode, system, 대상을 분리한다.

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

- `size/*` 라벨이 **0개** → "매핑 불가 — 해당 이슈 skip, 나머지 진행" (부분 성공 명시 — Rule 8).
  complexity는 보수적 fallback 3으로 처리하되 estimate 코멘트에 "라벨 미설정 — p50/p90 신뢰도 낮음" 명시. LLM 추론으로 complexity를 추측하는 것은 금지.
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

### 공통 Step 0 — mode·system 파싱

```
args = parse("$ARGUMENTS")
mode   = args.get("--mode")    # 없으면 fail loud
system = args.get("--system", "github")  # 기본값 github
```

mode 미명시 시:
> "--mode 미명시 — 사용 가능: `--mode pull|estimate|status`. auto-run하지 않습니다."

#### --batch 플래그

`--batch` 있으면: 개별 확인 게이트를 건너뛰고 전체 목록을 한 번에 표시 후 일괄 승인 (1회)

| 모드 | --batch 없음 | --batch 있음 |
|---|---|---|
| estimate | 이슈별 코멘트 초안 개별 확인 | 전체 코멘트 목록 일괄 승인 1회 |
| status | 이슈별 코멘트 초안 개별 확인 | 전체 코멘트 목록 일괄 승인 1회 |
| push | 이슈별 생성 초안 개별 확인 | 전체 생성 목록 일괄 승인 1회 |

- 개별 항목 문구를 수정하고 싶다면 --batch 없이 실행

`--batch` 없으면 (기본): 이슈별 개별 확인 게이트 유지

#### --system 플래그 파싱 (결정론)

| --system 값 | 사용 도구 | 비고 |
|---|---|---|
| `github` (기본) | `mcp__github__*` | 기존 동작 |
| `linear` | `mcp__linear__*` | Linear MCP 연결 필요 |
| `jira` | `mcp__jira__*` | Jira MCP 연결 필요 |

지정한 --system의 MCP 도구 가용성을 먼저 확인한다. 미연결이면:
> "지정한 --system의 MCP가 연결되지 않았습니다. (`--system linear` → Linear MCP, `--system jira` → Jira MCP)"

--system 미명시 시 github 기본값 사용. 도구 이름만 바뀌며 이후 로직은 동일하다.

#### --system jira 사전 설정 가이드

`--system jira`를 사용하려면 Jira MCP 서버를 Claude Code에 등록해야 한다. Jira Cloud와 Jira Server(Data Center)는 인증 방식이 다르다.

**Jira Cloud (Atlassian Cloud)**

```bash
# 1. API Token 발급: https://id.atlassian.com/manage-profile/security/api-tokens
# 2. claude settings.json에 MCP 서버 등록
claude mcp add jira-cloud \
  --transport sse \
  --url https://mcp.atlassian.com/v1/sse
# Atlassian Remote MCP는 OAuth 2.0 브라우저 인증 — 토큰 파일 불필요
```

또는 로컬 MCP 래퍼를 사용하는 경우:
```json
// ~/.claude/settings.json → mcpServers 항목에 추가
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_BASE_URL": "https://yourcompany.atlassian.net",
        "JIRA_EMAIL": "you@yourcompany.com",
        "JIRA_API_TOKEN": "<API_TOKEN>"
      }
    }
  }
}
```

**Jira Server / Data Center (온프레미스)**

```json
// ~/.claude/settings.json → mcpServers 항목에 추가
{
  "mcpServers": {
    "jira": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-jira"],
      "env": {
        "JIRA_BASE_URL": "https://jira.internal.yourcompany.com",
        "JIRA_PAT": "<PERSONAL_ACCESS_TOKEN>"
      }
    }
  }
}
```

> Jira Server/DC는 API Token 대신 PAT(Personal Access Token)을 사용한다. Jira 7.2+ 에서 지원.

**Jira Cloud/Server 공통 필드 차이**

ticket-bridge가 `--system jira`로 동작할 때 아래 Jira 전용 필드를 코멘트에 포함한다:

| 필드 | ticket-bridge 동작 |
|---|---|
| `story_points` | `.track/predicted.json`의 p50 값을 스토리 포인트 후보로 명시 (PM이 Jira 필드에 직접 입력, 자동 설정 0) |
| `sprint` | `.track/implementation-plan.md`의 sprint 컬럼 값을 인용 (Jira sprint 이름과 일치 여부는 PM 확인) |
| `issue_type` | pull 모드에서 Jira `issuetype` 필드 읽기 지원 (Bug / Story / Task / Sub-task) |
| `priority` | pull 모드에서 Jira `priority` 필드 읽기 지원 |

> **사내 Jira 커스텀 필드:** 조직마다 `customfield_10016` 등 커스텀 필드명이 다르다. ticket-bridge는 기본 필드만 지원하며, 커스텀 필드 매핑이 필요하면 `harness/ticket-map.json`에 `"jira_custom_fields"` 키로 매핑 테이블을 수동 작성한다.

---

### mode: pull

1. `list_issues` 도구로 대상 이슈를 읽는다 (필드: `number`, `title`, `body`, `labels[].name`, `state`).
2. 각 이슈 body를 WBS 태스크 후보로 분해한다 (LLM 분류 — sprint WBS와 동일).
3. 각 이슈의 `size/*` 라벨 → complexity bucket (결정론 매핑).
   - `size/*` 0개 → 해당 이슈 skip, 나머지 계속 진행 (fallback complexity 3, 신뢰도 낮음 명시).
4. `harness/ticket-import.md`에 태스크 후보 + complexity + 원본 이슈 번호를 기록한다.
5. `harness/ticket-map.json`에 태스크 ID ↔ 이슈 번호 매핑을 append (덮어쓰기 금지).
6. 다음 단계 안내: "`sprint --step plan harness/ticket-import.md`로 추정치를 계산하세요. ticket-bridge는 추정을 계산하지 않습니다."

> pull은 티켓 시스템에 **아무것도 쓰지 않는다** (read-only).

#### Jira 커스텀 필드 반자동 제안 (--system jira)

pull 모드에서 이슈를 읽을 때:
1. `mcp__jira__list_issues` 응답의 `fields` 객체에서 `customfield_*` 키를 결정론으로 추출 (json keys grep)
2. `harness/ticket-map.json`에 `custom_fields` 섹션이 없으면:
   ```
   발견된 커스텀 필드 목록:
   - customfield_10016 (sprint)
   - customfield_10014 (epic_link)
   - customfield_10028 (story_points)
   
   harness/ticket-map.json의 custom_fields에 추가할까요? [y/N]
   ```
3. 승인 시 ticket-map.json에 append:
   ```json
   "custom_fields": {
     "sprint": "customfield_10016",
     "epic_link": "customfield_10014",
     "story_points": "customfield_10028"
   }
   ```
4. 이후 estimate/status에서 story_points 필드를 코멘트에 포함.

> 이미 custom_fields가 ticket-map에 있으면 이 단계를 건너뛴다.

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

5. **확인 게이트**: 작성할 코멘트 전문을 사용자에게 보여주고 명시적 승인을 받는다. 승인 전 `add_comment` 호출 금지.
6. 승인 후 `add_comment`로 작성. `<!-- hplan:ticket-bridge -->` 마커 + 같은 태스크 ID 코멘트가 이미 있으면 skip + 안내.

---

### mode: status

1. `.track/actual_log.jsonl` 로드. 없으면 fail loud ("`sprint --step init` 먼저").
2. `harness/ticket-map.json`으로 태스크 ↔ 이슈 매칭.
3. 각 태스크의 진척을 결정론 집계 (complete 이벤트 유무, 경과, 블로커 수). 수치 생성 금지 — actual_log 값 인용.
4. ticket-map의 이슈 번호로 `list_commits`/`pull_request_read`를 조회해 관련 commit/PR 상태를 매칭 (정규식).

4-b. (선택) CI/CD 상태 수집:
   commit/PR 매칭 후 해당 PR의 check run 결과를 조회한다:
   `mcp__github__get_pull_request_status` → CI: ✅ PASS / ❌ FAIL / ⏳ PENDING
   결과를 status 코멘트에 한 줄로 포함한다. (`--system linear/jira`에서는 이 단계를 skip한다.)

4-c. (선택) PR review 상태 수집:
   `mcp__github__get_pull_request_reviews` → APPROVED / CHANGES_REQUESTED / PENDING
   리뷰어 수와 상태를 status 코멘트에 포함한다. (`--system linear/jira`에서는 이 단계를 skip한다.)

5. 진척 코멘트 본문을 만든다 (마커 포함).
6. **확인 게이트**: 코멘트 전문 + (선택) `--close` 플래그 시 상태 전환 후보를 사용자에게 보여주고 승인받는다.
7. 승인 후 `add_comment`. `--close` 플래그가 있고 모든 매칭 태스크가 complete면 해당 이슈를 closed 상태로 전환 (본문/제목 편집 금지).

---

### mode: push

> sprint --step plan 또는 harness/implementation-plan.md의 WBS 태스크를 실제 이슈로 생성한다.
> pull의 반대 방향 — hplan에서 외부 트래커로 내보내기.

1. `harness/implementation-plan.md` 또는 `harness/ticket-import.md` 로드. 없으면 fail loud.
2. 각 태스크에 대해 이슈 제목/설명 생성 (LLM — 자연어 생성).
3. complexity bucket → `size/*` 라벨 결정론 역매핑 (T1의 lookup 역순):
   ```
   1 → size/XS, 2 → size/S, 3 → size/M, 4 → size/L, 5 → size/XL
   ```
4. **확인 게이트**: 생성할 이슈 목록 전체를 보여주고 승인받는다. --batch 없으면 이슈별 개별 확인, --batch 있으면 전체 목록 1회 일괄 승인 (--batch 섹션 참조).
5. 승인 후 `create_issue`(system별 도구)로 이슈 생성. `ticket-map.json`에 태스크 ID ↔ 이슈 번호 append.
6. 이미 ticket-map에 해당 태스크가 있으면 skip + 안내 (중복 생성 금지).

> push는 create만 한다 — 기존 이슈 편집/삭제 금지.

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| `--mode` 미명시 | 미입력 | fail loud + 모드 목록 |
| 지정 system MCP 미연결 | `mcp__{system}__*` 미등록/실패 | fail loud — 대체 client 안 만듦, silent degrade 금지 |
| `size/*` 라벨 0개 (pull/estimate) | 라벨 매핑 결과 없음 | 해당 이슈 skip, 나머지 진행 + fallback complexity 3 + "라벨 미설정 — p50/p90 신뢰도 낮음" 명시 (Rule 8). LLM 추론 금지 |
| `size/*` 라벨 2개+ | 라벨 매핑 충돌 | fail loud + 충돌 라벨 나열. 임의 선택 금지 |
| `predicted.json` 없음 (estimate) | file not found | fail loud — "sprint --step plan 먼저, 전달할 추정치 없음" |
| `actual_log.jsonl` 없음 (status) | file not found | fail loud — "sprint --step init 먼저" |
| ticket-map 매핑 누락 | 태스크 ID 키 없음 | 해당 태스크 "매칭 불가" 표시, 나머지 진행 (부분 성공 명시) |
| write-back 권한 없음 | `add_comment` 403 | fail loud — "issue write 권한 없음. 계산 결과는 stdout으로 출력하니 수동 첨부 가능" — 거짓 done 금지 |
| 중복 코멘트 | 마커+태스크 ID 존재 | skip + 안내 (덮어쓰기 금지) |
| 확인 게이트 거부 | 사용자 미승인 | write-back 취소, 본문은 stdout 보존 |
| create_issue 권한 없음 | 403 | fail loud — "issue create 권한 없음. 수동 생성 필요" — 생성 목록 stdout 출력 |
| 태스크 ticket-map 이미 존재 | 키 충돌 | skip + "이미 이슈 #N와 매핑됨" 안내 |

원칙: **계산 단계와 write-back 단계 분리**. write-back이 실패/거부돼도 계산 결과는 stdout으로 surface — "complete"로 거짓 보고하지 않는다 (Rule 8).

---

## Quality Gate

### pull
- [ ] 티켓 시스템에 write 0회 (read-only)
- [ ] 모든 이슈 size/* → complexity 매핑됨 또는 skip+fallback 명시 (LLM 매핑 0)
- [ ] `harness/ticket-map.json` append (덮어쓰기 0)

### estimate
- [ ] 모든 수치 = predicted.json 인용값 (계산 0)
- [ ] write-back 전 확인 게이트 통과
- [ ] 마커 + 중복 코멘트 감지 동작

### status
- [ ] 진척 수치 = actual_log 인용 (생성 0)
- [ ] commit/PR 매칭 = 정규식 (LLM 0)
- [ ] CI/CD 상태 = `get_pull_request_status` 인용 (github 모드)
- [ ] PR review 상태 = `get_pull_request_reviews` 인용 (github 모드)
- [ ] write-back 전 확인 게이트 통과

### push
- [ ] ticket-map에 이미 있는 태스크 skip (중복 생성 0)
- [ ] 이슈 생성 전 확인 게이트 통과
- [ ] size/* 라벨 역매핑 = 결정론 (LLM 0)

---

## Examples

### Good Example
**입력:** `--mode pull #42 #43`

**기대 동작:**
1. 이슈 2개 read → body 분해 (LLM) → size/* → complexity (결정론)
2. `harness/ticket-import.md` + `harness/ticket-map.json` 기록
3. 티켓 시스템 write 0회, "sprint --step plan으로 추정 계산" 안내

### Good Example
**입력:** `--mode pull #99` (size/* 라벨 없는 이슈)

**기대 동작:** "#99: size/* 라벨 없음 — skip하고 나머지 진행. fallback complexity 3 사용, estimate 신뢰도 낮음." 부분 성공 명시

### Good Example
**입력:** `--mode estimate`

**기대 동작:**
1. predicted.json + ticket-map 로드 → p50/p90 인용 코멘트 생성
2. 코멘트 전문 표시 → 사용자 승인 → add_comment

### Good Example
**입력:** `--mode status --system linear`

**기대 동작:**
1. Linear MCP 가용성 확인 → mcp__linear__* 도구로 이슈 조회
2. actual_log + ticket-map 기반 진척 집계 (CI/CD·PR review 단계는 skip — linear 모드)
3. 확인 게이트 → mcp__linear__create_comment로 코멘트 작성

### Bad Example
**입력:** `--mode estimate` (predicted.json 없음)

**기대 동작:** "predicted.json 없음 — sprint --step plan 먼저. ticket-bridge는 추정을 계산하지 않습니다." fail loud

### Bad Example
**입력:** `--mode pull #99` (size/* 라벨 2개: size/S, size/M)

**기대 동작:** "#99: size/* 라벨 충돌 (size/S, size/M) — 하나만 남기고 재시도하세요. 임의 선택하지 않습니다." fail loud
