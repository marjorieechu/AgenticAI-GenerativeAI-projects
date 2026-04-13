# Agentic AI Projects

The repo serves as proof-of-work space for agentic AI.

It documents my learning journey from my course materials, build small and medium projects, and gradually move from simple single-agent experiments into production-minded agent workflows that fit real software and DevOps environments.

## Objectives

My current goal is not just to finish tutorials. It is to show visible progress in:

- agent design
- orchestration frameworks
- memory and tool use
- multi-agent workflows
- retrieval and context systems
- automation and DevOps-aligned AI workflows


## Current Learning Sources

The local course archive in this workspace covers these areas:

- OpenAI Agents SDK for single-agent systems
- OpenAI Agents SDK for multi-agent workflows
- AutoGen
- LangGraph
- CrewAI
- MCP servers
- n8n AI workflows

Those materials are being translated here into cleaner notes, skills documentation, and practical projects.

## Repository Structure

- `projects/` contains hands-on builds and experiments
- `ai-tools-skills/` contains framework notes, definitions, comparisons, and implementation guidance

## Skills Covered

- `ai-tools-skills/Autogen-framework/` for Microsoft AutoGen concepts and multi-agent collaboration
- `ai-tools-skills/CrewAI-FrameWork/` for crews, flows, and agent orchestration
- `ai-tools-skills/LangGraph-Framework/` for graph-based orchestration and stateful agents
- `ai-tools-skills/MCP/` for the Model Context Protocol and tool/context interoperability
- `ai-tools-skills/N8N/` for low-code AI workflow automation
- `ai-tools-skills/RAG/` for retrieval-augmented generation patterns

## Project Roadmap

The next projects to grow into are deliberately aligned with modern agent engineering and DevOps workflows:

1. AI release notes agent
Turns GitHub pull requests, commits, and issue activity into structured release notes and deployment summaries.

2. CI failure triage agent
Reads failed GitHub Actions logs, classifies root cause, suggests remediation, and opens a draft issue.

3. DevOps runbook assistant with RAG
Indexes internal runbooks, incident notes, and service docs so an agent can answer operational questions with grounded citations.

4. Ticket review and triage agent
Reviews GitHub issues or Jira-style tickets, checks completeness, classifies the request, suggests priority, and recommends the next engineering action.

5. Incident response multi-agent system
Uses separate agents for log analysis, impact assessment, remediation suggestion, and stakeholder communication.

6. Change risk reviewer
Reviews infrastructure or application pull requests, flags risky changes, and suggests rollback or test plans before merge.

7. Workflow automation agent with n8n plus MCP
Connects tickets, email, calendars, docs, and internal APIs into a usable operational assistant.

## What "Good" Looks Like In This Repo

For each project I want to show:

- the problem being solved
- the agent design or workflow pattern used
- tools, memory, or retrieval strategy
- how the system is evaluated
- how it could be deployed or integrated into a DevOps workflow

## References

- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- CrewAI introduction: https://docs.crewai.com/en/introduction
- MCP architecture: https://modelcontextprotocol.io/docs/learn/architecture
- MCP specification overview: https://modelcontextprotocol.io/specification/2025-06-18/basic/index
- n8n advanced AI docs: https://docs.n8n.io/advanced-ai/
