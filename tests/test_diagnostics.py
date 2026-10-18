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


def canonical_answers(config):
    return {q["id"]: q["answer"] for q in config["questions"]}


def deliberately_wrong_answer(question):
    if question.get("type") == "mc":
        return next(option for option in question.get("options", []) if option != question["answer"])
    return "I am deliberately submitting an unrelated incorrect response."


class DiagnosticEngineTests(unittest.TestCase):
    def test_seed_diagnostics_validate_and_include_chemistry(self):
        lessons = configured_lessons()
        self.assertGreaterEqual(len(lessons), 4)
        chemistry = [(course, lesson) for course, lesson in lessons if course["id"] == "chemistry_9701"]
        self.assertEqual(len(chemistry), 1)
        for course, lesson in lessons:
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(diagnostics.validate_diagnostic_config(lesson["diagnostic"]), [])

    def test_all_canonical_answers_route_to_project(self):
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            result = diagnostics.evaluate_diagnostic(config, canonical_answers(config))
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(result["score"], 5)
                self.assertEqual(result["outcome_key"], "project")
                self.assertEqual(result["weaknesses"], [])
                self.assertTrue(result.get("all_items_full", True))

    def test_prerequisite_failure_overrides_high_total_score(self):
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            answers = canonical_answers(config)
            prerequisite = next(q for q in config["questions"] if q["stage"] == "prerequisite")
            answers[prerequisite["id"]] = deliberately_wrong_answer(prerequisite)
            result = diagnostics.evaluate_diagnostic(config, answers)
            with self.subTest(lesson=lesson["id"]):
                self.assertEqual(result["outcome_key"], "prerequisite")
                self.assertIn(prerequisite["skill_tag"], [w["skill_tag"] for w in result["weaknesses"]])

    def test_score_thresholds_for_legacy_multiple_choice_diagnostics(self):
        expected_routes = {2: "level_1", 3: "level_2", 4: "level_3", 5: "project"}
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            if any(q.get("type") == "open_ended" for q in config["questions"]):
                continue
            questions = config["questions"]
            prerequisite = next(q for q in questions if q["stage"] == "prerequisite")
            for score, expected in expected_routes.items():
                answers = canonical_answers(config)
                correct_count = len(questions)
                for question in reversed(questions):
                    if correct_count <= score:
                        break
                    if question["id"] == prerequisite["id"]:
                        continue
                    answers[question["id"]] = deliberately_wrong_answer(question)
                    correct_count -= 1
                result = diagnostics.evaluate_diagnostic(config, answers)
                with self.subTest(lesson=lesson["id"], score=score):
                    self.assertEqual(result["score"], score)
                    self.assertEqual(result["outcome_key"], expected)

    def test_partial_credit_open_ended_diagnostic_is_not_full_credit(self):
        course, lesson = next(
            (course, lesson) for course, lesson in configured_lessons()
            if course["id"] == "chemistry_9701"
        )
        config = lesson["diagnostic"]
        answers = canonical_answers(config)
        prerequisite = next(q for q in config["questions"] if q["stage"] == "prerequisite")
        # Give a non-canonical partial answer that mentions only one atom count.
        answers[prerequisite["id"]] = "Al = 2"
        result = diagnostics.evaluate_diagnostic(config, answers)
        item = next(x for x in result["answer_review"] if x["question_id"] == prerequisite["id"])
        self.assertLess(item["marks_awarded"], item["max_marks"])
        self.assertFalse(item["correct"])
        self.assertEqual(result["outcome_key"], "prerequisite")

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
                result = {"prerequisite_correct": prerequisite_correct, "score": score}
                self.assertEqual(diagnostics.unlocked_pathways_for_score(result), expected)

    def test_missed_skill_is_listed_once(self):
        course, lesson = next(
            (course, lesson) for course, lesson in configured_lessons()
            if lesson.get("diagnostic") and lesson["diagnostic"]["questions"][0].get("type") == "mc"
        )
        config = lesson["diagnostic"]
        answers = canonical_answers(config)
        missed = config["questions"][2]
        answers[missed["id"]] = deliberately_wrong_answer(missed)
        result = diagnostics.evaluate_diagnostic(config, answers)
        skill_tags = [item["skill_tag"] for item in result["weaknesses"]]
        self.assertIn(missed["skill_tag"], skill_tags)
        self.assertEqual(len(skill_tags), len(set(skill_tags)))

    def test_pathways_select_their_authored_questions(self):
        for course, lesson in configured_lessons():
            config = lesson["diagnostic"]
            for route in ("level_2", "level_3", "project"):
                with self.subTest(lesson=lesson["id"], route=route):
                    selected = diagnostics.get_pathway_questions(lesson, route)
                    expected = config["pathways"][route]["questions"]
                    self.assertEqual([q["id"] for q in selected], [q["id"] for q in expected])


if __name__ == "__main__":
    unittest.main()
