"""Regression tests for collapsible Progress sections and saved layout state."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS_SOURCE = (ROOT / "sections" / "progress.py").read_text(encoding="utf-8")


class ProgressSectionsTests(unittest.TestCase):
    def test_every_top_level_progress_section_is_collapsible(self):
        expected = {
            "overview",
            "topic_detail",
            "mastery_receipt",
            "recommendations",
            "coach",
            "lesson_diagnostics",
            "ai_summary",
        }
        start = PROGRESS_SOURCE.index("_PROGRESS_SECTION_DEFAULTS = {")
        end = PROGRESS_SOURCE.index("\n}", start)
        defaults_block = PROGRESS_SOURCE[start:end]
        for section_id in expected:
            with self.subTest(section_id=section_id):
                self.assertIn(f'"{section_id}"', defaults_block)
                self.assertIn(f'_progress_section("{section_id}"', PROGRESS_SOURCE)

    def test_expander_state_is_persisted_and_autosaved(self):
        self.assertIn('key=_section_widget_key(section_id)', PROGRESS_SOURCE)
        self.assertIn('on_change=_save_section_state', PROGRESS_SOURCE)
        self.assertIn('"progress_sections"', PROGRESS_SOURCE)
        self.assertIn("state.mark_persistent_dirty()", PROGRESS_SOURCE)

    def test_overview_is_open_by_default_and_details_start_collapsed(self):
        self.assertIn('"overview": True', PROGRESS_SOURCE)
        for section_id in (
            "topic_detail",
            "mastery_receipt",
            "recommendations",
            "coach",
            "lesson_diagnostics",
            "ai_summary",
        ):
            self.assertIn(f'"{section_id}": False', PROGRESS_SOURCE)

    def test_sections_have_clear_purpose_descriptions(self):
        for description in (
            "A snapshot of courses, completed lessons",
            "Choose a course to review lesson progress",
            "A skill-by-skill view of evidence from practice questions",
            "Turns saved activity into suggested next actions",
            "Focused practice for this lesson",
            "Shows the selected topic's entry-diagnostic baseline",
            "A prototype simulation built from your own stored",
        ):
            with self.subTest(description=description):
                self.assertTrue(
                    description in PROGRESS_SOURCE
                    or (description == "Focused practice for this lesson"
                        and "Focused practice for this lesson" in (ROOT / "coach.py").read_text(encoding="utf-8"))
                )

    def test_mastery_receipt_does_not_nest_expanders(self):
        self.assertEqual(PROGRESS_SOURCE.count("st.expander("), 1)
        self.assertIn("with st.container(border=True):", PROGRESS_SOURCE)
        self.assertNotIn('with st.expander(f"{item[\'skill\']}', PROGRESS_SOURCE)


if __name__ == "__main__":
    unittest.main()
