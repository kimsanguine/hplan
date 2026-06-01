#!/usr/bin/env python3
"""Validate plugin structure, skill files, and command files.

Usage:
    python validate_plugins.py          # Validate all plugins
    python validate_plugins.py oracle   # Validate a specific plugin
"""

import json
import os
import re
import sys
from pathlib import Path

PLUGINS = ["hplan", "discover", "architect", "deliver", "operate"]
REQUIRED_SKILL_FIELDS = ["name", "description"]
SKILL_WORD_RANGE = (50, 5000)
DESC_MIN_LENGTH = 40
ERRORS = []
WARNINGS = []


def error(msg):
    ERRORS.append(msg)
    print(f"  ❌ {msg}")


def warn(msg):
    WARNINGS.append(msg)
    print(f"  ⚠️  {msg}")


def ok(msg):
    print(f"  ✅ {msg}")


def parse_frontmatter(filepath):
    """Extract YAML frontmatter from a markdown file."""
    content = filepath.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, content
    fm_text = match.group(1)
    fm = {}
    for line in fm_text.strip().split("\n"):
        if ":" in line:
            key, val = line.split(":", 1)
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm, content


def count_words(content):
    """Count words in content (excluding frontmatter)."""
    body = re.sub(r"^---\n.*?\n---\n?", "", content, flags=re.DOTALL)
    return len(body.split())


