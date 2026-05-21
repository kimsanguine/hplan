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
| **Python** | 3.9+ | `python3 --version`으로 확인 · Evidence Gate 스크립트 실행 필요 |
| **Git** | 2.x+ | pre-commit hook 사용 시 필요 (선택) |
| **OS** | macOS / Linux | Windows는 WSL2 권장 |

> **Python이 없다면?** Evidence Gate(`generate_report.py`, `gate_guard.py`)를 포함한 일부 스킬이 동작하지 않습니다. 나머지 스킬(SKILL.md 기반)은 Python 없이도 사용 가능합니다.

---

## 설치하기 (5분)

### 방법 1: 마켓플레이스 설치 (추천)

```bash
# 한 줄로 5개 플러그인 전부 설치
claude plugin marketplace add kimsanguine/hplan
```

### 방법 2: 개별 플러그인 설치

```bash
# 레포 클론 후 원하는 플러그인만 설치
git clone https://github.com/kimsanguine/hplan.git
cd hplan

claude plugin add hplan/     # 게이트 ⭐ (Should we build this?)
claude plugin add discover/  # 발견 (What to build?)
claude plugin add architect/ # 설계 (How to architect?)
claude plugin add deliver/   # 실행 (How to ship?)
claude plugin add operate/   # 측정·학습·운영 통합 (How to measure, learn & operate?)
```

만들지 말지부터 고민이라면 → `hplan`을 먼저 설치하세요 (evidence + COGS 게이트).
어떤 에이전트를 만들지 아직 모르겠다면 → `discover`을 설치하세요.
이미 뭘 만들지 정했다면 → `deliver`부터 시작하세요.

### 방법 3: 개별 스킬 복사 (플러그인 없이)

```bash
# 원하는 스킬만 복사
cp -r discover/skills/cost-sim/ ~/.claude/skills/
cp -r architect/skills/3-tier/ ~/.claude/skills/
```

### 다른 도구에서도 사용 가능

| 도구 | 스킬 (SKILL.md) | 커맨드 체이닝 |
|-----|:---:|:---:|
| Claude Code | ✅ | ✅ |
| Gemini CLI | ✅ | ⚠️ 수동 |
| Cursor | ✅ | ⚠️ 수동 |
| Codex CLI | ✅ | ⚠️ 수동 |
| Kiro | ✅ | ⚠️ 수동 |

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
| 딜리버리 | **deliver** | "어떻게 명세하고 만들까?" | PRD 작성, 인스트럭션 설계, OKR 설정, 4엔진 PPTX 라우터, 빌드 하네스 |
| 운영 | **operate** | "측정·학습·운영을 어떻게 할까?" | KPI 모니터링, 비용 추적, PM 암묵지 자산화, 포트폴리오 운영 |

---

## 시나리오별 따라하기

### 시나리오 1: "고객 문의 자동 응답 에이전트를 만들고 싶어"

이런 생각이 들었다면, 아래 순서로 진행하세요.

**Step 1 — 기회 탐색** (discover)

```
/discover 고객 상담 업무
```

이 커맨드는 내부적으로 `opp-tree` 스킬을 불러서, 어떤 상담 유형이 자동화에 적합한지 기회 트리를 만들어줍니다.

**Step 2 — 가정 검증** (discover)

```
/validate 고객 상담 챗봇 에이전트
```

에이전트를 만들기 전에 검증해야 할 가정 4축(Value, Feasibility, Reliability, Ethics)을 체크합니다. "이 에이전트가 정말 가치가 있는가? 기술적으로 가능한가? 신뢰성은? 윤리 이슈는?"

**Step 3 — 비용 시뮬레이션** (discover)

```
고객 상담 챗봇의 토큰 비용을 시뮬레이션해줘.
하루 200건 상담, 평균 대화 5턴, GPT-4o와 Claude Sonnet 비교.
```

`cost-sim` 스킬이 자동으로 불립니다. 월간 비용, 유저 스케일링 시나리오(1→10→100배), 최적화 전략까지 나옵니다.

**Step 4 — 아키텍처 설계** (architect)

```
/architecture 고객 상담 챗봇 - 다국어 지원, FAQ 자동응답, 에스컬레이션 포함
```

