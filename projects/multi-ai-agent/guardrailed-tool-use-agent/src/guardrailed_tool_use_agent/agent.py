from __future__ import annotations

import asyncio
import inspect
import os
from datetime import datetime
from pathlib import Path

from agents import (
    Agent,
    GuardrailFunctionOutput,
    RunConfig,
    RunContextWrapper,
    RunResult,
    Runner,
    SQLiteSession,
    TResponseInputItem,
    handoff,
    input_guardrail,
    trace,
)
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from dotenv import load_dotenv

from guardrailed_tool_use_agent.models import (
    FinalReport,
    GuardrailAssessment,
    PlannerToWriterInput,
    SearchPlan,
    SearchPlanItem,
    SearchSummary,
    SentimentAnalysis,
    WorkflowRunResult,
)
from guardrailed_tool_use_agent.tools import tavily_search


DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_WORKFLOW_NAME = "Guardrailed Tool Use Agent"


def _today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


async def extract_search_summary(run_result: RunResult) -> str:
    final_output = run_result.final_output
    if isinstance(final_output, SearchSummary):
        return final_output.summary
    if isinstance(final_output, SentimentAnalysis):
        signals = "\n".join(f"- {signal}" for signal in final_output.supporting_signals)
        return (
            f"Sentiment: {final_output.sentiment}\n"
            f"Summary: {final_output.summary}\n"
            f"Signals:\n{signals}"
        )
    return str(final_output)


