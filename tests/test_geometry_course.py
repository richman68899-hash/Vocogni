"""Acceptance tests for the Basic Geometry learning path."""
import unittest

import data
import logic
import math_grading


class BasicGeometryCourseTests(unittest.TestCase):
    def setUp(self):
        self.course = data.get_course("basic_geometry")

    def test_course_is_registered_in_the_catalog(self):
        self.assertIsNotNone(self.course)
        self.assertIn("basic_geometry", data.COURSE_ORDER)
        self.assertEqual(self.course["title"], "Basic Geometry")
        self.assertEqual(self.course["subject_id"], "mathematics")
        self.assertEqual(len(self.course["lessons"]), 5)

    def test_requested_learning_path_and_question_counts(self):
        lessons = self.course["lessons"]
        self.assertEqual(
            [lesson["title"] for lesson in lessons],
            [
                "Angles",
                "Perimeter",
                "Area",
                "Mixed Application",
                "Final Check — Post-test",
            ],
        )
        for lesson in lessons[:4]:
            with self.subTest(lesson=lesson["title"]):
                self.assertEqual(len(lesson["practice_questions"]), 5)
        self.assertEqual(len(lessons[4]["practice_questions"]), 8)
        self.assertEqual(lessons[3]["kind"], "application")
        self.assertEqual(lessons[4]["kind"], "assessment")

    def test_question_ids_are_unique_and_answers_are_configured(self):
        ids = []
        for lesson in self.course["lessons"]:
            self.assertTrue(lesson.get("explanation"))
            self.assertTrue(lesson.get("worked_example"))
            for question in lesson["practice_questions"]:
                ids.append(question["id"])
                self.assertIn(question["type"], {"mc", "numeric", "open_ended"})
                self.assertTrue(question.get("explanation"))
                self.assertTrue(question.get("mistake_tag"))
                if question["type"] == "mc":
                    self.assertIn(question["answer"], question["options"])
                elif question["type"] == "numeric":
                    self.assertIsInstance(question["answer"], (int, float))
                else:
                    self.assertEqual(math_grading.validate_open_response_question(question), [])
        self.assertEqual(len(ids), len(set(ids)))

    def test_every_authored_answer_receives_full_credit(self):
        for lesson in self.course["lessons"]:
            for question in lesson["practice_questions"]:
                with self.subTest(lesson=lesson["title"], question=question["id"]):
                    if question["type"] in {"mc", "numeric"}:
                        self.assertTrue(logic.check_answer(question, question["answer"]))
                    else:
                        result = math_grading.evaluate_open_response(
                            question, question["answer"]
                        )
                        self.assertTrue(result["full_credit"])
                        self.assertEqual(result["score"], result["max_marks"])

    def test_challenge_checks_both_area_and_perimeter(self):
        challenge = self.course["lessons"][3]["practice_questions"][-1]
        result = math_grading.evaluate_open_response(challenge, challenge["answer"])
        self.assertEqual(result["score"], 4)
        self.assertEqual(result["max_marks"], 4)
        self.assertTrue(result["full_credit"])


if __name__ == "__main__":
    unittest.main()