단일 에이전트로 충분한지, 멀티에이전트(3-tier)가 필요한지 판단하고 구조를 설계합니다.

**Step 5 — PRD 작성** (deliver)

```
/write-prd 고객 상담 자동응답 에이전트
```

에이전트 전용 PRD가 생성됩니다. 일반 PRD와 다른 점은 Instruction, Tools, Memory, Triggers, Failure Handling, Output Format, Guard Rails 섹션이 포함된다는 것입니다.

**Step 6 — 건강 점검 설정** (operate)

```
/health-check 고객 상담 에이전트
```

운영 중인 에이전트의 KPI, 실패율, 비용 추이를 모니터링할 대시보드 기준을 잡아줍니다.

---

### 시나리오 2: "이미 에이전트가 있는데 비용이 너무 많이 나와"

```
/cost-review 문서 요약 에이전트
```

이 커맨드는 `burn-rate` 스킬을 사용해서 현재 토큰 비용을 분석하고, 모델 다운그레이드, 캐싱, 배치 처리 등 최적화 방안을 제시합니다.

---

### 시나리오 3: "프로젝트에서 배운 교훈을 다음 에이전트에 반영하고 싶어"

이게 `operate` 플러그인의 핵심 용도입니다.

**Step 1 — 경험 추출**

```
/extract 지난 3개월 고객 상담 에이전트 운영하면서 배운 것들:
- 고객이 "긴급"이라고 하면 80%는 진짜 긴급이 아니었다
- 같은 질문이 3번 반복되면 자동화 대상이다
- 에이전트가 "모르겠다"고 답하는 게 틀린 답보다 낫다
```

`pm-framework` 스킬이 이 경험들을 **TK 유닛**(Tacit Knowledge unit)으로 구조화합니다.

```
TK-041: 긴급 트리거 검증 규칙
  패턴: 고객이 "긴급"을 언급할 때 실제 긴급률은 20% 이하
  활성 조건: 에이전트가 우선순위를 결정할 때
  의사결정: 긴급 키워드만으로 에스컬레이션하지 말 것. 실제 영향 범위 확인 후 판단.
```

**Step 2 — 에이전트 인스트럭션으로 변환**

```
/tk-to-instruction TK-041
```

TK 유닛을 에이전트가 바로 사용할 수 있는 인스트럭션 형식으로 변환합니다.

---

### 시나리오 4: "경쟁사가 비슷한 에이전트를 만들었는데 우리 차별점이 뭐지?"

```
에이전트 경쟁 우위를 분석해줘.
우리: 다국어 고객 상담 에이전트, 6개월 운영 경험, TK 유닛 40개 축적
경쟁사: 영어 단일 언어, 최근 출시, 범용 LLM 기반
```

`moat` 스킬이 자동으로 불립니다. 데이터 해자, 프로세스 해자, 네트워크 해자 관점에서 분석합니다.

---

## 스킬 전체 목록 (65개)

### hplan — 게이트 ⭐ (8개 스킬)

빌드 결정 *전에* 돌리는 evidence + COGS + decision 게이트. LLM 추정이 아닌 결정론적 Python 측정과 영구 메모리(JSONL)가 핵심.

| 스킬 | 기능 |
|------|------|
| `evidence-rubric` | 8축 100점 evidence 루브릭으로 아이디어 점수화 |
| `interview-synthesis` | AI 합성 결과 import → 인간 strength 태깅 강제 → 5/3 strong-Push 패턴 audit |
| `exclusions` | Append-only Do-Not-Build 영구 메모리, 한국어 fuzzy match로 collision 자동 감지 |
| `cogs-sentinel` | lognormal sampler가 p50/p90 월간 마진 계산 + free-user abuse blend |
| `ost` | Teresa Torres 식 Opportunity Solution Tree를 Mermaid + `docs/OPPORTUNITY_TREE.md`로 생성 |
| `decision-log` | build/interview/pivot/hold 결정 append-only 로그 + 3-6개월 self-eval audit |
| `handoff` | Build Gate brief → Spec-Kit / Kiro / GStack / Claude Code 4개 ecosystem 동시 export |
| `pmf-gate` | Post-launch PMF 신호 루프 — COGS 실시간 + 행동 지표 → 다음 Evidence Gate 입력 |

