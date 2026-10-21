"""
logic.py — Progress engine for Vocogni Version 1.

Deliberately framework-free: every function here takes plain data
(profile / progress dicts) as arguments and returns plain data. Nothing in
this file imports streamlit or touches st.session_state directly.

Why: this is exactly the boundary described in spec section 22
("organize the code so [a real database, LLM API, adaptive recommendation
system] can later be added without completely rewriting the application").
Because these functions don't know where `progress` came from, they will
work unchanged whether `progress` is loaded from st.session_state (today)
or fetched from a real database per logged-in user (later).
"""

import base64
import io
import math
import struct
from datetime import datetime, timezone
import wave

import data

APPLICATION_TAG = data.APPLICATION_MISTAKE_TAG


# ---------------------------------------------------------------------------
# Answer checking
# ---------------------------------------------------------------------------

def check_answer(question, user_answer):
    """Return True only for a fully correct answer in the question's schema."""
    question_type = question.get("type")
    if question_type == "mc":
        return user_answer == question.get("answer")

    if question_type == "open_ended":
        # Lazy imports keep the progress engine independent of the UI framework.
        if question.get("grader") == "math":
            import math_grading
            grader = math_grading
        else:
            import chemistry_grading
            grader = chemistry_grading
        result = grader.evaluate_open_response(question, user_answer)
        return bool(result["full_credit"])

    if question_type != "numeric":
        return False

    try:
        user_val = float(user_answer)
        expected = float(question["answer"])
    except (TypeError, ValueError, KeyError):
        return False
    tolerance = question.get("tolerance", 0.01)
    return abs(user_val - expected) <= tolerance


# ---------------------------------------------------------------------------
# Recording activity
# ---------------------------------------------------------------------------

def blank_course_progress():
    return {
        "started": False,
        "completed_lessons": [],
        "questions_attempted": 0,
        "correct_answers": 0,
        "mistakes": {},
        "diagnostics": {},
        "lesson_assessments": {},
        "practice_attempts": {},
        "lesson_screen_progress": {},
    }


def record_answer(progress, course_id, question, is_correct):
    """Mutate `progress` in place to record one answered question."""
    prog = progress.setdefault(course_id, blank_course_progress())
    prog["started"] = True
    prog["questions_attempted"] += 1
    if is_correct:
        prog["correct_answers"] += 1
    else:
        tag = question.get("mistake_tag", "Other")
        prog["mistakes"][tag] = prog["mistakes"].get(tag, 0) + 1


def mark_lesson_complete(progress, course_id, lesson_id):
    """Mutate `progress` in place to mark a lesson finished."""
    prog = progress.setdefault(course_id, blank_course_progress())
    if lesson_id not in prog["completed_lessons"]:
        prog["completed_lessons"].append(lesson_id)
    prog["started"] = True



# ---------------------------------------------------------------------------
# Course-agnostic Mastery Receipt
# ---------------------------------------------------------------------------
# This feature intentionally reads the published course schema instead of
# maintaining a list of course IDs or lesson IDs. Any registered course whose
# questions follow the normal lesson/question shapes is covered automatically.
#
# "Promising evidence" is deliberately not called mastery: performance on a
# small set of practice questions is not proof of durable or transferable
# learning. Delayed-retention testing is not yet part of the product.

_MASTERY_STATUSES = ("Needs review", "Developing", "Promising evidence", "Not tested")
_MASTERY_GENERIC_TAGS = {
    "other",
    "application / transfer error",
}


def _mastery_normalize(value):
    """Normalize labels for matching without changing the learner-facing label."""
    if not isinstance(value, str):
        return ""
    return " ".join(value.strip().split()).casefold()


