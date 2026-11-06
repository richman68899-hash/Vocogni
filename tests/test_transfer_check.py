"""Tests for independent transfer selection and catalogue coverage."""
import unittest
from unittest.mock import patch

import transfer_check


class IndependentTransferTests(unittest.TestCase):
    def test_selects_different_lesson_verified_application_for_same_skill(self):
        selected = transfer_check.select_transfer_question(
            [{"id": "fractions_l2_q1"}], course_id="fractions", lesson_id="fractions_l2"
        )
        self.assertIsNotNone(selected)
        self.assertTrue(selected["_is_transfer_check"])
        self.assertEqual(selected["skill_id"], "math.number.fraction_operations")
        self.assertEqual(selected["purpose"], "application")
        self.assertNotEqual(selected["source_lesson_id"], "fractions_l2")

    def test_no_different_lesson_item_means_no_transfer(self):
        selected = transfer_check.select_transfer_question(
            [{"id": "fractions_l1_q1"}], course_id="fractions", lesson_id="fractions_l1"
        )
        self.assertIsNone(selected)

    def test_missing_course_or_unknown_skill_returns_none(self):
        self.assertIsNone(transfer_check.select_transfer_question(
            [{"id": "unknown"}], course_id="fractions", lesson_id="fractions_l1"
        ))
        self.assertIsNone(transfer_check.select_transfer_question(
            [{"id": "fractions_l2_q1"}], course_id=None, lesson_id="fractions_l2"
        ))

    def test_selector_uses_verified_application_filter(self):
        with patch("transfer_check.question_engine.select_questions", return_value=[]) as select:
            self.assertIsNone(transfer_check.select_transfer_question(
                [{"id": "fractions_l2_q1"}], course_id="fractions", lesson_id="fractions_l2"
            ))
        select.assert_called_once_with(
            course_id="fractions", skill_id="math.number.fraction_operations",
            purpose="application", verified_only=True,
        )

    def test_append_is_idempotent_and_adds_at_most_one_item(self):
        practice = [{"id": "fractions_l2_q1"}]
        once = transfer_check.append_transfer_question(
            practice, course_id="fractions", lesson_id="fractions_l2"
        )
        twice = transfer_check.append_transfer_question(
            once, course_id="fractions", lesson_id="fractions_l2"
        )
        self.assertEqual(len([q for q in once if q.get("_is_transfer_check")]), 1)
        self.assertEqual([q["id"] for q in once], [q["id"] for q in twice])

    def test_selector_excludes_repeated_question_id(self):
        selected = transfer_check.select_transfer_question(
            [{"id": "fractions_l1_project_q1"}],
            course_id="fractions", lesson_id="fractions_l2",
        )
        self.assertIsNotNone(selected)
        self.assertNotEqual(selected["id"], "fractions_l1_project_q1")

    def test_coverage_audit_balances_covered_and_uncovered_pairs(self):
        report = transfer_check.audit_transfer_coverage()
        self.assertGreater(report["practice_course_skill_pairs"], 0)
        self.assertEqual(
            report["practice_course_skill_pairs"],
            report["covered_pairs"] + report["uncovered_pairs"],
        )
        self.assertTrue(all(isinstance(r["application_question_ids"], list) for r in report["rows"]))


if __name__ == "__main__":
    unittest.main()