### discover — 발견 (7개 스킬)

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `opp-tree` | 에이전트 기회 트리 작성 | "뭘 자동화하면 좋을까?" |
| `assumptions` | 4축 가정 검증 (가치/실현성/신뢰성/윤리) | "이거 진짜 만들어도 되나?" |
| `build-or-buy` | 직접 구축 vs 외부 솔루션 판단 | "사서 쓸까 직접 만들까?" |
| `hitl` | Human-in-the-loop 범위 설정 | "어디까지 자동화하고 어디서 사람이 개입?" |
| `cost-sim` | 토큰 비용 시뮬레이션 | "한 달에 얼마 들어?" |
| `agent-gtm` | 에이전트 Go-to-Market 전략 | "출시를 어떻게 해야 하지?" |
| `design-reference` | UI/UX 레퍼런스 수집·구조화 + 공통 패턴 추출 | "경쟁사 레퍼런스에서 패턴을 뽑아 설계에 반영하고 싶어" |

### architect — 설계 (8개 스킬)

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `3-tier` | 3계층 멀티에이전트 설계 | "에이전트 여러 개를 어떻게 엮지?" |
| `orchestration` | 오케스트레이션 패턴 선택 | "Sequential? Parallel? Router?" |
| `biz-model` | 에이전트 수익 모델 설계 | "이걸로 어떻게 돈 벌지?" |
| `router` | 작업별 LLM 모델 라우팅 | "이 작업에 Haiku? Sonnet? Opus?" |
| `memory-arch` | 에이전트 메모리 설계 | "대화 기록을 어떻게 관리하지?" |
| `moat` | 경쟁 우위 분석 | "경쟁사가 따라오면 어쩌지?" |
| `growth-loop` | 데이터 플라이휠 설계 | "사용할수록 똑똑해지게 만들려면?" |
| `design-token` | 시맨틱 CSS 토큰 + DESIGN.md 자동 생성 | "디자인 시스템 토큰을 어떻게 정의하지?" |

### deliver — 딜리버리 (27개 스킬, 핵심 15개 표시 — 전체 목록은 [README-ko.md](README-ko.md) 참조)

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `claude-md` | CLAUDE.md 자동 생성 + hplan 추천 | "이 프로젝트에 hplan을 어떻게 깔지?" |
| `instruction` | 에이전트 인스트럭션 7요소 설계 | "에이전트한테 뭐라고 말해줘야 하지?" |
| `prd` ⭐ | 에이전트 전용 PRD + **mermaid 정합성 게이트** (workflow↔userflow↔requirements 결정론 검증) | "기획서를 쓰고 누락 없는지 자동 검증하고 싶어" |
| `prompt` | PM 관점 프롬프트 설계 (CRISP) | "프롬프트를 어떻게 잘 짜지?" |
| `ctx-budget` | 컨텍스트 윈도우 토큰 예산 | "128K 토큰을 어떻게 배분하지?" |
| `okr` | 에이전트 OKR 설정 | "성공 기준을 어떻게 잡지?" |
| `stakeholder-map` | 이해관계자 매핑 | "누가 찬성하고 누가 막지?" |
| `agent-plan-review` | 설계 구현 전 4축 검증 | "이 설계 괜찮은지 구현 전에 봐줘" |
| `gemini-image-flow` | AI 이미지 생성 파이프라인 | "이미지 생성 에이전트를 어떻게 만들지?" |
| `infographic-gif-creator` | 인포그래픽 GIF/MP4 생성 | "이 아키텍처를 애니메이션으로 만들어줘" |
| `pptx-ai-slide` ⭐ | **4엔진 라우터** (mckinsey/hifidelity/html-qa/video) — 입력에 맞는 엔진 자동 선택 | "투자자용 피치 5장 / 강의자료 40장 / 영상→슬라이드 다 다른 도구로 해줘" |
| `agent-demo-video` | Remotion 기반 데모 영상 | "이해관계자용 데모 영상 만들어줘" |
| `harness-design` ⭐ NEW | 빌드 하네스 (4명+ 팀 + Ralph Loop + 백업/dry-run) | "자율 모드로 큰 작업 진행하고 싶어" |
| `parallel-team` ⭐ NEW | 독립 태스크 ≥2 → worktree 격리 병렬 디스패치 | "여러 모듈 동시에 작업해도 충돌 안 나게" |
| `build-loop` ⭐ NEW | `/build` 한 번으로 발견→리서치→설계→PRD→분해→구현 | "아이디어부터 구현까지 한 루프로" |

