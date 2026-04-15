# Guardrailed Tool Use Agent

This project is a scaffold for a guarded multi-agent workflow where a planner hands off to a writer, the writer can use a `SentimentAgent` as a tool, and the `SentimentAgent` can in turn use a specialist `SearchAgent` that owns Tavily search.

The central idea is not just "give the agent tools." It is "give the agent controlled discretion."

The overall system should be capable of:

- deciding when a prompt needs live search instead of model-only reasoning
- choosing when document retrieval or file access is appropriate
- recognizing when a request should remain local and not trigger any external access
- refusing or escalating requests that cross policy boundaries
- handing off only the minimum necessary context from one agent to the next

## Current Scaffold

This folder now includes a runnable scaffold with:

- `Planner` protected by an input guardrail
- `Writer` as the final report owner
- `SentimentAgent` exposed to `Writer` as an agent-tool
- `SearchAgent` nested under `SentimentAgent` as the search specialist
- Tavily wrapped so the raw search capability is not broadly exposed across the workflow
- session-backed runs and OpenAI trace-friendly workflow metadata

The example prompt in scope is:

- `What is the current market sentiment about Tesla?`

## Why This Project Matters

Tool-using agents become more useful, but they also become riskier.

Once an agent can access the web, internal files, tickets, databases, or connected systems, the problem changes from answer quality alone to decision quality and access governance.

This project is valuable because it explores a real production concern:

- how to let an agent act intelligently without letting it overreach

That makes it a strong multi-agent workflow project for security-conscious and enterprise-oriented environments.

## Core Problem

An agent may receive prompts such as:

- "Search the latest competitor pricing and summarize it."
- "Pull internal customer complaint data and identify trends."
- "Check the onboarding folder and tell me what legal terms are missing."
- "Look up my teammate's salary history and compare it to others."

Some of these requests are appropriate.
Some need restricted access.
Some should be denied entirely.

The system must therefore solve two tasks at once:

1. choose the right tool path
2. apply policy before any access happens

## Project Goal

Design a multi-agent workflow where tool selection is dynamic, but access is governed by clear rules and explicit handoffs.

The target behavior is:

- the agent can search or retrieve when the prompt justifies it
- the agent can explain why a tool is needed
- the agent only accesses approved data sources
- the agent blocks or escalates disallowed requests
- the final answer is grounded without violating privacy, scope, or safety policy
- each agent receives only the context it needs for its step

## Example Agent Roles And Handoffs

A strong multi-agent version should include:

- `Intent_Classifier` to determine whether the prompt requires external access
- `Policy_Guardrail` to classify the request as allowed, restricted, or blocked
- `Tool_Router` to choose web search, file search, database retrieval, or no tool use
- `Responder` to generate the final answer with a clear explanation of what was accessed

In the scaffolded version here, that idea is implemented more concretely as:

- `Planner` for scoped planning and guarded entry
- `Writer` for final synthesis
- `SentimentAgent` for company sentiment analysis
- `SearchAgent` for nested web search

This split is useful because it separates reasoning about the task from reasoning about access control.

Example handoff chain:

1. `Intent_Classifier` receives the raw user prompt and outputs:
   `tool_needed`, `requested_data_type`, `sensitivity_guess`, and `reason_for_access`
2. `Policy_Guardrail` receives only that structured intent summary, not full unrestricted system context, and returns:
   `decision`, `allowed_scope`, `blocked_scope`, `needs_approval`, and `guardrail_note`
3. `Tool_Router` receives the policy decision plus the minimum usable task context and returns:
   `selected_tool`, `tool_input`, and `access_scope`
4. `Responder` receives the tool result plus the policy note and produces:
   `response` and `audit_note`

The key point is that not every agent needs direct access to the full prompt, full workspace, or raw sensitive data.

In practice, the handoff is usually implemented by defining the next receiving agent explicitly and passing control to that agent with a narrowed prompt or structured payload. In other words, the next step is not just "call another function." It is "handoff to another agent definition that now becomes responsible for the next part of the workflow."

That means you can think of handoff as:

