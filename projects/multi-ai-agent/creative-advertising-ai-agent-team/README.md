# Creative Advertising AI Agent Team

This project scaffolds the module 3 multi-agent exercise from the course materials into a repo-ready Python project.

It turns the notebook flow into a reusable pipeline where four specialized agents collaborate on a creative advertising task:

- `Creative_Director` brainstorms 3 to 5 campaign ideas
- `Strategist` selects the top 2 ideas and explains the reasoning
- `Copywriter` writes launch-ready tweets for the shortlisted campaigns
- `Channel_Planner` converts the winning campaign into channel-specific execution angles

## Why This Project

This is a stronger multi-agent example than a generic chat demo because each agent has a narrow responsibility and a clear handoff:

- ideation
- evaluation
- copy generation

That makes the orchestration pattern visible and easy to extend later with tools, guardrails, human review, or channel-specific output formats.

## Project Structure

- `pyproject.toml` defines packaging and dependencies
- `src/creative_advertising_ai_agent_team/agent.py` contains the multi-agent pipeline
- `src/creative_advertising_ai_agent_team/models.py` defines the structured outputs for each stage
- `src/creative_advertising_ai_agent_team/cli.py` runs the workflow locally
- `tests/test_agent.py` covers the pipeline with mocked OpenAI runner calls

## Environment Expectations

The scaffold uses the OpenAI Agents SDK and expects:

- `OPENAI_API_KEY`
- optionally `OPENAI_MODEL`

The included `.env.example` shows the expected variables.

## Setup

PowerShell:

```powershell
$env:OPENAI_API_KEY="your_api_key_here"
$env:OPENAI_MODEL="gpt-5.4-mini"
```

Install dependencies:

```powershell
cd projects\multi-ai-agent\creative-advertising-ai-agent-team
pip install -e .
```

## Quick Start

Run the multi-agent campaign pipeline:

```powershell
cd projects\multi-ai-agent\creative-advertising-ai-agent-team
$env:PYTHONPATH="src"
python -m creative_advertising_ai_agent_team.cli --clear-session --session-id bali-launch --prompt "Launch campaign for a new eco-friendly water bottle in Bali" --pretty
```

Export a live run into timestamped artifact files:

```powershell
python -m creative_advertising_ai_agent_team.cli --clear-session --session-id bali-launch --prompt "Launch campaign for a new eco-friendly water bottle in Bali" --pretty --export-dir samples
```

This writes:

- a raw JSON artifact for the full response
- a markdown summary artifact for quick review or sharing

## Sample Artifacts

The project now includes checked-in sample output files:

- [samples/bali-launch-output.json](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/creative-advertising-ai-agent-team/samples/bali-launch-output.json)
- [samples/bali-launch-summary.md](C:/Users/user/Documents/AGENTIC-AI/agentic-ai-devops-labs/projects/multi-ai-agent/creative-advertising-ai-agent-team/samples/bali-launch-summary.md)

These are useful when you want to review the structure of a full run without rerunning the pipeline.

## Example Output Shape

```json
{
  "product_prompt": "Launch campaign for a new eco-friendly water bottle in Bali",
  "ideas": [
    "Refill Rituals",
    "Bali Beach Clean Sip",
    "Carry Less Plastic"
  ],
  "top_campaigns": [
    "Refill Rituals",
    "Bali Beach Clean Sip"
  ],
  "reasoning": "These ideas are memorable, audience-relevant, and easy to activate on social.",
  "tweets": [
    "Refill your day, not the landfill.",
    "Hydrate in Bali with a bottle built for lighter footprints."
  ],
  "channel_plan": {
    "twitter": [
      "Use refill-station map drops and creator challenges."
    ],
    "linkedin": [
      "Frame the launch as a sustainability and tourism partnership play."
    ],
    "email": [
      "Send a refill-guide launch email with partner stops and rewards."
    ],
    "short_video": [
      "Show a full Bali day built around refill moments and low-waste travel."
    ]
  },
  "model": "gpt-5.4-mini",
  "workflow_name": "Creative Advertising AI Agent Team",
  "session_enabled": true,
  "session_id": "bali-launch"
}
```

## Verification

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -v
```

## Extension Ideas

Good next upgrades for this scaffold:

1. add a design-brief agent that turns the winning campaign into creative direction for visuals
2. add web search or file search tools so the strategist can ground decisions in market context
3. add approval checkpoints before social copy is generated
4. add export helpers that save the final plan as a pitch deck brief or campaign handoff document
