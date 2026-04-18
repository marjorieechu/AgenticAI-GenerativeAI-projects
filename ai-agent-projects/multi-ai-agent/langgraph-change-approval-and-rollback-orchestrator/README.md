# LangGraph Change Approval and Rollback Orchestrator

Planned advanced DevOps LangGraph project focused on release risk evaluation, controlled approval routing, rollback planning, and post-deployment validation.

This project is intentionally positioned as a stronger follow-up to `langgraph-incident-command-graph`.

The incident-command graph focuses on:

- incident triage
- tool routing
- rollback and postmortem specialist branches
- guarded response generation

This next project raises the bar by shifting from reactive incident handling to proactive release control.
After learning more agent patterns through tools like CrewAI and workflow automation through tools like n8n.

Why:

- CrewAI helps internalize agent roles, delegation, and collaboration patterns
- n8n helps reinforce orchestration and event-driven automation thinking
- LangGraph is strongest when you already understand multi-step agent behavior and want to make it explicit, stateful, and controlled

That makes this project a better next step than another general-purpose LangGraph assistant.

## Why It Is More Advanced

Compared with the existing LangGraph DevOps incident project, this one is more advanced because it is expected to include:

- stronger state management across release stages
- clearer approval and blocking logic
- more deterministic operational routing
- richer risk-scoring and readiness decisions
- deeper rollback planning
- structured post-deploy validation output

This project should feel closer to a production release-governance system than a response-oriented incident assistant.

## Planned Problem Statement

Teams regularly need to decide whether a deployment or infrastructure change should proceed, pause, require approval, or be rolled back.

Those decisions are often based on fragmented context such as:

- release notes
- CI status
- recent incidents
- dependency risk
- service criticality
- known rollout constraints

This project will explore how LangGraph can model that decision path explicitly instead of leaving it as an unstructured chatbot conversation.

## Planned Goal

Build a DevOps-focused LangGraph workflow that can:

- assess change risk
- gather release evidence from multiple sources
- route high-risk changes into stricter review
- recommend approve, hold, or rollback-ready deployment
- generate rollback guidance when risk is elevated
- produce post-deploy verification steps

## Planned Workflow

The current concept is a graph with nodes such as:

1. `guardrail`
2. `change_intake`
3. `release_notes_lookup`
4. `test_signal_lookup`
5. `service_dependency_lookup`
6. `incident_history_lookup`
7. `risk_scorer`
8. `approval_specialist`
9. `rollback_specialist`
10. `post_deploy_validation_specialist`
11. `final_recommender`

Possible routing patterns:

- `guardrail -> final_recommender` for blocked or out-of-scope requests
- `change_intake -> release/test/dependency/incident evidence nodes`
- `risk_scorer -> approval_specialist` for medium or high risk
- `risk_scorer -> rollback_specialist` when rollback planning is needed
- `risk_scorer -> post_deploy_validation_specialist` when rollout is allowed but needs explicit checks
- specialist nodes -> `final_recommender`

## Planned State Design

The project will likely need a richer state object than the current incident graph. Expected state fields include:

- `change_request`
- `service_name`
- `environment`
- `risk_level`
- `approval_status`
- `evidence`
- `recommended_action`
- `rollback_plan`
- `post_deploy_checks`
- `audit_notes`

This should make the graph easier to inspect, test, and reason about than a looser multi-agent conversation.

## Planned Tooling

The likely first version should stay infrastructure-light and use fixture-backed tools, similar to the current incident graph.

Planned tools:

- `search_release_notes`
- `search_ci_results`
- `search_service_catalog`
- `search_past_incidents`
- `search_runbooks`
- optional `search_live_web`

That keeps the project testable without requiring real cloud, Kubernetes, PagerDuty, GitHub Actions, or Jira integrations.

## Planned Specialist Branches

Unlike the current incident project, this makes specialist review central to the architecture.

Likely branches:

- `approval_review`
- `rollback_analysis`
- `post_deploy_validation_plan`

These branches would not just gather evidence. They would transform the graph into distinct operational decision modes.

## Planned Example Prompts

- `Should we approve deployment of the payments API given two flaky tests and a recent timeout incident?`
- `Create a rollback plan for the checkout service if the new release increases 5xx errors after rollout.`
- `Assess release risk for this database migration and tell me what validation gates are missing.`
- `We want to deploy a config change to production. What evidence should be reviewed before approval?`

## Planned Verification

Once implemented, this project should be tested for at least:

- approval without specialist escalation
- evidence gathering across multiple tool nodes
- rollback-specialist routing
- post-deploy validation routing
- blocked request handling
- deterministic structured outputs
- graph visualization export

## Portfolio Value

This project should demonstrate:

- DevOps-aligned LangGraph architecture
- explicit operational state transitions
- controlled routing rather than ad hoc tool calling
- practical release-governance thinking
- stronger engineering maturity than a generic multi-agent demo

## Status

Current status: planning and README only.

No scaffold has been created yet beyond this folder and project brief.
