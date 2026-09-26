"""sections/course.py — Course detail + interactive lesson flow.

Covers spec sections 7 (Course View), 8 (Interactive Learning), and
9 (Real-World Application). A lesson moves through four stages, tracked in
st.session_state.lesson_flow:

    intro -> question -> feedback -> complete
                 ^___________|
           (loops per question)

When Settings > Feedback is "After submission" the feedback stage is
skipped per-question and a combined results summary is shown once, at the
complete stage, instead.
"""

import streamlit as st

import data
import logic
import state


def render_course_detail():
    course_id = st.session_state.current_course
    course = data.get_course(course_id)
    if course is None:
        st.session_state.current_course = None
        st.rerun()
        return

    progress = st.session_state.progress
    pct = logic.course_lesson_progress_percent(progress, course_id)

    if st.button("\u2190 Back to courses"):
        st.session_state.current_course = None
        st.rerun()

    st.markdown(f"<h2>{course['title']}</h2>", unsafe_allow_html=True)
    st.markdown(f"<p class='vc-muted'>{course['short_description']}</p>", unsafe_allow_html=True)
    st.progress(pct)
    st.markdown(f"<span class='vc-muted'>{pct}% complete</span>", unsafe_allow_html=True)

    st.markdown("<h3 style='margin-top:1.3rem;'>Lessons</h3>", unsafe_allow_html=True)

    prog = progress.get(course_id, {})
    completed = set(prog.get("completed_lessons", []))
    next_lesson = logic.next_incomplete_lesson(progress, course_id)
    next_lesson_id = next_lesson["id"] if next_lesson else None

    for idx, lesson in enumerate(course["lessons"]):
        _render_lesson_row(course_id, lesson, idx, progress, completed, next_lesson_id)

    if next_lesson is None:
        st.markdown(
            "<div class='vc-card' style='margin-top:0.5rem;'>You've completed "
            "every lesson in this course. Check the Progress page for a full "
            "breakdown of how you did.</div>",
            unsafe_allow_html=True,
        )