def _mastery_question_entries(lesson):
    """Collect questions from supported lesson/diagnostic shapes, de-duplicated by ID."""
    rows = []
    for field in ("practice_questions", "questions"):
        value = lesson.get(field, [])
        if isinstance(value, list):
            rows.extend(item for item in value if isinstance(item, dict))

    interactive = lesson.get("interactive_question")
    if isinstance(interactive, dict):
        rows.append(interactive)

    diagnostic = lesson.get("diagnostic", {})
    if isinstance(diagnostic, dict):
        questions = diagnostic.get("questions", [])
        if isinstance(questions, list):
            rows.extend(item for item in questions if isinstance(item, dict))
        pathways = diagnostic.get("pathways", {})
        if isinstance(pathways, dict):
            for pathway in pathways.values():
                if isinstance(pathway, dict):
                    pathway_questions = pathway.get("questions", [])
                    if isinstance(pathway_questions, list):
                        rows.extend(item for item in pathway_questions if isinstance(item, dict))

    # Stable IDs are important for proving performance across distinct items.
    # Keep the first copy where a question appears in multiple compatibility
    # fields (for example, both "questions" and "interactive_question").
    result = []
    seen_ids = set()
    for index, question in enumerate(rows):
        qid = question.get("id")
        if qid is not None and str(qid).strip():
            key = str(qid).strip()
            if key in seen_ids:
                continue
            seen_ids.add(key)
        result.append(question)
    return result


def _mastery_question_skill(question, lesson):
    """Infer a human-readable skill from question metadata, with safe fallbacks."""
    for field in ("skill_tag", "skill", "mistake_tag"):
        candidate = question.get(field)
        normalized = _mastery_normalize(candidate)
        if normalized and normalized not in _MASTERY_GENERIC_TAGS:
            return " ".join(candidate.strip().split())

    skill_ids = lesson.get("skill_ids", [])
    if isinstance(skill_ids, list) and len(skill_ids) == 1:
        candidate = skill_ids[0]
        if isinstance(candidate, str) and candidate.strip():
            return " ".join(candidate.strip().split())

    return str(lesson.get("title") or "Untitled lesson").strip()


def _mastery_result_ratio(result):
    """Return an item's earned fraction, handling marked and binary schemas."""
    if not isinstance(result, dict):
        return 0.0
    for earned_field in ("score", "marks_awarded"):
        try:
            possible = float(result.get("max_marks"))
            earned = float(result.get(earned_field))
            if possible > 0:
                return min(1.0, max(0.0, earned / possible))
        except (TypeError, ValueError):
            continue
    return 1.0 if bool(result.get("correct")) else 0.0


def _mastery_percent(evidence):
    if not evidence:
        return None
    return round(sum(item["ratio"] for item in evidence) / len(evidence) * 100)


