import unittest

import logic


class MistakeCoachTests(unittest.TestCase):
    def test_no_recorded_mistakes_returns_no_intervention(self):
        self.assertIsNone(logic.get_mistake_coach({}))

    def test_repeated_error_returns_explainable_next_step(self):
        progress = {
            "fractions": {
                "mistakes": {
                    "Meaning of the denominator": 3,
                    "Addition error": 1,
                }
            }
        }
        result = logic.get_mistake_coach(progress)
        self.assertIsNotNone(result)
        self.assertEqual(result["skill"], "Fraction structure")
        self.assertEqual(result["count"], 3)
        self.assertIn("Meaning of the denominator", result["evidence_label"])
        self.assertTrue(result["action"])
        self.assertIn("fractions", result["available_course_ids"])

    def test_highest_frequency_mistake_wins_deterministically(self):
        progress = {
            "fractions": {"mistakes": {"Meaning of the denominator": 2}},
            "algebra": {"mistakes": {"Sign errors": 5}},
        }
        first = logic.get_mistake_coach(progress)
        second = logic.get_mistake_coach(progress)
        self.assertEqual(first, second)
        self.assertEqual(first["count"], 5)
        self.assertEqual(first["skill"], "Equation transformations")
        self.assertIn("algebra", first["available_course_ids"])

    def test_unknown_tags_are_not_misdiagnosed(self):
        progress = {"fractions": {"mistakes": {"Unmapped mystery tag": 9}}}
        self.assertIsNone(logic.get_mistake_coach(progress))

    def test_zero_or_negative_counts_are_ignored(self):
        progress = {"algebra": {"mistakes": {"Sign errors": 0, "Variable misunderstanding": -1}}}
        self.assertIsNone(logic.get_mistake_coach(progress))

    def test_word_problem_recommendation_points_to_existing_course(self):
        progress = {"word_problems": {"mistakes": {"Translating key words": 2}}}
        result = logic.get_mistake_coach(progress)
        self.assertEqual(result["skill"], "Word-problem modelling")
        self.assertEqual(result["available_course_ids"], ["word_problems"])


if __name__ == "__main__":
    unittest.main()
