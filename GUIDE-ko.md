# 사용 가이드 — PM과 마케터를 위한 AI 에이전트 스킬셋

> 이 가이드는 Claude Code를 처음 쓰는 PM이나 마케터도 10분 안에 시작할 수 있도록 작성되었습니다.

---

## 이 스킬셋은 뭔가요?

대부분의 PM 스킬은 **"AI를 도구로 쓰는 PM"**을 돕습니다 — PRD 작성, 로드맵 관리, 경쟁 분석 등.

이 스킬셋은 다릅니다. **"AI 에이전트를 직접 만들고 운영하는 PM"**을 위한 것입니다.

### 일반 PM 스킬이 다루지 않는 6가지 영역

| 영역 | 하는 일 | 왜 필요한가 |
|-----|--------|-----------:|
| **에이전트 경제학** | 토큰 비용 시뮬레이션, 스케일 예측, 최적화 전략 | 유저 10명에 월 $3K인 에이전트는 100명이면 $30K — 만들기 전에 모델링이 필요 |
| **멀티에이전트 아키텍처** | Prometheus-Atlas-Worker 3계층 설계, 오케스트레이션 패턴 | 복잡한 워크플로우는 에이전트 여러 개가 협업해야지, 하나로는 안 됨 |
| **에이전트 전용 PRD** | Instruction, Tools, Triggers, Memory, Failure Handling 섹션 | 일반 PRD에는 에이전트의 실패 복구나 컨텍스트 윈도우 관리 명세가 없음 |
| **운영 신뢰성** | FMEA 기반 프리모템, SLO 설계, 에러 복구 패턴 | 에이전트의 실패는 소프트웨어와 다름 — 환각, 컨텍스트 드리프트, 비용 폭등 |
| **경쟁 해자** | 데이터 플라이휠, 프로세스 락인, 지식 해자 분석 | "GPT-4를 씁니다"는 해자가 아님. 축적된 운영 데이터와 암묵지가 해자 |
| **PM 암묵지** | TK-NNN(Never-ending Nuance Network) — PM 판단을 추출·구조화·에이전트에 주입 (TK-001→TK-999) | PM 경험이 재사용 가능한 자산이 되고, TK 간 연결이 지식 그래프를 형성해 모든 에이전트를 더 똑똑하게 만듦 |

일반 PM 스킬과 **경쟁이 아니라 보완 관계**입니다. 기존 스킬로 일반 PM 업무를 하고, 이 스킬셋으로 에이전트를 만드세요.

---

## 시스템 요구사항

