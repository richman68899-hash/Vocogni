"""Small, auditable helpers for P03 transfer checks.

Question selection stays inside VQE: only current verified records with an
explicit application purpose can be selected. Coverage reporting is metadata
accounting, not evidence that a question validly measures transfer.
"""
from __future__ import annotations

from typing import Any

import question_engine


def select_transfer_question(
    practice_questions: list[dict[str, Any]],
    *,
    course_id: str | None,
    lesson_id: str,
) -> dict[str, Any] | None:
    """Return one different-lesson, verified application item for a practiced skill."""
    if not course_id or not isinstance(practice_questions, list):
        return None

    practiced_ids = {
        str(item.get("id")) for item in practice_questions
        if isinstance(item, dict) and item.get("id")
    }
    practiced_skills: list[str] = []
    for item in practice_questions:
        if not isinstance(item, dict) or item.get("_is_transfer_check"):
            continue
        metadata = question_engine.attempt_metadata(
            str(item.get("id") or ""), course_id=course_id, lesson_id=lesson_id
        )
        skill = metadata.get("skill_id")
        if skill and skill not in practiced_skills:
            practiced_skills.append(skill)

    for skill in practiced_skills:
        records = question_engine.select_questions(
            course_id=course_id,
            skill_id=skill,
            purpose="application",
            verified_only=True,
        )
        for record in records:
            if record.get("lesson_id") == lesson_id:
                continue
            if str(record.get("question_id")) in practiced_ids:
                continue
            question = dict(record.get("question") or {})
            question.update({
                "id": record.get("question_id"),
                "_is_transfer_check": True,
                "source_lesson_id": record.get("lesson_id"),
            })
            return question
    return None


def append_transfer_question(
    practice_questions: list[dict[str, Any]],
    *,
    course_id: str | None,
    lesson_id: str,
) -> list[dict[str, Any]]:
    """Copy a practice set and append at most one transfer item, idempotently."""
    questions = list(practice_questions or [])
    if any(isinstance(q, dict) and q.get("_is_transfer_check") for q in questions):
        return questions
    candidate = select_transfer_question(
        questions, course_id=course_id, lesson_id=lesson_id
    )
    if candidate is not None:
        questions.append(candidate)
    return questions


def audit_transfer_coverage() -> dict[str, Any]:
    """Count verified course/skill pairs with at least one reviewed application item."""
    practice_pairs: set[tuple[str, str]] = set()
    application_ids: dict[tuple[str, str], list[str]] = {}
    for record in question_engine.iter_question_records():
        if record.get("verification_status") != "verified":
            continue
        metadata = question_engine.attempt_metadata(
            str(record.get("question_id") or ""),
            course_id=record.get("course_id"),
            lesson_id=record.get("lesson_id"),
        )
        course, skill, purpose = (
            record.get("course_id"), metadata.get("skill_id"),
            metadata.get("question_purpose"),
        )
        if not course or not skill:
            continue
        key = (str(course), str(skill))
        if purpose in ("practice", "conceptual", "reasoning"):
            practice_pairs.add(key)
        elif purpose == "application":
            application_ids.setdefault(key, []).append(str(record.get("question_id")))

    rows = [{
        "course_id": course,
        "skill_id": skill,
        "has_verified_application_item": bool(application_ids.get((course, skill))),
        "application_question_ids": sorted(application_ids.get((course, skill), [])),
    } for course, skill in sorted(practice_pairs)]
    covered = sum(row["has_verified_application_item"] for row in rows)
    return {
        "practice_course_skill_pairs": len(rows),
        "covered_pairs": covered,
        "uncovered_pairs": len(rows) - covered,
        "coverage_percent": round(covered / len(rows) * 100) if rows else 0,
        "rows": rows,
    }
