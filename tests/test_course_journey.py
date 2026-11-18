"""Regression tests for the course-to-lesson navigation path."""

from sections import course as course_section


def _configure_course(monkeypatch, lessons, next_lesson, diagnostic_id=None, diagnostic_done=False):
    monkeypatch.setattr(
        course_section.data,
        "get_course",
        lambda _course_id: {"lessons": lessons},
    )
    monkeypatch.setattr(
        course_section.logic,
        "next_incomplete_lesson",
        lambda _progress, _course_id: next_lesson,
    )
    monkeypatch.setattr(
        course_section.logic,
        "course_diagnostic_lesson_id",
        lambda _course_id: diagnostic_id,
    )
    monkeypatch.setattr(
        course_section.logic,
        "course_diagnostic_completed",
        lambda _progress, _course_id: diagnostic_done,
    )


def test_recent_course_activity_orders_resume_target_by_saved_timestamps():
    import logic

    courses = [
        {"id": "course_a"},
        {"id": "course_b"},
        {"id": "course_c"},
        {"id": "course_d"},
    ]
    progress = {
        "course_a": {
            "practice_attempts": {
                "lesson": [{"completed_at": "2026-11-16T12:00:00+07:00"}]
            }
        },
        "course_b": {
            "diagnostics": {
                "entry": {"completed_at": "2026-11-17T04:00:00Z"}
            }
        },
        "course_c": {
            "lesson_screen_progress": {
                "lesson": {"updated_at": "2026-11-18T08:00:00+07:00"}
            }
        },
        "course_d": {
            "practice_attempts": {
                "lesson": [{"completed_at": "not-a-timestamp"}]
            }
        },
    }

    ordered = logic.order_courses_by_recent_activity(courses, progress)

    assert [course["id"] for course in ordered] == [
        "course_c", "course_b", "course_a", "course_d"
    ]


def test_recent_course_activity_normalizes_offsets_and_preserves_ties():
    import logic

    courses = [{"id": "first"}, {"id": "second"}, {"id": "undated"}]
    progress = {
        "first": {"diagnostics": {"entry": {"completed_at": "2026-11-18T08:00:00+07:00"}}},
        "second": {"practice_attempts": {"lesson": [
            {"completed_at": "2026-11-18T01:00:00Z"}
        ]}},
        "undated": {},
    }

    ordered = logic.order_courses_by_recent_activity(courses, progress)

    assert [course["id"] for course in ordered] == ["first", "second", "undated"]


def test_previous_transfer_question_ids_only_reads_valid_course_history():
    progress = {
        "fractions": {
            "transfer_checks": [
                {"question_id": "used-1"},
                {"question_id": "used-2"},
                {"correct": True},
                None,
            ]
        }
    }

    assert course_section._previous_transfer_question_ids(progress, "fractions") == {
        "used-1", "used-2"
    }
    assert course_section._previous_transfer_question_ids(progress, "missing") == set()


def test_next_learning_lesson_returns_first_incomplete_lesson(monkeypatch):
    first = {"id": "lesson_1", "title": "First lesson"}
    _configure_course(monkeypatch, [first], first)

    assert course_section._next_learning_lesson({}, "sample") == first


def test_completed_entry_diagnostic_is_skipped(monkeypatch):
    diagnostic = {"id": "entry_check", "title": "Entry check"}
    first_lesson = {"id": "lesson_1", "title": "First lesson"}
    progress = {"sample": {"completed_lessons": []}}
    _configure_course(
        monkeypatch,
        [first_lesson],
        diagnostic,
        diagnostic_id="entry_check",
        diagnostic_done=True,
    )

    assert course_section._next_learning_lesson(progress, "sample") == first_lesson


def test_course_with_no_remaining_lesson_returns_none(monkeypatch):
    _configure_course(monkeypatch, [], None)

    assert course_section._next_learning_lesson({}, "sample") is None


def test_missing_course_returns_none(monkeypatch):
    monkeypatch.setattr(course_section.data, "get_course", lambda _course_id: None)

    assert course_section._next_learning_lesson({}, "missing") is None
