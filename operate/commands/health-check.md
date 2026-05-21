---
name: health-check
description: "Weekly agent health check — operational metrics, reliability, and quick improvement actions. Use when reviewing agent performance, running weekly status checks, or monitoring agent operational health."
argument-hint: "[agent name]"
---

# /health-check

> 에이전트 주간 건강 점검

## Instructions

You are running a **Weekly Health Check** for: **$ARGUMENTS**

### Phase 1: KPI Dashboard (kpi)
Use the **kpi** skill.
- Pull current values for operational KPIs (latency, success rate, error rate)
- Pull business KPIs (task completion, user satisfaction, cost per task)
- Compare with previous week and targets

### Phase 2: Reliability Scan (reliability)
Use the **reliability** skill.
- Check for degradation patterns
- Review error logs for new failure modes
- Assess SLA compliance

### Phase 3: North Star Check (north-star)
Use the **north-star** skill.
- Track North Star metric trend
- Identify leading indicators that are changing
- Flag early warnings

## Output Format

Deliver a **Weekly Health Report** with:
1. Traffic light summary (🟢 🟡 🔴 for each area)
2. Key metrics table with WoW change
3. Top 3 issues to address
4. Recommended actions for next week
