# LangGraph PR and Ticket Review Readiness Agent

Planned moderate-scope DevOps LangGraph project for reviewing pull requests and linked tickets against lower-layer readiness checklists before they are handed to a human reviewer.

This project is intentionally narrower than a full release-governance system and intentionally more structured than a generic chatbot reviewer.

Its purpose is not to replace human review.

Its purpose is to make human review higher quality by ensuring the lower-layer checks have already been performed.

This project fits the repo's DevOps and orchestration direction because it focuses on:

- pre-review operational quality gates
- structured workflow routing
- checklist enforcement
- human handoff preparation
- clear separation between automated validation and human decision-making

It also complements the existing LangGraph incident project well:

- `langgraph-incident-command-graph` is about incident triage after a problem appears
- this project is about review readiness before a change reaches a human reviewer

Together, they cover both reactive and preventive DevOps agent patterns.

## Problem Statement

In many engineering teams, pull requests and operational tickets reach human reviewers before basic readiness information has been provided.

That creates avoidable friction such as:

- missing linked ticket context
- no rollback note
- missing test evidence
- unclear environment impact
- undeclared config or secret changes
- no post-deploy validation plan

Human reviewers then spend time requesting the same baseline information repeatedly instead of focusing on higher-value technical judgment.

This project is intended to solve that gap.

## Project Goal

Build a LangGraph workflow that reviews a PR or ticket before human review and produces one of these outcomes:

- `ready_for_human_review`
- `needs_more_info`
- `blocked_by_checklist`

The workflow should inspect the provided change context, evaluate lower-layer checklist requirements, summarize risk, and create a clean handoff note for the human reviewer.

## Why LangGraph Is The Right Framework

This is a workflow problem more than a free-form agent chat problem.

The system needs to:

- inspect inputs
- validate required fields
- check checklist items
- branch based on missing information or elevated risk
- generate a handoff result

That is a strong LangGraph fit because LangGraph is useful when you need:

- explicit state
- deterministic routing
- conditional edges
- stop conditions
- structured outputs

This project could later integrate with MCP or n8n, but LangGraph should be the core orchestration layer.

## Scope Level

This should stay moderate in scope.

That means:

- no need for real GitHub, Jira, PagerDuty, or Kubernetes integration in the first version
- use fixture-backed inputs and mock PR or ticket payloads
- focus on workflow quality and output quality
- keep the first version local, testable, and easy to demo

This makes it realistic to implement while still showing meaningful engineering design.

## Planned Inputs

The first implementation should accept structured input representing a PR or ticket review package.

Likely fields:

- `artifact_type`
- `pr_title`
- `pr_description`
- `ticket_id`
- `ticket_summary`
- `changed_files_summary`
- `environment`
- `service_name`
- `test_evidence`
- `rollback_note`
- `monitoring_note`
- `deployment_note`
- `config_or_secret_change`

The initial version can treat these as local JSON fixtures or CLI-provided inputs.

## Planned Outcomes

### `ready_for_human_review`

Use this when:

- required context exists
- checklist is complete
- risk is summarized
- no mandatory blocker is missing

The human reviewer should receive:

- a concise readiness summary
- checklist status
- risk level
- specific review flags

### `needs_more_info`

Use this when the change is not fundamentally blocked, but information is missing.

Typical examples:

- linked ticket exists but rollout note is missing
- test evidence is vague or absent
- environment impact is not described
- monitoring validation steps are missing

The system should clearly state what must be added before human review.

### `blocked_by_checklist`

Use this when baseline readiness conditions are not met.

Typical examples:

- no linked ticket for a required change
- no rollback note for production-impacting work
- undeclared secret or config impact
- missing ownership or affected service information

This is a workflow block, not a final engineering judgment.

## Planned Workflow

The initial graph should likely use nodes such as:

1. `intake`
2. `artifact_classifier`
3. `ticket_link_check`
4. `checklist_reviewer`
5. `change_scope_reviewer`
6. `risk_summary`
7. `decision_router`
8. `human_handoff`

## Planned Node Responsibilities

### `intake`

- normalize the input package
- validate expected input shape
- initialize graph state

### `artifact_classifier`

