"""Regression tests for the framework-free answer checker."""
import unittest

import logic


class NumericAnswerValidationTests(unittest.TestCase):
    def setUp(self):
        self.question = {
            "id": "numeric_regression",
            "type": "numeric",
            "answer": 1,
            "tolerance": 0.01,
        }

    def test_accepts_valid_numeric_values(self):
        self.assertTrue(logic.check_answer(self.question, 1))
        self.assertTrue(logic.check_answer(self.question, "1.005"))
        self.assertTrue(logic.check_answer(self.question, 1.009))
        self.assertTrue(logic.check_answer(self.question, 1.01))

    def test_rejects_boolean_answers(self):
        self.assertFalse(logic.check_answer(self.question, True))
        self.assertFalse(logic.check_answer(self.question, False))

    def test_rejects_non_finite_user_answers(self):
        for answer in (float("nan"), float("inf"), float("-inf"), "nan", "inf"):
            with self.subTest(answer=answer):
                self.assertFalse(logic.check_answer(self.question, answer))

    def test_rejects_invalid_expected_values_and_tolerances(self):
        for expected in (True, float("nan"), float("inf"), "not-a-number"):
            with self.subTest(expected=expected):
                question = {**self.question, "answer": expected}
                self.assertFalse(logic.check_answer(question, 1))

        for tolerance in (True, -0.01, float("nan"), float("inf"), "invalid"):
            with self.subTest(tolerance=tolerance):
                question = {**self.question, "tolerance": tolerance}
                self.assertFalse(logic.check_answer(question, 1))

    def test_rejects_non_numeric_inputs_without_raising(self):
        for answer in (None, [], {}, "not a number"):
            with self.subTest(answer=answer):
                self.assertFalse(logic.check_answer(self.question, answer))


if __name__ == "__main__":
    unittest.main()
