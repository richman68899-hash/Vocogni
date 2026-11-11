"""Regression tests for the Word Problems five-item / three-screen structure."""
import unittest

import data
import logic
import diagnostics


class WordProblemsStructureTests(unittest.TestCase):
    def setUp(self):
        self.course = data.get_course("word_problems")

    def test_course_contains_four_learning_lessons_plus_one_separate_diagnostic(self):
        self.assertEqual(len(self.course["lessons"]), 4)
        first_lesson = self.course["lessons"][0]
        self.assertEqual(first_lesson["id"], "wp_l1")
        self.assertEqual(len(first_lesson["diagnostic"]["questions"]), 5)
        self.assertEqual(diagnostics.validate_diagnostic_config(first_lesson["diagnostic"]), [])

    def test_all_four_learning_lessons_have_three_screen_content(self):
        self.assertEqual(len(self.course["lessons"]), 4)
        for lesson in self.course["lessons"]:
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(lesson.get("explanation", "").strip())
                self.assertTrue(lesson.get("worked_example", "").strip())
                question = lesson.get("interactive_question")
                self.assertIsInstance(question, dict)
                for field in ("id", "type", "prompt", "answer", "explanation", "mistake_tag"):
                    self.assertIn(field, question)
                self.assertIn(question["type"], ("mc", "numeric"))
                if question["type"] == "mc":
                    self.assertIsInstance(question.get("options"), list)
                    self.assertIn(question["answer"], question["options"])
                else:
                    self.assertIn("tolerance", question)
                    self.assertIn("whole_number", question)

    def test_word_problems_progress_counts_diagnostic_as_first_of_five_items(self):
        progress = {"word_problems": {"completed_lessons": [], "diagnostics": {}}}
        self.assertEqual(logic.course_lesson_progress_percent(progress, "word_problems"), 0)

        progress["word_problems"]["diagnostics"]["wp_l1"] = {"score": 3, "total": 5}
        self.assertEqual(logic.course_lesson_progress_percent(progress, "word_problems"), 20)

        progress["word_problems"]["completed_lessons"].append("wp_l1")
        self.assertEqual(logic.course_lesson_progress_percent(progress, "word_problems"), 40)


if __name__ == "__main__":
    unittest.main()
