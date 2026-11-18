"""Tests for the read-only VQE pilot readiness audit."""
import unittest

from scripts.audit_pilot_readiness import audit_lesson


def _record(question_id, purpose="practice", skill_id="math.number.fraction_representation"):
    return {
        "course_id": "test_course",
        "lesson_id": "test_lesson",
        "question_id": question_id,
        "verification_status": "verified",
        "question": {
            "purpose": purpose,
            "skill_id": skill_id,
        },
    }


class PilotReadinessAuditTests(unittest.TestCase):
    def test_complete_lesson_with_verified_practice_and_application_is_ready(self):
        lesson = {
            "id": "test_lesson",
            "title": "Fractions",
            "explanation": "A fraction represents equal parts of a whole.",
            "worked_example": "Three of four equal parts is 3/4.",
        }
        report = audit_lesson(
            "test_course",
            lesson,
            [
                _record("q1"),
                _record("q2"),
                _record("q3", purpose="application"),
            ],
        )
        self.assertTrue(report["ready_for_structural_pilot_review"])
        self.assertEqual(report["verified_question_count"], 3)
        self.assertEqual(report["verified_practice_count"], 2)
        self.assertEqual(report["verified_application_or_reasoning_count"], 1)
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["warnings"], [])

    def test_legacy_and_unverified_questions_do_not_count_as_coverage(self):
        lesson = {
            "id": "test_lesson",
            "title": "Fractions",
            "explanation": "Core explanation.",
            "worked_example": "Example.",
        }
        records = [
            _record("legacy", purpose="practice"),
            {
                **_record("needs-review", purpose="practice"),
                "verification_status": "needs_review",
            },
        ]
        report = audit_lesson("test_course", lesson, records)
        self.assertFalse(report["ready_for_structural_pilot_review"])
        self.assertEqual(report["verified_question_count"], 0)
        self.assertTrue(any("at least 2" in error for error in report["errors"]))

    def test_missing_practice_and_skill_ids_are_reported(self):
        lesson = {
            "id": "test_lesson",
            "title": "Fractions",
            "explanation": "Core explanation.",
        }
        report = audit_lesson(
            "test_course",
            lesson,
            [
                _record("q1", purpose="conceptual", skill_id=None),
                _record("q2", purpose="application", skill_id=""),
            ],
        )
        self.assertFalse(report["ready_for_structural_pilot_review"])
        self.assertTrue(any("verified practice questions" in error for error in report["errors"]))
        self.assertTrue(any("stable skill IDs" in error for error in report["errors"]))
        self.assertTrue(any("worked example" in warning for warning in report["warnings"]))

    def test_missing_application_is_a_warning_not_a_false_release_failure(self):
        lesson = {
            "id": "test_lesson",
            "title": "Fractions",
            "explanation": "Core explanation.",
            "worked_example": "Example.",
        }
        report = audit_lesson(
            "test_course",
            lesson,
            [_record("q1"), _record("q2")],
        )
        self.assertTrue(report["ready_for_structural_pilot_review"])
        self.assertTrue(any("transfer evidence is limited" in warning for warning in report["warnings"]))


if __name__ == "__main__":
    unittest.main()
