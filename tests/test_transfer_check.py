"""Tests for independent transfer question selection."""
import unittest
from unittest.mock import patch

import transfer_check


class IndependentTransferTests(unittest.TestCase):
    def test_selects_verified_application_item_for_same_skill_from_other_lesson(self):
        practice = [{"id": "fractions_l2_q1"}]
        selected = transfer_check.select_transfer_question(
            practice, course_id="fractions", lesson_id="fractions_l2"
        )
        self.assertIsNotNone(selected)
        self.assertTrue(selected["_is_transfer_check"])
        self.assertEqual(selected["skill_id"], "math.number.fraction_operations")
        self.assertEqual(selected["purpose"], "application")
        self.assertNotEqual(selected["source_lesson_id"], "fractions_l2")

    def test_does_not_select_same_lesson_application_item(self):
        practice = [{"id": "fractions_l1_q1"}]
        selected = transfer_check.select_transfer_question(
            practice, course_id="fractions", lesson_id="fractions_l1"
        )
        # There is no separate-lesson application item for this exact skill.
        self.assertIsNone(selected)

    def test_missing_course_or_skill_returns_none(self):
        self.assertIsNone(transfer_check.select_transfer_question(
            [{"id": "unknown"}], course_id="fractions", lesson_id="fractions_l1"
        ))
        self.assertIsNone(transfer_check.select_transfer_question(
            [{"id": "fractions_l2_q1"}], course_id=None, lesson_id="fractions_l2"
        ))

    def test_append_adds_at_most_one_transfer_item_and_is_idempotent(self):
        practice = [{"id": "fractions_l2_q1"}]
        once = transfer_check.append_transfer_question(
            practice, course_id="fractions", lesson_id="fractions_l2"
        )
        twice = transfer_check.append_transfer_question(
            once, course_id="fractions", lesson_id="fractions_l2"
        )
        self.assertEqual(len([q for q in once if q.get("_is_transfer_check")]), 1)
        self.assertEqual(len([q for q in twice if q.get("_is_transfer_check")]), 1)
        self.assertEqual([q["id"] for q in once], [q["id"] for q in twice])

    def test_only_verified_application_candidates_are_considered(self):
        practice = [{"id": "fractions_l2_q1"}]
        with patch("transfer_check.question_engine.select_questions", return_value=[]) as select:
            self.assertIsNone(transfer_check.select_transfer_question(
                practice, course_id="fractions", lesson_id="fractions_l2"
            ))
            select.assert_called_once_with(
                course_id="fractions",
                skill_id="math.number.fraction_operations",
                purpose="application",
                verified_only=True,
            )


if __name__ == "__main__":
    unittest.main()
