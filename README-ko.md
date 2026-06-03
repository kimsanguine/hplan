# hplan — Claude Code로 만들었는데, 안 팔리나요?

> **문제는 코딩이 아니라 — 시장조사와 문제정의입니다.**
>
>  AI 시대 1인 메이커를 위한 Product Build Gate.

> 🐎 **이름의 뜻 — `hplan` = Harness Planning.**
> 말의 고삐(harness)처럼, Claude Code · Cursor · Lovable 같은 AI 코딩 도구의 거친 동력에 **방향을 부여하는 사전 계획**입니다. 코드를 만드는 도구는 이미 충분히 강합니다. 부족한 건 *"어디로 향할지"*. hplan은 코드를 쓰기 전 7일 동안 시장조사·문제정의·COGS(AI 기능 제공 원가)를 강제로 묻습니다.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-38-blue?style=flat-square)](#에이전트-pm-여정--5-plugin)
[![Plugins](https://img.shields.io/badge/plugins-5-purple?style=flat-square)](#에이전트-pm-여정--5-plugin)
[![Version](https://img.shields.io/badge/version-0.13.0-green?style=flat-square)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
[![English](https://img.shields.io/badge/lang-English-blue?style=flat-square)](README.md)

**요구사항:** Claude Code v1.0+ · Python 3.9+ · Git 2.x+ · macOS / Linux (Windows: WSL2)

> **Python 없이 시작 가능합니다.** 핵심 스킬(socratic-question, harness-discover, prd, conductor)은
> Python 없이 동작합니다. Python이 필요한 기능: cogs-sentinel, evidence-rubric, track-probe.sh
> 나중에 필요해지면 설치해도 됩니다.

```bash
git clone https://github.com/kimsanguine/hplan ~/.claude/plugins/hplan
```

## 5분 빠른 시작

설치 완료 후 Claude 세션에서:

```
/socratic-question [내 아이디어]
```

AI가 먼저 당신의 가정을 심문합니다. "만들 가치가 있는가"가 명확해지면 `/harness-discover`로 넘어가세요.

> 💡 **심화 내용** — 처음이라면 건너뛰어도 됩니다.
>
> **v0.13.1** — hplan 은 AI 도구가 HOW 로 달려가기 전에 **WHETHER 를 묻는 Product Build Gate** 입니다. ADK 5-Layer 완성: L1 Memory (CLAUDE.md) · L2 Skills (34개 PM 규율) · L3 Hooks (SessionStart · PreToolUse · PostToolUse) · L4 Subagents (8역할 병렬 팀) · L5 Plugins (마켓플레이스). `git clone` + `bash scripts/install-hooks.sh` 한 번으로 5개 레이어 전체 활성화. 자세한 변경 내역은 [CHANGELOG.md](CHANGELOG.md).

### 📺 99초 소개 영상

https://github.com/kimsanguine/hplan/releases/download/v0.9.0-video-preview/v9-core-16x9.mp4

> _5-plugin 라이프사이클: hplan (게이트) → discover → architect → deliver → operate. [v0.9.0-video-preview release](https://github.com/kimsanguine/hplan/releases/tag/v0.9.0-video-preview)._

## 만약 당신이...

- ✋ Claude Code · Cursor · Lovable로 진입했는데 **6개월째 pivot 반복**하고 있다면
- ✋ "이게 진짜 페인일까" 직감으로만 판단하고 **곧장 PRD부터 쓰고** 있다면
- ✋ "AI 무제한" 가격 약속했는데 **스케일에서 마진이 어떻게 잡힐지 계산을 못 했다면**
- ✋ 3개월 전 팀이 죽인 아이디어를 다시 들고 와도 **왜 죽였는지 기억 안 난다면**
- ✋ 빠른 도구는 다 있는데 **무엇을 만들지·왜 만들지가 모호하다면**

**hplan은 그 모든 미끄러짐을 PRD(제품 기능 명세서) 전에 멈춥니다.**

---

## 왜 만들었나 — AI 시대의 진짜 병목

2026년 시장에는 **바이브코딩·풀스택 빌딩 강의가 넘쳐납니다**. Claude Code · Cursor · Replit · Lovable · Bolt 같은 도구 사용법, Next.js + Supabase + Vercel + Stripe 풀스택 빌딩, AI Wrapper SaaS 빌딩, LangGraph 멀티에이전트 — 다 있죠.

그런데 모두 **"코딩 자동화의 사용법"** 입니다. Anthropic이 직접 *"90% 코드를 Claude Code가 쓴다"* (O'Reilly 2026.04)고 선언한 영역. AI가 곧 더 잘하게 될 영역.

**비개발자·1인 메이커가 이 도구들로 빌딩에 뛰어들면서 진짜 부족해진 4가지 능력**:

1. **"무엇을 만들 것인가"** — Discovery, ICP(Ideal Customer Profile — 가장 먼저 사줄 한 명)/JTBD 정의
2. **"왜 이게 진짜 페인인가"** — 인터뷰·검증·가설 사고
3. **"내가 만든 게 진짜 가치 있나"** — PMF(Product-Market Fit — 시장이 이 제품을 원하는 신호) 측정·Eval·메트릭 사고
4. **"첫 사용자를 어떻게 찾고 늘리나"** — Acquisition·Build in Public 사고

= 이 4가지가 모두 **"PM 사고"의 영역**입니다.

시장에 코딩 자동화 강의는 넘치고, **PM 사고 빌딩 도구는 거의 0**. hplan은 그 빈자리를 채웁니다.

---

## 누가 만들었나

저는 **김생근(Ethan)**입니다.

20년간 PM 일을 하면서 본 패턴 하나: **시장조사·문제정의가 풀리지 않은 채 빌딩에 들어가는 게 1인 메이커가 6개월을 잃는 가장 비싼 사고**입니다.

대기업 PM이 누리는 "다음 PRD 쓰기 전 5명 인터뷰" 규율이 1인 메이커에게는 없습니다. 그래서 hplan은 그 하네스를 *결정론적 도구*로 강제합니다 — Python 스크립트, MCP 서버, Claude Code hook, append-only registry 형태로.

---

## 어떤 사람을 위한 도구인가

**한 줄 정의**: *"제품을 빠르게 만들고 싶은데, 시장조사·문제정의가 풀리지 않아 못 나아가는 사람"*

| # | 페르소나 | 진짜 페인 | hplan으로 풀고 싶은 것 |
|---|---|---|---|
| **A** | 비개발자 1인 메이커 | Claude Code 진입 후 PMF 못 찾음 | 시장조사·문제정의 풀고 PMF 도달 |
| **B** | 주니어-미들 PM (사이드 프로젝트) | 회사 일이 아니니 ICP 정의가 어려움 | AI Native PM 전환 + 본인 SaaS Live |
| **C** | 직장인 사이드 빌더 | 퇴근 후 SaaS 만들고 싶은데 어디서 시작할지 모름 | 60일 빌딩 일지 + 첫 5명 paying user |
| **D** | 비개발자 솔로 founder | 공동창업자·외주 없이 직접 빌딩 — Spec·Eval 모름 | Claude Code + Spec-Kit 풀 셋업 + 첫 5명 |
| **E** | 기업 PM (사이드만) | 본업과 별개로 본인 제품 만들고 싶음 | 본인 SaaS Live + 기업 경험 압축한 분야별 비법노트 |

---

<p align="center">
  <video src="https://github.com/kimsanguine/hplan/releases/download/v0.9.0-video-preview/v9-core-16x9.mp4" autoplay loop muted playsinline width="800">
    <img src="docs/images/demo-terminal.svg" alt="hplan demo — 5-plugin 라이프사이클: hplan(게이트) → discover → architect → deliver → operate" width="800"/>
  </video>
</p>

> 🎬 **99초 소개 영상** — 5-plugin 라이프사이클 전체 흐름. 영상이 재생되지 않으면 [여기서 시청](https://github.com/kimsanguine/hplan/releases/tag/v0.9.0-video-preview).

## 하루 동안 hplan은 이렇게 끼어듭니다

hplan을 설치한 뒤에도 Claude와 평소대로 대화하면 됩니다. 단, **1인 메이커가 가장 자주 미끄러지는 순간**에 hplan이 멈춰줍니다:

| 당신이 Claude에게 하는 말 | hplan이 하는 일 |
|---|---|
| **"고객용 AI 어시스턴트 만들자"** | evidence부터 묻습니다. *"이 일에 주 30분 이상 쓰는 사용자가 누구인가요? 실제 고객 발화 3건 보여주세요."* 못 보여주면 PRD 작성을 멈춥니다. |
| **"이 AI 기능 월 ₩19,000에 팔자"** | 실제 provider 단가 + 예상 사용량 + 무료 abuse 시나리오로 COGS 계산. *"p50 마진 78%, p90 41%, free abuse 포함 −12%"*. 무엇을 바꿔야 하는지 정확한 숫자로 보여줍니다. |
| **"이거 지난 분기 Alex가 제안했던 거랑 비슷한데?"** | decision-log 조회. *"네 — 2026-02-03에 hold됐습니다. 이유는 [...]. 재검토 조건은 '엔터프라이즈 고객이 명시적으로 요청'. 그 조건이 충족됐나요?"* |
| **"마케팅 자동화 AI 만들자"** | exclusions registry 검사. *"이전 exclusion ex-2026-04-17과 겹칩니다. 기존 incumbent가 이미 점유. 재오픈 조건은 [...]. 해당되나요?"* |
| **"spec 짜서 바로 개발 시작하자"** | 게이트가 모두 GREEN인지 확인 후에야 spec 파일 생성. Evidence "interview", COGS "RED"이면 **파일 자체가 생성 안 됨**. filesystem 레벨 차단. |
| **"내 제품 결정이 정말 맞았나?"** | 최근 6-12개월 결정을 자동 audit. *"hold 8건 중 6건은 실제로 죽은 게 맞고 (correct), 2건은 다른 사람이 성공시켰음 (false_hold). 이 2건의 공통점은 [...]"* |
| **"이제 배포해도 되겠지?"** | QA 라운드가 확인합니다. evidence 단계에서 만든 페르소나 + PRD §15에서 결정된 도메인·개발 역할 에이전트가 병렬 검토. CRITICAL·HIGH = 0이 될 때까지 자동 수정 반복. 완료되면 `harness/qa-rounds/round-N.md` 최종 보고.<br><br>**전제 조건**: `deliver/qa-checklist --mode adversarial` 실행 전 두 파일이 필요합니다:<br>• `harness/PERSONA_SPECS.json` — `interview-synthesis audit` PASS 후 자동 생성<br>• `harness/QA_POOL.json` — `prd §15` 작성 후 자동 생성 |

핵심: **hplan을 일부러 부르지 않아도 됩니다.** "만들자", "팔자", "출시하자", "spec 짜자" 같은 말이 나오는 순간 자동 발동.

> 🆕 **Claude Code가 처음이라면?** → [`deliver/agent-setup`](deliver/skills/agent-setup/SKILL.md)가 프로젝트를 스캔하고, CLAUDE.md를 자동 생성하고, 맞는 hplan 플러그인을 추천해줍니다. 가장 빠른 온보딩 방법입니다.

---

## 60일 후 결과를 어떻게 측정하나

hplan을 PM 사고 도구로 깔고, 60일에 SaaS 1개를 Live하는 흐름:

```
Day 0-21    PM Discovery (Evidence Gate)
            └─ 인터뷰 5건 → ICP/JTBD 확정 → exclusions 정리
            ★ 첫 5명 베타 paying user

Day 22-49   빌더 작업 (Product + Build Gate)
            └─ Claude Code + Spec-Kit → 핵심 feature 3종
            └─ COGS sentinel GREEN → 가격 출시
            ★ 첫 10명 paying user

Day 50-60   매출·성과 구조
            └─ Eval suite + 5층 메트릭 + Build in Public
            ★ 30명 paying user (= ₩570,000 MRR)
```

**이 흐름이 패스트캠퍼스 25차시 강의의 백본이기도 합니다.** 강의에서는 Ethan이 PMFlow (PM의 1일 통합 AI Agent, ₩19,000/월)를 라이브 빌딩하면서 모든 결정에 "PM은 이렇게 한다"를 보여주고, 수강생은 본인 SaaS를 본인 분야로 만듭니다.

> 강의 정보 (D-day 2026년 6월 말 OT 촬영): [패스트캠퍼스 — 추후 업데이트]

---

> 💡 **심화 내용** — 처음이라면 건너뛰어도 됩니다.

## 기술적으로는 — Under the Hood

다른 PM toolkit과 hplan이 *어떻게* 다른지 궁금한 분께. 컨셉은 같지만 **결정론적 측정** + **영구 메모리** + **filesystem 레벨 강제**가 차별점:

- 🧪 **실행 가능한 COGS sentinel** — LLM 추정이 아니라 실제 Python sampler가 provider 단가 스냅샷으로 p50/p90 월간 마진 계산. 무료 사용자 abuse도 모델링.
- 📚 **Append-only exclusions registry** — 모든 "Do Not Build" 결정이 JSONL에 `reopen_trigger`와 함께 저장. 새 아이디어는 한국어 fuzzy match로 자동 collision check.
- 📊 **Self-evaluating decision log** — 모든 gate 결정이 이유와 함께 기록되고, outcome은 나중에 back-fill, `audit` 명령이 hit rate / false holds / missed builds 산출. 자기 정확도를 측정하는 유일한 PM gate.
- 🔌 **MCP server** — 같은 gate primitive가 MCP tool로도 노출되어 Cursor / Windsurf / Kiro / Codex / Goose에서도 호출 가능.
- 🛑 **Claude Code PreToolUse hook** — `harness/build-gate/checkpoint.json`이 `status: "approved"`가 되기 전까지 PRD.md / specs/* / .kiro/specs/* 작성을 파일 시스템 레벨에서 차단. 프롬프트 룰이 아닌 강제력 있는 게이트.
- 🚚 **Multi-target handoff** — 단일 brief JSON이 Spec-Kit `specs/NNN-slug/`, Kiro `.kiro/specs/`, GStack `/office-hours` brief, Claude Code `AGENTS.md` + `CLAUDE.md`로 동시 export.
- 📋 **Append-only qa_log.jsonl** — 배포 전 QA 라운드별 영구 로그. 페르소나·개발 리뷰어 풀, CRITICAL/HIGH 건수, 자동 수정 내역, 테스트 delta 추적. `decisions.jsonl` 패턴 확장 — "몇 라운드 만에 CRITICAL=0이 됐는지"가 다음 제품 QA 설계의 학습 데이터.

*이전 이름 `AI_PM_Skills` — v0.5에서 새 flagship plugin인 `hplan`이 라이프사이클 Stage 0에 들어가면서 리네임. 옛 URL은 자동 redirect.*

---

## 세 개의 엔지니어링 레이어

대부분의 AI PM 도구는 한 레이어에서만 작동합니다. hplan은 세 레이어를 모두 담은 유일한 프레임워크입니다:

| 레이어 | 역할 | hplan 도구 |
|--------|-----|-----------|
| **프롬프트 엔지니어링** | 의견이 아닌 실제 신호를 추출하는 구조화된 프롬프트 | evidence-rubric · interview-synthesis · OST |
| **컨텍스트 엔지니어링** | *쓰레기를 넣으면 쓰레기가 나온다.* LLM에 무엇이 들어가는지가 결과를 결정한다. 고객 문서·시장 데이터·경쟁사 분석이 PRD *이전*에 들어와야 한다. exclusions registry와 decision-log는 영구적으로 구조화된 기관 기억으로서의 컨텍스트다. | exclusions · decision-log · interview-synthesis |
| **하네스 엔지니어링** | 시스템 레벨의 결정론적 가드레일: Python 스크립트, append-only JSONL 레지스트리, 파일 시스템에서 PRD 작성을 차단하는 PreToolUse hook. 건너뛰고 싶어도 건너뛸 수 없는 규율. | gate_guard.py · cogs_sentinel.py · exclusions_registry.py · MCP 서버 |

> *프롬프트 엔지니어링은 어떻게 묻는지를 개선한다. 컨텍스트 엔지니어링은 무엇이 들어가는지를 결정한다. 하네스 엔지니어링은 진행할지 말지를 강제한다.*

잘 짜인 프롬프트에 잘못된 고객 데이터를 넣으면 자신감 있게 틀린 결론이 나옵니다. 훌륭한 evidence rubric도 개발자가 무시하고 PRD를 쓸 수 있다면 의미가 없습니다. 세 레이어가 모두 필요하고, 순서가 있습니다.

## WHETHER — 다른 도구들이 묻지 않는 질문

> **"AI 코딩 도구가 HOW를 잘하게 됐다면, hplan은 WHETHER(만들어야 하는가 YES/NO 판정)를 다룬다. 둘은 같이 쓰는 것이 아니라 순서가 있다 — hplan이 먼저다."**

**HOW**는 묻습니다: *"어떻게 만들까?"*
**WHETHER**는 묻습니다: *"만들어야 하는가 — YES인가 NO인가?"*

WHETHER는 WHY보다 큽니다. WHY는 이유를 답합니다("왜 사용자가 돈을 낼까?"). WHETHER는 WHY를 *포함*하는 이진 판정입니다 — hplan의 각 게이트는 WHY 질문에 답하고, 세 WHY가 합쳐져 WHETHER가 나옵니다:

| 게이트 | 답하는 WHY | 생성하는 WHETHER |
|--------|-----------|----------------|
| Evidence Rubric | 사용자에게 정말 이 문제가 있는가? | 진행할 충분한 증거가 있는가? |
| Exclusions Check | 이전에 왜 이 아이디어를 죽였나? | 이번 시도는 의미 있게 다른가? |
| COGS Sentinel | 왜 이 가격이 스케일에서 작동하는가? | 실제 비즈니스를 지탱할 수 있는가? |
| **세 개 합산** | — | **GO / HOLD / INVESTIGATE** |

다른 도구들은 **HOW**(superpowers → Claude Code 활용법), **WHO**(gstack → 에이전트 역할), **WHERE**(GSD → 워크플로우 위치)를 다룹니다. hplan은 **WHETHER** — 모든 결정보다 먼저 오는 결정을 다룹니다.

---

## 왜 이 프로젝트를 만들었나

2026년, PM들에게 "에이전트를 만들라"는 요구가 쏟아지고 있습니다.

그런데 기존 PM 스킬은 이 상황에 맞지 않습니다. 시중의 PM 스킬들은 **AI를 도구로 쓰는 법** — PRD를 빨리 쓰고, OKR을 자동 생성하고, 경쟁사를 분석하는 데 초점을 맞추고 있죠. 하지만 **에이전트를 제품으로 만드는 순간**, 부딪히는 질문은 완전히 달라집니다:

- "이 에이전트를 하루 1,000명이 쓰면 비용이 얼마나 나올까?"
- "에이전트가 환각(hallucination)을 일으키면 어떻게 복구시키지?"
- "에이전트 여러 개를 어떻게 조합하고 오케스트레이션하지?"
- "3개월 동안 쌓은 운영 노하우를 에이전트 인스트럭션에 어떻게 녹이지?"

저도 같은 질문을 했습니다. AI Dubbing, AI Avatar 서비스를 성장시키면서, 그리고 지금 Agentic AI 제품을 만들면서 마주친 문제들이었습니다. 그 경험을 체계화해서, 에이전트 라이프사이클 전체를 커버하는 **34개 프로덕션급 스킬**로 정리한 것이 이 프로젝트입니다.

---

## 30초 데모 셋업 (로컬 클론)

> CLI 사용자 전용. 데스크탑 앱은 아래 **빠른 시작** 의 마켓플레이스 경로를 사용하세요.

```bash
# 한 번만 실행 — 클론 + alias 자동 등록
bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan/main/scripts/setup.sh)
source ~/.zshrc   # 또는 ~/.bashrc

# 이후 바로 사용
claude-hplan       # 5-plugin 전체 (gate + discover + architect + deliver + operate)
claude-hplan-gate  # 게이트만 (WHETHER 판단 전용)
```

---

## 빠른 시작 (60초)

> **시스템 요구사항:** Claude Code v1.0+, Python 3.9+ (Evidence Gate 스크립트용), Git (pre-commit hook 선택). 자세한 설치 환경은 [GUIDE-ko.md](GUIDE-ko.md#시스템-요구사항) 참조.

### 유료 강의 수강생용 private 설치

```bash
bash <(curl -fsSL https://habix.ai/hplan/install.sh)
```

이 명령은 private package를 `~/hplan`에 설치하고 로컬 Claude CLI alias를 등록합니다. 운영 방식은 [`docs/private-distribution.md`](docs/private-distribution.md)에 정리되어 있습니다.

### 방법 A — 라이프사이클 커맨드 (권장, hplan 1개만 설치)

```bash
# Claude 세션에서 실행
/plugin marketplace add kimsanguine/hplan
/plugin install hplan@kimsanguine-hplan

# 전체 라이프사이클을 5개 커맨드로
# (harness-discover가 먼저 실행되는 이유: gate 판단에 필요한 evidence를 수집합니다)
/harness-discover "AI 마케팅 카피 생성기"   # 기회 매핑 + 가정 분석 + 비용 추정
/hplan "AI 마케팅 카피 생성기"            # WHETHER gate — GO / HOLD / INVESTIGATE
/harness-plan "마케팅 카피 에이전트"        # 아키텍처 설계 + W1 Done Criteria
/harness-build "마케팅 카피 에이전트"       # COGS gate → PRD 자동 작성 → W1 스프린트
/harness-operate "마케팅 카피 에이전트"     # 주간 KPI · 비용 · 개선 계획
```

### 방법 B — 게이트 세밀 제어 (전체 플러그인 설치 시)

```bash
# Claude 세션에서 실행
# 3개 게이트를 한 번에 — exclusions + evidence + COGS → 판정
/hplan "AI 마케팅 카피 생성기"
# → [exclusions] COLLISION with ex-2026-04-17 (해당 영역 이미 점유 중)
# → reopen_trigger UNMET → HOLD

# 개별 게이트로 깊은 분석:
/evidence-rubric "AI 마케팅 카피 생성기"   # 100점 루브릭 전체 + 인터뷰 합성
/cogs-sentinel --provider anthropic --model claude-sonnet-4-6 \
               --tokens-in 3000 --calls 40 --arpu 29
# → p50 마진 95%, p90 90%, blended 49% → GREEN
```

**Gate 통과 후** — VERDICT: GO가 나오면 추가 플러그인을 설치해 더 깊은 스킬을 활용할 수 있습니다:

```bash
# Claude 세션에서 복붙 (필요한 것만 선택해도 됩니다)
/plugin install discover@kimsanguine-hplan   # 발견 — opportunity tree, assumptions, cost sim
/plugin install architect@kimsanguine-hplan  # 설계 — orchestration, memory, moat
/plugin install deliver@kimsanguine-hplan    # 실행 — agent PRD, instruction, prompt, harness, design
/plugin install operate@kimsanguine-hplan    # 측정·학습·운영 — KPI, burn rate, PM 암묵지, 포트폴리오
```

스킬 이름을 외울 필요는 없습니다. 자연어로 질문하면 33개 스킬 중 맞는 게 auto-load 됩니다.

---

## 에이전트 PM 여정 — 5-plugin

이 프로젝트의 34개 스킬은 무작위 모음이 아닙니다. 에이전트 제품을 만드는 PM이 반드시 거치는 **5-plugin 라이프사이클** — v0.11.0부터 대규모 통합을 거쳐 더 단순하고 명확한 구조가 됐습니다.

```
게이트 → 발견 → 설계 → 딜리버리 → 운영
hplan   discover  architect  deliver   operate
  8        5         5          10        6   skills

   ↑                                            │
   └────── 축적된 TK가 다음 에이전트에 피드백 ─────┘
```

| 단계 | 플러그인 | 이 단계에서 부딪히는 질문 | 주요 스킬 |
|------|---------|------------------------|----------|
| **게이트** ⭐ | `hplan` | "정말 만들 가치가 있을까?" | brainstorm · evidence-rubric · interview-synthesis · exclusions · cogs-sentinel · ost · decision-log · handoff |
| **발견** | `discover` | "어떤 에이전트를 만들어야 할까?" | opp-tree · assumptions · cost-sim · hitl |
| **설계** | `architect` | "어떻게 구조를 잡을까?" | orchestration · router · memory-arch · design-token · strategy |
| **실행** | `deliver` | "어떻게 스펙을 쓰고 출시할까?" | agent-setup · prd · conductor · sprint · build-loop · respect · qa-checklist · ui-validate |
| **운영** | `operate` | "측정·학습·포트폴리오를 어떻게 할까?" | metrics-design · reliability · pm-engine · incident · ops-review · portfolio |

### hplan이 나머지 4개와 다른 점

다른 plugin들은 **prompt-driven thinking** — LLM이 고민하고 사람이 결정합니다.
`hplan`은 **deterministic measurement** — Python 스크립트가 p50/p90 COGS 마진을 계산하고, append-only registry가 exclusions/decisions를 영구 누적하고, MCP 서버가 Cursor/Windsurf/Kiro/Codex에서 hplan을 호출 가능하게 하고, PreToolUse hook이 사람 승인 전까지 PRD/spec 작성을 차단합니다. **`scripts/validate-mermaid.py`**가 PRD의 workflow ↔ userflow ↔ requirements 정합성을 결정론으로 차분 검증합니다. **discover/architect/deliver/operate를 대체하지 않고 layering**합니다.

특히 중요한 건 **마지막 단계인 operate → 첫 단계인 discover로 이어지는 순환 구조**입니다. operate에서 축적한 PM 운영 노하우(TK)가 다음 에이전트를 만들 때 자동으로 반영되기 때문에, 에이전트를 만들수록 다음 에이전트의 품질이 올라갑니다.

스킬 간에는 **자동 라우팅**도 작동합니다. 예를 들어 burn-rate(operate)로 토큰 비용을 분석하다 급증이 감지되면, router(architect)에게 모델 변경을 제안하고, 다시 cost-sim(discover)에서 비용 재시뮬레이션까지 연결됩니다. PM이 직접 "다음 스킬을 불러줘"라고 말할 필요가 없습니다.

---

## 이 프로젝트가 다른 이유 — 다른 스킬셋이 못하는 6가지

### ① 완전한 에이전트 라이프사이클 — 단편적 도구 모음이 아닙니다

시중의 PM 스킬셋은 대부분 "AI로 뭔가를 빠르게 하는 도구"입니다. PRD 자동생성, OKR 작성기, 경쟁사 분석기 같은 것들이죠. 하지만 에이전트를 제품으로 만들 때는 "어떤 에이전트를 만들지 → 어떻게 설계할지 → 어떻게 스펙을 쓸지 → 어떻게 운영할지 → 어떻게 학습시킬지"라는 **연속된 흐름**이 필요합니다.

이 마켓플레이스의 34개 스킬은 5-plugin에 정확히 매핑됩니다. 발견부터 자기개선 에이전트, 그리고 harness 기반 빌드와 포트폴리오 운영까지, **에이전트를 제품으로 만드는 구조화된 방법론**입니다.

### ② 2레이어 아키텍처 — Platform과 Content의 분리

스킬이 많아지면 반드시 생기는 문제가 있습니다: **"엉뚱한 스킬이 발동된다."** 33개 스킬이 서로 비슷한 키워드에 반응하면, Claude가 혼동을 일으키거든요.

이 문제를 해결하기 위해 **두 층을 분리**했습니다. Claude가 스킬을 찾는 메커니즘(Platform Layer — Skills 2.0 스펙의 frontmatter, auto-invocation 등)과, 각 스킬 안에서 "언제 나를 부르고, 언제 부르지 말아야 하는지"를 정의하는 내용(Content Layer — Trigger Gate 패턴)을 분리한 것입니다. 33개 스킬이 동시에 카탈로그에 있어도 routing 충돌이 안 나는 이유입니다.

```
┌─ Platform Layer ──── Skills 2.0 Spec ──────────────────────┐
│  frontmatter · auto-invocation · subagent · hooks · evals   │
├─ Content Layer ──── hplan 독자 패턴 ────────────────┤
│  Core Goal → Trigger Gate(Use/Route/Boundary)               │
│  → Failure Handling → Quality Gate → Examples               │
│  → context/domain.md (도메인 전문지식)                       │
└─────────────────────────────────────────────────────────────┘
```

Trigger Gate의 핵심은 세 가지입니다:
- **Use**: "이런 상황에서 나를 불러라" (정확한 발동 조건)
- **Route**: "이런 상황이면 다른 스킬에게 넘겨라" (플러그인 간 라우팅)
- **Boundary**: "이런 상황에서는 절대 나를 부르지 마라" (오발동 방지)

이 패턴 덕분에 260개 테스트 쿼리에서 **93.5% 트리거 정확도**를 달성했습니다 (34개 스킬 기준, 3회 majority vote). 34개 스킬이 서로 충돌하지 않고 정확하게 발동됩니다.

### ③ 데이터 플라이휠 — 쓸수록 쌓이는 PM 암묵지

이 프로젝트의 진짜 해자(moat)는 `operate` 플러그인입니다.

PM이 수년간 쌓은 운영 판단력 — "이런 상황에서는 이렇게 해야 해", "이 지표가 떨어지면 이게 원인일 확률이 높아" — 이런 암묵지는 보통 PM의 머릿속에만 있습니다. operate 는 이것을 **TK(Tacit Knowledge) 단위**로 구조화합니다.

```
PM의 판단/경험 기록 → /extract 명령어 → TK-NNN으로 구조화
  → PM-ENGINE-MEMORY.md에 축적 → /tk-to-instruction으로
  → 에이전트 시스템 프롬프트에 자동 반영 → 쓸수록 반복·축적
```

**왜 이게 중요하냐면**, 이렇게 축적된 TK는 경쟁자가 복사할 수 없기 때문입니다. 프레임워크 자체는 오픈소스이지만, PM-ENGINE-MEMORY.md에 쌓인 당신만의 판단 기록은 당신의 자산입니다. 에이전트를 오래 운영할수록 이 데이터가 쌓이고, 그게 다음 에이전트의 품질을 올리는 **전환비용(switching cost)**이 됩니다.

### ④ Eval 기반 ROI — "좋아졌다"는 느낌이 아닌, 숫자로 증명

"스킬을 설치하면 뭐가 좋아지는데?"라는 질문에 "느낌적으로 좋아집니다"라고 답하지 않습니다.

모든 스킬은 **54개 어설션을 포함한 10개 품질 테스트**로 측정됩니다. 같은 질문을 스킬 적용/미적용 상태로 Claude에게 던져서, 출력 품질 차이를 정량화합니다.

| | 스킬 적용 | 스킬 미적용 | 차이 |
|---|-----------|-----------|------|
| **테스트 통과율** | **100%** | 88% | **+12%** |

구체적으로 보면, `pm-framework` 스킬 없이 Claude에게 "운영 노하우를 구조화해줘"라고 하면 통과율이 40%까지 떨어집니다. `cost-sim` 스킬을 적용하면 비용 분석 산출량이 +46.6% 증가합니다. 이런 숫자가 있기 때문에, 어떤 스킬이 실제로 가치를 더하는지, 어떤 스킬을 개선해야 하는지를 **데이터로 판단**할 수 있습니다.

### ⑤ Good/Bad 예시 — 스킬 품질을 지속적으로 개선하는 장치

모든 스킬에는 `examples/good-01.md`(이상적인 출력)와 `examples/bad-01.md`(피해야 할 출력)가 포함됩니다. 여기에 `references/test-cases.md`의 엣지 케이스 테이블까지 있습니다.

이게 왜 중요하냐면, LLM 기반 스킬은 **"뭘 잘했는지, 뭘 못했는지"를 명확히 정의하지 않으면 개선할 수가 없습니다.** Good/Bad 예시가 있으면 Claude의 출력을 구체적인 기준으로 평가할 수 있고, 그 결과를 다시 스킬 개선에 반영할 수 있습니다. 장식이 아니라, 스킬 품질을 측정 가능하고 지속적으로 개선 가능하게 만드는 핵심 장치입니다.

### ⑥ Skills 2.0 최신 스펙 + 즉시 시작 가능한 온보딩

Claude Code의 최신 플랫폼 스펙을 모두 적용했습니다: auto-invocation(자동 호출), `context: fork`(서브에이전트 분리), `allowed-tools`(도구 접근 제한), `model` 필드(모델 지정), 동적 `!command` 주입, marketplace 배포, eval 시스템까지.

그런데 스펙만 따르면 새 사용자가 빈 파일로 시작해야 합니다. 그래서 [PM-ENGINE-MEMORY 스타터 킷](operate/skills/pm-engine/examples/PM-ENGINE-MEMORY-STARTER.md)을 함께 제공합니다. 실무에서 자주 쓰이는 5개 시드 TK(긴급 요청 우선순위, AI 네이티브 사고 필터, 에이전트 비용 10배 법칙 등)가 미리 들어 있어서, 설치 직후부터 operate의 가치를 체감할 수 있습니다. "데이터가 쌓이면 좋아질 거야"가 아니라, **설치한 순간부터 바로 쓸 수 있는** 설계입니다.

---

## 플러그인 — 전체 스킬 목록

<details>
<summary><strong>1. hplan ⭐</strong> — 정말 만들 가치가 있을까? <code>(8 skills, 9 commands)</code></summary>

발견(discover)보다 *먼저* 돌아가는 게이트. LLM 추정이 아닌 결정론적 Python 측정, run 간 영구 누적되는 메모리 (exclusions + decisions), 사람 승인 전까지 PRD/spec 작성을 막는 hook까지.

| 스킬 | 기능 | 이런 상황에서 쓰세요 |
|------|------|-------------------|
| `evidence-rubric` | 8축 100점 evidence 루브릭으로 점수화 — ICP, 최근 통증 이벤트, 현재 우회법, 반복도, 경제적 손실, 전환 트리거, MVP 좁힘, 첫 5명 획득 경로 | "이 아이디어 인터뷰까지라도 갈 가치가 있나?" |
| `interview-synthesis` | BuildBetter / Perspective 등 AI 합성 결과 import → 인간이 strength + Push/Pull/Habit/Anxiety 축 태깅 강제 → 5명 중 3명 강한 Push 패턴 audit | "고객 인터뷰 5건 끝났는데 패턴이 충분한가?" |
| `exclusions` | Append-only Do-Not-Build 영구 메모리. 한국어 fuzzy match로 collision 자동 감지 + reopen_trigger 보존 | "지난 분기 했던 거랑 비슷한데 — 그때 왜 죽였더라?" |
| `cogs-sentinel` | 실행 가능한 COGS 게이트 — lognormal sampler가 p50/p90 월간 마진 계산, free-user abuse blend, GREEN/CONDITIONAL_GO/RED 결정 | "월 $19에 팔면 p90 마진이 살아남나?" |
| `ost` | Teresa Torres 식 Opportunity Solution Tree를 `docs/OPPORTUNITY_TREE.md`로 Mermaid 다이어그램과 함께 생성 | "PRD 쓰기 전에 opportunity → solution → experiment 트리 잠그기" |
| `decision-log` | Append-only build/interview/pivot/hold 로그 + 3-6개월 뒤 self-eval audit (hit_rate, false_holds, missed_builds) | "6개월 전 내 제품 결정이 실제로 맞았나?" |
| `brainstorm` | 아이디어를 제품 컨셉으로 발전시키는 브레인스토밍 — 질문 흐름 구조화, 트레이드오프 탐색, 접근법 2~3가지 제안 | "막연한 아이디어를 PRD 이전에 구체화하고 싶어" |
| `handoff` | Build Gate brief → Spec-Kit / Kiro / GStack / Claude Code 4개 ecosystem 동시 export | "이제 코딩 에이전트로 넘어가자 — spec 자동 생성" |

**라이프사이클 커맨드 (hplan 1개만 설치해도 전체 커버):**

| 커맨드 | 단계 | 기능 |
|--------|------|------|
| `/harness-discover <idea>` | Discover | 기회 매핑 → 가정 분석 → 비용 시뮬 → 빌드/바이 결정 |
| `/harness-plan <system>` | Plan | 오케스트레이션 → 3-tier → 메모리 → 모델 라우팅 |
| `/harness-build <brief>` | Build | COGS gate + PRD 15-section 자동 작성 + W1 스프린트 |
| `/harness-operate <agent>` | Operate | KPI · 신뢰성 · 비용 · 개선 계획 + 지식 추출 |

**게이트 세밀 제어:** `/hplan` · `/harness-exclude` · `/harness-handoff` · `/harness-doctor`

**Cross-cutting 자산:** MCP 서버 (`hplan_mcp/`) — Cursor / Windsurf / Kiro / Codex / Goose 호환 · PreToolUse hook (`hooks/gate_guard.py`) · 4개 role-locked reviewer agents (`agents/`)
</details>

<details>
<summary><strong>2. discover</strong> — 어떤 에이전트를 만들까? <code>(6 skills)</code></summary>

에이전트를 만들기 전에 반드시 답해야 할 질문들 — "어디에 기회가 있는지", "리스크는 뭔지", "직접 만들어야 하는지 사야 하는지", "비용은 얼마인지"를 체계적으로 분석합니다.

> ⚠️ **현재 사용 가능 (6개):** `opp-tree` · `assumptions` · `cost-sim` · `hitl` · `socratic-question` · `customer-reach`
> 아래 목록의 `build-or-buy`, `agent-gtm`, `design-reference`는 **로드맵 예정**입니다 — 표에 섞여 있으니 위 6개만 호출 가능한 것으로 간주하세요.

| 스킬 | 기능 | 이런 상황에서 쓰세요 |
|------|------|-------------------|
| `opp-tree` | 반복 빈도·자동화 적합도·판단 의존도로 점수화한 기회 트리 구축 | "자동화 후보가 10개인데, 뭘 먼저 해야 할까?" |
| `assumptions` | 4축(가치·실현가능성·신뢰성·윤리) 기준 최고 위험 가정 추출 + 2일 검증 실험 설계 | "개발 시작 전에 가장 큰 리스크부터 확인하고 싶어" |
| `build-or-buy` | 6축 기준 Build vs Buy vs No-code 점수화 (차별화, 속도, 비용, 커스터마이징, 유지보수, 도메인) | "Intercom 봇을 쓸까, 우리가 직접 만들까?" |
| `hitl` | 가역성 × 오류영향 매트릭스로 자동화 레벨(1~5)과 에스컬레이션 기준 설정 | "환불 결정을 에이전트에게 맡겨도 괜찮을까?" |
| `cost-sim` | 1→10→100→1,000명 규모별 월간 운영 비용 시뮬레이션 (모델 가격 × 호출 패턴) | "Sonnet으로 하루 500콜이면 월 얼마 나올까?" |
| `agent-gtm` | 비치헤드 세그먼트 5기준 점수 + Shadow→Co-pilot→Auto→Delegation 신뢰 시퀀스 설계 | "B2B 고객에게 이 에이전트를 어떤 순서로 내보내지?" |
| `design-reference` | UI 레퍼런스 수집·구조화 + 디자인 언어 공통 패턴 추출 → 설계 시 참조 가능한 DESIGN-REFERENCE.md 생성 | "경쟁사·레퍼런스 앱에서 패턴을 뽑아 우리 설계에 반영하고 싶어" |
| `socratic-question` | PRD 작성 전 소크라테스식 질문으로 가정을 심문 — 숨은 리스크와 검증되지 않은 전제를 먼저 드러냄 | "아이디어에 뛰어들기 전에 내 가정을 먼저 검증하고 싶어" |

**커맨드:** `/harness-discover`
</details>

<details>
<summary><strong>3. architect</strong> — 어떻게 설계할까? <code>(5 skills)</code></summary>

에이전트의 구조를 잡는 단계입니다. 에이전트가 하나일 때는 괜찮지만, 여러 개가 협업해야 할 때 — 누가 전략을 짜고, 누가 실행하고, 비용은 어떻게 줄이고, 해자는 어떻게 만들지를 설계합니다.

> ⚠️ **현재 사용 가능 (5개):** `orchestration` · `router` · `memory-arch` · `design-token` · `strategy`
> 아래 목록의 `3-tier`, `biz-model`, `moat`, `growth-loop`는 **로드맵 예정**입니다 — 표에 섞여 있으니 위 5개만 호출 가능한 것으로 간주하세요.

| 스킬 | 기능 | 이런 상황에서 쓰세요 |
|------|------|-------------------|
| `3-tier` | Prometheus(전략) → Atlas(조율) → Worker(실행) 역할·통신·위임 설계 | "에이전트 5개가 필요한데, 누가 누구를 통제해야 하지?" |
| `orchestration` | Sequential/Parallel/Router/Hierarchical 패턴을 레이턴시·오류율·비용으로 비교 | "문서 처리 파이프라인을 직렬로 돌릴까, 병렬로 돌릴까?" |
| `biz-model` | 건당/구독/성과 기반 과금 설계 + 변동비 분석 (70% 이상 마진 타겟) | "API 호출당 과금? 월정액? 어떤 모델이 맞을까?" |
| `router` | 복잡도별 T1~T4 모델 자동 라우팅 + 폴백 체인으로 40-80% 비용 절감 | "단순 FAQ는 Haiku, 복잡 분석은 Opus — 자동으로 나눠줘" |
| `memory-arch` | Working/Episodic/Semantic/Procedural 메모리 레이어 + 토큰 예산 인식 검색 | "오늘 세션에서 어제 대화 맥락을 어떻게 기억시키지?" |
| `moat` | 6가지 해자 진단: 데이터 플라이휠, 워크플로우 락인, 네트워크 효과, 전환비용, 전문화, 브랜드 | "경쟁사가 GPT로 비슷한 걸 만들면, 우리 방어선은?" |
| `growth-loop` | 사용→데이터→개선→재사용 루프 설계 + 콜드스타트 해법 + 역루프(anti-loop) 식별 | "추천 결과가 쓸수록 좋아지게 만들려면?" |
| `design-token` | 색상·타이포·간격·그림자 디자인 토큰 체계 정의 + DESIGN.md 생성 → 일관된 UI 시스템 강제 | "컴포넌트마다 색이 다르게 들어가 있어, 토큰으로 통일하고 싶어" |

**커맨드:** `/harness-plan`
</details>

<details>
<summary><strong>4. deliver</strong> — 어떻게 스펙을 쓰고 출시할까? <code>(13 skills)</code></summary>

실제로 만들고 출시하는 단계입니다. 프로젝트 온보딩(CLAUDE.md 자동 생성)부터 에이전트 전용 PRD 작성, 시스템 프롬프트 설계, 토큰 예산 관리, 이해관계자 설득 자료 제작, 실행 진행 추적, 디자인 시스템 강제까지 포함합니다.

> ⚠️ **현재 사용 가능 (13개):** `agent-setup` · `prd` · `build-loop` · `qa-checklist` · `respect` · `sprint` · `ui-validate` · `conductor` · `ask-team` · `ticket-bridge` · `roadmap` · `stakeholder-update` · `stakeholder-review`
> 아래 목록의 나머지 스킬(instruction, prompt, ctx-budget, parallel-team 등)은 **로드맵 예정**입니다 — 표에 섞여 있으니 위 13개만 호출 가능한 것으로 간주하세요.

| 스킬 | 기능 | 이런 상황에서 쓰세요 |
|------|------|-------------------|
| `agent-setup` ⭐ | 프로젝트 구조 스캔 → CLAUDE.md 자동 생성 → 맞춤형 hplan 플러그인 추천 | "새 프로젝트에 Claude Code를 세팅하고, 어떤 스킬을 쓸지 추천받고 싶어" |
| `instruction` | Role/Context/Goal/Tools/Memory/Output/Failure 정의 + 최소 권한 도구 접근 설계 | "시스템 프롬프트에 뭘 넣고 뭘 빼야 하지?" |
| `prd` | **통합 15섹션 PRD** — 사람/문제/결정 (1-6) + 에이전트·실행 사양 (7-11) + 지표/가설/실패 (12-14) + QA Pool (15). 제품과 그 안의 에이전트를 단일 PRD로. | "1인 변호사 한국 판례 RAG PRD 작성해줘" |
| `prompt` | CRISP 프레임워크(Context/Role/Instruction/Scope/Parameters) + Why-First 원칙 + 7가지 실패 패턴 회피 | "프롬프트가 길어질수록 에이전트가 오히려 이상하게 동작해" |
| `ctx-budget` | 파일별 토큰 사용량 추정 → Essential/Conditional/Excluded 분류 → 70% 임계값 알림 | "RAG 문서 5개 + 대화 히스토리를 128K 컨텍스트에 어떻게 넣지?" |
| `okr` | 이중축 OKR: 비즈니스 임팩트 + 운영 건강도, 필수 비용 KR 포함 | "정확도 95%면 충분한가? 비용 지표도 넣어야 하는 거 아닌가?" |
| `stakeholder-map` | Power-Interest 매트릭스 + 블로커 대응 전략 + 내부 챔피언 발굴 | "법무팀이 에이전트 출시를 막고 있어, 어떻게 설득하지?" |
| `agent-plan-review` | 4축 리뷰 + 실패 모드 매트릭스(5+ 유형) + Mermaid 다이어그램 출력 | "코딩 시작 전에 이 설계의 허점을 찾아줘" |
| `gemini-image-flow` | Gemini API 엔드투엔드 이미지 파이프라인 + 모델 티어 자동 선택 | "스케치→코드 변환 파이프라인을 만들고 싶어" |
| `infographic-gif-creator` | 아키텍처/워크플로우 다이어그램 → HTML/CSS → GIF/MP4 애니메이션 | "멀티에이전트 흐름을 임원에게 시각적으로 보여줘야 해" |
| `pptx-ai-slide` | 스토리 기반 슬라이드 (피치/리뷰/투자자 변형 자동 생성) | "이사회 발표용 10장짜리 덱이 필요해" |
| `agent-demo-video` | 화면 녹화 + 애니메이션 + 나레이션 조합 (Remotion 기반) | "비기술 이해관계자에게 에이전트가 뭘 하는지 보여줘야 해" |
| `harness-design` | Build Gate harness 설계 — checkpoint.json + gate_guard.py 연동, 단계별 승인 흐름 정의 | "사람 승인 없이 PRD 바로 코딩으로 넘어가는 걸 막고 싶어" |
| `parallel-team` | 독립 태스크 분해 + 에이전트 팀 편성 → 병렬 실행 계획 + conflict 방지 설계 | "5개 태스크를 동시에 돌리고 싶은데 merge conflict가 걱정돼" |
| `ask-team` | 질문을 올바른 이해관계자 또는 에이전트 역할로 구조화하여 라우팅 — 잘못된 대상에게 물어보는 결정을 방지 | "이 트레이드오프를 누구에게 물어봐야 하지?" |
| `ticket-bridge` | PRD 결정과 게이트 출력물을 추적 가능한 티켓으로 변환 (Linear / Jira / GitHub Issues) | "게이트 판정 결과를 스프린트 티켓으로 자동 전환하고 싶어" |
| `build-loop` | 반복 구현 루프 설계 — TDD 단계 + 체크포인트 + self-review + commit 리듬 | "에이전트 구현 중에 어디서 멈추고 검증해야 할지 모르겠어" |
| `mobile-check` | 모바일 뷰포트 체크리스트 (터치 타겟·폰트 크기·safe area·스크롤 동작·landscape 레이아웃) | "PC에서 됐는데 모바일에서 깨져 — ship 전에 체크리스트 돌려줘" |
| `velocity-baseline` | 직전 프로젝트 git log + token usage → complexity × percentile lookup table 결정론 추출 | "예측 전에 내 실제 작업 속도부터 학습" |
| `estimate-tasks` | WBS 분해 + complexity 분류 (LLM) + loc/tokens/minutes 예측 (결정론 lookup) | "시작 전에 예측 scope lock — 얼마나 걸릴지 알고 싶어" |
| `progress-probe` | PostToolUse Hook + shell fallback → 매 tool call을 `.track/actual_log.jsonl`에 append | "매 prompt cycle 텔레메트리 — silent fail 대비 이중 메커니즘" |
| `blocker-detect` | 50+ 결정론 정규식·카운터 신호 (self-doubt / retry loops / test failures / context pressure / stalls) | "막힌 지점 자동 감지 — LLM 호출 0, 패턴+임계치만" |
| `progress-report` | 7 event-driven 트리거가 현재 상태 보고 강제 (phase 전환·블로커 임계·context 70% 시점) | "블로커 임계 도달 시점에 자동으로 상태 snapshot 받고 싶어" |
| `gate-checkpoint` | 6-phase 전환 게이트 (requirements → ship) PreToolUse Hook 차단 | "design phase 미통과 시 impl 코드 작성 기계적 차단" |
| `respect-checkpoint` | AI가 (screen_type × traffic) 분류 → 결정론 매트릭스 lookup → α+β+γ 게이트 조합 | "ship 직전 사용자 존중 게이트 — '이 존중은 사람이 넣는 겁니다' 강제" |
| `respect-brief` | 인터뷰 기반 RESPECT.md (5 섹션: three_second_rule / next_action / social_proof / hierarchy / motion) + 금지어 강제 | "UI 코드 작성 전 — 사용자 존중 의도를 YAML 제약으로 capture" |
| `hierarchy-rules` | Playwright + DOM saliency + pixel KMeans + WCAG AA 런타임 측정 (fold density / type hierarchy / 60-30-10 색 / whitespace / CTA count) | "사람이 실제로 본 것을 측정 — 토큰의 약속이 아님" |
| `motion-language` | 정규식 + framer-motion AST 스캔 → RESPECT motion_language 명세 대비 drift 보고 | "hover transition 200ms 일관? page easing 일관? ship 전 drift 감지" |
| `ui-drift-detect` | 5+ 화면 pHash + KMeans palette + DOM tree edit distance → 5 차원 drift score | "디자인 시스템 회귀 감지 — 신규 화면이 design language 깼나?" |

**커맨드:** `/harness-build`
</details>

<details>
<summary><strong>5. operate</strong> — 측정·학습·포트폴리오 운영 <code>(6 skills)</code></summary>

출시 이후가 진짜 시작입니다. 에이전트는 "조용히 틀리는" 경우가 많아서, 운영 지표 설정·비용 추적·실패 감지·실험 설계와 함께 PM 암묵지 구조화·포트폴리오 우선순위까지 한 플러그인에서 처리합니다.

> ⚠️ **현재 사용 가능 (6개):** `metrics-design` · `reliability` · `pm-engine` · `incident` · `ops-review` · `portfolio`
> 아래 목록의 나머지 스킬(kpi, burn-rate, premortem, scorecard-5axis 등)은 **로드맵 예정**입니다 — 표에 섞여 있으니 위 6개만 호출 가능한 것으로 간주하세요.

| 스킬 | 기능 | 이런 상황에서 쓰세요 |
|------|------|-------------------|
| `kpi` | 운영 + 비즈니스 5~7개 지표 정의, 선행/후행 지표 구분 | "에이전트 대시보드에 어떤 지표를 넣어야 하지?" |
| `reliability` | P95/P99 최악 케이스 정량화 + 세이프가드 설계 + SLA 티어 설정 | "100건 중 3건이 환각인데, 이게 허용 가능한 수준인가?" |
| `premortem` | 10~15개 실패 모드를 심각도 × 가능성 × 탐지 난이도로 점수화 | "'절대 깨지면 안 되는' 항목 리스트를 뽑아줘" |
| `burn-rate` | 모델·태스크별 토큰 비용 시각화 + 급증 감지 + 예산 상한 설정 | "이번 달 토큰 비용이 40% 올랐어 — 원인이 뭐야?" |
| `north-star` | 5가지 기준으로 핵심 지표 1개 선택 + 안티메트릭 설정 | "팀원마다 다른 KPI를 보고 있어, 뭘 기준으로 맞추지?" |
| `agent-ab-test` | MDE(최소 탐지 효과) 계산 + 동시 실험 설계 + LLM 비결정성 통제 | "프롬프트 A vs B — 진짜 차이가 있는 건지, 그냥 노이즈인지?" |
| `cohort` | 배포 코호트별 성과 추적 (최소 4주, n≥100 기준) | "v2.1이 정말로 v2.0보다 나아졌는지 확인하고 싶어" |
| `incident` | 무증상 장애 감지 + 트리아지 + 영향 범위 차단 + 5 Whys 분석 | "에이전트가 30분째 응답이 없는데 알림도 안 울려" |
| `pm-framework` | 암묵적 판단을 TK-NNN 단위로 변환 + 활성화/비활성화 조건 + 지식 그래프 연결 | "에이전트 운영 3년치 경험이 내 머릿속에만 있어" |
| `pm-decision` | 반복되는 PM 의사결정의 패턴 라이브러리 구축 (맥락, 기준, 실패 사례 포함) | "이 상황 전에도 겪었는데, 그때 왜 그렇게 결정했더라?" |
| `pm-engine` | 런타임에 TK 지식 그래프 동적 쿼리 + 하루 1건 TK 자동 추출 + 인스트럭션 자동 업데이트 | "내 운영 노하우를 에이전트가 알아서 활용했으면 좋겠어" |
| `agent-portfolio` | T1~T5 티어링 (Reach × Reliability × Strategic value) | "에이전트 5+ 개 운영 중 — 다음 분기에 어디 투자할까?" |
| `scorecard-5axis` | 가중 점수 (Accuracy / Reliability / Cost / Velocity / User Satisfaction) → 단일 비교 가능한 숫자 | "주간 운영 회의에서 에이전트 간 직접 비교" |
| `weekly-rollup` | Cron 기반 포트폴리오 rollup (trend + 이상 감지) | "월요일 아침 — 지난 주 fleet에 무슨 변화?" |
| `cross-team-routing` | capability × load × tier × handoff cost 점수화로 요청 라우팅 결정 | "3개 에이전트가 처리 가능 — 어디로 보낼까?" |

**커맨드:** `/harness-operate`

> 💡 [PM-ENGINE-MEMORY 스타터 킷](operate/skills/pm-engine/examples/PM-ENGINE-MEMORY-STARTER.md)으로 시작하세요 — 실무에서 검증된 5개 시드 TK가 미리 들어 있어, 빈 파일이 아닌 바로 쓸 수 있는 상태로 시작합니다.

> 프레임워크는 오픈소스입니다. 하지만 PM-ENGINE-MEMORY.md에 쌓이는 당신의 판단 기록은 당신만의 자산입니다.
</details>

---

## 설치

> **처음 설치라면 → 방법 A(Claude 데스크탑 앱)만 하면 됩니다.**
> CLI 사용자이거나 private 설치가 필요한 경우만 방법 B/C를 사용하세요.

### 방법 1: 자동 설치 스크립트 (CLI 권장)

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/kimsanguine/hplan/main/scripts/setup.sh)
source ~/.zshrc
```

`setup.sh` 가 수행하는 작업: 저장소 클론 → `claude-hplan` / `claude-hplan-gate` alias 등록 → git hook 설치 (선택).

> ⚠️ **`--plugin-dir` 플래그는 CLI 전용입니다.** 데스크탑 앱에서는 방법 2(마켓플레이스)를 사용하세요.

---

### 방법 2: GitHub Marketplace (데스크탑 앱 + CLI)

아래 명령을 **Claude 세션 안에서** 실행하세요 (`/` 로 시작하는 슬래시 커맨드는 터미널 bash가 아닌 Claude 세션에서만 동작합니다):

```
# 마켓플레이스 등록 (1회)
/plugin marketplace add kimsanguine/hplan

# 필요한 플러그인만 선택해서 설치
/plugin install hplan@kimsanguine-hplan
/plugin install discover@kimsanguine-hplan
/plugin install architect@kimsanguine-hplan
/plugin install deliver@kimsanguine-hplan
/plugin install operate@kimsanguine-hplan
```

> **Private repo 환경**: 마켓플레이스 설치가 "not found"로 실패하면, 방법 1(로컬 클론)을 사용하세요. 로컬 클론은 repo 공개 여부와 무관하게 동작합니다.

---

### 방법 3: 수동 로컬 클론

```bash
git clone https://github.com/kimsanguine/hplan.git ~/hplan

# 개별 플러그인 로드
claude --plugin-dir ~/hplan/hplan

# 전체 로드 (5-plugin)
claude \
  --plugin-dir ~/hplan/hplan \
  --plugin-dir ~/hplan/discover \
  --plugin-dir ~/hplan/architect \
  --plugin-dir ~/hplan/deliver \
  --plugin-dir ~/hplan/operate
```

---

**어디서부터 시작할지 모르겠다면?**
**어떤 AI 제품을 만들지 결정 못 하셨다면** → `hplan`으로 시작 — evidence 게이트가 먼저.
**Claude Code가 처음이라면** → `deliver/agent-setup`을 돌리면 프로젝트를 스캔하고 맞는 플러그인을 추천해줍니다.
**이미 게이트 통과했다면** → 라이프사이클 순서대로 (discover → architect → deliver → operate) 골라서 설치.

### 다른 AI 도구에서도 쓸 수 있습니다

명령어(commands)는 Claude Code 전용이지만, 스킬(SKILL.md) 자체는 다른 AI 도구에서도 그대로 동작합니다.

| 도구 | Skills | Commands | 사용법 |
|------|:------:|:--------:|--------|
| **Gemini CLI** | ✅ | ❌ | `.gemini/skills/`에 복사 |
| **Cursor** | ✅ | ❌ | `.cursor/skills/`에 복사 |
| **Codex CLI** | ✅ | ❌ | `.codex/skills/`에 복사 |
| **Kiro** | ✅ | ❌ | `.kiro/skills/`에 복사 |

---

<details>
<summary><strong>📐 아키텍처 상세</strong> — 기술적으로 어떻게 작동하는지 궁금하신 분을 위해</summary>

### 자동 호출 (Auto-Invocation)

스킬을 이름으로 부를 필요가 없습니다. "우리 CS팀 업무 중 에이전트가 맡을 수 있는 건 뭘까?"처럼 자연어로 질문하면, Claude가 각 SKILL.md의 `description` 필드와 매칭하여 가장 적합한 스킬을 자동으로 로드합니다. 260개 테스트 쿼리에서 **93.5% 정확도** (34개 스킬 기준).

### 크로스 플러그인 라우팅

하나의 스킬이 분석을 마친 뒤, 자연스럽게 다른 플러그인의 스킬로 넘기는 것이 가능합니다. Trigger Gate의 "Route" 필드가 이걸 선언적으로 정의합니다:

| 시작 스킬 | 이런 상황이 되면 | 넘어가는 스킬 |
|----------|---------------|-------------|
| `opp-tree` | "상위 기회의 가정을 검증해줘" | `assumptions` |
| `reliability` | "비용 급증 → 모델 라우팅 변경이 필요" | `router` |
| `prd` | "인스트럭션 설계가 필요해" | `architect/strategy` |
| `pm-engine` | "TK를 에이전트 인스트럭션으로 변환" | `prd` |

### 명령어 체이닝

> ⚠️ **아래 5개 슬래시 명령은 로드맵 예정입니다.** 현재 사용 가능한 슬래시: `/hplan` · `/prd` · `/harness-discover` · `/harness-plan` · `/harness-build` · `/harness-operate` · `/harness-doctor` · `/harness-exclude` · `/harness-handoff` · `/harness-verify` · `/evidence-rubric` · `/cogs-sentinel`. 아래 표는 향후 추가 예정 체이닝 패턴입니다.

| 명령어 (로드맵) | 실행되는 스킬 순서 | 플러그인 |
|--------|-----------------|---------|
| `/discover` | opp-tree → assumptions → hitl | discover |
| `/architecture` | orchestration → memory-arch → strategy | architect |
| `/write-prd` | prd → qa-checklist → respect | deliver |
| `/health-check` | metrics-design → reliability → ops-review | operate |
| `/tk-to-instruction` | pm-engine → prd | operate+deliver |

### Skills 1.0 vs Skills 2.0 — 이 프로젝트의 스펙 적용 현황

Claude Code의 스킬 시스템은 2025년 1.0에서 2026년 2.0으로 크게 업그레이드됐습니다. hplan은 Claude Code 2.0 스펙을 완전 적용한 상태입니다.

| 기능 | 1.0 (2025) | 2.0 (2026) | hplan 적용 |
|------|-----------|-----------|-----------------|
| Auto-invocation (자동 호출) | ❌ | ✅ | ✅ 93.5% 정확도 |
| Subagent (`context: fork`) | ❌ | ✅ | ✅ 5개 스킬 적용 |
| Tool restriction (도구 제한) | ❌ | ✅ | ✅ 3-tier 구조 |
| Marketplace + Evals | ❌ | ✅ | ✅ 전체 적용 |
| Dynamic injection (동적 주입) | ❌ | ✅ | ✅ 5개 스킬 적용 |
| Hooks | ❌ | ✅ | ⚠️ Spec-ready |

> ⚠️ `hooks`에 알려진 이슈가 있습니다 ([#17688](https://github.com/anthropics/claude-code/issues/17688)). 대체용 `validate_*.sh` 스크립트가 `references/`에 준비되어 있습니다.

### 파일 구조

```
hplan/                # repo 루트
├── hplan/            # Gate ⭐ (8 skills, 9 commands) — Product Build Gate
├── discover/           # 발견 (6 skills)
├── architect/            # 설계 (5 skills)
├── deliver/            # 실행 (13 skills)
├── operate/            # 운영·학습·포트폴리오 (6 skills)
│   └── evals/        # 품질 + 트리거 평가
├── docs/images/      # 다이어그램
├── validate_plugins.py
└── CONTRIBUTING.md
```

### 스킬 해부학 — 각 스킬 안에는 뭐가 들어 있나

33개 스킬 모두 동일한 내부 구조를 따릅니다. 이것은 Skills 2.0 스펙 준수만이 아니라, **스킬 품질을 측정·테스트·개선하기 위해 설계된 콘텐츠 아키텍처**입니다.

```
discover/skills/opp-tree/           ← 예시: opp-tree 스킬
├── SKILL.md                      ← 핵심 파일
│                                    · frontmatter (name, description,
│                                      argument-hint, allowed-tools)
│                                    · Trigger Gate (Use/Route/Boundary)
│                                    · Failure Handling (실패 시 복구 로직)
│                                    · Quality Gate (출력 품질 기준)
├── context/
│   └── domain.md                 ← 도메인 전문지식
│                                    Claude가 기본적으로 모르는 에이전트
│                                    경제학, 산업 벤치마크 등을 주입합니다
├── examples/
│   ├── good-01.md                ← ✅ "좋은 결과는 이런 모습"
│                                    Claude 출력의 앵커 역할을 합니다
│   └── bad-01.md                 ← ❌ "이건 피해야 하는 패턴과 그 이유"
│                                    흔한 실패를 사전에 방지합니다
└── references/
    ├── test-cases.md             ← 엣지 케이스, 경계 조건, 평가 기준
    │                                eval 시스템(54개 어설션)을 구동합니다
    └── troubleshooting.md        ← 실전에서 자주 발생하는 실패 + 복구 패턴
```

**각 파일이 실제로 미치는 영향:**

| 구성 요소 | 왜 넣었는가 | 측정된 효과 |
|-----------|-----------|-----------|
| `SKILL.md`의 Trigger Gate | Use/Route/Boundary 3조건으로 33개 스킬의 충돌 방지 | 93.5% 트리거 정확도 |
| `context/domain.md` | Claude가 기본적으로 모르는 도메인 전문성 주입 | +12~46% 출력 품질 향상 |
| `examples/good-01.md` | "이 수준이 정답"이라는 구체적 앵커 제공 | Claude 생성 품질 안정화 |
| `examples/bad-01.md` | "이건 틀린 것"이라는 명시적 반면교사 | 흔한 실패 패턴 사전 차단 |
| `references/test-cases.md` | 엣지 케이스 + 어설션 정의 | eval 시스템 구동 (54개 어설션) |

이 패턴이 34개 스킬 전체에 일관되게 적용됩니다. 총 **200개 이상의 보조 파일**이 각 스킬을 측정 가능하고, 테스트 가능하고, 개선 가능하게 만듭니다.

</details>

<details>
<summary>📐 플러그인 라이프사이클 다이어그램</summary>
<p align="center">
  <img src="docs/images/plugin-lifecycle.svg" alt="에이전트 제품 라이프사이클" width="800"/>
</p>
</details>

---

## 기여하기

[CONTRIBUTING.md](CONTRIBUTING.md)를 참고하세요. 새로운 스킬 추가, 기존 스킬 개선, 한↔영 번역 모두 환영합니다.

---

## 저자

**Sanguine Kim** — PM 20년차, AI Agent Builder & Educator

AI Dubbing·AI Avatar 서비스 성장을 거쳐, Agentic AI 제품을 리딩해왔습니다. 현재는 AI 에이전트 시대의 PM 역할 변화에 대한 강의와 워크숍을 준비하고 있습니다. UX, 데이터 드리븐, 그로스마케팅을 중요하게 생각하며, AI 네이티브 사고를 기반으로 제품을 만듭니다.

📬 **교육·컨설팅·기업 워크숍 문의:** kimsanguine@gmail.com

이 프로젝트를 교육 자료나 사내 트레이닝에 활용하고 계시다면, 한 줄 메일 주시면 감사하겠습니다. 커스터마이징 컨설팅과 강의 협업도 환영합니다.

- 참고 자료: Teresa Torres (*Continuous Discovery Habits*), Anthropic ("Building Effective Agents"), Steve Yegge (Gas Town 병렬 에이전트 설계), 곽병혁 (MCP-Skills 계층), Michael Polanyi (*The Tacit Dimension*)

---

## 관련 프로젝트

| 레포 | 설명 | 링크 |
|------|------|------|
| **AI_PM** | PM을 위한 Claude Code 가이드 — "왜" 에이전트를 만들어야 하는지, "어떻게" Claude Code를 쓰는지 | [github.com/kimsanguine/AI_PM](https://github.com/kimsanguine/AI_PM) |
| **hplan** | 바로 설치해서 쓸 수 있는 에이전트 스킬셋 *(이 레포)* | [github.com/kimsanguine/hplan](https://github.com/kimsanguine/hplan) |

> **AI_PM**에서 사고방식을 배우고, **hplan**으로 바로 실행하세요.

---

## 라이선스

MIT — [LICENSE](LICENSE)
