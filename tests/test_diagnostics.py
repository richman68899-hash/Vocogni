"""Unit tests for Vocogni's reusable lesson diagnostic engine."""
import unittest

import data
import diagnostics


def deliberately_wrong_answer(question):
    """Return a wrong response regardless of the question's input type."""
    if question.get("type") == "mc":
        return next(
            option for option in question.get("options", [])
            if option != question.get("answer")
        )
    if question.get("type") == "numeric":
        try:
            return float(question["answer"]) + 987.0
        except (TypeError, ValueError):
            return "deliberately incorrect response"
    return f"deliberately incorrect response for {question.get('id', 'question')}"


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

    def test_confidence_is_recorded_but_does_not_change_score_or_placement(self):
        course, lesson = configured_lessons()[0]
        config = lesson["diagnostic"]
        answers = {q["id"]: q["answer"] for q in config["questions"]}
        target = config["questions"][1]
        answers[target["id"]] = deliberately_wrong_answer(target)

        plain = diagnostics.evaluate_diagnostic(config, answers)
        informed = diagnostics.evaluate_diagnostic(
            config,
            answers,
            confidence={
                target["id"]: "very_sure",
                config["questions"][2]["id"]: "guessing",
            },
        )

        self.assertEqual(informed["score"], plain["score"])
        self.assertEqual(informed["outcome_key"], plain["outcome_key"])
        review = {item["question_id"]: item for item in informed["answer_review"]}
        self.assertEqual(review[target["id"]]["confidence"], "very_sure")
        self.assertIn("not a confirmed misconception", review[target["id"]]["confidence_interpretation"])
        self.assertEqual(review[config["questions"][2]["id"]]["confidence"], "guessing")
        self.assertEqual(informed["confidence_counts"]["very_sure"], 1)
        self.assertEqual(informed["confidence_counts"]["guessing"], 1)

    def test_unrecognised_confidence_is_ignored(self):
        course, lesson = configured_lessons()[0]
        config = lesson["diagnostic"]
        answers = {q["id"]: q["answer"] for q in config["questions"]}
        result = diagnostics.evaluate_diagnostic(
            config, answers, confidence={config["questions"][0]["id"]: "certain-ish"}
        )
        self.assertIsNone(result["answer_review"][0]["confidence"])

    def test_single_prerequisite_miss_does_not_override_four_correct_items(self):
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
                self.assertEqual(result["outcome_key"], "level_3")
                self.assertTrue(result["prerequisite_follow_up"])
                self.assertIn("single response is a follow-up signal", result["placement_reason"])
                self.assertIn(
                    prerequisite["skill_tag"],
                    [w["skill_tag"] for w in result["weaknesses"]],
                )
                self.assertEqual(
                    result["unlocked_pathways"],
                    ["level_1", "level_2", "level_3"],
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
                for question in (other_questions[-wrong_count:] if wrong_count else []):
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
