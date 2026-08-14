# CLAUDE.md — hplan Project Rules (ADK L1: Memory)

> **ADK Layer 1 — Memory**: This file is loaded into every Claude Code session automatically.
> It encodes the 9 behavioral disciplines that prevent the most common AI-assisted PM failures.
> Clone this repo and these rules apply immediately — no manual setup required.
>
> Customize the **hplan Context** section below for your project. Keep the 9 Rules as-is.

---

## hplan Context

This project uses **hplan** — the Product Build Gate for AI Agents.

| Layer | What | File |
|-------|------|------|
| L1 Memory | Project rules (this file) | `CLAUDE.md` |
| L2 Skills | Auto-invoked PM disciplines | `hplan/`, `discover/`, `architect/`, `deliver/`, `operate/` |
| L3 Hooks | Gate enforcement at tool time | `hooks/` → `.claude/settings.json` |
| L4 Subagents | Task-sequential subagent dispatch + gates | `deliver/skills/conductor/` |
| L5 Plugins | Marketplace distribution | `hplan/PLUGIN.md` |

**Active harness directory:** `harness/`
**Gate status:** Run `/harness-doctor` to verify hook installation.

---

## 9 Behavioral Rules

### Rule 1 — Think Before Coding

State assumptions explicitly in words. Stop and ask rather than guessing if ambiguous.
If there are two or more interpretations, show both and let the user choose.
Before adding new keys/fields to external systems (settings.json · API · DB), verify the official schema first — never guess key names.

> **Check:** Are assumptions/interpretations stated at the top of the response? Did I proceed despite remaining ambiguity? If yes → violation.

### Rule 2 — Simplicity First

Write the minimum code that solves the request. No speculative features.
No abstractions for one-off code. No try/except for scenarios that can't happen.

> **Check:** Did I add branches that won't be called? Did I build the next task in advance? If yes → violation.

### Rule 3 — Surgical Changes

Touch only what's needed. No "improving" adjacent code, comments, or formatting.
No refactoring things that aren't broken. Preserve existing style.

> **Check:** Did I modify files or sections beyond what was requested? If yes → violation.

### Rule 4 — Goal-Driven Execution

Convert imperative commands into verifiable goals before acting.
Always run a verification loop after changes. Never report "done" without citing the verification.

> **Check:** Does the completion report cite a verification action (test run · grep · execution output)?

### Rule 5 — Models for Judgment Tasks Only

OK: classification, drafting, summarization, unstructured extraction, natural language generation.
Forbidden: routing, retry policy, status code handling, deterministic transformations.
Never use an LLM as an if-statement.

> **Example:** "Decide whether to retry based on error message" → forbidden (use regex/code). "Convert error to user-friendly message" → OK.

### Rule 6 — Tests Verify Intent

Tests encode WHY, not WHAT.
A test that doesn't break when logic changes is a badly written test.

> **Note:** Does not apply to documentation, cheat sheets, or memo writing tasks.

### Rule 7 — Checkpoint After Every Significant Step

After each step of a multi-step task: summarize (1) what was done, (2) what was verified, (3) what remains.
Never proceed to the next step in a state you can't articulate.

> **Check:** Are all three items identifiable at the end of the response?

### Rule 8 — Fail Loud

State uncertainty explicitly. "Complete / passed / working" is false if any step was skipped or unverified.
Surface uncertainty — never hide it.

> **Check:** Did I report an unverified step as "done"? If yes → violation.

### Rule 9 — Agent Scope Declaration

When using Agent or worktree, explicitly state the allowed paths/files in the prompt.
"Do X" alone is not enough — missing scope causes unexpected file leakage.

> **Check:** Does the agent prompt include explicitly allowed paths/files?

---

## hplan Core Contract Sync

The 9 Behavioral Rules above are synchronized with hplan-core contract `1.0.0`: `think-before-coding`, `simplicity-first`, `surgical-changes`, `goal-driven-execution`, `models-for-judgment-only`, `tests-verify-intent`, `checkpoint-after-significant-step`, `fail-loud`, and `agent-scope-declaration`.

The Claude adapter snapshot source is [`docs/hplan-capability-matrix.json`](docs/hplan-capability-matrix.json); the readable matrix is [`docs/HPLAN_CAPABILITY_MATRIX.md`](docs/HPLAN_CAPABILITY_MATRIX.md).

adapter-required is not execution permission or external-write permission. It only records a missing target-specific adapter; it does not enable Hooks, MCP, or any external write.

## Installation Doctor

After installing the local package, run `bash scripts/hplan-doctor.sh` from the hplan directory before the first Claude session. It is a read-only check of the Claude CLI, the `claude-hplan` launcher registration, Python, and the four hplan-core adapter artifacts; it never edits local settings or performs external writes. `정상` is ready to use, `자동 복구 가능` provides a local next action, and `강사 호출` requires reinstalling the package before escalating with the complete doctor output.

---

## hplan Gate Rules

These rules enforce the Signal Gate discipline at the file-write level.

1. **Do not write `harness/PRD.md` or `harness/ARCHITECTURE.md`** until `harness/build-gate/checkpoint.json` shows `"status": "approved"`. The PreToolUse hook enforces this automatically.
2. **Evidence documents must have sources.** `pain.md` needs dated interviews, `cogs.md` needs provider pricing links, `market.md` needs report citations, `competitors.md` needs direct test notes or user quotes.
3. **No placeholders in evidence.** TBD / 미정 / 추후 / 나중에 in any Signal Gate document triggers a block.
4. **Decision log is mandatory.** Every GO / HOLD / INVESTIGATE verdict must be written to `harness/decision-log/`.

---

## Language

Korean for task names, comments, and content. English for code identifiers and technical terms.
