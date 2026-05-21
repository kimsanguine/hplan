# hplan — The Product Build Gate for AI Agents

> **The 30-minute check that stops you from spending 6 months building the wrong AI product.**

> 🐎 **What `hplan` means — Harness Planning.**
> Like a horse's harness, hplan gives direction to the raw power of AI coding tools (Claude Code, Cursor, Lovable, etc.). The tools that *make* code are already strong enough. What's missing is *where to point them*. hplan is the 7-day discipline that forces you to answer market research, problem definition, and COGS *before* a single PRD line is written.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](LICENSE)
[![Skills](https://img.shields.io/badge/skills-65-blue?style=flat-square)](#plugins--full-skill-list)
[![Plugins](https://img.shields.io/badge/plugins-5-purple?style=flat-square)](#the-agent-pm-journey--5-plugins)
[![Version](https://img.shields.io/badge/version-0.8.5-green?style=flat-square)](CHANGELOG.md)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)
[![한국어](https://img.shields.io/badge/lang-한국어-blue?style=flat-square)](README-ko.md)

> **v0.9.0** — hplan is the **Product Build Gate** that asks WHETHER before AI tools rush to HOW. v0.9 consolidates from 9 loose plugins into a clean **5-plugin lifecycle**: `hplan` (gate) → `discover` → `architect` → `deliver` → `operate`. Track + Craft are now absorbed into `deliver`; Measure + Learn are now absorbed into `operate`. v0.9 also adds a **3-skill design workflow**: `discover/design-reference` (100-site curated reference + DESIGN_BRIEF.md) → `architect/design-token` (semantic CSS tokens + DESIGN.md) → `deliver/mobile-check` (Playwright 375/768/1440px hard gate). See [CHANGELOG.md](CHANGELOG.md).

### 📺 99-second intro

https://github.com/kimsanguine/hplan/releases/download/v0.8.4-video-preview/v8-core-track-16x9.mp4

> _Core narrative + Track guardrail. Other variants (60s Editorial, 90s Demo, 84s Core-only) in [v0.8.4-video-preview release](https://github.com/kimsanguine/hplan/releases/tag/v0.8.4-video-preview)._

## The Problem hplan Solves

You have an AI product idea. Cursor can prototype it in a weekend. Spec-Kit can spec it in an hour. Claude Code can ship a first version overnight.

**But should you build it?**

Every AI tool today is great at making things *fast*. None of them ask whether the thing should exist at all. So PMs and founders end up:

- 🪦 Building products customers don't actually want (waitlists and "I would use this" aren't evidence)
- 💸 Promising "unlimited AI" pricing that quietly loses money at scale (Replit went from $2M ARR to single-digit margins this way)
- 🔁 Re-pitching the same idea their team killed 3 months ago — and nobody remembers why
- 📋 Confidently shipping clones of established incumbents without realizing the territory is taken
- 🤷 Making "build" or "hold" decisions and never finding out which ones were actually right

**hplan is the 30-minute proof that your next 6 months will work.** It's the discipline of saying "let me check first" — encoded as deterministic tools, not just good intentions.

## How hplan Shows Up in Your Day

This is what changes once hplan is installed. You keep talking to Claude the way you already do — hplan steps in at the moments you most often slip up:

| You say to Claude | What hplan does |
|---|---|
| **"Let's build an AI assistant for our customers"** | hplan pauses and asks for the evidence. *"Which users currently spend 30+ min/week on this? Show me 3 real customer quotes."* If you can't, it stops you before any PRD work. |
| **"We'll charge $19/month for this AI feature"** | hplan runs the COGS calculation with real provider pricing, your expected usage, and a free-tier abuse scenario. Returns *p50 margin: 78%, p90: 41%, with free abuse: −12%*. Tells you exactly what needs to change. |
| **"This is similar to the idea Alex pitched last quarter"** | hplan checks the decision log. *"Yes — that idea was held on 2026-02-03 because [reasons]. The condition to revisit was 'enterprise customers explicitly ask'. Is that condition met now?"* |
| **"It's an AI tool that helps marketers write copy"** | hplan checks the exclusions registry first. *"This overlaps with prior exclusion ex-2026-04-17: established incumbents already cover this. Reopen trigger was 'serve a vertical with regulatory copy requirements'. Do you?"* |
| **"Spec it out so we can start building"** | hplan blocks the write until all three gates are green. If Evidence Gate said "interview" and COGS said "RED", the spec file simply does not get created. Filesystem-level block, not a polite warning. |
| **"Were my product decisions actually right?"** | hplan audits the last 6–12 months automatically. *"You held 8 ideas. 6 turned out to be correctly killed (validated). 2 someone else shipped successfully — those are 'false holds'. Here's what those 2 had in common."* |

The pattern: **you don't have to remember to invoke hplan.** Once installed, it triggers when you say things like "let's build", "we'll charge", "ship it", "spec it out".

## Who This Is For

- **Solo founders** deciding what to spend the next 6 months building
- **Product managers** who keep getting asked "can we build this with AI?" and want a structured way to answer
- **Teams using Spec-Kit / Cursor / Kiro / Claude Code** who want a *pre-spec filter* — not a replacement
- **Anyone** who has shipped something that looked good on paper and died in production, and wants the next idea to go differently

## WHETHER — The Question Every Other Tool Skips

> **"AI 코딩 도구가 HOW를 잘하게 됐다면, hplan은 WHETHER를 다룬다. 둘은 같이 쓰는 것이 아니라 순서가 있다 — hplan이 먼저다."**
>
> *"If AI coding tools have mastered HOW, hplan handles WHETHER. They're not used together — there's an order. hplan goes first."*

**HOW** asks: *"In what way should we build this?"*
**WHETHER** asks: *"Should we build this at all — yes or no?"*

WHETHER is bigger than WHY. WHY answers the reason ("why would users pay?"). WHETHER is the binary verdict that *contains* WHY — every gate in hplan answers a WHY question, and together they produce the WHETHER:

| Gate | WHY it answers | WHETHER it produces |
|------|---------------|---------------------|
| Evidence Rubric | Why do users actually have this problem? | Do we have sufficient proof to proceed? |
| Exclusions Check | Why did we kill this idea before? | Is this iteration meaningfully different? |
| COGS Sentinel | Why would this pricing work at scale? | Can the economics support a real business? |
| **All 3 combined** | — | **GO / HOLD / INVESTIGATE** |

Other tools handle **HOW** (superpowers → how to work with Claude Code), **WHO** (gstack → who the agents are), **WHERE** (GSD → where in the workflow). hplan handles **WHETHER** — the decision that comes before all other decisions.

### hplan's 3 Principles vs Opposing Assumptions

| hplan 원칙 | 대립 가정 |
|-----------|---------|
| **대화↓ 고객문서↑** — 고객·시장·경쟁사에 대한 문서가 많을수록 LLM이 더 정확하게 돕는다 | LLM과 대화를 더 많이 할수록 결과가 개선된다 |
| **큰 작업은 단계별로** — 검증되지 않은 전제를 컨텍스트에 쌓지 않는다 | 한 번에 큰 컨텍스트를 주면 LLM이 더 잘 이해한다 |
| **검증 먼저·개발 나중** — 증거 없이 PRD를 쓰는 것은 기술적 부채의 시작이다 | 빠른 프로토타입을 만들어보면 검증된다 |

<p align="center">
  <img src="docs/images/demo-terminal.svg" alt="hplan demo — exclusion collision + RED COGS catch a bad idea before any PRD is written" width="800"/>
</p>

> 🆕 **New to Claude Code?** → [`deliver/claude-md`](deliver/skills/claude-md/SKILL.md) scans your project, auto-generates CLAUDE.md, and recommends the right hplan plugins. The fastest way to onboard.

## Under the Hood

For the technically curious, here's what makes hplan different from every other PM toolkit:

- 🧪 **Executable COGS sentinel** — p50 / p90 monthly margin is computed by a real Python sampler with provider pricing snapshots, not estimated by an LLM. Free-user abuse is modeled, not hand-waved.
- 📚 **Append-only exclusions registry** — every "Do Not Build" gets a JSONL entry with a `reopen_trigger`. New ideas auto-collision-check with Korean-aware fuzzy match.
- 📊 **Self-evaluating decision log** — every gate decision is logged with reasons; outcomes are back-filled later; an `audit` command surfaces hit rate, false holds, and missed builds. The only PM gate that measures its own accuracy.
- 🔌 **MCP server** — the same gate primitives are exposed as MCP tools, so Cursor / Windsurf / Kiro / Codex / Goose can call them, not just Claude Code.
- 🛑 **Claude Code PreToolUse hook** — blocks writes to `PRD.md` / `specs/*` / `.kiro/specs/*` until `harness/build-gate/checkpoint.json` shows `status: "approved"`. Gate enforcement at the filesystem level, not just in prompts.
- 🚚 **Multi-target handoff** — one brief JSON exports simultaneously to Spec-Kit `specs/NNN-slug/`, Kiro `.kiro/specs/`, GStack `/office-hours` brief, and Claude Code `AGENTS.md` + `CLAUDE.md`.

*Renamed from `AI_PM_Skills` in v0.5. v0.9 consolidates to a clean 5-plugin lifecycle: hplan (gate) → discover → architect → deliver → operate. Old URLs auto-redirect.*

---

## The Problem

In 2026, PMs are being asked to "build an agent" — but existing PM skills don't prepare you for that.

General PM skills teach you to **use AI as a tool** — write PRDs faster, generate OKRs, analyze competitors. But when you're **building agents as products**, the questions are fundamentally different:

- "What would it cost to run this agent at 1,000 users/day?"
- "How does an agent recover from hallucination?"
- "How do I orchestrate multiple agents together?"
- "How do I encode 3 months of operational judgment into the agent's instructions?"

This project turns those questions into **65 production-grade skills** across the full agent lifecycle.

---

## Quick Start (60 seconds)

```bash
# 1. Install the marketplace
/plugin marketplace add kimsanguine/hplan
/plugin install hplan@kimsanguine-hplan

# 2. Run all 3 gates in one command — exclusions + evidence + COGS → verdict
/hplan "AI marketing copy generator"
# → [exclusions] COLLISION with ex-2026-04-17 (established incumbents)
# → reopen_trigger UNMET → HOLD

# Or run individual gates for deeper analysis:
/hplan-evidence "AI marketing copy generator"   # full 100-point evidence rubric
/hplan-cogs --provider anthropic --model claude-sonnet-4-6 \
            --tokens-in 3000 --calls 40 --arpu 29
# → p50 margin 95%, p90 90%, blended 49% → GREEN
```

**Already past the gate?** Install by lifecycle stage:

```bash
/plugin install discover@kimsanguine-hplan   # Discover — opportunity trees, assumptions, cost sim, design-reference
/plugin install architect@kimsanguine-hplan  # Architect — orchestration, memory, moat, design-token
/plugin install deliver@kimsanguine-hplan    # Deliver — PRD, instructions, build tracking, UI/UX enforcement
/plugin install operate@kimsanguine-hplan    # Operate — KPI, reliability, portfolio, PM knowledge capture
```

---

## The Agent PM Journey — 5 Plugins

This isn't a random collection of skills. It's a **complete lifecycle** — the same path every agent PM walks. `hplan` is the gate that decides whether the thing should be built at all. Then four plugins cover the full journey from discovery to operation.

```
   Gate  →  Discover  →  Architect  →  Deliver  →  Operate
   hplan    discover      architect     deliver      operate
   8 skills  7 skills     8 skills     27 skills    15 skills

     ↑                                                   │
     └──── Operational insights feed back into gate ─────┘
```

| Plugin | The Question | Key Skills |
|--------|-------------|------------|
| **Gate** ⭐ `hplan` | "Should we build this at all?" | evidence-rubric · interview-synthesis · exclusions · cogs-sentinel · ost · decision-log · handoff · pmf-gate |
| **Discover** `discover` | "What agent should we build?" | opp-tree · assumptions · build-or-buy · cost-sim · hitl · agent-gtm · **design-reference** |
| **Architect** `architect` | "How should we structure it?" | 3-tier · orchestration · router · memory-arch · moat · growth-loop · biz-model · **design-token** |
| **Deliver** `deliver` | "How to spec, build, and ship it?" | PRD · instruction · prompt · harness · tracking (velocity/estimate/gate-checkpoint) · UI enforcement (mobile-check/hierarchy-rules/respect-brief) + 16 more |
| **Operate** `operate` | "How to run and improve agents over time?" | portfolio · scorecard · kpi · reliability · burn-rate · pm-engine · pm-framework + 8 more |

### What makes hplan different from the other 4

Other plugins are **prompt-driven thinking** — LLM ponders, you decide.
`hplan` adds **deterministic measurement** — Python scripts calculate p50/p90 COGS margins, append-only registries persist exclusions and decisions across runs, an MCP server lets Cursor/Windsurf/Kiro/Codex call hplan primitives, and a PreToolUse hook blocks PRD/spec writes until the human approves the gate. It is paired with discover/architect/deliver/operate, not a replacement.

Each skill **auto-loads from natural language** — describe your task and the right skill fires. Skills also **route across plugins**: burn-rate (operate) detects a cost spike → suggests router (architect) for model change → triggers cost-sim (discover) for re-simulation.

---

## Why This Is Different — 6 Things No Other Skillset Does

### ① Complete Agent Lifecycle, Not Random Tools

65 skills across 5 plugins cover the full agent product lifecycle (Gate → Discover → Architect → Deliver → Operate). This isn't "AI tools for PMs" — it's **a structured methodology for building agents as products**, from discovery to production operations.

### ② Two-Layer Architecture — Platform and Content Separation

We separate **how Claude finds skills** (Platform Layer — Skills 2.0 spec) from **what goes inside each skill** (Content Layer). The Content Layer defines the Trigger Gate (Use/Route/Boundary) pattern that prevents skill collisions, plus domain-specific context in each skill's `context/domain.md`. Result: **97.9% trigger accuracy** measured on v0.6 baseline (124 queries); v0.8 expands to 168 total queries (+44 for new 11 skills, re-measurement after API quota reset).

```
┌─ Platform Layer ──── Skills 2.0 Spec ──────────────────────┐
│  frontmatter · auto-invocation · subagent · hooks · evals   │
├─ Content Layer ──── hplan Pattern ──────────────────┤
│  Core Goal → Trigger Gate → Failure Handling                │
│  → Quality Gate → Examples · context/domain.md              │
└─────────────────────────────────────────────────────────────┘
```

### ③ Data Flywheel — PM Tacit Knowledge That Accumulates

learn is the moat. It structures your operational judgment into **TK (Tacit Knowledge) units**, then injects them into agent instructions. The more you use it, the smarter your agents get — and that knowledge **stays yours**.

```
PM judgment notes → /extract → TK-NNN structured units → PM-ENGINE-MEMORY.md
  → /tk-to-instruction → agent system prompt updated → repeat
```

This creates **switching cost**: competitors can copy the framework, but they can't copy your accumulated TK.

### ④ Eval-Driven ROI — Proof, Not Promises

Every skill is measured. 10 quality tests with 54 assertions prove what skills add vs base Claude. Result:

| | With Skill | Without Skill | Delta |
|---|-----------|--------------|-------|
| **Pass Rate** | **100%** | 88% | **+12%** |

`pm-framework` without skill drops to 40%. `cost-sim` with skill adds +46.6% output. This is **data-driven proof** that the skills work.

### ⑤ Good/Bad Examples for Data-Driven Improvement

Every skill includes `examples/good-01.md` and `examples/bad-01.md` — concrete right/wrong output pairs. Plus `references/test-cases.md` with edge case tables. These aren't decorative; they're **training signals** that make skill quality measurable and continuously improvable.

### ⑥ Skills 2.0 Full Spec + Instant Onboarding

Built on Claude Code's latest platform spec: auto-invocation, `context: fork`, `allowed-tools`, `model` field, dynamic `!command` injection, marketplace, and eval system. New users start with the [PM-ENGINE-MEMORY Starter Kit](learn/skills/pm-engine/examples/PM-ENGINE-MEMORY-STARTER.md) — 5 seed TK entries so the value is **immediate**, not "someday when I accumulate enough data."

### ⑦ Three Engineering Layers — The Stack Most AI Toolkits Miss

Most "AI for PMs" tools operate at a single layer: Prompt Engineering — better templates, faster output. hplan is built across three layers that must work together:

| Layer | What it does | hplan tools |
|-------|-------------|-------------|
| **Prompt Engineering** | Structured prompts that extract real signal — not opinion or LLM speculation | evidence-rubric · interview-synthesis · OST · cogs-sentinel |
| **Context Engineering** | *Garbage in, garbage out.* Customer documents, market data, and competitive context enter the system *before* any PRD — not inferred afterward. The exclusions registry and decision-log are institutional memory as permanent, structured context. | exclusions · decision-log · interview-synthesis |
| **Harness Engineering** | Deterministic guardrails enforced at the system level: Python scripts, append-only JSONL registries, a PreToolUse hook that blocks PRD writes at the filesystem. The discipline exists even when you'd rather skip it. | gate_guard.py · cogs_sentinel.py · exclusions_registry.py · MCP server |

> *Prompt Engineering improves HOW you ask. Context Engineering determines WHAT goes in. Harness Engineering enforces WHETHER you proceed.*

A perfect prompt with bad customer data produces confidently wrong conclusions. An excellent evidence rubric means nothing if a developer can bypass it and write the PRD anyway. All three layers are required — and in that order.

---

## Plugins — Full Skill List

<details>
<summary><strong>1. hplan ⭐</strong> — Should we build this at all? <code>(7 skills, 6 commands)</code></summary>

The gate that runs *before* discovery. Deterministic measurement (Python scripts, not LLM estimates), append-only memory (exclusions + decisions across runs), and a hook that blocks PRD/spec writes until a human approves.

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `evidence-rubric` | Score idea against 100-point evidence rubric — ICP, recent painful event, workaround, repetition, economic pain, switching trigger, MVP narrowness, acquisition path | "Should we even start interviews on this idea?" |
| `interview-synthesis` | Import AI synthesis output (BuildBetter / Perspective / similar tools), force human strength + Push/Pull/Habit/Anxiety axes tagging, audit 5-of-3 strong-Push rule | "We have 5 customer call transcripts — is the pattern strong enough?" |
| `exclusions` | Append-only Do-Not-Build registry with reopen_trigger and Korean-aware fuzzy-match collision detection | "Same idea as last quarter? Was it killed?" |
| `cogs-sentinel` | Executable COGS gate — p50/p90 monthly margin via lognormal sampler, free-user abuse blend, GREEN/CONDITIONAL_GO/RED decision | "Will $19/mo actually make money at p90?" |
| `ost` | Generate Teresa Torres-style Opportunity Solution Tree as `docs/OPPORTUNITY_TREE.md` with Mermaid diagram | "Lock the opportunity → solution → experiment tree before any PRD" |
| `decision-log` | Append-only build/interview/pivot/hold log + 3–6 month self-eval audit (hit_rate, false_holds, missed_builds) | "Were my product decisions 6 months ago actually right?" |
| `handoff` | Multi-target Build Gate brief → Spec-Kit / Kiro / GStack / Claude Code in one command | "Ready to start building — export the spec to my coding agent" |

**Commands:** `/hplan` ⭐ · `/hplan-evidence` · `/hplan-product` · `/hplan-build` · `/hplan-cogs` · `/hplan-exclude` · `/hplan-handoff`

**Cross-cutting assets:** MCP server (`hplan_mcp/`) for Cursor / Windsurf / Kiro / Codex / Goose · PreToolUse hook (`hooks/gate_guard.py`) · 4 role-locked reviewer agents (`agents/`)
</details>

<details>
<summary><strong>2. discover</strong> — What agent to build? <code>(7 skills, 2 commands)</code></summary>

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `opp-tree` | Build an opportunity tree scored by repeat frequency, automation fit, and judgment dependency | "We have 10 automation candidates — which one first?" |
| `assumptions` | Extract riskiest assumptions across 4 axes (Value/Feasibility/Reliability/Ethics) and design 2-day validation experiments | "What's the biggest risk before we start building?" |
| `build-or-buy` | Score Build vs Buy vs No-code across 6 axes (differentiation, speed, cost, customization, maintenance, domain) | "Should we use Intercom's bot or build our own agent?" |
| `hitl` | Set automation levels (1-5) and escalation triggers via reversibility × error-impact matrix | "Can the agent decide refunds, or must a human approve?" |
| `cost-sim` | Simulate monthly costs at 1→10→100→1,000 users by model pricing × call patterns | "Sonnet at 500 calls/day — what's the monthly bill?" |
| `agent-gtm` | Score beachhead segments (5 criteria) + design Shadow→Co-pilot→Auto→Delegation trust sequence | "How do we roll this agent out to B2B customers?" |
| `design-reference` ⭐ v0.8.5 NEW | Filter 100 curated KR/global reference sites (12 categories) → select 5-7 → generate DESIGN_BRIEF.md | "타겟 확정 후 UI 방향성 결정 — 핀테크? 푸드딜리버리? 레퍼런스 먼저" |

**Commands:** `/discover` · `/validate`
</details>

<details>
<summary><strong>3. architect</strong> — How to architect it? <code>(8 skills, 2 commands)</code></summary>

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `3-tier` | Design Prometheus (strategy) → Atlas (coordination) → Worker (execution) roles, comms, and delegation | "I need 5 agents — who controls whom?" |
| `orchestration` | Compare Sequential/Parallel/Router/Hierarchical patterns by latency, error rate, and cost | "Should my doc pipeline run serial or parallel?" |
| `biz-model` | Design per-use / subscription / outcome-based pricing + variable cost analysis targeting >70% margin | "Per-API-call billing or monthly flat fee?" |
| `router` | Auto-route tasks to T1-T4 models by complexity + fallback chains for 40-80% cost reduction | "Simple FAQ → Haiku, complex analysis → Opus — auto?" |
| `memory-arch` | Design Working/Episodic/Semantic/Procedural memory layers + token-budget-aware retrieval | "How does today's session recall yesterday's context?" |
| `moat` | Diagnose 6 moat types: data flywheel, workflow lock-in, network effects, switching costs, specialization, brand | "A competitor ships a GPT clone — what's our defense?" |
| `growth-loop` | Design usage→data→improvement→re-use loops + cold-start solutions + anti-loop identification | "How do we make recommendations improve with every use?" |
| `design-token` ⭐ v0.8.5 NEW | Read DESIGN_BRIEF.md → generate semantic CSS tokens (tokens.md) + DESIGN.md with breakpoint spec | "BRIEF 기반 --color-brand-primary 등 의미 토큰 생성 — craft/mobile-check 입력" |

**Commands:** `/architecture` · `/strategy-review`
</details>

<details>
<summary><strong>4. deliver</strong> — How to spec, build, and ship it? <code>(27 skills, 8 commands)</code></summary>

> **Onboarding (1):** claude-md
> **Core Spec (7):** instruction · prd · prompt · ctx-budget · okr · stakeholder-map · agent-plan-review
> **Communication (4):** gemini-image-flow · infographic-gif-creator · pptx-ai-slide · agent-demo-video
> **Build Tracking (7):** velocity-baseline · estimate-tasks · progress-probe · blocker-detect · progress-report · gate-checkpoint · respect-checkpoint
> **UI/UX Enforcement (5):** respect-brief · hierarchy-rules · motion-language · ui-drift-detect · mobile-check
> **Scaffolding (3):** harness-design · parallel-team · build-loop

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `claude-md` ⭐ | Scan project structure → auto-generate CLAUDE.md → recommend matching hplan plugins | "New project — set up Claude Code context" |
| `instruction` | Define Role/Context/Goal/Tools/Memory/Output/Failure with least-privilege tool access | "What goes in (and out of) the system prompt?" |
| `prd` | **Unified 14-section PRD** — People/Problem/Decisions + Agent/Execution Spec + Metrics/Hypotheses/Failure | "1인 변호사 한국 판례 RAG PRD 작성해줘" |
| `prompt` | CRISP framework + Why-First principle + 7 failure pattern avoidance | "Longer prompts make my agent behave worse" |
| `ctx-budget` | Estimate per-file token usage → classify Essential/Conditional/Excluded → 70% threshold alerts | "How do I fit 5 RAG docs + chat history into 128K?" |
| `okr` | Dual-axis OKRs: Business Impact + Operational Health with mandatory cost KR | "Is 95% accuracy enough, or do I need cost metrics too?" |
| `stakeholder-map` | Power-Interest matrix + blocker response strategies + internal champion cultivation | "Legal is blocking the agent rollout" |
| `agent-plan-review` | 4-axis review + failure mode matrix (5+ types) + Mermaid output | "Find the holes in this design before we start coding" |
| `gemini-image-flow` | End-to-end Gemini API image pipeline with model tier selection | "Build a sketch→code pipeline" |
| `infographic-gif-creator` | Convert architecture / workflow into HTML/CSS → GIF/MP4 animations | "Show the multi-agent flow to execs" |
| `pptx-ai-slide` | Story-driven slide decks (pitch / review / investor variants) | "Board presentation — 10 slides max" |
| `agent-demo-video` | Screen recordings + animations + narration via Remotion | "Show non-technical stakeholders what the agent does" |
| `velocity-baseline` | Extract personal velocity from prior projects (git log → complexity × percentile lookup) | "Before estimating, learn how fast I actually code" |
| `estimate-tasks` | WBS decomposition + complexity classification → loc/tokens/minutes prediction (deterministic) | "Lock predicted scope before starting" |
| `progress-probe` | PostToolUse Hook → append every tool call to `.track/actual_log.jsonl` | "Telemetry on every prompt cycle" |
| `blocker-detect` | 50+ deterministic regex/counter signals (self-doubt, retry loops, test failures, stalls) | "Auto-detect when I'm stuck — no LLM, just patterns" |
| `progress-report` | 7 event-driven triggers force a current-status report | "Status snapshot at phase transition / blocker threshold / context 70%" |
| `gate-checkpoint` | 6-phase transition gates (requirements → ship) with PreToolUse Hook blocking | "Can't write impl code until design phase passes" |
| `respect-checkpoint` | AI classifies screen_type × traffic → deterministic α/β/γ gate combination | "Ship-time user-respect gate enforcement" |
| `respect-brief` | Interview-driven RESPECT.md (5 sections) with forbidden words enforcement | "Before any UI code — capture user-respect intent as YAML constraints" |
| `hierarchy-rules` | Playwright + DOM saliency + WCAG AA (fold density / type hierarchy / 60-30-10 color) | "Measure what humans actually see — not what tokens promised" |
| `motion-language` | Regex + framer-motion AST scan → drift report against RESPECT spec | "Hover transitions all 200ms? Page easing consistent?" |
| `ui-drift-detect` | 5+ screen pHash + KMeans palette + DOM tree edit distance → 5-dimension drift score | "Design system regression — new screen broke the language?" |
| `mobile-check` | Playwright 375/768/1440px hard gate — no horizontal scroll, 44px touch targets, 14px+ fonts | "DESIGN.md 기준 3뷰포트 통과 전까지 빌드 완료 선언 금지" |
| `harness-design` | Design the build harness structure (decisions, evidence, gates) | "Set up the harness before coding starts" |
| `parallel-team` | Spawn + coordinate parallel worktree agents | "Dispatch 3 agents on independent tasks simultaneously" |
| `build-loop` | Autonomous build-loop orchestration with checkpoint gates | "Run the full build loop unattended" |

**Commands:** `/write-prd` · `/set-okr` · `/sprint` · `/track-init` · `/track-status` · `/track-retro` · `/craft-init` · `/craft-lint`
</details>

<details>
<summary><strong>5. operate</strong> — How to run and improve agents over time? <code>(15 skills, 5 commands)</code></summary>

> **Portfolio (4):** agent-portfolio · scorecard-5axis · weekly-rollup · cross-team-routing
> **Measure (8):** kpi · reliability · premortem · burn-rate · north-star · agent-ab-test · cohort · incident
> **Learn (3):** pm-framework · pm-decision · pm-engine

| Skill | What it does | When to use |
|-------|-------------|-------------|
| `agent-portfolio` | T1~T5 tiering by Reach × Reliability × Strategic value | "I run 5+ agents — which one deserves next quarter's investment?" |
| `scorecard-5axis` | Weighted scoring across Accuracy / Reliability / Cost / Velocity / User Satisfaction | "Head-to-head agent comparison for weekly ops review" |
| `weekly-rollup` | Cron-driven portfolio rollup (trend + anomaly detection across all agents) | "Monday morning — what changed across my agent fleet?" |
| `cross-team-routing` | Score capability × load × tier × handoff cost to decide which agent serves a request | "3 different agents could handle this — which should take it?" |
| `kpi` | Define 5-7 operational + business metrics with leading/lagging split | "What goes on the agent dashboard?" |
| `reliability` | Quantify P95/P99 worst cases + design safeguards + set SLA tiers | "3 out of 100 responses hallucinate — acceptable?" |
| `premortem` | Score 10-15 failure modes by Severity × Likelihood × Detection Difficulty | "Give me a 'this must not break' list" |
| `burn-rate` | Visualize token costs by model/task + spike detection + budget caps | "Token costs jumped 40% — what caused it?" |
| `north-star` | Select one metric via 5 criteria + set anti-metrics | "Team doesn't know which KPI matters most" |
| `agent-ab-test` | Calculate MDE + concurrent experiments + control for LLM nondeterminism | "Prompt A vs B — real difference or noise?" |
| `cohort` | Track performance by deployment cohort (4-week minimum, n≥100) | "Did v2.1 actually improve over v2.0?" |
| `incident` | Detect silent failures + triage + contain blast radius + 5 Whys | "Agent silent for 30 min — no alerts fired" |
| `pm-framework` | Convert implicit judgment into TK-NNN units with activation/deactivation conditions + knowledge graph linking | "3 years of agent ops experience is stuck in my head" |
| `pm-decision` | Build a pattern library of recurring PM decisions with context, criteria, and known failures | "I've seen this situation before — why did I decide that way?" |
| `pm-engine` | Agents dynamically query TK knowledge graph at runtime + auto-extract 1 TK/day + auto-update instructions | "I want my agents to leverage my operational know-how automatically" |

**Commands:** `/health-check` · `/cost-review` · `/extract` · `/decide` · `/tk-to-instruction`

> Start with the [PM-ENGINE-MEMORY Starter Kit](operate/skills/pm-engine/examples/PM-ENGINE-MEMORY-STARTER.md) — 5 seed TK entries to get going immediately.
</details>

---

## Installation

### Option 1: GitHub Marketplace (Recommended)

```bash
/plugin marketplace add kimsanguine/hplan
/plugin install hplan@kimsanguine-hplan    # or discover · architect · deliver · operate
```

### Option 2: Clone Locally

```bash
git clone https://github.com/kimsanguine/hplan.git
claude --plugin-dir ./hplan/hplan   # pick what you need (hplan, discover, architect, deliver, operate)
```

**Not sure which AI product to commit to?** → Start with `hplan` — evidence gate first.
**First time with Claude Code?** → Run `deliver/claude-md` — it scans your project and recommends the right plugins.
**Already past the gate?** → Pick by lifecycle stage (discover → architect → deliver → operate).

### Other AI Tools

| Tool | Skills | Commands | How to use |
|------|:------:|:--------:|-----------|
| **Gemini CLI** | ✅ | ❌ | Copy to `.gemini/skills/` |
| **Cursor** | ✅ | ❌ | Copy to `.cursor/skills/` |
| **Codex CLI** | ✅ | ❌ | Copy to `.codex/skills/` |
| **Kiro** | ✅ | ❌ | Copy to `.kiro/skills/` |

---

<details>
<summary><strong>📐 Architecture Deep-Dive</strong> — Two Layers, Skills 2.0, Trigger Gate, Commands</summary>

### Auto-Invocation

You don't call skills by name. Describe your task in natural language, and Claude matches it against each SKILL.md's `description` field to auto-load the best fit. Trigger accuracy: **97.9%** measured on v0.6 baseline (124 queries); v0.8 expands to 168 total queries (+44 for new 11 skills, re-measurement after API quota reset).

### Cross-Plugin Routing

The Trigger Gate's "Route" field enables routing between plugins:

| From | Trigger Condition | Route To |
|------|------------------|----------|
| `opp-tree` | "Validate assumptions for top opportunity" | `assumptions` |
| `burn-rate` | "Need model routing change" | `router` |
| `prd` | "Need instruction design" | `instruction` |
| `pm-framework` | "Convert TK to agent instruction" | `pm-engine` |

### Command Chaining

| Command | Chained Skills | Plugin |
|---------|---------------|--------|
| `/hplan` ⭐ | exclusions → evidence-rubric → cogs-sentinel → verdict | hplan |
| `/discover` | opp-tree → assumptions → build-or-buy | discover |
| `/architecture` | orchestration → 3-tier → memory-arch | architect |
| `/write-prd` | prd → instruction → ctx-budget | deliver |
| `/health-check` | kpi → reliability → burn-rate | measure |
| `/tk-to-instruction` | pm-engine → instruction | learn+deliver |

### Skills 1.0 vs Skills 2.0

| Feature | 1.0 (2025) | 2.0 (2026) | hplan |
|---------|-----------|-----------|-------------|
| Auto-invocation | ❌ | ✅ | ✅ 97.9% |
| Subagent (`context: fork`) | ❌ | ✅ | ✅ 5 skills |
| Tool restriction | ❌ | ✅ | ✅ 3-tier |
| Marketplace + Evals | ❌ | ✅ | ✅ Full |
| Dynamic injection | ❌ | ✅ | ✅ 5 skills |
| Hooks | ❌ | ✅ | ⚠️ Spec-ready |

> ⚠️ `hooks` have a known issue ([#17688](https://github.com/anthropics/claude-code/issues/17688)). Fallback `validate_*.sh` scripts available in `references/`.

### File Structure

```
hplan/                # repo root
├── hplan/            # Gate ⭐ (7 skills, 6 commands) — Product Build Gate
├── discover/           # Discovery (7 skills, 2 commands)
├── architect/            # Architecture (8 skills, 2 commands)
├── deliver/            # Deliver (27 skills, 8 commands) — spec + track + UI enforcement
├── operate/            # Operate (15 skills, 5 commands) — measure + learn + portfolio
├── evals/            # Quality + trigger evals
├── docs/images/      # Diagrams
├── validate_plugins.py
└── CONTRIBUTING.md
```

### Skill Anatomy — What's Inside Each Skill

Every skill follows a consistent internal structure. This isn't just Skills 2.0 spec compliance — it's a **content architecture** designed for measurable quality and continuous improvement:

```
discover/skills/opp-tree/           ← example skill
├── SKILL.md                      ← Core: frontmatter (name, description,
│                                    argument-hint, allowed-tools) +
│                                    Trigger Gate (Use/Route/Boundary) +
│                                    Failure Handling + Quality Gate
├── context/
│   └── domain.md                 ← Domain knowledge injected at runtime
│                                    (e.g., agent economics, industry benchmarks)
├── examples/
│   ├── good-01.md                ← ✅ Reference output — "this is what great looks like"
│   └── bad-01.md                 ← ❌ Anti-pattern — "this is what to avoid and why"
└── references/
    ├── test-cases.md             ← Edge cases, boundary conditions, eval criteria
    └── troubleshooting.md        ← Common failures + recovery patterns
```

**Why this matters:**

| Component | Purpose | Impact |
|-----------|---------|--------|
| `SKILL.md` Trigger Gate | Use/Route/Boundary → prevents wrong skill from firing | 97.9% trigger accuracy |
| `context/domain.md` | Domain expertise Claude doesn't have natively | +12~46% output quality |
| `examples/good-01.md` | Concrete "gold standard" output | Anchors Claude's generation |
| `examples/bad-01.md` | Explicit anti-patterns with explanations | Prevents common failures |
| `references/test-cases.md` | Edge cases + assertions | Powers eval system (54 assertions) |

This pattern repeats across all 65 skills — **200+ supporting files** that make each skill measurable, testable, and improvable.

</details>

<details>
<summary>📐 Plugin Lifecycle Diagram</summary>
<p align="center">
  <img src="docs/images/plugin-lifecycle.svg" alt="Agent Product Lifecycle" width="800"/>
</p>
</details>

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines. New skills, improvements, and translations (EN↔KO) are all welcome.

---

## Author

**Sanguine Kim** — 20-year PM veteran, AI Agent Builder & Educator

Built and scaled AI Dubbing and AI Avatar products, then led Agentic AI product development. Currently exploring the path of AI Agent PM educator — helping PMs navigate the shift from "using AI" to "building agents as products."

📬 **For training, consulting, or workshop inquiries:** kimsanguine@gmail.com

If you're using this project for corporate training or educational content, I'd appreciate a quick note. Customized consulting and co-teaching are welcome.

- References: Teresa Torres (*Continuous Discovery Habits*), Anthropic ("Building Effective Agents"), Steve Yegge (Gas Town parallel agent design), Byeonghyeok Kwak (MCP-Skills hierarchy), Michael Polanyi (*The Tacit Dimension*)

---

## Related

| Repo | What | Link |
|------|------|------|
| **AI_PM** | Claude Code guide for PMs — learn the why and how | [github.com/kimsanguine/AI_PM](https://github.com/kimsanguine/AI_PM) |
| **hplan** | Ready-to-use agent skillset — the tools *(this repo)* | [github.com/kimsanguine/hplan](https://github.com/kimsanguine/hplan) |

> **AI_PM** teaches the thinking. **hplan** gives you the tools.

---

## License

MIT — [LICENSE](LICENSE)
