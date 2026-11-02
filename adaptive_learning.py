"""Explainable, offline learning-intelligence recommendations.

This module turns existing question-level evidence into a ranked next action.
It is intentionally deterministic: no LLM, network request, or new learner data
is required. Scores are prioritisation heuristics, not validated diagnoses.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Any

import data
import math_taxonomy
import question_engine

ENGINE_VERSION = "learning-intelligence-2"


def _number(value: Any, default: float = 0.0) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return default
    return result if result >= 0 else default


def _result_ratio(result: dict[str, Any]) -> float:
    # Binary VQE records usually store only "correct"; marked responses store
    # score/max_marks. Do not interpret a missing score as zero for correct items.
    if "score" not in result and "marks_awarded" not in result:
        return 1.0 if result.get("correct") else 0.0
    maximum = _number(result.get("max_marks"), 1.0)
    earned = _number(result.get("score", result.get("marks_awarded")), 0.0)
    if maximum > 0:
        return min(1.0, max(0.0, earned / maximum))
    return 1.0 if result.get("correct") else 0.0


def _collect_skill_evidence(progress: dict[str, Any]) -> dict[str, dict[str, Any]]:
    evidence = {}
    for skill_id, skill in math_taxonomy.SKILLS.items():
        evidence[skill_id] = {
            "skill_id": skill_id,
            "skill": skill["label"],
            "strand": skill.get("strand", "Other"),
            "attempts": 0,
            "ratios": [],
            "recent_ratios": [],
            "mistake_tags": defaultdict(int),
            "locations": set(),
        }

    # The question registry is the source of truth for stable question-to-skill
    # mapping. Unverified/legacy questions are not assigned invented skill IDs.
    question_map = {}
    for record in question_engine.iter_question_records():
        question = record.get("question", {})
        skill_id = question.get("skill_id")
        if skill_id in evidence:
            question_map[(record.get("course_id"), record.get("lesson_id"), record.get("question_id"))] = {
                "skill_id": skill_id,
                "mistake_tag": question.get("mistake_tag"),
            }
            evidence[skill_id]["locations"].add((record.get("course_id"), record.get("lesson_id")))

    for course_id, course_progress in (progress or {}).items():
        if not isinstance(course_progress, dict):
            continue
        attempts_by_lesson = course_progress.get("practice_attempts", {})
        if not isinstance(attempts_by_lesson, dict):
            continue
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
                    if not isinstance(result, dict):
                        continue
                    qid = str(result.get("question_id") or "")
                    metadata = question_map.get((course_id, lesson_id, qid), {})
                    skill_id = result.get("skill_id") or metadata.get("skill_id")
                    if skill_id not in evidence:
                        continue
                    item = evidence[skill_id]
                    ratio = _result_ratio(result)
                    item["attempts"] += 1
                    item["ratios"].append(ratio)
                    item["recent_ratios"].append((str(attempt.get("completed_at") or ""), ratio))
                    tag = result.get("mistake_tag") or result.get("skill_tag") or metadata.get("mistake_tag")
                    if not result.get("correct") and tag:
                        item["mistake_tags"][str(tag)] += 1

    for item in evidence.values():
        item["accuracy"] = (
            sum(item["ratios"]) / len(item["ratios"]) if item["ratios"] else None
        )
        item["recent_ratios"].sort(key=lambda pair: pair[0])
        item["recent_accuracy"] = (
            sum(ratio for _, ratio in item["recent_ratios"][-3:]) /
            len(item["recent_ratios"][-3:]) if item["recent_ratios"] else None
        )
        item["repeat_errors"] = sum(item["mistake_tags"].values())
        item["locations"] = sorted(item["locations"])
        item["mistake_tags"] = dict(item["mistake_tags"])
    return evidence


def build_skill_trajectories(progress: dict[str, Any], limit: int = 5) -> dict[str, Any]:
    """Compare two consecutive three-answer windows for each evidenced skill.

    A directional trend is withheld until six recorded answers exist. The
    comparison is a short-term practice signal, not proof of retention,
    transfer, or mastery. Repeated answers are retained as practice evidence.
    """
    evidence = _collect_skill_evidence(progress)
    rows = []
    for skill_id, item in evidence.items():
        ordered = [ratio for _, ratio in item["recent_ratios"]]
        attempts = len(ordered)
        if not attempts:
            continue

        recent_window = ordered[-3:]
        recent_accuracy = sum(recent_window) / len(recent_window)
        previous_accuracy = None
        change_pp = None

        if attempts >= 6:
            previous_window = ordered[-6:-3]
            previous_accuracy = sum(previous_window) / len(previous_window)
            change_pp = round((recent_accuracy - previous_accuracy) * 100)
            if change_pp >= 15:
                trend = "Improving"
            elif change_pp <= -15:
                trend = "Needs attention"
            else:
                trend = "Steady"
        else:
            trend = "Building evidence"

        rows.append({
            "skill_id": skill_id,
            "skill": item["skill"],
            "strand": item["strand"],
            "attempts": attempts,
            "overall_accuracy_percent": round(item["accuracy"] * 100),
            "previous_window_accuracy_percent": (
                round(previous_accuracy * 100) if previous_accuracy is not None else None
            ),
            "recent_window_accuracy_percent": round(recent_accuracy * 100),
            "change_percentage_points": change_pp,
            "trend": trend,
        })

    status_order = {
        "Needs attention": 0,
        "Improving": 1,
        "Steady": 2,
        "Building evidence": 3,
    }
    rows.sort(key=lambda row: (
        status_order[row["trend"]],
        row["change_percentage_points"]
        if row["change_percentage_points"] is not None else 0,
        -row["attempts"],
        row["skill"],
    ))

    trend_counts = {
        label: sum(row["trend"] == label for row in rows)
        for label in status_order
    }
    try:
        display_limit = max(1, int(limit))
    except (TypeError, ValueError):
        display_limit = 5

    return {
        "engine_version": ENGINE_VERSION,
        "skills_with_evidence": len(rows),
        "skills_with_comparable_windows": sum(
            row["previous_window_accuracy_percent"] is not None for row in rows
        ),
        "trend_counts": trend_counts,
        "skills": rows[:display_limit],
        "evidence_note": (
            "A trend compares the latest three recorded answers with the three "
            "answers immediately before them. At least six answers are required. "
            "A 15-percentage-point change sets the Improving or Needs attention "
            "label; smaller changes are Steady. These are short-term practice "
            "signals, not validated measures of retention, transfer, or mastery."
        ),
    }


def _lesson_for_skill(skill_id: str, evidence_item: dict[str, Any]) -> tuple[str | None, str | None]:
    # Prefer the lesson containing verified questions for this skill.
    for course_id, lesson_id in evidence_item.get("locations", []):
        lesson, _ = data.get_lesson(course_id, lesson_id)
        if lesson:
            return course_id, lesson_id

    # A prerequisite may not yet have direct evidence. Find any course lesson
    # containing a verified question for that stable skill ID.
    for record in question_engine.iter_question_records():
        question = record.get("question", {})
        if question.get("skill_id") == skill_id:
            if data.get_lesson(record.get("course_id"), record.get("lesson_id"))[0]:
                return record.get("course_id"), record.get("lesson_id")
    return None, None


def _weakness_priority(item: dict[str, Any]) -> float:
    accuracy = item.get("accuracy")
    if accuracy is None:
        return 0.0
    # Low accuracy matters most; repeated errors and recent regression add
    # modest weight without allowing tiny samples to dominate.
    sample_weight = min(1.0, item["attempts"] / 4)
    priority = (1.0 - accuracy) * 70 * sample_weight
    priority += min(15, item["repeat_errors"] * 3)
    recent = item.get("recent_accuracy")
    if recent is not None and recent < accuracy:
        priority += min(10, (accuracy - recent) * 20)
    return round(priority, 2)


def build_learning_plan(progress: dict[str, Any], limit: int = 3) -> dict[str, Any]:
    """Return ranked skill actions, evidence and prerequisite-aware routing."""
    evidence = _collect_skill_evidence(progress)
    ranked = []
    for skill_id, item in evidence.items():
        if item["accuracy"] is None:
            continue
        priority = _weakness_priority(item)
        if priority <= 0:
            continue
        ranked.append((priority, skill_id, item))

    ranked.sort(key=lambda row: (-row[0], row[2]["accuracy"], row[2]["skill"]))
    actions = []
    for priority, skill_id, item in ranked:
        prerequisites = [
            prerequisite for prerequisite in math_taxonomy.SKILLS[skill_id].get("prerequisites", [])
            if prerequisite in evidence and (
                evidence[prerequisite]["accuracy"] is None
                or evidence[prerequisite]["accuracy"] < 0.75
            )
        ]
        target_skill = prerequisites[0] if prerequisites else skill_id
        target = evidence[target_skill]
        course_id, lesson_id = _lesson_for_skill(target_skill, target)
        if not course_id or not lesson_id:
            continue
        course = data.get_course(course_id)
        lesson, _ = data.get_lesson(course_id, lesson_id)
        if not course or not lesson:
            continue

        is_prerequisite = target_skill != skill_id
        target_accuracy = target.get("accuracy")
        if is_prerequisite:
            reason = (
                f"{item['skill']} depends on {target['skill']}, which has "
                "not yet reached the 75% practice-evidence threshold."
            )
            action = f"Review {target['skill']} before returning to {item['skill']}."
        elif item["repeat_errors"]:
            common_error = max(item["mistake_tags"], key=item["mistake_tags"].get)
            reason = (
                f"{item['attempts']} recorded answers average "
                f"{round(item['accuracy'] * 100)}%; recurring error: {common_error}."
            )
            action = f"Revisit {target['skill']} and practise identifying the step where {common_error.lower()} occurs."
        else:
            reason = (
                f"{item['attempts']} recorded answers average "
                f"{round(item['accuracy'] * 100)}%."
            )
            action = f"Review {target['skill']}, then complete a fresh practice set."
        actions.append({
            "skill_id": target_skill,
            "skill": target["skill"],
            "source_skill_id": skill_id,
            "course_id": course_id,
            "course_title": course["title"],
            "lesson_id": lesson_id,
            "lesson_title": lesson["title"],
            "priority": priority,
            "accuracy_percent": round(target_accuracy * 100) if target_accuracy is not None else None,
            "attempts": target["attempts"],
            "repeat_errors": target["repeat_errors"],
            "reason": reason,
            "action": action,
            "is_prerequisite_review": is_prerequisite,
        })
        if len(actions) >= max(1, int(limit)):
            break

    # Include transparent status counts so the UI can explain when evidence is
    # too sparse to make a confident personalised recommendation.
    tested = sum(item["accuracy"] is not None for item in evidence.values())
    return {
        "engine_version": ENGINE_VERSION,
        "actions": actions,
        "skills_tracked": len(evidence),
        "skills_with_practice_evidence": tested,
        "evidence_note": (
            "Recommendations use saved question-level practice results and the "
            "published skill prerequisites. They are transparent prototype "
            "heuristics, not a validated diagnosis or proof of mastery."
        ),
    }
