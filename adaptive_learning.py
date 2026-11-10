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
            "diagnostic_ratios": [],
            "diagnostic_mistake_tags": defaultdict(int),
            "diagnostic_locations": set(),
            "diagnostic_question_ids": set(),
            "locations": set(),
        }

    # The question registry is the source of truth for stable question-to-skill
    # mapping. Unverified/legacy questions are not assigned invented skill IDs.
    question_map = {}
    for record in question_engine.iter_question_records():
        # Only the reviewed registry is authoritative for practice evidence.
        # Legacy, generated, and needs-review questions must not create skill
        # accuracy or trajectory signals.
        if record.get("verification_status") != "verified":
            continue
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
                    # Fail closed: a saved result is evidence only when
                    # both the attempt and the current registry identify it as
                    # verified. A client-supplied skill_id alone is not proof.
                    if result.get("verification_status") != "verified":
                        continue
                    qid = str(result.get("question_id") or "")
                    metadata = question_map.get((course_id, lesson_id, qid))
                    if not metadata:
                        continue
                    skill_id = metadata.get("skill_id")
                    recorded_skill_id = result.get("skill_id")
                    if recorded_skill_id and recorded_skill_id != skill_id:
                        continue
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

    # Baseline diagnostics can identify likely skill gaps before practice.
    # Keep diagnostic and practice evidence separate; never blend denominators.
    for course_id, course_progress in (progress or {}).items():
        if not isinstance(course_progress, dict):
            continue
        diagnostics = course_progress.get("diagnostics", {})
        if not isinstance(diagnostics, dict):
            continue
        for lesson_id, diagnostic in diagnostics.items():
            if not isinstance(diagnostic, dict):
                continue
            review = diagnostic.get("answer_review", [])
            if not isinstance(review, list):
                continue
            for result_index, result in enumerate(review):
                if not isinstance(result, dict):
                    continue
                tag = _normalise_label(result.get("skill_tag"))
                skill_id = _DIAGNOSTIC_SKILL_TAG_MAP.get((str(course_id), tag))
                if skill_id not in evidence:
                    continue
                item = evidence[skill_id]
                question_id = str(result.get("question_id") or "")
                stable_question_id = question_id or f"legacy-item-{result_index}"
                evidence_id = (
                    str(course_id), str(lesson_id), stable_question_id
                )
                if evidence_id in item["diagnostic_question_ids"]:
                    continue
                item["diagnostic_question_ids"].add(evidence_id)
                item["diagnostic_ratios"].append(_event_ratio(result))
                item["diagnostic_locations"].add((str(course_id), str(lesson_id)))
                if not result.get("correct") and result.get("skill_tag"):
                    item["diagnostic_mistake_tags"][str(result["skill_tag"])] += 1

    for item in evidence.values():
        item["accuracy"] = (
            sum(item["ratios"]) / len(item["ratios"]) if item["ratios"] else None
        )
        item["diagnostic_accuracy"] = (
            sum(item["diagnostic_ratios"]) / len(item["diagnostic_ratios"])
            if item["diagnostic_ratios"] else None
        )
        item["recent_ratios"].sort(key=lambda pair: pair[0])
        item["recent_accuracy"] = (
            sum(ratio for _, ratio in item["recent_ratios"][-3:]) /
            len(item["recent_ratios"][-3:]) if item["recent_ratios"] else None
        )
        item["repeat_errors"] = sum(item["mistake_tags"].values())
        item["diagnostic_repeat_errors"] = sum(item["diagnostic_mistake_tags"].values())
        item["diagnostic_mistake_tags"] = dict(item["diagnostic_mistake_tags"])
        item["diagnostic_locations"] = sorted(item["diagnostic_locations"])
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
    practice attempts, verified independent transfer checks, and verified Coach
    answers. Transfer checks are kept as a distinct event type and never blended
    into ordinary practice accuracy. Unverified/generated items are excluded.
    Comparisons are shown only when both events contain at least two answers;
    they remain descriptive because the question sets may differ.
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
                for result_index, result in enumerate(review):
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

        # 3) Independent transfer checks are stored outside practice_attempts.
        # Re-resolve each item against the current VQE registry so stale, legacy,
        # or reclassified records cannot become transfer evidence.
        transfer_records = course_progress.get("transfer_checks", [])
        if isinstance(transfer_records, list):
            for transfer_index, result in enumerate(transfer_records):
                if not isinstance(result, dict):
                    continue
                if (
                    result.get("evidence_type") != "independent_transfer"
                    or result.get("independent") is not True
                ):
                    continue
                question_id = str(result.get("question_id") or "")
                source_lesson_id = str(result.get("lesson_id") or result.get("source_lesson_id") or "")
                practice_lesson_id = str(result.get("practice_lesson_id") or "")
                completed = _parse_event_timestamp(
                    result.get("recorded_at") or result.get("completed_at")
                )
                if not question_id or not source_lesson_id or not practice_lesson_id or completed is None:
                    continue
                metadata = question_engine.attempt_metadata(
                    question_id,
                    course_id=course_id,
                    lesson_id=source_lesson_id,
                )
                skill_id = metadata.get("skill_id")
                if (
                    metadata.get("verification_status") != "verified"
                    or metadata.get("question_purpose") != "application"
                    or not isinstance(skill_id, str)
                    or skill_id not in math_taxonomy.SKILLS
                    or result.get("verification_status") != "verified"
                    or result.get("source_skill_id") != skill_id
                    or (result.get("skill_id") and result.get("skill_id") != skill_id)
                ):
                    continue
                practice_title = _course_lesson_labels(course_id, practice_lesson_id)[1]
                source_title = _course_lesson_labels(course_id, source_lesson_id)[1]
                ratio = _event_ratio(result)
                events.append({
                    "event_id": (
                        f"transfer:{course_id}:{practice_lesson_id}:"
                        f"{result.get('attempt_number', transfer_index + 1)}:"
                        f"{question_id}:{completed.isoformat()}"
                    ),
                    "course_id": course_id,
                    "course_title": course_title,
                    "lesson_id": practice_lesson_id,
                    "lesson_title": practice_title,
                    "source_lesson_id": source_lesson_id,
                    "source_lesson_title": source_title,
                    "skill_id": skill_id,
                    "skill": math_taxonomy.SKILLS[skill_id]["label"],
                    "event_type": "transfer",
                    "intervention_label": "Independent transfer check",
                    "completed_at": completed.isoformat(),
                    "_sort_at": completed,
                    "correct_answers": 1 if ratio >= 0.999 else 0,
                    "total_items": 1,
                    "accuracy_percent": round(ratio * 100),
                })

        # 4) Coach answers are stored individually. Group verified Coach

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
            "practice, independent transfer, and Coach records. Transfer checks "
            "remain separate from practice accuracy. Each comparison requires "
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
    """Return ranked skill actions with explicit evidence-aware prerequisite routing."""
    evidence = _collect_skill_evidence(progress)
    ranked = []
    for skill_id, item in evidence.items():
        source = "practice" if item["accuracy"] is not None else "diagnostic"
        accuracy = item["accuracy"] if source == "practice" else item["diagnostic_accuracy"]
        if accuracy is None:
            continue
        scoring = dict(item)
        scoring["accuracy"] = accuracy
        scoring["attempts"] = (
            item["attempts"] if source == "practice"
            else len(item["diagnostic_question_ids"])
        )
        scoring["repeat_errors"] = item["repeat_errors"] if source == "practice" else item["diagnostic_repeat_errors"]
        scoring["mistake_tags"] = item["mistake_tags"] if source == "practice" else item["diagnostic_mistake_tags"]
        scoring["recent_accuracy"] = item["recent_accuracy"] if source == "practice" else None
        priority = _weakness_priority(scoring)
        if priority > 0:
            ranked.append((priority, skill_id, scoring, source))

    ranked.sort(key=lambda row: (-row[0], row[2]["accuracy"], row[2]["skill"]))
    actions = []
    routed_skills = set()
    for priority, skill_id, item, evidence_source in ranked:
        prerequisites = []
        for prerequisite in math_taxonomy.SKILLS[skill_id].get("prerequisites", []):
            if prerequisite not in evidence:
                continue
            prerequisite_item = evidence[prerequisite]
            prerequisite_source = (
                "practice" if prerequisite_item["accuracy"] is not None
                else "diagnostic" if prerequisite_item["diagnostic_accuracy"] is not None
                else "none"
            )
            prerequisite_accuracy = (
                prerequisite_item["accuracy"] if prerequisite_source == "practice"
                else prerequisite_item["diagnostic_accuracy"] if prerequisite_source == "diagnostic"
                else None
            )
            if prerequisite_accuracy is None:
                prerequisites.append((prerequisite, "untested"))
            elif prerequisite_accuracy < 0.75:
                prerequisites.append((prerequisite, "below_threshold"))

        # Prefer a demonstrated prerequisite gap over an untested prerequisite.
        # Missing evidence is a reason to check, not evidence of failure.
        weak_prerequisites = [entry for entry in prerequisites if entry[1] == "below_threshold"]
        target_skill, prerequisite_status = (
            weak_prerequisites[0] if weak_prerequisites
            else prerequisites[0] if prerequisites
            else (skill_id, None)
        )
        if target_skill in routed_skills:
            continue

        target = evidence[target_skill]
        target_source = (
            "practice" if target["accuracy"] is not None
            else "diagnostic" if target["diagnostic_accuracy"] is not None
            else "none"
        )
        target_accuracy = (
            target["accuracy"] if target_source == "practice"
            else target["diagnostic_accuracy"] if target_source == "diagnostic"
            else None
        )
        target_attempts = (
            target["attempts"] if target_source == "practice"
            else len(target["diagnostic_question_ids"])
            if target_source == "diagnostic" else 0
        )
        target_repeat_errors = target["repeat_errors"] if target_source == "practice" else target["diagnostic_repeat_errors"] if target_source == "diagnostic" else 0
        target_mistake_tags = target["mistake_tags"] if target_source == "practice" else target["diagnostic_mistake_tags"] if target_source == "diagnostic" else {}
        course_id, lesson_id = _lesson_for_skill(target_skill, target)
        if not course_id or not lesson_id:
            locations = target.get("diagnostic_locations", [])
            if locations:
                course_id, lesson_id = locations[0]
        if not course_id or not lesson_id:
            continue
        course = data.get_course(course_id)
        lesson, _ = data.get_lesson(course_id, lesson_id)
        if not course or not lesson:
            continue

        is_prerequisite = target_skill != skill_id
        is_prerequisite_review = is_prerequisite and prerequisite_status == "below_threshold"
        is_prerequisite_check = is_prerequisite and prerequisite_status == "untested"
        if is_prerequisite_review:
            threshold_source = (
                "practice evidence" if target_source == "practice"
                else "baseline diagnostic evidence"
            )
            reason = (
                f"{item['skill']} depends on {target['skill']}, which is below "
                f"the 75% review threshold based on {threshold_source}."
            )
            action = f"Review {target['skill']} before returning to {item['skill']}."
        elif is_prerequisite_check:
            reason = (
                f"{item['skill']} depends on {target['skill']}, but there is no "
                "recorded diagnostic or practice evidence for that prerequisite yet."
            )
            action = f"Complete a short check of {target['skill']} before continuing with {item['skill']}."
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
        # A single selected-response diagnostic item is a hypothesis to check,
        # not enough evidence to prescribe a persistent weakness intervention.
        confirmation_required = (
            target_source == "diagnostic" and target_attempts < 2
        )
        if confirmation_required:
            reason = (
                f"One distinct baseline diagnostic item suggests {target['skill']} "
                f"may need attention ({round(target_accuracy * 100)}% on that item). "
                "This is a preliminary signal, not a confirmed skill gap; "
                "it is based on baseline diagnostic evidence."
            )
            action = (
                f"Check {target['skill']} with another distinct question before "
                "treating it as a persistent weakness."
            )

        actions.append({
            "evidence_source": target_source,
            "evidence_strength": (
                "single_diagnostic_item" if confirmation_required
                else "multiple_diagnostic_items" if target_source == "diagnostic"
                else "practice_observed"
            ),
            "confirmation_required": confirmation_required,
            "diagnostic_items": (
                len(target["diagnostic_question_ids"])
                if target_source == "diagnostic" else 0
            ),
            "skill_id": target_skill,
            "skill": target["skill"],
            "source_skill_id": skill_id,
            "course_id": course_id,
            "course_title": course["title"],
            "lesson_id": lesson_id,
            "lesson_title": lesson["title"],
            "priority": priority,
            "accuracy_percent": round(target_accuracy * 100) if target_accuracy is not None else None,
            "attempts": target_attempts,
            "repeat_errors": target_repeat_errors,
            "common_error": max(target_mistake_tags, key=target_mistake_tags.get) if target_mistake_tags else None,
            "reason": reason,
            "action": action,
            "is_prerequisite_review": is_prerequisite_review,
            "is_prerequisite_check": is_prerequisite_check,
        })
        routed_skills.add(target_skill)
        if len(actions) >= max(1, int(limit)):
            break

    # Include transparent status counts so the UI can explain when evidence is
    # too sparse to make a confident personalised recommendation.
    tested = sum(item["accuracy"] is not None for item in evidence.values())
    diagnostically_tested = sum(item["diagnostic_accuracy"] is not None for item in evidence.values())
    return {
        "engine_version": ENGINE_VERSION,
        "actions": actions,
        "skills_tracked": len(evidence),
        "skills_with_practice_evidence": tested,
        "skills_with_diagnostic_evidence": diagnostically_tested,
        "evidence_note": (
            "Practice recommendations use saved question-level results. When "
            "practice is absent, mapped baseline diagnostic answers can suggest "
            "a provisional review target. A single diagnostic item is always "
            "marked for confirmation with a distinct question before it is "
            "treated as a persistent gap. An untested prerequisite triggers a "
            "check, not a weakness label. Diagnostic and practice scores stay "
            "separate; repeated prerequisite targets are deduplicated. These "
            "heuristics are not a validated diagnosis or proof of mastery."
        ),
    }
