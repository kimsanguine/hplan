---
name: extract
description: "Extract PM tacit knowledge from an experience or situation and structure it as a TK unit. Use when capturing lessons learned, documenting decision rationale, or converting experience into reusable knowledge."
argument-hint: "[experience or lesson learned]"
---

# /extract

> PM 경험에서 암묵지를 추출하고 TK로 구조화

## Instructions

You are extracting **PM Tacit Knowledge** from: **$ARGUMENTS**

### Phase 1: Experience Analysis (pm-framework)
Use the **pm-framework** skill.
- Identify the core insight from the experience
- Classify the TK type: Decision Pattern / Failure Pattern / Heuristic / Anti-Pattern / Insight
- Assign a TK-NNN identifier

### Phase 2: Structure as TK Unit
Format the knowledge using the TK template:
- **Name**: Memorable, descriptive title
- **Type**: DP / FP / HE / AP / IN
- **Context**: When does this knowledge apply?
- **Activation Conditions**: What triggers this knowledge?
- **Deactivation Conditions**: When does it NOT apply?
- **Core Insight**: The actual knowledge (1-2 sentences)
- **Evidence**: Supporting experiences or data
- **Counter-examples**: When this failed or didn't apply

### 🔍 Checkpoint
Before storing to PM-ENGINE-MEMORY, present the user with:
1. **Summary**: Extracted TK unit with type classification and activation conditions
2. **Options**:
   - "Store this TK unit as-is"
   - "Refine the activation/deactivation conditions"
   - "Extract additional TK units from the same experience"

Wait for user confirmation before continuing to Phase 3.

### Phase 3: Store (pm-engine)
Use the **pm-engine** skill.
- Add to PM-ENGINE-MEMORY.md
- Cross-reference with existing TK entries
- Update index

## Output Format

Deliver a **TK Unit** ready for PM-ENGINE-MEMORY.md insertion.
