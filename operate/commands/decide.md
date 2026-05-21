---
name: decide
description: "Apply decision patterns from the library to a current situation. Match, apply, check for traps, and optionally extract new patterns. Use when facing a product decision, choosing between options, or wanting to apply structured decision frameworks."
argument-hint: "[decision situation]"
---

# /decide

> 의사결정 패턴 매칭 및 적용

## Instructions

You are applying **Decision Patterns** to: **$ARGUMENTS**

### Phase 1: Situation Analysis
- Describe the decision context clearly
- Identify stakeholders and constraints
- List the options being considered

### Phase 2: Pattern Matching (pm-decision)
Use the **pm-decision** skill.
- Match the situation against the 6 core decision patterns
- Select the most applicable pattern(s)
- Check for cognitive traps (sunk cost, anchoring, etc.)

### Phase 3: Apply Pattern (pm-framework)
Use the **pm-framework** skill.
- Apply the matched pattern to the current situation
- Document the reasoning process
- Generate a recommendation with confidence level

### Phase 4: Knowledge Capture (optional)
If a new insight emerged:
- Extract and structure as a new TK unit
- Update PM-ENGINE-MEMORY.md via **pm-engine** skill

## Output Format

Deliver a **Decision Log** with:
1. Decision context and options
2. Matched pattern(s) and rationale
3. Analysis using the pattern framework
4. Recommendation with confidence level (High/Medium/Low)
5. Risks and mitigation plan
