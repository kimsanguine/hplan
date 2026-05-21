---
name: cost-review
description: "Monthly cost review — token spend analysis, budget tracking, and cost optimization recommendations. Use when reviewing agent operating costs, planning cost reduction, or doing monthly budget reconciliation."
argument-hint: "[agent name]"
---

# /cost-review

> 에이전트 월간 비용 리뷰

## Instructions

You are running a **Monthly Cost Review** for: **$ARGUMENTS**

### Phase 1: Spend Analysis (burn-rate)
Use the **burn-rate** skill.
- Break down token spend by model, task type, and user segment
- Compare actual vs budgeted spend
- Calculate cost per successful task

### Phase 2: Efficiency Metrics (kpi)
Use the **kpi** skill to correlate cost with business impact.
- Cost per converted user
- ROI calculation (value delivered / tokens spent)
- Identify highest-cost, lowest-value interactions

### Phase 3: Optimization Plan
Based on Phase 1 and 2:
- Identify top 3 cost reduction opportunities
- Model potential savings from model routing changes
- Recommend prompt optimization targets

## Output Format

Deliver a **Monthly Cost Report** with:
1. Executive summary (total spend, budget variance, unit economics)
2. Spend breakdown table
3. Cost-efficiency analysis
4. Top 3 optimization recommendations with estimated savings
5. Budget forecast for next month