def _render_lesson_row(course_id, lesson, idx, progress, completed, next_lesson_id):
    unlocked = logic.is_lesson_unlocked(progress, course_id, idx)
    is_done = lesson["id"] in completed
    is_current = lesson["id"] == next_lesson_id

    row_class = "vc-lesson-row"
    if not unlocked:
        row_class += " vc-lesson-row--locked"
    elif is_current:
        row_class += " vc-lesson-row--current"

    if is_done:
        status_text = "\u2713 Completed"
    elif not unlocked:
        status_text = "\U0001F512 Locked \u2014 finish the previous lesson first"
    elif is_current:
        status_text = "Up next"
    else:
        status_text = ""

    kind_badge = (
        "<span class='vc-badge vc-badge--apply'>Real-World Challenge</span>"
        if lesson["kind"] == "application" else ""
    )

    col_info, col_action = st.columns([3, 1])
    with col_info:
        st.markdown(
            f"<div class='{row_class}'>"
            f"<div><strong>{idx + 1}. {lesson['title']}</strong> {kind_badge}<br>"
            f"<span class='vc-muted'>{status_text}</span></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    with col_action:
        if unlocked:
            label = "Review" if is_done else ("Continue" if is_current else "Start")
            if st.button(label, key=f"lesson_btn_{lesson['id']}", use_container_width=True):
                st.session_state.current_lesson = lesson["id"]
                st.session_state.lesson_flow = state.new_lesson_flow(course_id, lesson["id"])
                st.rerun()
        else:
            st.button("Locked", key=f"locked_btn_{lesson['id']}", disabled=True, use_container_width=True)


# ---------------------------------------------------------------------------
# Lesson flow
# ---------------------------------------------------------------------------

def render_lesson_flow():
    flow = st.session_state.lesson_flow
    if not flow:
        st.session_state.current_lesson = None
        st.rerun()
        return

    course_id = flow["course_id"]
    lesson_id = flow["lesson_id"]
    course = data.get_course(course_id)
    lesson, _ = data.get_lesson(course_id, lesson_id)

    if course is None or lesson is None:
        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None
        st.rerun()
        return

    progress = st.session_state.progress
    prog = progress.get(course_id, {})
    already_done = lesson_id in prog.get("completed_lessons", [])

    if st.button("\u2190 Back to course"):
        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None
        st.rerun()

    st.markdown(f"<span class='vc-muted'>{course['title']}</span>", unsafe_allow_html=True)
    st.markdown(f"<h2>{lesson['title']}</h2>", unsafe_allow_html=True)

    if already_done:
        _render_already_completed(lesson)
        return

    stage = flow["stage"]
    if stage == "intro":
        _render_intro(lesson, flow)
    elif stage == "question":
        _render_question(lesson, flow, course_id)
    elif stage == "feedback":
        _render_feedback(lesson, flow)
    elif stage == "complete":
        _render_complete(course, lesson, flow, course_id)
    else:
        flow["stage"] = "intro"
        st.rerun()


def _box_class(lesson):
    return "vc-challenge-box" if lesson["kind"] == "application" else "vc-summary-box"


def _render_already_completed(lesson):
    st.markdown(f"<div class='{_box_class(lesson)}'>{lesson['explanation']}</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='vc-card'>\u2713 You already completed this lesson. "
        "Practice questions aren't replayed once a lesson is finished \u2014 "
        "head back to the course to pick another lesson.</div>",
        unsafe_allow_html=True,
    )
    if st.button("Back to course", type="primary"):
        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None
        st.rerun()


def _render_intro(lesson, flow):
    st.markdown(f"<div class='{_box_class(lesson)}'>{lesson['explanation']}</div>", unsafe_allow_html=True)
    button_label = "Begin Challenge" if lesson["kind"] == "application" else "Begin Practice"
    if st.button(button_label, type="primary"):
        flow["stage"] = "question"
        flow["q_index"] = 0
        st.rerun()


def _render_question(lesson, flow, course_id):
    questions = lesson["questions"]
    idx = flow["q_index"]
    total = len(questions)
    question = questions[idx]
    settings = st.session_state.settings

    st.markdown(f"<span class='vc-muted'>Question {idx + 1} of {total}</span>", unsafe_allow_html=True)
    st.markdown(f"#### {question['prompt']}")

    answer_key = f"answer_{lesson['id']}_{question['id']}"

    if question["type"] == "mc":
        choice = st.radio("Your answer:", question["options"], index=None, key=answer_key)
        user_answer = choice
        can_submit = choice is not None
    else:
        if settings.get("difficulty") == "Easy" and question.get("input_hint"):
            st.caption(f"Hint: {question['input_hint']}")
        step = 1.0 if question.get("whole_number") else 0.1
        fmt = "%.0f" if question.get("whole_number") else "%.2f"
        user_answer = st.number_input("Your answer:", step=step, format=fmt, key=answer_key)
        can_submit = True

    if st.button("Submit Answer", type="primary", disabled=not can_submit):
        is_correct = logic.check_answer(question, user_answer)
        logic.record_answer(st.session_state.progress, course_id, question, is_correct)

        flow["last_correct"] = is_correct
        flow["last_user_answer"] = user_answer
        flow["results"].append({
            "correct": is_correct,
            "explanation": question["explanation"],
        })

        if settings.get("feedback_timing", "Immediate") == "Immediate":
            flow["stage"] = "feedback"
        elif idx + 1 < total:
            flow["q_index"] = idx + 1
            flow["stage"] = "question"
        else:
            flow["stage"] = "complete"
        st.rerun()


def _render_feedback(lesson, flow):
    questions = lesson["questions"]
    idx = flow["q_index"]
    question = questions[idx]
    is_correct = flow["last_correct"]

    feedback_class = "vc-feedback--correct" if is_correct else "vc-feedback--incorrect"
    headline = "Correct." if is_correct else "Not quite."
    st.markdown(
        f"<div class='vc-feedback {feedback_class}'><strong>{headline}</strong><br>"
        f"{question['explanation']}</div>",
        unsafe_allow_html=True,
    )

    if is_correct and st.session_state.settings.get("sound"):
        _play_beep_once()

    total = len(questions)
    is_last = idx + 1 >= total
    next_label = "Finish Lesson" if is_last else "Next Question"
    if st.button(next_label, type="primary"):
        if is_last:
            flow["stage"] = "complete"
        else:
            flow["q_index"] = idx + 1
            flow["stage"] = "question"
        st.rerun()


def _render_complete(course, lesson, flow, course_id):
    logic.mark_lesson_complete(st.session_state.progress, course_id, lesson["id"])
    settings = st.session_state.settings

    if settings.get("feedback_timing") != "Immediate":
        st.markdown("<h4>Your results</h4>", unsafe_allow_html=True)
        for i, r in enumerate(flow["results"], start=1):
            cls = "vc-feedback--correct" if r["correct"] else "vc-feedback--incorrect"
            mark = "Correct" if r["correct"] else "Incorrect"
            st.markdown(
                f"<div class='vc-feedback {cls}'><strong>Question {i}: {mark}</strong><br>"
                f"{r['explanation']}</div>",
                unsafe_allow_html=True,
            )

    correct_count = sum(1 for r in flow["results"] if r["correct"])
    total_count = len(flow["results"]) or 1
    st.markdown(
        f"<div class='vc-card'><strong>Lesson complete.</strong> You answered "
        f"{correct_count} of {total_count} question{'s' if total_count != 1 else ''} "
        f"correctly.</div>",
        unsafe_allow_html=True,
    )

    progress = st.session_state.progress
    next_lesson = logic.next_incomplete_lesson(progress, course_id)

    col1, col2 = st.columns(2)
    with col1:
        if next_lesson is not None:
            if st.button("Continue to Next Lesson", type="primary", use_container_width=True):
                st.session_state.current_lesson = next_lesson["id"]
                st.session_state.lesson_flow = state.new_lesson_flow(course_id, next_lesson["id"])
                st.rerun()
    with col2:
        if st.button("Back to Course", use_container_width=True):
            st.session_state.current_lesson = None
            st.session_state.lesson_flow = None
            st.rerun()

    if st.button("\U0001F4DD Add a Note About This Lesson", use_container_width=True):
        st.session_state.note_draft_title = f"{course['title']} \u2014 {lesson['title']}"
        st.session_state.selected_note_id = None
        st.session_state.note_editor_open = True
        st.session_state.nav = "Notes"
        st.rerun()


def _play_beep_once():
    try:
        beep_b64 = logic.get_correct_answer_beep_base64()
        st.markdown(
            f'<audio autoplay="true">'
            f'<source src="data:audio/wav;base64,{beep_b64}" type="audio/wav">'
            f'</audio>',
            unsafe_allow_html=True,
        )
    except Exception:
        pass  # Sound is a nice-to-have; never let it break the lesson flow.