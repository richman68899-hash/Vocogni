"""Regression tests for numeric terms in open-response math rubrics."""
import unittest

import math_grading


class MathGradingNumericTokenTests(unittest.TestCase):
    def test_numeric_rubric_terms_match_complete_values_only(self):
        self.assertFalse(math_grading._contains("12", "2"))
        self.assertFalse(math_grading._contains("2.5", "2"))
        self.assertFalse(math_grading._contains("x2", "2"))
        self.assertTrue(math_grading._contains("x = 2", "2"))
        self.assertTrue(math_grading._contains("(2, 3)", "2"))

    def test_malformed_open_response_marks_are_reported_without_raising(self):
        question = {
            "id": "malformed_math_rubric",
            "type": "open_ended",
            "prompt": "Explain the method.",
            "answer": "x = 2",
            "explanation": "A model explanation.",
            "max_marks": True,
            "marking_points": [
                {"marks": "two", "match_any": ["x = 2"]},
                None,
            ],
        }
        errors = math_grading.validate_open_response_question(question)
        self.assertTrue(any("max_marks" in error for error in errors))
        self.assertTrue(any("positive integer marks" in error for error in errors))
        self.assertTrue(any("must be a dictionary" in error for error in errors))

    def test_numeric_rubric_no_longer_awards_a_wrong_root_embedded_in_12(self):
        point = {
            "match_groups": [["-1"], ["2"]],
        }
        self.assertFalse(math_grading._point_awarded(point, math_grading.normalize_answer("x = -1 and x = 12")))
        self.assertTrue(math_grading._point_awarded(point, math_grading.normalize_answer("x = -1 and x = 2")))


if __name__ == "__main__":
    unittest.main()
