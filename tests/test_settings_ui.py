"""Regression tests for Settings defaults, presets, and UI structure."""
import base64
import io
import unittest
import wave
from pathlib import Path

import logic
import settings_model


ROOT = Path(__file__).resolve().parents[1]


class SettingsPageTests(unittest.TestCase):
    def test_feedback_cues_are_valid_short_wav_files_and_distinct(self):
        correct = base64.b64decode(logic.get_correct_answer_beep_base64())
        incorrect = base64.b64decode(logic.get_wrong_answer_beep_base64())
        self.assertNotEqual(correct, incorrect)
        for payload, expected_duration_range in (
            (correct, (0.20, 0.35)),
            (incorrect, (0.15, 0.29)),
        ):
            with wave.open(io.BytesIO(payload), "rb") as sound:
                self.assertEqual(sound.getnchannels(), 1)
                self.assertEqual(sound.getsampwidth(), 2)
                self.assertEqual(sound.getframerate(), 22050)
                duration = sound.getnframes() / sound.getframerate()
                self.assertGreater(duration, expected_duration_range[0])
                self.assertLess(duration, expected_duration_range[1])

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
                "wrong_answer_sound",
                "answer_shake",
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
        self.assertFalse(settings_model.DEFAULT_SETTINGS["sound"])
        self.assertFalse(settings_model.DEFAULT_SETTINGS["wrong_answer_sound"])
        self.assertFalse(settings_model.DEFAULT_SETTINGS["answer_shake"])

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
        self.assertIn("Correct cue off", summary)
        self.assertIn("Incorrect cue off", summary)
        self.assertIn("Wrong-answer shake off", summary)

    def test_socials_ai_upgrade_and_misc_sections_are_available(self):
        source = (ROOT / "sections" / "settings.py").read_text(encoding="utf-8")
        for section in ("Socials", "AI", "Upgrade", "Misc"):
            self.assertIn(f'("{section}",', source)
            self.assertIn(f'if active_section == "{section}":', source)
        self.assertIn("Only verified official links will be listed.", source)
        self.assertIn("No paid plans or upgrade actions are currently available.", source)

    def test_settings_page_is_grouped_and_has_no_unrelated_medical_disclaimer(self):
        source = (ROOT / "sections" / "settings.py").read_text(encoding="utf-8")
        self.assertIn("Quick setups", source)
        self.assertIn("Appearance", source)
        self.assertIn("Learning preferences", source)
        self.assertIn("Focus & interaction", source)
        self.assertIn("Incorrect-answer cue", source)
        self.assertIn("Wrong-answer shake", source)
        self.assertIn("Motion warning:", source)
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

    def test_settings_page_has_clickable_future_ready_categories(self):
        source = (ROOT / "sections" / "settings.py").read_text(encoding="utf-8")
        for section in (
            "General",
            "Appearance",
            "Learning",
            "Focus & sound",
            "Reading comfort",
            "Notifications",
            "Account",
            "Privacy & safety",
        ):
            with self.subTest(section=section):
                self.assertIn('("' + section + '",', source)
                self.assertIn('active_section == "' + section + '"', source)
        self.assertIn("settings_active_section", source)
        self.assertIn("on_click=_select_settings_section", source)
        self.assertIn("Notification controls will be added here in a future update.", source)
        self.assertIn("Account and sign-in management will be added here in a future update.", source)

    def test_ai_section_preferences_are_saved_and_feed_the_offline_summary(self):
        source = (ROOT / "sections" / "settings.py").read_text(encoding="utf-8")
        required_controls = (
            "ai_preview_teaching_style",
            "ai_preview_explanation_depth",
            "ai_preview_hint_strategy",
            "ai_preview_correction_style",
            "ai_preview_adaptive_mastery",
            "ai_preview_challenge_level",
            "ai_preview_transfer_questions",
            "ai_preview_reasoning_steps",
            "ai_preview_check_calculations",
            "ai_preview_show_sources",
            "ai_preview_flag_uncertainty",
            "ai_preview_response_language",
            "ai_preview_answer_format",
            "ai_preview_model_preference",
            "ai_preview_speed_preference",
            "ai_preview_web_research",
            "ai_preview_image_input",
            "ai_preview_age_appropriate",
            "ai_preview_context_permission",
            "ai_preview_memory_review",
        )
        for key in required_controls:
            with self.subTest(control=key):
                self.assertIn(key, source)
        self.assertIn("These preferences are saved to your learner settings", source)
        self.assertIn('settings["ai_preferences"] = ai_preferences', source)
        self.assertIn("AI_PREFERENCE_DEFAULTS", source)
        self.assertNotIn("ai_preview_", "\n".join(settings_model.DEFAULT_SETTINGS.keys()))


    def test_settings_navigation_is_grouped_and_ai_preferences_are_collapsible(self):
        source = (ROOT / "sections" / "settings.py").read_text(encoding="utf-8")
        self.assertIn('category_groups = [', source)
        self.assertIn('("Personalize",', source)
        self.assertIn('("Learning",', source)
        self.assertIn('("Account & privacy",', source)
        self.assertIn('("More",', source)
        for label in (
            "01 · Teaching approach",
            "02 · Adaptation & challenge",
            "03 · Answer quality & sources",
            "04 · Interaction preferences",
            "05 · Model & capability preferences",
            "06 · Boundaries & learner control",
        ):
            with self.subTest(group=label):
                self.assertIn(f'st.expander("{label}"', source)
        self.assertIn('Currently viewing **{active_section}**', source)
        self.assertIn("rule-based progress summary", source)
        self.assertIn("No LLM or external AI provider is used here.", source)

    def test_wrong_answer_shake_and_sound_are_opt_in_and_respect_motion_preferences(self):
        source = (ROOT / "sections" / "course.py").read_text(encoding="utf-8")
        self.assertIn('display_settings.get("wrong_answer_sound", False)', source)
        self.assertIn('display_settings.get("answer_shake", False)', source)
        self.assertIn('display_settings.get("animations", True)', source)
        self.assertIn('display_settings.get("reduced_motion", False)', source)
        self.assertIn("vc-feedback--shake", source)
        self.assertIn("get_wrong_answer_beep_base64()", source)

    def test_course_supports_automatic_and_on_request_hints(self):
        source = (ROOT / "sections" / "course.py").read_text(encoding="utf-8")
        self.assertIn('if hint_mode == "Easy":', source)
        self.assertIn('elif hint_mode == "Adaptive":', source)
        self.assertIn('"Show hint"', source)
        self.assertIn('if hint_mode == "Medium":', source)

    def test_focus_sound_controls_flush_changes_immediately(self):
        settings_source = (ROOT / "sections" / "settings.py").read_text(encoding="utf-8")
        focus_section = settings_source.split('if active_section == "Focus & sound":', 1)[1].split(
            'if active_section == "Reading comfort":', 1
        )[0]

        for setting_key in ("animations", "sound", "wrong_answer_sound", "answer_shake"):
            with self.subTest(setting=setting_key):
                widget_block = focus_section.split(
                    f'key=SETTING_WIDGET_KEYS["{setting_key}"],', 1
                )[1].split("\n                )", 1)[0]
                self.assertIn("on_change=_persist_setting_widget", widget_block)
                self.assertIn(f'args=("{setting_key}",)', widget_block)

        save_helper = settings_source.split("def _save_settings_now()", 1)[1].split(
            "def _persist_setting_widget", 1
        )[0]
        self.assertIn("state.mark_persistent_dirty()", save_helper)
        self.assertIn("state.flush_persistent_save()", save_helper)

        setting_callback = settings_source.split("def _persist_setting_widget", 1)[1].split(
            "def _persist_ai_preference", 1
        )[0]
        self.assertIn("_save_settings_now()", setting_callback)

        app_source = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.session_state.pop("_settings_save_confirmation_pending", False)', app_source)


if __name__ == "__main__":
    unittest.main()