def mastery_receipt_for_course(progress, course_id):
    """Build a transparent, course-schema-driven learning-evidence receipt.

    The function has no course-specific branches. It discovers skills from
    each registered course's lessons/questions, then joins them to saved
    question-level practice attempts and diagnostic answer reviews.

    Status rules:
    - Needs review: practice performance is below 60%, the latest recorded
      item is below 60%, an unpractised diagnostic flagged a gap, or only a
      legacy aggregate mistake count is available.
    - Developing: practice evidence exists but the stronger threshold below
      has not been met.
    - Promising evidence: at least 3 distinct practice question IDs, at least
      80% average item performance, and at least 80% on the latest item.
    - Not tested: no practice evidence or unresolved diagnostic/legacy error.
    """
    course = data.get_course(course_id)
    if not course:
        return None

    course_progress = progress.get(course_id, {})
    if not isinstance(course_progress, dict):
        course_progress = {}

    # Ordered registry: insertion order follows the course author's content.
    skill_records = {}
    question_skill_by_lesson = {}
    mistake_tag_skill_candidates = {}

    def ensure_skill(label, lesson_title=None):
        safe_label = str(label or "Untitled skill").strip() or "Untitled skill"
        normalized = _mastery_normalize(safe_label) or "untitled skill"
        record = skill_records.get(normalized)
        if record is None:
            record = {
                "_key": normalized,
                "skill": safe_label,
                "_question_ids": set(),
                "_practice": [],
                "_diagnostic": [],
                "_lesson_titles": [],
                "legacy_error_count": 0,
            }
            skill_records[normalized] = record
        if lesson_title and lesson_title not in record["_lesson_titles"]:
            record["_lesson_titles"].append(lesson_title)
        return record

    # Construct the skill catalogue entirely from this course's authored data.
    lessons = course.get("lessons", [])
    if not isinstance(lessons, list):
        lessons = []
    for lesson in lessons:
        if not isinstance(lesson, dict):
            continue
        lesson_id = str(lesson.get("id") or "")
        lesson_title = str(lesson.get("title") or lesson_id or "Untitled lesson")
        question_map = question_skill_by_lesson.setdefault(lesson_id, {})
        questions = _mastery_question_entries(lesson)

        # A lesson with no question bank still appears as an untested skill.
        if not questions:
            ensure_skill(lesson_title, lesson_title)
            declared_skills = lesson.get("skill_ids", [])
            if isinstance(declared_skills, list):
                for declared in declared_skills:
                    if isinstance(declared, str) and declared.strip():
                        ensure_skill(declared, lesson_title)
            continue

        for question in questions:
            skill_label = _mastery_question_skill(question, lesson)
            skill = ensure_skill(skill_label, lesson_title)
            question_id = question.get("id")
            if question_id is not None and str(question_id).strip():
                question_id = str(question_id).strip()
                question_map[question_id] = skill["_key"]
                skill["_question_ids"].add(question_id)

            mistake_tag = question.get("mistake_tag")
            mistake_key = _mastery_normalize(mistake_tag)
            if mistake_key and mistake_key not in _MASTERY_GENERIC_TAGS:
                mistake_tag_skill_candidates.setdefault(mistake_key, set()).add(skill["_key"])

    # Diagnostic results are baseline evidence, not a substitute for practice.
    diagnostics = course_progress.get("diagnostics", {})
    if isinstance(diagnostics, dict):
        for lesson_id, diagnostic in diagnostics.items():
            if not isinstance(diagnostic, dict):
                continue
            answer_review = diagnostic.get("answer_review", [])
            if isinstance(answer_review, list) and answer_review:
                for item in answer_review:
                    if not isinstance(item, dict):
                        continue
                    question_id = item.get("question_id")
                    mapped_key = question_skill_by_lesson.get(str(lesson_id), {}).get(
                        str(question_id).strip() if question_id is not None else ""
                    )
                    if mapped_key:
                        skill = skill_records[mapped_key]
                    else:
                        lesson, _ = data.get_lesson(course_id, str(lesson_id))
                        lesson_title = lesson.get("title", str(lesson_id)) if lesson else str(lesson_id)
                        skill = ensure_skill(
                            item.get("skill_tag") or item.get("mistake_tag") or lesson_title,
                            lesson_title,
                        )
                    ratio = _mastery_result_ratio(item)
                    # Some diagnostic schemas only store "correct" for objective
                    # questions; for marked items, score/max_marks takes priority.
                    skill["_diagnostic"].append({
                        "ratio": ratio,
                        "question_id": str(question_id) if question_id is not None else None,
                        "completed_at": diagnostic.get("completed_at", ""),
                    })
            else:
                # Older diagnostic records may preserve only a weakness list.
                weaknesses = diagnostic.get("weaknesses", [])
                if isinstance(weaknesses, list):
                    lesson, _ = data.get_lesson(course_id, str(lesson_id))
                    lesson_title = lesson.get("title", str(lesson_id)) if lesson else str(lesson_id)
                    for weakness in weaknesses:
                        if isinstance(weakness, dict):
                            skill = ensure_skill(
                                weakness.get("skill_tag") or lesson_title,
                                lesson_title,
                            )
                            skill["_diagnostic"].append({
                                "ratio": 0.0,
                                "question_id": weakness.get("question_id"),
                                "completed_at": diagnostic.get("completed_at", ""),
                            })

    # Practice attempts keep per-question results. Resolve IDs against the
    # live lesson schema so skill names automatically follow newly added courses.
    practice_attempts = course_progress.get("practice_attempts", {})
    evidence_order = 0
    if isinstance(practice_attempts, dict):
        for lesson_id, attempts in practice_attempts.items():
            if not isinstance(attempts, list):
                continue
            lesson, _ = data.get_lesson(course_id, str(lesson_id))
            lesson_title = lesson.get("title", str(lesson_id)) if lesson else str(lesson_id)
            question_map = question_skill_by_lesson.get(str(lesson_id), {})
            for attempt in attempts:
                if not isinstance(attempt, dict):
                    continue
                results = attempt.get("results", [])
                if not isinstance(results, list):
                    continue
                for result in results:
                    if not isinstance(result, dict):
                        continue
                    evidence_order += 1
                    question_id = result.get("question_id")
                    normalized_qid = str(question_id).strip() if question_id is not None else ""
                    mapped_key = question_map.get(normalized_qid)
                    if mapped_key:
                        skill = skill_records[mapped_key]
                    else:
                        # Handles old question IDs and well-formed future course
                        # items whose schema carries a skill tag in the result.
                        skill = ensure_skill(
                            result.get("skill_tag") or result.get("mistake_tag") or lesson_title,
                            lesson_title,
                        )
                    ratio = _mastery_result_ratio(result)
                    skill["_practice"].append({
                        "ratio": ratio,
                        "correct": ratio >= 0.999,
                        "question_id": normalized_qid or None,
                        "completed_at": attempt.get("completed_at", ""),
                        "attempt_number": attempt.get("attempt_number"),
                        "_order": evidence_order,
                    })

    # Aggregate mistake counters predate item-level tracking in some sessions.
    # Use them only when no item-level practice history exists for that skill.
    mistakes = course_progress.get("mistakes", {})
    if isinstance(mistakes, dict):
        for tag, count in mistakes.items():
            try:
                error_count = max(0, int(count))
            except (TypeError, ValueError):
                continue
            if error_count <= 0:
                continue
            normalized_tag = _mastery_normalize(tag)
            candidates = mistake_tag_skill_candidates.get(normalized_tag, set())
            if len(candidates) == 1:
                skill = skill_records[next(iter(candidates))]
            elif normalized_tag in skill_records:
                skill = skill_records[normalized_tag]
            else:
                skill = ensure_skill(tag)
            skill["legacy_error_count"] += error_count

    skill_items = []
    for record in skill_records.values():
        practice = record["_practice"]
        diagnostic = record["_diagnostic"]
        practice_percent = _mastery_percent(practice)
        diagnostic_percent = _mastery_percent(diagnostic)
        distinct_question_ids = {
            item["question_id"] for item in practice if item.get("question_id")
        }
        latest_practice = max(
            practice,
            key=lambda item: (str(item.get("completed_at") or ""), item["_order"]),
            default=None,
        )
        latest_ratio = latest_practice["ratio"] if latest_practice else None
        diagnostic_flagged = any(item["ratio"] < 0.999 for item in diagnostic)

        if practice:
            if practice_percent < 60 or (latest_ratio is not None and latest_ratio < 0.60):
                status = "Needs review"
            elif (
                len(distinct_question_ids) >= 3
                and practice_percent >= 80
                and latest_ratio is not None
                and latest_ratio >= 0.80
            ):
                status = "Promising evidence"
            else:
                status = "Developing"
        elif diagnostic and diagnostic_percent is not None and diagnostic_percent < 100:
            status = "Needs review"
        elif record["legacy_error_count"] > 0:
            status = "Needs review"
        else:
            status = "Not tested"

        lesson_titles = list(record["_lesson_titles"])
        lead_lesson = lesson_titles[0] if lesson_titles else None
        if status == "Needs review":
            if lead_lesson:
                next_action = (
                    f'Review "{lead_lesson}" and retry practice for {record["skill"]}; '
                    "check the explanation after each answer."
                )
            else:
                next_action = (
                    f"Review {record['skill']} using the course lessons, then answer "
                    "a fresh practice question."
                )
        elif status == "Developing":
            if lead_lesson:
                next_action = (
                    f'Build more evidence for {record["skill"]} in "{lead_lesson}" '
                    "by answering different practice questions."
                )
            else:
                next_action = f"Answer different practice questions for {record['skill']}."
        elif status == "Not tested":
            if lead_lesson:
                next_action = (
                    f'Practise {record["skill"]} in "{lead_lesson}" so Vocogni can '
                    "collect question-level evidence."
                )
            else:
                next_action = f"Try a practice question for {record['skill']}."
        else:
            next_action = (
                f"Keep {record['skill']} reliable by applying it in a different "
                "question or mixed task when one is available."
            )

        skill_items.append({
            "skill": record["skill"],
            "status": status,
            "practice_performance_percent": practice_percent,
            "practice_answers": len(practice),
            "distinct_practice_questions": len(distinct_question_ids),
            "full_credit_answers": sum(item["correct"] for item in practice),
            "latest_practice_percent": round(latest_ratio * 100) if latest_ratio is not None else None,
            "diagnostic_performance_percent": diagnostic_percent,
            "diagnostic_items": len(diagnostic),
            "diagnostic_flagged": diagnostic_flagged,
            "legacy_error_count": record["legacy_error_count"],
            "lesson_titles": lesson_titles,
            "next_action": next_action,
        })

    status_counts = {
        status: sum(item["status"] == status for item in skill_items)
        for status in _MASTERY_STATUSES
    }
    priority = {"Needs review": 0, "Developing": 1, "Not tested": 2, "Promising evidence": 3}
    first_action = next(
        (item["next_action"] for status in ("Needs review", "Developing", "Not tested", "Promising evidence")
         for item in skill_items if item["status"] == status),
        "Start a lesson to create your first learning evidence.",
    )
    return {
        "course_id": course_id,
        "course_title": course.get("title", course.get("topic_label", course_id)),
        "skills": skill_items,
        "status_counts": status_counts,
        "skills_total": len(skill_items),
        "practice_answers_total": sum(item["practice_answers"] for item in skill_items),
        "next_action": first_action,
        "thresholds": {
            "promising_min_distinct_questions": 3,
            "promising_min_performance_percent": 80,
            "needs_review_below_percent": 60,
        },
        "evidence_note": (
            "Rule-based practice evidence, not a validated mastery score. "
            "Promising evidence requires at least 3 distinct practice question IDs, "
            "at least 80% average performance, and at least 80% on the latest item. "
            "Entry diagnostics are baseline evidence; passing a diagnostic alone does "
            "not establish mastery. Delayed-retention testing is not yet measured."
        ),
    }