### operate — 측정·학습·운영 (15개 스킬)

v0.9에서 `measure`(측정) + `learn`(학습) + 기존 `operate`(포트폴리오 운영)가 하나로 통합되었습니다.

**측정 (ex-measure)**

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `kpi` | 운영 + 비즈니스 KPI 설계 | "어떤 지표를 봐야 하지?" |
| `reliability` | 신뢰성 체계 점검 | "에이전트가 엉뚱한 답을 하면?" |
| `premortem` | 사전 실패 모드 분석 (FMEA) | "출시 전에 뭐가 터질 수 있지?" |
| `burn-rate` | 토큰 비용 추적/최적화 | "비용이 왜 이렇게 늘었지?" |
| `north-star` | North Star Metric 정의 | "이 에이전트의 궁극적 성공 지표는?" |
| `agent-ab-test` | A/B 테스트 설계/분석 | "프롬프트 변경 효과가 진짜야?" |
| `cohort` | 코호트 분석 | "버전별 성능이 어떻게 변하지?" |
| `incident` | 장애 대응 프로토콜 | "에이전트가 터졌는데 어떻게 하지?" |

**학습 (ex-learn)**

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `pm-framework` | PM 암묵지 → TK 유닛 구조화 | "내 경험을 체계적으로 정리하고 싶어" |
| `pm-decision` | 6가지 의사결정 패턴 적용 | "이 상황에서 어떻게 판단하지?" |
| `pm-engine` | PM-ENGINE-MEMORY 인터페이스 | "축적된 TK를 에이전트에 주입하고 싶어" |

**포트폴리오 운영**

| 스킬 | 하는 일 | 이럴 때 쓰세요 |
|------|--------|-------------|
| `agent-portfolio` | T1~T5 티어링 + 운영 주의력 분배 | "운영 중 에이전트가 5개 넘었는데 어디부터 손볼지" |
| `scorecard-5axis` | Accuracy/Reliability/Cost/Velocity/Satisfaction 5축 가중 단일 점수 | "에이전트 N개를 헤드 투 헤드로 비교하고 싶어" |
| `weekly-rollup` | 주차별 평균·Δ·Top 이동자·이상치 자동 요약 | "금요일 운영 회의 직전 5분 브리프" |
| `cross-team-routing` | capability + 부하 + 티어 + handoff 점수 기반 라우팅 결정 | "이 요청을 어느 팀 에이전트가 받을지" |

---

## 커맨드 전체 목록 (19개)

커맨드는 여러 스킬을 체이닝해서 한 번에 실행하는 워크플로우입니다.

| 커맨드 | 플러그인 | 하는 일 |
|--------|---------|--------|
| `/hplan-evidence` | hplan | Evidence Gate — exclusions check + 100점 루브릭 + 인터뷰 audit |
| `/hplan-product` | hplan | Product Gate — OST + 사용자 여정 + 사이트맵 + 디자인 포인터 |
| `/hplan-build` | hplan | Build Gate — COGS sentinel + decision log + checkpoint approval |
| `/hplan-cogs` | hplan | COGS sentinel만 빠르게 — p50/p90 마진 + free-abuse 시뮬레이션 |
| `/hplan-exclude` | hplan | "Do Not Build" 영구 메모리 add/check/list |
| `/hplan-handoff` | hplan | Build Gate brief → Spec-Kit / Kiro / GStack / Claude Code export |
| `/hplan-doctor` | hplan | 설치 진단 — 훅 등록·실행·체크포인트·레지스트리·git 훅 5-check |
| `/discover` | discover | 자동화 기회 탐색 + 기회 트리 생성 |
| `/validate` | discover | 에이전트 가정 4축 검증 |
| `/architecture` | architect | 에이전트 아키텍처 설계 |
| `/strategy-review` | architect | 전략 리뷰 (수익 모델 + 경쟁 우위) |
| `/write-prd` | deliver | 에이전트 전용 PRD 작성 |
| `/set-okr` | deliver | 에이전트 OKR 설정 |
| `/sprint` | deliver | 프로토타입 스프린트 계획 |
| `/health-check` | operate | 주간 건강 점검 (KPI + 비용 + 실패율) |
| `/cost-review` | operate | 비용 심층 분석 + 최적화 제안 |
| `/extract` | operate | 경험에서 TK 유닛 추출 |
| `/decide` | operate | 의사결정 프레임워크 적용 |
| `/tk-to-instruction` | operate | TK → 에이전트 인스트럭션 변환 |

