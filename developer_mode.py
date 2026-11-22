"""Local-only synthetic data for testing Vocogni's complete learning workflow.

The generated learner is fictional. Evidence is built from the current verified
question catalogue, so Adaptive Learning reads it through the same provenance
checks used for real practice records.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any


_PRACTICE_PATTERNS = (
    (False, False, False, True, True, True),
    (False, False, False, False, True, False),
    (True, True, False, True, True, True),
)

_PREFERRED_SKILLS = (
    "math.number.fraction_representation",
    "math.number.fraction_operations",
    "math.algebra.linear_equations",
)


def _empty_course_progress() -> dict[str, Any]:
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


def build_synthetic_learner_state() -> dict[str, Any]:
    """Build a full local-only learner bundle with verified adaptive evidence."""
    import data
    import question_engine
    from settings_model import DEFAULT_SETTINGS
    from streak_garden.models import default_garden_state

    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in question_engine.iter_question_records():
        if not isinstance(record, dict) or record.get("verification_status") != "verified":
            continue
        metadata = record.get("metadata")
        if not isinstance(metadata, dict):
            continue
        skill_id = metadata.get("skill_id")
        if isinstance(skill_id, str) and skill_id.strip():
            grouped[skill_id].append(record)

    chosen_skills = [skill for skill in _PREFERRED_SKILLS if grouped.get(skill)]
    if len(chosen_skills) < 2:
        chosen_skills.extend(
            skill for skill in sorted(grouped)
            if skill not in chosen_skills
        )
    chosen_skills = chosen_skills[:3]
    if len(chosen_skills) < 2:
        raise RuntimeError(
            "The current verified question catalogue has too few skills to build the sample."
        )

    progress = {
        course_id: _empty_course_progress()
        for course_id in data.COURSE_ORDER
    }
    now = datetime.now(timezone.utc)

    for skill_index, skill_id in enumerate(chosen_skills):
        records = grouped[skill_id]
        pattern = _PRACTICE_PATTERNS[skill_index]
        for attempt_index, correct in enumerate(pattern):
            record = records[attempt_index % len(records)]
            course_id = str(record["course_id"])
            lesson_id = str(record["lesson_id"])
            question_id = str(record["question_id"])
            question = record["question"]
            provenance = question_engine.attempt_metadata(
                question_id,
                course_id=course_id,
                lesson_id=lesson_id,
            )
            result = dict(provenance)
            result.update({
                "question_id": question_id,
                "course_id": course_id,
                "lesson_id": lesson_id,
                "verification_status": "verified",
                "question_version": question.get("question_version", 1),
                "skill_id": skill_id,
                "correct": bool(correct),
                "mistake_tag": (
                    question.get("mistake_tag")
                    or question.get("skill_tag")
                    or "Sample practice error"
                ),
            })
            completed_at = now - timedelta(days=len(pattern) - attempt_index)
            course_progress = progress[course_id]
            course_progress["started"] = True
            course_progress["questions_attempted"] += 1
            course_progress["correct_answers"] += int(correct)
            if not correct:
                tag = str(result["mistake_tag"])
                course_progress["mistakes"][tag] = (
                    course_progress["mistakes"].get(tag, 0) + 1
                )
            course_progress["practice_attempts"].setdefault(lesson_id, []).append({
                "attempt_id": f"local-sample-{skill_index}-{attempt_index}",
                "completed_at": completed_at.isoformat(),
                "results": [result],
            })

    # Add one synthetic entry diagnostic where the authored course bank exposes
    # the expected structure. Adaptive Learning still validates the skill tags.
    diagnostic_added = False
    for course in data.all_courses_in_order():
        for lesson in course.get("lessons", []):
            diagnostic = lesson.get("diagnostic")
            questions = diagnostic.get("questions", []) if isinstance(diagnostic, dict) else []
            if not isinstance(questions, list):
                continue
            answer_review = []
            weaknesses = []
            for index, question in enumerate(questions[:5]):
                if not isinstance(question, dict):
                    continue
                skill_tag = question.get("skill_tag") or question.get("mistake_tag")
                if not isinstance(skill_tag, str) or not skill_tag.strip():
                    continue
                correct = index >= 3
                answer_review.append({
                    "question_id": question.get("id"),
                    "skill_tag": skill_tag,
                    "correct": correct,
                })
                if not correct:
                    weaknesses.append({"skill_tag": skill_tag})
            if not answer_review:
                continue
            total = len(answer_review)
            score = sum(1 for item in answer_review if item["correct"])
            course_progress = progress[str(course["id"])]
            course_progress["diagnostics"][str(lesson["id"])] = {
                "score": score,
                "total": total,
                "percent": round(score / total * 100),
                "outcome_label": "Synthetic developer baseline",
                "completed_at": now.isoformat(),
                "answer_review": answer_review,
                "weaknesses": weaknesses,
            }
            diagnostic_added = True
            break
        if diagnostic_added:
            break

    profile = {
        "name": "Synthetic Developer Learner",
        "age": "",
        "gender": "Prefer not to say",
        "grade": "Grade 8",
        "country": "",
        "timezone": "Prefer not to say",
        "favorite_subjects": ["Mathematics"],
        "learning_goals": "Synthetic profile for local developer testing.",
        "strong_subjects": [],
        "weak_subjects": [],
        "interests": "Testing learning workflows",
        "career_interests": "",
        "description": "Synthetic developer data. Not a real learner record.",
        "vocoins": 0,
        "learning_style": "Prefer not to say",
        "preferred_difficulty": "Adaptive",
        "preferred_session_length": "Prefer not to say",
        "preferred_feedback_style": "Prefer not to say",
        "preferred_language": "English",
        "saved": True,
    }
    settings = dict(DEFAULT_SETTINGS)
    settings.update({
        "personalized_progress_recommendations": True,
        "ai_share_learning_summary": False,
        "ai_share_recent_chat_history": False,
        "learning_data_choices_reviewed": True,
        "tutorial_completed": True,
    })

    return {
        "profile": profile,
        "progress": progress,
        "notes": [{
            "id": 1,
            "title": "Developer test note",
            "content": "This note is synthetic and exists to test Notes and local saving.",
            "folder_id": None,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }],
        "whiteboards": [],
        "note_folders": [],
        "next_note_folder_id": 1,
        "milestones": [],
        "next_milestone_id": 1,
        "settings": settings,
        "streak_garden": default_garden_state(),
        "next_note_id": 2,
    }

def is_synthetic_learner_state(learner_state: Any) -> bool:
    """Detect this module's sample profile, including partially edited samples.

    The backup file is the authoritative active-mode marker for newly loaded
    samples. These content markers support cleanly exiting samples created by
    older versions that did not preserve the previous workspace.
    """
    if not isinstance(learner_state, dict):
        return False

    profile = learner_state.get("profile")
    if isinstance(profile, dict):
        if (
            profile.get("name") == "Synthetic Developer Learner"
            or profile.get("description") == "Synthetic developer data. Not a real learner record."
        ):
            return True

    notes = learner_state.get("notes")
    if isinstance(notes, list) and any(
        isinstance(note, dict) and note.get("title") == "Developer test note"
        for note in notes
    ):
        return True

    progress = learner_state.get("progress")
    if isinstance(progress, dict):
        for course_progress in progress.values():
            if not isinstance(course_progress, dict):
                continue
            diagnostics = course_progress.get("diagnostics")
            if isinstance(diagnostics, dict) and any(
                isinstance(item, dict)
                and item.get("outcome_label") == "Synthetic developer baseline"
                for item in diagnostics.values()
            ):
                return True
            attempts_by_lesson = course_progress.get("practice_attempts")
            if isinstance(attempts_by_lesson, dict):
                for attempts in attempts_by_lesson.values():
                    if isinstance(attempts, list) and any(
                        isinstance(attempt, dict)
                        and str(attempt.get("attempt_id", "")).startswith("local-sample-")
                        for attempt in attempts
                    ):
                        return True

    return False