# ---------------------------------------------------------------------------
# Lesson locking
# ---------------------------------------------------------------------------

def is_lesson_unlocked(progress, course_id, lesson_index):
    """Lesson 0 is always unlocked; lesson N unlocks once lesson N-1 is done."""
    if lesson_index == 0:
        return True
    course = data.get_course(course_id)
    prev_lesson = course["lessons"][lesson_index - 1]
    prog = progress.get(course_id, {})
    return prev_lesson["id"] in prog.get("completed_lessons", [])


def next_incomplete_lesson(progress, course_id):
    """Return the first not-yet-completed lesson dict, or None if all done."""
    course = data.get_course(course_id)
    prog = progress.get(course_id, {})
    completed = set(prog.get("completed_lessons", []))
    for lesson in course["lessons"]:
        if lesson["id"] not in completed:
            return lesson
    return None


# ---------------------------------------------------------------------------
# Progress / accuracy calculations
# ---------------------------------------------------------------------------

def course_accuracy(progress, course_id):
    """Accuracy percentage (0-100) for a course, or None if never attempted."""
    prog = progress.get(course_id, {})
    attempted = prog.get("questions_attempted", 0)
    if attempted == 0:
        return None
    return prog.get("correct_answers", 0) / attempted * 100


def course_diagnostic_lesson_id(course_id):
    """Return the lesson ID holding this course's course-entry diagnostic."""
    course = data.get_course(course_id)
    if not course:
        return None
    return next(
        (lesson["id"] for lesson in course["lessons"] if lesson.get("diagnostic")),
        None,
    )


