import unittest

import chemistry_course
import chemistry_grading
import data
import diagnostics


class ChemistryCourseStructureTests(unittest.TestCase):
    def test_course_is_registered_with_full_metadata(self):
        course = data.get_course("chemistry_9701")
        self.assertIsNotNone(course)
        self.assertEqual(course["category_id"], "academics")
        self.assertEqual(course["subject_id"], "chemistry")
        self.assertEqual(course["lesson_count"], 12)
        self.assertEqual(course["lesson_count"], len(course["lessons"]))
        self.assertEqual(len({lesson["id"] for lesson in course["lessons"]}), 12)

    def test_every_existing_course_has_shared_catalogue_metadata(self):
        for course in data.all_courses_in_order():
            with self.subTest(course=course["id"]):
                self.assertTrue(course.get("category_id"))
                self.assertTrue(course.get("category_label"))
                self.assertTrue(course.get("subject_id"))
                self.assertTrue(course.get("subject_label"))
                self.assertEqual(course["lesson_count"], len(course["lessons"]))

    def test_all_twelve_chemistry_lessons_have_three_screens_and_question_sets(self):
        course = data.get_course("chemistry_9701")
        self.assertEqual(len(course["lessons"]), 12)
        for lesson in course["lessons"]:
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(lesson.get("explanation", "").strip())
                self.assertTrue(lesson.get("worked_example", "").strip())
                questions = lesson.get("practice_questions", [])
                self.assertGreaterEqual(len(questions), 3)
                self.assertEqual(lesson.get("interactive_question"), questions[0])
                for question in questions:
                    self.assertEqual(question["type"], "open_ended")
                    self.assertTrue(question.get("prompt"))
                    self.assertGreater(question.get("max_marks", 0), 0)
                    errors = chemistry_grading.validate_open_response_question(question)
                    self.assertEqual(errors, [])
                    self.assertEqual(
                        sum(point["marks"] for point in question["marking_points"]),
                        question["max_marks"],
                    )

    def test_each_practice_model_answer_is_full_credit(self):
        for lesson in chemistry_course.LESSONS:
            for question in lesson["practice_questions"]:
                with self.subTest(question=question["id"]):
                    result = chemistry_grading.evaluate_open_response(
                        question, question["answer"]
                    )
                    self.assertTrue(result["full_credit"])
                    self.assertEqual(result["score"], question["max_marks"])

    def test_each_entry_diagnostic_model_answer_is_full_credit(self):
        config = chemistry_course.COURSE_DIAGNOSTIC
        for question in config["questions"]:
            with self.subTest(question=question["id"]):
                result = chemistry_grading.evaluate_open_response(
                    question, question["answer"]
                )
                self.assertTrue(result["full_credit"])
                self.assertEqual(result["score"], question["max_marks"])
        for route, pathway in config["pathways"].items():
            for question in pathway.get("questions", []):
                with self.subTest(pathway=route, question=question["id"]):
                    result = chemistry_grading.evaluate_open_response(
                        question, question["answer"]
                    )
                    self.assertTrue(result["full_credit"])
                    self.assertEqual(result["score"], question["max_marks"])

    def test_question_ids_are_unique_within_course(self):
        ids = []
        for lesson in chemistry_course.LESSONS:
            ids.extend(question["id"] for question in lesson["practice_questions"])
        self.assertEqual(len(ids), len(set(ids)))

    def test_diagnostic_pathway_rubrics_are_valid(self):
        config = chemistry_course.COURSE_DIAGNOSTIC
        questions = list(config["questions"])
        for pathway in config["pathways"].values():
            questions.extend(pathway.get("questions", []))
        for question in questions:
            with self.subTest(question=question["id"]):
                self.assertEqual(
                    chemistry_grading.validate_open_response_question(question),
                    [],
                )
                self.assertEqual(
                    sum(point["marks"] for point in question["marking_points"]),
                    question["max_marks"],
                )

    def test_course_entry_diagnostic_has_valid_five_stage_config(self):
        errors = diagnostics.validate_diagnostic_config(chemistry_course.COURSE_DIAGNOSTIC)
        self.assertEqual(errors, [])
        course = data.get_course("chemistry_9701")
        self.assertEqual(
            course["lessons"][0]["diagnostic"]["questions"][0]["id"],
            chemistry_course.COURSE_DIAGNOSTIC["questions"][0]["id"],
        )

    def test_metadata_uses_published_lessons_not_diagnostic(self):
        course = data.get_course("chemistry_9701")
        self.assertEqual(course["lesson_count"], 12)
        self.assertTrue(all("diagnostic" not in lesson for lesson in course["lessons"][1:]))


if __name__ == "__main__":
    unittest.main()