def validate_plugin_json(plugin_dir):
    """Validate plugin.json manifest."""
    pj = plugin_dir / ".claude-plugin" / "plugin.json"
    if not pj.exists():
        error(f"{plugin_dir.name}: Missing .claude-plugin/plugin.json")
        return False
    try:
        data = json.loads(pj.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        error(f"{plugin_dir.name}: Invalid JSON in plugin.json: {e}")
        return False

    for field in ["name", "version", "description", "author", "license"]:
        if field not in data:
            error(f"{plugin_dir.name}/plugin.json: Missing required field '{field}'")

    if data.get("name") != plugin_dir.name:
        error(f"{plugin_dir.name}/plugin.json: name '{data.get('name')}' != directory '{plugin_dir.name}'")

    desc = data.get("description", "")
    if len(desc) < DESC_MIN_LENGTH:
        warn(f"{plugin_dir.name}/plugin.json: description too short ({len(desc)} chars, min {DESC_MIN_LENGTH})")

    ok(f"{plugin_dir.name}/plugin.json valid")
    return True


def validate_skill(skill_dir):
    """Validate a single SKILL.md file. Returns (is_valid, is_alias)."""
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        error(f"{skill_dir}: Missing SKILL.md")
        return False, False

    fm, content = parse_frontmatter(skill_file)
    if fm is None:
        error(f"{skill_dir.name}: No frontmatter in SKILL.md")
        return False, False

    for field in REQUIRED_SKILL_FIELDS:
        if field not in fm:
            error(f"{skill_dir.name}: Missing frontmatter field '{field}'")

    if fm.get("name") != skill_dir.name:
        error(f"{skill_dir.name}: frontmatter name '{fm.get('name')}' != directory name")

    desc = fm.get("description", "")
    if len(desc) < DESC_MIN_LENGTH:
        warn(f"{skill_dir.name}: description too short ({len(desc)} chars)")

    is_alias = bool(fm.get("alias_for", "").strip())

    wc = count_words(content)
    lo, hi = SKILL_WORD_RANGE
    if wc < lo:
        if is_alias:
            # 의도적 alias wrapper — 단어 수 제한 면제
            pass
        else:
            # alias_for 없는 stub은 실행 불가 → error
            error(f"{skill_dir.name}: Only {wc} words (min {lo}) and no alias_for metadata — stub is non-executable")
    elif wc > hi:
        warn(f"{skill_dir.name}: {wc} words exceeds {hi} word soft limit")

    if "$ARGUMENTS" not in content:
        warn(f"{skill_dir.name}: No $ARGUMENTS variable found")

    alias_tag = f" [alias→{fm.get('alias_for')}]" if is_alias else ""
    ok(f"{skill_dir.name}/SKILL.md valid ({wc} words){alias_tag}")
    return True, is_alias


def validate_command(cmd_file):
    """Validate a command markdown file."""
    fm, content = parse_frontmatter(cmd_file)
    if fm is None:
        error(f"{cmd_file.name}: No frontmatter")
        return False

    if "description" not in fm:
        error(f"{cmd_file.name}: Missing 'description' in frontmatter")

    desc = fm.get("description", "")
    if "Use when" not in desc and "use when" not in desc.lower():
        warn(f"{cmd_file.name}: description lacks 'Use when...' trigger pattern")

    if "## Instructions" not in content:
        warn(f"{cmd_file.name}: Missing '## Instructions' section")

    if "## Output Format" not in content:
        warn(f"{cmd_file.name}: Missing '## Output Format' section")

    ok(f"{cmd_file.name} valid")
    return True


def validate_marketplace(root):
    """Validate marketplace.json."""
    mp = root / ".claude-plugin" / "marketplace.json"
    if not mp.exists():
        warn("No .claude-plugin/marketplace.json found")
        return
    try:
        data = json.loads(mp.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        error(f"marketplace.json: Invalid JSON: {e}")
        return

    plugin_names = {p["name"] for p in data.get("plugins", [])}
    expected = set(PLUGINS)
    if plugin_names != expected:
        error(f"marketplace.json plugins mismatch: got {plugin_names}, expected {expected}")
    else:
        ok(f"marketplace.json: All {len(expected)} plugins listed")


def main():
    root = Path(__file__).parent
    targets = sys.argv[1:] if len(sys.argv) > 1 else PLUGINS

    print("=" * 60)
    print("hplan — Plugin Validator")
    print("=" * 60)

    # Marketplace
    print("\n📦 Marketplace")
    validate_marketplace(root)

    total_skills = 0
    total_aliases = 0
    total_commands = 0
    EXPECTED_ACTIVE_SKILLS = 32
    EXPECTED_ALIASES = 0
    # v0.13.x migration note: deliver/ticket-bridge skill added (GitHub Issues ⇄ sprint/.track bridge).
    # deliver plugin skills +1. Total: 31 → 32.
    # v0.13.0 migration note: conductor Phase 0/Step E/--mode sprint + ui-validate assertion engine.
    # No skill count change — all existing skills strengthened. Total: 31 (unchanged).
    # v0.12.0 migration note: brainstorm skill added to hplan plugin.
    # hplan plugin: 7 → 8 skills. Total: 30 → 31.
    # v0.11.0 migration note: 18 skills consolidated (48→30).
    # Removed/merged: pmf-gate, agent-gtm, build-or-buy, biz-model, moat, growth-loop,
    #   burn-rate, weekly-rollup, agent-portfolio, portfolio-report, pm-decision,
    #   agent-ab-test, cohort, cross-team-routing, premortem, scorecard-5axis,
    #   agent-instructions, claude-md, delivery-plan, track, agent-plan-review,
    #   ctx-budget, stakeholder-map, harness-design, parallel-team.
    # Added: conductor, qa-checklist, ops-review, portfolio, strategy, agent-setup, sprint.
    # v0.10.1 migration note: 17 deprecated aliases removed intentionally.
    # Removed aliases: mobile-check, hierarchy-rules, motion-language, ui-drift-detect,
    #   estimate-tasks, progress-probe, blocker-detect, progress-report, gate-checkpoint,
    #   velocity-baseline, respect-brief, respect-checkpoint, scorecard-5axis, weekly-rollup,
    #   north-star, kpi, pm-framework.
    # Replacements: see README.md "Plugins — Full Skill List" for --mode / --step routes.

    for plugin_name in targets:
        plugin_dir = root / plugin_name
        if not plugin_dir.is_dir():
            error(f"Plugin directory '{plugin_name}' not found")
            continue

        print(f"\n🔌 Plugin: {plugin_name}")

        # plugin.json
        validate_plugin_json(plugin_dir)

        # Skills
        skills_dir = plugin_dir / "skills"
        if skills_dir.is_dir():
            for skill_dir in sorted(skills_dir.iterdir()):
                if skill_dir.is_dir():
                    _, is_alias = validate_skill(skill_dir)
                    total_skills += 1
                    if is_alias:
                        total_aliases += 1

        # Commands
        cmds_dir = plugin_dir / "commands"
        if cmds_dir.is_dir():
            for cmd_file in sorted(cmds_dir.glob("*.md")):
                validate_command(cmd_file)
                total_commands += 1

    # Skill count validation (full scan only)
    active_skills = total_skills - total_aliases
    if len(targets) == len(PLUGINS):  # full scan
        if active_skills != EXPECTED_ACTIVE_SKILLS:
            error(f"Active skill count mismatch: {active_skills} active (expected {EXPECTED_ACTIVE_SKILLS})")
        else:
            ok(f"Active skill count: {active_skills} ✓")
        if total_aliases != EXPECTED_ALIASES:
            error(f"Alias count mismatch: {total_aliases} aliases (expected {EXPECTED_ALIASES})")
        else:
            ok(f"Alias count: {total_aliases} ✓")

    # Summary
    print("\n" + "=" * 60)
    print(f"Scanned: {len(targets)} plugins, {active_skills} active + {total_aliases} alias = {total_skills} skills, {total_commands} commands")
    print(f"Errors:   {len(ERRORS)}")
    print(f"Warnings: {len(WARNINGS)}")
    print("=" * 60)

    if ERRORS:
        print("\n🚫 VALIDATION FAILED")
        sys.exit(1)
    else:
        print("\n✅ ALL CHECKS PASSED")
        sys.exit(0)


if __name__ == "__main__":
    main()
