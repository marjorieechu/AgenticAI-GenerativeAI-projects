from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field


class SearchPlanItem(BaseModel):
    reason: str = Field(description="Why this search step is needed.")
    query: str = Field(description="The exact query to send to the search specialist.")


class SearchPlan(BaseModel):
    searches: list[SearchPlanItem] = Field(
        description="Two or three scoped search tasks for the research workflow."
    )


class GuardrailAssessment(BaseModel):
    blocked: bool = Field(description="Whether the request should be blocked.")
    category: str = Field(description="The policy category detected for the request.")
    reasoning: str = Field(description="Why the request was allowed or blocked.")


class SearchSummary(BaseModel):
    summary: str = Field(description="Concise search summary grounded in recent online information.")


class SentimentAnalysis(BaseModel):
    sentiment: str = Field(description="Overall market sentiment: positive, negative, or neutral.")
    summary: str = Field(description="Short explanation of the observed sentiment and why.")
    supporting_signals: list[str] = Field(
        description="Bullet-style signals supporting the sentiment classification."
    )


class FinalReport(BaseModel):
    short_summary: str = Field(description="Brief executive summary of the answer.")
    markdown_report: str = Field(description="Detailed markdown report for the user.")
    follow_up_questions: list[str] = Field(
        description="Follow-up questions that would deepen the research."
    )


class PlannerToWriterInput(BaseModel):
    original_query: str = Field(description="The original user query.")
    search_plan: SearchPlan = Field(description="The planner's structured search plan.")


@dataclass(frozen=True)
class WorkflowRunResult:
    mode: str
    user_query: str
    model: str
    workflow_name: str
    session_enabled: bool
    trace_hint: str
    final_output: dict[str, object]
    session_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "mode": self.mode,
            "user_query": self.user_query,
            "model": self.model,
            "workflow_name": self.workflow_name,
            "session_enabled": self.session_enabled,
            "session_id": self.session_id,
            "trace_hint": self.trace_hint,
            "final_output": self.final_output,
        }
