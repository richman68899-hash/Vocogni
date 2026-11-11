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
import hashlib
import io
import json
import math
import struct
from datetime import datetime, timezone
import wave

import data
import math_taxonomy
import question_engine

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
        "mistake_reflections": [],
        "diagnostics": {},
        "lesson_assessments": {},
        "practice_attempts": {},
        "skill_confirmation_attempts": [],
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

    def ensure_skill(label, lesson_title=None, skill_id=None):
        safe_label = str(label or "Untitled skill").strip() or "Untitled skill"
        stable_id = (
            str(skill_id).strip()
            if isinstance(skill_id, str) and skill_id in math_taxonomy.SKILLS
            else None
        )
        normalized = _mastery_normalize(safe_label) or "untitled skill"
        key = stable_id or normalized
        record = skill_records.get(key)
        if record is None:
            record = {
                "_key": key,
                "skill": safe_label,
                "skill_id": stable_id,
                "_question_ids": set(),
                "_practice": [],
                "_diagnostic": [],
                "_lesson_titles": [],
                "legacy_error_count": 0,
            }
            skill_records[key] = record
        elif stable_id and not record.get("skill_id"):
            record["skill_id"] = stable_id
        if lesson_title and lesson_title not in record["_lesson_titles"]:
            record["_lesson_titles"].append(lesson_title)
        return record

    # Construct the skill catalogue entirely from this course's authored data.
    lessons = course.get("lessons", [])
    if not isinstance(lessons, list):
        lessons = []
    # Resolve current, verified VQE metadata once. Legacy and stale items
    # keep their tag-based mapping; approved items group evidence by stable ID.
    verified_vqe_by_id = {
        (str(record.get("lesson_id") or ""), str(record.get("question_id") or "")): record["question"]
        for record in question_engine.iter_question_records(course_id=course_id)
        if record.get("verification_status") == "verified"
    }

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
            question_id = question.get("id")
            normalized_qid = str(question_id).strip() if question_id is not None else ""
            vqe_question = verified_vqe_by_id.get((lesson_id, normalized_qid))
            if vqe_question and vqe_question.get("skill_id") in math_taxonomy.SKILLS:
                skill_id = vqe_question["skill_id"]
                skill_label = vqe_question.get("skill_label") or _mastery_question_skill(question, lesson)
            else:
                skill_id = None
                skill_label = _mastery_question_skill(question, lesson)
            skill = ensure_skill(skill_label, lesson_title, skill_id=skill_id)
            if normalized_qid:
                question_map[normalized_qid] = skill["_key"]
                skill["_question_ids"].add(normalized_qid)

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
                    question_id = result.get("question_id")
                    normalized_qid = str(question_id).strip() if question_id is not None else ""
                    # A practice attempt can contain a VQE item authored in a
                    # different lesson (for example, a diagnostic pathway).
                    # New records identify the canonical source lesson. Legacy
                    # records without provenance continue using the attempt key.
                    source_lesson_id = str(
                        result.get("lesson_id")
                        or result.get("source_lesson_id")
                        or lesson_id
                    )
                    # Practice contributes only when the saved result and the
                    # current reviewed registry agree on its canonical source.
                    if (
                        result.get("verification_status") != "verified"
                        or (source_lesson_id, normalized_qid) not in verified_vqe_by_id
                    ):
                        continue
                    evidence_order += 1
                    source_question_map = question_skill_by_lesson.get(source_lesson_id, {})
                    mapped_key = source_question_map.get(normalized_qid)
                    source_lesson, _ = data.get_lesson(course_id, source_lesson_id)
                    source_lesson_title = (
                        source_lesson.get("title", source_lesson_id)
                        if source_lesson else source_lesson_id
                    )
                    recorded_skill_id = result.get("skill_id")
                    if isinstance(recorded_skill_id, str) and recorded_skill_id in math_taxonomy.SKILLS:
                        # New result records carry the stable VQE skill ID.
                        # This takes precedence over mutable human-readable tags.
                        skill = ensure_skill(
                            math_taxonomy.SKILLS[recorded_skill_id]["label"],
                            source_lesson_title,
                            skill_id=recorded_skill_id,
                        )
                    elif mapped_key:
                        # Historical records without skill_id resolve through
                        # the current question map, preserving old progress.
                        skill = skill_records[mapped_key]
                    else:
                        # Legacy and future non-VQE items retain tag-based mapping.
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
                        "source_lesson_id": source_lesson_id,
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
            "skill_id": record.get("skill_id"),
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
# Offline AI progress summary
# ---------------------------------------------------------------------------