def course_diagnostic_completed(progress, course_id):
    """Return True when the configured course-entry diagnostic is saved."""
    diagnostic_lesson_id = course_diagnostic_lesson_id(course_id)
    if diagnostic_lesson_id is None:
        return True
    prog = progress.get(course_id, {})
    records = prog.get("diagnostics", {})
    return isinstance(records, dict) and diagnostic_lesson_id in records


def update_lesson_screen_checkpoint(progress, course_id, lesson_id, updates):
    """Update only one lesson's durable screen checkpoint; leave learning history intact."""
    if not isinstance(updates, dict):
        raise TypeError("updates must be a dictionary")
    course_progress = progress.setdefault(course_id, blank_course_progress())
    screen_records = course_progress.setdefault("lesson_screen_progress", {})
    if not isinstance(screen_records, dict):
        screen_records = {}
        course_progress["lesson_screen_progress"] = screen_records
    existing = screen_records.get(lesson_id, {})
    checkpoint = dict(existing) if isinstance(existing, dict) else {}
    checkpoint.update(updates)
    if "completed_screens" in checkpoint:
        values = checkpoint.get("completed_screens", [])
        if not isinstance(values, list):
            values = []
        clean = []
        for value in values:
            try:
                screen = int(value)
            except (TypeError, ValueError):
                continue
            if screen in (1, 2, 3) and screen not in clean:
                clean.append(screen)
        checkpoint["completed_screens"] = clean
    checkpoint["updated_at"] = datetime.now(timezone.utc).isoformat()
    screen_records[lesson_id] = checkpoint
    course_progress["started"] = True
    return dict(checkpoint)


