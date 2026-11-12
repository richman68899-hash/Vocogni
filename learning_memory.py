"""Transparent, privacy-minimizing learner skill memory for Vocogni."""
from __future__ import annotations

from datetime import datetime, timezone
import re


SCHEMA_VERSION = 1
RECENT_WINDOW = 8


def _now():
    return datetime.now(timezone.utc).isoformat()


def _safe_int(value, default=0):
    """Read an integer from legacy JSON without allowing malformed values to crash."""
    if isinstance(value, bool):
        return default
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _safe_percent(value):
    return min(100, _safe_int(value, default=0))


def _safe_list(value):
    return value if isinstance(value, list) else []


def _safe_ids(value):
    """Return hashable, non-empty IDs from a possibly malformed saved list."""
    return [
        str(item).strip()
        for item in _safe_list(value)
        if isinstance(item, (str, int)) and not isinstance(item, bool)
        and str(item).strip()
    ]


def _slug(value):
    text = str(value or "").strip().casefold()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "unclassified_skill"


def skill_identity(question):
    """Use existing course-authored skill tags; fall back to existing mistake tags."""
    label = question.get("skill_tag") or question.get("skill") or question.get("mistake_tag") or "Unclassified skill"
    label = str(label).strip() or "Unclassified skill"
    return _slug(question.get("skill_id") or label), label


def record_attempt(progress, course_id, lesson_id, lesson_title, question,
                   is_correct, marking_result=None, source="practice"):
    """Persist aggregate score/criterion evidence without storing raw answers."""
    if not isinstance(progress, dict):
        raise TypeError("Learner progress must be a dictionary.")
    question = question if isinstance(question, dict) else {}
    marking_result = marking_result if isinstance(marking_result, dict) else {}

    course_progress = progress.setdefault(course_id, {})
    if not isinstance(course_progress, dict):
        course_progress = {}
        progress[course_id] = course_progress
    memory = course_progress.get("learning_memory")
    if not isinstance(memory, dict):
        memory = {"schema_version": SCHEMA_VERSION, "skills": {}, "attempts_recorded": 0}
        course_progress["learning_memory"] = memory
    memory.setdefault("schema_version", SCHEMA_VERSION)
    skills = memory.get("skills")
    if not isinstance(skills, dict):
        skills = {}
        memory["skills"] = skills

    key, label = skill_identity(question)
    question_id = str(question.get("id") or "unknown_question")
    skill = skills.get(key)
    if not isinstance(skill, dict):
        skill = {
            "skill_key": key, "label": label, "attempts": 0,
            "marks_awarded": 0, "max_marks": 0, "recent_scores": [],
            "criterion_history": {}, "evidence": [],
        }
        skills[key] = skill
    skill["label"] = label

    fallback_maximum = _safe_int(question.get("max_marks", 1), default=1)
    maximum = max(1, _safe_int(marking_result.get("max_marks", fallback_maximum), default=fallback_maximum))
    fallback_score = int(bool(is_correct))
    awarded = min(max(0, _safe_int(marking_result.get("score", fallback_score), default=fallback_score)), maximum)
    percent = round(100 * awarded / maximum)
    skill["attempts"] = _safe_int(skill.get("attempts", 0)) + 1
    skill["marks_awarded"] = _safe_int(skill.get("marks_awarded", 0)) + awarded
    skill["max_marks"] = _safe_int(skill.get("max_marks", 0)) + maximum
    recent_scores = [_safe_percent(value) for value in _safe_list(skill.get("recent_scores"))]
    skill["recent_scores"] = (recent_scores + [percent])[-RECENT_WINDOW:]

    missed = []
    history = skill.get("criterion_history")
    if not isinstance(history, dict):
        history = {}
        skill["criterion_history"] = history
    for index, point in enumerate(_safe_list(marking_result.get("marking_points")), start=1):
        if not isinstance(point, dict):
            continue
        point_id = str(point.get("id") or f"criterion_{index}")
        criterion_label = str(point.get("criteria") or point_id)
        criterion = history.get(point_id)
        if not isinstance(criterion, dict):
            criterion = {
                "label": criterion_label, "seen": 0, "misses": 0, "last_seen_at": None,
                "question_ids": [], "missed_question_ids": [],
            }
            history[point_id] = criterion
        criterion["label"] = criterion_label
        criterion["seen"] = _safe_int(criterion.get("seen", 0)) + 1
        question_ids = _safe_ids(criterion.get("question_ids"))
        if question_id not in question_ids:
            question_ids.append(question_id)
        criterion["question_ids"] = question_ids[-RECENT_WINDOW:]
        criterion["last_seen_at"] = _now()

        met = point.get("met")
        if not isinstance(met, bool):
            marks_awarded = _safe_int(point.get("marks_awarded", 0))
            marks_available = max(1, _safe_int(point.get("marks_available", 1), default=1))
            met = marks_awarded >= marks_available
        if not met:
            criterion["misses"] = _safe_int(criterion.get("misses", 0)) + 1
            missed_question_ids = _safe_ids(criterion.get("missed_question_ids"))
            if question_id not in missed_question_ids:
                missed_question_ids.append(question_id)
            criterion["missed_question_ids"] = missed_question_ids[-RECENT_WINDOW:]
            missed.append({"id": point_id, "label": criterion_label})

    seen_at = _now()
    evidence = [item for item in _safe_list(skill.get("evidence")) if isinstance(item, dict)]
    evidence.append({
        "lesson_id": str(lesson_id),
        "lesson_title": str(lesson_title or lesson_id),
        "question_id": question_id,
        "source": str(source),
        "score_percent": percent,
        "marks_awarded": awarded,
        "max_marks": maximum,
        "full_credit": awarded == maximum,
        "missed_criteria": missed,
        "seen_at": seen_at,
    })
    skill["evidence"] = evidence[-RECENT_WINDOW:]
    skill["last_seen_at"] = seen_at
    skill["last_lesson_id"] = str(lesson_id)
    skill["last_lesson_title"] = str(lesson_title or lesson_id)
    memory["attempts_recorded"] = _safe_int(memory.get("attempts_recorded", 0)) + 1
    return {"skill_key": key, "skill_label": label, "score_percent": percent, "missed_criteria": missed}


