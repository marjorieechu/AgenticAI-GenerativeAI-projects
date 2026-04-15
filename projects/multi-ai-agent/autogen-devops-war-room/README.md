# AutoGen DevOps War Room

This project scaffolds an AutoGen group chat team in a DevOps context, following the later-stage learning pattern where multiple AI agents collaborate with a human participant.

Instead of a marketing team, this scaffold models a DevOps incident war room with:

- `Incident_Commander`
- `Release_Investigator`
- `Incident_Comms_Lead`
- `Human_Operator` through the AutoGen user proxy pattern

That gives you **3 AI agents plus 1 human**, which is the right shape for the later group chat stage.

## Why This Project

Group chat is a natural fit for DevOps work because incident handling is rarely a single-role problem.

In a realistic release or outage scenario, you often need:

- one role to coordinate the team
- one role to investigate deployment failure signals
- one role to convert technical findings into stakeholder communication
- one human who can approve, redirect, or stop the discussion

This scaffold reflects that pattern directly.

## AI Team Design

The project defines these three AI roles:

### `Incident_Commander`

- coordinates the response
- keeps the conversation focused
- pushes the team toward a go/no-go or hold decision

### `Release_Investigator`

- analyzes CI/CD and deployment failure symptoms
- proposes likely root causes and safe next debugging steps

### `Incident_Comms_Lead`

- drafts stakeholder-ready updates
- translates technical findings into operationally clear status language

### `Human_Operator`

- participates through AutoGen's user proxy pattern
- can guide, approve, or terminate the conversation

## Temperature Setting

This scaffold sets a **moderate temperature of `0.6`** for model clients.

That choice is intentional:

- lower than a highly creative setting
- high enough to avoid overly rigid or repetitive responses
- appropriate for incident discussion where some flexibility is useful but reliability matters more than novelty

This temperature is defined centrally in [config.py](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/autogen-devops-war-room/src/autogen_devops_war_room/config.py).

## What APIs Do You Need?

You do **not** need Gemini, GPT, and Claude all at once unless you explicitly want the mixed-model setup.

### Minimal Setup

To get started, you only need:

- `OPENAI_API_KEY`

That supports the `openai_only` mode, where all 3 AI agents use the same OpenAI model.

### Mixed-Model Setup

If you want the exact multi-model group chat pattern:

- `OPENAI_API_KEY` for `Release_Investigator`
- `OPENAI_API_KEY` for `Incident_Comms_Lead`
- `OPENAI_API_KEY` for `Incident_Commander` for now

At the moment, this scaffold is temporarily switched to OpenAI for all three AI roles because the Gemini quota in your environment is exhausted. The project structure is still set up so the commander role can be moved back to Gemini later.

So the practical answer is:

- `GPT` is enough to start
- `Gemini` can be reintroduced later for the commander when quota is available
- `Claude` is not required for this scaffold

## AutoGen Installation

Yes, you do need to install AutoGen packages.

This scaffold is built for the current package layout:

- `autogen-agentchat`
- `autogen-ext[openai]`
- `autogen-ext[anthropic]`

Install from the project folder:

```powershell
cd projects\multi-ai-agent\autogen-devops-war-room
pip install -e .
```

This project still includes the Anthropic extension in dependencies so the scaffold can be extended later, but the current mixed mode does not require an Anthropic key.

## Environment Variables

Minimal `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

Mixed-model `.env`:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
```

See [.env.example](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/autogen-devops-war-room/.env.example).

## Project Structure

- `pyproject.toml` defines dependencies and packaging
- `src/autogen_devops_war_room/config.py` defines team modes and temperature
- `src/autogen_devops_war_room/team.py` builds the AutoGen group chat team
- `src/autogen_devops_war_room/cli.py` runs the incident war room from the terminal
- `tests/test_config.py` checks configuration behavior
- `samples/devops-war-room-prompt.md` contains the example incident prompt

## Group Chat Pattern

This scaffold uses the AutoGen group chat pattern with a human component.

The intended flow is:

1. `Human_Operator` provides the incident scenario
2. `Incident_Commander` frames the discussion
3. `Release_Investigator` analyzes the technical issue
4. `Incident_Comms_Lead` drafts the stakeholder message
5. the human can intervene, refine, approve, or stop the process

That is the main reason this belongs in the multi-agent folder rather than as a simple assistant demo.

## Example Scenario

The sample prompt is:

`We have a production deployment failure after a GitHub Actions release. One migration failed, rollback safety is unclear, and leadership needs a quick operational update. Discuss the likely root cause, safe next action, and a concise stakeholder status note.`

See [samples/devops-war-room-prompt.md](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/autogen-devops-war-room/samples/devops-war-room-prompt.md).

## Sample Outputs

The project folder now includes screenshots from a live AutoGen run:

- [autogen-war-room-startup.png](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/autogen-devops-war-room/autogen-war-room-startup.png)
- [autogen-war-room-transcript.png](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/autogen-devops-war-room/autogen-war-room-transcript.png)

These screenshots demonstrate:

- the group chat startup flow
- the human operator being prompted for input
- the three AI agents responding in sequence
- the DevOps-focused transcript output instead of a marketing-style brainstorm

## Quick Start

Run the OpenAI-only team:

```powershell
cd projects\multi-ai-agent\autogen-devops-war-room
python -m autogen_devops_war_room.cli --team-mode openai_only
```

Run the mixed-model team:

```powershell
python -m autogen_devops_war_room.cli --team-mode mixed
```

Right now, `mixed` behaves as the intended later-stage team layout, but with the commander temporarily running on OpenAI until Gemini quota is restored.

Run with a fixed non-interactive human reply:

```powershell
python -m autogen_devops_war_room.cli --team-mode openai_only --auto-human-reply "Proceed with a conservative rollback recommendation."
```

## Verification

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

## Recommended Next Step

After this scaffold, the strongest next upgrade is:

1. add repo or CI log context as a tool input
2. let the investigator inspect structured failure artifacts
3. capture a sample transcript for the README
4. only then expand the team beyond 3 AI agents

## Portfolio Value

This project demonstrates:

- AutoGen group chat design
- human-in-the-loop orchestration
- a 3-agent team pattern
- optional multi-model composition
- a DevOps-focused adaptation of agent collaboration
