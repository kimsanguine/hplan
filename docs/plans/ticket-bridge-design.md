# ticket-bridge 설계 — GitHub Issues ⇄ hplan 실행 레이어 연결

> 작성일: 2026-06-01
> 상태: Draft (설계 문서, 미구현)
> 작성자: Claude
> 대상 스킬: `deliver/skills/ticket-bridge` (신규 1개)

---

## 1. 문제 정의

hplan의 실행 레이어(`sprint`, `conductor`)는 **닫힌 로컬 파일 세계**에서만 작동한다.

- `sprint`은 `.track/predicted.json`을 쓰고 `profiles/<op>/velocity/baseline.jsonl`을 읽는다.
- `conductor`는 `harness/implementation-plan.md` 태스크를 순차 실행하고 `harness/PROGRESS.md`에 기록한다.
- 두 스킬 모두 **system of record(SoR)** — 실제 팀이 보는 티켓 — 와 연결되지 않는다.

이 단절은 레포 자체에서 경험적으로 확인된다 (2026-06-01 검증):

| 관찰 | 사실 | 의미 |
|---|---|---|
| GitHub Issues | 0개 | WBS의 입력 소스가 없음 — `sprint --step plan`은 PRD 텍스트만 먹는다 |
| PR 머지 | squash-merge, 초 단위 자동 머지 (merge commit 0개, 총 50 commit) | PR이 추적 단위로 살아있지 않음 — 상태를 되돌려 쓸 곳이 없음 |
| `baseline.jsonl` | 레포 전체에 0개 (`profiles/`는 `_template`만 존재) | estimate lookup의 기준 데이터 자체가 없음 → fallback만 돈다 |

즉 hplan은 "추적 규율"을 설파하면서 **자기 자신을 dogfooding하지 않는다**. 추정치는 로컬 JSON에 갇히고, 팀이 보는 티켓에는 hplan이 계산한 p50/p90 / 진척 / 블로커가 전혀 흘러가지 않는다.

원하는 페르소나: **"티켓에 접근 가능한 technical PM"** — 티켓을 끌어와 WBS/추정에 매핑하고, 코드베이스 상태를 읽어, 상태·추정을 티켓에 **되돌려 쓰는** 에이전트.

---

## 2. 스킬 경계 (scope)

단일 신규 스킬 `deliver/skills/ticket-bridge`. **모드 3개 고정. 더 늘리지 않는다 (Rule 2).**

| 모드 | 책임 | 입력 → 출력 |
|---|---|---|
| `--mode pull` | GitHub Issues → WBS 태스크 후보 (sprint가 먹을 수 있는 형태) | `list_issues` → `harness/ticket-import.md` |
| `--mode status` | `.track/` + git/PR 상태 읽어 → issue에 진척 코멘트 백 | `.track/` + `list_commits`/`pull_request_read` → `add_issue_comment` |
| `--mode estimate` | `predicted.json`의 p50/p90 → issue에 추정 코멘트/라벨 부착 | `.track/predicted.json` → `add_issue_comment` (+ 선택적 라벨) |

### 한다 (does)

- GitHub Issue body/label/state를 읽어 sprint의 WBS 입력으로 **변환만** 한다.
- 이미 계산된 `.track/predicted.json`·`actual_log.jsonl` 값을 issue 코멘트로 **전달만** 한다.
- 결정론 매핑(§6)으로 label/state → complexity bucket → baseline lookup을 수행한다.

### 명시적으로 안 한다 (does NOT)

- **추정치를 직접 계산하지 않는다.** lookup·전달만. 수치 생성은 `sprint --step plan`의 책임 (Rule 5 경계 보존).
- **태스크를 실행하지 않는다.** 실행은 `conductor`. ticket-bridge는 read/translate/write-back만.
- **GitHub API client를 새로 짜지 않는다.** 기존 GitHub MCP 도구만 쓴다 (§4).
- **Issue를 생성/수정/종료하지 않는다** (`issue_write` open/close 트랜지션 제외 — §4 참조). 본문 편집·삭제 없음.
- **PR을 머지/생성하지 않는다.** PR 상태는 read-only.
- **멀티 레포 / 자동 라벨 생성 / 양방향 실시간 sync는 v1 범위 밖** (§8 미해결 질문).

---

## 3. 데이터 흐름