| 항목 | 최소 버전 | 비고 |
|-----|---------|------|
| **Claude Code** | v1.0.0+ | `claude --version`으로 확인 · [설치 가이드](https://docs.anthropic.com/ko/docs/claude-code) |
| **Python** | 3.9+ | `python3 --version`으로 확인 · Evidence Gate 스크립트 실행 필요 (선택 — 아래 참고) |
| **Git** | 2.x+ | pre-commit hook 사용 시 필요 (선택) |
| **OS** | macOS / Linux | Windows는 WSL2 권장 |

> **자연어 탐색은 Python 없이 시작할 수 있습니다.** 자연어로 트리거되는 스킬(socratic-question, prd, conductor 루프)은
> Python 없이 동작합니다. 다만 `/hplan` 게이트(exclusions·COGS)와 `harness-discover`의 HITL 단계는 Python이 필요합니다
> (cogs-sentinel, evidence-rubric, `decision_log.py` 등). 나중에 필요해지면 설치해도 됩니다.
>
> **Python이 없다면?** Evidence Gate(`generate_report.py`, `gate_guard.py`)를 포함한 일부 스킬이 동작하지 않습니다. 나머지 스킬(SKILL.md 기반)은 Python 없이도 사용 가능합니다.

---

## 설치하기 (5분)

> **처음 설치라면 → 방법 1 (마켓플레이스 설치)만 하면 됩니다.**
> CLI 사용자이거나 플러그인을 선택 설치해야 한다면 방법 2/3를 사용하세요.

### 방법 1: 마켓플레이스 설치 (추천)

아래 명령을 **Claude 세션 안에서** 실행하세요 (`/` 로 시작하는 슬래시 커맨드는 터미널 bash가 아닌 Claude 세션에서만 동작합니다):

```
# 한 줄로 5개 플러그인 전부 설치
/plugin marketplace add kimsanguine/hplan
/plugin install hplan@hplan
```

### 방법 2: 개별 플러그인 설치

아래 명령을 **Claude 세션 안에서** 실행하세요:

```
# 필요한 플러그인만 선택해서 설치
/plugin install hplan@hplan      # 게이트 ⭐ (Should we build this?)
/plugin install discover@hplan   # 발견 (What to build?)
/plugin install architect@hplan  # 설계 (How to architect?)
/plugin install deliver@hplan    # 실행 (How to ship?)
/plugin install operate@hplan    # 운영 (How to operate?) — KPI·신뢰성·포트폴리오·PM 암묵지 자산화
```

만들지 말지부터 고민이라면 → `hplan`을 먼저 설치하세요 (evidence + COGS 게이트).
어떤 에이전트를 만들지 아직 모르겠다면 → `discover`을 설치하세요.
이미 뭘 만들지 정했다면 → `deliver`부터 시작하세요.

### 방법 3: 개별 스킬 복사 (플러그인 없이)

```bash
# 원하는 스킬만 복사
cp -r discover/skills/cost-sim/ ~/.claude/skills/
cp -r architect/skills/orchestration/ ~/.claude/skills/
```

### 다른 도구에서도 사용 가능

| 도구 | 스킬 (SKILL.md) | 커맨드 체이닝 | 비고 |
|-----|:---:|:---:|------|
| Claude Code | ✅ | ✅ | — |
| Gemini CLI | ✅ | ⚠️ 수동 | — |
| Cursor | ✅ | ⚠️ 수동 | — |
| Codex CLI | 25 native / 9 adapter-required | ❌ | [hplan_codex capability matrix](https://github.com/kimsanguine/hplan_codex/blob/main/runtime/hplan-core/HPLAN_CAPABILITY_MATRIX.md) 확인 후 Codex 전용 adapter 사용 |
| Kiro | ✅ | ⚠️ 수동 | — |

---

## 외부 도구 연동 (Linear · Slack · team-map)

> 💡 **심화 내용** — 처음이라면 건너뛰어도 됩니다.

`ticket-bridge`와 `ask-team` 스킬은 MCP 연결이나 팀 맵 파일 없이도 초안 생성 모드로 동작합니다. hplan core adapter의 외부 connector write는 disabled이므로, 아래 연결은 초안·조회·수동 승인 경로를 위한 선택 사항이며 hplan이 직접 전송하거나 티켓을 생성하지 않습니다.

### Linear 연동 (`ticket-bridge --system linear`)

1. [Linear MCP 서버](https://linear.app/docs/mcp)를 Claude Code에 등록합니다.

   ```bash
   # claude_desktop_config.json 또는 .mcp.json에 추가
   {
     "mcpServers": {
       "linear": {
         "command": "npx",
         "args": ["-y", "@linear/mcp-server"],
         "env": { "LINEAR_API_KEY": "<your-api-key>" }
       }
     }
   }
   ```

2. Linear API 키는 **Settings → API → Personal API keys**에서 발급합니다.
3. 연결 확인 후 `ticket-bridge --system linear --mode pull` 을 실행합니다.

> **주의:** Linear MCP 미등록 상태에서 `--system linear`를 호출하면 스킬이 `--system github`으로 자동 폴백하고 경고를 출력합니다.

### Slack 연동 (`ask-team --mode ask`)

`ask-team`은 Gmail MCP가 Claude Code에 내장되어 있다고 가정하지 않습니다. Gmail·Slack 등 연결 도구는 사용자가 자신의 Claude 환경에 별도로 구성할 때만 사용할 수 있으며, hplan은 메시지 초안을 만듭니다.

```bash
# .mcp.json에 추가
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-slack"],
      "env": { "SLACK_BOT_TOKEN": "<xoxb-...>", "SLACK_TEAM_ID": "<T...>" }
    }
  }
}
```

Slack Bot Token은 **api.slack.com → Your Apps → OAuth & Permissions**에서 `chat:write` 스코프로 발급합니다.

> **Slack MCP 없이도** `ask-team --mode ask`는 동작합니다 — 메시지 초안을 생성하고 사용자가 승인한 채널로 수동 전달하도록 안내합니다.

### team-map.json 초기 설정 (`ask-team --mode ask`)

`ask-team`은 첫 실행 시 `harness/team-map.json`이 없으면 작동하지 않습니다. 아래 최소 템플릿을 프로젝트 루트의 `harness/` 디렉토리에 만드세요.

```bash
mkdir -p harness
cat > harness/team-map.json << 'EOF'
{
  "eng-lead": {"email": "gildong@example.com", "channel": "gmail"},
  "design-lead": {"notion_page": "<page-id>", "channel": "notion"},
  "pm-sponsor": {"slack_channel": "#sponsor-channel", "channel": "slack"}
}
EOF
```

> **주의**: 이 포맷은 ask-team SKILL.md의 결정론 라우팅이 기대하는 포맷입니다.
> `ask-team --mode init`을 사용하면 대화형으로 자동 생성됩니다.

키(key)가 팀원 식별자이며, `channel` 값이 라우팅 결정론 분기의 기준이 됩니다 — `gmail`, `notion`, `slack` 중 하나. 팀원·채널·주소만 채워두면 즉시 사용 가능합니다.

---

## MCP 연결 빠른 가이드

hplan의 일부 스킬(ask-team, ticket-bridge)은 선택적으로 외부 MCP 도구를 참조할 수 있습니다. connector write는 core adapter에서 disabled이며, 도구 가용성은 사용자의 Claude 환경 설정에 따라 달라집니다.

| 스킬 | 필요한 MCP | 연결 방법 |
|---|---|---|
| ask-team (팀 질문) | 사용자가 구성한 Gmail / Notion / Slack / Zoom | Claude 환경에서 해당 MCP 도구를 별도 구성 |
| ticket-bridge (티켓 초안) | 사용자가 구성한 GitHub / Linear / Jira | 해당 MCP 도구를 별도 구성; hplan은 초안·로컬 artifact만 생성 |

> MCP 없이 시작하면 `ask-team --mode solo`와 ticket-ready local artifact 생성부터 시작합니다.
> 연결이 필요한 스킬을 호출했는데 도구가 없으면 어떤 MCP가 없는지 안내합니다(fail loud).

---

## 5개 플러그인 한눈에 보기

v0.9부터 `measure` + `learn`이 `operate`로 통합되어 **5-plugin 라이프사이클**로 단순화되었습니다.

```
에이전트 제품 생명주기:

  게이트 → 발견 → 설계 → 딜리버리 → 운영
    │       │      │        │        │
  hplan  discover  architect  deliver  operate
```

| 단계 | 플러그인 | 핵심 질문 | 이런 상황에서 쓰세요 |
|-----|---------|---------|----------------|
| 게이트 ⭐ | **hplan** | "정말 만들 가치가 있을까?" | PRD 쓰기 전에 인터뷰·경쟁·COGS·과거 결정 확인 |
| 발견 | **discover** | "어떤 에이전트를 만들까?" | 자동화할 업무를 찾고 있을 때, 비용이 맞는지 확인할 때 |
| 설계 | **architect** | "어떤 구조로 만들까?" | 단일 에이전트 vs 멀티에이전트 결정, 아키텍처 설계 |
| 딜리버리 | **deliver** | "어떻게 명세하고 만들까?" | PRD 작성, 인스트럭션 설계, 스프린트·QA 추적, UI 검증, 빌드 루프 |
| 운영 | **operate** | "측정·학습·포트폴리오를 어떻게 할까?" | KPI · 신뢰성 · 포트폴리오 · PM 암묵지 자산화 |

---

## 시나리오별 따라하기

### 시나리오 1: "AI 가계부 앱, 처음부터 끝까지 일관되게 만들고 싶어"

**배경** — 1인 메이커. "기존 가계부 앱엔 AI 분석이 없다"는 불만을 여러 번 들었다.
만들어야 할지, 만든다면 어떻게 일관되게 진행할지 모르겠다.

---

**Step 1 — gate: 만들어야 하는가 (WHETHER)**

```
/hplan AI 가계부, 지출 패턴 자동 분석
```

Evidence Gate 실행. 인터뷰 3건 결과 **78점 (GO)**. `generate_report.py` 출력에서 전환 트리거·경제적 고통 확인, build 판정. 이 점수와 근거가 이후 모든 결정의 **기준선①**이 된다.

**Step 2 — plan: 기술 결정을 한 번, 끝까지 유지**

```
/harness-plan AI 가계부 앱
/cogs-sentinel --requests 200/day --model gemini-flash
```

아키텍처 결정: FastAPI + Supabase + Gemini Flash, 월 $8 예상. **이 결정이 PRD·운영 전 구간에 자동 반영됩니다 (기준선②).** 이후 "Firebase로 바꾸면 어때요?" 같은 요청이 들어오면 plan 결정을 참조해 이탈 경고를 냅니다. 디자인 토큰(색상·타이포·간격)도 `/harness-plan` 단계에서 함께 정의되어 이후 모든 화면 구현의 기준이 됩니다 (기준선③).

**Step 3 — deliver: 일관된 기반 위에서 구현**

```
/prd AI 가계부 v1
```

PRD에 기준선①(PMF 근거)·②(아키텍처)·③(디자인 토큰)이 자동 반영됩니다. 통과 후 구현 시작. 구현 도중 새 기능 추가 요청이 오면 "Step 1 근거와 연결되는가?"를 먼저 확인합니다.

**Step 4 — operate: 기준선 이탈 없이 운영**

```
/harness-operate AI 가계부
```

아키텍처·디자인·PMF 근거 3개 기준선을 동시에 점검합니다. 이탈 감지 시 경고 → decision-log 기록 → 다음 스프린트에 반영.

| 구간 | hplan의 역할 |
|------|-------------|
| 시작 | Evidence Gate → WHETHER 결정 |
| 설계 | 아키텍처·디자인 토큰 → 기준선 수립 |
| 구현 | PRD → 기준선 반영 |
| 운영 | harness-operate → 기준선 이탈 방지 |

> 1인 메이커가 6개월 후 "이게 처음 의도였나?" 하는 순간을 없앤다.

---

### 시나리오 2: "이미 에이전트가 있는데 비용이 너무 많이 나와"

```
/harness-operate 문서 요약 에이전트
```

이 커맨드는 운영 단계의 비용 분석을 포함해 현재 토큰 비용을 점검하고, 모델 다운그레이드, 캐싱, 배치 처리 등 최적화 방안을 제시합니다.

---

### 시나리오 3: "프로젝트에서 배운 교훈을 다음 에이전트에 반영하고 싶어"

이게 `operate` 플러그인의 핵심 용도입니다.

**Step 1 — 경험 추출**

```
/harness-operate 지난 3개월 고객 상담 에이전트 운영하면서 배운 것들:
- 고객이 "긴급"이라고 하면 80%는 진짜 긴급이 아니었다
- 같은 질문이 3번 반복되면 자동화 대상이다
- 에이전트가 "모르겠다"고 답하는 게 틀린 답보다 낫다
```

`/harness-operate`의 지식 추출 단계(`pm-engine` 스킬)가 이 경험들을 **TK 유닛**(Tacit Knowledge unit)으로 구조화합니다.

```
TK-041: 긴급 트리거 검증 규칙
  패턴: 고객이 "긴급"을 언급할 때 실제 긴급률은 20% 이하
  활성 조건: 에이전트가 우선순위를 결정할 때
  의사결정: 긴급 키워드만으로 에스컬레이션하지 말 것. 실제 영향 범위 확인 후 판단.
```

**Step 2 — 에이전트 인스트럭션으로 변환**

같은 `/harness-operate` 운영 루프 안에서 TK 유닛을 에이전트가 바로 사용할 수 있는 인스트럭션 형식으로 변환합니다 (`pm-engine`의 인스트럭션 자동 업데이트).

---

### 시나리오 4: "경쟁사가 비슷한 에이전트를 만들었는데 우리 차별점이 뭐지?"

```
에이전트 경쟁 우위를 분석해줘.
우리: 다국어 고객 상담 에이전트, 6개월 운영 경험, TK 유닛 40개 축적
경쟁사: 영어 단일 언어, 최근 출시, 범용 LLM 기반
```

`strategy` 스킬이 자동으로 불립니다 (경쟁 해자 분석은 strategy로 통합됐습니다). 데이터 해자, 프로세스 해자, 네트워크 해자 관점에서 분석합니다.

---

## 스킬 전체 목록 (34개)

> 아래 표는 **디스크에 실제로 존재하는 34개 스킬만** 나열합니다. 플러그인별 합계: hplan 8 · discover 6 · architect 4 · deliver 10 · operate 6 = **34개**.

### hplan — 게이트 ⭐ (8개 스킬)

빌드 결정 *전에* 돌리는 evidence + COGS + decision 게이트. LLM 추정이 아닌 결정론적 Python 측정과 영구 메모리(JSONL)가 핵심.

| 스킬 | 기능 |
|------|------|
| `brainstorm` | Phase 0 Worth-Building Check + 대화형 설계 + Signal Gate Bootstrap — 아이디어를 validated 설계 문서로 전환, prd 진입 전 필수 단계 |
| `evidence-rubric` | 8축 100점 evidence 루브릭으로 아이디어 점수화 → build/interview/pivot/hold 판정 |
| `interview-synthesis` | AI 합성 결과 import → 인간 strength 태깅 강제 → 5/3 strong-Push 패턴 audit |
| `exclusions` | Append-only Do-Not-Build 영구 메모리, 한국어 fuzzy match로 collision 자동 감지 |
| `cogs-sentinel` | lognormal sampler가 p50/p90 월간 마진 계산 + free-user abuse blend → GREEN/CONDITIONAL_GO/RED |
| `ost` | Teresa Torres 식 Opportunity Solution Tree를 Mermaid + `docs/OPPORTUNITY_TREE.md`로 생성 |
| `decision-log` | build/interview/pivot/hold 결정 append-only 로그 + 3-6개월 self-eval audit |
| `handoff` | Build Gate brief → Spec-Kit / Kiro / GStack / Claude Code 4개 ecosystem 동시 export |

### discover — 발견 (6개 스킬)

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `opp-tree` | 에이전트 기회 트리 작성 (반복 빈도·자동화 적합도·판단 의존도 점수화) | "뭘 자동화하면 좋을까?" |
| `assumptions` | 4축 가정 검증 (가치/실현성/신뢰성/윤리) + build-or-buy 판단 포함 | "이거 진짜 만들어도 되나? 사서 쓸까 직접 만들까?" |
| `cost-sim` | 토큰 비용 시뮬레이션 (규모별 월간 운영 비용) | "한 달에 얼마 들어?" |
| `hitl` | Human-in-the-loop 범위 설정 (자동화 레벨 + 에스컬레이션 기준) | "어디까지 자동화하고 어디서 사람이 개입?" |
| `customer-reach` | 인터뷰 대상자 확보 + LinkedIn DM·커뮤니티 포스팅·설문 초안 생성 | "고객 인터뷰를 누구한테 어떻게 요청하지?" |
| `socratic-question` | 소크라테스식 질문으로 가정을 먼저 심문 — 숨은 리스크와 검증되지 않은 전제 드러내기 | "아이디어에 뛰어들기 전에 내 가정을 먼저 검증하고 싶어" |

### architect — 설계 (4개 스킬)

> 흡수: `router`는 v0.14.1에서 `orchestration --pattern router`로 흡수됐습니다. 경쟁 해자(moat)·비즈니스 모델(biz-model)·성장 루프(growth-loop)는 `strategy` 스킬로 통합됐습니다.

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `orchestration` | 오케스트레이션 패턴 선택 (Sequential/Parallel/Router/Hierarchical). `--pattern router`는 작업별 LLM 모델 라우팅까지 커버 | "Sequential? Parallel? Router? 이 작업에 Haiku? Sonnet? Opus?" |
| `memory-arch` | 에이전트 메모리 설계 (Working/Episodic/Semantic/Procedural) | "대화 기록을 어떻게 관리하지?" |
| `strategy` | 전략 설계 통합 — 비즈니스 모델 캔버스 + 경쟁 해자 분석 + 성장 루프 설계 | "이걸로 어떻게 돈 벌지? 경쟁사가 따라오면 어쩌지?" |
| `design-token` | 2-step 디자인 파이프라인 (브리프 → 시맨틱 토큰 + DESIGN.md 자동 생성) | "디자인 시스템 토큰을 어떻게 정의하지?" |

### deliver — 딜리버리 (10개 스킬)

> 흡수: `roadmap` → `prd --mode roadmap` · `stakeholder-review` → `ask-team --mode review`.

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `agent-setup` ⭐ | 프로젝트 스캔 → CLAUDE.md/AGENTS.md 생성 + 7요소 인스트럭션 설계 통합 | "새 프로젝트에 Claude Code를 세팅하고 에이전트 인스트럭션을 짜고 싶어" |
| `prd` ⭐ | 통합 15섹션 에이전트 PRD + **mermaid 정합성 게이트** (workflow↔userflow↔requirements 결정론 검증). `--mode roadmap`은 §6 Now/Next/Later → Mermaid gantt + RICE | "기획서를 쓰고 누락 없는지 자동 검증하고 싶어 / 백로그를 로드맵으로" |
| `build-loop` ⭐ | `/harness-build` 한 번으로 발견→리서치→설계→PRD→분해→구현 | "아이디어부터 구현까지 한 루프로" |
| `conductor` | 태스크별 fresh subagent 디스패치 + 2단계 게이트(spec→quality) 반복 실행 | "harness-plan 승인 후 구현 루프를 순차+게이트로 돌리고 싶어" |
| `sprint` | 스프린트 계획-실행-추적 통합 (PRD → WBS 분해, predicted.json, probe/detect/report) | "스프린트 계획을 잡고 진척을 추적하고 싶어" |
| `qa-checklist` | docs/PRD.md 파싱 → QA_CHECKLIST.md 자동 생성 (TC를 critical/major/minor 분류) | "PRD 기반으로 QA 체크리스트를 자동 생성하고 싶어" |
| `respect` | 2-mode UI respect (brief = 코딩 전 RESPECT.md / checkpoint = ship 전 α/β/γ 게이트) | "ship 직전 사용자 존중 게이트를 강제하고 싶어" |
| `ui-validate` | 통합 UI 검증 (hierarchy/motion/drift/mobile/tc-gate) — 각 check 독립 실행·실패 | "Playwright로 위계·모션·드리프트·모바일을 검증하고 싶어" |
| `ask-team` | 질문을 올바른 이해관계자 또는 에이전트 역할로 구조화하여 라우팅. `--mode review`는 PRD 스테이크홀더 리뷰 | "이 트레이드오프를 누구에게 물어봐야 하지? / PRD 리뷰를 추적하고 싶어" |
| `ticket-bridge` | PRD 결정·게이트 출력물 → Linear / Jira / GitHub Issues용 티켓 초안으로 변환 | "게이트 판정 결과에서 스프린트 티켓 초안을 만들고 싶어" |

### operate — 측정·학습·포트폴리오 운영 (6개 스킬)

v0.9에서 `measure`(측정) + `learn`(학습) + 기존 `operate`(포트폴리오 운영)가 하나로 통합되었습니다. 흡수: `stakeholder-update` → `ops-review`.

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `metrics-design` | 지표 위계 + OKR 설계 (North Star → KPI 도출 → OKR, `--step north-star\|kpi\|okr\|all`) | "어떤 지표를 봐야 하지? 성공 기준을 어떻게 잡지?" |
| `reliability` | 신뢰성 체계 점검 (실패 패턴 식별 + 세이프가드 + 신뢰성 타겟) | "에이전트가 엉뚱한 답을 하면?" |
| `incident` | 장애 대응 프로토콜 (트리아지 + 영향 범위 차단 + 포스트모템) | "에이전트가 터졌는데 어떻게 하지?" |
| `pm-engine` | PM-ENGINE-MEMORY 인터페이스 — TK 추출/쿼리/인스트럭션 변환 + 의사결정 패턴 매칭 | "축적된 TK를 에이전트에 주입하고 싶어 / 이 상황에서 어떻게 판단하지?" |
| `portfolio` | 에이전트 포트폴리오 관리 (T1~T5 티어링 + 크로스-에이전트 비용 비교 + 헬스 스코어) | "운영 중 에이전트가 5개 넘었는데 어디부터 손볼지" |
| `ops-review` | 주간/월간 운영 리뷰 + 비용 추적(burn-rate) + 이해관계자 보고서 4종 (임원·팀·파트너·위키) | "운영 리뷰를 돌리고 진행 상황 임원 보고서를 빠르게 만들고 싶어" |

---

## COGS 파라미터를 어떻게 채우나요?

> 이 섹션은 `/cogs-sentinel`이나 `cost-sim`을 처음 쓰는 수강생을 위한 단계별 안내입니다.

`cogs-sentinel`을 호출하면 Claude가 아래 파라미터를 물어봅니다. 처음 보면 막막하지만, 각 값은 "추측이 아니라 근거가 있는 추정"입니다. 아래 순서대로 따라가세요.

### Step 1 — calls_per_user_month: 월간 호출 수 추정

> "유료 사용자 1명이 한 달에 몇 번 이 기능을 쓸까?"

방법:
1. **유사 앱 리뷰를 읽는다** — App Store · Google Play 리뷰에서 "하루에 X번 씁니다" 발화를 찾는다.
2. **직접 인터뷰한다** — "하루에 몇 번 쓰실 것 같으세요?"라고 물어본다. 답을 30으로 나누면 월간 수치.
3. **보수적으로 설정한다** — 처음엔 실제보다 2배 높게 설정해 최악을 먼저 확인한다.

예시 (AI 헬스케어 복약 알림 앱, 유료 $9.9/월):

| 기능 | 추정 근거 | calls_per_user_month |
|-----|---------|-------------------|
| 복약 기록 분석 | "하루 1번 기록" → 30회/월 | 30 |
| 주간 건강 리포트 | "주 1회 리포트 생성" → 4회/월 | 4 |
| 의약품 상호작용 확인 | "새 약 처방 시" → 2회/월 | 2 |

### Step 2 — tokens_in / tokens_out: 호출당 토큰 수 추정

> "한 번 호출할 때 입력·출력 토큰이 몇 개나 될까?"

방법:
1. **실제로 프롬프트를 써보고 세어본다** — Claude Code에서 같은 작업을 직접 해보고 "약 X토큰"이라는 응답을 참조한다.
2. **경험칙 사용** — 짧은 분류·요약 = 500~1,500 tokens_in / 200~500 tokens_out. 긴 리포트 생성 = 2,000~5,000 tokens_in / 800~2,000 tokens_out.
3. **넉넉하게 잡는다** — 실제 운영 시 컨텍스트가 늘어나므로 추정치의 1.5배로 설정.

예시 (복약 기록 분석):

```
tokens_in:  1,200  # 사용자 기록 텍스트(800) + 시스템 프롬프트(400)
tokens_out:   600  # 분석 결과 3~5줄
```

### Step 3 — arpu: 월간 사용자당 평균 수익

> "유료 사용자 1명이 한 달에 얼마를 낼까?"

방법:
1. **경쟁사 가격을 본다** — 유사 앱 3개의 가격을 평균낸다.
2. **인터뷰에서 WTP(지불 의향)를 묻는다** — "이 기능에 월 얼마까지 낼 의향이 있으세요?"
3. **무료 tier가 있다면 paid_conversion도 함께** — 무료 100명 중 유료 전환이 5명이면 `paid_conversion: 0.05`.

예시 (AI 헬스케어 복약 알림 앱):
```
arpu: 9.9        # 월 $9.9 구독
paid_conversion: 0.06   # 무료→유료 전환율 6%
```

### Step 4 — 한 번에 붙여서 실행

위 3단계를 채웠으면 Claude에게 자연어로 전달하면 됩니다:

```
AI 헬스케어 복약 알림 앱 COGS를 계산해줘.
- 모델: claude-haiku-3-5
- 월간 호출: 36회 (복약분석30 + 리포트4 + 상호작용2)
- 호출당 입력 토큰: 1,200 / 출력 토큰: 600
- 월 구독료(ARPU): $9.9
- 무료→유료 전환율: 6%
- 무료 유저 abuse 배수: 3
```

`cogs-sentinel` 스킬이 자동으로 호출되어 p50/p90 마진과 GREEN/CONDITIONAL_GO/RED 판정을 반환합니다.

> **파라미터가 전혀 없다면?** `cost-sim`을 먼저 실행하세요. "Sonnet으로 하루 500콜이면?"처럼 자연어로 물어보면 시나리오 초안을 잡아주고, 그 결과를 `cogs-sentinel`에 넘기면 됩니다. 두 스킬은 paired 관계입니다.

---

## 커맨드 전체 목록 (12개)

커맨드는 여러 스킬을 체이닝해서 한 번에 실행하는 워크플로우입니다. v1.1.0 기준 사용 가능한 슬래시 커맨드는 아래 12개입니다.

**게이트 (hplan)**

| 커맨드 | 플러그인 | 하는 일 |
|--------|---------|--------|
| `/hplan` | hplan | Build Gate 통합 진입 — WHETHER 결정(evidence + COGS + decision) |
| `/evidence-rubric` | hplan | Evidence Gate — exclusions check + 100점 루브릭 + 인터뷰 audit |
| `/cogs-sentinel` | hplan | COGS sentinel만 빠르게 — p50/p90 마진 + free-abuse 시뮬레이션 |
| `/harness-exclude` | hplan | "Do Not Build" 영구 메모리 add/check/list |
| `/harness-handoff` | hplan | Build Gate brief → Spec-Kit / Kiro / GStack / Claude Code export |
| `/harness-doctor` | hplan | 설치 진단 — 훅 등록·실행·체크포인트·레지스트리·git 훅 5-check |

**라이프사이클 (hplan 1개만 설치해도 전체 커버)**

| 커맨드 | 단계 | 하는 일 |
|--------|------|--------|
| `/harness-discover <idea>` | Discover | 기회 매핑 → 가정 분석 → 비용 시뮬 → 빌드/바이 결정 |
| `/harness-plan <system>` | Plan | 오케스트레이션 → 전략 → 메모리 → 모델 라우팅 → 디자인 토큰 |
| `/harness-build <brief>` | Build | COGS gate + PRD 15-section 자동 작성 + W1 스프린트 |
| `/harness-verify` | Verify | 구현물 검증 게이트 (테스트·체크포인트·드리프트) |
| `/harness-operate <agent>` | Operate | KPI · 신뢰성 · 비용 · 개선 계획 + 지식 추출(TK) |

**스펙 (deliver)**

| 커맨드 | 플러그인 | 하는 일 |
|--------|---------|--------|
| `/prd` | deliver | 통합 15섹션 에이전트 PRD + mermaid 정합성 게이트 |

---

## 자주 묻는 질문

**Q: Claude Code가 없으면 못 쓰나요?**
A: Gemini CLI와 Cursor는 각 도구의 스킬 경로로 수동 사용이 가능합니다. Codex는 Claude 스킬 파일을 복사해 쓰는 대상이 아닙니다. [hplan_codex capability matrix](https://github.com/kimsanguine/hplan_codex/blob/main/runtime/hplan-core/HPLAN_CAPABILITY_MATRIX.md)의 Codex 전용 adapter(25 native / 9 adapter-required, command 없음)를 사용하세요.

**Q: 기존 PM 스킬이랑 충돌하나요?**
A: 아닙니다. 기존 PM 스킬은 일반 PM 업무(로드맵, 스테이크홀더 커뮤니케이션 등)를 다루고, 이 스킬셋은 에이전트 구축/운영을 다룹니다. 둘 다 설치해서 쓰세요.

**Q: 영어로만 써야 하나요?**
A: 커맨드와 프롬프트 모두 한국어로 입력하면 됩니다. 스킬 내부의 개념 설명은 한국어, 인스트럭션은 영어로 작성되어 있어 LLM 실행 품질과 사용자 이해도를 동시에 잡았습니다.

**Q: TK-NNN이 뭔가요? 꼭 써야 하나요?**
A: TK = Tacit Knowledge(암묵지), NNN = Never-ending Nuance Network(끝없이 쌓이는 뉘앙스의 네트워크). TK-001부터 TK-999까지 PM의 판단 기준을 축적합니다. 예: "고객이 긴급이라고 하면 80%는 가짜 긴급이다." 이걸 구조화해서 에이전트 인스트럭션에 넣으면, 당신의 경험이 에이전트의 판단 기준이 됩니다. 매일 1개씩 약 3년이면 999개 — 에이전트가 PM의 분신이 되는 시점입니다. `operate` 플러그인의 `pm-engine` 스킬이 이를 담당합니다 (TK 추출·쿼리·인스트럭션 변환·의사결정 패턴 매칭 통합). 선택사항이지만, 쓰면 쓸수록 에이전트가 강해집니다.

**Q: 에이전트를 만들어본 적이 없어도 되나요?**
A: 네. 먼저 `/hplan` 게이트로 "정말 만들 가치가 있는가(WHETHER)"를 확인한 뒤, `/harness-discover`로 "어떤 업무를 자동화할 수 있는지"를 탐색합니다. 기술적 배경 없이 PM 관점에서 접근할 수 있도록 설계되었습니다.

---

## 추천 시작 경로

### PM이라면

```
/hplan → /harness-discover → /harness-plan → /prd → /harness-build → /harness-verify
```

### 마케터라면

```
/hplan [마케팅 자동화 업무] → /harness-discover → /prd → /harness-operate
```

### 이미 에이전트를 운영 중이라면

```
/harness-operate [운영 교훈 + 비용·KPI 점검 + TK 추출]
```

---

## 벤치마크 요약

이 스킬셋이 실제로 효과가 있는지 10개 테스트(54개 검증 항목)로 측정했습니다.

| | 스킬 사용 | 스킬 미사용 | 차이 |
|---|---------|----------|-----|
| **검증 통과율** | **100%** | 88% | **+12%** |
| **평균 실행 시간** | 62초 | 42초 | +20초 |

특히 `pm-engine`(TK 유닛)과 `orchestration`(멀티에이전트 설계 — Hierarchical 패턴)은 스킬 없이는 Claude가 제대로 수행하지 못하는 **역량 게이팅(capability-gating)** 영역이었습니다.

> **측정 caveat:** 이 수치(100% vs 88% 등)는 v0.4 (당시 32개 스킬) 기준 측정값입니다([CHANGELOG 0.4.0](CHANGELOG.md), 2026-03-06). v1.1.0 (34개 스킬, 5-plugin 구조) 기준 재측정은 아직 끝나지 않았으므로 *직접적인 v1.1.0 비교가 아니라 이전 baseline*입니다. v1.1.0 재측정은 별도 후속입니다.

---

## 라이선스

MIT — 자유롭게 사용, 수정, 배포할 수 있습니다.
