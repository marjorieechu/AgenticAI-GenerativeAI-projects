from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from guardrailed_tool_use_agent.agent import GuardrailedSentimentWorkflow
from guardrailed_tool_use_agent.models import FinalReport, SentimentAnalysis


class GuardrailedSentimentWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ.pop("OPENAI_MODEL", None)

    def tearDown(self) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL", None)

    @patch("guardrailed_tool_use_agent.agent.load_dotenv")
    @patch("guardrailed_tool_use_agent.agent.SQLiteSession")
    @patch("guardrailed_tool_use_agent.agent.Runner.run_sync")
    def test_writer_handoff_returns_structured_report(
        self,
        mock_run_sync: MagicMock,
        mock_sqlite_session: MagicMock,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        mock_sqlite_session.return_value = MagicMock()

        run_result = MagicMock()
        run_result.final_output = FinalReport(
            short_summary="Tesla sentiment is mixed but slightly positive.",
            markdown_report="## Tesla sentiment\nRecent coverage is mixed but constructive.",
            follow_up_questions=[
                "Which headlines are driving sentiment most strongly?",
                "How much of the narrative is product-driven versus valuation-driven?",
            ],
        )
        mock_run_sync.return_value = run_result

        workflow = GuardrailedSentimentWorkflow(
            session_id="tesla-demo",
            db_path=Path("tests/.tmp/session.db"),
        )
        result = workflow.run_writer_handoff(
            "What is the current market sentiment about Tesla?"
        )

        self.assertEqual(result.mode, "writer_handoff")
        self.assertTrue(result.session_enabled)
        self.assertEqual(result.session_id, "tesla-demo")
        self.assertEqual(
            result.final_output["short_summary"],
            "Tesla sentiment is mixed but slightly positive.",
        )
        self.assertIn("SentimentAgent", result.trace_hint)

    @patch("guardrailed_tool_use_agent.agent.load_dotenv")
    @patch("guardrailed_tool_use_agent.agent.Runner.run_sync")
    def test_sentiment_only_mode_returns_sentiment_payload(
        self,
        mock_run_sync: MagicMock,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        run_result = MagicMock()
        run_result.final_output = SentimentAnalysis(
            sentiment="neutral",
            summary="Recent coverage is balanced between optimism and risk.",
            supporting_signals=[
                "Analysts remain divided on near-term catalysts.",
                "News flow includes both growth optimism and valuation concerns.",
            ],
        )
        mock_run_sync.return_value = run_result

        workflow = GuardrailedSentimentWorkflow(stateless=True)
        result = workflow.run_sentiment_only(
            "What is the current market sentiment about Tesla?"
        )

        self.assertEqual(result.mode, "sentiment_only")
        self.assertFalse(result.session_enabled)
        self.assertEqual(result.final_output["sentiment"], "neutral")

    @patch("guardrailed_tool_use_agent.agent.load_dotenv")
    def test_missing_api_key_raises_clear_error(
        self,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        workflow = GuardrailedSentimentWorkflow(stateless=True)

        with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY is required"):
            workflow.run_writer_handoff("What is the current market sentiment about Tesla?")


if __name__ == "__main__":
    unittest.main()
