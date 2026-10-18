"""Progress-page Coach: targeted practice and descriptive improvement tracking."""
from __future__ import annotations

import random
import re

import streamlit as st

import data
import logic
import state


MESSAGE_BANK = {
    "zero": [
        "Great job — you haven't made a mistake in this practice set. Keep it up.",
        "Clean run. You're ready to stretch the same skill a little further.",
        "Excellent accuracy. Use these warm-up questions to keep the skill sharp.",
    ],
    "low": [
        "A small number of errors is useful feedback. Let's target the exact skill.",
        "You're close. A little focused practice can make this more reliable.",
        "Good progress. These questions will help reinforce the step that slipped.",
    ],
    "medium": [
        "Some steps need more practice. Work carefully and check each move.",
        "Let's slow down and strengthen the part of this lesson that caused errors.",
        "Mistakes show us where to focus next. Try these targeted questions.",
    ],
    "high": [
        "Let's rebuild this skill one step at a time. Accuracy matters more than speed.",
        "This topic needs another pass. Use each question to practise the core method.",
        "Start with the fundamentals, then build up. You can improve through deliberate practice.",
    ],
    "new": [
        "Start with a few warm-up questions to establish a baseline.",
        "Let's check the basics first, then use your answers to guide practice.",
        "Try these questions at your own pace. Focus on the method, not speed.",
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
    questions = []
    for lesson in lessons:
        for question in lesson.get("questions", []):
            if question.get("type") in ("mc", "numeric") and question.get("prompt"):
                questions.append((lesson, question))
    return questions


def _randomized_question(course_id, lesson_id, index):
    """Reuse authored questions; safely vary integer coefficients for clean factorization."""
    candidates = _lesson_candidates(course_id, lesson_id)
    if not candidates:
        candidates = _lesson_candidates(course_id)
    if not candidates:
        return None

    lesson, original = random.choice(candidates)
    question = dict(original)
    question["options"] = list(original.get("options", []))
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


def render(progress):
    st.markdown("### Coach")
    st.caption("Focused practice for this lesson. Questions are drawn from your course content; generated variants are used only when their answers are unambiguous.")

    courses = data.all_courses_in_order()
    if not courses:
        st.info("No courses are available yet.")
        return

    labels = {course["topic_label"]: course["id"] for course in courses}
    selected_label = st.selectbox("Coach topic", list(labels), key="coach_course")
    course_id = labels[selected_label]
    course = data.get_course(course_id)
    course_progress = progress.setdefault(course_id, {})
    diagnostic_records = course_progress.get("diagnostics", {})
    lesson_options = [(lesson["id"], lesson["title"]) for lesson in course.get("lessons", [])]
    if not lesson_options:
        st.info("This course has no lessons to practise yet.")
        return

    lesson_titles = {title: lesson_id for lesson_id, title in lesson_options}
    selected_title = st.selectbox("Focus lesson", list(lesson_titles), key="coach_lesson")
    lesson_id = lesson_titles[selected_title]

    lesson_record = diagnostic_records.get(lesson_id, {}) if isinstance(diagnostic_records, dict) else {}
    baseline_mistakes = max(0, int(lesson_record.get("total", 0) or 0) - int(lesson_record.get("score", 0) or 0))
    baseline_attempted = int(lesson_record.get("total", 0) or 0)
    band = _error_band(baseline_attempted, baseline_mistakes)
    attempts_key = f"coach_attempts_{course_id}_{lesson_id}"
    question_index = int(st.session_state.get(attempts_key, 0))
    messages = MESSAGE_BANK[band]
    st.markdown(f"**{messages[question_index % len(messages)]}**")
    st.write("Here are some focused warm-up questions." if band in ("zero", "new") else "Let's practise the skill behind the errors.")

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
            if is_correct:
                coach_data["correct_answers"] = int(coach_data.get("correct_answers", 0)) + 1
                st.success("Correct. Keep going.")
            else:
                coach_data["total_mistakes"] = int(coach_data.get("total_mistakes", 0)) + 1
                st.error("Not quite. Review the method, then try another question.")
                if question.get("explanation"):
                    st.write(question["explanation"])
            st.session_state[attempts_key] = question_index + 1
            state.mark_persistent_dirty()
            state.flush_persistent_save()
            st.rerun()

    coach_data = course_progress.get("coach", {})
    st.markdown("#### Coaching data")
    cols = st.columns(3)
    with cols[0]:
        st.metric("Questions attempted", int(coach_data.get("questions_attempted", 0)))
    with cols[1]:
        st.metric("Correct answers", int(coach_data.get("correct_answers", 0)))
    with cols[2]:
        st.metric("Total mistakes", int(coach_data.get("total_mistakes", 0)))
    _render_improvement(progress, course_id, lesson_id)
