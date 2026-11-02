"""Regression tests for Analog Clock Foundations and its VQE integration."""

import unittest

import adaptive_learning
import clock_course
import clock_math
import data
import diagnostics
import math_taxonomy
import question_engine


class AnalogClockCourseTests(unittest.TestCase):
    def test_course_is_registered_with_complete_lesson_flow(self):
        course = data.get_course("analog_clocks")
        assert course is not None
        assert course["title"] == "Analog Clock Foundations"
        assert course["subject_id"] == "mathematics"
        assert course["lesson_count"] == 6
        assert [lesson["id"] for lesson in course["lessons"]] == [
            "clock_l1", "clock_l2", "clock_l3",
            "clock_l4", "clock_l5", "clock_l6",
        ]
        assert all(lesson.get("worked_example") for lesson in course["lessons"])
        assert all(lesson.get("practice_questions") for lesson in course["lessons"])

    def test_entry_diagnostic_has_five_stages_and_valid_routes(self):
        config = clock_course.COURSE_ENTRY_DIAGNOSTIC
        assert diagnostics.validate_diagnostic_config(config) == []
        assert [item["stage"] for item in config["questions"]] == [
            "prerequisite", "level_1", "level_2", "level_3", "project",
        ]
        assert all(config["pathways"][key]["questions"] for key in (
            "level_2", "level_3", "project",
        ))

    def test_core_lesson_question_banks_are_verified_and_route_scoped(self):
        for lesson in clock_course.LESSONS[:5]:
            lesson_id = lesson["id"]
            assert question_engine.is_vqe_pilot_lesson("analog_clocks", lesson_id)
            records = question_engine.select_questions(
                course_id="analog_clocks",
                lesson_id=lesson_id,
                pathway="standard",
                verified_only=True,
            )
            expected_ids = [item["id"] for item in lesson["practice_questions"]]
            assert [item["question_id"] for item in records] == expected_ids
            assert all(item["verification_status"] == "verified" for item in records)

        for route, expected_id in (
            ("level_2", "clock_entry_l2_q1"),
            ("level_3", "clock_entry_l3_q1"),
            ("project", "clock_entry_project_q1"),
        ):
            records = question_engine.select_questions(
                course_id="analog_clocks",
                lesson_id="clock_l1",
                pathway=route,
                verified_only=True,
            )
            ids = [item["question_id"] for item in records]
            assert expected_id in ids
            assert len(ids) == 4

    def test_vqe_registry_and_taxonomy_are_consistent(self):
        assert question_engine.validate_registry() == []
        for skill_id in (
            "math.time.clock_parts",
            "math.time.minute_counting",
            "math.time.hour_hand_position",
            "math.time.reading_analog_time",
            "math.time.elapsed_time",
        ):
            assert skill_id in math_taxonomy.SKILLS
            assert math_taxonomy.SKILLS[skill_id]["grade_bands"] == [3, 4, 5, 6, 7, 8, 9]

    def test_clock_hand_geometry_and_minute_counting(self):
        assert clock_math.minute_hand_angle(25) == 150
        assert clock_math.hour_hand_angle(3, 0) == 90
        assert clock_math.hour_hand_angle(3, 30) == 105
        assert clock_math.minute_count(23) == (4, 3)
        assert clock_math.hand_endpoint(0, 80) == (150.0, 70.0)

    def test_spoken_time_and_elapsed_time_across_hour_boundaries(self):
        assert clock_math.spoken_time(2, 0) == "2 o'clock"
        assert clock_math.spoken_time(2, 15) == "quarter past 2"
        assert clock_math.spoken_time(2, 30) == "half past 2"
        assert clock_math.spoken_time(2, 45) == "quarter to 3"
        assert clock_math.spoken_time(8, 52) == "8 minutes to 9"
        assert clock_math.elapsed_minutes(2, 47, 3, 18) == 31
        assert clock_math.elapsed_minutes(11, 50, 12, 10) == 20
        assert clock_math.elapsed_minutes(12, 50, 1, 10) == 20

    def test_diagnostic_evidence_maps_to_all_five_clock_skills(self):
        answers = {
            question["id"]: question["answer"]
            for question in clock_course.COURSE_ENTRY_DIAGNOSTIC["questions"]
        }
        result = diagnostics.evaluate_diagnostic(
            clock_course.COURSE_ENTRY_DIAGNOSTIC,
            answers,
        )
        progress = {
            "analog_clocks": {
                "diagnostics": {"clock_l1": result},
            }
        }
        timeline = adaptive_learning.build_intervention_timeline(progress)
        assert timeline["events_total"] == 5
        assert {event["skill_id"] for event in timeline["events"]} == {
            "math.time.clock_parts",
            "math.time.minute_counting",
            "math.time.hour_hand_position",
            "math.time.reading_analog_time",
            "math.time.elapsed_time",
        }


if __name__ == "__main__":
    unittest.main()
