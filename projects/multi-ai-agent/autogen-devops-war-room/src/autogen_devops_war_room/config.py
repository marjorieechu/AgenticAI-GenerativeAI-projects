from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv


TeamMode = Literal["openai_only", "mixed"]
Provider = Literal["openai", "gemini", "anthropic"]
MODERATE_TEMPERATURE = 0.6


@dataclass(frozen=True)
class RoleModelConfig:
    role_name: str
    provider: Provider
    model: str
    env_var: str


def load_env() -> None:
    load_dotenv()


def supported_team_modes() -> tuple[str, str]:
    return ("openai_only", "mixed")


def effective_openai_model() -> str:
    configured = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if configured.startswith("gpt-5"):
        return "gpt-4o-mini"
    return configured


def role_layout(mode: TeamMode) -> list[RoleModelConfig]:
    if mode == "openai_only":
        return [
            RoleModelConfig("incident_commander", "openai", effective_openai_model(), "OPENAI_API_KEY"),
            RoleModelConfig("release_investigator", "openai", effective_openai_model(), "OPENAI_API_KEY"),
            RoleModelConfig("incident_comms_lead", "openai", effective_openai_model(), "OPENAI_API_KEY"),
        ]
    if mode == "mixed":
        return [
            RoleModelConfig("incident_commander", "openai", effective_openai_model(), "OPENAI_API_KEY"),
            RoleModelConfig("release_investigator", "openai", effective_openai_model(), "OPENAI_API_KEY"),
            RoleModelConfig("incident_comms_lead", "openai", effective_openai_model(), "OPENAI_API_KEY"),
        ]
    raise ValueError(f"Unsupported team mode: {mode}")


def validate_env_for_mode(mode: TeamMode) -> list[str]:
    missing: list[str] = []
    for item in role_layout(mode):
        if not os.getenv(item.env_var):
            missing.append(item.env_var)
    return sorted(set(missing))
