from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, Field


class CreativeIdeas(BaseModel):
    ideas: list[str] = Field(
        description="Three to five creative campaign concepts for the requested product or launch."
    )


class SelectedCampaigns(BaseModel):
    top_campaigns: list[str] = Field(
        description="The two campaign ideas judged most promising."
    )
    reasoning: str = Field(
        description="Brief explanation of why the selected ideas are strongest."
    )


class TweetCopy(BaseModel):
    tweets: list[str] = Field(
        description="Two to three launch-ready tweets for the shortlisted campaigns."
    )


class ChannelPlan(BaseModel):
    twitter: list[str] = Field(
        description="Recommended Twitter or X execution angles for the selected campaigns."
    )
    linkedin: list[str] = Field(
        description="Recommended LinkedIn post angles for the selected campaigns."
    )
    email: list[str] = Field(
        description="Recommended email campaign angles or subject-line directions."
    )
    short_video: list[str] = Field(
        description="Recommended short-video concepts for reels, TikTok, or shorts."
    )


@dataclass(frozen=True)
class PipelineRunResult:
    product_prompt: str
    ideas: list[str]
    top_campaigns: list[str]
    reasoning: str
    tweets: list[str]
    channel_plan: dict[str, list[str]]
    model: str
    workflow_name: str
    session_enabled: bool
    session_id: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "product_prompt": self.product_prompt,
            "ideas": self.ideas,
            "top_campaigns": self.top_campaigns,
            "reasoning": self.reasoning,
            "tweets": self.tweets,
            "channel_plan": self.channel_plan,
            "model": self.model,
            "workflow_name": self.workflow_name,
            "session_enabled": self.session_enabled,
            "session_id": self.session_id,
        }
