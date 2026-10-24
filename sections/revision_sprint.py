"""Course-detail UI for the Personalized Revision Sprint."""

from __future__ import annotations

from collections import defaultdict

import streamlit as st

import revision_sprint as sprint_logic
import state


_SESSION_KEY = "personalized_revision_sprint"


def render(course, progress):
    """Render a small, personalized revision session beneath course lessons."""
    course_id = course.get("id")
    if not course_id:
        return

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3>Personalized Revision Sprint</h3>", unsafe_allow_html=True)
    st.caption(
        "A short revision set built from this course's existing questions. "
        "It prioritizes skills that need practice, gives answer feedback, and "
        "records results in your learning history."
    )

    bank = sprint_logic.question_bank_for_course(course_id)
    if len(bank) < 3:
        st.info(
            "This course does not yet have three supported practice questions "
            "for a revision sprint. Continue with the lesson practice while the "
            "question bank is expanded."
        )
        return

    session = st.session_state.get(_SESSION_KEY)
    if isinstance(session, dict) and session.get("course_id") != course_id:
        st.session_state.pop(_SESSION_KEY, None)
        session = None

    if not isinstance(session, dict):
        _render_setup(course, progress, bank)
    elif session.get("stage") == "active":
        _render_active(session, progress)
    elif session.get("stage") == "results":
        _render_results(session)
    else:
        st.session_state.pop(_SESSION_KEY, None)
        _render_setup(course, progress, bank)


def _render_setup(course, progress, bank):
    course_id = course["id"]
    available_counts = [count for count in (3, 5, 10) if count <= len(bank)]
    count = st.selectbox(
        "Questions in this sprint",
        options=available_counts,
        format_func=lambda value: f"{value}-question sprint",
        key=f"revision_sprint_count_{course_id}",
    )
    mode_label = st.radio(
        "Question selection",
        options=[
            "Personalized — focus on weak skills and previous mistakes",
            "Whole course — mix questions across lessons",
        ],
        key=f"revision_sprint_mode_{course_id}",
    )

    weak_skills = sprint_logic.weak_skills_for_course(progress, course_id, limit=3)
    if weak_skills:
        st.caption("Current priority skills: " + " · ".join(weak_skills))
    else:
        st.caption(
            "No clear weak-skill pattern is recorded yet. The personalized sprint "
            "will prioritize unanswered questions and broaden coverage."
        )

    st.caption(
        f"This course currently provides {len(bank)} supported questions. "
        "The sprint uses authored course content and the existing marking rules; "
        "it is not an official mock exam or a predicted school grade."
    )

    if st.button(
        "Build my revision sprint",
        type="primary",
        key=f"revision_sprint_start_{course_id}",
        use_container_width=True,
    ):
        mode = "balanced" if mode_label.startswith("Whole course") else "personalized"
        questions = sprint_logic.select_questions(
            progress,
            course_id,
            count=count,
            mode=mode,
        )
        sequence = int(st.session_state.get("_revision_sprint_sequence", 0)) + 1
        st.session_state["_revision_sprint_sequence"] = sequence
        st.session_state[_SESSION_KEY] = {
            "session_id": f"{course_id}_{sequence}",
            "course_id": course_id,
            "course_title": course.get("title", course_id),
            "mode": mode,
            "stage": "active",
            "items": questions,
            "answer_keys": [
                f"revision_sprint_answer_{course_id}_{sequence}_{index}"
                for index in range(len(questions))
            ],
        }
        st.rerun()


def _answer_widget(question, label, key):
    question_type = question.get("type")
    if question_type == "mc":
        return st.radio(
            label,
            options=question.get("options", []),
            index=None,
            key=key,
        )
    if question_type == "open_ended":
        st.caption(
            f"Mark allocation: {question.get('max_marks', 1)}. "
            "Show the relevant reasoning, method, or calculation."
        )
        return st.text_area(
            label,
            key=key,
            height=115,
            placeholder="Write your answer and working.",
        )

    step = 1.0 if question.get("whole_number") else 0.1
    return st.number_input(
        label,
        value=None,
        step=step,
        format="%g",
        key=key,
    )


def _render_active(session, progress):
    items = session.get("items", [])
    if not items:
        st.warning("No supported questions were selected. Build a new sprint.")
        if st.button("Return to sprint setup", key=f"revision_sprint_empty_{session['session_id']}"):
            st.session_state.pop(_SESSION_KEY, None)
            st.rerun()
        return

    with st.form(
        f"revision_sprint_form_{session['session_id']}",
        clear_on_submit=False,
    ):
        st.markdown(f"**{session.get('course_title', 'Course')} · {len(items)} questions**")
        for index, item in enumerate(items):
            question = item["question"]
            st.markdown(f"**Question {index + 1} of {len(items)}**")
            st.caption(f"{item['skill']} · {item['lesson_title']}")
            st.write(question.get("prompt", "Practice question"))
            _answer_widget(
                question,
                "Your answer",
                session["answer_keys"][index],
            )
            if index < len(items) - 1:
                st.markdown("---")

        submitted = st.form_submit_button(
            "Mark my sprint",
            type="primary",
            use_container_width=True,
        )

    if not submitted:
        return

    graded_items = []
    unanswered = []
    for index, item in enumerate(items):
        answer = st.session_state.get(session["answer_keys"][index])
        if answer is None or (isinstance(answer, str) and not answer.strip()):
            unanswered.append(index + 1)
            continue
        evaluation = sprint_logic.evaluate_question(item["question"], answer)
        graded_items.append({
            "item": item,
            "answer": answer,
            "evaluation": evaluation,
        })

    if unanswered:
        st.warning(
            "Answer every question before submitting. Still blank: "
            + ", ".join(str(index) for index in unanswered)
            + "."
        )
        return

    summary = sprint_logic.record_sprint_attempt(
        st.session_state.progress,
        session["course_id"],
        graded_items,
    )
    state.mark_persistent_dirty()
    save_ok = state.flush_persistent_save()

    session["stage"] = "results"
    session["graded_items"] = graded_items
    session["summary"] = summary
    session["save_confirmed"] = bool(save_ok)
    st.session_state[_SESSION_KEY] = session
    st.rerun()