def get_lesson_screen_checkpoint(progress, course_id, lesson_id):
    """Return a safe copy of the latest saved screen checkpoint for a lesson."""
    course_progress = progress.get(course_id, {})
    records = course_progress.get("lesson_screen_progress", {})
    if not isinstance(records, dict):
        return {}
    checkpoint = records.get(lesson_id, {})
    if not isinstance(checkpoint, dict):
        return {}
    result = dict(checkpoint)
    if isinstance(result.get("completed_screens"), list):
        result["completed_screens"] = list(result["completed_screens"])
    return result


def course_lesson_progress_percent(progress, course_id):
    course = data.get_course(course_id)
    if not course:
        return 0
    total = len(course["lessons"])
    prog = progress.get(course_id, {})
    done = len(prog.get("completed_lessons", []))
    diagnostic_lesson_id = course_diagnostic_lesson_id(course_id)
    if diagnostic_lesson_id:
        total += 1
        done += int(diagnostic_lesson_id in prog.get("diagnostics", {}))
    return int(round(done / total * 100)) if total else 0


def classify_strength(accuracy):
    """
    Prototype logic only — a simple accuracy threshold, not an AI-diagnosed
    assessment of the learner's cognition (see spec section 12).
    """
    if accuracy is None:
        return None
    if accuracy >= 80:
        return "Strength"
    if accuracy < 60:
        return "Weakness"
    return "Developing"


def common_mistakes_for_course(progress, course_id):
    """List of (mistake_tag, count) for a course, sorted most-common first."""
    prog = progress.get(course_id, {})
    mistakes = prog.get("mistakes", {})
    items = [(tag, count) for tag, count in mistakes.items() if count > 0]
    items.sort(key=lambda kv: kv[1], reverse=True)
    return items


def per_course_stats(progress):
    """One summary dict per course — used by the Progress page and the
    prototype AI summary."""
    stats = []
    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        prog = progress.get(course_id, {})
        attempted = prog.get("questions_attempted", 0)
        correct = prog.get("correct_answers", 0)
        accuracy = (correct / attempted * 100) if attempted else None
        stats.append({
            "course_id": course_id,
            "topic_label": course["topic_label"],
            "questions_attempted": attempted,
            "correct_answers": correct,
            "accuracy": accuracy,
            "top_mistakes": common_mistakes_for_course(progress, course_id)[:2],
        })
    return stats


def overall_stats(progress):
    """Aggregate stats across all courses, for the Progress page overview."""
    courses_attempted = 0
    courses_completed = 0
    lessons_completed = 0
    questions_attempted = 0
    correct_answers = 0
    total_mistakes = 0

    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        prog = progress.get(course_id, {})
        if prog.get("started"):
            courses_attempted += 1
        done = len(prog.get("completed_lessons", []))
        lessons_completed += done
        diagnostic_id = course_diagnostic_lesson_id(course_id)
        diagnostic_done = (
            not diagnostic_id
            or diagnostic_id in prog.get("diagnostics", {})
        )
        if done == len(course["lessons"]) and diagnostic_done and (
            done > 0 or bool(diagnostic_id and diagnostic_done)
        ):
            courses_completed += 1
        questions_attempted += prog.get("questions_attempted", 0)
        correct_answers += prog.get("correct_answers", 0)
        total_mistakes += sum(prog.get("mistakes", {}).values())

    return {
        "courses_attempted": courses_attempted,
        "courses_completed": courses_completed,
        "lessons_completed": lessons_completed,
        "questions_attempted": questions_attempted,
        "correct_answers": correct_answers,
        "total_mistakes": total_mistakes,
    }


