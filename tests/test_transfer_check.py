"""Tests for independent transfer selection and catalogue coverage."""
import unittest
from unittest.mock import patch

import transfer_check
import audit_transfer_coverage


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

    def test_selects_geometry_application_item_from_different_lesson(self):
        selected = transfer_check.select_transfer_question(
            [{"id": "geometry_l1_q1"}],
            course_id="basic_geometry",
            lesson_id="geometry_l1",
        )
        self.assertIsNotNone(selected)
        self.assertEqual(selected["id"], "geometry_l4_transfer_q1")
        self.assertEqual(selected["purpose"], "application")
        self.assertEqual(selected["skill_id"], "math.geometry.angle_facts")
        self.assertEqual(selected["source_lesson_id"], "geometry_l4")

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
        practice = [{"id": "fractions_l2_q1"}]
        repeated_candidate = {
            "question_id": "fractions_l2_q1",
            "lesson_id": "fractions_l1",
            "question": {"type": "numeric", "prompt": "Repeated item"},
        }
        with patch("transfer_check.question_engine.select_questions", return_value=[repeated_candidate]):
            selected = transfer_check.select_transfer_question(
                practice, course_id="fractions", lesson_id="fractions_l2"
            )
        self.assertIsNone(selected)

    def test_coverage_audit_balances_covered_and_uncovered_pairs(self):
        report = transfer_check.audit_transfer_coverage()
        self.assertGreater(report["practice_course_skill_pairs"], 0)
        self.assertEqual(
            report["practice_course_skill_pairs"],
            report["covered_pairs"] + report["uncovered_pairs"],
        )
        self.assertTrue(all(isinstance(r["application_question_ids"], list) for r in report["rows"]))
        self.assertTrue(all("practice_lesson_ids" in r for r in report["rows"]))
        self.assertTrue(all("has_cross_lesson_application_item" in r for r in report["rows"]))


    def test_cli_report_recalculates_totals_for_course_filter(self):
        with patch("audit_transfer_coverage.transfer_check.audit_transfer_coverage", return_value={
            "rows": [
                {"course_id": "fractions", "skill_id": "skill.a",
                 "practice_lesson_ids": ["lesson_1"],
                 "has_cross_lesson_application_item": True,
                 "application_question_ids": ["q_app"]},
                {"course_id": "algebra", "skill_id": "skill.b",
                 "practice_lesson_ids": ["lesson_2"],
                 "has_cross_lesson_application_item": False,
                 "application_question_ids": []},
            ]
        }):
            report = audit_transfer_coverage.build_report(course_id="fractions")
        self.assertEqual(report["practice_course_skill_pairs"], 1)
        self.assertEqual(report["covered_pairs"], 1)
        self.assertEqual(report["uncovered_pairs"], 0)
        self.assertEqual(report["coverage_percent"], 100)

    def test_cli_report_discloses_catalogue_only_limitation(self):
        report = {
            "practice_course_skill_pairs": 1,
            "covered_pairs": 0,
            "uncovered_pairs": 1,
            "coverage_percent": 0,
            "rows": [{
                "course_id": "fractions",
                "skill_id": "math.number.fraction_operations",
                "practice_lesson_ids": ["fractions_l2"],
                "has_cross_lesson_application_item": False,
                "application_question_ids": [],
            }],
        }
        rendered = audit_transfer_coverage.render_report(report, uncovered_only=True)
        self.assertIn("[UNCOVERED] fractions / math.number.fraction_operations", rendered)
        self.assertIn("does not prove novelty", rendered)


if __name__ == "__main__":
    unittest.main()
