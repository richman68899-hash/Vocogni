"""Integration contracts for VQE adoption in existing tutoring features.

Keep these tests framework-free because the diagnostics CI job intentionally
runs without the Streamlit UI dependency installed.
"""
import unittest
from pathlib import Path

import logic
import question_engine
import revision_sprint


ROOT = Path(__file__).resolve().parents[1]
COURSE_SOURCE = (ROOT / "sections" / "course.py").read_text(encoding="utf-8")
COACH_SOURCE = (ROOT / "coach.py").read_text(encoding="utf-8")


class VQEIntegrationTests(unittest.TestCase):
    def test_lesson_selector_uses_verified_core_and_route_filter(self):
        self.assertIn("question_engine.is_vqe_pilot_lesson(course_id, lesson.get(\"id\", \"\"))", COURSE_SOURCE)
        self.assertIn("question_engine.select_questions(", COURSE_SOURCE)
        self.assertIn("verified_only=True", COURSE_SOURCE)
        self.assertIn('selected_pathway = route if route in ("level_2", "level_3", "project") else "standard"', COURSE_SOURCE)
        self.assertIn("question_engine.attempt_metadata(", COURSE_SOURCE)

    def test_pilot_lesson_has_no_silent_unverified_fallback(self):
        self.assertIn(
            "The lesson will not fall back to unverified content",
            COURSE_SOURCE,
        )
        self.assertIn("if question_engine.is_vqe_pilot_lesson(course_id, lesson[\"id\"]):", COURSE_SOURCE)

    def test_coach_uses_verified_questions_for_pilot_lessons(self):
        self.assertIn("question_engine.select_questions(", COACH_SOURCE)
        self.assertIn("verified_only=True", COACH_SOURCE)
        self.assertIn(
            "if not candidates and not (\n        lesson_id and question_engine.is_vqe_pilot_lesson(course_id, lesson_id)\n    ):",
            COACH_SOURCE,
        )
        self.assertIn('coach_data.setdefault("attempts", [])', COACH_SOURCE)

    def test_revision_sprint_uses_verified_pilot_and_preserves_legacy_lessons(self):
        bank = revision_sprint.question_bank_for_course("fractions")
        pilot_lessons = {"fractions_l1", "fractions_l2"}
        pilot_items = [item for item in bank if item["lesson_id"] in pilot_lessons]
        self.assertTrue(pilot_items)
        self.assertTrue(all(item["verification_status"] == "verified" for item in pilot_items))
        self.assertTrue(any(item["lesson_id"] == "fractions_l3" for item in bank))
        self.assertTrue(any(
            item["verification_status"] == "legacy"
            for item in bank if item["lesson_id"] == "fractions_l3"
        ))

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