_SUMMARY_COPY = {
    "English": {
        "empty": "You have not recorded any practice questions yet. Start a course from Browse; once practice is recorded, this summary can identify patterns and recommend a next step.",
        "snapshot": "Here is your current learning snapshot.",
        "overall": "Across {courses} active course(s), you answered {correct} of {attempted} questions correctly ({accuracy}% overall accuracy).",
        "single": "Your recorded accuracy in {course} is {accuracy}%.",
        "strongest": "Your strongest recorded area is {course} ({accuracy}%).",
        "weakest": "The area currently needing the most attention is {course} ({accuracy}%).",
        "mistakes": "Recorded mistake categories to review:",
        "corrected": "Revisit a worked method, then close it and reconstruct the solution independently.",
        "find_error": "Before viewing a correction, identify the first step where your method diverged.",
        "misconception": "Focus on the rule or concept behind the error, not only on memorising the correction.",
        "next": "Recommended next step: {step}",
        "scoped": "Keep this next action within {course}: {step}",
        "adaptive_low": "Mastery adjustment: consolidate the underlying skill before increasing difficulty; the current accuracy is below 60%.",
        "adaptive_high": "Mastery adjustment: with at least five attempts and accuracy of 85% or higher, try a harder application while checking retention.",
        "adaptive_mid": "Mastery adjustment: keep practising at the current level and collect more evidence before changing difficulty.",
        "steady": "Progression: use a steady sequence of review, independent practice, and one application question; difficulty is not adjusted automatically.",
        "confidence": "Practice focus: choose one manageable skill, use short practice sets, and build consistency.",
        "standard": "Practice focus: use a balanced set of familiar questions and a few new applications.",
        "stretch": "Practice focus: after reviewing errors, attempt a less familiar or more demanding application.",
        "transfer": "Transfer: apply the same idea to a question in a different context.",
        "hint_on_request": "Hint strategy: make an initial attempt, then request a hint only when it is useful.",
        "hint_progressive": "Hint strategy: reveal one small clue at a time, retrying after each clue.",
        "hint_guided": "Hint strategy: work through what is known, what is required, and which relationship connects them.",
        "hint_example": "Hint strategy: study one worked example, then solve a similar question without looking.",
        "socratic": "Understanding check: which step feels least secure, and what makes it difficult?",
        "direct": "Priority: review the weakest area, practise its next incomplete lesson, and check the result.",
        "detailed": "How to use this report: treat accuracy as a snapshot of recorded attempts. Review the underlying method, practise it independently, and then test it with a different question.",
        "brief": "Keep the next session focused on one lesson and one review target.",
        "everyday": "Where useful, connect the next question to a familiar real-world situation.",
        "reasoning": "Reasoning check: explain why the chosen method fits the question before calculating.",
        "calculation": "Accuracy check: verify units, signs, and the final result where relevant.",
        "uncertain": "Evidence limits: these are rule-based interpretations of saved activity, not a diagnosis or proof of mastery.",
        "brief_uncertain": "Note: this is a snapshot of saved activity, not a definitive mastery assessment.",
        "evidence": "Evidence used: saved question attempts, correct-answer totals, and recorded mistake tags. No external sources are consulted.",
        "scope": "Scope: recommendations are restricted to {course}.",
        "broad_scope": "Scope: the report compares all active courses.",
        "memory_on": "Saved AI preferences guided this report. The offline summary does not create a separate model memory.",
        "memory_off": "Preference memory is off: this report uses the current settings only and creates no separate AI memory.",
        "context_off": "Your display name was not used. The report uses saved practice records locally and sends nothing to an external provider.",
        "safety": "Learner-appropriate safeguards remain active regardless of the age-appropriateness preference.",
        "limits": "Local capability boundary: model selection, response-speed tiers, web research, and image/worksheet analysis are not active in this offline summary.",
        "course_breakdown": "Course-by-course recorded performance:",
        "interpret": "Interpretation: accuracy describes the questions recorded so far. A small or uneven sample can change quickly, so use it to choose what to practise rather than as a final judgement.",
        "settings": "Settings applied:",
        "teaching": "Teaching approach",
        "depth": "Explanation depth",
        "hint": "Hint strategy",
        "correction": "Correction style",
        "challenge": "Challenge level",
        "language": "Response language",
        "format": "Answer format",
        "exam_heading": "Performance overview",
        "footer": "Generated locally from saved Vocogni learning data.",
    },
    "Bahasa Indonesia": {
        "empty": "Belum ada soal latihan yang tercatat. Mulai kursus dari Browse; setelah latihan tercatat, ringkasan ini dapat menemukan pola dan menyarankan langkah berikutnya.",
        "snapshot": "Berikut gambaran kemajuan belajarmu saat ini.",
        "overall": "Di {courses} kursus aktif, kamu menjawab {correct} dari {attempted} soal dengan benar (akurasi keseluruhan {accuracy}%).",
        "single": "Akurasi tercatatmu di {course} adalah {accuracy}%.",
        "strongest": "Area dengan hasil tercatat terbaik adalah {course} ({accuracy}%).",
        "weakest": "Area yang saat ini paling perlu diperhatikan adalah {course} ({accuracy}%).",
        "mistakes": "Kategori kesalahan yang tercatat untuk ditinjau:",
        "corrected": "Pelajari kembali contoh penyelesaian, tutup contohnya, lalu susun ulang langkah penyelesaian secara mandiri.",
        "find_error": "Sebelum melihat koreksi, cari langkah pertama ketika metode yang kamu gunakan mulai menyimpang.",
        "misconception": "Fokus pada aturan atau konsep di balik kesalahan, bukan hanya menghafal koreksinya.",
        "next": "Langkah berikutnya yang disarankan: {step}",
        "scoped": "Batasi langkah berikutnya pada {course}: {step}",
        "adaptive_low": "Penyesuaian penguasaan: kuatkan keterampilan dasar sebelum menaikkan tingkat kesulitan; akurasi saat ini di bawah 60%.",
        "adaptive_high": "Penyesuaian penguasaan: dengan minimal lima percobaan dan akurasi 85% atau lebih, coba penerapan yang lebih menantang sambil memeriksa daya ingat.",
        "adaptive_mid": "Penyesuaian penguasaan: lanjutkan latihan pada tingkat saat ini dan kumpulkan lebih banyak bukti sebelum mengubah kesulitan.",
        "steady": "Urutan belajar: tinjau materi, berlatih mandiri, lalu kerjakan satu soal penerapan; tingkat kesulitan tidak diubah otomatis.",
        "confidence": "Fokus latihan: pilih satu keterampilan yang terjangkau, gunakan sesi latihan singkat, dan bangun konsistensi.",
        "standard": "Fokus latihan: gunakan kombinasi soal yang sudah dikenal dan beberapa penerapan baru.",
        "stretch": "Fokus latihan: setelah meninjau kesalahan, coba penerapan yang lebih asing atau menantang.",
        "transfer": "Penerapan: gunakan ide yang sama untuk menyelesaikan soal dalam konteks berbeda.",
        "hint_on_request": "Strategi petunjuk: coba kerjakan terlebih dahulu, lalu minta petunjuk saat diperlukan.",
        "hint_progressive": "Strategi petunjuk: tampilkan satu petunjuk kecil setiap kali, lalu coba lagi.",
        "hint_guided": "Strategi petunjuk: uraikan apa yang diketahui, apa yang ditanyakan, dan hubungan yang menghubungkannya.",
        "hint_example": "Strategi petunjuk: pelajari satu contoh penyelesaian, lalu kerjakan soal serupa tanpa melihat contoh.",
        "socratic": "Pemeriksaan pemahaman: langkah mana yang terasa paling belum kamu kuasai, dan mengapa?",
        "direct": "Prioritas: tinjau area terlemah, kerjakan pelajaran berikutnya yang belum selesai, lalu periksa hasilnya.",
        "detailed": "Cara menggunakan laporan ini: anggap akurasi sebagai gambaran dari percobaan yang tercatat. Tinjau metodenya, latih secara mandiri, lalu uji dengan soal yang berbeda.",
        "brief": "Fokuskan sesi berikutnya pada satu pelajaran dan satu target tinjauan.",
        "everyday": "Jika sesuai, hubungkan soal berikutnya dengan situasi sehari-hari yang sudah dikenal.",
        "reasoning": "Pemeriksaan penalaran: jelaskan mengapa metode yang dipilih sesuai dengan soal sebelum menghitung.",
        "calculation": "Pemeriksaan ketelitian: periksa satuan, tanda, dan hasil akhir jika relevan.",
        "uncertain": "Batas bukti: ini adalah interpretasi berbasis aturan dari aktivitas tersimpan, bukan diagnosis atau bukti penguasaan.",
        "brief_uncertain": "Catatan: ini hanya gambaran aktivitas tersimpan, bukan penilaian penguasaan yang pasti.",
        "evidence": "Bukti yang digunakan: percobaan soal tersimpan, jumlah jawaban benar, dan kategori kesalahan tercatat. Tidak ada sumber eksternal yang digunakan.",
        "scope": "Cakupan: rekomendasi dibatasi pada {course}.",
        "broad_scope": "Cakupan: laporan membandingkan semua kursus aktif.",
        "memory_on": "Preferensi AI yang tersimpan digunakan untuk laporan ini. Ringkasan offline tidak membuat memori model terpisah.",
        "memory_off": "Memori preferensi nonaktif: laporan ini hanya menggunakan pengaturan saat ini dan tidak membuat memori AI terpisah.",
        "context_off": "Nama tampilanmu tidak digunakan. Laporan memakai catatan latihan secara lokal dan tidak mengirim data ke penyedia eksternal.",
        "safety": "Perlindungan yang sesuai untuk pelajar tetap aktif terlepas dari preferensi kesesuaian usia.",
        "limits": "Batas kemampuan lokal: pilihan model, tingkat kecepatan, riset web, serta analisis gambar/lembar kerja belum aktif dalam ringkasan offline ini.",
        "course_breakdown": "Performa tercatat untuk setiap kursus:",
        "interpret": "Interpretasi: akurasi menggambarkan soal yang sudah tercatat. Sampel yang sedikit atau tidak merata dapat berubah cepat, jadi gunakan data ini untuk memilih latihan, bukan sebagai penilaian akhir.",
        "settings": "Pengaturan yang diterapkan:",
        "teaching": "Pendekatan mengajar",
        "depth": "Kedalaman penjelasan",
        "hint": "Strategi petunjuk",
        "correction": "Gaya koreksi",
        "challenge": "Tingkat tantangan",
        "language": "Bahasa respons",
        "format": "Format jawaban",
        "exam_heading": "Gambaran performa",
        "footer": "Dibuat secara lokal dari data belajar Vocogni yang tersimpan.",
    },
    "Mandarin": {
        "empty": "目前还没有记录练习题。请先从 Browse 开始一门课程；记录练习后，本摘要便能识别学习模式并建议下一步。",
        "snapshot": "以下是你目前的学习情况。",
        "overall": "在 {courses} 门进行中的课程中，你答对了 {correct}/{attempted} 道题，整体正确率为 {accuracy}%。",
        "single": "你在 {course} 的记录正确率为 {accuracy}%。",
        "strongest": "目前记录表现最好的是 {course}（{accuracy}%）。",
        "weakest": "目前最值得优先复习的是 {course}（{accuracy}%）。",
        "mistakes": "建议复习的已记录错误类别：",
        "corrected": "重新学习一道例题，然后合上例题，独立还原解题步骤。",
        "find_error": "查看订正前，先找出你的方法从哪一步开始出现偏差。",
        "misconception": "重点理解错误背后的规则或概念，而不只是记住正确答案。",
        "next": "建议的下一步：{step}",
        "scoped": "下一步仅围绕 {course}：{step}",
        "adaptive_low": "掌握度调整：目前正确率低于 60%，应先巩固基础技能，再提高难度。",
        "adaptive_high": "掌握度调整：至少完成五次练习且正确率达到 85% 后，可以尝试更有挑战性的应用题，同时检查是否真正掌握。",
        "adaptive_mid": "掌握度调整：先维持当前难度继续练习，收集更多记录后再调整难度。",
        "steady": "学习顺序：复习、独立练习，再完成一道应用题；系统不会自动调整难度。",
        "confidence": "练习重点：选择一项可完成的技能，通过短练习逐步建立稳定性。",
        "standard": "练习重点：结合熟悉的题目与少量新的应用题。",
        "stretch": "练习重点：复习错误后，尝试不太熟悉或更具挑战性的应用题。",
        "transfer": "迁移应用：在不同情境中运用同一个概念。",
        "hint_on_request": "提示策略：先独立尝试，确实需要时再请求提示。",
        "hint_progressive": "提示策略：每次只查看一条小提示，然后重新尝试。",
        "hint_guided": "提示策略：依次明确已知条件、所求内容，以及连接两者的关系。",
        "hint_example": "提示策略：先学习一道例题，再不看例题独立完成类似题目。",
        "socratic": "理解检查：哪一个步骤让你最没有把握？原因是什么？",
        "direct": "优先事项：复习最薄弱的领域，完成下一节未完成的课程，然后检查结果。",
        "detailed": "如何使用本报告：正确率只是已记录练习的阶段性表现。请复习相关方法，独立练习，再用不同题目检验。",
        "brief": "下一次学习集中在一节课程和一个复习目标上。",
        "everyday": "合适时，将下一道题与熟悉的现实生活情境联系起来。",
        "reasoning": "推理检查：计算前，先说明所选方法为什么适合这道题。",
        "calculation": "准确性检查：必要时核对单位、正负号和最终结果。",
        "uncertain": "证据限制：这些建议是根据已保存活动生成的规则化解释，并非诊断，也不能证明已经掌握。",
        "brief_uncertain": "说明：这只是已保存学习活动的概况，并非最终掌握程度评估。",
        "evidence": "使用的证据：已保存的答题记录、正确答案数量和错误标签。不会查询外部来源。",
        "scope": "范围：建议仅限于 {course}。",
        "broad_scope": "范围：报告会比较所有进行中的课程。",
        "memory_on": "本报告使用了已保存的 AI 偏好设置。离线摘要不会创建独立的模型记忆。",
        "memory_off": "偏好记忆已关闭：本报告只使用当前设置，不会创建独立的 AI 记忆。",
        "context_off": "未使用你的显示名称。报告仅在本地读取已保存的练习记录，不会发送给外部服务商。",
        "safety": "无论年龄适宜性偏好如何设置，面向学习者的安全保护都会继续生效。",
        "limits": "本地功能限制：模型选择、响应速度等级、网络研究，以及图片/练习纸分析，目前不会用于这份离线摘要。",
        "course_breakdown": "各课程的记录表现：",
        "interpret": "数据解释：正确率只反映目前记录的题目。样本较少或分布不均时，结果可能迅速变化；请用它选择练习内容，而不要视为最终评价。",
        "settings": "本次应用的设置：",
        "teaching": "教学方式",
        "depth": "解释深度",
        "hint": "提示策略",
        "correction": "纠错方式",
        "challenge": "挑战程度",
        "language": "回复语言",
        "format": "答案格式",
        "exam_heading": "学习表现概览",
        "footer": "本摘要由 Vocogni 已保存的学习数据在本地生成。",
    },
}



