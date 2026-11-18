"""Source-level integration checks for the progressive help UI.

These checks intentionally avoid importing Streamlit so the diagnostics job
can verify the learner-facing wiring in a lightweight environment.
"""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COURSE_SOURCE = (ROOT / "sections" / "course.py").read_text(encoding="utf-8")


class ProgressiveHelpUiTests(unittest.TestCase):
    def test_question_screen_calls_help_before_answer_input(self):
        prompt = COURSE_SOURCE.index('f"#### {question[\'prompt\']}"')
        help_call = COURSE_SOURCE.index(
            "_render_progressive_question_help(lesson, flow, course_id, question, review_metadata)",
            prompt,
        )
        answer_input = COURSE_SOURCE.index("answer_key = (", help_call)
        self.assertLess(prompt, help_call)
        self.assertLess(help_call, answer_input)

    def test_help_ui_uses_verified_registry_status_and_never_hints_transfer_items(self):
        start = COURSE_SOURCE.index("def _render_progressive_question_help(")
        end = COURSE_SOURCE.index("def _render_question(", start)
        helper = COURSE_SOURCE[start:end]
        self.assertIn('if question.get("_is_transfer_check"):', helper)
        self.assertIn("verification_status=review_metadata.get(\"verification_status\")", helper)
        self.assertIn("unverified_content", helper)
        self.assertIn("No reviewed hints are available", helper)

    def test_help_reveals_one_step_at_a_time_and_records_exposure(self):
        start = COURSE_SOURCE.index("def _render_progressive_question_help(")
        end = COURSE_SOURCE.index("def _render_question(", start)
        helper = COURSE_SOURCE[start:end]
        self.assertIn("I'm stuck — guide me", helper)
        self.assertIn("Show next hint", helper)
        self.assertIn("_record_learning_intervention(", helper)
        self.assertIn('event_suffix=f"guided_help_{level}"', helper)
        self.assertIn("flow[\"_guided_help_level\"]", helper)

    def test_help_is_session_scoped_and_does_not_change_the_answer_widget_key(self):
        start = COURSE_SOURCE.index("def _render_progressive_question_help(")
        end = COURSE_SOURCE.index("def _render_question(", start)
        helper = COURSE_SOURCE[start:end]
        self.assertIn("_guided_help_question_key", helper)
        self.assertNotIn("question.get(\"answer\")", helper)
        self.assertNotIn("flow[\"results\"]", helper)
        self.assertIn("answer_key = (", COURSE_SOURCE)


if __name__ == "__main__":
    unittest.main()
