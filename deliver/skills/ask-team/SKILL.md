---
name: ask-team
description: "PM이 사람에게 질문하고 답을 모으는 비동기 채널 — comms MCP(Gmail/Notion/Zoom/Slack)를 감싸는 번역기. --mode ask(질문 초안 작성), --mode pull-answers(스레드·회의록에서 답 수집), --mode digest(수집한 답 요약 → decision-log/ticket-bridge 라우팅), --mode solo(팀원 없을 때 Claude가 역할 대리 시뮬레이션), --mode init(팀 세팅 대화형 온보딩). 메시지를 자동 발송하지 않는다 — 초안/코멘트까지만. Use when a PM needs to ask teammates for status/decisions and collect their answers into hplan."
argument-hint: "[--mode ask|pull-answers|digest|solo|init] [question or topic]"
allowed-tools: ["Read", "Write",
  "mcp__gmail__create_draft", "mcp__gmail__search_threads", "mcp__gmail__get_thread",
  "mcp__notion__notion-create-comment", "mcp__notion__notion-get-comments",
  "mcp__notion__notion-create-pages", "mcp__notion__notion-update-page", "mcp__notion__notion-search",
  "mcp__zoom__search_meetings", "mcp__zoom__get_file_content",
  "mcp__zoom__get_recording_resource", "mcp__zoom__search_zoom", "mcp__zoom__get_meeting_assets",
  "mcp__slack__post_message", "mcp__slack__search_messages", "mcp__slack__get_thread_replies"]
model: sonnet
---

## Core Goal

PM이 "사람에게 질문하고 답을 받는" 기둥을 hplan에 연결한다.
ask-team은 **번역기**다 — 질문/요약 문구만 생성하고, 외부 comms 시스템(Gmail/Notion/Zoom/Slack)을 통한 전달·수집은 MCP 도구에 위임한다. 답을 *판단*하거나 메시지를 *자동 발송*하지 않는다.

| 모드 | 책임 | 입력 → 출력 |
|---|---|---|
| `--mode ask` | 질문 초안 작성 (발송 X — 사람이 보냄) | 질문 + 대상 → Gmail `create_draft` / Notion 코멘트 / Slack 메시지 미리보기 |
| `--mode pull-answers` | 스레드·회의록·코멘트에서 답 수집 | `search_threads`/Zoom transcript/`get-comments`/`get_thread_replies` → `harness/answers.md` |
| `--mode digest` | 수집한 답 요약 → 라우팅 | `harness/answers.md` → `hplan/decision-log` 또는 `deliver/ticket-bridge` |
| `--mode solo` | Claude가 역할 대리 시뮬레이션 | 질문 + 역할 목록 → 역할별 답변 → `harness/answers.md` (simulated 태깅) |

> **기본값**: `--mode` 미명시 → fail loud + 모드 목록. auto-run 금지.

### 능력 차원의 안전장치
Gmail MCP는 `create_draft`만 노출하고 **send 도구가 없다.** ask-team은 구조적으로 메일을 자동 발송할 수 없다 — 초안을 만들면 사람이 Gmail에서 검토 후 보낸다. Slack의 `post_message`는 preview-only로 처리하며 사용자 승인 후에만 호출한다. 확인 게이트가 정책이 아니라 능력으로 강제된다.

---

## Rule 5 준수 경계

| 작업 | LLM 사용 | 근거 |
|---|---|---|
| 질문 문구 생성 (ask) | ✅ 자연어 생성 | Rule 5 허용 |
| 답변 요약 문구 생성 (digest) | ✅ 자연어 생성 | Rule 5 허용 |
| 역할 대리 답변 생성 (solo) | ✅ 자연어 생성 | Rule 5 허용 |
| **대상(수신자) 라우팅** | ❌ **결정론 lookup** | `harness/team-map.json` 매핑 |
| **채널 선택 (Gmail/Notion/Zoom/Slack)** | ❌ 결정론 | 매핑 테이블 — LLM if문 금지 |
| **답변 ↔ 질문 매칭** | ❌ 결정론 | question_id + 스레드/코멘트 ID |
| **digest 라우팅 (decision-log vs ticket-bridge)** | ❌ 결정론 | 답변에 붙은 tag(`#decision`/`#ticket`)로 분기 |

> **자체 점검:** 수신자 라우팅·채널 선택·답변 매칭·digest 분기에서 LLM 호출이 감지되면 즉시 fail — Rule 5 위반. "답변이 긍정인지 LLM이 판단" 같은 것도 금지 (요약만, 판단은 사람).

---

## Trigger Gate

