from __future__ import annotations

from dataclasses import dataclass
from pydantic import BaseModel, Field


class ToolAgentResult(BaseModel):
    topic: str = Field(description="The main subject of the answer.")
    answer: str = Field(description="The concise final answer returned to the user.")
    tool_strategy: str = Field(
        description="Short note describing which tool path the agent used or should have used."
    )
    caveats: str = Field(
        description="Limits, uncertainty, or grounding note for the answer."
    )


@dataclass(frozen=True)
class AgentRunResult:
    response: ToolAgentResult
    mode: str
    model: str
    session_enabled: bool
    trace_workflow: str
    session_id: str | None = None

    def to_dict(self) -> dict[str, str | bool | None | dict[str, str]]:
        return {
            "response": self.response.model_dump(),
            "mode": self.mode,
            "model": self.model,
            "session_enabled": self.session_enabled,
            "session_id": self.session_id,
            "trace_workflow": self.trace_workflow,
        }
