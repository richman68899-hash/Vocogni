"""Framework-free helpers for matching courses in the learning catalogue."""
from __future__ import annotations

from typing import Any, Iterable, Mapping


def filter_courses(
    courses: Iterable[Mapping[str, Any]],
    statuses: Mapping[str, str],
    *,
    search: str = "",
    status_filter: str = "All",
    difficulty_filter: str = "All",
    category_filter: str = "All",
    subject_filter: str = "All",
) -> list[Mapping[str, Any]]:
    """Return courses matching all supplied filters, preserving catalogue order."""
    query = str(search or "").strip().casefold()
    filtered: list[Mapping[str, Any]] = []

    for course in courses:
        haystack = " ".join(
            str(course.get(field, "") or "")
            for field in (
                "title",
                "short_description",
                "category_label",
                "subject_label",
                "level",
                "curriculum",
            )
        ).casefold()
        if query and query not in haystack:
            continue

        course_id = str(course.get("id", ""))
        course_status = statuses.get(course_id, "Not started")
        if status_filter != "All" and course_status != status_filter:
            continue
        if difficulty_filter != "All" and course.get("difficulty") != difficulty_filter:
            continue
        if category_filter != "All" and course.get("category_id") != category_filter:
            continue
        if subject_filter != "All" and course.get("subject_id") != subject_filter:
            continue

        filtered.append(course)

    return filtered
