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
                "font_family",
                "background_tone",
                "corner_style",
                "use_custom_accent",
                "custom_accent_color",
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
        self.assertEqual(settings_model.safe_value("difficulty", "Medium"), "Adaptive")
        self.assertEqual(settings_model.SETTING_OPTIONS["difficulty"], ["Adaptive", "Easy", "Hard"])
        self.assertFalse(settings_model.safe_value("sound", "false"))
        self.assertTrue(settings_model.safe_value("sound", "true"))
        self.assertEqual(settings_model.safe_value("font_family", "Not a font"), "Inter")
        self.assertEqual(settings_model.safe_value("custom_accent_color", "#aabbcc"), "#AABBCC")
        self.assertEqual(settings_model.safe_value("custom_accent_color", "bad-colour"), "#176B5B")
        self.assertEqual(settings_model.safe_value("custom_accent_color", "#FFF"), "#176B5B")

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
        self.assertIn("Interface font", source)
        self.assertIn("Background tone", source)
        self.assertIn("Corner style", source)
        self.assertIn("st.color_picker(", source)
        self.assertIn("Use a custom accent colour", source)
        lowered = source.lower()
        self.assertNotIn("neurodivergence", lowered)
        self.assertNotIn("adhd", lowered)
        self.assertNotIn("medical condition", lowered)

    def test_course_supports_automatic_and_on_request_hints(self):
        source = (ROOT / "sections" / "course.py").read_text(encoding="utf-8")
        self.assertIn('if hint_mode == "Easy":', source)
        self.assertIn('elif hint_mode == "Adaptive":', source)
        self.assertIn('"Show hint"', source)
        self.assertIn('if hint_mode == "Medium":', source)


if __name__ == "__main__":
    unittest.main()
