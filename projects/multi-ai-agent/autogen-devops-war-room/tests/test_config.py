import os
import unittest

from autogen_devops_war_room.config import MODERATE_TEMPERATURE, role_layout, validate_env_for_mode


class ConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original = {
            "OPENAI_API_KEY": os.environ.get("OPENAI_API_KEY"),
            "GEMINI_API_KEY": os.environ.get("GEMINI_API_KEY"),
            "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY"),
        }

    def tearDown(self) -> None:
        for key, value in self.original.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    def test_openai_only_requires_only_openai_key(self) -> None:
        os.environ["OPENAI_API_KEY"] = "test-openai"
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)

        self.assertEqual(validate_env_for_mode("openai_only"), [])

    def test_mixed_mode_requires_all_three_keys(self) -> None:
        os.environ["OPENAI_API_KEY"] = "test-openai"
        os.environ.pop("GEMINI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)

        self.assertEqual(validate_env_for_mode("mixed"), [])

    def test_mixed_layout_is_three_ai_agents(self) -> None:
        layout = role_layout("mixed")

        self.assertEqual(len(layout), 3)
        self.assertEqual(layout[0].provider, "openai")
        self.assertEqual(layout[1].provider, "openai")
        self.assertEqual(layout[2].provider, "openai")

    def test_temperature_is_moderate(self) -> None:
        self.assertEqual(MODERATE_TEMPERATURE, 0.6)


if __name__ == "__main__":
    unittest.main()
