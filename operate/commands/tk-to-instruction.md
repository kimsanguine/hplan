---
name: tk-to-instruction
description: "Convert a TK (Tacit Knowledge) entry into an agent instruction fragment that can be embedded in system prompts. Use when turning PM knowledge into agent behavior, creating instruction snippets from experience, or building agent personality from tacit knowledge."
argument-hint: "[TK-NNN identifier]"
---

# /tk-to-instruction

> TK를 에이전트 Instruction 조각으로 변환

## Instructions

You are converting **TK to Agent Instruction** for: **$ARGUMENTS**

### Phase 1: TK Retrieval (pm-engine)
Use the **pm-engine** skill.
- Retrieve the specified TK entry from PM-ENGINE-MEMORY.md
- If no specific TK is named, list available entries for selection

### Phase 2: Instruction Translation (pm-framework)
Use the **pm-framework** skill.
- Convert the TK's core insight into imperative instruction language
- Transform activation/deactivation conditions into if/when clauses
- Adapt the knowledge level (expert → instruction for any model)

### Phase 3: Instruction Formatting
Format as an agent instruction fragment:
```
## [TK Name] (from TK-NNN)
When [activation condition]:
- [Instruction 1]
- [Instruction 2]
Do NOT apply when [deactivation condition].
Rationale: [Why this matters]
```

### Phase 4: Integration Guide
- Suggest where in a system prompt this instruction fits best
- Note any dependencies on other instructions
- Provide a test scenario to verify the instruction works

## Output Format

Deliver an **Instruction Fragment** ready to paste into a system prompt, plus integration notes.
