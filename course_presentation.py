"""Framework-free presentation helpers for course catalog content."""
import html


def course_card_metadata(course):
    """Format only configured, learner-useful course metadata."""
    level = course.get("level")
    if not isinstance(level, str) or not level.strip() or level.strip().casefold() in {
        "not specified", "level not specified", "none", "null", "n/a"
    }:
        level = ""

    metadata_parts = [
        course.get("category_label", "Other"),
        course.get("subject_label", "Other"),
        f'{course.get("lesson_count", len(course.get("lessons", [])))} lessons',
        level,
    ]
    return " · ".join(
        html.escape(str(value).strip())
        for value in metadata_parts
        if value is not None and str(value).strip()
    )
