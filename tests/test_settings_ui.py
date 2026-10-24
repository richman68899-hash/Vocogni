"""Regression tests for the redesigned Settings page."""
import unittest
from pathlib import Path

from sections import settings as settings_page


ROOT = Path(__file__).resolve().parents[1]


class SettingsPageTests(unittest.TestCase):
    def test_presets_only_change_existing_durable_settings(self):
        known_settings = set(settings_page.DEFAULT_SETTINGS)
        for name, values in settings_page.PRESETS.items():
            with self.subTest(preset=name):
                self.assertTrue(values)
                self.assertLessEqual(set(values), known_settings)

    def test_every_visible_setting_maps_to_a_durable_setting(self):
        self.assertEqual(
            set(settings_page.SETTING_WIDGET_KEYS),
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
        self.assertTrue(set(settings_page.SETTING_WIDGET_KEYS) <= set(settings_page.DEFAULT_SETTINGS))

    def test_invalid_legacy_values_fall_back_safely(self):
        self.assertEqual(settings_page._safe_value("appearance", "Sepia"), "Light")
        self.assertEqual(settings_page._safe_value("text_size", None), "Medium")
        self.assertEqual(settings_page._safe_value("difficulty", "Impossible"), "Adaptive")

    def test_setup_summary_reflects_real_setting_labels(self):
        summary = settings_page._current_summary(settings_page.DEFAULT_SETTINGS)
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
