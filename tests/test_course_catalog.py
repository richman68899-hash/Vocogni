"""Course catalogue metadata invariants across every published course."""
import unittest

import data


class CourseCatalogTests(unittest.TestCase):
    def test_every_course_has_shared_metadata_and_derived_lesson_count(self):
        for course in data.all_courses_in_order():
            with self.subTest(course=course["id"]):
                self.assertTrue(course.get("category_id"))
                self.assertTrue(course.get("category"))
                self.assertTrue(course.get("subject_id"))
                self.assertTrue(course.get("subject"))
                self.assertEqual(
                    course.get("lesson_count"),
                    len(course.get("lessons", [])),
                )

    def test_chemistry_course_has_twelve_lessons_and_expected_metadata(self):
        course = data.get_course("chemistry_9701")
        self.assertIsNotNone(course)
        self.assertEqual(course["lesson_count"], 12)
        self.assertEqual(course["category_id"], "academics")
        self.assertEqual(course["subject_id"], "chemistry")
        self.assertEqual(course["level"], "Grade 10")
        self.assertIn("9701", course["curriculum"])

    def test_chemistry_lessons_use_three_screen_structure_and_open_responses(self):
        course = data.get_course("chemistry_9701")
        for lesson in course["lessons"]:
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(lesson.get("explanation", "").strip())
                self.assertTrue(lesson.get("worked_example", "").strip())
                question = lesson.get("interactive_question", {})
                self.assertEqual(question.get("type"), "open_ended")
                self.assertTrue(question.get("marking_points"))
                self.assertGreater(question.get("max_marks", 0), 0)


if __name__ == "__main__":
    unittest.main()
