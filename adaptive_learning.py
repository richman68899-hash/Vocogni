"""Explainable, offline learning-intelligence recommendations.

This module turns existing question-level evidence into a ranked next action.
It is intentionally deterministic: no LLM, network request, or new learner data
is required. Scores are prioritisation heuristics, not validated diagnoses.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
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


# Diagnostic labels are authored wording, not stable skill IDs. These explicit
# mappings connect the current lower-secondary diagnostic items to the VQE
# skill taxonomy. Unmapped tags are deliberately left unclassified.
_DIAGNOSTIC_SKILL_TAG_MAP = {
    ("fractions", "meaning of the denominator"): "math.number.fraction_representation",
    ("fractions", "representing fractions"): "math.number.fraction_representation",
    ("fractions", "equivalent fractions"): "math.number.fraction_representation",
    ("fractions", "comparing fractions"): "math.number.fraction_representation",
    ("fractions", "applying fractions in context"): "math.number.fraction_operations",
    ("algebra", "meaning of a variable"): "math.algebra.variables_expressions",
    ("algebra", "solving a one-step equation"): "math.algebra.linear_equations",
    ("algebra", "solving equations with brackets"): "math.algebra.linear_equations",
    ("word_problems", "choosing a basic operation"): "math.problem_solving.expression_translation",
    ("word_problems", "translating key words"): "math.problem_solving.expression_translation",
    ("word_problems", "translating relationships"): "math.problem_solving.expression_translation",
    ("word_problems", "selecting relevant information"): "math.problem_solving.expression_translation",
    ("word_problems", "building a cost model"): "math.problem_solving.linear_cost_models",
    ("analog_clocks", "clock hand roles"): "math.time.clock_parts",
    ("analog_clocks", "counting minute groups of five"): "math.time.minute_counting",
    ("analog_clocks", "hour hand position"): "math.time.hour_hand_position",
    ("analog_clocks", "combining both hands"): "math.time.reading_analog_time",
    ("analog_clocks", "elapsed time"): "math.time.elapsed_time",
}


def _normalise_label(value: Any) -> str:
    return " ".join(str(value or "").strip().casefold().split())


def _parse_event_timestamp(value: Any) -> datetime | None:
    """Parse saved ISO timestamps; treat naive legacy timestamps as UTC."""
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _event_ratio(result: dict[str, Any]) -> float:
    """Use awarded marks for marked answers and correctness for binary items."""
    return _result_ratio(result)


def _course_lesson_labels(course_id: str, lesson_id: str) -> tuple[str, str]:
    course = data.get_course(course_id)
    lesson, _ = data.get_lesson(course_id, lesson_id)
    return (
        str(course.get("title", course_id)) if course else str(course_id),
        str(lesson.get("title", lesson_id)) if lesson else str(lesson_id),
    )


def build_intervention_timeline(
    progress: dict[str, Any],
    limit: int = 12,
) -> dict[str, Any]:
    """Build a chronological, per-skill record of diagnostics and interventions.

    Includes explicitly mapped diagnostic skill tags, verified question-level
    practice attempts, and verified Coach answers. Unverified/generated items
    are excluded. Comparisons are shown only when both events contain at least
    two answers; they remain descriptive because the question sets may differ.
    """
    if not isinstance(progress, dict):
        progress = {}

    events: list[dict[str, Any]] = []

    for raw_course_id, course_progress in progress.items():
        course_id = str(raw_course_id)
        if not isinstance(course_progress, dict):
            continue
        course_title, _ = _course_lesson_labels(course_id, "")

        # 1) Baseline diagnostic results, grouped by the explicit diagnostic
        # skill-tag mapping above.
        diagnostics = course_progress.get("diagnostics", {})
        if isinstance(diagnostics, dict):
            for lesson_id, diagnostic in diagnostics.items():
                if not isinstance(diagnostic, dict):
                    continue
                completed = _parse_event_timestamp(diagnostic.get("completed_at"))
                if completed is None:
                    continue
                lesson_title = _course_lesson_labels(course_id, str(lesson_id))[1]
                by_skill: dict[str, list[float]] = defaultdict(list)
                review = diagnostic.get("answer_review", [])
                if not isinstance(review, list):
                    review = []
                for result in review:
                    if not isinstance(result, dict):
                        continue
                    tag = _normalise_label(result.get("skill_tag"))
                    skill_id = _DIAGNOSTIC_SKILL_TAG_MAP.get((course_id, tag))
                    if skill_id not in math_taxonomy.SKILLS:
                        continue
                    by_skill[skill_id].append(_event_ratio(result))

                for skill_id, ratios in by_skill.items():
                    if not ratios:
                        continue
                    events.append({
                        "event_id": f"diagnostic:{course_id}:{lesson_id}:{skill_id}",
                        "course_id": course_id,
                        "course_title": course_title,
                        "lesson_id": str(lesson_id),
                        "lesson_title": lesson_title,
                        "skill_id": skill_id,
                        "skill": math_taxonomy.SKILLS[skill_id]["label"],
                        "event_type": "baseline",
                        "intervention_label": "Diagnostic baseline",
                        "completed_at": completed.isoformat(),
                        "_sort_at": completed,
                        "correct_answers": sum(1 for ratio in ratios if ratio >= 0.999),
                        "total_items": len(ratios),
                        "accuracy_percent": round(sum(ratios) / len(ratios) * 100),
                    })

        # 2) Saved lesson / revision-sprint practice. A skill is included only
        # when its answer provenance explicitly marks it as VQE-verified.
        attempts_by_lesson = course_progress.get("practice_attempts", {})
        if isinstance(attempts_by_lesson, dict):
            for lesson_id, attempts in attempts_by_lesson.items():
                if not isinstance(attempts, list):
                    continue
                lesson_title = _course_lesson_labels(course_id, str(lesson_id))[1]
                for attempt_index, attempt in enumerate(attempts):
                    if not isinstance(attempt, dict):
                        continue
                    completed = _parse_event_timestamp(attempt.get("completed_at"))
                    if completed is None:
                        continue
                    grouped: dict[str, list[float]] = defaultdict(list)
                    results = attempt.get("results", [])
                    if not isinstance(results, list):
                        continue
                    for result in results:
                        if not isinstance(result, dict):
                            continue
                        skill_id = result.get("skill_id")
                        if (
                            result.get("verification_status") != "verified"
                            or not isinstance(skill_id, str)
                            or skill_id not in math_taxonomy.SKILLS
                        ):
                            continue
                        grouped[skill_id].append(_event_ratio(result))

                    pathway = str(attempt.get("pathway_label") or "").strip()
                    if not pathway:
                        raw_pathway = str(attempt.get("pathway") or "").strip()
                        pathway = (
                            "Personalized Revision Sprint"
                            if raw_pathway == "revision_sprint"
                            else raw_pathway.replace("_", " ").title() or "Practice"
                        )

                    for skill_id, ratios in grouped.items():
                        if not ratios:
                            continue
                        events.append({
                            "event_id": (
                                f"practice:{course_id}:{lesson_id}:"
                                f"{attempt.get('attempt_number', attempt_index + 1)}:"
                                f"{skill_id}:{completed.isoformat()}"
                            ),
                            "course_id": course_id,
                            "course_title": course_title,
                            "lesson_id": str(lesson_id),
                            "lesson_title": lesson_title,
                            "skill_id": skill_id,
                            "skill": math_taxonomy.SKILLS[skill_id]["label"],
                            "event_type": "practice",
                            "intervention_label": pathway,
                            "completed_at": completed.isoformat(),
                            "_sort_at": completed,
                            "correct_answers": sum(1 for ratio in ratios if ratio >= 0.999),
                            "total_items": len(ratios),
                            "accuracy_percent": round(sum(ratios) / len(ratios) * 100),
                        })

        # 3) Coach answers are stored individually. Group verified Coach
        # attempts by skill and UTC calendar day to avoid treating each answer
        # as a separate intervention event.
        coach_data = course_progress.get("coach", {})
        coach_attempts = coach_data.get("attempts", []) if isinstance(coach_data, dict) else []
        coach_groups: dict[tuple[str, str, str], list[tuple[datetime, float]]] = defaultdict(list)
        if isinstance(coach_attempts, list):
            for result in coach_attempts:
                if not isinstance(result, dict):
                    continue
                skill_id = result.get("skill_id")
                completed = _parse_event_timestamp(result.get("completed_at"))
                if (
                    result.get("verification_status") != "verified"
                    or not isinstance(skill_id, str)
                    or skill_id not in math_taxonomy.SKILLS
                    or completed is None
                ):
                    continue
                lesson_id = str(result.get("lesson_id") or "")
                day = completed.date().isoformat()
                coach_groups[(lesson_id, skill_id, day)].append(
                    (completed, 1.0 if result.get("correct") else 0.0)
                )

        for (lesson_id, skill_id, day), rows in coach_groups.items():
            rows.sort(key=lambda item: item[0])
            ratios = [ratio for _, ratio in rows]
            completed = rows[-1][0]
            lesson_title = _course_lesson_labels(course_id, lesson_id)[1]
            events.append({
                "event_id": f"coach:{course_id}:{lesson_id}:{skill_id}:{day}",
                "course_id": course_id,
                "course_title": course_title,
                "lesson_id": lesson_id,
                "lesson_title": lesson_title,
                "skill_id": skill_id,
                "skill": math_taxonomy.SKILLS[skill_id]["label"],
                "event_type": "coach",
                "intervention_label": "Coach practice",
                "completed_at": completed.isoformat(),
                "_sort_at": completed,
                "correct_answers": sum(1 for ratio in ratios if ratio >= 0.999),
                "total_items": len(ratios),
                "accuracy_percent": round(sum(ratios) / len(ratios) * 100),
            })

    # Compare each event with the most recent earlier event for that skill
    # that also has at least two answers. Single-answer events remain visible
    # but cannot move the comparison baseline.
    by_skill_course: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for event in events:
        by_skill_course[(event["course_id"], event["skill_id"])].append(event)

    for skill_events in by_skill_course.values():
        skill_events.sort(key=lambda item: item["_sort_at"])
        previous_comparable = None
        for event in skill_events:
            event["comparison"] = None
            if event["total_items"] >= 2 and previous_comparable is not None:
                delta = event["accuracy_percent"] - previous_comparable["accuracy_percent"]
                if delta >= 15:
                    direction = "Higher recorded performance"
                elif delta <= -15:
                    direction = "Lower recorded performance"
                else:
                    direction = "Similar recorded performance"
                event["comparison"] = {
                    "direction": direction,
                    "change_percentage_points": delta,
                    "previous_accuracy_percent": previous_comparable["accuracy_percent"],
                    "previous_items": previous_comparable["total_items"],
                    "previous_label": previous_comparable["intervention_label"],
                    "previous_completed_at": previous_comparable["completed_at"],
                }
            if event["total_items"] >= 2:
                previous_comparable = event

    events.sort(key=lambda item: (item["_sort_at"], item["skill"]), reverse=True)
    try:
        display_limit = max(1, int(limit))
    except (TypeError, ValueError):
        display_limit = 12

    for event in events:
        event.pop("_sort_at", None)

    return {
        "events": events[:display_limit],
        "skills_tracked": len({item["skill_id"] for item in events}),
        "events_total": len(events),
        "comparable_events": sum(bool(item.get("comparison")) for item in events),
        "limited_sample_events": sum(item["total_items"] < 2 for item in events),
        "evidence_note": (
            "The timeline links explicitly mapped diagnostic tags with verified "
            "question-level practice and Coach records. Each comparison requires "
            "at least two answers in both events. Question sets and difficulty can "
            "differ, so a change is descriptive and does not prove that an "
            "intervention caused learning gain or durable mastery."
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
