"""Tests for grouped Learning Rhythm activity dates."""
import unittest
from datetime import date

import data
import learning_maintenance


class ActivityDatesByCourseTests(unittest.TestCase):
    def test_dates_are_grouped_by_course_without_changing_global_union(self):
        first, second = data.COURSE_ORDER[:2]
        progress = {
            first: {
                "practice_attempts": {
                    "lesson_a": [{
                        "completed_at": "2026-10-30T10:00:00+00:00",
                        "results": [{"question_id": "q1", "correct": True}],
                    }]
                },
                "lesson_screen_progress": {},
                "diagnostics": {},
            },
            second: {
                "practice_attempts": {
                    "lesson_b": [{
                        "completed_at": "2026-10-31T10:00:00+00:00",
                        "results": [{"question_id": "q2", "correct": True}],
                    }]
                },
                "lesson_screen_progress": {},
                "diagnostics": {},
            },
        }
        grouped = learning_maintenance.activity_dates_by_course(progress, "UTC+0")
        self.assertEqual(grouped[first], {date(2026, 10, 30)})
        self.assertEqual(grouped[second], {date(2026, 10, 31)})
        self.assertEqual(
            learning_maintenance.activity_dates(progress, "UTC+0"),
            grouped[first] | grouped[second],
        )

    def test_empty_course_records_do_not_create_dates(self):
        course_id = data.COURSE_ORDER[0]
        grouped = learning_maintenance.activity_dates_by_course(
            {course_id: {"practice_attempts": {"lesson": [{"results": []}]}}},
            "UTC+0",
        )
        self.assertEqual(grouped, {})


if __name__ == "__main__":
    unittest.main()
