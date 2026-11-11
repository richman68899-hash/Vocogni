"""Tests for the course-schema-driven Mastery Receipt."""
import unittest
from unittest.mock import patch

import data
import logic
import question_engine


def _question(question_id, skill, *, mistake_tag=None, question_type="mc"):
    question = {
        "id": question_id,
        "type": question_type,
        "prompt": f"Question for {skill}",
        "answer": "A",
        "explanation": "Configured explanation.",
        "skill_tag": skill,
        "mistake_tag": mistake_tag or skill,
    }
    if question_type == "mc":
        question["options"] = ["A", "B"]
    return question


def _course(course_id, questions, *, diagnostic_questions=None):
    lesson = {
        "id": f"{course_id}_lesson",
        "title": "A newly authored lesson",
        "kind": "standard",
        "explanation": "A concept explanation.",
        "worked_example": "A worked example.",
        "practice_questions": questions,
    }
    if diagnostic_questions is not None:
        lesson["diagnostic"] = {"questions": diagnostic_questions}
    return {
        "id": course_id,
        "title": "Unseen New Course",
        "topic_label": "Unseen Topic",
        "lessons": [lesson],
    }


class MasteryReceiptTests(unittest.TestCase):
    def _registered_course(self, course):
        course_id = course["id"]
        records = []
        for lesson in course.get("lessons", []):
            for question in lesson.get("practice_questions", []):
                records.append({
                    "course_id": course_id,
                    "lesson_id": lesson["id"],
                    "question_id": question["id"],
                    "verification_status": "verified",
                    "question": question,
                })
        return (
            patch.dict(data.COURSES, {course_id: course}),
            patch.object(data, "COURSE_ORDER", list(data.COURSE_ORDER) + [course_id]),
            patch.object(question_engine, "iter_question_records", return_value=records),
        )

    def test_receipt_adapts_to_a_new_course_without_course_specific_rules(self):
        course_id = "unseen_course_for_receipt_test"
        questions = [
            _question("q1", "Vector components"),
            _question("q2", "Vector components"),
            _question("q3", "Vector components"),
            _question("q4", "Direction conventions"),
        ]
        course = _course(course_id, questions)
        contexts = self._registered_course(course)
        with contexts[0], contexts[1], contexts[2]:
            progress = {
                course_id: {
                    "practice_attempts": {
                        f"{course_id}_lesson": [{
                            "attempt_number": 1,
                            "completed_at": "2026-10-20T10:00:00+00:00",
                            "results": [
                                {"question_id": "q1", "verification_status": "verified", "correct": True},
                                {"question_id": "q2", "verification_status": "verified", "correct": True},
                                {"question_id": "q3", "verification_status": "verified", "correct": True},
                                {"question_id": "q4", "verification_status": "verified", "correct": False},
                            ],
                        }]
                    }
                }
            }
            receipt = logic.mastery_receipt_for_course(progress, course_id)

        self.assertEqual(receipt["course_id"], course_id)
        self.assertEqual(receipt["course_title"], "Unseen New Course")
        skills = {item["skill"]: item for item in receipt["skills"]}
        self.assertEqual(skills["Vector components"]["status"], "Promising evidence")
        self.assertEqual(skills["Vector components"]["distinct_practice_questions"], 3)
        self.assertEqual(skills["Vector components"]["practice_performance_percent"], 100)
        self.assertEqual(skills["Direction conventions"]["status"], "Needs review")
        self.assertEqual(receipt["status_counts"]["Promising evidence"], 1)
        self.assertEqual(receipt["status_counts"]["Needs review"], 1)

    def test_repeating_one_question_does_not_count_as_three_distinct_questions(self):
        course_id = "repeat_question_course"
        course = _course(course_id, [_question("same-q", "Rearranging equations")])
        contexts = self._registered_course(course)
        with contexts[0], contexts[1], contexts[2]:
            progress = {
                course_id: {
                    "practice_attempts": {
                        f"{course_id}_lesson": [
                            {
                                "attempt_number": index,
                                "completed_at": f"2026-10-2{index}T10:00:00+00:00",
                                "results": [{"question_id": "same-q", "verification_status": "verified", "correct": True}],
                            }
                            for index in (1, 2, 3)
                        ]
                    }
                }
            }
            receipt = logic.mastery_receipt_for_course(progress, course_id)

        skill = receipt["skills"][0]
        self.assertEqual(skill["practice_answers"], 3)
        self.assertEqual(skill["distinct_practice_questions"], 1)
        self.assertEqual(skill["status"], "Developing")

    def test_cross_lesson_verified_practice_uses_canonical_source_lesson(self):
        course_id = "cross_lesson_receipt_course"
        skill_id = "math.number.fraction_representation"
        source_question = _question("source-q", "Fraction representation")
        attempt_question = _question("attempt-q", "Other lesson skill")
        course = {
            "id": course_id,
            "title": "Cross-lesson receipt course",
            "lessons": [
                {
                    "id": "practice_lesson",
                    "title": "Practice lesson",
                    "practice_questions": [attempt_question],
                },
                {
                    "id": "source_lesson",
                    "title": "Canonical source lesson",
                    "practice_questions": [source_question],
                },
            ],
        }
        registry = [{
            "course_id": course_id,
            "lesson_id": "source_lesson",
            "question_id": "source-q",
            "verification_status": "verified",
            "question": {
                **source_question,
                "skill_id": skill_id,
                "skill_label": "Fraction representation",
            },
        }]
        progress = {
            course_id: {
                "practice_attempts": {
                    "practice_lesson": [{
                        "attempt_number": 1,
                        "completed_at": "2026-11-11T10:00:00+00:00",
                        "results": [{
                            "question_id": "source-q",
                            "lesson_id": "source_lesson",
                            "course_id": course_id,
                            "skill_id": skill_id,
                            "verification_status": "verified",
                            "correct": True,
                        }],
                    }]
                }
            }
        }

        with (
            patch.dict(data.COURSES, {course_id: course}),
            patch.object(data, "COURSE_ORDER", list(data.COURSE_ORDER) + [course_id]),
            patch.object(question_engine, "iter_question_records", return_value=registry),
        ):
            receipt = logic.mastery_receipt_for_course(progress, course_id)

        skill = next(item for item in receipt["skills"] if item["skill_id"] == skill_id)
        self.assertEqual(skill["practice_answers"], 1)
        self.assertEqual(skill["distinct_practice_questions"], 1)
        self.assertEqual(skill["practice_performance_percent"], 100)

    def test_diagnostic_failure_flags_unpractised_skill_for_review(self):
        course_id = "diagnostic_gap_course"
        diagnostic_questions = [
            {
                **_question("diagnostic-q", "Balancing equations"),
                "stage": "prerequisite",
            }
        ]
        course = _course(
            course_id,
            [_question("practice-q", "Balancing equations")],
            diagnostic_questions=diagnostic_questions,
        )
        contexts = self._registered_course(course)
        with contexts[0], contexts[1], contexts[2]:
            progress = {
                course_id: {
                    "diagnostics": {
                        f"{course_id}_lesson": {
                            "completed_at": "2026-10-20T10:00:00+00:00",
                            "answer_review": [{
                                "question_id": "diagnostic-q",
                                "skill_tag": "Balancing equations",
                                "correct": False,
                            }],
                        }
                    }
                }
            }
            receipt = logic.mastery_receipt_for_course(progress, course_id)

        skill = receipt["skills"][0]
        self.assertEqual(skill["status"], "Needs review")
        self.assertTrue(skill["diagnostic_flagged"])
        self.assertIsNone(skill["practice_performance_percent"])

    def test_passing_a_diagnostic_alone_does_not_claim_mastery(self):
        course_id = "diagnostic_only_course"
        diagnostic_questions = [
            {
                **_question("diagnostic-q", "Interpreting gradients"),
                "stage": "prerequisite",
            }
        ]
        course = _course(
            course_id,
            [_question("practice-q", "Interpreting gradients")],
            diagnostic_questions=diagnostic_questions,
        )
        contexts = self._registered_course(course)
        with contexts[0], contexts[1], contexts[2]:
            progress = {
                course_id: {
                    "diagnostics": {
                        f"{course_id}_lesson": {
                            "answer_review": [{
                                "question_id": "diagnostic-q",
                                "skill_tag": "Interpreting gradients",
                                "correct": True,
                            }]
                        }
                    }
                }
            }
            receipt = logic.mastery_receipt_for_course(progress, course_id)

        skill = receipt["skills"][0]
        self.assertEqual(skill["status"], "Not tested")
        self.assertEqual(skill["diagnostic_performance_percent"], 100)

    def test_partial_credit_questions_use_marks_not_only_boolean_correctness(self):
        course_id = "marked_question_course"
        question = _question(
            "open-q", "Equilibrium reasoning", question_type="open_ended"
        )
        course = _course(course_id, [question])
        contexts = self._registered_course(course)
        with contexts[0], contexts[1], contexts[2]:
            progress = {
                course_id: {
                    "practice_attempts": {
                        f"{course_id}_lesson": [{
                            "attempt_number": 1,
                            "results": [{
                                "question_id": "open-q",
                                "verification_status": "verified",
                                "correct": False,
                                "score": 1,
                                "max_marks": 3,
                            }],
                        }]
                    }
                }
            }
            receipt = logic.mastery_receipt_for_course(progress, course_id)

        skill = receipt["skills"][0]
        self.assertEqual(skill["practice_performance_percent"], 33)
        self.assertEqual(skill["status"], "Needs review")

    def test_every_currently_registered_course_gets_a_receipt_from_its_own_schema(self):
        self.assertTrue(data.all_courses_in_order())
        for course in data.all_courses_in_order():
            with self.subTest(course=course["id"]):
                receipt = logic.mastery_receipt_for_course({}, course["id"])
                self.assertIsNotNone(receipt)
                self.assertEqual(receipt["course_id"], course["id"])
                self.assertTrue(receipt["skills"])
                self.assertTrue(
                    all(item["status"] == "Not tested" for item in receipt["skills"])
                )

    def test_unverified_or_unregistered_practice_does_not_enter_receipt(self):
        course_id = "unverified_practice_course"
        course = _course(course_id, [_question("verified-q", "Fraction meaning")])
        contexts = self._registered_course(course)
        with contexts[0], contexts[1], contexts[2]:
            progress = {
                course_id: {
                    "practice_attempts": {
                        f"{course_id}_lesson": [{
                            "results": [
                                {
                                    "question_id": "verified-q",
                                    "verification_status": "legacy",
                                    "correct": True,
                                },
                                {
                                    "question_id": "not-in-registry",
                                    "verification_status": "verified",
                                    "correct": True,
                                },
                            ]
                        }]
                    }
                }
            }
            receipt = logic.mastery_receipt_for_course(progress, course_id)

        skill = receipt["skills"][0]
        self.assertEqual(skill["practice_answers"], 0)
        self.assertIsNone(skill["practice_performance_percent"])
        self.assertEqual(skill["status"], "Not tested")

    def test_unknown_course_returns_none_instead_of_crashing(self):
        self.assertIsNone(logic.mastery_receipt_for_course({}, "not-a-real-course"))


if __name__ == "__main__":
    unittest.main()