def _render_results(session):
    summary = session.get("summary", {})
    graded_items = session.get("graded_items", [])

    st.markdown("#### Your revision results")
    if session.get("save_confirmed"):
        st.success("Your sprint result and practice evidence were saved.")
    else:
        st.error(
            "Your result is visible, but saving was not confirmed. Check your "
            "connection and use the app's save status before leaving."
        )

    score = summary.get("marks_awarded", 0)
    maximum = summary.get("max_marks", 0)
    percent = summary.get("percent", 0)
    columns = st.columns(3)
    with columns[0]:
        st.metric("Practice score", f"{score} / {maximum}", f"{percent}% of available marks")
    with columns[1]:
        st.metric("Full-credit answers", f"{summary.get('full_credit_answers', 0)} / {summary.get('questions', 0)}")
    with columns[2]:
        st.metric("Question count", summary.get("questions", 0))

    st.caption(
        "This score describes this sprint only. It is not an official exam mark, "
        "a guarantee of improvement, or a prediction of your school grade."
    )

    skill_totals = defaultdict(lambda: {"score": 0, "maximum": 0, "questions": 0})
    for entry in graded_items:
        skill = entry["item"]["skill"]
        evaluation = entry["evaluation"]
        skill_totals[skill]["score"] += int(evaluation["score"])
        skill_totals[skill]["maximum"] += int(evaluation["max_marks"])
        skill_totals[skill]["questions"] += 1

    if skill_totals:
        skill_rows = sorted(
            skill_totals.items(),
            key=lambda row: (
                row[1]["score"] / row[1]["maximum"] if row[1]["maximum"] else 0,
                row[0].casefold(),
            ),
        )
        st.markdown("**Focus next**")
        for skill, totals in skill_rows[:3]:
            skill_percent = round(totals["score"] / totals["maximum"] * 100) if totals["maximum"] else 0
            st.write(
                f"- **{skill}** — {skill_percent}% "
                f"({totals['score']}/{totals['maximum']} marks)"
            )

    st.markdown("#### Answer review")
    for index, entry in enumerate(graded_items):
        item = entry["item"]
        question = item["question"]
        evaluation = entry["evaluation"]
        ratio = evaluation["score"] / evaluation["max_marks"] if evaluation["max_marks"] else 0
        outcome = (
            "Full credit"
            if evaluation["correct"]
            else "Partial credit"
            if ratio > 0
            else "Needs review"
        )
        with st.expander(
            f"Question {index + 1}: {outcome} · {item['skill']}",
            expanded=not evaluation["correct"],
        ):
            st.write(question.get("prompt", "Practice question"))
            st.write("**Your answer:**", entry["answer"])
            st.write(
                f"**Result:** {evaluation['score']} / "
                f"{evaluation['max_marks']} marks"
            )

            marking = evaluation.get("marking_result")
            if question.get("type") == "open_ended":
                missed_points = (marking or {}).get("missed_points", [])
                if missed_points:
                    st.markdown("**Marking points to strengthen**")
                    for point in missed_points:
                        st.write("- " + str(point.get("criteria", "Review this criterion")))
                        if point.get("feedback"):
                            st.caption(point["feedback"])
            elif not evaluation["correct"]:
                st.write("**Expected answer:**", question.get("answer", "Not configured"))

            explanation = question.get("explanation")
            if explanation:
                st.write("**Why:**", explanation)

            st.caption(
                f"Related skill: {item['skill']} · "
                f"Course lesson: {item['lesson_title']}"
            )

    review_candidate = min(
        graded_items,
        key=lambda entry: (
            entry["evaluation"]["score"] / entry["evaluation"]["max_marks"]
            if entry["evaluation"]["max_marks"] else 0,
            entry["evaluation"]["correct"],
        ),
    )
    review_item = review_candidate["item"]
    review_col, new_col = st.columns(2)
    with review_col:
        if st.button(
            f"Review: {review_item['lesson_title']}",
            type="primary",
            key=f"revision_sprint_review_{session['session_id']}",
            use_container_width=True,
        ):
            st.session_state.nav = "Browse"
            st.session_state.current_course = session["course_id"]
            st.session_state.current_lesson = review_item["lesson_id"]
            st.session_state.lesson_flow = state.new_lesson_flow(
                session["course_id"],
                review_item["lesson_id"],
            )
            st.rerun()
    with new_col:
        if st.button(
            "Build another sprint",
            key=f"revision_sprint_again_{session['session_id']}",
            use_container_width=True,
        ):
            st.session_state.pop(_SESSION_KEY, None)
            st.rerun()
