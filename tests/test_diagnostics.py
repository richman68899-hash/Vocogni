"""Unit tests for Vocogni's reusable lesson diagnostic engine."""
import unittest

import data
import diagnostics


def configured_lessons():
    return [
        (course, lesson)
        for course in data.all_courses_in_order()
        for lesson in course["lessons"]
        if lesson.get("diagnostic")
    ]


def deliberately_wrong_answer(question):
    """Create a wrong response regardless of question input type."""
    question_type = question.get("type")
    if question_type == "mc":
        return next(
            option for option in question.get("options", [])
            if option != question.get("answer")
        )
    if question_type == "numeric":
        try:
            return float(question["answer"]) + 987.0
        except (TypeError, ValueError):
            return "deliberately incorrect response"
    return f"deliberately incorrect response for {question.get('id', 'question')}"


class DiagnosticEngineTests(unittest.TestCase):
    def test_all_seed_diagnostics_validate(self):
        lessons = configured_lessons()
        self.assertGreaterEqual(len(lessons), 3)
        for course, lesson in lessons:
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(
                    diagnostics.validate_diagnostic_config(lesson["diagnostic"]),
                    [],
                )

    def test_all_configured_model_answers_route_to_project(self):
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            answers = {q["id"]: q["answer"] for q in config["questions"]}
            result = diagnostics.evaluate_diagnostic(config, answers)
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(result["score"], 5)
                self.assertEqual(result["outcome_key"], "project")
                self.assertEqual(result["weaknesses"], [])

    def test_prerequisite_failure_overrides_high_total_score(self):
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            answers = {q["id"]: q["answer"] for q in config["questions"]}
            prerequisite = next(
                q for q in config["questions"] if q["stage"] == "prerequisite"
            )
            answers[prerequisite["id"]] = deliberately_wrong_answer(prerequisite)
            result = diagnostics.evaluate_diagnostic(config, answers)
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(result["score"], 4)
                self.assertEqual(result["outcome_key"], "prerequisite")
                self.assertIn(
                    prerequisite["skill_tag"],
                    [w["skill_tag"] for w in result["weaknesses"]],
                )

    def test_score_thresholds_with_prerequisite_correct(self):
        expected_routes = {
            2: "level_1",
            3: "level_2",
            4: "level_3",
            5: "project",
        }
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            questions = config["questions"]
            prerequisite = next(
                q for q in questions if q["stage"] == "prerequisite"
            )
            other_questions = [
                q for q in questions if q["id"] != prerequisite["id"]
            ]
            for score, expected in expected_routes.items():
                answers = {q["id"]: q["answer"] for q in questions}
                wrong_count = 5 - score
                for question in other_questions[-wrong_count:] if wrong_count else []:
                    answers[question["id"]] = deliberately_wrong_answer(question)
                result = diagnostics.evaluate_diagnostic(config, answers)
                with self.subTest(lesson=lesson["id"], score=score):
                    self.assertEqual(result["score"], score)
                    self.assertEqual(result["outcome_key"], expected)

    def test_cumulative_pathway_unlocks_and_prerequisite_gate(self):
        cases = [
            (False, 5, ["level_1"]),
            (True, 1, ["level_1"]),
            (True, 2, ["level_1"]),
            (True, 3, ["level_1", "level_2"]),
            (True, 4, ["level_1", "level_2", "level_3"]),
            (True, 5, ["level_1", "level_2", "level_3", "project"]),
        ]
        for prerequisite_correct, score, expected in cases:
            with self.subTest(prerequisite=prerequisite_correct, score=score):
                result = {
                    "prerequisite_correct": prerequisite_correct,
                    "score": score,
                }
                self.assertEqual(
                    diagnostics.unlocked_pathways_for_score(result),
                    expected,
                )

    def test_missed_skill_is_listed(self):
        course, lesson = configured_lessons()[0]
        config = lesson["diagnostic"]
        answers = {q["id"]: q["answer"] for q in config["questions"]}
        missed = config["questions"][2]
        answers[missed["id"]] = deliberately_wrong_answer(missed)
        result = diagnostics.evaluate_diagnostic(config, answers)
        skill_tags = [item["skill_tag"] for item in result["weaknesses"]]
        self.assertIn(missed["skill_tag"], skill_tags)

    def test_l2_l3_and_project_select_their_own_practice_questions(self):
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            for route in ("level_2", "level_3", "project"):
                with self.subTest(lesson=lesson["id"], route=route):
                    selected = diagnostics.get_pathway_questions(lesson, route)
                    expected = config["pathways"][route]["questions"]
                    self.assertEqual(
                        [q["id"] for q in selected],
                        [q["id"] for q in expected],
                    )


if __name__ == "__main__":
    unittest.main()
