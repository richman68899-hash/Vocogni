"""Verified one-item follow-up checks for provisional diagnostic signals.

Confirmation results remain separate from ordinary practice attempts so they
can strengthen a diagnostic hypothesis without inflating practice accuracy
or the learner's skill-trajectory windows.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import logic
import question_engine

SUPPORTED_TYPES = {"mc", "numeric"}


def select_confirmation_question(*, course_id: str, skill_id: str, exclude_question_ids=()):
    """Return the first unused, VQE-verified MC/numeric practice item for a skill."""
    if not str(course_id or "").strip() or not str(skill_id or "").strip():
        return None
    # Any reviewed item can provide an independent check; conceptual
    # questions are important for diagnosing foundational understanding.
    candidates = question_engine.select_questions(
        course_id=str(course_id),
        skill_id=str(skill_id),
        verified_only=True,
        include_pathways=True,
        exclude_ids={str(item) for item in exclude_question_ids},
    )
    for record in candidates:
        if not isinstance(record, dict):
            continue
        question = record.get("question")
        qid = str(record.get("question_id") or "")
        lesson_id = str(record.get("lesson_id") or "")
        if not isinstance(question, dict) or not qid or not lesson_id:
            continue
        if question.get("type") not in SUPPORTED_TYPES:
            continue
        metadata = question_engine.attempt_metadata(qid, course_id=str(course_id), lesson_id=lesson_id)
        if metadata.get("verification_status") == "verified" and metadata.get("skill_id") == skill_id:
            return deepcopy(record)
    return None


def record_confirmation(progress: dict[str, Any], question_record: dict[str, Any], user_answer: Any) -> dict[str, Any]:
    """Store one verified confirmation result without retaining the raw response."""
    if not isinstance(progress, dict) or not isinstance(question_record, dict):
        raise TypeError("Learner progress and a selected question record are required.")
    question = question_record.get("question")
    course_id = str(question_record.get("course_id") or "").strip()
    lesson_id = str(question_record.get("lesson_id") or "").strip()
    qid = str(question_record.get("question_id") or "").strip()
    if not isinstance(question, dict) or question.get("type") not in SUPPORTED_TYPES:
        raise ValueError("Only verified multiple-choice or numeric questions can be used.")
    if not course_id or not lesson_id or not qid:
        raise ValueError("Question provenance is incomplete.")
    if user_answer is None or (isinstance(user_answer, str) and not user_answer.strip()):
        raise ValueError("An answer is required.")
    skill_id = str(question.get("skill_id") or "").strip()
    metadata = question_engine.attempt_metadata(qid, course_id=course_id, lesson_id=lesson_id)
    if (metadata.get("verification_status") != "verified"
            or metadata.get("skill_id") != skill_id
            or question_record.get("verification_status") != "verified"):
        raise ValueError("This question is no longer verified for the selected skill.")
    current = progress.get(course_id, {})
    if current and not isinstance(current, dict):
        raise ValueError("The learner's course progress is malformed.")
    attempts = current.get("skill_confirmation_attempts", []) if isinstance(current, dict) else []
    if not isinstance(attempts, list):
        raise ValueError("The learner's confirmation history is malformed.")
    for attempt in attempts:
        if not isinstance(attempt, dict):
            continue
        results = attempt.get("results", [])
        if isinstance(results, list) and any(
            isinstance(item, dict)
            and item.get("question_id") == qid
            and item.get("skill_id") == skill_id
            for item in results
        ):
            raise ValueError("This question has already been used for confirmation.")

    correct = bool(logic.check_answer(question, user_answer))
    answered_at = datetime.now(timezone.utc).isoformat()
    result_record = {
        "question_id": qid, "course_id": course_id, "lesson_id": lesson_id,
        "skill_id": skill_id, "verification_status": "verified",
        "verification_engine_version": metadata.get("verification_engine_version"),
        "question_version": metadata.get("question_version", 1),
        "question_purpose": metadata.get("question_purpose"),
        "correct": correct, "score": int(correct), "max_marks": 1,
        "answered_at": answered_at, "evidence_source": "diagnostic_confirmation",
    }
    attempt_record = {
        "lesson_id": lesson_id, "skill_id": skill_id,
        "source": "diagnostic_confirmation", "completed_at": answered_at,
        "results": [result_record],
    }
    course_progress = progress.setdefault(course_id, {})
    if not isinstance(course_progress, dict):
        raise ValueError("The learner's course progress is malformed.")
    course_progress.setdefault("skill_confirmation_attempts", []).append(attempt_record)
    return {
        "question_id": qid, "skill_id": skill_id, "correct": correct,
        "expected_answer": question.get("answer"),
        "explanation": str(question.get("explanation") or ""),
        "answered_at": answered_at,
    }


__all__ = ["SUPPORTED_TYPES", "select_confirmation_question", "record_confirmation"]
