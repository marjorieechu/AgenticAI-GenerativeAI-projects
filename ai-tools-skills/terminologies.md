# AI Agent Terminologies

This document defines common terms used when discussing AI agents, agent workflows, and multi-agent systems.

## Node

A node is a single step or unit of work in an agent workflow. A node can represent an action such as calling an LLM, checking a condition, using a tool, retrieving data, writing to memory, or returning an output.

In graph-based agent systems, nodes are connected together so the agent can move from one step to the next.

## Schedule Node

A schedule node is a node responsible for running a task at a specific time, after a delay, or on a recurring interval.

Examples:
- Run an email summary every morning.
- Re-check a failed job after 10 minutes.
- Trigger a report every Friday.

In agent systems, schedule nodes are useful for automation, retries, recurring monitoring, and periodic tasks.

## Trigger Node

A trigger node is the starting point that activates a workflow when some event happens.

Common triggers include:
- A user sends a message.
- A webhook is received.
- A file is uploaded.
- A database record changes.
- A time-based event occurs.

A trigger node does not usually do the main work itself. Its purpose is to detect an event and start the process.

## Scale

Scale refers to the ability of an AI agent system to handle increasing demand, complexity, or workload without failing or becoming too slow.

Scaling can mean:
- Serving more users at the same time.
- Running more agents in parallel.
- Handling larger datasets or longer workflows.
- Expanding from one task to many related tasks.

In practice, scaling usually involves better infrastructure, queueing, batching, caching, and careful control of cost and latency.

## Memory

Memory is the information an AI agent keeps or can retrieve in order to behave more consistently across steps or over time.

Types of memory commonly discussed in agent systems:
- Short-term memory: context kept during the current conversation or workflow run.
- Long-term memory: information stored and reused across future sessions.
- Working memory: temporary state used while solving the current task.
- External memory: information stored outside the model, such as in a vector database, file, or database table.

Memory helps agents remember user preferences, prior decisions, task state, and relevant knowledge.

## LangChain

LangChain is a framework and ecosystem for building applications powered by large language models. It is commonly used to build AI agents, tool-using workflows, retrieval pipelines, and multi-step chains.

In agent contexts, LangChain is often used for:
- Connecting LLMs to tools and APIs.
- Managing prompts and message history.
- Building chains and agent workflows.
- Adding retrieval over documents or knowledge bases.
- Orchestrating multi-step reasoning and execution.

If you meant "longchain," the most likely intended term is "LangChain."

## Handoff

A handoff is the transfer of control, task ownership, or context from one agent, tool, or workflow step to another.

Examples:
- A triage agent hands off billing issues to a billing agent.
- A planner agent hands off execution to a tool-using worker agent.
- A chatbot hands off a conversation to a human support operator.

A good handoff includes enough context for the next agent or actor to continue without losing important information.

## Agent

An agent is an AI system that can perceive input, reason about what to do, and take actions toward a goal. Unlike a simple chatbot, an agent often has access to tools, memory, and multi-step workflows.

## Workflow

A workflow is the structured sequence of steps an agent or automation follows to complete a task. In many agent systems, workflows are represented as chains, graphs, or state machines.

## Tool

A tool is any external capability the agent can use beyond plain text generation. Examples include web search, calculators, databases, code execution, APIs, and file operations.

## Context

Context is the information available to the model at the moment it generates a response. This can include system instructions, chat history, retrieved documents, tool results, and memory.

## Orchestration

Orchestration is the logic that coordinates how different models, tools, nodes, and agents work together. It controls sequencing, branching, retries, and handoffs.

## Multi-Agent System

A multi-agent system is a setup where multiple AI agents work together, often with different roles, such as planning, research, execution, verification, or escalation.

## Retrieval-Augmented Generation (RAG)

RAG is a pattern where an agent retrieves relevant external information before generating a response. This helps the model answer with more accurate and task-specific knowledge.

## State

State is the current data describing where the agent is in a process. It can include inputs, outputs, progress markers, decisions made, and pending next steps.
