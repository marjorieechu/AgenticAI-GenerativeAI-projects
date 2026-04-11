from __future__ import annotations

import asyncio
import inspect
import os
from pathlib import Path

from agents import (
    Agent,
    CodeInterpreterTool,
    FileSearchTool,
    RunConfig,
    Runner,
    SQLiteSession,
    WebSearchTool,
    trace,
)
from dotenv import load_dotenv

from ai_agent_leverage_tool.models import AgentRunResult, ToolAgentResult
from ai_agent_leverage_tool.tools import tavily_search


DEFAULT_MODEL = "gpt-5.4-mini"
DEFAULT_MODE = "tavily"
DEFAULT_WORKFLOW_NAME = "AI Agent Leverage Tool"


def _instructions_for_mode(mode: str) -> str:
    common = """
Context:
You are a tool-using research assistant.

Instructions:
- Decide whether the request needs tool use or can be answered directly.
- Prefer grounded tool usage for fresh information, calculations, or document retrieval.
- Use prior conversation context when session memory is enabled.
- Do not claim to have searched or computed anything unless a tool was actually used.
- Keep the final answer concise and practical.

Output:
- Return structured output.
""".strip()

    if mode == "tavily":
        return common + "\n- Use the Tavily search tool when the question needs current web information."
    if mode == "openai_web":
        return common + "\n- Use the hosted web search tool when the question needs live web information."
    if mode == "hybrid":
        return common + "\n- Use hosted web search for fresh information and code interpreter for calculations or simulations."
    if mode == "file_search":
        return common + "\n- Use file search to answer from indexed files or vector stores."
    raise ValueError(f"Unsupported mode: {mode}")


class ToolEnabledAgent:
    def __init__(
        self,
        *,
        mode: str = DEFAULT_MODE,
        model: str | None = None,
        session_id: str = "tool_agent_demo",
        db_path: Path | str = Path("data/session.db"),
        stateless: bool = False,
        vector_store_ids: list[str] | None = None,
    ) -> None:
        load_dotenv()

        self.mode = mode
        self.model = model or os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
        self.session_id = session_id
        self.db_path = Path(db_path)
        self.stateless = stateless
        self.vector_store_ids = vector_store_ids or []
        self.workflow_name = f"{DEFAULT_WORKFLOW_NAME} ({self.mode})"

        self.session = None
        if not self.stateless:
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.session = SQLiteSession(session_id=self.session_id, db_path=str(self.db_path))

        self.agent = Agent(
            name=f"Tool Agent [{self.mode}]",
            instructions=_instructions_for_mode(self.mode),
            model=self.model,
            tools=self._build_tools(),
            output_type=ToolAgentResult,
        )

    def _build_tools(self) -> list[object]:
        if self.mode == "tavily":
            return [tavily_search]
        if self.mode == "openai_web":
            return [WebSearchTool()]
        if self.mode == "hybrid":
            return [
                WebSearchTool(),
                CodeInterpreterTool(
                    tool_config={"type": "code_interpreter", "container": {"type": "auto"}}
                ),
            ]
        if self.mode == "file_search":
            if not self.vector_store_ids:
                raise ValueError(
                    "file_search mode requires one or more vector store ids."
                )
            return [FileSearchTool(vector_store_ids=self.vector_store_ids)]
        raise ValueError(f"Unsupported mode: {self.mode}")

    def respond(self, user_input: str) -> AgentRunResult:
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError("OPENAI_API_KEY is required to run this project.")

        run_config = RunConfig(
            workflow_name=self.workflow_name,
            trace_metadata={"tool_mode": self.mode},
        )

        with trace(self.workflow_name, metadata={"tool_mode": self.mode}):
            result = Runner.run_sync(
                self.agent,
                user_input,
                session=self.session,
                run_config=run_config,
            )

        return AgentRunResult(
            response=result.final_output_as(ToolAgentResult),
            mode=self.mode,
            model=self.model,
            session_enabled=self.session is not None,
            session_id=self.session_id if self.session is not None else None,
            trace_workflow=self.workflow_name,
        )

    def clear_session(self) -> None:
        if self.session is not None:
            self._run_async(self.session.clear_session())

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
