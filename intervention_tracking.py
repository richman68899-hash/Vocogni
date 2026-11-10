"""Privacy-minimising records of learner-visible teaching-support exposures.

The report links a support exposure to the next few later, currently verified
answers for the same skill. It is a descriptive sequence, not causal attribution.
Raw answers, prompts, notes, or chat content are never stored here.
"""
from __future__ import annotations

from bisect import bisect_right
from datetime import datetime, timezone
from typing import Any

import data
import math_taxonomy
import question_engine


SCHEMA_VERSION = 1
HISTORY_LIMIT = 300
FOLLOW_UP_LIMIT = 3

INTERVENTION_LABELS = {
    "concept_explanation": "Concept explanation shown",
    "worked_example": "Worked example shown",
    "hint": "Hint shown",
    "answer_feedback": "Answer feedback shown",
    "targeted_repair": "Targeted repair cue shown",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _result_ratio(result: dict[str, Any]) -> float:
    if "score" not in result and "marks_awarded" not in result:
        return 1.0 if result.get("correct") else 0.0
    try:
        maximum = float(result.get("max_marks", 1) or 1)
        earned = float(result.get("score", result.get("marks_awarded", 0)) or 0)
    except (TypeError, ValueError):
        return 1.0 if result.get("correct") else 0.0
    if maximum <= 0:
        return 1.0 if result.get("correct") else 0.0
    return min(1.0, max(0.0, earned / maximum))


def record_intervention(
    progress: dict[str, Any],
    *,
    course_id: str,
    lesson_id: str,
    intervention_type: str,
    event_id: str,
    skill_id: str | None = None,
    question_id: str | None = None,
    attempt_number: int | None = None,
    occurred_at: str | None = None,
) -> bool:
    """Append one idempotent exposure record; return False for a duplicate."""
    if not isinstance(progress, dict):
        raise TypeError("Learner progress must be a dictionary.")
    if intervention_type not in INTERVENTION_LABELS:
        raise ValueError(f"Unsupported intervention type: {intervention_type!r}")
    if not str(course_id or "").strip() or not str(lesson_id or "").strip():
        raise ValueError("Course and lesson IDs are required.")
    event_id = str(event_id or "").strip()
    if not event_id:
        raise ValueError("A stable event_id is required.")

    timestamp = _parse_timestamp(occurred_at) or _parse_timestamp(_now())
    course_progress = progress.setdefault(str(course_id), {})
    if not isinstance(course_progress, dict):
        course_progress = {}
        progress[str(course_id)] = course_progress
    events = course_progress.setdefault("intervention_events", [])
    if not isinstance(events, list):
        events = []
        course_progress["intervention_events"] = events

    if any(
        isinstance(item, dict) and item.get("event_id") == event_id
        for item in events
    ):
        return False

    event = {
        "schema_version": SCHEMA_VERSION,
        "event_id": event_id[:240],
        "intervention_type": intervention_type,
        "intervention_label": INTERVENTION_LABELS[intervention_type],
        "lesson_id": str(lesson_id)[:120],
        "skill_id": str(skill_id)[:160] if skill_id else None,
        "question_id": str(question_id)[:160] if question_id else None,
        "attempt_number": (
            max(1, int(attempt_number))
            if attempt_number is not None
            else None
        ),
        "occurred_at": timestamp.isoformat(),
    }
    events.append(event)
    course_progress["intervention_events"] = events[-HISTORY_LIMIT:]
    return True


def _verified_answers(progress: dict[str, Any]) -> list[dict[str, Any]]:
    answers: list[dict[str, Any]] = []
    for raw_course_id, course_progress in progress.items():
        course_id = str(raw_course_id)
        if not isinstance(course_progress, dict):
            continue
        attempts_by_lesson = course_progress.get("practice_attempts", {})
        if not isinstance(attempts_by_lesson, dict):
            continue
        for raw_lesson_id, attempts in attempts_by_lesson.items():
            lesson_id = str(raw_lesson_id)
            if not isinstance(attempts, list):
                continue
            for attempt in attempts:
                if not isinstance(attempt, dict):
                    continue
                results = attempt.get("results", [])
                if not isinstance(results, list):
                    continue
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    question_id = str(result.get("question_id") or "")
                    answered_at = _parse_timestamp(result.get("answered_at"))
                    if not question_id or answered_at is None:
                        continue
                    # Practice-sprint containers may hold a question sourced
                    # from another lesson. The saved provenance identifies its
                    # canonical source lesson; fall back only for legacy records.
                    source_lesson_id = str(
                        result.get("lesson_id")
                        or result.get("source_lesson_id")
                        or lesson_id
                    )
                    metadata = question_engine.attempt_metadata(
                        question_id,
                        course_id=course_id,
                        lesson_id=source_lesson_id,
                    )
                    if metadata.get("verification_status") != "verified":
                        continue
                    skill_id = metadata.get("skill_id")
                    if not skill_id:
                        continue
                    recorded_skill = result.get("skill_id")
                    if recorded_skill and recorded_skill != skill_id:
                        continue
                    answers.append({
                        "course_id": course_id,
                        "skill_id": skill_id,
                        "question_id": question_id,
                        "answered_at": answered_at,
                        "ratio": _result_ratio(result),
                    })
    answers.sort(key=lambda item: item["answered_at"])
    return answers


def build_intervention_report(
    progress: dict[str, Any],
    limit: int = 12,
) -> dict[str, Any]:
    """Describe each support exposure and the next three verified same-skill answers."""
    if not isinstance(progress, dict):
        progress = {}

    # Index the ordered answer stream once. Each support event can then find
    # its next three same-course/same-skill answers in O(log n), rather than
    # rescanning every answer for every event.
    answers_by_skill: dict[tuple[str, str], dict[str, list[Any]]] = {}
    for answer in _verified_answers(progress):
        key = (answer["course_id"], answer["skill_id"])
        bucket = answers_by_skill.setdefault(
            key, {"timestamps": [], "answers": []}
        )
        bucket["timestamps"].append(answer["answered_at"])
        bucket["answers"].append(answer)

    events: list[dict[str, Any]] = []
    for raw_course_id, course_progress in progress.items():
        course_id = str(raw_course_id)
        if not isinstance(course_progress, dict):
            continue
        stored_events = course_progress.get("intervention_events", [])
        if not isinstance(stored_events, list):
            continue
        for event in stored_events:
            if not isinstance(event, dict):
                continue
            intervention_type = event.get("intervention_type")
            if intervention_type not in INTERVENTION_LABELS:
                continue
            occurred_at = _parse_timestamp(event.get("occurred_at"))
            if occurred_at is None or not event.get("event_id"):
                continue
            skill_id = str(event.get("skill_id") or "") or None
            follow_up = []
            if skill_id:
                bucket = answers_by_skill.get((course_id, skill_id))
                if bucket:
                    start = bisect_right(bucket["timestamps"], occurred_at)
                    follow_up = bucket["answers"][
                        start:start + FOLLOW_UP_LIMIT
                    ]

            course = data.get_course(course_id)
            lesson, _ = data.get_lesson(course_id, str(event.get("lesson_id") or ""))
            events.append({
                "event_id": str(event["event_id"]),
                "course_id": course_id,
                "course_title": str(course.get("title", course_id)) if course else course_id,
                "lesson_id": str(event.get("lesson_id") or ""),
                "lesson_title": str(lesson.get("title", event.get("lesson_id") or "Lesson")) if lesson else str(event.get("lesson_id") or "Lesson"),
                "skill_id": skill_id,
                "skill": math_taxonomy.SKILLS[skill_id]["label"] if skill_id in math_taxonomy.SKILLS else None,
                "intervention_type": intervention_type,
                "intervention_label": INTERVENTION_LABELS[intervention_type],
                "occurred_at": occurred_at.isoformat(),
                "follow_up_answer_count": len(follow_up),
                "follow_up_accuracy_percent": (
                    round(sum(item["ratio"] for item in follow_up) / len(follow_up) * 100)
                    if follow_up else None
                ),
            })

    events.sort(key=lambda item: item["occurred_at"], reverse=True)
    try:
        display_limit = max(1, int(limit))
    except (TypeError, ValueError):
        display_limit = 12

    return {
        "events_total": len(events),
        "events_with_follow_up": sum(item["follow_up_answer_count"] > 0 for item in events),
        "events": events[:display_limit],
        "evidence_note": (
            "Follow-up is the next up to three later answers that still pass the "
            "current Verified Question Engine check for the same skill. Answers "
            "are resolved using their saved canonical question-source lesson when "
            "available, with the attempt lesson used only for legacy records. Multiple "
            "support events can share subsequent answers; this is a descriptive "
            "sequence, not evidence that a support caused a result. Older answer "
            "records without per-answer timestamps are not matched."
        ),
    }


__all__ = ["INTERVENTION_LABELS", "record_intervention", "build_intervention_report"]
