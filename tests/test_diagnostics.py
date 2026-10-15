"""Unit tests for VOCogni's reusable lesson diagnostic engine (no Streamlit UI required)."""
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


class DiagnosticEngineTests(unittest.TestCase):
    def test_three_seed_diagnostics_validate(self):
        lessons = configured_lessons()
        self.assertEqual(len(lessons), 3)
        for course, lesson in lessons:
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(diagnostics.validate_diagnostic_config(lesson["diagnostic"]), [])

    def test_all_correct_routes_to_project(self):
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
            prerequisite = next(q for q in config["questions"] if q["stage"] == "prerequisite")
            wrong = next(option for option in prerequisite["options"] if option != prerequisite["answer"])
            answers[prerequisite["id"]] = wrong
            result = diagnostics.evaluate_diagnostic(config, answers)
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(result["score"], 4)
                self.assertEqual(result["outcome_key"], "prerequisite")
                self.assertIn(prerequisite["skill_tag"], [w["skill_tag"] for w in result["weaknesses"]])

    def test_score_thresholds_with_prerequisite_correct(self):
        expected_routes = {2: "level_1", 3: "level_2", 4: "level_3", 5: "project"}
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            questions = config["questions"]
            prerequisite = next(q for q in questions if q["stage"] == "prerequisite")
            for score, expected in expected_routes.items():
                answers = {q["id"]: q["answer"] for q in questions}
                # Keep the prerequisite item correct; make enough of the
                # remaining items wrong to reach the requested score.
                for question in reversed(questions):
                    if sum(answers[q["id"]] == q["answer"] for q in questions) <= score:
                        break
                    if question["id"] == prerequisite["id"]:
                        continue
                    wrong = next(option for option in question.get("options", []) if option != question["answer"])
                    answers[question["id"]] = wrong
                result = diagnostics.evaluate_diagnostic(config, answers)
                with self.subTest(lesson=lesson["id"], score=score):
                    self.assertEqual(result["score"], score)
                    self.assertEqual(result["outcome_key"], expected)

    def test_score_unlocks_cumulative_pathways(self):
        cases = [
            (1, False, ["level_1"]),
            (2, True, ["level_1"]),
            (3, True, ["level_1", "level_2"]),
            (4, True, ["level_1", "level_2", "level_3"]),
            (5, True, ["level_1", "level_2", "level_3", "project"]),
        ]
        for score, prerequisite_correct, expected in cases:
            with self.subTest(score=score, prerequisite_correct=prerequisite_correct):
                self.assertEqual(
                    diagnostics.unlocked_pathways_for_score(score, prerequisite_correct),
                    expected,
                )

    def test_missed_skill_is_listed_once(self):
        course, lesson = configured_lessons()[0]
        config = lesson["diagnostic"]
        answers = {q["id"]: q["answer"] for q in config["questions"]}
        missed = config["questions"][2]
        wrong = next(option for option in missed["options"] if option != missed["answer"])
        answers[missed["id"]] = wrong
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
                    self.assertEqual([q["id"] for q in selected], [q["id"] for q in expected])


if __name__ == "__main__":
    unittest.main()
