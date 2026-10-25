"""Personalized revision-sprint logic, built on Vocogni's authored course content.

This module is framework-free. It selects existing supported practice questions,
prioritizes documented weaknesses, grades with the current transparent graders,
and saves completed sprint results into the existing practice-history schema.
It does not generate AI content or predict an official examination grade.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timezone

import data
import logic
import question_engine


SUPPORTED_QUESTION_TYPES = ("mc", "numeric", "open_ended")
WEAKNESS_STATUS_RANK = {
    "Needs review": 0,
    "Developing": 1,
    "Not tested": 2,
    "Promising evidence": 3,
}


def _is_supported_question(question):
    if not isinstance(question, dict) or not question.get("id") or not question.get("prompt"):
        return False

    question_type = question.get("type")
    if question_type == "mc":
        options = question.get("options")
        return isinstance(options, list) and len(options) >= 2 and question.get("answer") in options

    if question_type == "numeric":
        try:
            float(question.get("answer"))
            return True
        except (TypeError, ValueError):
            return False

    if question_type == "open_ended":
        points = question.get("marking_points")
        try:
            maximum = int(question.get("max_marks", 0))
        except (TypeError, ValueError):
            return False
        return isinstance(points, list) and bool(points) and maximum > 0

    return False


def question_bank_for_course(course_id):
    """Collect unique supported items through the shared VQE catalogue.

    VQE pilot lessons and pathway items are strict: only reviewed, currently
    verified content is included. Non-pilot lesson questions remain on the
    legacy-compatible path while those lessons await review.
    """
    course = data.get_course(course_id)
    if not course:
        return []

    lesson_indexes = {
        str(lesson.get("id") or ""): index
        for index, lesson in enumerate(course.get("lessons", []))
        if isinstance(lesson, dict)
    }
    per_lesson_index = defaultdict(int)
    bank = []

    for record in question_engine.iter_question_records(course_id=course_id):
        lesson_id = str(record.get("lesson_id") or "")
        question = record.get("question", {})
        status = record.get("verification_status", "legacy")
        source_fields = record.get("source_fields", [record.get("source_field", "")])
        is_pathway = any(
            str(field).startswith("diagnostic.pathways.")
            for field in source_fields
        )
        pilot = question_engine.is_vqe_pilot_lesson(course_id, lesson_id)

        if (pilot or is_pathway) and status != "verified":
            continue
        if not _is_supported_question(question):
            continue

        lesson_title = str(record.get("lesson_title") or lesson_id or "Untitled lesson")
        skill = (
            question.get("skill_tag")
            or question.get("skill")
            or question.get("mistake_tag")
            or lesson_title
        )
        bank.append({
            "lesson_id": lesson_id,
            "lesson_title": lesson_title,
            "lesson_index": lesson_indexes.get(lesson_id, 0),
            "question_index": per_lesson_index[lesson_id],
            "question_id": str(record["question_id"]),
            "skill": " ".join(str(skill).strip().split()) or lesson_title,
            "skill_id": question.get("skill_id"),
            "question_version": question.get("question_version", 1),
            "verification_status": status,
            "question_purpose": question.get("purpose"),
            "verification_engine_version": question.get(
                "verification_engine_version", question_engine.ENGINE_VERSION
            ),
            "question": deepcopy(question),
        })
        per_lesson_index[lesson_id] += 1
    return bank


def weak_skills_for_course(progress, course_id, limit=3):
    """Return evidence-led skills that currently need review or development."""
    receipt = logic.mastery_receipt_for_course(progress, course_id)
    if not receipt:
        return []

    priority = {"Needs review": 0, "Developing": 1}
    rows = []
    for item in receipt.get("skills", []):
        status = item.get("status")
        if status not in priority:
            continue
        percent = item.get("practice_performance_percent")
        sort_percent = 101 if percent is None else float(percent)
        rows.append((priority[status], sort_percent, item.get("skill", "")))
    rows.sort(key=lambda row: (row[0], row[1], str(row[2]).casefold()))
    return [label for _, _, label in rows[:max(0, int(limit))] if label]


def _question_history(progress, course_id):
    """Map saved question attempts by source lesson and question ID."""
    course_progress = progress.get(course_id, {})
    attempts_by_lesson = course_progress.get("practice_attempts", {}) if isinstance(course_progress, dict) else {}
    history = defaultdict(list)
    if not isinstance(attempts_by_lesson, dict):
        return history

    for lesson_id, attempts in attempts_by_lesson.items():
        if not isinstance(attempts, list):
            continue
        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue
            results = attempt.get("results", [])
            if not isinstance(results, list):
                continue
            for result in results:
                if not isinstance(result, dict) or result.get("question_id") is None:
                    continue
                key = (str(lesson_id), str(result["question_id"]))
                history[key].append({
                    "correct": bool(result.get("correct")),
                    "score": result.get("score", int(bool(result.get("correct")))),
                    "max_marks": result.get("max_marks", 1),
                })
    return history


def select_questions(progress, course_id, count=5, mode="personalized"):
    """Select a bounded sprint and rotate across weak skills or lessons."""
    bank = question_bank_for_course(course_id)
    if not bank:
        return []

    try:
        count = max(1, int(count))
    except (TypeError, ValueError):
        count = 5
    count = min(count, len(bank))
    if mode not in ("personalized", "balanced"):
        mode = "personalized"

    history = _question_history(progress, course_id)
    receipt = logic.mastery_receipt_for_course(progress, course_id)
    skill_status = {}
    if receipt:
        for item in receipt.get("skills", []):
            label = str(item.get("skill") or "").strip()
            if label:
                skill_status[label.casefold()] = item.get("status", "Not tested")

    ranked = []
    for item in bank:
        past = history.get((item["lesson_id"], item["question_id"]), [])
        wrong_count = sum(not row["correct"] for row in past)
        latest_correct = past[-1]["correct"] if past else None
        status = skill_status.get(item["skill"].casefold(), "Not tested")
        status_rank = WEAKNESS_STATUS_RANK.get(status, 2)

        if mode == "balanced":
            priority = 0
        elif latest_correct is False:
            priority = 0
        elif status == "Needs review":
            priority = 0
        elif status == "Developing":
            priority = 1
        elif status == "Not tested" or not past:
            priority = 2
        elif status == "Promising evidence":
            priority = 3
        else:
            priority = status_rank

        ranked.append({
            **item,
            "_priority": priority,
            "_wrong_count": wrong_count,
            "_attempt_count": len(past),
            "_latest_correct": latest_correct,
        })

    # Group candidates so a sprint samples more than one skill (or lesson)
    # when the course bank allows it, rather than taking five adjacent items.
    groups = {}
    for item in ranked:
        group_key = item["skill"].casefold() if mode == "personalized" else item["lesson_id"]
        if group_key not in groups:
            groups[group_key] = {
                "first_index": item["lesson_index"] * 10000 + item["question_index"],
                "items": [],
            }
        groups[group_key]["items"].append(item)

    for group in groups.values():
        group["items"].sort(key=lambda item: (
            item["_priority"],
            0 if item["_latest_correct"] is False else 1,
            -item["_wrong_count"],
            item["_attempt_count"],
            item["lesson_index"],
            item["question_index"],
        ))

    group_order = sorted(
        groups,
        key=lambda key: (
            groups[key]["items"][0]["_priority"],
            groups[key]["first_index"],
            key,
        ),
    )
    chosen = []
    while len(chosen) < count:
        added_this_round = False
        for key in group_order:
            if groups[key]["items"] and len(chosen) < count:
                chosen.append(groups[key]["items"].pop(0))
                added_this_round = True
        if not added_this_round:
            break

    return [
        {
            "lesson_id": item["lesson_id"],
            "lesson_title": item["lesson_title"],
            "skill": item["skill"],
            "skill_id": item.get("skill_id"),
            "question_id": item["question_id"],
            "question_version": item.get("question_version", 1),
            "verification_status": item.get("verification_status", "legacy"),
            "question_purpose": item.get("question_purpose"),
            "verification_engine_version": item.get(
                "verification_engine_version", question_engine.ENGINE_VERSION
            ),
            "question": deepcopy(item["question"]),
        }
        for item in chosen
    ]


def evaluate_question(question, answer):
    """Grade an answer using the same configured rules as lesson practice."""
    if answer is None or (isinstance(answer, str) and not answer.strip()):
        raise ValueError("An answer is required.")

    question_type = question.get("type")
    marking_result = None
    if question_type == "open_ended":
        if question.get("grader") == "math":
            import math_grading
            grader = math_grading
        else:
            import chemistry_grading
            grader = chemistry_grading
        marking_result = grader.evaluate_open_response(question, answer)
        correct = bool(marking_result.get("full_credit"))
        maximum = int(marking_result.get("max_marks", question.get("max_marks", 1)))
        score = int(marking_result.get("score", 0))
    else:
        correct = bool(logic.check_answer(question, answer))
        maximum = 1
        score = int(correct)

    return {
        "correct": correct,
        "score": score,
        "max_marks": max(1, maximum),
        "marking_result": marking_result,
    }


def record_sprint_attempt(progress, course_id, graded_items, completed_at=None):
    """Save one sprint's results into existing lesson practice history."""
    if not graded_items:
        raise ValueError("A revision sprint needs at least one graded answer.")

    if completed_at is None:
        completed_at = datetime.now(timezone.utc).isoformat()
    elif isinstance(completed_at, datetime):
        if completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=timezone.utc)
        completed_at = completed_at.isoformat()

    course_progress = progress.setdefault(course_id, logic.blank_course_progress())
    defaults = logic.blank_course_progress()
    for key, value in defaults.items():
        course_progress.setdefault(key, deepcopy(value))

    grouped_results = {}
    total_score = 0
    total_marks = 0
    full_credit = 0

    for entry in graded_items:
        item = entry["item"]
        question = item["question"]
        evaluation = entry["evaluation"]
        is_correct = bool(evaluation["correct"])
        score = int(evaluation["score"])
        maximum = max(1, int(evaluation["max_marks"]))
        total_score += score
        total_marks += maximum
        full_credit += int(is_correct)

        logic.record_answer(progress, course_id, question, is_correct)
        result = {
            "question_id": str(question["id"]),
            "correct": is_correct,
            "score": score,
            "max_marks": maximum,
            "skill_tag": item["skill"],
            "mistake_tag": question.get("mistake_tag", item["skill"]),
            "question_version": item.get("question_version", question.get("question_version", 1)),
            "skill_id": item.get("skill_id", question.get("skill_id")),
            "question_purpose": item.get("question_purpose", question.get("purpose")),
            "verification_status": item.get(
                "verification_status", question.get("verification_status", "legacy")
            ),
            "verification_engine_version": item.get(
                "verification_engine_version",
                question.get("verification_engine_version", question_engine.ENGINE_VERSION),
            ),
        }
        grouped_results.setdefault(item["lesson_id"], []).append(result)

    history_by_lesson = course_progress.setdefault("practice_attempts", {})
    for lesson_id, results in grouped_results.items():
        history = history_by_lesson.setdefault(lesson_id, [])
        attempt_numbers = []
        for attempt in history:
            if isinstance(attempt, dict):
                try:
                    attempt_numbers.append(int(attempt.get("attempt_number", 0)))
                except (TypeError, ValueError):
                    pass
        awarded = sum(int(result["score"]) for result in results)
        maximum = sum(int(result["max_marks"]) for result in results)
        correct = sum(bool(result["correct"]) for result in results)
        history.append({
            "attempt_number": max(attempt_numbers, default=0) + 1,
            "pathway": "revision_sprint",
            "pathway_label": "Personalized Revision Sprint",
            "correct": correct,
            "total": len(results),
            "percent": round(awarded / maximum * 100) if maximum else 0,
            "accuracy_percent": round(correct / len(results) * 100) if results else 0,
            "marks_awarded": awarded,
            "max_marks": maximum,
            "completed_at": completed_at,
            "results": results,
        })

    return {
        "questions": len(graded_items),
        "full_credit_answers": full_credit,
        "marks_awarded": total_score,
        "max_marks": total_marks,
        "percent": round(total_score / total_marks * 100) if total_marks else 0,
        "practice_attempts_saved": len(grouped_results),
        "completed_at": completed_at,
    }
