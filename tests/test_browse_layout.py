"""Regression tests for the course catalog's responsive metadata and filters."""
from course_presentation import course_card_metadata


def test_missing_level_metadata_is_hidden_instead_of_exposed_as_a_placeholder():
    course = {
        "category_label": "Mathematics",
        "subject_label": "Mathematics",
        "lesson_count": 4,
        "level": "Not specified",
        "lessons": [{}, {}, {}, {}],
    }

    metadata = course_card_metadata(course)

    assert "Not specified" not in metadata
    assert "Level not specified" not in metadata
    assert metadata == "Mathematics · Mathematics · 4 lessons"


def test_blank_level_is_hidden_but_real_level_is_preserved():
    base = {
        "category_label": "Science",
        "subject_label": "Chemistry",
        "lesson_count": 3,
        "lessons": [{}, {}, {}],
    }

    assert _course_card_metadata({**base, "level": ""}) == "Science · Chemistry · 3 lessons"
    assert _course_card_metadata({**base, "level": "IGCSE"}) == (
        "Science · Chemistry · 3 lessons · IGCSE"
    )


def test_course_metadata_escapes_user_visible_values():
    course = {
        "category_label": "<script>alert(1)</script>",
        "subject_label": "Science",
        "lesson_count": 1,
        "level": None,
        "lessons": [{}],
    }

    metadata = _course_card_metadata(course)

    assert "<script>" not in metadata
    assert "&lt;script&gt;" in metadata
