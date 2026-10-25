"""Integration tests for VQE adoption in existing tutoring features."""
import unittest
from unittest.mock import patch

import coach
import data
import logic
import question_engine
import revision_sprint
from sections import course as course_section


class VQEIntegrationTests(unittest.TestCase):
    def test_lesson_selector_uses_verified_core_and_selected_pathway(self):
        lesson = data.get_course("fractions")["lessons"][0]
        questions, route = course_section._select_structured_questions(
            lesson,
            {"outcome_key": "level_3", "selected_pathway": "level_2"},
            course_id="fractions",
        )
        ids = {question["id"] for question in questions}
        self.assertEqual(route, "level_2")
        self.assertEqual(
            ids,
            {"fractions_l1_q1", "fractions_l1_q2", "fractions_l1_screen3", "fractions_l1_l2_q1"},
        )
        self.assertTrue(all(question.get("verification_status") == "verified" for question in questions))

    def test_pilot_lesson_does_not_fall_back_when_reviewed_bank_is_unavailable(self):
        lesson = data.get_course("fractions")["lessons"][0]
        with patch.dict(question_engine.VERIFICATION_REGISTRY, {}, clear=True):
            questions, _ = course_section._select_structured_questions(
                lesson, {"outcome_key": "level_1"}, course_id="fractions"
            )
        self.assertEqual(questions, [])

    def test_coach_uses_verified_questions_for_pilot_lessons(self):
        candidates = coach._lesson_candidates("fractions", "fractions_l1")
        self.assertTrue(candidates)
        self.assertTrue(all(
            question.get("verification_status") == "verified"
            for _, question in candidates
        ))
        ids = {question["id"] for _, question in candidates}
        self.assertIn("fractions_l1_q1", ids)
        self.assertIn("fractions_l1_l2_q1", ids)
        self.assertNotIn("fractions_l1_d1", ids)

    def test_revision_sprint_uses_verified_pilot_and_preserves_legacy_lessons(self):
        bank = revision_sprint.question_bank_for_course("fractions")
        pilot_ids = {
            "fractions_l1", "fractions_l2"
        }
        pilot_items = [item for item in bank if item["lesson_id"] in pilot_ids]
        self.assertTrue(pilot_items)
        self.assertTrue(all(item["verification_status"] == "verified" for item in pilot_items))
        self.assertTrue(any(item["lesson_id"] == "fractions_l3" for item in bank))
        self.assertTrue(any(item["verification_status"] == "legacy" for item in bank if item["lesson_id"] == "fractions_l3"))

    def test_revision_sprint_saves_vqe_provenance_in_question_result(self):
        bank = revision_sprint.question_bank_for_course("fractions")
        item = next(row for row in bank if row["question_id"] == "fractions_l1_q1")
        progress = {"fractions": logic.blank_course_progress()}
        revision_sprint.record_sprint_attempt(
            progress,
            "fractions",
            [{
                "item": item,
                "answer": "3/4",
                "evaluation": {
                    "correct": True,
                    "score": 1,
                    "max_marks": 1,
                    "marking_result": None,
                },
            }],
            completed_at="2026-10-25T05:00:00+00:00",
        )
        result = progress["fractions"]["practice_attempts"]["fractions_l1"][0]["results"][0]
        self.assertEqual(result["question_id"], "fractions_l1_q1")
        self.assertEqual(result["question_version"], 1)
        self.assertEqual(result["skill_id"], "math.number.fraction_representation")
        self.assertEqual(result["verification_status"], "verified")
        self.assertEqual(result["question_purpose"], "conceptual")

    def test_attempt_metadata_has_backward_compatible_legacy_fallback(self):
        metadata = question_engine.attempt_metadata(
            "old_unregistered_question",
            course_id="fractions",
            lesson_id="fractions_l3",
        )
        self.assertEqual(metadata["verification_status"], "legacy")
        self.assertEqual(metadata["question_version"], 1)
        self.assertIsNone(metadata["skill_id"])


if __name__ == "__main__":
    unittest.main()