```
                  ┌──────────────────────────────────────────────┐
                  │                ticket-bridge                  │
                  │            (deliver/skills/)                  │
                  └──────────────────────────────────────────────┘
                       ▲              │                 ▲
   GitHub Issues       │              │                 │
   (system of record)  │              ▼                 │
   ┌──────────┐        │       ┌──────────────┐         │
   │  Issue   │──pull──┘       │   sprint     │         │
   │  body    │  (read)        │  .track/     │         │
   │  labels  │                │ predicted.json│        │
   │  state   │◀──status──┐    │ actual_log    │        │
   └──────────┘  (write   │    └──────────────┘         │
        ▲         back)   │            │                 │
        │                 │            ▼                 │
        └────estimate─────┘     ┌──────────────┐         │
          (write back)          │  conductor   │─────────┘
                                │ 태스크 실행   │  (git/PR 상태 생성)
                                └──────────────┘
```

방향 정리 (화살표 = 데이터 흐름 방향):

| 화살표 | 방향 | 모드 | 내용 |
|---|---|---|---|
| Issue → ticket-bridge → sprint | 단방향 (right) | `pull` | Issue body/label/state → WBS 태스크 후보 |
| sprint(.track) → ticket-bridge → Issue | 단방향 (left, write-back) | `estimate` | predicted.json p50/p90 → Issue 코멘트 |
| .track + conductor(git/PR) → ticket-bridge → Issue | 단방향 (left, write-back) | `status` | actual_log + git/PR 상태 → Issue 코멘트 |

핵심: ticket-bridge는 **번역기**다. sprint/conductor의 내부 포맷을 GitHub 포맷으로, 또는 그 반대로 바꿀 뿐 어느 쪽 데이터도 *생성*하지 않는다. 양방향처럼 보이지만 각 모드는 단방향이다 (실시간 sync 아님).

---

## 4. GitHub 통합 메커니즘

**원칙 (Rule 1 — 외부 스키마 검증):** 새 API client 코드를 짜지 않는다. 환경에 이미 있는 GitHub MCP 도구를 그대로 호출한다. Issue/PR의 스키마는 GitHub의 것이므로 **추측 금지** — 아래 필드만 읽고 쓴다.

### 사용 MCP 도구 + 읽고/쓰는 필드

| MCP 도구 | 모드 | R/W | 사용 필드 (GitHub 스키마) |
|---|---|---|---|
| `mcp__github__list_issues` | pull | R | `number`, `title`, `body`, `labels[].name`, `state` |
| `mcp__github__issue_read` | pull, status, estimate | R | 단일 issue의 `body`, `labels`, `state`, `number` |
| `mcp__github__list_commits` | status | R | `sha`, `commit.message` (태스크 ID 매칭용) |
| `mcp__github__pull_request_read` | status | R | `state`, `merged`, `head.ref`, `body` |
| `mcp__github__add_issue_comment` | status, estimate | W | `body` (마크다운 코멘트 본문) |
| `mcp__github__issue_write` | status (선택) | W | `state` 전환만 (`open`↔`closed`). **body/title 편집 금지** |

> Rule 1 명시: **Issue의 schema = body(텍스트) + labels(문자열 배열) + state(`open`/`closed`)**. ticket-bridge는 이 3개 필드 외 어떤 키도 읽거나 쓰지 않는다. 커스텀 필드/projects v2 필드는 v1 범위 밖.

### write-back 형식 (코멘트만, 본문 비파괴)

상태·추정은 **새 코멘트**로 추가한다 (issue body를 덮어쓰지 않음 — 비파괴 원칙):

```markdown
<!-- hplan:ticket-bridge -->
## hplan estimate (T-003 ↔ #42)
- complexity: 3 (label `complexity:M`에서 매핑)
- LOC p50/p90: 95 / 240
- tokens p50/p90: 9100 / 18500
- minutes p50/p90: 17 / 38
- baseline_ref: 2026-05-17T... (trust_grade: B)
> 출처: .track/predicted.json — sprint --step plan 산출. ticket-bridge는 전달만 함.
```

`<!-- hplan:ticket-bridge -->` 마커로 자기 코멘트를 식별 → 중복 코멘트 방지(같은 마커+같은 태스크 ID 코멘트가 있으면 새로 달지 않고 스킵 또는 안내).

라벨 부착(estimate, 선택): 기존에 존재하는 `estimate:p50-*` 류 라벨이 있을 때만 부착. **라벨을 새로 생성하지 않는다** (§7 fail loud).

---

## 5. Rule 5 준수 경계 표

sprint/SKILL.md의 표 스타일을 그대로 따른다.

