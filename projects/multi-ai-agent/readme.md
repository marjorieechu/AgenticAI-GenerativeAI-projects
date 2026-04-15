# Multi-AI-Agent

These projects explore how more than one agent can collaborate on a task.

It builds on the single-agent baseline and moves toward orchestration patterns where agents can divide responsibilities, exchange outputs, and complete a workflow together.

## Goal

Experiment with multi-agent coordination and understand when multiple specialized agents are better than one general agent.

## Focus Areas

- task decomposition
- role specialization
- handoffs between agents
- response aggregation
- limits of naive multi-agent setups

## Why This Project Matters

A multi-agent system is not automatically better than a single agent. This project helps answer practical questions such as:

- when should work be split across agents
- how should responsibilities be assigned
- how does context move between agents
- what kind of orchestration is needed to keep output coherent

## Current Direction

This is still an early-stage project. The main value right now is understanding the pattern, not claiming production readiness.

## Available Scaffolds

- `ci-failure-triage-agent` for a structured DevOps-oriented multi-step analysis workflow
- `creative-advertising-ai-agent-team` for a role-based marketing pipeline with idea generation, campaign selection, and copywriting
- `guardrailed-tool-handoff-agent` for an access-controlled workflow where an agent decides when to use search or external tools without overreaching into sensitive information
- `autogen-devops-war-room` for a three-agent AutoGen group chat with a human operator in a DevOps incident-response context
- `autogen-devops-war-room` for an AutoGen group chat incident-response team that includes a human operator and optional mixed-model roles

## Good Next Upgrade Paths

1. Add a planner agent and a worker agent
2. Introduce structured outputs between agents
3. Add tool access for one or more agents
4. Add memory or retrieval for shared context
5. Rebuild the flow using LangGraph or CrewAI for stronger orchestration

## Portfolio Value

This project helps transition from prompt-based experiments into actual agent system design.
