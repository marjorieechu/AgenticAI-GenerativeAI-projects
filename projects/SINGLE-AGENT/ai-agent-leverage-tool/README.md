# AI Agent Leverage Tool

This project is about a single AI agent that becomes more useful by leveraging tools.

In this context, a tool is any capability the agent can call beyond plain text generation. Instead of answering only from its built-in model knowledge, the agent can reach outside itself to search the web, retrieve files, run code, or interact with connected systems.

That matters because a tool-using agent can:

- fetch fresher information
- ground answers in external data
- perform calculations instead of guessing
- combine search and reasoning in the same workflow
- handle tasks that a plain prompt-only agent cannot do reliably

## What Tool Use Means Here

For this project, tool use means the agent can decide when to call external functions or hosted OpenAI tools based on the user's request.

Examples:

- if the user asks for recent news, the agent should search
- if the user asks for calculations, the agent should run code
- if the user asks about stored documents, the agent should search indexed files
- if the task needs both recent information and analysis, the agent should combine tools

This is the key shift from a basic single agent to a more practical one: the model is no longer the only source of answers.

## Project Focus

This project explores two categories of tools:

1. External tools the developer wires in manually
2. Built-in tools already available through OpenAI

The main external tool in scope is Tavily for web search.

The main built-in OpenAI tools in scope are:

- `WebSearchTool`
- `FileSearchTool`
- `CodeInterpreterTool`
- `ImageGenerationTool`
- `HostedMCPTool`

Together, these give a strong baseline for building an agent that can search, retrieve, analyze, and respond more intelligently.

## Why This Project Matters

A tool-enabled agent is much closer to a real production workflow than a plain chatbot.

It demonstrates:

- decision-making about when to use tools
- safe separation between model reasoning and external actions
- better handling of live information
- a path from simple single-agent demos into richer research and operations assistants

## External Tool: Tavily

Tavily is used here as an external search tool that gives the agent reliable web access.

In this project, Tavily plays the role of:

- real-time search provider
- external source for current product, market, or news information
- function-based tool the agent can call when a question needs recent facts

Typical flow:

1. The user asks a question that needs recent information
2. The agent decides a web search is necessary
3. The Tavily tool is called with a search query and sends the request to the Tavily API
4. The search results are summarized and integrated into the final answer

This keeps the agent from pretending to know fresh information that it has not actually looked up.

## OpenAI Built-In Tools

OpenAI also provides built-in tools that can be attached directly to an agent.

### WebSearchTool

`WebSearchTool` lets the agent perform web searches without you writing a custom search function.

Use it when:

- the question is time-sensitive
- the answer depends on current events or live product information
- you want hosted search behavior managed through OpenAI

### FileSearchTool

`FileSearchTool` lets the agent retrieve information from indexed files or vector stores.

Use it when:

- you want the agent to answer from internal documents
- the task depends on notes, PDFs, manuals, or knowledge base files
- you want retrieval instead of open-web search

### CodeInterpreterTool

`CodeInterpreterTool` lets the agent execute code in a sandboxed environment.

Use it when:

- the task involves calculations
- you need data analysis
- the user wants simulations, tables, or transformations

This is especially useful when search gives raw numbers and the agent still needs to analyze them.

### ImageGenerationTool

`ImageGenerationTool` lets the agent create images from prompts.

Use it when:

- the task needs a generated visual
- you want diagrams, concepts, or creative outputs

### HostedMCPTool

`HostedMCPTool` lets the agent connect to tool surfaces exposed through MCP.

Use it when:

- the agent needs structured access to external systems
- you want a cleaner integration path than writing one-off tool functions for every service

## Example Tool Patterns

This project naturally supports a few common single-agent patterns.

### Search-Only Agent

The agent uses Tavily or `WebSearchTool` to answer current questions.

Good for:

- recent product information
- latest AI model discussions
- market headlines

### Search Plus Memory

The agent uses session memory so follow-up questions can reuse the earlier search context.

Good for:

- asking about a product first, then requesting a summary
- comparing a follow-up question to the earlier topic

### Search Plus Code

The agent uses web search for facts and `CodeInterpreterTool` for calculations or simulation.

Good for:

- pricing analysis
- market comparison
- percentage change scenarios

### Retrieval Plus Reasoning

The agent uses `FileSearchTool` to retrieve internal information and then explains it clearly.

Good for:

- company documents
- product manuals
- internal research notes

## Intended Project Scope

This project is meant to show how a single agent can:

- decide when tool use is necessary
- call an external search tool like Tavily
- leverage OpenAI built-in tools where appropriate
- combine search, memory, and code execution in one workflow
- produce better answers than a no-tool baseline

## Current Scaffold

This folder now includes a starter implementation with:

- `pyproject.toml` for project packaging and dependencies
- `src/ai_agent_leverage_tool/agent.py` for the OpenAI Agents SDK wrapper
- `src/ai_agent_leverage_tool/tools.py` for the Tavily function tool
- `src/ai_agent_leverage_tool/cli.py` for local execution
- `src/ai_agent_leverage_tool/models.py` for structured output
- `tests/test_agent.py` for local mocked tests

## Supported Tool Modes

The scaffold currently supports four modes:

### `tavily`

Uses a custom external function tool that calls Tavily search directly.

### `openai_web`

Uses OpenAI's hosted `WebSearchTool`.