| 작업 | LLM 사용 | 근거 |
|---|---|---|
| Issue body → 태스크 후보 분해 (pull) | ✅ 분류 | 자연어 텍스트 → sub-task 분류. sprint WBS와 동일 성격 |
| Issue 한 줄 요약 → 코멘트 산문 생성 (status/estimate) | ✅ 자연어 생성 | Rule 5 허용: 자연어 렌더링 |
| **label/state → complexity bucket 매핑** | ❌ **결정론 lookup** | §6 순수 매핑 테이블. LLM 금지 |
| **complexity → baseline percentile lookup** | ❌ **결정론 lookup** | sprint Step 4와 동일. baseline.jsonl 직접 인용 |
| **issue state → open/closed 전환 판단** | ❌ 결정론 | `.track` 완료 이벤트 유무 → 상태 매핑. if-statement를 LLM으로 대체 금지 |
| **commit/PR ↔ 태스크 매칭** | ❌ 결정론 | commit message·branch명의 태스크 ID 정규식 매칭 |
| **중복 코멘트 감지** | ❌ 결정론 | 마커 문자열 + 태스크 ID grep |
| **라벨 라우팅 (어느 라벨을 달지)** | ❌ 결정론 | §6 매핑 결과를 라벨명으로 직결 |

> **자체 점검:** label→complexity, complexity→estimate, state 전환, commit 매칭, 라벨 라우팅에서 LLM 호출이 감지되면 즉시 fail — Rule 5 위반 (sprint Step 4와 동일 규율).

---

## 6. 결정론적 매핑 규칙

전 과정 순수 lookup. LLM 호출 0.

### 6.1 label/state → complexity bucket

라벨 taxonomy는 **설정 가능해야 하지만 v1 기본값을 고정**한다 (taxonomy 선택은 §8 미해결 질문). 기본 매핑:

| Issue 신호 | complexity bucket | 비고 |
|---|---|---|
| label `complexity:XS` 또는 `size:XS` | 1 | |
| label `complexity:S` / `size:S` | 2 | |
| label `complexity:M` / `size:M` | 3 | |
| label `complexity:L` / `size:L` | 4 | |
| label `complexity:XL` / `size:XL` | 5 | |
| 매핑 라벨 없음 + body 존재 | (보류) | LLM 분류로 **fallback하지 않는다** — §7 ambiguous label fail loud |

> 라벨이 두 개 이상 매핑되면(`size:S` + `complexity:L` 동시) → ambiguous, fail loud (§7). 임의 선택 금지.

### 6.2 complexity → baseline lookup (sprint Step 4와 동일)

```python
# LLM 호출 0 — baseline.jsonl 직접 인용
row = baseline[complexity]   # 1..5
est = {
    "loc_p50": row["loc_p50"],   "loc_p90": row["loc_p90"],
    "tokens_p50": row["tokens_p50"], "tokens_p90": row["tokens_p90"],
    "minutes_p50": row["minutes_p50"], "minutes_p90": row["minutes_p90"],
}
```

ticket-bridge는 이 lookup을 **직접 수행하지 않는 것이 원칙**이다 — `predicted.json`이 이미 있으면 그 값을 읽어 전달한다. `predicted.json`이 없을 때만(estimate 모드 단독 실행) 위 lookup을 수행하되, **sprint와 동일한 baseline.jsonl 경로를 공유**한다.

### 6.3 state 매핑 (status 모드, 선택적 close)

```
.track/actual_log.jsonl 에서 해당 태스크의 event=="complete" 존재?
  → 있음: issue가 open이면 issue_write state=closed 후보 (단, §8 자동 close 정책 미정 → 기본은 코멘트만, --close 플래그로만 전환)
  → 없음: 상태 변경 없음, 진척 코멘트만
```

### 6.4 라벨 라우팅

§6.1 매핑 결과(complexity bucket)를 그대로 라벨명으로 직결. 예: bucket 3 → `complexity:M`. 해당 라벨이 레포에 **이미 존재할 때만** 부착(§7).

---

## 7. 실패 모드 (fail loud)

