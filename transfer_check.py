"""Selection and evidence rules for independent transfer checks.

A transfer item must be currently verified, authored for application, belong
to the same course and skill as the lesson practice, and come from a different
lesson. Transfer evidence is intentionally separate from practice accuracy.
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
    """Return one verified application item for a practiced skill, if available."""
    if not course_id or not isinstance(practice_questions, list):
        return None

    practiced_skills: list[str] = []
    for question in practice_questions:
        if not isinstance(question, dict) or question.get("_is_transfer_check"):
            continue
        metadata = question_engine.attempt_metadata(
            str(question.get("id") or ""),
            course_id=course_id,
            lesson_id=lesson_id,
        )
        skill_id = metadata.get("skill_id")
        if skill_id and skill_id not in practiced_skills:
            practiced_skills.append(skill_id)

    for skill_id in practiced_skills:
        candidates = question_engine.select_questions(
            course_id=course_id,
            skill_id=skill_id,
            purpose="application",
            verified_only=True,
        )
        for record in candidates:
            if record.get("lesson_id") == lesson_id:
                continue
            question = dict(record["question"])
            question["_is_transfer_check"] = True
            question["source_lesson_id"] = record.get("lesson_id")
            question["id"] = record.get("question_id")
            return question
    return None


def append_transfer_question(
    practice_questions: list[dict[str, Any]],
    *,
    course_id: str | None,
    lesson_id: str,
) -> list[dict[str, Any]]:
    """Copy a practice set and append one eligible transfer item at most once."""
    questions = list(practice_questions or [])
    if any(isinstance(item, dict) and item.get("_is_transfer_check") for item in questions):
        return questions
    transfer = select_transfer_question(
        questions, course_id=course_id, lesson_id=lesson_id
    )
    if transfer is not None:
        questions.append(transfer)
    return questions


def audit_transfer_coverage() -> dict[str, Any]:
    """Summarise which verified skill records have a usable transfer item.

    Coverage is reported at the course+skill level. This is a catalogue audit,
    not a claim that any item has been field-tested for transfer validity.
    """
    practice_pairs: set[tuple[str, str]] = set()
    application_pairs: set[tuple[str, str]] = set()
    application_records: dict[tuple[str, str], list[str]] = {}

    for record in question_engine.iter_question_records():
        if record.get("verification_status") != "verified":
            continue
        question = record.get("question") or {}
        metadata = question_engine.attempt_metadata(
            str(record.get("question_id") or ""),
            course_id=record.get("course_id"),
            lesson_id=record.get("lesson_id"),
        )
        skill_id = metadata.get("skill_id")
        course = record.get("course_id")
        lesson = record.get("lesson_id")
        if not skill_id or not course or not lesson:
            continue
        pair = (str(course), str(skill_id))
        if metadata.get("question_purpose") in ("practice", "conceptual", "reasoning"):
            practice_pairs.add(pair)
        if metadata.get("question_purpose") == "application":
            application_pairs.add(pair)
            application_records.setdefault(pair, []).append(str(record.get("question_id")))

    rows = []
    for course, skill_id in sorted(practice_pairs):
        ids = application_records.get((course, skill_id), [])
        rows.append({
            "course_id": course,
            "skill_id": skill_id,
            "has_verified_application_item": bool(ids),
            "application_question_ids": sorted(ids),
        })
    covered = sum(bool(row["has_verified_application_item"]) for row in rows)
    return {
        "practice_course_skill_pairs": len(rows),
        "covered_pairs": covered,
        "uncovered_pairs": len(rows) - covered,
        "coverage_percent": round(covered / len(rows) * 100) if rows else 0,
        "rows": rows,
    }