def progress_summary_signature(profile, progress, preferences=None):
    """Stable cache key: summary output must refresh when its inputs change."""
    profile = profile if isinstance(profile, dict) else {}
    progress = progress if isinstance(progress, dict) else {}
    preferences = preferences if isinstance(preferences, dict) else {}
    profile_context = {
        "preferred_language": profile.get("preferred_language", "English"),
        "name": (
            profile.get("name", "")
            if preferences.get("ai_preview_context_permission", True)
            else ""
        ),
    }
    payload = json.dumps(
        {
            "profile": profile_context,
            "progress": progress,
            "preferences": preferences,
        },
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()

def _summary_language(profile, preferences):
    """Resolve explicit language, or use the learner's saved language for auto mode."""
    selected = preferences.get("ai_preview_response_language", "Match lesson language")
    if selected == "Match lesson language":
        selected = (profile or {}).get("preferred_language", "English")
    normalized = str(selected or "English").strip().casefold()
    if normalized in {"bahasa indonesia", "indonesian", "indonesia"}:
        return "Bahasa Indonesia"
    if normalized in {"mandarin", "mandarin chinese", "chinese", "中文", "汉语"}:
        return "Mandarin"
    return "English"


def _format_progress_summary(lines, format_style, exam_heading="Performance overview"):
    """Apply the selected output structure without changing the evidence."""
    if format_style == "Short paragraphs":
        body = " ".join(line.strip() for line in lines if line.strip())
    elif format_style == "Bullet points":
        body = "\n".join(
            line if not line or line.endswith(":") else (line if line.startswith("- ") else f"- {line}")
            for line in lines
        )
    elif format_style == "Exam-style response":
        body = exam_heading + "\n" + "\n".join(lines)
    else:
        body = "\n".join(lines)
    return _wrap_summary(body)


def generate_progress_summary(profile, progress, preferences=None):
    """Generate a settings-aware learning report using deterministic offline rules."""
    profile = profile if isinstance(profile, dict) else {}
    progress = progress if isinstance(progress, dict) else {}
    preferences = preferences if isinstance(preferences, dict) else {}

    language = _summary_language(profile, preferences)
    copy = _SUMMARY_COPY[language]
    name = str(profile.get("name") or "").strip()
    if not preferences.get("ai_preview_context_permission", True) or not name:
        name = {"English": "there", "Bahasa Indonesia": "kamu", "Mandarin": "同学"}[language]

    style = preferences.get("ai_preview_teaching_style", "Adaptive")
    depth = preferences.get("ai_preview_explanation_depth", "Balanced")
    format_style = preferences.get("ai_preview_answer_format", "Structured steps")
    challenge = preferences.get("ai_preview_challenge_level", "Adaptive")
    correction = preferences.get("ai_preview_correction_style", "Explain the misconception")
    hint_strategy = preferences.get("ai_preview_hint_strategy", "On request")

    use_reasoning = bool(preferences.get("ai_preview_reasoning_steps", True))
    check_calculations = bool(preferences.get("ai_preview_check_calculations", True))
    show_uncertainty = bool(preferences.get("ai_preview_flag_uncertainty", True))
    show_sources = bool(preferences.get("ai_preview_show_sources", True))
    use_transfer = bool(preferences.get("ai_preview_transfer_questions", True))
    everyday_examples = bool(preferences.get("ai_preview_everyday_examples", True))
    ask_follow_up = bool(preferences.get("ai_preview_follow_up_questions", True))
    adaptive = bool(preferences.get("ai_preview_adaptive_mastery", True))
    lesson_scope = bool(preferences.get("ai_preview_lesson_scope", False))

    stats = per_course_stats(progress)
    attempted = [item for item in stats if item["questions_attempted"] > 0]
    lines = [f"Hi {name}. {copy['snapshot']}"]

    if not attempted:
        lines.extend(["", copy["empty"]])
    else:
        strongest = max(attempted, key=lambda item: item["accuracy"])
        weakest = min(attempted, key=lambda item: item["accuracy"])
        total_attempted = sum(item["questions_attempted"] for item in attempted)
        total_correct = sum(item["correct_answers"] for item in attempted)
        overall_accuracy = total_correct / total_attempted * 100 if total_attempted else 0

        lines.extend([
            "",
            copy["overall"].format(
                courses=len(attempted),
                correct=total_correct,
                attempted=total_attempted,
                accuracy=f"{overall_accuracy:.0f}",
            ),
        ])
        if strongest["course_id"] == weakest["course_id"]:
            lines.append(copy["single"].format(
                course=strongest["topic_label"],
                accuracy=f"{strongest['accuracy']:.0f}",
            ))
        else:
            lines.append(copy["strongest"].format(
                course=strongest["topic_label"],
                accuracy=f"{strongest['accuracy']:.0f}",
            ))
            lines.append(copy["weakest"].format(
                course=weakest["topic_label"],
                accuracy=f"{weakest['accuracy']:.0f}",
            ))

        if depth != "Brief" and weakest["top_mistakes"]:
            lines.extend(["", copy["mistakes"]])
            for tag, count in weakest["top_mistakes"][:(2 if depth == "Balanced" else 4)]:
                lines.append(f"- {tag} ({count})")
            correction_key = {
                "Show the corrected method": "corrected",
                "Ask me to find the error": "find_error",
            }.get(correction, "misconception")
            lines.append(copy[correction_key])

        next_step = _recommend_next_step(progress, weakest)
        next_key = "scoped" if lesson_scope else "next"
        lines.extend(["", copy[next_key].format(
            course=weakest["topic_label"],
            step=next_step,
        )])

        if adaptive:
            if overall_accuracy < 60:
                lines.append(copy["adaptive_low"])
            elif total_attempted >= 5 and overall_accuracy >= 85:
                lines.append(copy["adaptive_high"])
            else:
                lines.append(copy["adaptive_mid"])
        else:
            lines.append(copy["steady"])

        if challenge == "Build confidence":
            lines.append(copy["confidence"])
        elif challenge == "Standard":
            lines.append(copy["standard"])
        elif challenge == "Stretch me":
            lines.append(copy["stretch"])
        elif challenge == "Adaptive":
            if overall_accuracy < 60:
                lines.append(copy["confidence"])
            elif total_attempted >= 5 and overall_accuracy >= 85:
                lines.append(copy["stretch"])
            else:
                lines.append(copy["standard"])

        if use_transfer and not lesson_scope:
            lines.append(copy["transfer"])
        if hint_strategy == "Progressive hints":
            lines.append(copy["hint_progressive"])
        elif hint_strategy == "Guided questions":
            lines.append(copy["hint_guided"])
        elif hint_strategy == "Worked example first":
            lines.append(copy["hint_example"])
        else:
            lines.append(copy["hint_on_request"])

        if style == "Socratic (ask me questions)" and ask_follow_up:
            lines.extend(["", copy["socratic"]])
        elif style == "Direct and concise":
            lines.append(copy["direct"])
        elif style == "Detailed instructor" and depth == "In-depth":
            lines.append(copy["detailed"])
        elif style == "Adaptive" and depth != "Brief":
            lines.append(copy["brief"] if overall_accuracy < 60 else copy["direct"])

        if everyday_examples and not lesson_scope:
            lines.append(copy["everyday"])
        if use_reasoning:
            lines.append(copy["reasoning"])
        if check_calculations:
            lines.append(copy["calculation"])

        if depth == "In-depth":
            lines.extend(["", copy["course_breakdown"]])
            for item in attempted:
                lines.append(
                    f"- {item['topic_label']}: {item['correct_answers']}/"
                    f"{item['questions_attempted']} ({item['accuracy']:.0f}%)"
                )
            lines.append(copy["interpret"])

        if show_sources:
            lines.append(copy["evidence"])

        if show_uncertainty:
            lines.append(copy["uncertain"])
        else:
            lines.append(copy["brief_uncertain"])

        if lesson_scope:
            lines.append(copy["scope"].format(course=weakest["topic_label"]))
        else:
            lines.append(copy["broad_scope"])

    # Preference and capability controls are surfaced honestly. Settings that
    # need a hosted model, web access, or image processing must not be implied
    # to work inside this deterministic local summary.
    if preferences.get("ai_preview_remember_preferences", True):
        lines.append(copy["memory_on"])
    else:
        lines.append(copy["memory_off"])
    if not preferences.get("ai_preview_context_permission", True):
        lines.append(copy["context_off"])
    if not preferences.get("ai_preview_age_appropriate", True):
        lines.append(copy["safety"])

    if preferences.get("ai_preview_memory_review", True):
        lines.extend([
            "",
            copy["settings"],
            f"- {copy['teaching']}: {style}",
            f"- {copy['depth']}: {depth}",
            f"- {copy['hint']}: {hint_strategy}",
            f"- {copy['correction']}: {correction}",
            f"- {copy['challenge']}: {challenge}",
            f"- {copy['language']}: {language}",
            f"- {copy['format']}: {format_style}",
        ])

    lines.extend(["", copy["limits"], copy["footer"]])

    return _format_progress_summary(lines, format_style, copy["exam_heading"])


def _recommend_next_step(progress, weakest_stat):
    """Recommend the next incomplete lesson in the weakest recorded course."""
    course_id = weakest_stat["course_id"]
    course = data.get_course(course_id)
    lesson = next_incomplete_lesson(progress, course_id)
    if lesson is not None:
        return f"Complete the “{lesson['title']}” lesson in {course['topic_label']}."
    return f"Revisit the {course['topic_label']} lessons for extra practice."


def _format_local_summary(body, format_style, language):
    """Retain the legacy empty-state formatter for older internal callers."""
    if language not in {"Match lesson language", "English"}:
        body += (
            f"\n\nLanguage preference saved: {language}. "
            "This prototype currently generates the local progress summary in English."
        )
    if format_style == "Bullet points":
        body = "\n".join(
            f"- {line}" if line and not line.startswith("- ") else line
            for line in body.splitlines()
        )
    elif format_style == "Short paragraphs":
        body = " ".join(line.strip() for line in body.splitlines() if line.strip())
    return _wrap_summary(body)


def _wrap_summary(body):
    """Apply the standard product title to a locally generated summary."""
    return "Vocogni Learning Summary — Prototype\n\n" + body


# ---------------------------------------------------------------------------
# Optional answer-feedback sounds — generated with the standard library only.
# They are short, low-volume cues, and are never required for scoring.
# ---------------------------------------------------------------------------

def _generate_beep_wav_bytes(frequency=880.0, duration_ms=150, volume=0.25, sample_rate=22050):
    """Keep the original simple beep generator available for compatibility."""
    n_samples = int(sample_rate * duration_ms / 1000)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()
        for i in range(n_samples):
            t = i / sample_rate
            fade = 1.0 - (i / n_samples)
            sample = volume * fade * math.sin(2 * math.pi * frequency * t)
            frames += struct.pack("<h", int(sample * 32767))
        wf.writeframes(bytes(frames))
    return buf.getvalue()


def _feedback_tone(age, duration, frequency, decay=13.0):
    """Return a soft, quickly-attacked sine tone with an exponential decay."""
    if age < 0 or age >= duration:
        return 0.0
    attack = min(1.0, age / 0.006)
    release = max(0.0, 1.0 - age / duration) ** 1.5
    return math.sin(2 * math.pi * frequency * age) * attack * release * math.exp(-decay * age * 0.12)


def _generate_feedback_wav_bytes(kind, sample_rate=22050):
    """Synthesize a short, volume-limited cue for correct or incorrect answers."""
    is_correct = kind == "correct"
    duration = 0.30 if is_correct else 0.24
    volume = 0.20 if is_correct else 0.14
    n_samples = int(sample_rate * duration)
    buf = io.BytesIO()

    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        frames = bytearray()

        for index in range(n_samples):
            t = index / sample_rate
            if is_correct:
                # Low, rounded note with upward harmonics: a compact bass-chime.
                sample = (
                    0.46 * _feedback_tone(t, 0.245, 174.61, 9.0)
                    + 0.27 * _feedback_tone(t - 0.022, 0.205, 349.23, 11.0)
                    + 0.17 * _feedback_tone(t - 0.052, 0.165, 523.25, 13.0)
                    + 0.06 * _feedback_tone(t - 0.064, 0.105, 1046.50, 15.0)
                )
            else:
                # A restrained, descending double bell with metallic partials.
                sample = (
                    0.47 * _feedback_tone(t, 0.19, 880.00, 6.0)
                    + 0.17 * _feedback_tone(t, 0.16, 1760.00, 6.0)
                    + 0.42 * _feedback_tone(t - 0.065, 0.17, 698.46, 7.0)
                    + 0.13 * _feedback_tone(t - 0.065, 0.14, 1396.92, 7.0)
                )
            # Keep peak amplitude comfortably below full scale to reduce harshness.
            sample = max(-0.32, min(0.32, sample * volume))
            frames += struct.pack("<h", int(sample * 32767))

        wf.writeframes(bytes(frames))
    return buf.getvalue()


def get_correct_answer_beep_base64():
    """Base64 WAV for the optional warm bass-and-chime correct-answer cue."""
    return base64.b64encode(_generate_feedback_wav_bytes("correct")).decode("ascii")


def get_wrong_answer_beep_base64():
    """Base64 WAV for the optional descending-bell incorrect-answer cue."""
    return base64.b64encode(_generate_feedback_wav_bytes("incorrect")).decode("ascii")
