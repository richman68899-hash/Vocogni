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
