"""Tests for the evidence-aligned Learning Rhythm and review scheduler."""
import unittest
from datetime import date
from unittest.mock import patch

import data
import learning_maintenance as maintenance


TODAY = date(2026, 10, 23)
COURSE_ID = "fractions"
LESSON_ID = "fractions_l1"


def _attempt(day, *, correct=True, question_id="q1", percent=None):
    results = [{"question_id": question_id, "correct": correct}]
    if percent is not None:
        results = [{
            "question_id": question_id,
            "correct": percent >= 100,
            "score": percent,
            "max_marks": 100,
        }]
    return {
        "attempt_number": 1,
        "completed_at": f"{day}T12:00:00+00:00",
        "results": results,
    }


def _progress(attempts=None, diagnostics=None, checkpoints=None):
    course = data.get_course(COURSE_ID)
    assert course is not None
    first_lesson = course["lessons"][0]["id"]
    return {
        COURSE_ID: {
            "practice_attempts": {first_lesson: attempts or []},
            "diagnostics": diagnostics or {},
            "lesson_screen_progress": checkpoints or {},
        }
    }


class LearningMaintenanceTests(unittest.TestCase):
    def test_only_completed_practice_and_diagnostics_count_as_learning_days(self):
        progress = _progress(
            attempts=[
                _attempt("2026-10-21", correct=True),
                _attempt("2026-10-21", correct=False, question_id="q2"),
            ],
            diagnostics={
                "fractions_l1": {
                    "completed_at": "2026-10-22T12:00:00+00:00",
                    "score": 3,
                    "total": 5,
                }
            },
            checkpoints={
                "fractions_l2": {
                    "updated_at": "2026-10-20T12:00:00+00:00",
                    "completed": False,
                    "screen_3_submitted": False,
                    "results": [],
                }
            },
        )
        self.assertEqual(
            maintenance.activity_dates(progress, "UTC+0"),
            {date(2026, 10, 21), date(2026, 10, 22)},
        )

    def test_streak_weekly_goal_and_day_cards_are_calculated_from_distinct_days(self):
        progress = _progress(
            attempts=[
                _attempt("2026-10-20", question_id="q1"),
                _attempt("2026-10-21", question_id="q2"),
                _attempt("2026-10-22", question_id="q3"),
                _attempt("2026-10-23", question_id="q4"),
            ]
        )
        summary = maintenance.build_maintenance_summary(
            progress, timezone_label="UTC+0", weekly_target=3, today=TODAY
        )
        self.assertEqual(summary["current_streak"], 4)
        self.assertEqual(summary["longest_streak"], 4)
        self.assertEqual(summary["active_days_this_week"], 4)
        self.assertTrue(summary["week_goal_met"])
        self.assertTrue(summary["today_complete"])
        self.assertEqual(
            [day["label"] for day in summary["week_day_cards"]],
            ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        )
        self.assertFalse(summary["week_day_cards"][0]["active"])
        self.assertTrue(summary["week_day_cards"][4]["active"])
        self.assertTrue(summary["week_day_cards"][5]["future"])

    def test_yesterday_streak_can_continue_without_calling_it_lost(self):
        progress = _progress(
            attempts=[
                _attempt("2026-10-20", question_id="q1"),
                _attempt("2026-10-21", question_id="q2"),
                _attempt("2026-10-22", question_id="q3"),
            ]
        )
        summary = maintenance.build_maintenance_summary(
            progress, timezone_label="UTC+0", today=TODAY
        )
        self.assertEqual(summary["current_streak"], 3)
        self.assertFalse(summary["today_complete"])

    def test_gap_of_two_days_resets_current_streak_but_preserves_best(self):
        progress = _progress(
            attempts=[
                _attempt("2026-10-17", question_id="q1"),
                _attempt("2026-10-18", question_id="q2"),
                _attempt("2026-10-20", question_id="q3"),
                _attempt("2026-10-21", question_id="q4"),
            ]
        )
        summary = maintenance.build_maintenance_summary(
            progress, timezone_label="UTC+0", today=TODAY
        )
        self.assertEqual(summary["current_streak"], 0)
        self.assertEqual(summary["longest_streak"], 2)
        self.assertEqual(summary["last_active_day"], date(2026, 10, 21))

    def test_profile_timezone_controls_local_learning_day(self):
        # 18:30 UTC on Oct 22 is 01:30 on Oct 23 at UTC+7.
        progress = _progress(attempts=[
            {
                "completed_at": "2026-10-22T18:30:00+00:00",
                "results": [{"question_id": "q1", "correct": True}],
            }
        ])
        self.assertEqual(
            maintenance.activity_dates(progress, "UTC+7"),
            {date(2026, 10, 23)},
        )
        self.assertEqual(
            maintenance.activity_dates(progress, "UTC+0"),
            {date(2026, 10, 22)},
        )

    def test_low_recent_performance_gets_next_day_review(self):
        progress = _progress(attempts=[
            _attempt("2026-10-22", correct=False, percent=40),
        ])
        summary = maintenance.build_maintenance_summary(
            progress, timezone_label="UTC+0", today=TODAY
        )
        self.assertEqual(summary["total_due_reviews"], 1)
        review = summary["due_reviews"][0]
        self.assertEqual(review["interval_days"], 1)
        self.assertEqual(review["due_date"], TODAY)
        self.assertEqual(review["days_overdue"], 0)

    def test_successful_practice_on_distinct_days_increases_review_spacing(self):
        course = data.get_course(COURSE_ID)
        lessons = course["lessons"]
        # Use separate lessons so each schedule follows its own history.
        progress = {
            COURSE_ID: {
                "practice_attempts": {
                    lessons[0]["id"]: [
                        _attempt("2026-10-22", question_id="a"),
                    ],
                    lessons[1]["id"]: [
                        _attempt("2026-10-13", question_id="b1"),
                        _attempt("2026-10-17", question_id="b2"),
                        _attempt("2026-10-22", question_id="b3"),
                    ],
                    lessons[2]["id"]: [
                        _attempt("2026-10-12", question_id="c1"),
                        _attempt("2026-10-17", question_id="c2"),
                        _attempt("2026-10-22", question_id="c3"),
                    ],
                },
                "diagnostics": {},
                "lesson_screen_progress": {},
            }
        }
        summary = maintenance.build_maintenance_summary(
            progress, timezone_label="UTC+0", today=TODAY, review_limit=10
        )
        schedules = {
            item["lesson_id"]: item
            for item in (summary["due_reviews"] + summary["upcoming_reviews"])
        }
        self.assertEqual(schedules[lessons[0]["id"]]["interval_days"], 1)
        self.assertEqual(schedules[lessons[1]["id"]]["interval_days"], 7)
        self.assertEqual(schedules[lessons[1]["id"]]["due_date"], date(2026, 10, 29))
        self.assertEqual(schedules[lessons[2]["id"]]["interval_days"], 7)

    def test_complete_checkpoint_can_backfill_a_missing_attempt_record(self):
        progress = _progress(
            attempts=[],
            checkpoints={
                "fractions_l1": {
                    "updated_at": "2026-10-22T12:00:00+00:00",
                    "completed": True,
                    "screen_3_submitted": True,
                    "results": [{"question_id": "q1", "correct": True}],
                }
            },
        )
        self.assertEqual(
            maintenance.activity_dates(progress, "UTC+0"),
            {date(2026, 10, 22)},
        )

    def test_invalid_weekly_goal_falls_back_to_default(self):
        summary = maintenance.build_maintenance_summary(
            {}, timezone_label="UTC+0", weekly_target=99, today=TODAY
        )
        self.assertEqual(summary["weekly_target"], 3)

    def test_unknown_timezone_safely_uses_utc(self):
        self.assertEqual(
            maintenance.activity_dates(
                _progress(attempts=[_attempt("2026-10-22")]),
                "timezone not in supported format",
            ),
            {date(2026, 10, 22)},
        )

    def test_opening_app_or_partial_screen_checkpoint_does_not_create_activity(self):
        progress = _progress(
            attempts=[{"completed_at": "2026-10-22T12:00:00+00:00", "results": []}],
            checkpoints={
                "fractions_l1": {
                    "updated_at": "2026-10-22T12:00:00+00:00",
                    "completed": False,
                    "screen_3_submitted": False,
                    "results": [{"question_id": "q1", "correct": True}],
                }
            },
        )
        self.assertEqual(maintenance.activity_dates(progress, "UTC+0"), set())

    def test_saved_answer_counts_even_if_the_learner_leaves_before_finishing_the_set(self):
        progress = _progress(
            checkpoints={
                "fractions_l1": {
                    "updated_at": "2026-10-23T12:00:00+00:00",
                    "completed": False,
                    "screen_3_submitted": True,
                    "results": [{"question_id": "q1", "correct": False}],
                }
            },
        )
        self.assertEqual(
            maintenance.activity_dates(progress, "UTC+0"),
            {date(2026, 10, 23)},
        )
        summary = maintenance.build_maintenance_summary(
            progress, timezone_label="UTC+0", today=TODAY
        )
        self.assertTrue(summary["today_complete"])
        # An unfinished attempt creates a learning day, not a spaced-review item.
        self.assertEqual(summary["total_due_reviews"], 0)

    def test_submitted_question_counts_even_when_an_older_completed_attempt_exists(self):
        progress = _progress(
            attempts=[_attempt("2026-10-20", question_id="q1")],
            checkpoints={
                "fractions_l1": {
                    "updated_at": "2026-10-23T09:00:00+00:00",
                    "completed": False,
                    "screen_3_submitted": True,
                    "results": [{"question_id": "q2", "correct": True}],
                }
            },
        )
        self.assertEqual(
            maintenance.activity_dates(progress, "UTC+0"),
            {date(2026, 10, 20), date(2026, 10, 23)},
        )



    def test_activity_days_in_period_supports_a_one_day_weekly_goal(self):
        active_dates = {date(2026, 10, 1), date(2026, 10, 21)}
        self.assertEqual(
            maintenance.activity_days_in_period(active_dates, "week", TODAY),
            1,
        )

    def test_activity_days_in_period_counts_current_month_but_not_other_months(self):
        active_dates = {
            date(2026, 9, 30),
            date(2026, 10, 1),
            date(2026, 10, 21),
            date(2026, 10, 24),
        }
        self.assertEqual(
            maintenance.activity_days_in_period(active_dates, "month", TODAY),
            2,
        )

    def test_activity_days_in_period_rejects_unknown_period(self):
        with self.assertRaises(ValueError):
            maintenance.activity_days_in_period({TODAY}, "year", TODAY)


if __name__ == "__main__":
    unittest.main()