- the first agent receives the original prompt
- the next agent receives a transformed or narrowed version of that prompt
- the receiving agent works as the new prompt owner for its step

This is close to creating a prompt-specific continuation for the next agent, but it should not be treated as a blind clone of the original receiver. The important design choice is that the receiving agent should get only the scoped context it actually needs.

## Implementation Guide

If you build this with the OpenAI Agents SDK, the implementation would usually revolve around a few key imports and concepts:

- `Agent` for defining each specialized agent
- `Runner` for executing the workflow
- `handoff` or handoff configuration for passing work from one agent to another
- `input_guardrails` for validating or blocking requests before they reach tool-calling stages
- structured output models so each handoff passes controlled, predictable fields

The scaffold in this folder follows that pattern directly:

- `Planner` uses an `input_guardrail`
- the planner-to-writer transition is defined with `handoff(...)`
- the `Planner` is cloned into a prompt-aware handoff version with `planner.clone(...)`
- `SentimentAgent` is exposed to `Writer` with `.as_tool(...)`
- `SearchAgent` is exposed to `SentimentAgent` with `.as_tool(...)`
- Tavily stays nested under `SearchAgent`

It is also valid to treat a tool capability as its own specialist agent instead of attaching it directly as a tool to every other agent.

For example:

- a `Search_Agent` can own the web search capability
- a `Retriever_Agent` can own approved file or document lookup
- another agent can hand off to those agents only after policy approval

This pattern is useful when you want search or retrieval to be mediated by a dedicated agent role rather than exposing the raw tool broadly across the workflow.

If you use an external tool such as Tavily, one good pattern is to nest it under a specialist `Search_Agent`. That agent owns the Tavily integration, receives only approved search inputs, and returns a structured summary to the rest of the workflow.

That is the pattern implemented in this scaffold:

- `Writer` does not call Tavily directly
- `SentimentAgent` does not own raw Tavily directly
- `SearchAgent` owns Tavily
- `SentimentAgent` calls `SearchAgent`
- `Writer` calls `SentimentAgent`

In practical terms, the implementation would look something like this at the design level:

1. import the SDK primitives for agent definitions, handoffs, and guardrails
2. define typed models for:
   `IntentRequest`, `PolicyDecision`, `ToolSelection`, and `FinalResponse`
3. attach an input guardrail before tool selection so prompts are screened for restricted or blocked access
4. configure handoffs so:
   `Intent_Classifier -> Policy_Guardrail -> Tool_Router -> Responder`
5. ensure only the approved scope is passed into any tool-enabled stage

The important part is that `input_guardrails` should act before retrieval or search happens, and handoff definitions should restrict what context moves between agents.

## Tool-As-Agent Pattern

In some implementations, the best pattern is not:

- one main agent with direct access to every tool

Instead, it can be:

- one agent decides whether search is needed
- one policy agent approves scope
- one specialist search agent performs the search
- one responder agent turns the result into the final answer

That means a search tool can effectively be wrapped by a `Search_Agent` and made available to another agent through handoff rather than through unrestricted direct tool access.

Example:

- `Intent_Classifier` decides the prompt needs fresh information
- `Policy_Guardrail` approves public web search only
- `Tool_Router` hands off to `Search_Agent`
- `Search_Agent` performs the approved search and returns a structured summary
- `Responder` uses that summary to answer the user

This approach is often safer because:

- fewer agents have direct tool permissions
- search behavior can be isolated and audited
- retrieval prompts can be standardized
- guardrails can sit in front of specialist access agents

## Traces And Visibility

This kind of project should also make use of traces on the OpenAI platform so you can see how the workflow actually behaved.

Traces are especially useful here because they let you inspect:

- which agent received the original prompt
- when a handoff happened from one agent to another
- whether the guardrail step allowed, restricted, or blocked access
- whether a specialist `Search_Agent` was invoked
- whether a tool such as Tavily was used underneath that search agent
- how the final answer was grounded

In a guarded workflow, traces help answer questions like:

- did the search request go through `Policy_Guardrail` first
- did `Tool_Router` hand off to `Search_Agent` or choose no tool at all
- was Tavily used only after the allowed scope was approved
- did the responder get a filtered summary instead of raw sensitive output

