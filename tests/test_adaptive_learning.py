"""Tests for the offline, explainable learning-intelligence engine."""
import unittest

import adaptive_learning
import math_taxonomy


class AdaptiveLearningTests(unittest.TestCase):
    def test_empty_progress_returns_no_personalised_action(self):
        plan = adaptive_learning.build_learning_plan({})
        self.assertEqual(plan["actions"], [])
        self.assertEqual(plan["skills_with_practice_evidence"], 0)

    def test_weak_skill_is_ranked_and_explained(self):
        progress = {
            "fractions": {
                "practice_attempts": {
                    "fractions_l1": [{
                        "completed_at": "2026-10-30T10:00:00+00:00",
                        "results": [
                            {"question_id": "fractions_l1_q1", "skill_id": "math.number.fraction_representation", "correct": False, "score": 0, "max_marks": 1, "mistake_tag": "Denominator confusion"},
                            {"question_id": "fractions_l1_q2", "skill_id": "math.number.fraction_representation", "correct": False, "score": 0, "max_marks": 1, "mistake_tag": "Denominator confusion"},
                            {"question_id": "fractions_l1_screen3", "skill_id": "math.number.fraction_representation", "correct": True, "score": 1, "max_marks": 1},
                        ],
                    }]
                }
            }
        }
        plan = adaptive_learning.build_learning_plan(progress)
        self.assertTrue(plan["actions"])
        action = plan["actions"][0]
        self.assertEqual(action["skill_id"], "math.number.fraction_representation")
        self.assertIn("Denominator confusion", action["reason"])
        self.assertGreater(action["priority"], 0)

    def test_prerequisite_is_prioritised_when_dependency_is_weak(self):
        skill_id = "math.algebra.linear_equations"
        prerequisite = math_taxonomy.SKILLS[skill_id]["prerequisites"][0]
        progress = {
            "algebra": {
                "practice_attempts": {
                    "algebra_l2": [{
                        "completed_at": "2026-10-30T10:00:00+00:00",
                        "results": [
                            {"question_id": "algebra_l2_q1", "skill_id": skill_id, "correct": False, "score": 0, "max_marks": 1},
                            {"question_id": "algebra_l2_q2", "skill_id": skill_id, "correct": False, "score": 0, "max_marks": 1},
                        ],
                    }]
                }
            }
        }
        plan = adaptive_learning.build_learning_plan(progress)
        self.assertTrue(plan["actions"])
        self.assertEqual(plan["actions"][0]["skill_id"], prerequisite)
        self.assertTrue(plan["actions"][0]["is_prerequisite_review"])

    def test_plan_uses_existing_skill_taxonomy_and_does_not_mutate_progress(self):
        progress = {"fractions": {"practice_attempts": {}}}
        before = repr(progress)
        plan = adaptive_learning.build_learning_plan(progress)
        self.assertEqual(repr(progress), before)
        self.assertEqual(plan["skills_tracked"], len(math_taxonomy.SKILLS))


    def test_skill_trajectory_requires_six_recorded_answers(self):
        progress = {
            "fractions": {
                "practice_attempts": {
                    "fractions_l1": [{
                        "completed_at": "2026-10-30T10:00:00+00:00",
                        "results": [
                            {"question_id": f"q{i}", "skill_id": "math.number.fraction_representation",
                             "correct": i % 2 == 0, "score": int(i % 2 == 0), "max_marks": 1}
                            for i in range(5)
                        ],
                    }]
                }
            }
        }
        result = adaptive_learning.build_skill_trajectories(progress)
        item = next(row for row in result["skills"] if row["skill_id"] == "math.number.fraction_representation")
        self.assertEqual(item["trend"], "Building evidence")
        self.assertIsNone(item["previous_window_accuracy_percent"])
        self.assertEqual(item["attempts"], 5)

    def test_skill_trajectory_detects_improvement_from_equal_windows(self):
        progress = {
            "fractions": {
                "practice_attempts": {
                    "fractions_l1": [
                        {
                            "completed_at": "2026-10-30T10:00:00+00:00",
                            "results": [
                                {"question_id": f"old{i}", "skill_id": "math.number.fraction_representation",
                                 "correct": False, "score": 0, "max_marks": 1}
                                for i in range(3)
                            ],
                        },
                        {
                            "completed_at": "2026-10-31T10:00:00+00:00",
                            "results": [
                                {"question_id": f"new{i}", "skill_id": "math.number.fraction_representation",
                                 "correct": True, "score": 1, "max_marks": 1}
                                for i in range(3)
                            ],
                        },
                    ]
                }
            }
        }
        result = adaptive_learning.build_skill_trajectories(progress)
        item = next(row for row in result["skills"] if row["skill_id"] == "math.number.fraction_representation")
        self.assertEqual(item["trend"], "Improving")
        self.assertEqual(item["previous_window_accuracy_percent"], 0)
        self.assertEqual(item["recent_window_accuracy_percent"], 100)
        self.assertEqual(item["change_percentage_points"], 100)

    def test_skill_trajectory_detects_regression_and_does_not_mutate_progress(self):
        progress = {
            "fractions": {
                "practice_attempts": {
                    "fractions_l1": [
                        {
                            "completed_at": "2026-10-30T10:00:00+00:00",
                            "results": [
                                {"question_id": f"old{i}", "skill_id": "math.number.fraction_representation",
                                 "correct": True, "score": 1, "max_marks": 1}
                                for i in range(3)
                            ],
                        },
                        {
                            "completed_at": "2026-10-31T10:00:00+00:00",
                            "results": [
                                {"question_id": f"new{i}", "skill_id": "math.number.fraction_representation",
                                 "correct": False, "score": 0, "max_marks": 1}
                                for i in range(3)
                            ],
                        },
                    ]
                }
            }
        }
        before = repr(progress)
        result = adaptive_learning.build_skill_trajectories(progress)
        item = next(row for row in result["skills"] if row["skill_id"] == "math.number.fraction_representation")
        self.assertEqual(item["trend"], "Needs attention")
        self.assertEqual(item["change_percentage_points"], -100)
        self.assertEqual(repr(progress), before)



if __name__ == "__main__":
    unittest.main()
