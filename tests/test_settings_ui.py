"""Regression tests for Settings defaults, presets, and UI structure."""
import unittest
from pathlib import Path

import settings_model


ROOT = Path(__file__).resolve().parents[1]


class SettingsPageTests(unittest.TestCase):
    def test_presets_only_change_existing_durable_settings(self):
        known_settings = set(settings_model.DEFAULT_SETTINGS)
        for name, values in settings_model.PRESETS.items():
            with self.subTest(preset=name):
                self.assertTrue(values)
                self.assertLessEqual(set(values), known_settings)

    def test_every_visible_setting_maps_to_a_durable_setting(self):
        self.assertEqual(
            set(settings_model.SETTING_WIDGET_KEYS),
            {
                "appearance",
                "text_size",
                "feedback_timing",
                "difficulty",
                "animations",
                "sound",
                "larger_text",
                "high_readability",
            },
        )
        self.assertTrue(
            set(settings_model.SETTING_WIDGET_KEYS)
            <= set(settings_model.DEFAULT_SETTINGS)
        )

    def test_invalid_legacy_values_fall_back_safely(self):
        self.assertEqual(settings_model.safe_value("appearance", "Sepia"), "Light")
        self.assertEqual(settings_model.safe_value("text_size", None), "Medium")
        self.assertEqual(settings_model.safe_value("difficulty", "Impossible"), "Adaptive")
        self.assertFalse(settings_model.safe_value("sound", "false"))
        self.assertTrue(settings_model.safe_value("sound", "true"))

    def test_setup_summary_reflects_real_setting_labels(self):
        summary = settings_model.current_summary(settings_model.DEFAULT_SETTINGS)
        self.assertIn("Light theme", summary)
        self.assertIn("Medium text", summary)
        self.assertIn("immediate feedback", summary)
        self.assertIn("Sound on", summary)

    def test_settings_page_is_grouped_and_has_no_unrelated_medical_disclaimer(self):
        source = (ROOT / "sections" / "settings.py").read_text(encoding="utf-8")
        self.assertIn("Quick setups", source)
        self.assertIn("Appearance", source)
        self.assertIn("Learning preferences", source)
        self.assertIn("Focus & interaction", source)
        self.assertIn("Reading comfort", source)
        lowered = source.lower()
        self.assertNotIn("neurodivergence", lowered)
        self.assertNotIn("adhd", lowered)
        self.assertNotIn("medical condition", lowered)


if __name__ == "__main__":
    unittest.main()
