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



    def test_intervention_timeline_connects_mapped_diagnostic_to_verified_practice(self):
        progress = {
            "fractions": {
                "diagnostics": {
                    "fractions_l1": {
                        "completed_at": "2026-10-30T09:00:00+00:00",
                        "answer_review": [
                            {"skill_tag": "Equivalent fractions", "correct": False},
                            {"skill_tag": "Comparing fractions", "correct": True},
                            {"skill_tag": "Unmapped diagnostic label", "correct": False},
                        ],
                    }
                },
                "practice_attempts": {
                    "fractions_l1": [{
                        "attempt_number": 1,
                        "pathway_label": "Level 2 — Medium",
                        "completed_at": "2026-10-31T09:00:00+00:00",
                        "results": [
                            {"question_id": "q1", "skill_id": "math.number.fraction_representation",
                             "verification_status": "verified", "correct": True, "score": 1, "max_marks": 1},
                            {"question_id": "q2", "skill_id": "math.number.fraction_representation",
                             "verification_status": "verified", "correct": True, "score": 1, "max_marks": 1},
                            {"question_id": "q3", "skill_id": "math.number.fraction_representation",
                             "verification_status": "needs_review", "correct": False, "score": 0, "max_marks": 1},
                        ],
                    }],
                },
            }
        }
        before = repr(progress)
        result = adaptive_learning.build_intervention_timeline(progress)
        self.assertEqual(result["events_total"], 2)
        practice = next(item for item in result["events"] if item["event_type"] == "practice")
        self.assertEqual(practice["total_items"], 2)
        self.assertEqual(practice["accuracy_percent"], 100)
        self.assertEqual(practice["comparison"]["direction"], "Higher recorded performance")
        self.assertEqual(practice["comparison"]["change_percentage_points"], 50)
        self.assertEqual(repr(progress), before)

    def test_intervention_timeline_requires_two_answers_per_comparison(self):
        progress = {
            "algebra": {
                "diagnostics": {
                    "algebra_l1": {
                        "completed_at": "2026-10-30T09:00:00+00:00",
                        "answer_review": [
                            {"skill_tag": "Meaning of a variable", "correct": False},
                        ],
                    }
                },
                "practice_attempts": {
                    "algebra_l1": [{
                        "pathway_label": "Level 1 — Easy",
                        "completed_at": "2026-10-31T09:00:00+00:00",
                        "results": [
                            {"question_id": "q1", "skill_id": "math.algebra.variables_expressions",
                             "verification_status": "verified", "correct": True},
                        ],
                    }],
                },
            }
        }
        result = adaptive_learning.build_intervention_timeline(progress)
        self.assertEqual(result["comparable_events"], 0)
        practice = next(item for item in result["events"] if item["event_type"] == "practice")
        self.assertIsNone(practice["comparison"])
        self.assertEqual(practice["total_items"], 1)

    def test_intervention_timeline_groups_verified_coach_answers_by_day(self):
        progress = {
            "algebra": {
                "coach": {
                    "attempts": [
                        {"lesson_id": "algebra_l1", "skill_id": "math.algebra.variables_expressions",
                         "verification_status": "verified", "correct": True,
                         "completed_at": "2026-11-01T09:00:00+00:00"},
                        {"lesson_id": "algebra_l1", "skill_id": "math.algebra.variables_expressions",
                         "verification_status": "verified", "correct": False,
                         "completed_at": "2026-11-01T10:00:00+00:00"},
                        {"lesson_id": "algebra_l1", "skill_id": "math.algebra.variables_expressions",
                         "verification_status": "needs_review", "correct": True,
                         "completed_at": "2026-11-01T11:00:00+00:00"},
                    ]
                }
            }
        }
        result = adaptive_learning.build_intervention_timeline(progress)
        self.assertEqual(result["events_total"], 1)
        event = result["events"][0]
        self.assertEqual(event["event_type"], "coach")
        self.assertEqual(event["total_items"], 2)
        self.assertEqual(event["accuracy_percent"], 50)

    def test_intervention_timeline_ignores_unmapped_diagnostics_and_empty_progress(self):
        empty = adaptive_learning.build_intervention_timeline({})
        self.assertEqual(empty["events"], [])
        progress = {
            "fractions": {
                "diagnostics": {
                    "fractions_l1": {
                        "completed_at": "2026-10-30T09:00:00+00:00",
                        "answer_review": [
                            {"skill_tag": "Unknown label", "correct": False},
                        ],
                    }
                }
            }
        }
        result = adaptive_learning.build_intervention_timeline(progress)
        self.assertEqual(result["events"], [])




    def test_diagnostic_identifies_specific_skill_before_practice_exists(self):
        progress = {"fractions": {"diagnostics": {"fractions_l1": {
            "answer_review": [
                {"skill_tag": "Meaning of the denominator", "correct": False, "score": 0, "max_marks": 1},
                {"skill_tag": "Representing fractions", "correct": False, "score": 0, "max_marks": 1},
                {"skill_tag": "Equivalent fractions", "correct": True, "score": 1, "max_marks": 1},
            ],
        }}, "practice_attempts": {}}}
        plan = adaptive_learning.build_learning_plan(progress)
        action = next(row for row in plan["actions"] if row["skill_id"] == "math.number.fraction_representation")
        self.assertEqual(action["evidence_source"], "diagnostic")
        self.assertEqual(action["accuracy_percent"], 33)
        self.assertEqual(plan["skills_with_diagnostic_evidence"], 1)
        self.assertEqual(plan["skills_with_practice_evidence"], 0)

    def test_prerequisite_reason_names_diagnostic_evidence_source(self):
        progress = {"fractions": {"diagnostics": {"fractions_l1": {
            "answer_review": [
                {"skill_tag": "Meaning of the denominator", "correct": False, "score": 0, "max_marks": 1},
                {"skill_tag": "Applying fractions in context", "correct": False, "score": 0, "max_marks": 1},
            ],
        }}, "practice_attempts": {}}}
        plan = adaptive_learning.build_learning_plan(progress)
        prerequisite_actions = [
            row for row in plan["actions"]
            if row["is_prerequisite_review"] and row["evidence_source"] == "diagnostic"
        ]
        self.assertTrue(prerequisite_actions)
        self.assertIn("baseline diagnostic evidence", prerequisite_actions[0]["reason"])
        self.assertNotIn("practice-evidence threshold", prerequisite_actions[0]["reason"])

    def test_practice_evidence_takes_precedence_over_diagnostic(self):
        progress = {"fractions": {
            "diagnostics": {"fractions_l1": {"answer_review": [
                {"skill_tag": "Meaning of the denominator", "correct": False, "score": 0, "max_marks": 1},
            ]}},
            "practice_attempts": {"fractions_l1": [{
                "completed_at": "2026-11-02T10:00:00+00:00",
                "results": [{"question_id": "fractions_l1_q1",
                    "skill_id": "math.number.fraction_representation",
                    "correct": True, "score": 1, "max_marks": 1}],
            }]},
        }}
        plan = adaptive_learning.build_learning_plan(progress)
        action = next(row for row in plan["actions"] if row["skill_id"] == "math.number.fraction_representation")
        self.assertEqual(action["evidence_source"], "practice")
        self.assertEqual(action["accuracy_percent"], 100)

if __name__ == "__main__":
    unittest.main()
