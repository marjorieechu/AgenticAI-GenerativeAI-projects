# Projects

This folder contains the practical side of the repository.

The early projects are intentionally simple. Over time, this folder moves from tutorial-scale agents into more realistic systems that combine orchestration, memory, retrieval, tooling, and DevOps automation.

## Current Projects

### No-memory-AI-Agent

An early single-agent baseline.

What it proves:

- basic prompt-to-response agent behavior
- simple tool-free execution
- a clean starting point before adding memory, guardrails, and retrieval

### multi-ai-agent

An early multi-agent exploration.

What it proves:

- task decomposition across more than one agent
- agent collaboration patterns
- a stepping stone toward orchestrated workflows

## Recommended Next Builds

These are the strongest next projects for this repo because they are practical, portfolio-friendly, and aligned with real engineering workflows.

### 1. DevOps Runbook RAG Assistant

Input:

- markdown runbooks
- postmortems
- onboarding docs
- deployment notes

Output:

- grounded answers with citations
- suggested remediation steps
- escalation guidance

Why it matters:

- shows practical RAG, not toy chatbot work
- maps well to SRE and platform engineering use cases
- easy to expand with evaluation later

Suggested stack:

- Python
- embeddings plus vector store
- retrieval pipeline
- optional LangGraph for answer and verification flow

### 2. Incident Response Multi-Agent Workflow

Agent roles:

- log analysis agent
- incident summarizer
- remediation planner
- communication agent

Why it matters:

- demonstrates clear agent specialization
- fits real operations workflows
- strong visibility project because it is easy to explain

Suggested stack:

- CrewAI or LangGraph
- structured JSON outputs
- optional dashboard or CLI

### 3. Ticket Review And Triage Agent

Input:

- GitHub issues
- Jira-style tickets
- bug reports
- feature requests

Output:

- ticket type classification
- completeness review
- suggested priority
- missing information checklist
- rewritten engineering-ready summary

Why it matters:

- aligns well with backlog triage and delivery workflows
- shows practical AI support for software teams
- can grow into RAG using internal templates, policies, and runbooks

Suggested stack:

- Python
- structured outputs
- GitHub API or Jira API
- optional RAG for ticket standards and team playbooks

### 4. AI Release Notes and Change Summary Agent

Input:

- merged pull requests
- commit history
- linked issues

Output:

- human-readable release notes
- risk summary
- deployment checklist

Why it matters:

- very practical
- fast to build
- useful for personal and team workflows

### 5. n8n Ops Automation Assistant

Workflow ideas:

- watch a GitHub issue
- summarize context
- create tasks
- notify Slack or email
- update Google Sheets or Notion

Why it matters:

- shows low-code orchestration skills
- useful for demos and quick wins
- pairs well with MCP and API-based tools

## Build Standard For Future Projects

Each project in this repo should eventually include:

- problem statement
- architecture diagram or workflow description
- setup steps
- example input and output
- limitations
- next iteration plan