sprint의 Failure Handling 표 스타일.

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| `baseline.jsonl` 없음 (estimate 단독) | file not found | **fail loud**: "baseline 없음 — `sprint --step plan` 먼저 실행하거나 velocity-baseline 생성 필요. ticket-bridge는 추정을 *계산*하지 않음." (conservative fallback도 sprint 책임) |
| ambiguous label | §6.1에서 매핑 라벨 0개 또는 2개+ | **fail loud**: 해당 issue 번호 + 충돌 라벨 나열 → "complexity 라벨을 하나만 지정하세요." 임의 선택·LLM 추론 금지 |
| MCP 도구 미사용 가능 | `mcp__github__*` 호출 실패/미등록 | **fail loud**: "GitHub MCP 미연결 — 환경에 github MCP server 등록 필요. ticket-bridge는 대체 API client를 만들지 않음." 로컬 파일 작업으로 silent degrade 금지 |
| write-back 권한 없음 | `add_issue_comment`/`issue_write` 403/권한 에러 | **fail loud**: "issue write 권한 없음 (read-only token?) — pull/계산은 완료됨, write-back만 실패. 결과를 stdout으로 출력하니 수동 첨부 가능." 계산 결과는 보존 |
| `.track/predicted.json` 없음 (estimate) | file not found | fail loud: "`sprint --step plan` 먼저 — 전달할 추정치 없음" |
| `.track/actual_log.jsonl` 없음 (status) | file not found | fail loud: "`sprint --step init` 먼저 — 전달할 진척 없음" (sprint status와 동일 규율) |
| 중복 코멘트 | 마커+태스크 ID 이미 존재 | skip + 안내 (덮어쓰기/중복 금지) |
| issue ↔ 태스크 매칭 실패 | commit/branch에 태스크 ID 정규식 미스 | 해당 태스크 "매칭 불가"로 표시, 나머지는 진행 (부분 성공 명시 — Rule 8) |

원칙: **계산 단계와 write-back 단계를 분리**한다. write-back이 실패해도 계산 결과는 stdout으로 surface한다 — "complete"로 거짓 보고하지 않는다 (Rule 8).

---

## 8. 미해결 질문 (human 판단 필요)

1. **라벨 taxonomy** — §6.1 기본값은 `complexity:*` / `size:*` 두 관례를 가정했다. 실제 팀은 어느 라벨 체계를 쓰는가? 둘 다 없으면 매핑 불가다. taxonomy를 `profiles/<op>/`의 yaml로 빼야 하는가, 스킬에 하드코딩해도 되는가?
2. **자동 코멘트 vs 확인 요청** — status/estimate write-back을 자동으로 달 것인가, 매번 사용자 확인을 거칠 것인가? 현재 §6.3은 자동 close를 `--close` 플래그로만 제한했지만, 코멘트 자체도 confirm 게이트가 필요한가? (PM 페르소나 신뢰도 vs 노이즈 트레이드오프)
3. **멀티 레포** — hplan 한 레포 기준으로 설계했다. 한 PRD가 여러 레포에 걸치면(monorepo 아님) issue source가 분산된다. v1은 단일 레포로 못박는 게 맞는가?
4. **태스크 ↔ issue 매칭 키** — §6.3/6.4는 commit message·branch명의 태스크 ID(T-001) 정규식 매칭을 가정한다. 실제로 commit이 태스크 ID를 담는 컨벤션이 있는가? 없다면 issue number ↔ predicted.json task id를 무엇으로 잇는가 (수동 매핑 테이블 `harness/ticket-map.json`?).
5. **baseline 부재 현실** — 레포에 `baseline.jsonl`이 0개다. ticket-bridge estimate는 sprint가 baseline을 만든 *이후에만* 의미가 있다. 닭-달걀 문제 — 첫 도입 시 estimate 모드를 비활성화하고 pull/status만 먼저 굴리는 단계적 롤아웃이 맞는가?

---

## 효과/리스크 정직한 평가

구현 난이도는 **낮음~중간**이다 — 신규 API client가 없고(MCP 재사용), 추정 계산도 sprint에서 빌려오므로 ticket-bridge의 고유 코드는 사실상 (a) MCP 호출 래핑, (b) §6 결정론 매핑 테이블, (c) 코멘트 마크다운 렌더링 세 덩어리뿐이다. 개발자 한 명이 하루에 SKILL.md + 매핑 규칙을 구현할 수 있다. 가장 큰 리스크는 **기술이 아니라 데이터다**: baseline.jsonl이 없고 라벨 taxonomy가 정해지지 않은 상태에서는 estimate/매핑 모드가 전부 fail loud로 떨어진다(§7). 즉 이 스킬의 진짜 선결 조건은 코드가 아니라 §8의 1·4·5번 질문에 대한 사람의 답이며, 그것 없이 구현부터 하면 "잘 동작하는데 쓸 데이터가 없는" 스킬이 된다 — hplan이 dogfooding을 못 하는 현재 상태의 정확한 반복이다.