# ---------------------------------------------------------------------------
# Recommendations — rule-based prototype logic
#
# TO REPLACE WITH A REAL RECOMMENDATION MODEL LATER:
#   Keep the signature `generate_recommendations(progress) -> list[str]`
#   (or evolve it to return structured dicts instead of strings). Swap the
#   rule checks below for a call to your model / service. Every caller
#   (sections/browse.py, sections/progress.py) only reads the returned
#   list, so nothing else needs to change.
# ---------------------------------------------------------------------------

def generate_recommendations(progress, limit=4):
    recs = []

    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        prog = progress.get(course_id, {})
        if not prog.get("started"):
            recs.append(f"Start {course['title']}")

    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        acc = course_accuracy(progress, course_id)
        if acc is not None and acc < 60:
            recs.append(f"Review {course['title']}")

    fractions_acc = course_accuracy(progress, "fractions")
    algebra_acc = course_accuracy(progress, "algebra")
    if (
        fractions_acc is not None and fractions_acc >= 80
        and algebra_acc is not None and algebra_acc < 60
    ):
        recs.append("Continue Algebra Basics")

    seen = set()
    deduped = []
    for rec in recs:
        if rec not in seen:
            seen.add(rec)
            deduped.append(rec)
    return deduped[:limit]


# ---------------------------------------------------------------------------
# Mistake-to-Mastery Coach
#
# Turns accumulated error evidence into one concrete next action. This is
# deliberately deterministic: the recommendation is explainable and works
# without an LLM. Its long-term value comes from learner-specific evidence
# and measured improvement, not from the rule table alone.
# ---------------------------------------------------------------------------

_MISTAKE_COACH_RULES = (
    {
        "patterns": ("denominator", "equivalent fractions", "comparing fractions",
                     "adding fractions", "subtracting unlike fractions", "simplification"),
        "skill": "Fraction structure",
        "why": "Your recorded errors point to fraction structure, not just arithmetic.",
        "action": "Review equivalent fractions, then solve three unlike-denominator questions.",
        "course_ids": ("fractions",),
    },
    {
        "patterns": ("variable", "inverse operation", "equations with brackets",
                     "equations on both sides", "two-step equations", "sign errors"),
        "skill": "Equation transformations",
        "why": "Your recorded errors suggest one or more equation steps are not yet reliable.",
        "action": "Write one inverse operation per line and check the result by substitution.",
        "course_ids": ("algebra",),
    },
    {
        "patterns": ("translating", "key words", "relevant information",
                     "forming an equation", "multi-step setup", "misidentifying the operation"),
        "skill": "Word-problem modelling",
        "why": "The difficulty appears to be translating a situation into mathematics before calculating.",
        "action": "Define the unknown, write the relationship, and only then calculate.",
        "course_ids": ("word_problems",),
    },
    {
        "patterns": ("budget", "pricing", "cost model", "break-even", "sharing a multi-step cost"),
        "skill": "Applied modelling",
        "why": "Your errors cluster around choosing and building a model for a real situation.",
        "action": "List known values and constraints, define the unknown, then test whether the answer fits the context.",
        "course_ids": ("word_problems", "algebra"),
    },
)


def get_mistake_coach(progress):
    """Return one explainable intervention from durable mistake counts, or None.

    Counts are evidence of repeated errors, not proof of a misconception.
    Only use known course IDs when suggesting a course destination.
    """
    candidates = []
    for course_id in data.COURSE_ORDER:
        course = data.get_course(course_id)
        prog = progress.get(course_id, {})
        mistakes = prog.get("mistakes", {})
        for tag, count in mistakes.items():
            if not isinstance(count, (int, float)) or count <= 0:
                continue
            tag_text = str(tag).casefold()
            for rule in _MISTAKE_COACH_RULES:
                if any(pattern in tag_text for pattern in rule["patterns"]):
                    candidates.append({
                        "source_course_id": course_id,
                        "source_course_title": course["title"],
                        "mistake_tag": str(tag),
                        "count": int(count),
                        "skill": rule["skill"],
                        "why": rule["why"],
                        "action": rule["action"],
                        "course_ids": rule["course_ids"],
                    })
                    break
    if not candidates:
        return None
    candidates.sort(key=lambda item: (-item["count"], item["skill"], item["mistake_tag"]))
    chosen = candidates[0]
    destinations = []
    for course_id in chosen["course_ids"]:
        if course_id in data.COURSES and course_id not in destinations:
            destinations.append(course_id)
    chosen["available_course_ids"] = destinations
    chosen["evidence_label"] = (
        f"{chosen['count']} recorded error{'s' if chosen['count'] != 1 else ''}: "
        f"{chosen['mistake_tag']}"
    )
    return chosen


