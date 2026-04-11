from __future__ import annotations

import os
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch

from ai_agent_leverage_tool.agent import ToolEnabledAgent
from ai_agent_leverage_tool.models import ToolAgentResult


class ToolEnabledAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ.pop("OPENAI_MODEL", None)

    def tearDown(self) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL", None)

    @patch("ai_agent_leverage_tool.agent.load_dotenv")
    @patch("ai_agent_leverage_tool.agent.SQLiteSession")
    @patch("ai_agent_leverage_tool.agent.Runner.run_sync")
    def test_tavily_mode_uses_session_and_returns_structured_result(
        self,
        mock_run_sync: MagicMock,
        mock_sqlite_session: MagicMock,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        mock_sqlite_session.return_value = MagicMock()
        run_result = MagicMock()
        run_result.final_output_as.return_value = ToolAgentResult(
            topic="Tesla",
            answer="Tesla remains the active topic.",
            tool_strategy="Used Tavily search for current information.",
            caveats="Search-based summary; verify exact figures from primary sources.",
        )
        mock_run_sync.return_value = run_result

        agent = ToolEnabledAgent(
            mode="tavily",
            session_id="tool-demo",
            db_path=Path("tests/.tmp/session.db"),
        )
        result = agent.respond("What are reviewers saying about Tesla today?")

        self.assertEqual(result.mode, "tavily")
        self.assertTrue(result.session_enabled)
        self.assertEqual(result.session_id, "tool-demo")
        self.assertEqual(result.response.topic, "Tesla")
        self.assertEqual(result.trace_workflow, "AI Agent Leverage Tool (tavily)")

    @patch("ai_agent_leverage_tool.agent.load_dotenv")
    def test_hybrid_mode_builds_hosted_tools(self, _mock_load_dotenv: MagicMock) -> None:
        agent = ToolEnabledAgent(mode="hybrid", stateless=True)

        self.assertEqual(agent.mode, "hybrid")
        self.assertEqual(len(agent.agent.tools), 2)
        self.assertTrue(agent.stateless)

    @patch("ai_agent_leverage_tool.agent.load_dotenv")
    def test_file_search_requires_vector_store_ids(self, _mock_load_dotenv: MagicMock) -> None:
        with self.assertRaisesRegex(ValueError, "vector store ids"):
            ToolEnabledAgent(mode="file_search", stateless=True)

    @patch("ai_agent_leverage_tool.agent.load_dotenv")
    def test_missing_api_key_raises_clear_error(self, _mock_load_dotenv: MagicMock) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        agent = ToolEnabledAgent(mode="tavily", stateless=True)

        with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY is required"):
            agent.respond("Hello")


if __name__ == "__main__":
    unittest.main()
