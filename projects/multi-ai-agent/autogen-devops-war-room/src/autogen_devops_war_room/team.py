from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from autogen_devops_war_room.config import MODERATE_TEMPERATURE, RoleModelConfig, TeamMode, role_layout


@dataclass
class TeamBundle:
    team: object
    model_clients: list[object]


def build_team(
    mode: TeamMode,
    *,
    human_input_func: Callable[[str], str],
    max_rounds: int = 10,
) -> TeamBundle:
    from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
    from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
    from autogen_agentchat.teams import RoundRobinGroupChat

    layout = {item.role_name: item for item in role_layout(mode)}

    commander_client = _build_model_client(layout["incident_commander"])
    investigator_client = _build_model_client(layout["release_investigator"])
    comms_client = _build_model_client(layout["incident_comms_lead"])
    clients = [commander_client, investigator_client, comms_client]

    human_operator = UserProxyAgent(
        name="Human_Operator",
        description="The human incident owner who can guide or stop the discussion.",
        input_func=human_input_func,
    )

    incident_commander = AssistantAgent(
        name="Incident_Commander",
        model_client=commander_client,
        description="Coordinates the war-room discussion and pushes toward a go/no-go recommendation.",
        system_message="""
You are the Incident Commander in a DevOps war room.
Coordinate the team, keep the conversation focused, ask for clarification from the human when needed, and drive toward a clear decision.
Be concise and operationally minded.
""".strip(),
    )
    release_investigator = AssistantAgent(
        name="Release_Investigator",
        model_client=investigator_client,
        description="Investigates CI/CD and deployment failure signals.",
        system_message="""
You investigate release failures in CI/CD and production deployment workflows.
Focus on evidence, likely root causes, dependency chains, deployment blockers, and safe next debugging steps.
""".strip(),
    )
    incident_comms_lead = AssistantAgent(
        name="Incident_Comms_Lead",
        model_client=comms_client,
        description="Produces stakeholder-ready communication and status phrasing.",
        system_message="""
You translate technical incident analysis into clear stakeholder communication.
Summarize impact, current status, mitigation posture, and the next update in calm, precise language.
""".strip(),
    )

    termination = MaxMessageTermination(max_rounds) | TextMentionTermination("WAR_ROOM_COMPLETE")
    team = RoundRobinGroupChat(
        participants=[
            human_operator,
            incident_commander,
            release_investigator,
            incident_comms_lead,
        ],
        termination_condition=termination,
    )
    return TeamBundle(team=team, model_clients=clients)


def _build_model_client(config: RoleModelConfig) -> object:
    import os

    if config.provider == "openai":
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        return OpenAIChatCompletionClient(
            model=config.model,
            api_key=os.getenv(config.env_var),
            temperature=MODERATE_TEMPERATURE,
        )

    if config.provider == "gemini":
        from autogen_core.models import ModelFamily
        from autogen_ext.models.openai import OpenAIChatCompletionClient

        return OpenAIChatCompletionClient(
            model=config.model,
            api_key=os.getenv(config.env_var),
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
            model_info={
                "vision": False,
                "function_calling": True,
                "json_output": True,
                "structured_output": True,
                "family": ModelFamily.GEMINI_2_0_FLASH,
            },
            temperature=MODERATE_TEMPERATURE,
        )

    if config.provider == "anthropic":
        from autogen_ext.models.anthropic import AnthropicChatCompletionClient

        return AnthropicChatCompletionClient(
            model=config.model,
            api_key=os.getenv(config.env_var),
            temperature=MODERATE_TEMPERATURE,
        )

    raise ValueError(f"Unsupported provider: {config.provider}")
