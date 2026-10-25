"""Progress-page Coach: targeted practice and descriptive improvement tracking."""
from __future__ import annotations

import random
from datetime import datetime, timezone

import streamlit as st

import data
import logic
import question_engine
import state


MESSAGE_BANK = {
    "zero": [
        "No errors in this set. Try a new example to check whether the method transfers.",
        "All answers in this set were correct. Try a different question to extend the practice.",
        "Your answers were accurate in this set. A varied question can test the same skill in a new context.",
    ],
    "low": [
        "A few errors point to a step worth reviewing. Focus on that step in the next questions.",
        "Most steps are working. Focused practice can help make the method more consistent.",
        "Review the step that caused an error, then practise it in a fresh example.",
    ],
    "medium": [
        "Some steps need more practice. Work carefully and check each part of the method.",
        "Review the step where errors occurred, then check each part of the method.",
        "Errors help identify what to practise next. Use these questions to reinforce that step.",
    ],
    "high": [
        "This skill may need a more gradual review. Start with the core method and build from there.",
        "Review the core method first, then apply it across a few focused questions.",
        "Start with the fundamentals and add complexity as the method becomes more reliable.",
    ],
    "new": [
        "Answer a few questions to establish a starting point.",
        "Check the basics first, then use your answers to guide the next practice set.",
        "Work at a steady pace and focus on applying the method accurately.",
    ],
}


def _lesson_candidates(course_id, lesson_id=None):
    course = data.get_course(course_id)
    if not course:
        return []
    lessons = course.get("lessons", [])
    if lesson_id:
        selected = next((lesson for lesson in lessons if lesson.get("id") == lesson_id), None)
        if selected:
            lessons = [selected]
        else:
            return []

    questions = []
    for lesson in lessons:
        current_lesson_id = lesson.get("id")
        if question_engine.is_vqe_pilot_lesson(course_id, current_lesson_id):
            records = question_engine.select_questions(
                course_id=course_id,
                lesson_id=current_lesson_id,
                verified_only=True,
                include_pathways=True,
            )
            for record in records:
                question = record["question"]
                if question.get("type") in ("mc", "numeric") and question.get("prompt"):
                    questions.append((lesson, question))
            continue

        # Non-pilot lessons retain their existing authored-question behaviour
        # until their content has been reviewed and opted into VQE.
        for question in lesson.get("questions", []):
            if question.get("type") in ("mc", "numeric") and question.get("prompt"):
                questions.append((lesson, question))
    return questions


def _randomized_question(course_id, lesson_id, index):
    """Reuse authored questions; safely vary integer coefficients for clean factorization."""
    candidates = _lesson_candidates(course_id, lesson_id)
    if not candidates and not (
        lesson_id and question_engine.is_vqe_pilot_lesson(course_id, lesson_id)
    ):
        candidates = _lesson_candidates(course_id)
    if not candidates:
        return None

    lesson, original = random.choice(candidates)
    question = dict(original)
    question["options"] = list(original.get("options", []))
    question["_vqe_source_question_id"] = original.get(
        "_vqe_source_question_id", original.get("id")
    )
    prompt = str(question.get("prompt", ""))

    # Generate a fresh, exactly factorable quadratic when the lesson explicitly
    # teaches factoring. Other authored questions are reused with shuffled choices.
    topic = (lesson.get("title", "") + " " + prompt).lower()
    if "factor" in topic and ("quadratic" in topic or "x" in prompt.lower()):
        a, b = random.randint(1, 8), random.randint(1, 8)
        c = a * b
        question["type"] = "mc"
        question["prompt"] = f"Factorise x² + {a + b}x + {c}."
        correct = f"(x + {a})(x + {b})" if a != b else f"(x + {a})²"
        distractors = [
            f"(x - {a})(x - {b})",
            f"(x + {a})(x - {b})",
            f"(x + {a + b})(x + {c})",
        ]
        question["options"] = list(dict.fromkeys([correct] + [item for item in distractors if item != correct]))[:4]
        question["answer"] = correct
        question["explanation"] = f"Find two numbers that multiply to {c} and add to {a + b}: {a} and {b}."
        question["id"] = f"coach_factor_{index}_{a}_{b}"
        question["verification_status"] = "generated_template"
        question["verification_engine_version"] = question_engine.ENGINE_VERSION
    else:
        if question["type"] == "mc" and question["options"]:
            random.shuffle(question["options"])
        question["id"] = f"coach_{index}_{question.get('id', 'question')}"
    question["coach_source_lesson"] = lesson.get("title", "Lesson practice")
    return question


def _error_band(attempted, mistakes):
    if attempted <= 0:
        return "new"
    rate = mistakes / attempted
    if mistakes == 0:
        return "zero"
    if rate <= 0.2:
        return "low"
    if rate <= 0.4:
        return "medium"
    return "high"


