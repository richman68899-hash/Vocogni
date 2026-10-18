"""Regression tests for open-ended rubric marking and shared course metadata."""
import unittest

import assessment
import data
from chemistry_course import CHEMISTRY_COURSE, LESSONS


class OpenEndedAssessmentTests(unittest.TestCase):
    def test_course_covers_twelve_lessons_and_is_in_catalogue(self):
        self.assertEqual(len(LESSONS), 12)
        self.assertIn("chemistry_9701", data.COURSES)
        self.assertIn("chemistry_9701", data.COURSE_ORDER)
        course = data.get_course("chemistry_9701")
        self.assertEqual(course["lesson_count"], len(course["lessons"]))
        self.assertEqual(course["category_id"], "academics")
        self.assertEqual(course["subject_id"], "chemistry")
        self.assertEqual(course["level"], "Grade 10")
        self.assertTrue(all(lesson.get("interactive_question", {}).get("marking_points") for lesson in LESSONS))

    def test_every_existing_course_has_shared_catalogue_metadata(self):
        for course in data.all_courses_in_order():
            with self.subTest(course=course["id"]):
                self.assertIn(course["category_id"], data.COURSE_CATEGORIES)
                self.assertTrue(course["subject_id"])
                self.assertTrue(course["category"])
                self.assertTrue(course["subject"])
                self.assertEqual(course["lesson_count"], len(course["lessons"]))

    def test_canonical_open_answer_gets_all_configured_marks(self):
        question = LESSONS[0]["interactive_question"]
        result = assessment.grade_open_ended(question, question["answer"])
        self.assertEqual(result["marks_awarded"], result["max_marks"])
        self.assertTrue(result["is_full_credit"])

    def test_partial_written_response_gets_partial_credit(self):
        question = LESSONS[0]["interactive_question"]
        result = assessment.grade_open_ended(question, "Al = 2")
        self.assertGreater(result["marks_awarded"], 0)
        self.assertLess(result["marks_awarded"], result["max_marks"])
        self.assertFalse(result["is_full_credit"])
        self.assertTrue(result["missing_points"])

    def test_unicode_subscripts_and_equation_arrow_normalize(self):
        self.assertEqual(
            assessment.normalize_notation("Fe + 2HCl → FeCl₂ + H₂"),
            assessment.normalize_notation("Fe + 2HCl -> FeCl2 + H2"),
        )

    def test_typo_warning_does_not_rewrite_answer(self):
        question = {
            "id": "test_sulfate",
            "type": "open_ended",
            "answer": "sulfate",
            "typo_terms": ["sulfate"],
            "max_marks": 1,
            "marking_points": [{
                "id": "name",
                "criteria": "Names sulfate",
                "marks": 1,
                "match_any": ["sulfate"],
            }],
        }
        response = "sulfite"
        result = assessment.grade_open_ended(question, response)
        self.assertEqual(result["raw_response"], response)
        self.assertFalse(result["is_full_credit"])
        self.assertTrue(result["warnings"])
        self.assertIn("sulfite", result["raw_response"])

    def test_empty_answer_scores_zero(self):
        question = LESSONS[0]["interactive_question"]
        result = assessment.grade_open_ended(question, "")
        self.assertEqual(result["marks_awarded"], 0)
        self.assertFalse(result["is_full_credit"])


if __name__ == "__main__":
    unittest.main()