This matters because the value of the project is not only the final answer. It is also the visibility of the decision path.

For example, a good trace might show:

1. user prompt enters `Intent_Classifier`
2. handoff to `Policy_Guardrail`
3. policy decision returns `allowed` for public web search only
4. handoff to `Tool_Router`
5. handoff to `Search_Agent`
6. Tavily runs inside `Search_Agent`
7. structured results return to `Responder`
8. final answer is generated with an audit note

That kind of trace makes it much easier to prove that the workflow used guarded search rather than uncontrolled search.

For the scaffold in this folder, the trace tree you should expect for the Tesla example is:

1. `Planner`
2. `Writer`
3. `SentimentAgent`
4. `SearchAgent`
5. `tavily_search`

This shows:

- the planner entrypoint
- the planner-to-writer handoff
- `SentimentAgent` being used as a tool by `Writer`
- `SearchAgent` acting as a nested specialist search agent
- Tavily running at the lowest level of the tree

## Suggested SDK-Level Components

The scaffold guide should assume components like:

- an `Intent_Classifier` agent with structured output and no direct tool access
- a `Policy_Guardrail` step using input guardrails to block or narrow unsafe requests
- a `Tool_Router` agent that is only allowed to call approved external tools or hand off to specialist access agents such as `Search_Agent`
- a `Search_Agent` that owns a search integration such as Tavily and only accepts policy-approved search requests
- a `Responder` agent that receives the filtered result and writes the final answer

That means this project is not just about prompting multiple agents. It is about combining:

- handoff design
- guardrail enforcement
- scoped tool access
- trace visibility
- structured outputs between steps

## Guardrail Design

The strongest version of this project should define explicit policies before implementation.

Examples:

### Allowed

- public web search for current information
- retrieval from approved internal documents
- access to project files inside a permitted workspace
- querying a knowledge base that is already approved for the agent

### Restricted

- customer data containing personal information
- finance records
- employee records
- private support tickets
- internal documents outside the assigned scope

Restricted requests may require:

- redaction
- approval
- narrower filtering
- audit logging
- human review

### Blocked

- salary lookups without authorization
- requests for secrets, tokens, or credentials
- broad exfiltration requests
- unrelated sensitive file access
- policy-violating surveillance or monitoring requests

## Example Workflow

A practical pipeline could look like this:

1. User sends a prompt
2. `Intent_Classifier` decides whether the task needs a tool
3. `Intent_Classifier` hands off a structured access request to `Policy_Guardrail`
4. `Policy_Guardrail` checks whether the requested access is allowed
5. If allowed, `Policy_Guardrail` hands off an approved scope to `Tool_Router`
6. If restricted, the workflow asks for approval or narrows the request before any tool call happens
7. If blocked, the workflow refuses and explains why
8. `Tool_Router` calls the approved tool path and hands the result to `Responder`
9. `Responder` returns a grounded answer plus an access summary

## Handoff Rules

To keep the workflow safe, handoffs should follow explicit constraints:

- pass structured summaries instead of raw chain-of-thought
- pass approved scope, not blanket access
- redact or omit sensitive fields before downstream handoff
- attach a short audit note to each policy-sensitive transition
- prevent tool-calling agents from bypassing the `Policy_Guardrail` step
- require re-evaluation if a downstream agent wants broader access than originally approved

## What The Output Should Include

A strong structured output for this project might contain:

- `decision`: allowed, restricted, or blocked
- `tool_needed`: yes or no
- `selected_tool`: web_search, file_search, database_query, none
- `access_scope`: what data source was used or approved
- `reasoning`: short explanation of why this path was chosen
- `response`: the final user-facing answer
- `audit_note`: short note describing what access happened or why it was denied

## Good Guardrail Behaviors

The agent team should:

- avoid searching when the answer can be handled locally
- avoid claiming to have accessed data when it did not
- limit retrieval to the smallest relevant scope
- explain refusals in plain language
- log or summarize sensitive access decisions for auditability
- enforce that every tool call comes after a policy-approved handoff

