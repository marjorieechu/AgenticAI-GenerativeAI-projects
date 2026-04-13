from __future__ import annotations

import os
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch

from creative_advertising_ai_agent_team.agent import CreativeAdvertisingPipeline
from creative_advertising_ai_agent_team.cli import export_run_artifacts
from creative_advertising_ai_agent_team.models import (
    ChannelPlan,
    CreativeIdeas,
    PipelineRunResult,
    SelectedCampaigns,
    TweetCopy,
)


class CreativeAdvertisingPipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        os.environ["OPENAI_API_KEY"] = "test-key"
        os.environ.pop("OPENAI_MODEL", None)

    def tearDown(self) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("OPENAI_MODEL", None)

    @patch("creative_advertising_ai_agent_team.agent.load_dotenv")
    @patch("creative_advertising_ai_agent_team.agent.SQLiteSession")
    @patch("creative_advertising_ai_agent_team.agent.Runner.run_sync")
    def test_pipeline_runs_four_agent_handoff_sequence(
        self,
        mock_run_sync: MagicMock,
        mock_sqlite_session: MagicMock,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        mock_sqlite_session.return_value = MagicMock()

        director_result = MagicMock()
        director_result.final_output_as.return_value = CreativeIdeas(
            ideas=[
                "Refill Rituals",
                "Bali Beach Clean Sip",
                "Carry Less Plastic",
            ]
        )
        strategist_result = MagicMock()
        strategist_result.final_output_as.return_value = SelectedCampaigns(
            top_campaigns=["Refill Rituals", "Bali Beach Clean Sip"],
            reasoning="These ideas are memorable, aligned to the eco angle, and easy to activate on social.",
        )
        copywriter_result = MagicMock()
        copywriter_result.final_output_as.return_value = TweetCopy(
            tweets=[
                "Refill your day, not the landfill.",
                "Hydrate in Bali with a bottle built for lighter footprints.",
                "Beach days feel better with less plastic in the story.",
            ]
        )
        channel_planner_result = MagicMock()
        channel_planner_result.final_output_as.return_value = ChannelPlan(
            twitter=[
                "Use refill-station map drops and stamp-collection moments.",
                "Pair creator posts with location-based hydration challenges.",
            ],
            linkedin=[
                "Position the launch as a sustainability-meets-tourism brand play.",
                "Highlight partner ecosystem with cafes, studios, and surf schools.",
            ],
            email=[
                "Launch an island guide email built around refill stops and partner offers.",
                "Use a welcome sequence for travelers and eco-conscious locals.",
            ],
            short_video=[
                "Show a day-in-the-life Bali route powered by refill moments.",
                "Cut influencer footage from yoga, surf, and cafe transitions.",
            ],
        )
        mock_run_sync.side_effect = [
            director_result,
            strategist_result,
            copywriter_result,
            channel_planner_result,
        ]

        pipeline = CreativeAdvertisingPipeline(
            session_id="creative-demo",
            db_path=Path("tests/.tmp/session.db"),
        )
        result = pipeline.run_campaign(
            "Launch campaign for a new eco-friendly water bottle in Bali"
        )

        self.assertEqual(result.top_campaigns, ["Refill Rituals", "Bali Beach Clean Sip"])
        self.assertEqual(len(result.ideas), 3)
        self.assertEqual(len(result.tweets), 3)
        self.assertIn("twitter", result.channel_plan)
        self.assertEqual(len(result.channel_plan["email"]), 2)
        self.assertTrue(result.session_enabled)
        self.assertEqual(result.session_id, "creative-demo")
        self.assertEqual(result.workflow_name, "Creative Advertising AI Agent Team")
        self.assertEqual(mock_run_sync.call_count, 4)

    @patch("creative_advertising_ai_agent_team.agent.load_dotenv")
    def test_stateless_mode_skips_sqlite_session(
        self,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        pipeline = CreativeAdvertisingPipeline(stateless=True)

        self.assertTrue(pipeline.stateless)
        self.assertIsNone(pipeline.session)

    @patch("creative_advertising_ai_agent_team.agent.load_dotenv")
    def test_missing_api_key_raises_clear_error(
        self,
        _mock_load_dotenv: MagicMock,
    ) -> None:
        os.environ.pop("OPENAI_API_KEY", None)
        pipeline = CreativeAdvertisingPipeline(stateless=True)

        with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY is required"):
            pipeline.run_campaign("Launch a product")

    def test_export_run_artifacts_writes_json_and_markdown(self) -> None:
        result = PipelineRunResult(
            product_prompt="Launch campaign for a new eco-friendly water bottle in Bali",
            ideas=["Idea 1", "Idea 2", "Idea 3"],
            top_campaigns=["Idea 1", "Idea 2"],
            reasoning="Idea 1 and Idea 2 are easiest to execute.",
            tweets=["Tweet one", "Tweet two"],
            channel_plan={
                "twitter": ["Twitter angle"],
                "linkedin": ["LinkedIn angle"],
                "email": ["Email angle"],
                "short_video": ["Short video angle"],
            },
            model="gpt-5.4-mini",
            workflow_name="Creative Advertising AI Agent Team",
            session_enabled=True,
            session_id="bali-launch",
        )

        export_dir = Path("tests/.tmp/exports")
        export_dir.mkdir(parents=True, exist_ok=True)

        json_path, markdown_path = export_run_artifacts(
            result,
            export_dir=export_dir,
            export_prefix="bali-launch",
        )

        self.assertTrue(json_path.exists())
        self.assertTrue(markdown_path.exists())
        self.assertIn("bali-launch-", json_path.name)
        self.assertEqual(json_path.suffix, ".json")
        self.assertEqual(markdown_path.suffix, ".md")

        json_text = json_path.read_text(encoding="utf-8")
        markdown_text = markdown_path.read_text(encoding="utf-8")
        self.assertIn('"product_prompt": "Launch campaign for a new eco-friendly water bottle in Bali"', json_text)
        self.assertIn("# Campaign Run Summary", markdown_text)
        self.assertIn("Top campaigns:", markdown_text)
        self.assertIn("Channel plan:", markdown_text)

        json_path.unlink()
        markdown_path.unlink()


if __name__ == "__main__":
    unittest.main()
