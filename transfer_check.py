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
    exclude_question_ids: set[str] | None = None,
) -> dict[str, Any] | None:
    """Return one different-lesson, verified application item for a practiced skill."""
    if not course_id or not isinstance(practice_questions, list):
        return None

    practiced_ids = {
        str(item.get("id")) for item in practice_questions
        if isinstance(item, dict) and item.get("id")
    }
    practiced_ids.update(str(item) for item in (exclude_question_ids or set()))
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
    exclude_question_ids: set[str] | None = None,
) -> list[dict[str, Any]]:
    """Copy a practice set and append at most one transfer item, idempotently."""
    questions = list(practice_questions or [])
    if any(isinstance(q, dict) and q.get("_is_transfer_check") for q in questions):
        return questions
    candidate = select_transfer_question(
        questions, course_id=course_id, lesson_id=lesson_id,
        exclude_question_ids=exclude_question_ids,
    )
    if candidate is not None:
        questions.append(candidate)
    return questions


def audit_transfer_coverage() -> dict[str, Any]:
    """Count verified course/skill pairs with cross-lesson application items.

    This is catalogue coverage only; it does not validate novelty or learning
    transfer. An application item in the same lesson does not count as coverage.
    """
    practice_lessons: dict[tuple[str, str], set[str]] = {}
    application_records: dict[tuple[str, str], list[dict[str, str]]] = {}

    for record in question_engine.iter_question_records():
        if record.get("verification_status") != "verified":
            continue
        metadata = question_engine.attempt_metadata(
            str(record.get("question_id") or ""),
            course_id=record.get("course_id"),
            lesson_id=record.get("lesson_id"),
        )
        course = record.get("course_id")
        skill = metadata.get("skill_id")
        purpose = metadata.get("question_purpose")
        lesson = record.get("lesson_id")
        question_id = str(record.get("question_id") or "")
        if not course or not skill or not lesson or not question_id:
            continue
        key = (str(course), str(skill))
        if purpose in ("practice", "conceptual", "reasoning"):
            practice_lessons.setdefault(key, set()).add(str(lesson))
        elif purpose == "application":
            application_records.setdefault(key, []).append({
                "question_id": question_id,
                "lesson_id": str(lesson),
            })

    rows = []
    for (course, skill), lessons in sorted(practice_lessons.items()):
        candidates = [
            item for item in application_records.get((course, skill), [])
            if any(item["lesson_id"] != practice_lesson for practice_lesson in lessons)
        ]
        rows.append({
            "course_id": course,
            "skill_id": skill,
            "practice_lesson_ids": sorted(lessons),
            "has_cross_lesson_application_item": bool(candidates),
            "application_question_ids": sorted({item["question_id"] for item in candidates}),
        })

    covered = sum(row["has_cross_lesson_application_item"] for row in rows)
    total = len(rows)
    return {
        "practice_course_skill_pairs": total,
        "covered_pairs": covered,
        "uncovered_pairs": total - covered,
        "coverage_percent": round(covered / total * 100) if total else 0,
        "rows": rows,
    }
