# Contributing to hplan

Thank you for your interest in contributing!

## Project Structure

```
hplan/                         # repo root
├── hplan/                     # Gate ⭐ — should we build this? (7 skills, 6 commands)
│   ├── .claude-plugin/
│   │   └── plugin.json
│   ├── skills/                # evidence-rubric, interview-synthesis, exclusions,
│   │   └── ...                # cogs-sentinel, ost, decision-log, handoff
│   ├── commands/              # hplan-evidence, -product, -build, -cogs, -exclude, -handoff
│   ├── scripts/               # 9 deterministic Python modules
│   ├── hplan_mcp/             # MCP server for Cursor/Windsurf/Kiro/Codex/Goose
│   ├── hooks/                 # PreToolUse gate_guard.py
│   ├── agents/                # 4 role-locked reviewer agents
│   └── references/            # 14 playbooks + provider_pricing.json
├── discover/                    # Discovery — what agent to build (6 skills)
│   ├── .claude-plugin/
│   │   └── plugin.json        # Plugin manifest (required)
│   ├── skills/
│   │   ├── opp-tree/SKILL.md
│   │   ├── assumptions/SKILL.md
│   │   └── ...
│   └── commands/
│       ├── discover.md
│       └── validate.md
├── architect/                     # Strategy — how to architect it (7 skills)
├── deliver/                     # Execution — spec and ship (12 skills)
├── operate/                     # Operations — KPI, reliability, PM knowledge (15 skills)
│   └── evals/                 # Trigger eval queries + benchmark data
│       ├── evals.json         # Quality eval definitions
│       ├── trigger-evals.json # Trigger accuracy queries
│       ├── per-skill/         # Per-skill eval files
│       └── workspace/         # Eval run outputs + benchmark results
├── README.md                  # English
├── README-ko.md               # Korean (한국어)
├── CHANGELOG.md               # Version history
├── progress.md                # Phase-by-phase progress log
└── CONTRIBUTING.md            # This file
```

## File Conventions

### SKILL.md Format

```markdown
---
name: skill-name-in-kebab-case
description: "One-line English description with 'Use when...' trigger pattern (200+ chars recommended)"
argument-hint: "What to provide — e.g., agent name, domain"
---

# Skill Title

> Korean one-line description (한국어 요약)

## Core Goal
1-2 sentence statement of the skill's purpose and primary output.

## Trigger Gate

**Use this skill when:**
- Condition 1
- Condition 2

**Route to another skill when:**
- `other-skill` — when X applies instead
- `another-skill` — when Y applies instead

**Boundary — what this skill does NOT do:**
- Out-of-scope item 1
- Out-of-scope item 2

## 개념 (Concept)
Korean explanation of the core idea.
This section teaches the PM the underlying framework/methodology.

## Instructions
English instructions with $ARGUMENTS variable.
Step-by-step LLM execution logic goes here.

## Failure Handling

| Failure | Detection | Fallback |
|---------|-----------|----------|
| Missing input | How to detect | What to do |
| Low-quality output | How to detect | What to do |

## Quality Gate (self-check before delivery)

- [ ] Check item 1
- [ ] Check item 2
- [ ] Check item 3

## Examples

**Good output signal:** Description of what a good result looks like.

**Bad output signal:** Description of what indicates the skill underperformed.
```

**Key rules:**
- `name` in frontmatter = directory name (kebab-case)
- `description` in English, 200+ chars recommended, with "Use when..." trigger phrases
- `argument-hint` describes what input the user should provide
- **Core Goal** — what this skill produces (1-2 sentences)
- **Trigger Gate** — Use/Route/Boundary for accurate skill selection
- **개념 (Concept)** in Korean for primary audience education
- **Instructions** in English for LLM execution quality
- **Failure Handling** — table of failure → detection → fallback
- **Quality Gate** — self-check checklist before delivering output
- **Examples** — good/bad output signals
- Always include `$ARGUMENTS` as the user input variable
- Keep skill names **short and intuitive** (e.g., `kpi`, `moat`, `prd`)

### Command Format

```markdown
---
description: "One-line English description with 'Use when...' trigger pattern"
---

# /command-name

> Korean description (한국어 요약)

## Instructions
Multi-phase workflow that references skills by name.
Use "invoke the X skill" rather than listing skills in frontmatter.
```

**Note:** Command frontmatter only supports `description:` as an official field. Do not use `skills:` or `name:` — these are not recognized by Claude Code.

### Plugin Manifest (plugin.json)

Each plugin has a `.claude-plugin/plugin.json` manifest (not PLUGIN.md):

```json
{
  "name": "plugin-name",
  "version": "0.3.0",
  "description": "Discovery-oriented description with 'Use when...' trigger phrases",
  "author": {
    "name": "Your Name",
    "url": "https://github.com/yourname"
  },
  "repository": "https://github.com/yourname/your-repo",
  "license": "MIT",
  "keywords": ["agent", "pm", "your-domain-keywords"],
  "skills": "./skills/",
  "commands": "./commands/"
}
```

## Naming Convention

### Plugin Names — Greek Mythology Archetypes

Each plugin is named after a Greek mythological figure whose archetype maps to a phase of the agent product lifecycle:

| Plugin | Archetype | Phase | Why |
|--------|-----------|-------|-----|
| **discover** | Oracle of Delphi (the seer) | Discovery | Reveals which agent to build |
| **architect** | Atlas (the titan) | Architecture | Bears the structural weight of design |
| **deliver** | Hephaestus's Forge | Execution | Crafts raw ideas into specs |
| **measure** | Argus Panoptes (100-eyed) | Monitoring | Watches every metric and failure |
| **learn** | The Muses | Knowledge | Transforms experience into wisdom |

Rules for new plugin names: (1) the metaphor must be instantly intuitive, (2) must work as a single-word CLI namespace.

### Skill Names — Short Functional Handles

**Skills** use short, functional names that anyone can understand at a glance (e.g., `kpi` not `agent-key-performance-indicators`, `3-tier` not `three-tier-orchestrator-architecture`).

Good examples: `prd`, `moat`, `cost-sim`, `premortem`, `hitl`

## How to Contribute

### Adding a New Skill

1. Choose the right plugin (hplan / discover / architect / deliver / measure / learn)
2. Create directory: `[plugin]/skills/[skill-name]/SKILL.md`
3. Follow the SKILL.md format above
4. Add a trigger eval query to `operate/evals/per-skill/[skill-name].json` (2 positive + 2 negative)
5. If the skill chains with others, update or create a Command

### Improving Existing Skills

- Fix instructions that produce poor LLM outputs
- Add missing edge cases or anti-patterns
- Improve examples and templates
- Translate or improve Korean/English sections

## PM-Framework Note

The `learn` plugin provides frameworks for managing PM tacit knowledge. **Frameworks** (TK structure, decision patterns) are open source. **Data** (your personal TK entries in `PM-ENGINE-MEMORY.md`) is yours and should never be committed.

## Questions?

Open an issue or reach out to [@your-github-username](https://github.com/your-github-username).