### Use This Skill When
- "이거 팀에 물어봐줘" / "담당자한테 확인 요청" → `--mode ask`
- "답변 왔는지 모아줘" → `--mode pull-answers`
- "받은 답 정리해서 결정 로그/티켓에 붙여줘" → `--mode digest`
- "팀원 없는데 혼자 검토해줘" / "CTO 관점으로 봐줘" → `--mode solo`
- "ask-team 처음 세팅하고 싶어" / "팀원 연락처 등록" → `--mode init`

### Route to Other Skills When
- 결정 기록 자체 → `hplan/decision-log`
- 티켓에 상태 코멘트 → `deliver/ticket-bridge --mode status`
- 고객 인터뷰 합성(디스커버리) → `hplan/interview-synthesis` (ask-team은 *내부 팀* 질문용)

### Boundary Checks
- `--mode` 미명시 → fail loud
- comms MCP 미연결 → fail loud (대체 client 안 만듦)
- 메시지 자동 발송 시도 → 불가 (Gmail send 도구 없음). 초안까지만.
- Slack `post_message` → preview-only, 사용자 승인 후 호출

---

## Inputs

| 입력 | 출처 | 처리 |
|---|---|---|
| `--mode` | `$ARGUMENTS` | ask/pull-answers/digest/solo 분기 |
| 질문/주제 | `$ARGUMENTS` 나머지 | 질문 본문 또는 수집 필터 |
| `harness/team-map.json` | 수동 | 사람 → 채널/주소 매핑 |
| `harness/questions.jsonl` | ask 산출 | question_id ↔ 대상 ↔ 채널 추적 |
| `harness/answers.md` | pull-answers/solo 산출 | digest 입력 |

`$ARGUMENTS`를 파싱해 mode와 대상을 분리한다. comms MCP 가용성을 먼저 확인하고, 없으면 fail loud.

> **MCP 서버명 주의:** allowed-tools는 관례명(`mcp__gmail__*` 등)으로 선언했다. 실제 도구명은 사용자 환경의 MCP 서버 설정에 따라 다르다 — 미발견 시 silent degrade 금지, fail loud로 "어느 comms MCP가 연결됐는지" 안내한다.

---

## 결정론적 라우팅 규칙

### 수신자 → 채널 (순수 lookup, LLM 0)

`harness/team-map.json`:
```json
{ "alex": {"email": "alex@team.com", "channel": "gmail"},
  "design": {"notion_page": "<page-id>", "channel": "notion"},
  "eng": {"slack_channel": "#eng-team", "channel": "slack"} }
```
- 대상이 team-map에 없으면 → fail loud (임의 추측 금지).
- channel 값으로 사용할 MCP 도구를 결정론 분기:
  - `gmail` → `create_draft`
  - `notion` → `notion-create-comment`
  - `slack` → `post_message` (preview-only) → 사용자 승인 후 발송

### 답변 ↔ 질문 매칭
- ask가 `harness/questions.jsonl`에 `{question_id, target, channel, ref_id}`를 기록.
- pull-answers는 ref_id(스레드 ID/코멘트 ID/회의 ID/슬랙 ts)로 답을 역매칭한다.

### digest 라우팅
- 답변 텍스트의 태그로 분기: `#decision` → `hplan/decision-log`, `#ticket:<n>` → `deliver/ticket-bridge`.
- 태그 없으면 → `harness/answers.md`에만 남기고 라우팅 보류 (안내).

---

## Instructions

You are running ask-team with arguments: **$ARGUMENTS**

### 공통 Step 0 — mode 파싱 + MCP 확인
```
mode = args.get("--mode")   # 없으면 fail loud
```
comms MCP 도구 가용성 확인. 하나도 없으면 fail loud.

### mode: ask
1. `harness/team-map.json`으로 대상 → 채널 결정 (결정론). 미매핑 → fail loud.
2. 질문 문구를 생성한다 (LLM — 명확하고 답하기 쉬운 단일 질문).
3. **확인 게이트**: 초안 전문 + 수신자 + 채널을 사용자에게 보여주고 승인받는다.
4. 승인 후 채널별 도구 호출:
   - gmail → `create_draft` (to/subject/body). **발송 아님 — 초안 생성.** 사람이 Gmail에서 보냄.
   - notion → `notion-create-comment` (page/comment).
   - slack → `post_message` **preview-only** 승인 후 발송. 채널은 `team-map.json`의 `slack_channel` 값.
5. `harness/questions.jsonl`에 `{question_id, target, channel, ref_id, ts}` append.
6. 안내: "Gmail 초안 생성됨 — 검토 후 직접 발송하세요. ask-team은 발송하지 않습니다." (Slack은 승인 후 발송.)