class GuardrailedSentimentWorkflow:
    def __init__(
        self,
        *,
        model: str | None = None,
        session_id: str = "guardrailed_sentiment_demo",
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
            self.session = SQLiteSession(session_id=self.session_id, db_path=str(self.db_path))

        self.guardrail_agent = Agent(
            name="SensitiveAccessGuardrail",
            instructions="""
Context:
You classify whether a request should be blocked before any search or external tool use.

Instructions:
- Block requests involving military, defense, weapons, politics, elections, salaries, secrets, credentials, or clearly sensitive private information.
- Allow normal company sentiment or market research questions.
- Return a short reasoning note either way.
""".strip(),
            model=self.model,
            output_type=GuardrailAssessment,
        )

        @input_guardrail
        async def sensitive_access_guardrail(
            ctx: RunContextWrapper[None],
            agent: Agent,
            input: str | list[TResponseInputItem],
        ) -> GuardrailFunctionOutput:
            result = await Runner.run(self.guardrail_agent, input, context=ctx.context)
            return GuardrailFunctionOutput(
                output_info=result.final_output,
                tripwire_triggered=result.final_output.blocked,
            )

        self.sensitive_access_guardrail = sensitive_access_guardrail

        self.search_agent = Agent(
            name="SearchAgent",
            instructions=f"""
Current date: {_today()}

Context:
You are a search specialist agent that owns the Tavily tool.

Instructions:
- Use Tavily to search for the most recent relevant information.
- Stay within the query scope you are given.
- Return a concise factual summary grounded in the search results.
""".strip(),
            model=self.model,
            tools=[tavily_search],
            output_type=SearchSummary,
        )

        self.sentiment_agent = Agent(
            name="SentimentAgent",
            instructions=f"""
Current date: {_today()}

Context:
You are a market sentiment analyst specializing in current public sentiment about companies.

Instructions:
- Determine whether sentiment is positive, negative, or neutral.
- Use the nested search specialist when fresh online information is needed.
- Consider signals from recent news, analyst commentary, and market discussion.
- Keep the result concise and evidence-based.
""".strip(),
            model=self.model,
            output_type=SentimentAnalysis,
            tools=[
                self.search_agent.as_tool(
                    "search_company_sentiment",
                    "Search for recent online information relevant to company sentiment.",
                    custom_output_extractor=extract_search_summary,
                )
            ],
        )

        self.writer_agent = Agent(
            name="Writer",
            instructions=f"""
Current date: {_today()}

Context:
You are an expert market research writer preparing a concise but grounded report.

Instructions:
- You may use SentimentAgent when the request asks for market sentiment or when it would materially improve the answer.
- Summarize the result objectively and clearly.
- Explain what kind of information was accessed.
- Write a professional markdown report and include follow-up questions.

Tools:
- sentiment: Use the SentimentAgent to analyze current company sentiment.
""".strip(),
            model=self.model,
            output_type=FinalReport,
            tools=[
                self.sentiment_agent.as_tool(
                    "sentiment",
                    "Analyze recent company sentiment using the specialist sentiment agent.",
                    custom_output_extractor=extract_search_summary,
                )
            ],
        )

        self.planner_agent = Agent(
            name="Planner",
            instructions=f"""
Current date: {_today()}

Context:
You are a guarded research planner.

Instructions:
- For an allowed company research request, break the task into 2 or 3 focused search items.
- Keep the plan tightly scoped to the user's request.
- Do not plan any access beyond public web information.
""".strip(),
            model=self.model,
            output_type=SearchPlan,
            input_guardrails=[self.sensitive_access_guardrail],
        )

        def on_planner_to_writer(
            ctx: RunContextWrapper[None],
            input_data: PlannerToWriterInput,
        ) -> None:
            _ = (ctx, input_data)

        self.handoff_to_writer = handoff(
            agent=self.writer_agent,
            input_type=PlannerToWriterInput,
            on_handoff=on_planner_to_writer,
            tool_name_override="transfer_to_writer",
            tool_description_override="Transfer the original query and scoped search plan to Writer.",
        )

        self.planner_with_handoff = self.planner_agent.clone(
            instructions=(
                f"{RECOMMENDED_PROMPT_PREFIX}\n\n"
                f"{self.planner_agent.instructions}\n\n"
                "When the SearchPlan is ready, call the handoff tool "
                "`transfer_to_writer` with JSON shaped like "
                "{ original_query: <user query>, search_plan: <SearchPlan> }."
            ),
            handoffs=[self.handoff_to_writer],
        )

    def run_writer_handoff(self, user_query: str) -> WorkflowRunResult:
        return self._run_mode(
            mode="writer_handoff",
            starting_agent=self.planner_with_handoff,
            user_query=user_query,
            trace_metadata={"entrypoint": "planner", "guardrails": "enabled"},
        )

    def run_sentiment_only(self, user_query: str) -> WorkflowRunResult:
        return self._run_mode(
            mode="sentiment_only",
            starting_agent=self.sentiment_agent,
            user_query=user_query,
            trace_metadata={"entrypoint": "sentiment_agent", "guardrails": "writer_bypass"},
        )

    def clear_session(self) -> None:
        if self.session is not None:
            self._run_async(self.session.clear_session())

    def _run_mode(
        self,
        *,
        mode: str,
        starting_agent: Agent,
        user_query: str,
        trace_metadata: dict[str, str],
    ) -> WorkflowRunResult:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required to run this project.")

        run_config = RunConfig(workflow_name=self.workflow_name, trace_metadata=trace_metadata)
        with trace(self.workflow_name, metadata=trace_metadata):
            result = Runner.run_sync(
                starting_agent,
                user_query,
                session=self.session,
                run_config=run_config,
            )

        final_output = result.final_output
        if hasattr(final_output, "model_dump"):
            payload = final_output.model_dump()
        else:
            payload = {"value": str(final_output)}

        return WorkflowRunResult(
            mode=mode,
            user_query=user_query,
            model=self.model,
            workflow_name=self.workflow_name,
            session_enabled=self.session is not None,
            session_id=self.session_id if self.session is not None else None,
            trace_hint=(
                "Review OpenAI platform traces for the handoff chain "
                "Planner -> Writer -> SentimentAgent -> SearchAgent -> Tavily."
            ),
            final_output=payload,
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