### `hybrid`

Uses both:

- `WebSearchTool` for fresh information
- `CodeInterpreterTool` for calculations and simple analysis

### `file_search`

Uses `FileSearchTool` and requires one or more vector store ids.

This mode is scaffolded for later expansion and depends on you having vector store ids available.

## Environment Expectations

This project will likely require:

- `OPENAI_API_KEY`
- `TAVILY_API_KEY`

Depending on implementation, it may also use:

- local `.env` loading
- SQLite session memory
- Python requests or HTTP client utilities

The scaffold currently uses:

- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `TAVILY_API_KEY`

## Setup

PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_MODEL="gpt-5.4-mini"
$env:TAVILY_API_KEY="your_tavily_key_here"
```

Git Bash:

```bash
export OPENAI_API_KEY="your_api_key_here"
export OPENAI_MODEL="gpt-5.4-mini"
export TAVILY_API_KEY="your_tavily_key_here"
```

Install dependencies:

PowerShell:

```powershell
cd projects\SINGLE-AGENT\ai-agent-leverage-tool
pip install -e .
```

Git Bash:

```bash
cd projects/SINGLE-AGENT/ai-agent-leverage-tool
pip install -e .
```

## Quick Start

Run the Tavily-backed mode.

Requirements:

- `OPENAI_API_KEY`
- `TAVILY_API_KEY`

PowerShell:

```powershell
cd projects\SINGLE-AGENT\ai-agent-leverage-tool
$env:PYTHONPATH="src"
python -m ai_agent_leverage_tool.cli --mode tavily --clear-session --session-id tavily-demo --message "What are people saying about the latest GPT-5 model?" --pretty
```

Git Bash:

```bash
cd projects/SINGLE-AGENT/ai-agent-leverage-tool
PYTHONPATH=src python -m ai_agent_leverage_tool.cli --mode tavily --clear-session --session-id tavily-demo --message "What are people saying about the latest GPT-5 model?" --pretty
```

Run the built-in web search mode.

Requirements:

- `OPENAI_API_KEY`

Git Bash:

```bash
PYTHONPATH=src python -m ai_agent_leverage_tool.cli --mode openai_web --message "What are the latest announcements around OpenAI models?" --pretty
```

Run the hybrid mode.

Requirements:

- `OPENAI_API_KEY`

Git Bash:

```bash
PYTHONPATH=src python -m ai_agent_leverage_tool.cli --mode hybrid --message "Find the current base price of a Tesla Cybertruck, then estimate the price if tariffs rise from 5% to 20%." --pretty
```

Run the file search mode.

Requirements:

- `OPENAI_API_KEY`
- one or more vector store ids

Git Bash:

```bash
PYTHONPATH=src python -m ai_agent_leverage_tool.cli --mode file_search --vector-store-id vs_example123 --message "What does the internal product note say about battery range?" --pretty
```

## Traces And Logs

Tool-enabled agents are harder to reason about if you only look at the final answer. That is where traces and logs matter.

In this project, traces help you inspect:

- when the agent ran
- which workflow mode was active
- whether a tool call happened
- which tool path was used
- how the run moved from model reasoning into tool execution and back

The scaffold wraps runs with a workflow-level trace name and attaches metadata for the active tool mode.

That gives you a clearer debugging path when:

- the wrong tool was selected
- a tool call failed
- the answer was not grounded well enough
- a follow-up question did not use memory the way you expected

Practically, think of traces as execution visibility for agent workflows and logs as the record of what happened during the run.

## Sample Outputs

Two successful local runs have been captured for this project.

### Tavily Mode

[tavily-tool-run.png](/C:/Users/user/Documents/AGENTIC-AI/AgenticAI-GenerativeAI-projects/projects/SINGLE-AGENT/ai-agent-leverage-tool/tavily-tool-run.png)

This run demonstrates:

- Git Bash execution with `PYTHONPATH=src`
- external tool usage through Tavily
- structured output with `topic`, `answer`, `tool_strategy`, and `caveats`
- session-backed metadata including `mode`, `model`, `session_enabled`, `session_id`, and `trace_workflow`

### Hybrid Mode

[hybrid-tool-run.png](/C:/Users/user/Documents/AGENTIC-AI/AgenticAI-GenerativeAI-projects/projects/SINGLE-AGENT/ai-agent-leverage-tool/hybrid-tool-run.png)

This run demonstrates:

- hybrid tool use combining hosted web search and calculation support
- a practical pricing-style task instead of a simple lookup
- structured output that explains both the tool path and the caveats
- trace metadata showing the workflow executed in `hybrid` mode

## Local Verification

Run tests:

PowerShell:

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

Git Bash:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Example Use Cases

- a live market research agent
- a product comparison agent
- a vehicle review summarizer
- a pricing simulation assistant
- a current-events assistant that can search before answering

## What This Project Proves

- a single agent can become significantly more capable through tools
- external search improves freshness
- built-in tools reduce custom integration work
- code execution improves reliability for calculations
- tool orchestration is a practical next step after simple single-agent memory demos

## Recommended Next Steps

1. Run and capture a successful local example for each supported mode
2. Add session-memory demos that show follow-up behavior after a tool call
3. Add a no-tool baseline for comparison against the tool-enabled modes
4. Add output examples or screenshots to the README
5. Extend the hybrid mode with a stronger market or pricing workflow
