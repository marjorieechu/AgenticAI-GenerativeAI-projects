from __future__ import annotations

import asyncio
import inspect
import os
from pathlib import Path

from agents import Agent, RunConfig, Runner, SQLiteSession, trace
from dotenv import load_dotenv

from creative_advertising_ai_agent_team.models import (
    ChannelPlan,
    CreativeIdeas,
    PipelineRunResult,
    SelectedCampaigns,
    TweetCopy,
)


DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_WORKFLOW_NAME = "Creative Advertising AI Agent Team"


class CreativeAdvertisingPipeline:
    def __init__(
        self,
        *,
        model: str | None = None,
        session_id: str = "creative_ad_team",
        db_path: Path | str = Path("data/session.db"),
        stateless: bool = False,
    ) -> None:
        load_dotenv()

        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.session_id = session_id
        self.db_path = Path(db_path)
        self.stateless = stateless
        self.workflow_name = DEFAULT_WORKFLOW_NAME

        self.session = None
        if not self.stateless:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.session = SQLiteSession(
                session_id=self.session_id,
                db_path=str(self.db_path),
            )

        self.creative_director = Agent(
            name="Creative_Director",
            instructions="""
Context:
You are a creative director at an advertising agency.

Instructions:
- Brainstorm 3 to 5 distinct campaign ideas for the given product or launch prompt.
- Keep ideas concrete, memorable, and easy for downstream agents to evaluate.
- Tailor the concepts to the audience, location, and product details in the prompt.

Output:
- Return only structured output.
""".strip(),
            model=self.model,
            output_type=CreativeIdeas,
        )
        self.strategist = Agent(
            name="Strategist",
            instructions="""
Context:
You are a marketing strategist evaluating campaign ideas.

Instructions:
- Select the top 2 campaign ideas with the strongest market potential.
- Prefer ideas that are differentiated, audience-relevant, and easy to execute.
- Explain the tradeoffs and why the selected ideas stand out.

Output:
- Return only structured output.
""".strip(),
            model=self.model,
            output_type=SelectedCampaigns,
        )
        self.copywriter = Agent(
            name="Copywriter",
            instructions="""
Context:
You are a copywriter creating launch-ready social content.

Instructions:
- Write 2 to 3 engaging tweets total for the selected campaign ideas.
- Make the copy concise, campaign-specific, and usable as a first-draft social post.
- Reflect the tone implied by the campaign concepts and launch prompt.

Output:
- Return only structured output.
""".strip(),
            model=self.model,
            output_type=TweetCopy,
        )
        self.channel_planner = Agent(
            name="Channel_Planner",
            instructions="""
Context:
You are a channel strategist translating campaign concepts into channel-specific execution.

Instructions:
- Use the selected campaigns and draft tweets to recommend next moves for four channels:
  Twitter/X, LinkedIn, email, and short-form video.
- Keep each recommendation concrete enough for a marketer to act on immediately.
- Align each channel angle to the campaign concepts and launch brief.

Output:
- Return only structured output.
""".strip(),
            model=self.model,
            output_type=ChannelPlan,
        )

    def run_campaign(self, product_prompt: str) -> PipelineRunResult:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required to run this project.")

        with trace(self.workflow_name, metadata={"pipeline": "creative_advertising"}):
            ideas_result = Runner.run_sync(
                self.creative_director,
                product_prompt,
                session=self.session,
                run_config=self._run_config("creative_director"),
            )
            ideas = ideas_result.final_output_as(CreativeIdeas).ideas

            strategist_result = Runner.run_sync(
                self.strategist,
                self._build_strategist_input(product_prompt, ideas),
                session=self.session,
                run_config=self._run_config("strategist"),
            )
            selected = strategist_result.final_output_as(SelectedCampaigns)

            copywriter_result = Runner.run_sync(
                self.copywriter,
                self._build_copywriter_input(product_prompt, selected.top_campaigns),
                session=self.session,
                run_config=self._run_config("copywriter"),
            )
            tweets = copywriter_result.final_output_as(TweetCopy).tweets

            channel_planner_result = Runner.run_sync(
                self.channel_planner,
                self._build_channel_planner_input(
                    product_prompt,
                    selected.top_campaigns,
                    tweets,
                ),
                session=self.session,
                run_config=self._run_config("channel_planner"),
            )
            channel_plan = channel_planner_result.final_output_as(ChannelPlan)

        return PipelineRunResult(
            product_prompt=product_prompt,
            ideas=ideas,
            top_campaigns=selected.top_campaigns,
            reasoning=selected.reasoning,
            tweets=tweets,
            channel_plan=channel_plan.model_dump(),
            model=self.model,
            workflow_name=self.workflow_name,
            session_enabled=self.session is not None,
            session_id=self.session_id if self.session is not None else None,
        )

    def clear_session(self) -> None:
        if self.session is not None:
            self._run_async(self.session.clear_session())

    def _run_config(self, stage: str) -> RunConfig:
        return RunConfig(
            workflow_name=self.workflow_name,
            trace_metadata={"pipeline": "creative_advertising", "stage": stage},
        )

    @staticmethod
    def _build_strategist_input(product_prompt: str, ideas: list[str]) -> str:
        formatted_ideas = "\n".join(f"- {idea}" for idea in ideas)
        return (
            f"Launch brief:\n{product_prompt}\n\n"
            f"Campaign ideas to evaluate:\n{formatted_ideas}"
        )

    @staticmethod
    def _build_copywriter_input(product_prompt: str, campaigns: list[str]) -> str:
        formatted_campaigns = "\n".join(f"- {campaign}" for campaign in campaigns)
        return (
            f"Launch brief:\n{product_prompt}\n\n"
            f"Selected campaigns:\n{formatted_campaigns}"
        )

    @staticmethod
    def _build_channel_planner_input(
        product_prompt: str,
        campaigns: list[str],
        tweets: list[str],
    ) -> str:
        formatted_campaigns = "\n".join(f"- {campaign}" for campaign in campaigns)
        formatted_tweets = "\n".join(f"- {tweet}" for tweet in tweets)
        return (
            f"Launch brief:\n{product_prompt}\n\n"
            f"Selected campaigns:\n{formatted_campaigns}\n\n"
            f"Draft tweets:\n{formatted_tweets}"
        )

    @staticmethod
    def _run_async(coro: object) -> object:
        if not inspect.isawaitable(coro):
            return coro
        try:
            return asyncio.run(coro)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
