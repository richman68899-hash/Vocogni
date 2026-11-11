"""Tests for the offline, explainable learning-intelligence engine."""
import unittest
from copy import deepcopy
from unittest.mock import patch

import adaptive_learning
import math_taxonomy
import question_engine


def _build_with_verified_fixtures(builder, progress):
    """Give synthetic test questions explicit verified registry provenance."""
    fixture_progress = deepcopy(progress)
    records = []
    for course_id, course_progress in fixture_progress.items():
        if not isinstance(course_progress, dict):
            continue
        attempts_by_lesson = course_progress.get("practice_attempts", {})
        if not isinstance(attempts_by_lesson, dict):
            continue
        for lesson_id, attempts in attempts_by_lesson.items():
            if not isinstance(attempts, list):
                continue
            for attempt in attempts:
                if not isinstance(attempt, dict):
                    continue
                for result in attempt.get("results", []):
                    if not isinstance(result, dict):
                        continue
                    question_id = str(result.get("question_id") or "")
                    skill_id = result.get("skill_id")
                    if not question_id or not skill_id:
                        continue
                    result["verification_status"] = "verified"
                    records.append({
                        "course_id": course_id,
                        "lesson_id": lesson_id,
                        "question_id": question_id,
                        "verification_status": "verified",
                        "question": {"skill_id": skill_id},
                    })
    with patch.object(question_engine, "iter_question_records", return_value=records):
        return builder(fixture_progress)


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
        plan = _build_with_verified_fixtures(adaptive_learning.build_learning_plan, progress)
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
                            {"question_id": "algebra_l2_prerequisite_q1", "skill_id": prerequisite, "correct": False, "score": 0, "max_marks": 1},
                        ],
                    }]
                }
            }
        }
        plan = _build_with_verified_fixtures(adaptive_learning.build_learning_plan, progress)
        self.assertTrue(plan["actions"])
        self.assertEqual(plan["actions"][0]["skill_id"], prerequisite)
        self.assertTrue(plan["actions"][0]["is_prerequisite_review"])

    def test_single_item_diagnostic_signal_requires_confirmation(self):
        progress = {
            "fractions": {
                "diagnostics": {
                    "fractions_l1": {
                        "completed_at": "2026-10-30T09:00:00+00:00",
                        "answer_review": [{
                            "question_id": "fractions_l1_d1",
                            "skill_tag": "Meaning of the denominator",
                            "correct": False,
                        }],
                    }
                }
            }
        }
        plan = adaptive_learning.build_learning_plan(progress)
        action = next(
            item for item in plan["actions"]
            if item["skill_id"] == "math.number.fraction_representation"
        )
        self.assertTrue(action["confirmation_required"])
        self.assertEqual(action["diagnostic_items"], 1)
        self.assertEqual(action["evidence_strength"], "single_diagnostic_item")
        self.assertIn("another distinct question", action["action"])
        self.assertIn("preliminary signal", action["reason"])
        self.assertIn("fractions_l1_d1", action["evidence_question_ids"])
        self.assertEqual(action["confirmation_items"], 0)

    def test_two_distinct_diagnostic_items_are_counted_separately(self):
        progress = {
            "fractions": {
                "diagnostics": {
                    "fractions_l1": {
                        "completed_at": "2026-10-30T09:00:00+00:00",
                        "answer_review": [
                            {"question_id": "fractions_l1_d1", "skill_tag": "Meaning of the denominator", "correct": False},
                            {"question_id": "fractions_l1_d2", "skill_tag": "Representing fractions", "correct": False},
                            {"question_id": "fractions_l1_d2", "skill_tag": "Representing fractions", "correct": False},
                        ],
                    }
                }
            }
        }
        plan = adaptive_learning.build_learning_plan(progress)
        action = next(
            item for item in plan["actions"]
            if item["skill_id"] == "math.number.fraction_representation"
        )
        self.assertEqual(action["diagnostic_items"], 2)
        self.assertFalse(action["confirmation_required"])
        self.assertEqual(action["evidence_strength"], "multiple_diagnostic_items")

    def test_saved_skill_confirmation_counts_as_a_second_diagnostic_evidence_item(self):
        progress = {
            "fractions": {
                "diagnostics": {
                    "fractions_l1": {
                        "completed_at": "2026-10-30T09:00:00+00:00",
                        "answer_review": [{
                            "question_id": "fractions_l1_d1",
                            "skill_tag": "Meaning of the denominator",
                            "correct": False,
                        }]
                    }
                },
                "skill_confirmation_attempts": [{
                    "lesson_id": "fractions_l1",
                    "completed_at": "2026-10-30T09:10:00+00:00",
                    "results": [{
                        "question_id": "fractions_l1_q2",
                        "lesson_id": "fractions_l1",
                        "skill_id": "math.number.fraction_representation",
                        "verification_status": "verified",
                        "correct": True,
                        "score": 1,
                        "max_marks": 1,
                    }]
                }]
            }
        }
        records = [{
            "course_id": "fractions",
            "lesson_id": "fractions_l1",
            "question_id": "fractions_l1_q2",
            "verification_status": "verified",
            "question": {"skill_id": "math.number.fraction_representation"},
        }]
        with patch.object(question_engine, "iter_question_records", return_value=records):
            plan = adaptive_learning.build_learning_plan(progress)
        action = next(item for item in plan["actions"] if item["skill_id"] == "math.number.fraction_representation")
        self.assertFalse(action["confirmation_required"])
        self.assertEqual(action["diagnostic_items"], 2)
        self.assertEqual(action["confirmation_items"], 1)
        self.assertIn("fractions_l1_q2", action["evidence_question_ids"])
        self.assertEqual(plan["skills_with_practice_evidence"], 0)

    def test_unverified_confirmation_cannot_change_diagnostic_evidence(self):
        progress = {
            "fractions": {
                "diagnostics": {
                    "fractions_l1": {"answer_review": [{
                        "question_id": "fractions_l1_d1",
                        "skill_tag": "Meaning of the denominator",
                        "correct": False,
                    }]}
                },
                "skill_confirmation_attempts": [{
                    "lesson_id": "fractions_l1",
                    "results": [{
                        "question_id": "unreviewed_q",
                        "skill_id": "math.number.fraction_representation",
                        "verification_status": "verified",
                        "correct": True,
                    }]
                }]
            }
        }
        with patch.object(question_engine, "iter_question_records", return_value=[]):
            plan = adaptive_learning.build_learning_plan(progress)
        action = next(item for item in plan["actions"] if item["skill_id"] == "math.number.fraction_representation")
        self.assertTrue(action["confirmation_required"])
        self.assertEqual(action["diagnostic_items"], 1)
        self.assertEqual(action["confirmation_items"], 0)

    def test_cross_lesson_verified_practice_uses_canonical_source_provenance(self):
        skill_id = "math.time.clock_parts"
        progress = {
            "analog_clocks": {
                "practice_attempts": {
                    "clock_l1": [{
                        "completed_at": "2026-11-11T10:00:00+00:00",
                        "results": [{
                            "question_id": "clock_l6_q7",
                            "lesson_id": "clock_l6",
                            "course_id": "analog_clocks",
                            "skill_id": skill_id,
                            "verification_status": "verified",
                            "correct": True,
                        }],
                    }]
                }
            }
        }
        registry = [{
            "course_id": "analog_clocks",
            "lesson_id": "clock_l6",
            "question_id": "clock_l6_q7",
            "verification_status": "verified",
            "question": {"skill_id": skill_id, "mistake_tag": "Clock hand roles"},
        }]

        with patch.object(question_engine, "iter_question_records", return_value=registry):
            evidence = adaptive_learning._collect_skill_evidence(progress)

        item = evidence[skill_id]
        self.assertEqual(item["attempts"], 1)
        self.assertEqual(item["accuracy"], 1.0)
        self.assertIn(("analog_clocks", "clock_l6", "clock_l6_q7"), item["practice_question_ids"])

    def test_plan_uses_existing_skill_taxonomy_and_does_not_mutate_progress(self):
        progress = {"fractions": {"practice_attempts": {}}}
        before = repr(progress)
        plan = _build_with_verified_fixtures(adaptive_learning.build_learning_plan, progress)
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
        result = _build_with_verified_fixtures(adaptive_learning.build_skill_trajectories, progress)
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
        result = _build_with_verified_fixtures(adaptive_learning.build_skill_trajectories, progress)
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
        result = _build_with_verified_fixtures(adaptive_learning.build_skill_trajectories, progress)
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
        plan = _build_with_verified_fixtures(adaptive_learning.build_learning_plan, progress)
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
        plan = _build_with_verified_fixtures(adaptive_learning.build_learning_plan, progress)
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
                "results": [
                    {"question_id": "fractions_l1_q1",
                     "skill_id": "math.number.fraction_representation",
                     "correct": True, "score": 1, "max_marks": 1},
                    {"question_id": "fractions_l1_q2",
                     "skill_id": "math.number.fraction_representation",
                     "correct": False, "score": 0, "max_marks": 1,
                     "mistake_tag": "Denominator confusion"},
                ],
            }]},
        }}
        plan = _build_with_verified_fixtures(adaptive_learning.build_learning_plan, progress)
        action = next(row for row in plan["actions"] if row["skill_id"] == "math.number.fraction_representation")
        self.assertEqual(action["evidence_source"], "practice")
        self.assertEqual(action["accuracy_percent"], 50)

    def test_untested_prerequisite_is_a_check_not_a_weakness(self):
        skill_id = "math.algebra.linear_equations"
        prerequisite = "math.algebra.variables_expressions"
        progress = {"algebra": {"practice_attempts": {"algebra_l2": [{
            "completed_at": "2026-11-08T10:00:00+00:00",
            "results": [
                {"question_id": "linear_q1", "skill_id": skill_id, "verification_status": "verified", "correct": False, "score": 0, "max_marks": 1},
                {"question_id": "linear_q2", "skill_id": skill_id, "verification_status": "verified", "correct": False, "score": 0, "max_marks": 1},
            ],
        }]}}}
        records = [
            {"course_id": "algebra", "lesson_id": "algebra_l2", "question_id": qid,
             "verification_status": "verified", "question": {"skill_id": skill_id}}
            for qid in ("linear_q1", "linear_q2")
        ]
        records.append({
            "course_id": "algebra", "lesson_id": "algebra_l2",
            "question_id": "variables_check_q1", "verification_status": "verified",
            "question": {"skill_id": prerequisite},
        })
        with (
            patch.object(question_engine, "iter_question_records", return_value=records),
            patch.object(adaptive_learning, "_lesson_for_skill", return_value=("algebra", "algebra_l2")),
        ):
            plan = adaptive_learning.build_learning_plan(progress)
        action = next(row for row in plan["actions"] if row["skill_id"] == prerequisite)
        self.assertEqual(action["evidence_source"], "none")
        self.assertIsNone(action["accuracy_percent"])
        self.assertEqual(action["attempts"], 0)
        self.assertTrue(action["is_prerequisite_check"])
        self.assertFalse(action["is_prerequisite_review"])
        self.assertIn("no recorded", action["reason"].lower())
        self.assertNotIn("below the 75%", action["reason"])

    def test_shared_prerequisite_is_recommended_only_once(self):
        variables = "math.algebra.variables_expressions"
        progress = {"algebra": {"practice_attempts": {"algebra_l2": [{
            "completed_at": "2026-11-08T10:00:00+00:00",
            "results": [
                {"question_id": "variables_q1", "skill_id": variables, "correct": False, "score": 0, "max_marks": 1},
                {"question_id": "variables_q2", "skill_id": variables, "correct": False, "score": 0, "max_marks": 1},
                {"question_id": "equations_q1", "skill_id": "math.algebra.linear_equations", "correct": False, "score": 0, "max_marks": 1},
                {"question_id": "equations_q2", "skill_id": "math.algebra.linear_equations", "correct": False, "score": 0, "max_marks": 1},
                {"question_id": "translation_q1", "skill_id": "math.problem_solving.expression_translation", "correct": False, "score": 0, "max_marks": 1},
                {"question_id": "translation_q2", "skill_id": "math.problem_solving.expression_translation", "correct": False, "score": 0, "max_marks": 1},
            ],
        }]}}}
        plan = _build_with_verified_fixtures(adaptive_learning.build_learning_plan, progress)
        target_ids = [row["skill_id"] for row in plan["actions"]]
        self.assertEqual(
            target_ids.count(variables),
            1,
            "A shared prerequisite should not occupy multiple recommendation slots.",
        )

    def test_intervention_timeline_includes_verified_transfer_separately(self):
        progress = {
            "fractions": {
                "transfer_checks": [{
                    "question_id": "fractions_l1_project_q1",
                    "lesson_id": "fractions_l1",
                    "practice_lesson_id": "fractions_l2",
                    "skill_id": "math.number.fraction_operations",
                    "source_skill_id": "math.number.fraction_operations",
                    "verification_status": "verified",
                    "question_purpose": "application",
                    "evidence_type": "independent_transfer",
                    "independent": True,
                    "correct": True,
                    "recorded_at": "2026-11-08T10:00:00+00:00",
                    "attempt_number": 1,
                }]
            }
        }
        registry_record = {
            "course_id": "fractions",
            "lesson_id": "fractions_l1",
            "question_id": "fractions_l1_project_q1",
            "verification_status": "verified",
            "question": {
                "skill_id": "math.number.fraction_operations",
                "purpose": "application",
            },
        }
        with patch.object(question_engine, "iter_question_records", return_value=[registry_record]):
            result = adaptive_learning.build_intervention_timeline(progress)
        transfer = next(item for item in result["events"] if item["event_type"] == "transfer")
        self.assertEqual(transfer["lesson_id"], "fractions_l2")
        self.assertEqual(transfer["source_lesson_id"], "fractions_l1")
        self.assertEqual(transfer["intervention_label"], "Independent transfer check")
        self.assertEqual(transfer["accuracy_percent"], 100)
        self.assertEqual(transfer["total_items"], 1)
        self.assertIsNone(transfer["comparison"])

    def test_intervention_timeline_rejects_unverified_or_mismatched_transfer(self):
        progress = {"fractions": {"transfer_checks": [
            {
                "question_id": "fractions_l1_project_q1",
                "lesson_id": "fractions_l1",
                "practice_lesson_id": "fractions_l2",
                "source_skill_id": "math.number.fraction_operations",
                "verification_status": "needs_review",
                "evidence_type": "independent_transfer",
                "independent": True,
                "correct": True,
                "recorded_at": "2026-11-08T10:00:00+00:00",
            },
            {
                "question_id": "fractions_l1_project_q1",
                "lesson_id": "fractions_l1",
                "practice_lesson_id": "fractions_l2",
                "source_skill_id": "math.algebra.linear_equations",
                "verification_status": "verified",
                "evidence_type": "independent_transfer",
                "independent": True,
                "correct": True,
                "recorded_at": "2026-11-08T10:01:00+00:00",
            },
        ]}}
        registry_record = {
            "course_id": "fractions",
            "lesson_id": "fractions_l1",
            "question_id": "fractions_l1_project_q1",
            "verification_status": "verified",
            "question": {
                "skill_id": "math.number.fraction_operations",
                "purpose": "application",
            },
        }
        with patch.object(question_engine, "iter_question_records", return_value=[registry_record]):
            result = adaptive_learning.build_intervention_timeline(progress)
        self.assertFalse(any(item["event_type"] == "transfer" for item in result["events"]))

if __name__ == "__main__":
    unittest.main()
