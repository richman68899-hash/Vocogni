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
        self.assertFalse(math_grading._contains("-2", "2"))
        self.assertFalse(math_grading._contains("x = -2", "2"))
        self.assertTrue(math_grading._contains("x = -2", "-2"))
        self.assertTrue(math_grading._contains("10 - 2 = 8", "2"))
        self.assertFalse(math_grading._contains("2e3", "2"))
        self.assertFalse(math_grading._contains("x^2", "2"))

    def test_numeric_rubric_no_longer_awards_a_wrong_root_embedded_in_12(self):
        point = {
            "match_groups": [["-1"], ["2"]],
        }
        self.assertFalse(math_grading._point_awarded(point, math_grading.normalize_answer("x = -1 and x = 12")))
        self.assertTrue(math_grading._point_awarded(point, math_grading.normalize_answer("x = -1 and x = 2")))


if __name__ == "__main__":
    unittest.main()
