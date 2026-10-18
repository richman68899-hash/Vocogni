import unittest

import data
import diagnostics
import math_grading
import quadratics_course
import quadratics_visuals


class QuadraticsCourseTests(unittest.TestCase):
    def test_course_metadata_and_lesson_count(self):
        course = data.get_course("quadratics_graphs")
        self.assertIsNotNone(course)
        self.assertEqual(course["category_id"], "academics")
        self.assertEqual(course["subject_id"], "mathematics")
        self.assertEqual(course["lesson_count"], 14)
        self.assertEqual(course["lesson_count"], len(course["lessons"]))

    def test_course_covers_all_lessons_visuals_and_question_sets(self):
        self.assertEqual(len(quadratics_course.LESSONS), 14)
        self.assertEqual(len({lesson["id"] for lesson in quadratics_course.LESSONS}), 14)
        seen_questions = set()
        visuals = set()
        for lesson in quadratics_course.LESSONS:
            with self.subTest(lesson=lesson["id"]):
                self.assertTrue(lesson["explanation"].strip())
                self.assertTrue(lesson["worked_example"].strip())
                self.assertTrue(lesson.get("visual_key"))
                visuals.add(lesson["visual_key"])
                self.assertGreaterEqual(len(lesson["practice_questions"]), 3)
                for question in lesson["practice_questions"]:
                    self.assertEqual(question["type"], "open_ended")
                    self.assertEqual(question["grader"], "math")
                    self.assertNotIn(question["id"], seen_questions)
                    seen_questions.add(question["id"])
                    self.assertEqual(math_grading.validate_open_response_question(question), [])
                    result = math_grading.evaluate_open_response(question, question["answer"])
                    self.assertTrue(result["full_credit"], question["id"])
        self.assertTrue({"coefficient_family", "quadratic_family", "quadratic_features",
                         "discriminant", "sign_chart", "inequality_overlap",
                         "line_parabola_intersections", "integral_under_curve",
                         "area_between_curves", "symmetry_explorer"} <= visuals)

    def test_all_diagnostic_rubrics_validate_and_model_answers_are_full_credit(self):
        config = quadratics_course.COURSE_DIAGNOSTIC
        self.assertEqual(diagnostics.validate_diagnostic_config(config), [])
        for question in config["questions"]:
            self.assertEqual(math_grading.validate_open_response_question(question), [])
            self.assertTrue(math_grading.evaluate_open_response(question, question["answer"])["full_credit"])
        for pathway in config["pathways"].values():
            for question in pathway["questions"]:
                self.assertTrue(math_grading.evaluate_open_response(question, question["answer"])["full_credit"])

    def test_partial_credit_and_notation_normalization(self):
        question = quadratics_course.LESSONS[1]["interactive_question"]
        result = math_grading.evaluate_open_response(question, "The roots are x=2 and x=3.")
        self.assertGreater(result["score"], 0)
        self.assertLess(result["score"], result["max_marks"])
        self.assertEqual(math_grading.normalize_answer("x² − 5x + 6"), "x^2-5x+6")

    def test_svg_graphs_generate_without_external_assets(self):
        for key in ("coefficient_family", "quadratic_family", "quadratic_features",
                    "discriminant", "sign_chart", "inequality_overlap",
                    "line_parabola_intersections", "integral_under_curve",
                    "area_between_curves", "symmetry_explorer"):
            with self.subTest(visual=key):
                svg = quadratics_visuals.build_visual(key)
                self.assertTrue(svg.startswith("<svg"))
                self.assertIn("viewBox", svg)
                self.assertIn("</svg>", svg)


if __name__ == "__main__":
    unittest.main()
