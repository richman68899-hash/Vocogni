"""Learner-authored mistake reflections stored as structured learning evidence.

Reflections are linked to a specific submitted answer, not stored as free-
floating notes. They remain separate from automated marking and question
provenance so later AI analysis can distinguish learner interpretation from
system-generated feedback.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

REFLECTION_SCHEMA_VERSION = 1
MAX_REFLECTION_LENGTH = 2000


def normalize_reflection_text(value: Any) -> str:
    """Trim learner text and enforce a bounded, plain-text payload."""
    if not isinstance(value, str):
        return ""
    return value.strip()[:MAX_REFLECTION_LENGTH]


def find_mistake_reflection(
    course_progress: dict[str, Any],
    answer_id: str,
) -> dict[str, Any] | None:
    """Find the learner reflection linked to one submitted answer."""
    if not isinstance(course_progress, dict) or not isinstance(answer_id, str):
        return None
    records = course_progress.get("mistake_reflections", [])
    if not isinstance(records, list):
        return None
    return next(
        (
            item for item in records
            if isinstance(item, dict) and item.get("answer_id") == answer_id
        ),
        None,
    )


def upsert_mistake_reflection(
    course_progress: dict[str, Any],
    *,
    answer_id: str,
    course_id: str,
    lesson_id: str,
    question_id: str,
    attempt_number: int,
    text: str,
    question_prompt: str | None = None,
    now: str | None = None,
) -> dict[str, Any]:
    """Create or update one learner reflection without changing answer marking."""
    if not isinstance(course_progress, dict):
        raise TypeError("course_progress must be a dictionary.")
    required = {
        "answer_id": answer_id,
        "course_id": course_id,
        "lesson_id": lesson_id,
        "question_id": question_id,
    }
    if any(not isinstance(value, str) or not value.strip() for value in required.values()):
        raise ValueError("A valid answer, course, lesson, and question ID are required.")

    cleaned_text = normalize_reflection_text(text)
    if not cleaned_text:
        raise ValueError("Write a short explanation before saving.")
    timestamp = now or datetime.now(timezone.utc).isoformat()

    records = course_progress.setdefault("mistake_reflections", [])
    if not isinstance(records, list):
        records = []
        course_progress["mistake_reflections"] = records

    existing = find_mistake_reflection(course_progress, answer_id)
    if existing is None:
        existing = {
            "schema_version": REFLECTION_SCHEMA_VERSION,
            "answer_id": answer_id,
            "course_id": course_id,
            "lesson_id": lesson_id,
            "question_id": question_id,
            "attempt_number": max(1, int(attempt_number)),
            "source": "learner",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        records.append(existing)

    existing.update({
        "schema_version": REFLECTION_SCHEMA_VERSION,
        "text": cleaned_text,
        "updated_at": timestamp,
        "source": "learner",
    })
    if isinstance(question_prompt, str) and question_prompt.strip():
        existing["question_prompt"] = question_prompt.strip()[:1000]
    return existing
