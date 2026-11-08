"""Regression tests for verified learning-evidence provenance."""
import unittest
from unittest.mock import patch

import adaptive_learning


class VerifiedLearningEvidenceTests(unittest.TestCase):
    def test_only_verified_registry_questions_and_verified_attempts_count(self):
        skill_id = "math.number.fraction_representation"
        registry = [
            {
                "course_id": "fractions",
                "lesson_id": "fraction_basics",
                "question_id": "verified-q",
                "verification_status": "verified",
                "question": {
                    "skill_id": skill_id,
                    "mistake_tag": "equivalent fractions",
                },
            },
            {
                "course_id": "fractions",
                "lesson_id": "fraction_basics",
                "question_id": "needs-review-q",
                "verification_status": "needs_review",
                "question": {
                    "skill_id": skill_id,
                    "mistake_tag": "equivalent fractions",
                },
            },
        ]
        progress = {
            "fractions": {
                "practice_attempts": {
                    "fraction_basics": [
                        {
                            "completed_at": "2026-11-08T10:00:00+00:00",
                            "results": [
                                {
                                    "question_id": "verified-q",
                                    "verification_status": "verified",
                                    "skill_id": skill_id,
                                    "correct": True,
                                },
                                {
                                    "question_id": "verified-q",
                                    "verification_status": "legacy",
                                    "skill_id": skill_id,
                                    "correct": False,
                                },
                                {
                                    "question_id": "needs-review-q",
                                    "verification_status": "verified",
                                    "skill_id": skill_id,
                                    "correct": False,
                                },
                                {
                                    "question_id": "unknown-q",
                                    "verification_status": "verified",
                                    "skill_id": skill_id,
                                    "correct": False,
                                },
                                {
                                    "question_id": "verified-q",
                                    "verification_status": "verified",
                                    "skill_id": "math.algebra.linear_equations",
                                    "correct": False,
                                },
                            ],
                        }
                    ]
                }
            }
        }

        with patch.object(
            adaptive_learning.question_engine,
            "iter_question_records",
            return_value=registry,
        ):
            evidence = adaptive_learning._collect_skill_evidence(progress)

        item = evidence[skill_id]
        self.assertEqual(item["attempts"], 1)
        self.assertEqual(item["accuracy"], 1.0)
        self.assertEqual(item["mistake_tags"], {})
        self.assertEqual(item["recent_ratios"], [("2026-11-08T10:00:00+00:00", 1.0)])

    def test_unverified_question_registry_cannot_create_skill_locations(self):
        skill_id = "math.number.fraction_representation"
        registry = [
            {
                "course_id": "fractions",
                "lesson_id": "fraction_basics",
                "question_id": "legacy-q",
                "verification_status": "legacy",
                "question": {"skill_id": skill_id},
            }
        ]
        progress = {
            "fractions": {
                "practice_attempts": {
                    "fraction_basics": [{
                        "results": [{
                            "question_id": "legacy-q",
                            "verification_status": "verified",
                            "skill_id": skill_id,
                            "correct": True,
                        }]
                    }]
                }
            }
        }

        with patch.object(
            adaptive_learning.question_engine,
            "iter_question_records",
            return_value=registry,
        ):
            evidence = adaptive_learning._collect_skill_evidence(progress)

        self.assertEqual(evidence[skill_id]["attempts"], 0)
        self.assertEqual(evidence[skill_id]["locations"], [])


if __name__ == "__main__":
    unittest.main()
