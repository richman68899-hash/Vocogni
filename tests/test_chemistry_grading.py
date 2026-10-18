import unittest

import chemistry_course
import chemistry_grading
import logic


class ChemistryGradingTests(unittest.TestCase):
    def setUp(self):
        self.lessons = chemistry_course.LESSONS

    def question(self, lesson_number):
        return self.lessons[lesson_number - 1]["interactive_question"]

    def test_subscripts_and_arrows_are_normalized_without_changing_digits(self):
        self.assertEqual(
            chemistry_grading.normalize_answer("Ca(OH)₂ → Ca²⁺"),
            chemistry_grading.normalize_answer("Ca(OH)2 -> Ca2+"),
        )

    def test_lesson_one_full_answer_awards_each_marking_point(self):
        question = self.question(1)
        answer = (
            "Al = 2, S = 3, O = 12. The bracket subscript 3 multiplies each atom "
            "in SO4. A coefficient multiplies the whole formula, while a subscript "
            "defines atom ratios."
        )
        result = chemistry_grading.evaluate_open_response(question, answer)
        self.assertEqual(result["score"], question["max_marks"])
        self.assertTrue(result["full_credit"])

    def test_lesson_one_partial_answer_receives_partial_credit(self):
        question = self.question(1)
        result = chemistry_grading.evaluate_open_response(
            question, "Al = 2, S = 3, O = 12."
        )
        self.assertEqual(result["score"], 3)
        self.assertFalse(result["full_credit"])

    def test_typo_warning_is_non_destructive(self):
        question = self.question(7)
        answer = "Barium sulfite forms BaSO3, which is insoluble."
        result = chemistry_grading.evaluate_open_response(question, answer)
        self.assertIsNotNone(result["typo_warning"])
        self.assertIn("sulfite", result["normalized_answer"])
        self.assertIn("sulfate", result["typo_warning"])
        self.assertNotIn("sulfate", result["normalized_answer"])

    def test_unsubmitted_empty_answer_awards_no_marks(self):
        question = self.question(1)
        result = chemistry_grading.evaluate_open_response(question, "")
        self.assertEqual(result["score"], 0)
        self.assertFalse(result["full_credit"])

    def test_legacy_numeric_and_mc_answers_still_work(self):
        self.assertTrue(logic.check_answer(
            {"type": "mc", "answer": "A"}, "A"
        ))
        self.assertTrue(logic.check_answer(
            {"type": "numeric", "answer": 2.5, "tolerance": 0.01}, "2.501"
        ))
        self.assertFalse(logic.check_answer(
            {"type": "numeric", "answer": 2.5, "tolerance": 0.01}, "wrong"
        ))

    def test_open_ended_question_is_supported_by_shared_answer_checker(self):
        question = self.question(1)
        answer = (
            "Al = 2, S = 3, O = 12. The bracket subscript 3 multiplies each atom "
            "in SO4. A coefficient multiplies the whole formula, while a subscript "
            "defines atom ratios."
        )
        self.assertTrue(logic.check_answer(question, answer))


if __name__ == "__main__":
    unittest.main()
