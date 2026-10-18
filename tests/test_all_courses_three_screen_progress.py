"""Regression tests for all-course diagnostic-first structured lessons and persistence."""
import unittest

import data
import diagnostics
import logic


class AllCoursesThreeScreenTests(unittest.TestCase):
    def test_each_course_has_a_course_entry_diagnostic(self):
        for course in data.all_courses_in_order():
            with self.subTest(course=course["id"]):
                diagnostic_lesson_id = logic.course_diagnostic_lesson_id(course["id"])
                self.assertIsNotNone(diagnostic_lesson_id)
                lesson, _ = data.get_lesson(course["id"], diagnostic_lesson_id)
                self.assertIsNotNone(lesson)
                self.assertEqual(
                    diagnostics.validate_diagnostic_config(lesson["diagnostic"]), []
                )

    def test_every_learning_lesson_has_three_screen_content(self):
        seen_question_ids = set()
        for course in data.all_courses_in_order():
            self.assertGreaterEqual(len(course["lessons"]), 1)
            self.assertEqual(course["lesson_count"], len(course["lessons"]))
            for lesson in course["lessons"]:
                with self.subTest(course=course["id"], lesson=lesson["id"]):
                    self.assertTrue(lesson.get("explanation", "").strip())
                    self.assertTrue(lesson.get("worked_example", "").strip())
                    question = lesson.get("interactive_question")
                    self.assertIsInstance(question, dict)
                    for field in ("id", "type", "prompt", "answer", "explanation", "mistake_tag"):
                        self.assertIn(field, question)
                    self.assertNotIn(question["id"], seen_question_ids)
                    seen_question_ids.add(question["id"])
                    self.assertIn(question["type"], ("mc", "numeric", "open_ended"))
                    if question["type"] == "mc":
                        self.assertIsInstance(question.get("options"), list)
                        self.assertIn(question["answer"], question["options"])
                    elif question["type"] == "numeric":
                        self.assertIn("tolerance", question)
                        self.assertIn("whole_number", question)
                    else:
                        self.assertGreater(question.get("max_marks", 0), 0)
                        self.assertTrue(question.get("marking_points"))

    def test_course_progress_counts_saved_diagnostic_without_changing_lesson_history(self):
        for course in data.all_courses_in_order():
            course_id = course["id"]
            first_lesson_id = course["lessons"][0]["id"]
            diagnostic_id = logic.course_diagnostic_lesson_id(course_id)
            progress = {
                course_id: {
                    "started": True,
                    "completed_lessons": [],
                    "diagnostics": {},
                    "questions_attempted": 9,
                    "correct_answers": 6,
                    "mistakes": {"Existing error": 2},
                    "practice_attempts": {first_lesson_id: [{"attempt_number": 1}]},
                    "lesson_assessments": {first_lesson_id: {"baseline_score": 3}},
                }
            }
            self.assertFalse(logic.course_diagnostic_completed(progress, course_id))
            self.assertEqual(logic.course_lesson_progress_percent(progress, course_id), 0)
            progress[course_id]["diagnostics"][diagnostic_id] = {
                "score": 4, "total": 5, "percent": 80
            }
            self.assertTrue(logic.course_diagnostic_completed(progress, course_id))
            expected_diagnostic_percent = round(100 / (len(course["lessons"]) + 1))
            self.assertEqual(
                logic.course_lesson_progress_percent(progress, course_id),
                expected_diagnostic_percent,
            )
            progress[course_id]["completed_lessons"].append(first_lesson_id)
            expected_two_items_percent = round(200 / (len(course["lessons"]) + 1))
            self.assertEqual(
                logic.course_lesson_progress_percent(progress, course_id),
                expected_two_items_percent,
            )
            self.assertEqual(progress[course_id]["questions_attempted"], 9)
            self.assertEqual(progress[course_id]["correct_answers"], 6)
            self.assertEqual(progress[course_id]["mistakes"], {"Existing error": 2})
            self.assertEqual(progress[course_id]["practice_attempts"][first_lesson_id][0]["attempt_number"], 1)
            self.assertEqual(progress[course_id]["lesson_assessments"][first_lesson_id]["baseline_score"], 3)

    def test_screen_checkpoint_resumes_and_does_not_overwrite_existing_progress(self):
        progress = {
            "fractions": {
                "started": True,
                "completed_lessons": ["fractions_l1"],
                "questions_attempted": 12,
                "correct_answers": 9,
                "mistakes": {"Denominator confusion": 3},
                "diagnostics": {"fractions_l1": {"score": 4, "total": 5}},
                "practice_attempts": {"fractions_l1": [{"attempt_number": 1, "correct": 2}]},
                "lesson_assessments": {"fractions_l1": {"baseline_score": 4}},
            }
        }
        checkpoint = logic.update_lesson_screen_checkpoint(
            progress, "fractions", "fractions_l2",
            {
                "current_screen": 3,
                "completed_screens": [1, 2],
                "completed": False,
                "screen_3_submitted": False,
                "question_id": "fractions_l2_screen3",
                "attempt_number": 2,
            },
        )
        self.assertEqual(checkpoint["current_screen"], 3)
        self.assertEqual(checkpoint["completed_screens"], [1, 2])
        restored = logic.get_lesson_screen_checkpoint(progress, "fractions", "fractions_l2")
        self.assertEqual(restored["question_id"], "fractions_l2_screen3")
        restored["completed_screens"].append(3)
        self.assertEqual(
            progress["fractions"]["lesson_screen_progress"]["fractions_l2"]["completed_screens"],
            [1, 2],
            "Mutating the returned checkpoint must not mutate saved progress.",
        )
        logic.update_lesson_screen_checkpoint(
            progress, "fractions", "fractions_l2",
            {"completed_screens": [1, 2, 3], "screen_3_submitted": True},
        )
        self.assertEqual(
            logic.get_lesson_screen_checkpoint(progress, "fractions", "fractions_l2")["completed_screens"],
            [1, 2, 3],
        )
        self.assertEqual(progress["fractions"]["completed_lessons"], ["fractions_l1"])
        self.assertEqual(progress["fractions"]["questions_attempted"], 12)
        self.assertEqual(progress["fractions"]["correct_answers"], 9)
        self.assertEqual(progress["fractions"]["diagnostics"]["fractions_l1"]["score"], 4)
        self.assertEqual(progress["fractions"]["practice_attempts"]["fractions_l1"][0]["attempt_number"], 1)
        self.assertEqual(progress["fractions"]["lesson_assessments"]["fractions_l1"]["baseline_score"], 4)

    def test_diagnostic_helper_handles_invalid_course_id_safely(self):
        self.assertIsNone(logic.course_diagnostic_lesson_id("not-a-course"))


if __name__ == "__main__":
    unittest.main()