## Failure Modes To Avoid

This project should explicitly guard against:

- unnecessary web searches
- over-broad file retrieval
- access to irrelevant internal information
- leaking sensitive material into final answers
- pretending a request is allowed without policy evaluation
- using tools before policy review has completed
- passing raw sensitive outputs between agents when a smaller structured summary would be enough

## Why This Fits The Multi-Agent Folder

This is a strong multi-agent project because the challenge is not just answering the question. The challenge is coordinating:

- task understanding
- policy enforcement
- tool routing
- controlled handoffs
- grounded response generation

That makes it a better fit for orchestration than a basic single-agent demo.

## Project Structure

- `pyproject.toml` defines packaging and dependencies
- `src/guardrailed_tool_use_agent/agent.py` contains the guarded multi-agent workflow
- `src/guardrailed_tool_use_agent/tools.py` contains the Tavily tool wrapper
- `src/guardrailed_tool_use_agent/models.py` defines structured outputs and handoff payloads
- `src/guardrailed_tool_use_agent/cli.py` runs the workflow locally
- `tests/test_agent.py` covers the scaffold with mocked OpenAI runs
- `samples/tesla-sentiment-example.md` documents the intended trace tree

## Trace Screenshots

The folder also includes OpenAI platform trace screenshots captured from a live Tesla sentiment run:

- [trace-planner-writer.png](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/guardrailed-tool-use-agent/trace-planner-writer.png)
- [trace-sentiment-agent.png](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/guardrailed-tool-use-agent/trace-sentiment-agent.png)
- [trace-search-agent.png](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/guardrailed-tool-use-agent/trace-search-agent.png)

These screenshots should help confirm:

- the planner-to-writer handoff occurred
- `Writer` used `SentimentAgent` as a tool
- `SentimentAgent` invoked `SearchAgent`
- the lowest-level search activity ran under the nested search path rather than being exposed directly to the top-level writer

## Setup

PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_MODEL="gpt-5.4-mini"
$env:TAVILY_API_KEY="your_tavily_key_here"
```

Install dependencies:

```powershell
cd projects\multi-ai-agent\guardrailed-tool-use-agent
pip install -e .
```

## Quick Start

Run the full guarded handoff workflow:

```powershell
cd projects\multi-ai-agent\guardrailed-tool-use-agent
$env:PYTHONPATH="src"
python -m guardrailed_tool_use_agent.cli --mode writer_handoff --clear-session --session-id tesla-guarded --prompt "What is the current market sentiment about Tesla?" --pretty
```

Run the sentiment specialist directly:

```powershell
$env:PYTHONPATH="src"
python -m guardrailed_tool_use_agent.cli --mode sentiment_only --prompt "What is the current market sentiment about Tesla?" --pretty
```

## Verification

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

## Recommended Next Step

The best implementation path after this scaffold is:

1. strengthen the guardrail categories and refusal language
2. add a second restricted-access source beyond public web search
3. log structured audit notes for each policy-sensitive step
4. capture and document one successful Tesla trace from the OpenAI platform

## Notes For The Guide

Because this README is meant as an implementation guide and not a finished scaffold, it should be read as:

- what agents to create
- where to place handoffs
- where to attach `input_guardrails`
- where a search tool can be wrapped by a `Search_Agent`
- how traces should reveal the guardrail and handoff flow
- how to keep tool access scoped and policy-aware

It is now also a repo scaffold guide for a concrete example:

- planner handoff to writer
- writer calling `SentimentAgent` as a tool
- `SentimentAgent` calling `SearchAgent` as a tool
- `SearchAgent` calling Tavily
- traces showing the nested chain clearly

The actual function names can vary slightly depending on the SDK version you use, but the implementation pattern should stay the same:

- guardrail first
- handoff second
- tool call third
- response generation last

## Portfolio Value

This project demonstrates:

- practical tool-routing design
- AI guardrail thinking beyond generic safety language
- controlled autonomy
- explicit multi-agent handoff design
- trace-aware workflow observability
- explainable access decisions
- a realistic path toward enterprise-grade agent systems