- determine whether the item is primarily:
- application change
- infrastructure change
- CI/CD change
- configuration change
- mixed change

This classification should influence which checklist items matter most.

### `ticket_link_check`

- verify a linked ticket exists when required
- confirm the ticket includes purpose, scope, and acceptance criteria
- ensure the ticket is relevant to the PR or requested review item

### `checklist_reviewer`

- review baseline readiness checklist items
- identify missing or weak evidence
- mark items as passed, missing, or blocked

### `change_scope_reviewer`

- identify whether the change touches:
- deployment configuration
- CI/CD pipelines
- secrets or config
- networking
- database or migrations
- customer-facing production services

This scope review should feed the risk summary.

### `risk_summary`

- assign a risk level such as low, medium, or high
- highlight why the change needs closer human attention
- avoid pretending to make final approval decisions

### `decision_router`

- produce `ready_for_human_review`, `needs_more_info`, or `blocked_by_checklist`
- route based on checklist completeness and scope impact

### `human_handoff`

- prepare a concise reviewer-facing summary
- include:
- checklist status
- risk level
- missing items if any
- recommendation for what the human reviewer should focus on

## Planned State Design

The graph state should remain explicit and compact.

A strong first version would likely track:

- `artifact_type`
- `ticket_present`
- `required_fields_missing`
- `checklist_results`
- `scope_flags`
- `risk_level`
- `decision`
- `review_summary`
- `handoff_note`

This makes testing easier and keeps the workflow inspectable.

## Planned Checklist Areas

The checklist should focus on practical DevOps review readiness, not abstract AI behavior.

Baseline checklist areas:

- linked ticket exists
- purpose of change is clearly described
- affected service or environment is identified
- rollback note is included
- test evidence is included
- monitoring or alerting impact is described
- deployment note is present when relevant
- config or secret changes are declared
- post-deploy validation steps are included

Optional later additions:

- migration impact declared
- cross-team dependency note included
- blast-radius statement included
- reviewer ownership or domain label present

## Planned Conditional Routing

The graph should explicitly model routing such as:

- missing ticket -> `blocked_by_checklist`
- missing rollback note for production-impacting change -> `blocked_by_checklist`
- missing test evidence -> `needs_more_info`
- complete checklist with manageable risk -> `ready_for_human_review`

This should be implemented as graph routing, not hidden prompt behavior.

## Planned Output Shape

A strong structured output should include:

- `decision`
- `artifact_type`
- `risk_level`
- `checklist_status`
- `missing_items`
- `reviewer_focus_areas`
- `handoff_summary`

That output should be readable by both humans and future automation layers.

## Planned Example Prompts

- `Review this PR for readiness before platform reviewer handoff. It modifies Helm values and deployment probes.`
- `Check whether this infrastructure ticket is complete enough for human SRE review.`
- `Validate this CI pipeline PR against the lower-layer DevOps checklist and tell me if it is ready for human approval.`
- `Review this production config change ticket and tell me whether it should pass to a human reviewer or be blocked for missing information.`

## Planned Local Test Fixtures

The first implementation should likely include sample inputs such as:

- application PR with complete checklist
- infrastructure ticket with missing rollback note
- CI/CD PR with missing test evidence
- config change with undeclared environment impact
- production ticket with clear handoff summary

These fixtures will make the project easier to test and demo.

## Planned Verification

Once implemented, test coverage should include:

- ready-for-review path
- needs-more-info path
- blocked-by-checklist path
- classifier behavior across multiple change types
- checklist validation output
- deterministic structured response generation
- graph visualization export

## Planned Stretch Goals

After the first working version, possible extensions include:

- GitHub PR metadata ingestion
- Jira ticket ingestion
- MCP-backed checklist retrieval
- n8n-triggered review workflows
- reviewer-specific handoff formatting

These should come after the first local, testable implementation is stable.

## Portfolio Value

This project should demonstrate:

- LangGraph workflow design for operational review gates
- practical DevOps checklist reasoning
- strong separation between automation and human judgment
- engineering-focused state and routing design
- a realistic pre-review automation use case

## Status

Current status: planning and README only.

No scaffold has been created yet beyond this folder and project brief.