def _profile_skill(skill):
    """Build a learner-facing summary from valid portions of a saved skill record."""
    skill = skill if isinstance(skill, dict) else {}
    attempts = _safe_int(skill.get("attempts", 0))
    maximum = _safe_int(skill.get("max_marks", 0))
    marks = _safe_int(skill.get("marks_awarded", 0))
    average = min(100, round(100 * marks / maximum)) if maximum else 0
    recent = [_safe_percent(value) for value in _safe_list(skill.get("recent_scores"))]

    history = skill.get("criterion_history")
    if not isinstance(history, dict):
        history = {}
    criteria = []
    for cid, value in history.items():
        if not isinstance(value, dict):
            continue
        criteria.append({
            "id": str(cid),
            "label": str(value.get("label") or cid),
            "seen": _safe_int(value.get("seen", 0)),
            "misses": _safe_int(value.get("misses", 0)),
            "distinct_questions": len(set(_safe_ids(value.get("question_ids")))),
            "distinct_missed_questions": len(set(_safe_ids(value.get("missed_question_ids")))),
        })

    repeats = [
        item for item in criteria
        if item["distinct_missed_questions"] >= 2 and item["distinct_questions"] >= 2
    ]
    repeats.sort(key=lambda item: (-item["misses"], -item["seen"], item["label"].casefold()))
    if repeats:
        status = "Repeat snag"
    elif attempts >= 2 and average < 60:
        status = "Needs review"
    else:
        latest_practice_by_question = {}
        for evidence_index, item in enumerate(_safe_list(skill.get("evidence"))):
            if not isinstance(item, dict) or item.get("source") != "practice":
                continue
            question_id = str(item.get("question_id") or "")
            if question_id:
                latest_practice_by_question[question_id] = (
                    evidence_index,
                    _safe_percent(item.get("score_percent", 0)),
                )
        chronological_scores = [
            score
            for _, score in sorted(
                latest_practice_by_question.values(),
                key=lambda entry: entry[0],
            )
        ]
        recent_distinct_practice = chronological_scores[-3:]
        has_consistent_evidence = (
            len(recent_distinct_practice) == 3
            and all(value >= 80 for value in recent_distinct_practice)
        )
        if has_consistent_evidence:
            status = "Consistent evidence"
        elif attempts >= 2:
            status = "Developing"
        else:
            status = "Gathering evidence"

    trend = "not enough attempts"
    if len(recent) >= 2:
        change = recent[-1] - recent[-2]
        trend = "improving" if change >= 10 else ("slipping" if change <= -10 else "roughly steady")
    return {
        "skill_key": str(skill.get("skill_key") or ""),
        "label": str(skill.get("label") or "Unclassified skill"),
        "attempts": attempts, "marks_awarded": marks, "max_marks": maximum,
        "average_percent": average, "recent_scores": recent, "trend": trend,
        "status": status, "repeat_snags": repeats,
        "last_lesson_id": skill.get("last_lesson_id"),
        "last_lesson_title": skill.get("last_lesson_title"),
    }


