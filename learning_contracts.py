"""Versioned provenance contract for newly recorded question answers.

This module defines record shape only. It does not score answers, validate
question content, or decide whether an item is verified. VQE remains the
authority for question verification; subject-specific graders remain the
authority for scoring.

The contract is additive: older persisted attempt records may not contain
these fields and must continue to be read by existing consumers.
"""
from __future__ import annotations

from typing import Any


PROVENANCE_SCHEMA_VERSION = 1
VERIFICATION_STATUSES = frozenset({
    "legacy",
    "needs_review",
    "verified",
    "retired",
})


def _optional_text(value: Any) -> str | None:
    """Return a trimmed non-empty string, or None for missing/blank values."""
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def build_question_provenance(
    question_id: str,
    *,
    course_id: str | None = None,
    lesson_id: str | None = None,
    question_version: int = 1,
    skill_id: str | None = None,
    question_purpose: str | None = None,
    verification_status: str = "legacy",
    verification_engine_version: str | None = None,
    question_source_field: str | None = None,
) -> dict[str, Any]:
    """Build the common provenance payload attached to a new answer record.

    Context fields remain optional for callers that can resolve a question
    globally. Invalid values are deliberately not silently upgraded to a
    verified status; use validate_question_provenance() to inspect the shape.
    """
    clean_question_id = _optional_text(question_id)
    return {
        "provenance_schema_version": PROVENANCE_SCHEMA_VERSION,
        "question_id": clean_question_id or "",
        "course_id": _optional_text(course_id),
        "lesson_id": _optional_text(lesson_id),
        "question_version": question_version,
        "skill_id": _optional_text(skill_id),
        "question_purpose": _optional_text(question_purpose),
        "verification_status": verification_status,
        "verification_engine_version": _optional_text(verification_engine_version),
        "question_source_field": _optional_text(question_source_field),
    }


def validate_question_provenance(record: Any) -> list[str]:
    """Return contract violations for one provenance payload.

    This is intentionally a structural check. In particular, a record marked
    'verified' is not re-verified here; that determination belongs to VQE.
    """
    if not isinstance(record, dict):
        return ["Question provenance must be a dictionary."]

    issues: list[str] = []
    schema_version = record.get("provenance_schema_version")
    if type(schema_version) is not int or schema_version != PROVENANCE_SCHEMA_VERSION:
        issues.append(
            f"provenance_schema_version must equal {PROVENANCE_SCHEMA_VERSION}."
        )

    question_id = record.get("question_id")
    if not isinstance(question_id, str) or not question_id.strip():
        issues.append("question_id must be a non-empty string.")

    question_version = record.get("question_version")
    if type(question_version) is not int or question_version < 1:
        issues.append("question_version must be a positive integer.")

    for field in ("course_id", "lesson_id", "skill_id", "question_purpose",
                  "verification_engine_version", "question_source_field"):
        value = record.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            issues.append(f"{field} must be a non-empty string or None.")

    status = record.get("verification_status")
    if status not in VERIFICATION_STATUSES:
        issues.append(
            "verification_status must be one of: "
            + ", ".join(sorted(VERIFICATION_STATUSES))
            + "."
        )

    return issues