### mode: pull-answers
1. `harness/questions.jsonl` 로드. 없으면 fail loud ("ask 먼저").
2. 각 question의 channel/ref_id로 답 조회:
   - gmail → `search_threads`/`get_thread` (해당 스레드의 새 메시지)
   - notion → `notion-get-comments`
   - zoom → **아래 Zoom 회의록 정밀 추출 절차 따름**
   - slack → `get_thread_replies` (ref_id = 스레드 ts)
3. 답을 question_id로 역매칭 (결정론). 매칭 안 되면 "미응답"으로 표시.
4. `harness/answers.md`에 question ↔ answer ↔ 출처를 기록 (요약은 digest에서).

#### Zoom 회의록 정밀 추출

1. `mcp__zoom__search_meetings`로 question의 ref_id(회의 ID) 검색
2. `mcp__zoom__get_meeting_assets`로 회의 자산 목록 확인 (transcript 존재 여부 사전 검증)
3. `mcp__zoom__get_file_content`로 transcript 전문 수집
4. transcript에서 question의 키워드로 관련 발언 추출 (결정론 — 키워드 매칭):
   - 키워드 전후 3분 이내 발언을 context로 포함
   - 발언자 + 타임스탬프 + 발언 텍스트 구조로 기록
5. `mcp__zoom__search_zoom`으로 회의 내 안건·채팅에서 보충 정보 검색

추출 결과를 `harness/answers.md`에 아래 형식으로 기록:
```
- question_id: Q-001
- source: Zoom 회의 (ID: <회의ID>, <날짜 시간>)
- speaker: [발언자명]
- timestamp: 00:23:15
- answer: "[발언 원문]"
- context: "[전후 발언 요약]"
```

### mode: digest
1. `harness/answers.md` 로드. 없으면 fail loud ("pull-answers 먼저").
2. 각 답변을 요약한다 (LLM — 판단 아님, 압축만). `evidence_type: "simulated"` 태그 답변은 요약 시 명시.
3. 태그로 라우팅 (결정론): `#decision` → decision-log 항목 초안, `#ticket:<n>` → ticket-bridge status 코멘트 후보.
4. **확인 게이트**: 라우팅 대상 + 요약을 보여주고 승인받은 뒤 해당 스킬로 넘긴다.

### mode: init

> ask-team 최초 사용 시 `harness/team-map.json`을 대화형으로 생성합니다.

1. "팀원을 몇 명 등록할까요?"를 묻는다 (AskUserQuestion)
2. 각 팀원에 대해: 이름 / 이메일 또는 채널 / 주 커뮤니케이션 채널(gmail|notion|slack|zoom) 입력
3. 입력 결과로 `harness/team-map.json` 생성:
   ```json
   {
     "alex": {"email": "alex@team.com", "channel": "gmail"},
     "design": {"notion_page": "<page-id>", "channel": "notion"},
     "eng": {"slack_channel": "#eng-team", "channel": "slack"}
   }
   ```
4. "harness/persona-config.md도 설정할까요?" (AskUserQuestion)
   - 예: ICP/타겟 도메인 역할 목록 입력 → `harness/persona-config.md` 생성
5. 완료 후: "이제 `ask-team --mode ask [질문] [이름]`으로 사용할 수 있습니다" 안내

> init은 언제든 재실행 가능합니다. 기존 `team-map.json`이 있으면 덮어쓸지 확인 후 진행합니다.

### mode: solo

> 팀원이 없을 때 Claude가 역할(CTO/Designer/초기유저)을 맡아 질문에 답하는 시뮬레이션.

1. 역할 목록 결정 순서 (결정론):
   a. `$ARGUMENTS`에 명시된 역할 → 그대로 사용
   b. `harness/persona-config.md` 존재 시 → 파일에서 로드
   c. 없으면 기본: "CTO, Designer, 초기유저 A"

   `harness/persona-config.md` 형식:
   ```
   roles:
     - 법무팀 실무자 (계약서 검토 경험 3년+)
     - 스타트업 HR 담당자
     - 잠재 고객 (중소기업 대표)
   ```
   이 파일이 있으면 solo 모드가 자동으로 도메인 맞춤 역할을 사용합니다.

2. 각 역할로 질문에 답한다 (LLM — 자연어 생성, Rule 5 허용).
3. 역할별 답변을 `harness/answers.md`에 기록 (출처: "simulated — solo mode", `evidence_type: "simulated"`).
4. **확인 게이트**: "이 답변은 AI 시뮬레이션입니다. 실제 인터뷰로 검증하세요" 명시 후 저장.

solo 모드 답변은 `evidence_type: "simulated"`로 태깅된다 — Signal Gate는 simulated 답변을 실제 증거로 인정하지 않는다.

> **도메인 역할 설정**: `/harness-discover --mode opp` 완료 후 ICP가 정의되면
> `harness/persona-config.md`에 타겟 역할을 기록해두세요. solo 모드가 자동으로 활용합니다.

