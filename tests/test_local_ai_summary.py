"""Tests for the offline, preference-aware progress summary."""
import unittest
from unittest.mock import patch

import logic


class LocalProgressSummaryTests(unittest.TestCase):
    def _stats(self):
        return [
            {
                "course_id": "algebra",
                "topic_label": "Algebra",
                "questions_attempted": 10,
                "correct_answers": 6,
                "accuracy": 60.0,
                "top_mistakes": [("Sign errors", 3)],
            },
            {
                "course_id": "fractions",
                "topic_label": "Fractions",
                "questions_attempted": 10,
                "correct_answers": 9,
                "accuracy": 90.0,
                "top_mistakes": [],
            },
        ]

    @patch("logic._recommend_next_step", return_value="Complete Linear Equations.")
    @patch("logic.per_course_stats")
    def test_summary_uses_local_stats_and_preferences(self, stats, _next_step):
        stats.return_value = self._stats()
        summary = logic.generate_progress_summary(
            {"name": "Learner"},
            {},
            preferences={
                "ai_preview_teaching_style": "Direct and concise",
                "ai_preview_answer_format": "Bullet points",
                "ai_preview_challenge_level": "Stretch me",
                "ai_preview_transfer_questions": True,
                "ai_preview_reasoning_steps": False,
                "ai_preview_check_calculations": False,
            },
        )
        self.assertIn("75% overall accuracy", summary)
        self.assertIn("Priority:", summary)
        self.assertIn("Stretch me", summary) if "Stretch me" in summary else self.assertIn("less familiar application", summary)
        self.assertIn("Transfer:", summary)
        self.assertNotIn("Reasoning check:", summary)
        self.assertNotIn("Accuracy check:", summary)
        self.assertIn("- Hi Learner.", summary)

    @patch("logic.per_course_stats", return_value=[])
    def test_empty_state_is_local_and_discloses_language_limit(self, _stats):
        summary = logic.generate_progress_summary(
            {"name": "Learner"},
            {},
            preferences={"ai_preview_response_language": "Bahasa Indonesia"},
        )
        self.assertIn("have not attempted any practice questions yet", summary.lower())
        self.assertIn("currently generates the local progress summary in English", summary)

    def test_summary_engine_does_not_call_provider(self):
        import inspect
        source = inspect.getsource(logic.generate_progress_summary)
        self.assertNotIn("chat_completion", source)
        self.assertNotIn("requests.", source)


if __name__ == "__main__":
    unittest.main()
