# HPLAN Capability Matrix

Contract version: `1.0.0`
Target: `claude`

| Capability | Lifecycle | Owner | Support | Entrypoint | Smoke fixture | Fallback artifact |
| --- | --- | --- | --- | --- | --- | --- |
| agent-setup | active | hplan-core | native | capability:agent-setup | smoke.agent-setup | agent-setup-checklist |
| ask-team | active | hplan-core | native | capability:ask-team | smoke.ask-team | team-question-brief |
| assumptions | active | hplan-core | native | capability:assumptions | smoke.assumptions | assumption-register |
| brainstorm | active | hplan-core | native | capability:brainstorm | smoke.brainstorm | idea-set |
| build-loop | active | hplan-core | native | capability:build-loop | smoke.build-loop | build-checklist |
| cogs-sentinel | active | hplan-core | native | capability:cogs-sentinel | smoke.cogs-sentinel | cost-risk-report |
| conductor | active | hplan-core | native | capability:conductor | smoke.conductor | delivery-plan |
| cost-sim | active | hplan-core | native | capability:cost-sim | smoke.cost-sim | cost-simulation |
| customer-reach | active | hplan-core | native | capability:customer-reach | smoke.customer-reach | outreach-brief |
| decision-log | active | hplan-core | native | capability:decision-log | smoke.decision-log | decision-record |
| design-token | active | hplan-core | native | capability:design-token | smoke.design-token | design-token-set |
| evidence-rubric | active | hplan-core | native | capability:evidence-rubric | smoke.evidence-rubric | evidence-scorecard |
| exclusions | active | hplan-core | native | capability:exclusions | smoke.exclusions | exclusion-register |
| handoff | active | hplan-core | native | capability:handoff | smoke.handoff | handoff-brief |
| hitl | active | hplan-core | native | capability:hitl | smoke.hitl | approval-plan |
| incident | active | hplan-core | native | capability:incident | smoke.incident | incident-report |
| interview-synthesis | active | hplan-core | native | capability:interview-synthesis | smoke.interview-synthesis | research-synthesis |
| memory-arch | active | hplan-core | native | capability:memory-arch | smoke.memory-arch | memory-architecture |
| metrics-design | active | hplan-core | native | capability:metrics-design | smoke.metrics-design | metrics-tree |
| opp-tree | active | hplan-core | native | capability:opp-tree | smoke.opp-tree | opportunity-tree |
| ops-review | active | hplan-core | native | capability:ops-review | smoke.ops-review | operations-review |
| orchestration | active | hplan-core | native | capability:orchestration | smoke.orchestration | orchestration-design |
| ost | active | hplan-core | native | capability:ost | smoke.ost | opportunity-solution-tree |
| pm-engine | active | hplan-core | native | capability:pm-engine | smoke.pm-engine | knowledge-unit |
| portfolio | active | hplan-core | native | capability:portfolio | smoke.portfolio | portfolio-review |
| prd | active | hplan-core | native | capability:prd | smoke.prd | product-requirements-document |
| qa-checklist | active | hplan-core | native | capability:qa-checklist | smoke.qa-checklist | quality-checklist |
| reliability | active | hplan-core | native | capability:reliability | smoke.reliability | reliability-review |
| respect | active | hplan-core | native | capability:respect | smoke.respect | collaboration-brief |
| socratic-question | active | hplan-core | native | capability:socratic-question | smoke.socratic-question | discovery-question-set |
| sprint | active | hplan-core | native | capability:sprint | smoke.sprint | sprint-plan |
| strategy | active | hplan-core | native | capability:strategy | smoke.strategy | strategy-brief |
| ticket-bridge | active | hplan-core | native | capability:ticket-bridge | smoke.ticket-bridge | ticket-brief |
| ui-validate | active | hplan-core | native | capability:ui-validate | smoke.ui-validate | ui-validation-report |

## Compatibility aliases

| Alias | Canonical target | Expiry |
| --- | --- | --- |
| roadmap | prd | 2027-08-14 |
| router | orchestration | 2027-08-14 |
| stakeholder-update | ops-review | 2027-08-14 |