---

## Failure Handling

| 실패 상황 | 감지 | 대응 |
|---|---|---|
| `--mode` 미명시 | 미입력 | fail loud + 모드 목록 |
| comms MCP 미연결 | 관례명 도구 미발견 | fail loud — "Gmail/Notion/Zoom/Slack MCP 중 연결된 것이 없음". 대체 client 안 만듦 |
| Slack MCP 미연결 | 도구 미발견 | fail loud — "Slack MCP 미연결. Gmail/Notion으로 대체 가능" |
| 대상 미매핑 (ask) | team-map에 키 없음 | fail loud + "team-map.json에 대상 추가 필요". 주소 추측 금지 |
| 자동 발송 요구 | send 도구 부재 | fail loud — "ask-team은 발송 불가(초안만). Gmail에서 직접 발송" |
| `questions.jsonl` 없음 (pull) | file not found | fail loud — "ask 먼저" |
| Zoom transcript 없음 | `get_file_content` 빈 결과 | "회의록 미생성 또는 미업로드 — Zoom 설정 확인 필요" + `get_meeting_assets`로 대체 자산 탐색 |
| `answers.md` 없음 (digest) | file not found | fail loud — "pull-answers 먼저" |
| 미응답 question | ref_id로 답 0건 | "미응답" 표시, 나머지 진행 (부분 성공 명시 — Rule 8) |
| digest 태그 없음 | `#decision`/`#ticket` 부재 | answers.md에만 보존, 라우팅 보류 + 안내 |

원칙: **답을 판단하지 않는다.** ask-team은 질문 전달·답 수집·요약까지만. GO/HOLD 같은 판단은 사람 또는 hplan 게이트의 몫 (Rule 5/8).

---

## Quality Gate

### ask
- [ ] 대상 → 채널 = team-map lookup (LLM 라우팅 0)
- [ ] 발송 0회 (초안/코멘트만). Slack은 사용자 승인 후에만 post_message 호출
- [ ] 확인 게이트 통과 후에만 도구 호출
- [ ] questions.jsonl append (덮어쓰기 0)

### pull-answers
- [ ] 답 ↔ question = ref_id 결정론 매칭
- [ ] 미응답 명시
- [ ] 답 텍스트 원문 보존 (판단·가공 0)

### digest
- [ ] 요약 = 압축만 (판단 0)
- [ ] 라우팅 = 태그 결정론 분기
- [ ] 라우팅 전 확인 게이트 통과
- [ ] simulated 답변 별도 명시

### solo
- [ ] 역할별 답변 생성 (LLM)
- [ ] `evidence_type: "simulated"` 태깅
- [ ] "AI 시뮬레이션" 경고 명시 후 저장
- [ ] Signal Gate에 실제 증거로 전달 금지

---

## Examples

### Good Example
**입력:** `--mode ask "결제 모듈 마감일 언제로 볼까요?" alex`

**기대 동작:**
1. team-map에서 alex → gmail (결정론)
2. 질문 초안 생성 (LLM) → 확인 게이트 → `create_draft`
3. "초안 생성됨, Gmail에서 발송하세요" + questions.jsonl 기록

### Good Example
**입력:** `--mode ask "스프린트 회고 공유 요청" eng`

**기대 동작:**
1. team-map에서 eng → slack, `#eng-team` (결정론)
2. 메시지 초안 생성 (LLM) → 확인 게이트
3. 사용자 승인 후 `post_message` 호출 → questions.jsonl 기록

### Good Example
**입력:** `--mode solo "MVP 출시 전 가장 큰 리스크가 뭘까요?"`

**기대 동작:**
1. 역할 파싱: CTO, Designer, 초기유저 A (기본값)
2. 각 역할로 답변 생성 (LLM)
3. answers.md에 `evidence_type: "simulated"` 태깅 기록
4. "AI 시뮬레이션 — 실제 인터뷰로 검증하세요" 경고 명시

### Good Example
**입력:** `--mode digest`

**기대 동작:**
1. answers.md 로드 → 각 답 요약 (LLM). simulated 답변 별도 명시
2. `#decision` 태그 답 → decision-log 초안 / `#ticket:17` → ticket-bridge 후보
3. 확인 게이트 → 라우팅

### Bad Example
**입력:** `--mode ask "..." bob` (bob이 team-map에 없음)

**기대 동작:** "bob 미매핑 — harness/team-map.json에 추가하세요. 주소를 추측하지 않습니다." fail loud

### Bad Example
**입력:** `--mode ask "..." alex --send`

**기대 동작:** "ask-team은 발송할 수 없습니다(Gmail send 도구 없음). 초안만 생성하니 Gmail에서 직접 보내세요." fail loud
