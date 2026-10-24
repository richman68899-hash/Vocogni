"""Tests for the course-agnostic Personalized Revision Sprint."""
import unittest
from unittest.mock import patch

import data
import logic
import revision_sprint


def _mc(qid, skill, *, answer="A"):
    return {
        "id": qid,
        "type": "mc",
        "prompt": f"Choose an answer for {skill}.",
        "options": ["A", "B", "C"],
        "answer": answer,
        "explanation": f"Explanation for {skill}.",
        "skill_tag": skill,
        "mistake_tag": skill,
    }


def _numeric(qid, skill, answer=2):
    return {
        "id": qid,
        "type": "numeric",
        "prompt": f"Calculate the value for {skill}.",
        "answer": answer,
        "tolerance": 0.01,
        "whole_number": True,
        "explanation": f"Work through {skill}.",
        "skill_tag": skill,
        "mistake_tag": skill,
    }


def _open(qid, skill):
    return {
        "id": qid,
        "type": "open_ended",
        "grader": "math",
        "prompt": f"Show the method for {skill}.",
        "answer": "x = 2",
        "accepted_answers": [],
        "explanation": f"Method for {skill}.",
        "skill_tag": skill,
        "mistake_tag": skill,
        "max_marks": 1,
        "marking_points": [{
            "id": "value",
            "criteria": "Obtains x = 2",
            "marks": 1,
            "numeric_targets": [{"value": 2, "tolerance": 0}],
        }],
    }


def _course(course_id, lessons):
    return {
        "id": course_id,
        "title": "Test Revision Course",
        "topic_label": "Test Revision",
        "short_description": "Test content",
        "lessons": lessons,
    }


class RevisionSprintTests(unittest.TestCase):
    def _registered_course(self, course):
        course_id = course["id"]
        return (
            patch.dict(data.COURSES, {course_id: course}),
            patch.object(data, "COURSE_ORDER", list(data.COURSE_ORDER) + [course_id]),
        )

    def test_question_bank_supports_mc_numeric_and_open_responses_and_deduplicates(self):
        q1 = _mc("q1", "Fractions")
        q2 = _numeric("q2", "Arithmetic")
        q3 = _open("q3", "Algebra")
        course = _course("revision_bank_test", [{
            "id": "lesson_1",
            "title": "Mixed practice",
            "practice_questions": [q1, q2, q3],
            "questions": [q1],
            "interactive_question": q2,
            "diagnostic": {"questions": [_mc("diagnostic_only", "Diagnostic")]},
        }])
        contexts = self._registered_course(course)
        with contexts[0], contexts[1]:
            bank = revision_sprint.question_bank_for_course(course["id"])

        self.assertEqual({item["question_id"] for item in bank}, {"q1", "q2", "q3"})
        self.assertEqual(len(bank), 3)
        self.assertTrue(all(item["lesson_id"] == "lesson_1" for item in bank))

    def test_personalized_selection_prioritizes_a_previously_missed_question(self):
        course = _course("revision_priority_test", [{
            "id": "lesson_1",
            "title": "Core skills",
            "questions": [
                _mc("q1", "Alpha"),
                _mc("q2", "Beta"),
                _mc("q3", "Gamma"),
            ],
        }])
        progress = {
            course["id"]: {
                "practice_attempts": {
                    "lesson_1": [{
                        "attempt_number": 1,
                        "completed_at": "2026-10-22T12:00:00+00:00",
                        "results": [{"question_id": "q1", "correct": False}],
                    }]
                }
            }
        }
        contexts = self._registered_course(course)
        receipt = {"skills": [
            {"skill": "Alpha", "status": "Promising evidence", "practice_performance_percent": 90},
            {"skill": "Beta", "status": "Developing", "practice_performance_percent": 70},
            {"skill": "Gamma", "status": "Not tested", "practice_performance_percent": None},
        ]}
        with contexts[0], contexts[1], patch.object(logic, "mastery_receipt_for_course", return_value=receipt):
            selected = revision_sprint.select_questions(
                progress, course["id"], count=3, mode="personalized"
            )

        self.assertEqual(selected[0]["question_id"], "q1")
        self.assertEqual(len({item["question_id"] for item in selected}), 3)

    def test_whole_course_mix_rotates_across_lessons(self):
        course = _course("revision_mix_test", [
            {
                "id": "lesson_1",
                "title": "Lesson one",
                "questions": [_mc("q1", "Skill A"), _mc("q2", "Skill A")],
            },
            {
                "id": "lesson_2",
                "title": "Lesson two",
                "questions": [_mc("q3", "Skill B"), _mc("q4", "Skill B")],
            },
        ])
        contexts = self._registered_course(course)
        with contexts[0], contexts[1], patch.object(
            logic,
            "mastery_receipt_for_course",
            return_value={"skills": []},
        ):
            selected = revision_sprint.select_questions(
                {}, course["id"], count=2, mode="balanced"
            )

        self.assertEqual(len(selected), 2)
        self.assertEqual(
            {item["lesson_id"] for item in selected},
            {"lesson_1", "lesson_2"},
        )

    def test_answer_grading_uses_existing_marking_rules(self):
        open_question = _open("q_open", "Algebra")
        correct = revision_sprint.evaluate_question(open_question, "x = 2")
        incorrect = revision_sprint.evaluate_question(open_question, "x = 5")

        self.assertTrue(correct["correct"])
        self.assertEqual(correct["score"], 1)
        self.assertEqual(correct["max_marks"], 1)
        self.assertFalse(incorrect["correct"])
        self.assertEqual(incorrect["score"], 0)

    def test_completed_sprint_saves_attempts_and_updates_course_totals(self):
        progress = {"revision_store_test": logic.blank_course_progress()}
        q1 = _mc("q1", "Fractions")
        q2 = _numeric("q2", "Arithmetic")
        graded_items = [
            {
                "item": {
                    "lesson_id": "lesson_1",
                    "lesson_title": "Fractions",
                    "skill": "Fractions",
                    "question_id": "q1",
                    "question": q1,
                },
                "answer": "A",
                "evaluation": {
                    "correct": True,
                    "score": 1,
                    "max_marks": 1,
                    "marking_result": None,
                },
            },
            {
                "item": {
                    "lesson_id": "lesson_2",
                    "lesson_title": "Arithmetic",
                    "skill": "Arithmetic",
                    "question_id": "q2",
                    "question": q2,
                },
                "answer": 4,
                "evaluation": {
                    "correct": False,
                    "score": 0,
                    "max_marks": 1,
                    "marking_result": None,
                },
            },
        ]

        summary = revision_sprint.record_sprint_attempt(
            progress,
            "revision_store_test",
            graded_items,
            completed_at="2026-10-24T08:00:00+00:00",
        )
        course_progress = progress["revision_store_test"]

        self.assertEqual(summary["questions"], 2)
        self.assertEqual(summary["practice_attempts_saved"], 2)
        self.assertEqual(summary["percent"], 50)
        self.assertEqual(course_progress["questions_attempted"], 2)
        self.assertEqual(course_progress["correct_answers"], 1)
        self.assertEqual(len(course_progress["practice_attempts"]["lesson_1"]), 1)
        self.assertEqual(
            course_progress["practice_attempts"]["lesson_2"][0]["pathway_label"],
            "Personalized Revision Sprint",
        )
        self.assertEqual(
            course_progress["practice_attempts"]["lesson_2"][0]["results"][0]["question_id"],
            "q2",
        )


if __name__ == "__main__":
    unittest.main()
