"""Regression tests for Coach question-source selection and attribution."""
import unittest
from unittest.mock import patch

import coach


class CoachProvenanceTests(unittest.TestCase):
    def test_legacy_catalogue_reads_practice_and_interactive_question_schemas(self):
        course = {
            "lessons": [{"id": "lesson_a", "title": "Lesson A"}],
        }
        records = [
            {
                "lesson_id": "lesson_a",
                "source_field": "practice_questions",
                "verification_status": "legacy",
                "question": {"id": "practice_q", "type": "numeric", "prompt": "Calculate 2 + 2."},
            },
            {
                "lesson_id": "lesson_a",
                "source_field": "interactive_question",
                "verification_status": "legacy",
                "question": {"id": "interactive_q", "type": "mc", "prompt": "Choose one.", "options": ["A", "B"]},
            },
            {
                "lesson_id": "lesson_a",
                "source_field": "questions",
                "verification_status": "needs_review",
                "question": {"id": "invalid_q", "type": "mc", "prompt": "Do not expose."},
            },
        ]

        with (
            patch.object(coach.data, "get_course", return_value=course),
            patch.object(coach.question_engine, "is_vqe_pilot_lesson", return_value=False),
            patch.object(coach.question_engine, "iter_question_records", return_value=records),
        ):
            candidates = coach._lesson_candidates("course", "lesson_a")

        self.assertEqual(
            [question["id"] for _, question in candidates],
            ["practice_q", "interactive_q"],
        )

    def test_course_wide_fallback_keeps_actual_source_lesson(self):
        source_lesson = {"id": "source_lesson", "title": "Actual source"}
        source_question = {
            "id": "source_q",
            "type": "numeric",
            "prompt": "Calculate 7 + 5.",
            "answer": 12,
            "source_course_id": "source_course",
            "source_lesson_id": "source_lesson",
        }

        with (
            patch.object(coach, "_lesson_candidates", side_effect=[[], [(source_lesson, source_question)]]),
            patch.object(coach.question_engine, "is_vqe_pilot_lesson", return_value=False),
        ):
            presented = coach._randomized_question("selected_course", "selected_lesson", 3)

        self.assertEqual(presented["_vqe_source_question_id"], "source_q")
        self.assertEqual(presented["_coach_source_course_id"], "source_course")
        self.assertEqual(presented["_coach_source_lesson_id"], "source_lesson")

    def test_attempt_metadata_uses_question_source_not_selected_lesson(self):
        question = {
            "id": "coach_2_source_q",
            "_vqe_source_question_id": "source_q",
            "_coach_source_course_id": "source_course",
            "_coach_source_lesson_id": "source_lesson",
            "type": "numeric",
            "_coach_generated_variant": False,
        }
        with (
            patch.object(coach.question_engine, "attempt_metadata", return_value={"question_id": "source_q"}) as metadata,
            patch.object(coach.learning_contracts, "add_presentation_context", return_value={"attributed": True}) as add_context,
        ):
            result = coach._attempt_provenance(question, "selected_course", "selected_lesson")

        metadata.assert_called_once_with(
            "source_q",
            course_id="source_course",
            lesson_id="source_lesson",
        )
        add_context.assert_called_once_with(
            {"question_id": "source_q"},
            presented_question_id="coach_2_source_q",
            question_origin="authored_reuse",
            content_modified=False,
        )
        self.assertEqual(result, {"attributed": True})


if __name__ == "__main__":
    unittest.main()