# ---------------------------------------------------------------------------
# Simulated AI progress summary
#
# TO REPLACE WITH A REAL LLM LATER:
#   1. pip install anthropic, and add it to requirements.txt.
#   2. Provide an API key via an environment variable or st.secrets
#      (never hard-code a key in source).
#   3. Keep this function's exact signature:
#        generate_progress_summary(profile, progress) -> str
#      sections/progress.py calls it without knowing how it's implemented.
#   4. Inside, build a short prompt from the same stats gathered below
#      (per_course_stats, weakest/strongest topic, top mistakes) and send
#      it to client.messages.create(model=..., messages=[...]), returning
#      the response text instead of the template text below.
#   5. Wrap the API call in try/except and fall back to the template
#      version if the call fails or no key is configured, so the Progress
#      page always shows something.
# ---------------------------------------------------------------------------

def generate_progress_summary(profile, progress):
    name = (profile.get("name") or "").strip() or "there"
    stats = per_course_stats(progress)
    attempted = [s for s in stats if s["questions_attempted"] > 0]

    if not attempted:
        body = (
            f"Hi {name}. You haven't attempted any practice questions yet.\n\n"
            "Start any course from the Browse page — this summary will "
            "update with real feedback based on your activity."
        )
        return _wrap_summary(body)

    strongest = max(attempted, key=lambda s: s["accuracy"])
    weakest = min(attempted, key=lambda s: s["accuracy"])

    lines = [f"Hi {name}. Here is where your practice stands right now.", ""]

    if strongest["accuracy"] >= 80:
        lines.append(
            f"You have made strong progress in {strongest['topic_label']}, "
            f"answering {strongest['accuracy']:.0f}% of attempted questions "
            "correctly."
        )
    else:
        lines.append(
            f"Your strongest area so far is {strongest['topic_label']}, at "
            f"{strongest['accuracy']:.0f}% accuracy."
        )

    if weakest["course_id"] != strongest["course_id"]:
        lines.append(
            f"Your main difficulty right now is {weakest['topic_label']} "
            f"({weakest['accuracy']:.0f}% accuracy)."
        )

    if weakest["top_mistakes"]:
        lines.append("")
        lines.append("You should review:")
        for i, (tag, _count) in enumerate(weakest["top_mistakes"], start=1):
            lines.append(f"{i}. {tag}")

    lines.append("")
    lines.append(f"Recommended next step: {_recommend_next_step(progress, weakest)}")

    return _wrap_summary("\n".join(lines))


def _recommend_next_step(progress, weakest_stat):
    course_id = weakest_stat["course_id"]
    course = data.get_course(course_id)
    lesson = next_incomplete_lesson(progress, course_id)
    if lesson is not None:
        return f"Complete the \u201c{lesson['title']}\u201d lesson in {course['topic_label']}."
    return f"Revisit the {course['topic_label']} lessons for extra practice."


def _wrap_summary(body):
    return "Vocogni Learning Summary \u2014 Prototype\n\n" + body


# ---------------------------------------------------------------------------
# Optional sound cue — generated on the fly with the standard library only,
# so Version 1 needs no bundled audio asset.
# ---------------------------------------------------------------------------

def _generate_beep_wav_bytes(frequency=880.0, duration_ms=150, volume=0.25, sample_rate=22050):
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            fade = 1.0 - (i / n_samples)  # avoid a click at the tail
            sample = volume * fade * math.sin(2 * math.pi * frequency * t)
            frames += struct.pack("<h", int(sample * 32767))
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def get_correct_answer_beep_base64():
    """Base64-encoded short WAV beep, used for the Settings > Sound option."""
    return base64.b64encode(_generate_beep_wav_bytes()).decode("ascii")