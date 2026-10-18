"""Transparent, privacy-minimizing learner skill memory for Vocogni."""
from __future__ import annotations

from datetime import datetime, timezone
import re


SCHEMA_VERSION = 1
RECENT_WINDOW = 8


def _now():
    return datetime.now(timezone.utc).isoformat()


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
    """Persist aggregate score/criterion evidence. Raw answer text is never accepted or stored."""
    course_progress = progress.setdefault(course_id, {})
    if not isinstance(course_progress, dict):
        course_progress = {}
        progress[course_id] = course_progress
    memory = course_progress.setdefault(
        "learning_memory",
        {"schema_version": SCHEMA_VERSION, "skills": {}, "attempts_recorded": 0},
    )
    if not isinstance(memory, dict):
        memory = {"schema_version": SCHEMA_VERSION, "skills": {}, "attempts_recorded": 0}
        course_progress["learning_memory"] = memory
    memory.setdefault("schema_version", SCHEMA_VERSION)
    memory.setdefault("attempts_recorded", 0)
    if not isinstance(memory.get("skills"), dict):
        memory["skills"] = {}

    key, label = skill_identity(question)
    skill = memory["skills"].setdefault(key, {
        "skill_key": key, "label": label, "attempts": 0,
        "marks_awarded": 0, "max_marks": 0, "recent_scores": [],
        "criterion_history": {}, "evidence": [],
    })
    skill["label"] = label
    maximum = max(1, int((marking_result or {}).get("max_marks", question.get("max_marks", 1)) or 1))
    awarded = int((marking_result or {}).get("score", int(bool(is_correct))) or 0)
    awarded = min(max(0, awarded), maximum)
    percent = round(100 * awarded / maximum)
    skill["attempts"] = int(skill.get("attempts", 0)) + 1
    skill["marks_awarded"] = int(skill.get("marks_awarded", 0)) + awarded
    skill["max_marks"] = int(skill.get("max_marks", 0)) + maximum
    skill["recent_scores"] = (list(skill.get("recent_scores", [])) + [percent])[-RECENT_WINDOW:]

    missed = []
    if marking_result:
        history = skill.setdefault("criterion_history", {})
        for index, point in enumerate(marking_result.get("marking_points", []), start=1):
            if not isinstance(point, dict):
                continue
            point_id = str(point.get("id") or f"criterion_{index}")
            criterion_label = str(point.get("criteria") or point_id)
            criterion = history.setdefault(point_id, {
                "label": criterion_label, "seen": 0, "misses": 0, "last_seen_at": None,
            })
            criterion["label"] = criterion_label
            criterion["seen"] = int(criterion.get("seen", 0)) + 1
            criterion["last_seen_at"] = _now()
            met = point.get("met")
            if met is None:
                met = int(point.get("marks_awarded", 0)) >= int(point.get("marks_available", 1))
            if not bool(met):
                criterion["misses"] = int(criterion.get("misses", 0)) + 1
                missed.append({"id": point_id, "label": criterion_label})

    seen_at = _now()
    evidence = list(skill.get("evidence", []))
    evidence.append({
        "lesson_id": str(lesson_id),
        "lesson_title": str(lesson_title or lesson_id),
        "question_id": str(question.get("id") or "unknown_question"),
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
    memory["attempts_recorded"] = int(memory.get("attempts_recorded", 0)) + 1
    return {"skill_key": key, "skill_label": label, "score_percent": percent, "missed_criteria": missed}


def _profile_skill(skill):
    attempts = int(skill.get("attempts", 0))
    maximum = int(skill.get("max_marks", 0))
    marks = int(skill.get("marks_awarded", 0))
    average = round(100 * marks / maximum) if maximum else 0
    recent = [int(value) for value in skill.get("recent_scores", [])]
    criteria = [
        {"id": cid, "label": value.get("label", cid),
         "seen": int(value.get("seen", 0)), "misses": int(value.get("misses", 0))}
        for cid, value in skill.get("criterion_history", {}).items()
        if isinstance(value, dict)
    ]
    repeats = [item for item in criteria if item["misses"] >= 2 and item["seen"] >= 2]
    repeats.sort(key=lambda item: (-item["misses"], -item["seen"], item["label"].casefold()))
    if repeats:
        status = "Repeat snag"
    elif attempts >= 2 and average < 60:
        status = "Needs review"
    elif attempts >= 3 and len(recent) >= 3 and all(value >= 80 for value in recent[-3:]):
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
        "skill_key": skill.get("skill_key", ""),
        "label": skill.get("label", "Unclassified skill"),
        "attempts": attempts, "marks_awarded": marks, "max_marks": maximum,
        "average_percent": average, "recent_scores": recent, "trend": trend,
        "status": status, "repeat_snags": repeats,
        "last_lesson_id": skill.get("last_lesson_id"),
        "last_lesson_title": skill.get("last_lesson_title"),
    }


def course_fingerprint(progress, course_id):
    """Derive a simple, inspectable learner profile from that course's saved evidence."""
    course_progress = progress.get(course_id, {}) if isinstance(progress, dict) else {}
    memory = course_progress.get("learning_memory", {}) if isinstance(course_progress, dict) else {}
    records = memory.get("skills", {}) if isinstance(memory, dict) else {}
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
        "attempts_recorded": int(memory.get("attempts_recorded", 0)) if isinstance(memory, dict) else 0,
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
    """Show a repair cue only if a rubric miss repeats for this skill and appears again now."""
    key, label = skill_identity(question)
    profile = course_fingerprint(progress, course_id)
    skill = next((item for item in profile["skills"] if item["skill_key"] == key), None)
    if not skill or not skill["repeat_snags"]:
        return None
    repeats = skill["repeat_snags"]
    if marking_result is not None:
        currently_missed = {
            str(item.get("id")) for item in marking_result.get("marking_points", [])
            if isinstance(item, dict) and not bool(item.get("met"))
        }
        repeats = [item for item in repeats if item["id"] in currently_missed]
        if not repeats:
            return None
    criterion = repeats[0]
    return {
        "skill_label": label, "criterion": criterion["label"],
        "misses": criterion["misses"], "seen": criterion["seen"],
        "repair": repair_suggestion(label, criterion["label"]),
    }


def render_course_fingerprint(st, progress, course_id):
    """Render a learner-facing summary inside Vocogni's existing Progress screen."""
    from html import escape

    profile = course_fingerprint(progress, course_id)
    st.markdown("<h3>Learning Fingerprint</h3>", unsafe_allow_html=True)
    st.caption(
        "Built from saved attempts and marking-point evidence. A repeat snag needs "
        "at least two misses; consistent evidence needs three recent high-scoring attempts. "
        "These are practice signals, not permanent ability labels."
    )
    if not profile["skills"]:
        st.info("Your fingerprint builds automatically as you complete diagnostics and practice.")
        return

    columns = st.columns(3)
    columns[0].metric("Skills with evidence", profile["skill_count"])
    columns[1].metric("Priority reviews", profile["review_count"])
    columns[2].metric("Consistent evidence", profile["reliable_count"])

    if profile["repeat_snags"]:
        snag = profile["repeat_snags"][0]
        st.markdown(
            "<div class='vc-card vc-card--current'><strong>Best next repair</strong><br>"
            f"<strong>{escape(snag['skill_label'])}</strong>: {escape(snag['label'])}<br>"
            f"<span class='vc-muted'>Missed {snag['misses']} times across {snag['seen']} attempts.</span>"
            "</div>", unsafe_allow_html=True,
        )
        st.write(repair_suggestion(snag["skill_label"], snag["label"]))
    elif profile["priority_skill"]:
        skill = profile["priority_skill"]
        st.markdown(
            f"**Suggested review:** {escape(skill['label'])} — "
            f"{skill['average_percent']}% of marks across {skill['attempts']} attempts."
        )
        st.write(repair_suggestion(skill["label"]))
    else:
        st.success("No repeated rubric snag is currently flagged. Keep testing skills on fresh questions.")

    with st.expander("Inspect skill evidence", expanded=False):
        for skill in profile["skills"]:
            st.markdown(
                f"**{escape(skill['label'])}** — {escape(skill['status'])} "
                f"({skill['average_percent']}% of marks; {skill['attempts']} attempts)"
            )
            st.progress(skill["average_percent"])
            st.caption(f"Recent signal: {skill['trend']}. Last practiced: {escape(skill['last_lesson_title'] or 'Not recorded')}.")
            for criterion in skill["repeat_snags"]:
                st.warning(
                    f"Recurring criterion: {criterion['label']} "
                    f"({criterion['misses']} misses in {criterion['seen']} attempts)."
                )


__all__ = ["record_attempt", "skill_identity", "course_fingerprint",
           "repair_suggestion", "feedback_nudge", "render_course_fingerprint"]