---

## 자주 묻는 질문

**Q: Claude Code가 없으면 못 쓰나요?**
A: 스킬 파일(SKILL.md)은 표준 마크다운이라 Gemini CLI, Cursor, Codex CLI 등 마크다운 스킬을 지원하는 도구에서 사용할 수 있습니다. 커맨드 체이닝은 Claude Code에서 가장 잘 동작합니다.

**Q: 기존 PM 스킬이랑 충돌하나요?**
A: 아닙니다. 기존 PM 스킬은 일반 PM 업무(로드맵, 스테이크홀더 커뮤니케이션 등)를 다루고, 이 스킬셋은 에이전트 구축/운영을 다룹니다. 둘 다 설치해서 쓰세요.

**Q: 영어로만 써야 하나요?**
A: 커맨드와 프롬프트 모두 한국어로 입력하면 됩니다. 스킬 내부의 개념 설명은 한국어, 인스트럭션은 영어로 작성되어 있어 LLM 실행 품질과 사용자 이해도를 동시에 잡았습니다.

**Q: TK-NNN이 뭔가요? 꼭 써야 하나요?**
A: TK = Tacit Knowledge(암묵지), NNN = Never-ending Nuance Network(끝없이 쌓이는 뉘앙스의 네트워크). TK-001부터 TK-999까지 PM의 판단 기준을 축적합니다. 예: "고객이 긴급이라고 하면 80%는 가짜 긴급이다." 이걸 구조화해서 에이전트 인스트럭션에 넣으면, 당신의 경험이 에이전트의 판단 기준이 됩니다. 매일 1개씩 약 3년이면 999개 — 에이전트가 PM의 분신이 되는 시점입니다. `operate` 플러그인의 pm-framework/pm-decision/pm-engine 스킬이 이를 담당합니다. 선택사항이지만, 쓰면 쓸수록 에이전트가 강해집니다.

**Q: 에이전트를 만들어본 적이 없어도 되나요?**
A: 네. discover 플러그인의 `/discover`부터 시작하면 "어떤 업무를 자동화할 수 있는지"부터 탐색합니다. 기술적 배경 없이 PM 관점에서 접근할 수 있도록 설계되었습니다.

---

## 추천 시작 경로

### PM이라면

```
/discover → /validate → cost-sim → /architecture → /write-prd → /set-okr
```

### 마케터라면

```
/discover [마케팅 자동화 업무] → cost-sim → /write-prd → /health-check
```

### 이미 에이전트를 운영 중이라면

```
/health-check → /cost-review → /extract [운영 교훈] → /tk-to-instruction
```

---

## 벤치마크 요약

이 스킬셋이 실제로 효과가 있는지 10개 테스트(54개 검증 항목)로 측정했습니다.

| | 스킬 사용 | 스킬 미사용 | 차이 |
|---|---------|----------|-----|
| **검증 통과율** | **100%** | 88% | **+12%** |
| **평균 실행 시간** | 62초 | 42초 | +20초 |

특히 `pm-framework`(TK 유닛)과 `3-tier`(멀티에이전트 설계)는 스킬 없이는 Claude가 제대로 수행하지 못하는 **역량 게이팅(capability-gating)** 영역이었습니다.

> **참고:** 벤치마크는 v0.4 (32개 스킬) 기준 측정값입니다. v0.9.1 (65개 스킬, 5-plugin 구조) 기준 재측정은 차기 iteration에서 진행 예정입니다.

---

## 라이선스

MIT — 자유롭게 사용, 수정, 배포할 수 있습니다.
