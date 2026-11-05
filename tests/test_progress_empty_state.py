"""Tests for the Progress page's first-use empty state."""

from sections.progress import _has_learning_activity


def test_empty_progress_has_no_learning_activity():
    assert not _has_learning_activity({
        "courses_attempted": 0,
        "courses_completed": 0,
        "lessons_completed": 0,
        "questions_attempted": 0,
    })


def test_started_course_counts_as_learning_activity():
    assert _has_learning_activity({"courses_attempted": 1})


def test_recorded_lesson_counts_as_learning_activity():
    assert _has_learning_activity({"lessons_completed": 1})


def test_recorded_question_attempt_counts_as_learning_activity():
    assert _has_learning_activity({"questions_attempted": 1})


def test_missing_or_malformed_counters_are_treated_as_zero():
    assert not _has_learning_activity({"courses_attempted": None, "lessons_completed": "bad"})