def _render_improvement(progress, course_id, lesson_id):
    """Compare existing lesson assessment records; do not claim causal learning gains."""
    course_progress = progress.get(course_id, {})
    diagnostics = course_progress.get("diagnostics", {})
    assessments = course_progress.get("lesson_assessments", {})
    baseline = diagnostics.get(lesson_id, {}) if isinstance(diagnostics, dict) else {}
    post = assessments.get(lesson_id, {}) if isinstance(assessments, dict) else {}

    if baseline and post and isinstance(baseline.get("percent"), (int, float)) and isinstance(post.get("post_practice_percent"), (int, float)):
        delta = post["post_practice_percent"] - baseline["percent"]
        direction = "improved" if delta > 0 else "declined" if delta < 0 else "stayed the same"
        st.caption(
            f"Lesson comparison: performance {direction} by {delta:+.0f} percentage points "
            "from baseline to post-lesson practice. Descriptive comparison only."
        )
        return
    st.caption("Improvement tracking will compare saved diagnostic and post-lesson results when both are available.")


def render(progress, show_heading=True):
    if show_heading:
        st.markdown("### Coach")
    st.caption("Practise a specific lesson with questions from the course. Generated variants are used only when the expected answer is unambiguous.")

    courses = data.all_courses_in_order()
    if not courses:
        st.info("No courses are available yet.")
        return

    labels = {course["topic_label"]: course["id"] for course in courses}
    selected_label = st.selectbox("Course", list(labels), key="coach_course")
    course_id = labels[selected_label]
    course = data.get_course(course_id)
    course_progress = progress.setdefault(course_id, {})
    diagnostic_records = course_progress.get("diagnostics", {})
    lesson_options = [(lesson["id"], lesson["title"]) for lesson in course.get("lessons", [])]
    if not lesson_options:
        st.info("This course has no lessons to practise yet.")
        return

    lesson_titles = {title: lesson_id for lesson_id, title in lesson_options}
    selected_title = st.selectbox("Lesson to practise", list(lesson_titles), key="coach_lesson")
    lesson_id = lesson_titles[selected_title]

    lesson_record = diagnostic_records.get(lesson_id, {}) if isinstance(diagnostic_records, dict) else {}
    baseline_mistakes = max(0, int(lesson_record.get("total", 0) or 0) - int(lesson_record.get("score", 0) or 0))
    baseline_attempted = int(lesson_record.get("total", 0) or 0)
    band = _error_band(baseline_attempted, baseline_mistakes)
    attempts_key = f"coach_attempts_{course_id}_{lesson_id}"
    question_index = int(st.session_state.get(attempts_key, 0))
    messages = MESSAGE_BANK[band]
    st.markdown(f"**{messages[question_index % len(messages)]}**")
    st.write("Start with a short set of warm-up questions." if band in ("zero", "new") else "Focus on the step behind the earlier errors.")

    question = _randomized_question(course_id, lesson_id, question_index)
    if question is None:
        st.info("There are no supported practice questions for this course yet.")
        return

    st.markdown(f"**{question.get('prompt', 'Practice question')}**")
    widget_key = f"coach_answer_{course_id}_{lesson_id}_{question_index}"
    if question.get("type") == "mc":
        answer = st.radio("Choose an answer", question.get("options", []), key=widget_key, index=None)
    else:
        answer = st.number_input("Your answer", key=widget_key, value=None, step=1.0, format="%g")

    if st.button("Check answer", key=f"coach_check_{course_id}_{lesson_id}_{question_index}"):
        if answer is None or (isinstance(answer, str) and not answer.strip()):
            st.warning("Choose or enter an answer first.")
        else:
            is_correct = logic.check_answer(question, answer)
            coach_data = course_progress.setdefault("coach", {
                "questions_attempted": 0,
                "correct_answers": 0,
                "total_mistakes": 0,
            })
            coach_data["questions_attempted"] = int(coach_data.get("questions_attempted", 0)) + 1
            coach_data.setdefault("attempts", []).append({
                "question_id": str(question.get("_vqe_source_question_id", question.get("id", ""))),
                "presented_question_id": str(question.get("id", "")),
                "question_version": question.get("question_version", 1),
                "skill_id": question.get("skill_id"),
                "question_purpose": question.get("purpose"),
                "verification_status": question.get("verification_status", "legacy"),
                "verification_engine_version": question.get(
                    "verification_engine_version", question_engine.ENGINE_VERSION
                ),
                "user_answer": answer,
                "correct": bool(is_correct),
                "completed_at": datetime.now(timezone.utc).isoformat(),
            })
            if is_correct:
                coach_data["correct_answers"] = int(coach_data.get("correct_answers", 0)) + 1
                st.success("Correct. Your answer matches the expected result.")
            else:
                coach_data["total_mistakes"] = int(coach_data.get("total_mistakes", 0)) + 1
                st.error("The answer does not match the expected result. Review the method, then continue.")
                if question.get("explanation"):
                    st.write(question["explanation"])
            st.session_state[attempts_key] = question_index + 1
            state.mark_persistent_dirty()
            if state.flush_persistent_save():
                st.rerun()
            else:
                st.error("Your answer was recorded in this session, but saving failed. It will remain pending for retry.")

    coach_data = course_progress.get("coach", {})
    st.markdown("#### Practice record")
    cols = st.columns(3)
    with cols[0]:
        st.metric("Questions attempted", int(coach_data.get("questions_attempted", 0)))
    with cols[1]:
        st.metric("Correct answers", int(coach_data.get("correct_answers", 0)))
    with cols[2]:
        st.metric("Total mistakes", int(coach_data.get("total_mistakes", 0)))
    _render_improvement(progress, course_id, lesson_id)