def course_fingerprint(progress, course_id):
    """Derive a simple, inspectable learner profile from that course's saved evidence."""
    course_progress = progress.get(course_id, {}) if isinstance(progress, dict) else {}
    if not isinstance(course_progress, dict):
        course_progress = {}
    memory = course_progress.get("learning_memory", {})
    if not isinstance(memory, dict):
        memory = {}
    records = memory.get("skills", {})
    if not isinstance(records, dict):
        records = {}
    skills = [_profile_skill(item) for item in records.values() if isinstance(item, dict)]
    skills.sort(key=lambda item: (
        0 if item["repeat_snags"] else (1 if item["status"] == "Needs review" else 2),
        item["average_percent"], -item["attempts"], item["label"].casefold(),
    ))
    repeat_snags = []
    for skill in skills:
        for criterion in skill["repeat_snags"]:
            repeat_snags.append({**criterion, "skill_key": skill["skill_key"], "skill_label": skill["label"]})
    repeat_snags.sort(key=lambda item: (-item["misses"], item["skill_label"].casefold()))
    return {
        "skills": skills,
        "attempts_recorded": _safe_int(memory.get("attempts_recorded", 0)),
        "skill_count": len(skills),
        "review_count": sum(item["status"] in ("Repeat snag", "Needs review") for item in skills),
        "reliable_count": sum(item["status"] == "Consistent evidence" for item in skills),
        "repeat_snags": repeat_snags,
        "priority_skill": skills[0] if skills and skills[0]["status"] in ("Repeat snag", "Needs review") else None,
    }


def repair_suggestion(skill_label, criterion_label=""):
    """Short, deterministic next-step cues for common authored math/chemistry skills."""
    text = f"{skill_label} {criterion_label}".casefold()
    if any(term in text for term in ("completing the square", "perfect square", "vertex form")):
        return "Factor out a first when needed. Then halve the x-coefficient inside the bracket, square it, and balance the change outside."
    if any(term in text for term in ("endpoint", "inequal", "sign chart", "interval")):
        return "Find and mark the roots first. Test one value in each interval; include roots only for ≥ or ≤."
    if any(term in text for term in ("intersection", "simultaneous", "ordered pair", "substitute")):
        return "Equate the y-expressions, solve for x, substitute to find y, and check the point in both equations."
    if any(term in text for term in ("discriminant", "real root", "number of roots")):
        return "Calculate D = b² − 4ac first: positive means two real roots, zero one repeated root, negative none."
    if any(term in text for term in ("symmetr", "axis", "vertex")):
        return "Read vertex (h, k) from a(x − h)² + k. The vertical axis is x = h; verify with −b/(2a)."
    if any(term in text for term in ("integral", "area", "upper", "lower", "bound")):
        return "Write the bounds and identify the upper curve. Integrate upper − lower, then evaluate F(upper) − F(lower)."
    if any(term in text for term in ("factor", "root", "intercept")):
        return "Set the expression equal to zero and factor. Check each root by substitution; keep roots separate from the vertex."
    return "Review the worked example, then solve a fresh question with different values and explain each key step."


def feedback_nudge(progress, course_id, question, marking_result=None):
    """Show a repair cue only if a rubric miss repeats and appears again now."""
    question = question if isinstance(question, dict) else {}
    key, label = skill_identity(question)
    profile = course_fingerprint(progress, course_id)
    skill = next((item for item in profile["skills"] if item["skill_key"] == key), None)
    if not skill or not skill["repeat_snags"]:
        return None
    repeats = skill["repeat_snags"]
    if marking_result is not None:
        if not isinstance(marking_result, dict):
            return None
        currently_missed = set()
        for item in _safe_list(marking_result.get("marking_points")):
            if not isinstance(item, dict):
                continue
            met = item.get("met")
            if isinstance(met, bool):
                is_missed = not met
            else:
                marks_awarded = _safe_int(item.get("marks_awarded", 0))
                marks_available = max(1, _safe_int(item.get("marks_available", 1), default=1))
                is_missed = marks_awarded < marks_available
            if is_missed:
                currently_missed.add(str(item.get("id")))
        repeats = [item for item in repeats if item["id"] in currently_missed]
        if not repeats:
            return None
    criterion = repeats[0]
    return {
        "skill_label": label, "criterion": criterion["label"],
        "misses": criterion["misses"], "seen": criterion["seen"],
        "repair": repair_suggestion(label, criterion["label"]),
    }


__all__ = ["record_attempt", "skill_identity", "course_fingerprint",
           "repair_suggestion", "feedback_nudge"]
