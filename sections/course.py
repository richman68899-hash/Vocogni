"""
sections/course.py — Course detail + interactive lesson flow.

VOCogni Version 1.4.0
- Adds one-time lesson diagnostics and explicit placement results.
- Routes the initial learning path according to diagnostic outcomes.
- Records a separate baseline and post-lesson practice checkpoint.

Covers:
- Course View
- Interactive Learning
- Real-World Application

A lesson moves through four stages:

    intro -> question -> feedback -> complete
                 ^___________|
           (loops per question)

When Settings > Feedback is "After submission", the feedback stage is
skipped per-question and a combined results summary is shown at the
complete stage.

V1.2.0 persistence behavior:
- Durable progress mutations are marked with state.mark_persistent_dirty().
- Answer submission flushes persistence before rerunning the lesson UI.
- Lesson completion is persisted through app.py's end-of-run autosave.
- Navigation-only reruns remain session-only.
- Logout remains a final safety save through app.py.

Important:
    st.rerun() immediately stops the current script execution.
    Therefore, when a durable mutation is followed immediately by a
    required rerun, this module explicitly flushes persistence first.
"""

from __future__ import annotations

from datetime import datetime, timezone

import streamlit as st

import data
import diagnostics
import logic
import state


# ===========================================================================
# PERSISTENCE / RERUN HELPERS
# ===========================================================================

def _rerun_after_persistence() -> None:
    """
    Flush pending durable state before forcing a rerun.

    If persistence fails, do not rerun. Keeping the current execution
    alive allows the save error to remain visible and preserves the
    dirty state for a later retry.
    """

    success = state.flush_persistent_save()

    if success:
        st.rerun()


# ===========================================================================
# COURSE DETAIL
# ===========================================================================

def render_course_detail() -> None:
    """
    Render the selected course and its lesson list.
    """

    course_id = st.session_state.current_course

    course = data.get_course(course_id)

    if course is None:

        st.session_state.current_course = None
        st.rerun()
        return

    progress = st.session_state.progress

    pct = logic.course_lesson_progress_percent(
        progress,
        course_id,
    )

    # -----------------------------------------------------------------------
    # Back to courses
    # -----------------------------------------------------------------------

    if st.button(
        "← Back to courses",
        key="back_to_courses",
    ):

        st.session_state.current_course = None
        st.rerun()

    # -----------------------------------------------------------------------
    # Course heading
    # -----------------------------------------------------------------------

    st.markdown(
        f"<h2>{course['title']}</h2>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<p class='vc-muted'>{course['short_description']}</p>",
        unsafe_allow_html=True,
    )

    st.progress(pct)

    st.markdown(
        f"<span class='vc-muted'>{pct}% complete</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<h3 style='margin-top:1.3rem;'>Lessons</h3>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Lesson state
    # -----------------------------------------------------------------------

    prog = progress.get(
        course_id,
        {},
    )

    completed = set(
        prog.get(
            "completed_lessons",
            [],
        )
    )

    next_lesson = logic.next_incomplete_lesson(
        progress,
        course_id,
    )

    next_lesson_id = (
        next_lesson["id"]
        if next_lesson
        else None
    )

    # -----------------------------------------------------------------------
    # Lesson list
    # -----------------------------------------------------------------------

    for idx, lesson in enumerate(
        course["lessons"]
    ):

        _render_lesson_row(
            course_id,
            lesson,
            idx,
            progress,
            completed,
            next_lesson_id,
        )

    # -----------------------------------------------------------------------
    # Course completed
    # -----------------------------------------------------------------------

    if next_lesson is None:

        st.markdown(
            "<div class='vc-card' style='margin-top:0.5rem;'>"
            "You've completed every lesson in this course. "
            "Check the Progress page for a full breakdown of how you did."
            "</div>",
            unsafe_allow_html=True,
        )


# ===========================================================================
# LESSON ROW
# ===========================================================================

def _render_lesson_row(
    course_id,
    lesson,
    idx,
    progress,
    completed,
    next_lesson_id,
) -> None:
    """
    Render one lesson row.
    """

    unlocked = logic.is_lesson_unlocked(
        progress,
        course_id,
        idx,
    )

    is_done = lesson["id"] in completed

    is_current = lesson["id"] == next_lesson_id

    row_class = "vc-lesson-row"

    if not unlocked:

        row_class += " vc-lesson-row--locked"

    elif is_current:

        row_class += " vc-lesson-row--current"

    # -----------------------------------------------------------------------
    # Status
    # -----------------------------------------------------------------------

    if is_done:

        status_text = "✓ Completed"

    elif not unlocked:

        status_text = (
            "🔒 Locked — finish the previous lesson first"
        )

    elif is_current:

        status_text = "Up next"

    else:

        status_text = ""

    # -----------------------------------------------------------------------
    # Kind badge
    # -----------------------------------------------------------------------

    kind_badge = (
        "<span class='vc-badge vc-badge--apply'>"
        "Real-World Challenge"
        "</span>"
        if lesson["kind"] == "application"
        else ""
    )

    # -----------------------------------------------------------------------
    # Layout
    # -----------------------------------------------------------------------

    col_info, col_action = st.columns(
        [3, 1]
    )

    with col_info:

        st.markdown(
            f"<div class='{row_class}'>"
            f"<div>"
            f"<strong>{idx + 1}. {lesson['title']}</strong> "
            f"{kind_badge}<br>"
            f"<span class='vc-muted'>{status_text}</span>"
            f"</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    with col_action:

        if unlocked:

            label = (
                "Review"
                if is_done
                else (
                    "Continue"
                    if is_current
                    else "Start"
                )
            )

            if st.button(
                label,
                key=f"lesson_btn_{lesson['id']}",
                use_container_width=True,
            ):

                # These are session-only learning-flow changes.
                st.session_state.current_lesson = (
                    lesson["id"]
                )

                st.session_state.lesson_flow = (
                    state.new_lesson_flow(
                        course_id,
                        lesson["id"],
                    )
                )

                st.rerun()

        else:

            st.button(
                "Locked",
                key=f"locked_btn_{lesson['id']}",
                disabled=True,
                use_container_width=True,
            )


# ===========================================================================
# LESSON FLOW
# ===========================================================================

def render_lesson_flow() -> None:
    """
    Render the current lesson flow.
    """

    flow = st.session_state.lesson_flow

    if not flow:

        st.session_state.current_lesson = None
        st.rerun()
        return

    course_id = flow["course_id"]
    lesson_id = flow["lesson_id"]

    course = data.get_course(
        course_id
    )

    lesson, _ = data.get_lesson(
        course_id,
        lesson_id,
    )

    if course is None or lesson is None:

        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None

        st.rerun()
        return

    progress = st.session_state.progress

    prog = progress.get(
        course_id,
        {},
    )

    already_done = (
        lesson_id
        in prog.get(
            "completed_lessons",
            [],
        )
    )

    # -----------------------------------------------------------------------
    # Back to course
    # -----------------------------------------------------------------------

    if st.button(
        "← Back to course",
        key="back_to_course",
    ):

        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None

        st.rerun()

    # -----------------------------------------------------------------------
    # Lesson heading
    # -----------------------------------------------------------------------

    st.markdown(
        f"<span class='vc-muted'>{course['title']}</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"<h2>{lesson['title']}</h2>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # ONE-TIME DIAGNOSTIC + ADAPTIVE PATHWAY
    # -----------------------------------------------------------------------
    #
    # Diagnostic records are durable and keyed by lesson ID. The diagnostic
    # never contributes to ordinary practice accuracy/question counts.
    diagnostic_config = lesson.get("diagnostic")
    diagnostic_records = prog.setdefault("diagnostics", {})
    diagnostic_result = diagnostic_records.get(lesson_id)

    if diagnostic_config and diagnostic_result is None:
        # One-time diagnostic always gates lesson entry, including lessons
        # whose ordinary practice was completed before diagnostics existed.
        _render_diagnostic(lesson, course_id)
        return

    if diagnostic_config and diagnostic_result is not None:
        if not diagnostic_result.get("pathway_started_at"):
            _render_diagnostic_result(lesson, course_id, diagnostic_result)
            return
        unlocked_pathways = diagnostics.unlocked_pathways_for_score(diagnostic_result)
        if not flow.get("active_questions"):
            flow["selected_pathway"] = diagnostic_result.get("outcome_key", "level_1")
            flow["active_questions"] = diagnostics.get_pathway_questions(
                lesson, flow["selected_pathway"]
            )

    # -----------------------------------------------------------------------
    # Stage
    # -----------------------------------------------------------------------
    #
    # IMPORTANT:
    #
    # A lesson can be marked completed while its current flow is still in
    # the "complete" stage. We therefore allow that stage to render even
    # when already_done is True.
    #
    # Without this distinction, the next rerun after completion could jump
    # straight to _render_already_completed() and lose the Continue button.
    # -----------------------------------------------------------------------

    stage = flow.get(
        "stage",
        "intro",
    )

    if already_done and stage != "complete":

        _render_already_completed(
            lesson
        )

        return

    if stage == "intro":

        _render_intro(
            lesson,
            flow,
        )

    elif stage == "question":

        _render_question(
            lesson,
            flow,
            course_id,
        )

    elif stage == "feedback":

        _render_feedback(
            lesson,
            flow,
        )

    elif stage == "complete":

        _render_complete(
            course,
            lesson,
            flow,
            course_id,
        )

    else:

        # Invalid transient state — reset safely.
        flow["stage"] = "intro"
        st.rerun()


# ===========================================================================
# COMPLETED LESSON
# ===========================================================================

def _render_already_completed(
    lesson,
) -> None:
    """
    Render the review screen for a previously completed lesson.
    """

    st.markdown(
        f"<div class='{_box_class(lesson)}'>"
        f"{lesson['explanation']}"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='vc-card'>"
        "✓ You already completed this lesson. "
        "Practice questions aren't replayed once a lesson is finished — "
        "head back to the course to pick another lesson."
        "</div>",
        unsafe_allow_html=True,
    )

    if st.button(
        "Back to course",
        type="primary",
        key="completed_back_to_course",
    ):

        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None

        st.rerun()


# ===========================================================================
# INTRO
# ===========================================================================

def _render_intro(
    lesson,
    flow,
) -> None:
    """Render the lesson introduction and selected diagnostic pathway."""
    selected_pathway = flow.get("selected_pathway")
    diagnostic_config = lesson.get("diagnostic", {})
    if selected_pathway == "prerequisite":
        st.info("Recommended route: prerequisite review")
        st.markdown("#### Review the prerequisite")
        st.write(diagnostic_config.get("prerequisite_review", "Review the required foundation."))
    elif selected_pathway == "project":
        project_intro = diagnostic_config.get("pathways", {}).get("project", {}).get("intro")
        if project_intro:
            st.info("Recommended route: real-life application")
            st.write(project_intro)
    elif selected_pathway in ("level_1", "level_2", "level_3"):
        route_labels = {"level_1": "Level 1 — Easy", "level_2": "Level 2 — Medium", "level_3": "Level 3 — Hard"}
        st.info(f"Recommended route: {route_labels[selected_pathway]}")

    st.markdown(
        f"<div class='{_box_class(lesson)}'>"
        f"{lesson['explanation']}"
        f"</div>",
        unsafe_allow_html=True,
    )

    button_label = (
        "Begin Challenge"
        if selected_pathway == "project" or lesson["kind"] == "application"
        else "Begin Practice"
    )
    if st.button(button_label, type="primary", key="begin_lesson"):
        flow["stage"] = "question"
        flow["q_index"] = 0
        flow["results"] = []
        st.rerun()


# ===========================================================================
# REUSABLE LESSON DIAGNOSTIC
# ===========================================================================

def _render_diagnostic(lesson, course_id) -> None:
    """Collect and save the one-time baseline diagnostic for a configured lesson."""
    config = lesson.get("diagnostic", {})
    errors = diagnostics.validate_diagnostic_config(config)
    if errors:
        st.error("This lesson's diagnostic is not configured correctly.")
        for error in errors:
            st.write(f"- {error}")
        return

    st.markdown("### Test 1 — Diagnostic")
    st.write(
        "Complete this one-time five-question test first. "
        "It is separate from ordinary practice scores and will identify skills "
        "worth reviewing before recommending a learning route."
    )
    answers = {}
    with st.form(f"lesson_diagnostic_{lesson['id']}", clear_on_submit=False):
        for index, question in enumerate(config["questions"], start=1):
            st.markdown(f"**Question {index} of {len(config['questions'])}**")
            st.markdown(f"#### {question['prompt']}")
            st.caption(f"Skill checked: {question['skill_tag']}")
            key = f"diagnostic_answer_{lesson['id']}_{question['id']}"
            if question["type"] == "mc":
                answers[question["id"]] = st.radio(
                    "Choose one answer", question.get("options", []),
                    index=None, key=key,
                )
            else:
                raw = st.text_input("Your answer", key=key)
                if raw.strip():
                    try:
                        number = float(raw.strip())
                        answers[question["id"]] = (
                            int(number) if question.get("whole_number") and number.is_integer() else number
                        )
                    except ValueError:
                        answers[question["id"]] = raw
                else:
                    answers[question["id"]] = None
        submitted = st.form_submit_button(
            "Submit diagnostic", type="primary", use_container_width=True
        )

    if not submitted:
        return

    missing = [
        question["id"] for question in config["questions"]
        if answers.get(question["id"]) is None
        or (isinstance(answers.get(question["id"]), str) and not answers[question["id"]].strip())
    ]
    if missing:
        st.warning("Answer all five questions before submitting. Your diagnostic has not been recorded.")
        return

    prog = state.get_course_progress(course_id)
    records = prog.setdefault("diagnostics", {})
    if lesson["id"] in records:
        st.info("A diagnostic is already recorded for this lesson. It cannot be retaken.")
        return

    try:
        result = diagnostics.evaluate_diagnostic(config, answers)
    except (TypeError, ValueError) as exc:
        st.error(f"Diagnostic could not be scored: {exc}")
        return

    records[lesson["id"]] = result
    prog["started"] = True
    state.mark_persistent_dirty()
    if state.flush_persistent_save():
        st.rerun()
    else:
        st.error(
            "Your result exists in this session, but saving failed. Use Retry save "
            "before refreshing or leaving this lesson; otherwise the one-time result "
            "may not be preserved across sessions."
        )


def _render_diagnostic_result(lesson, course_id, result) -> None:
    """Show score, flagged weaknesses, placement rationale, and the route entry."""
    st.markdown("### Diagnostic results")
    st.metric("Baseline score", f"{result['score']} / {result['total']}", f"{result['percent']}%")
    st.subheader(result["outcome_label"])
    st.write(result["outcome_summary"])
    st.caption(result["placement_reason"])

    weaknesses = result.get("weaknesses", [])
    if weaknesses:
        st.markdown("#### Skills to review")
        for weakness in weaknesses:
            st.markdown(f"- **{weakness['skill_tag']}** — {weakness['recommended_action']}")
    else:
        st.success("No weaknesses were flagged by these five diagnostic items.")

    with st.expander("Review your diagnostic answers"):
        for index, item in enumerate(result.get("answer_review", []), start=1):
            label = "Correct" if item["correct"] else "Needs review"
            st.markdown(f"**{index}. {label} — {item['skill_tag']}**")
            st.caption(item["prompt"])
            st.write(f"Your answer: {item.get('user_answer')}")
            st.write(f"Expected answer: {item.get('expected_answer')}")
            st.write(item["explanation"])

    if result.get("outcome_key") == "prerequisite":
        st.markdown("#### Prerequisite review")
        st.write(lesson.get("diagnostic", {}).get("prerequisite_review", ""))

    unlocked = diagnostics.unlocked_pathways_for_score(result)
    route_labels = {
        "level_1": "Level 1 — Easy",
        "level_2": "Level 2 — Medium",
        "level_3": "Level 3 — Hard",
        "project": "Real-life project",
    }
    st.markdown("#### Unlocked practice tests")
    st.caption("Choose any unlocked route. Higher routes remain locked until the diagnostic score and prerequisite check meet the rule.")
    if not result.get("pathway_started_at"):
        selected = st.selectbox(
            "Practice route",
            options=unlocked,
            format_func=lambda route: route_labels[route],
            key=f"diagnostic_route_choice_{lesson['id']}",
        )
        start_label = "Start selected pathway"
    else:
        selected = result.get("selected_pathway", result.get("outcome_key", "level_1"))
        st.info(f"Your diagnostic is already recorded. Selected route: {route_labels.get(selected, selected)}. You cannot retake the diagnostic.")
        start_label = "Continue selected pathway"
    if st.button(start_label, type="primary", key=f"start_pathway_{lesson['id']}"):
        prog = state.get_course_progress(course_id)
        saved_result = prog.setdefault("diagnostics", {}).get(lesson["id"])
        if not saved_result:
            st.error("The diagnostic result is missing. Please return to the course and reopen the lesson.")
            return
        if selected not in diagnostics.unlocked_pathways_for_score(saved_result):
            st.error("That practice route is not unlocked by the saved diagnostic.")
            return
        saved_result["pathway_started_at"] = datetime.now(timezone.utc).isoformat()
        saved_result["selected_pathway"] = selected
        flow = st.session_state.lesson_flow
        flow["selected_pathway"] = selected
        flow["active_questions"] = diagnostics.get_pathway_questions(lesson, selected)
        flow["stage"] = "intro"
        flow["q_index"] = 0
        flow["results"] = []
        state.mark_persistent_dirty()
        if state.flush_persistent_save():
            st.rerun()
        else:
            st.error("The route could not be saved yet. Use Retry save before leaving this lesson.")


# ===========================================================================
# QUESTION
# ===========================================================================

def _render_question(
    lesson,
    flow,
    course_id,
) -> None:
    """
    Render and process the current question.
    """

    questions = flow.get("active_questions", lesson["questions"])

    idx = flow["q_index"]

    total = len(questions)

    # -----------------------------------------------------------------------
    # Safety checks
    # -----------------------------------------------------------------------

    if not questions:

        flow["stage"] = "complete"
        st.rerun()
        return

    if idx < 0 or idx >= total:

        flow["q_index"] = 0
        flow["stage"] = "question"

        st.rerun()
        return

    question = questions[idx]

    settings = st.session_state.settings

    # -----------------------------------------------------------------------
    # Question heading
    # -----------------------------------------------------------------------

    st.markdown(
        f"<span class='vc-muted'>"
        f"Question {idx + 1} of {total}"
        f"</span>",
        unsafe_allow_html=True,
    )

    st.markdown(
        f"#### {question['prompt']}"
    )

    answer_key = (
        f"answer_{lesson['id']}_{question['id']}"
    )

    # -----------------------------------------------------------------------
    # Answer input
    # -----------------------------------------------------------------------

    if question["type"] == "mc":

        choice = st.radio(
            "Your answer:",
            question["options"],
            index=None,
            key=answer_key,
        )

        user_answer = choice

        can_submit = choice is not None

    else:

        if (
            settings.get("difficulty")
            == "Easy"
            and question.get("input_hint")
        ):

            st.caption(
                f"Hint: {question['input_hint']}"
            )

        step = (
            1.0
            if question.get("whole_number")
            else 0.1
        )

        fmt = (
            "%.0f"
            if question.get("whole_number")
            else "%.2f"
        )

        user_answer = st.number_input(
            "Your answer:",
            step=step,
            format=fmt,
            key=answer_key,
        )

        can_submit = True

    # -----------------------------------------------------------------------
    # Submit answer
    # -----------------------------------------------------------------------

    if st.button(
        "Submit Answer",
        type="primary",
        disabled=not can_submit,
        key=f"submit_answer_{lesson['id']}_{question['id']}",
    ):

        # ---------------------------------------------------------------
        # Calculate correctness
        # ---------------------------------------------------------------

        is_correct = logic.check_answer(
            question,
            user_answer,
        )

        # ---------------------------------------------------------------
        # Update durable learner progress
        # ---------------------------------------------------------------

        logic.record_answer(
            st.session_state.progress,
            course_id,
            question,
            is_correct,
        )

        # ---------------------------------------------------------------
        # IMPORTANT V1.2 AUTOSAVE HOOK
        # ---------------------------------------------------------------
        #
        # record_answer() changes durable learner state:
        # - questions_attempted
        # - correct_answers
        # - mistakes
        #
        # Therefore the persistent state is now dirty.
        # ---------------------------------------------------------------

        state.mark_persistent_dirty()

        # ---------------------------------------------------------------
        # Update transient lesson state
        # ---------------------------------------------------------------

        flow["last_correct"] = is_correct

        flow["last_user_answer"] = user_answer

        flow["results"].append(
            {
                "correct": is_correct,
                "explanation": question["explanation"],
            }
        )

        # ---------------------------------------------------------------
        # Determine next stage
        # ---------------------------------------------------------------

        if (
            settings.get(
                "feedback_timing",
                "Immediate",
            )
            == "Immediate"
        ):

            flow["stage"] = "feedback"

        elif idx + 1 < total:

            flow["q_index"] = idx + 1
            flow["stage"] = "question"

        else:

            flow["stage"] = "complete"

        # ---------------------------------------------------------------
        # IMPORTANT
        #
        # We must persist BEFORE rerun.
        #
        # st.rerun() stops this execution immediately, meaning app.py
        # will not reach its normal end-of-run flush.
        # ---------------------------------------------------------------

        _rerun_after_persistence()


# ===========================================================================
# FEEDBACK
# ===========================================================================

def _render_feedback(
    lesson,
    flow,
) -> None:
    """
    Render immediate feedback for the current question.
    """

    questions = flow.get("active_questions", lesson["questions"])

    idx = flow["q_index"]

    question = questions[idx]

    is_correct = flow["last_correct"]

    feedback_class = (
        "vc-feedback--correct"
        if is_correct
        else "vc-feedback--incorrect"
    )

    headline = (
        "Correct."
        if is_correct
        else "Not quite."
    )

    st.markdown(
        f"<div class='vc-feedback {feedback_class}'>"
        f"<strong>{headline}</strong><br>"
        f"{question['explanation']}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Correct-answer sound
    # -----------------------------------------------------------------------

    if (
        is_correct
        and st.session_state.settings.get(
            "sound"
        )
    ):

        _play_beep_once()

    # -----------------------------------------------------------------------
    # Next question
    # -----------------------------------------------------------------------

    total = len(questions)

    is_last = (
        idx + 1 >= total
    )

    next_label = (
        "Finish Lesson"
        if is_last
        else "Next Question"
    )

    if st.button(
        next_label,
        type="primary",
        key=f"feedback_next_{lesson['id']}_{idx}",
    ):

        if is_last:

            # Transient state only.
            flow["stage"] = "complete"

        else:

            flow["q_index"] = idx + 1
            flow["stage"] = "question"

        st.rerun()


# ===========================================================================
# COMPLETE
# ===========================================================================

def _render_complete(
    course,
    lesson,
    flow,
    course_id,
) -> None:
    """
    Render the lesson-completion screen.

    Lesson completion is a durable mutation.

    It is performed exactly once:
        not completed → mark complete → mark dirty

    The normal app.py end-of-run flush then persists it.
    """

    progress = st.session_state.progress

    prog = progress.get(
        course_id
    )

    if prog is None:

        # Defensive creation in case older/invalid state is encountered.
        prog = state.get_course_progress(
            course_id
        )

    completed_lessons = prog.setdefault(
        "completed_lessons",
        [],
    )

    # -----------------------------------------------------------------------
    # Persist completion exactly once
    # -----------------------------------------------------------------------

    if lesson["id"] not in completed_lessons:

        logic.mark_lesson_complete(
            progress,
            course_id,
            lesson["id"],
        )

        # mark_lesson_complete() changed durable learner state.
        state.mark_persistent_dirty()

    settings = st.session_state.settings

    # -----------------------------------------------------------------------
    # Combined results
    # -----------------------------------------------------------------------

    if settings.get(
        "feedback_timing"
    ) != "Immediate":

        st.markdown(
            "<h4>Your results</h4>",
            unsafe_allow_html=True,
        )

        for i, result in enumerate(
            flow["results"],
            start=1,
        ):

            cls = (
                "vc-feedback--correct"
                if result["correct"]
                else "vc-feedback--incorrect"
            )

            mark = (
                "Correct"
                if result["correct"]
                else "Incorrect"
            )

            st.markdown(
                f"<div class='vc-feedback {cls}'>"
                f"<strong>Question {i}: {mark}</strong><br>"
                f"{result['explanation']}"
                f"</div>",
                unsafe_allow_html=True,
            )

    # -----------------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------------

    correct_count = sum(
        1
        for result in flow["results"]
        if result["correct"]
    )

    total_count = (
        len(flow["results"])
        or 1
    )

    # Store a single descriptive post-lesson checkpoint for comparison with
    # the one-time baseline. This is not claimed to be a validated learning-gain
    # measure because the diagnostic and practice items are not equivalent forms.
    baseline = prog.setdefault("diagnostics", {}).get(lesson["id"])
    assessments = prog.setdefault("lesson_assessments", {})
    if baseline and flow["results"] and lesson["id"] not in assessments:
        post_percent = round(correct_count / len(flow["results"]) * 100)
        assessments[lesson["id"]] = {
            "baseline_score": baseline.get("score", 0),
            "baseline_total": baseline.get("total", 5),
            "baseline_percent": baseline.get("percent", 0),
            "post_correct": correct_count,
            "post_total": len(flow["results"]),
            "post_practice_percent": post_percent,
            "percentage_point_difference": post_percent - baseline.get("percent", 0),
            "pathway": baseline.get("outcome_key", "unknown"),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        state.mark_persistent_dirty()

    question_word = (
        "question"
        if total_count == 1
        else "questions"
    )

    st.markdown(
        f"<div class='vc-card'>"
        f"<strong>Lesson complete.</strong> "
        f"You answered {correct_count} of "
        f"{total_count} {question_word} correctly."
        f"</div>",
        unsafe_allow_html=True,
    )

    assessment = prog.get("lesson_assessments", {}).get(lesson["id"])
    if assessment:
        st.markdown("#### Starting point and practice checkpoint")
        before, after, difference = st.columns(3)
        with before:
            st.metric("Diagnostic baseline", f"{assessment['baseline_score']}/{assessment['baseline_total']}", f"{assessment['baseline_percent']}%")
        with after:
            st.metric("Post-lesson practice", f"{assessment['post_correct']}/{assessment['post_total']}", f"{assessment['post_practice_percent']}%")
        with difference:
            delta = assessment["percentage_point_difference"]
            st.metric("Descriptive difference", f"{delta:+d} pp")
        st.caption(
            "These are descriptive checkpoints, not a validated measure of learning gain: "
            "the diagnostic and lesson-practice questions are different."
        )

    # -----------------------------------------------------------------------
    # Next lesson
    # -----------------------------------------------------------------------

    next_lesson = logic.next_incomplete_lesson(
        progress,
        course_id,
    )

    col1, col2 = st.columns(2)

    with col1:

        if next_lesson is not None:

            if st.button(
                "Continue to Next Lesson",
                type="primary",
                use_container_width=True,
                key="continue_next_lesson",
            ):

                st.session_state.current_lesson = (
                    next_lesson["id"]
                )

                st.session_state.lesson_flow = (
                    state.new_lesson_flow(
                        course_id,
                        next_lesson["id"],
                    )
                )

                # There should normally be nothing pending because the
                # previous completion was flushed at the end of its run.
                # Flush defensively in case a previous save failed.
                state.flush_persistent_save()

                st.rerun()

    with col2:

        if st.button(
            "Back to Course",
            use_container_width=True,
            key="complete_back_to_course",
        ):

            # Defensive flush before leaving the completed lesson.
            state.flush_persistent_save()

            st.session_state.current_lesson = None
            st.session_state.lesson_flow = None

            st.rerun()

    # -----------------------------------------------------------------------
    # Add lesson note
    # -----------------------------------------------------------------------

    if st.button(
        "📝 Add a Note About This Lesson",
        use_container_width=True,
        key="add_lesson_note",
    ):

        # Session-only note-editor navigation.
        st.session_state.note_draft_title = (
            f"{course['title']} — {lesson['title']}"
        )

        st.session_state.selected_note_id = None

        st.session_state.note_editor_open = True

        st.session_state.nav = "Notes"

        st.rerun()


# ===========================================================================
# VISUAL HELPERS
# ===========================================================================

def _box_class(
    lesson,
) -> str:
    """
    Return the appropriate lesson content box class.
    """

    return (
        "vc-challenge-box"
        if lesson["kind"] == "application"
        else "vc-summary-box"
    )


def _play_beep_once() -> None:
    """
    Play the correct-answer beep without allowing sound failure
    to break the lesson.
    """

    try:

        beep_b64 = (
            logic.get_correct_answer_beep_base64()
        )

        st.markdown(
            f'<audio autoplay="true">'
            f'<source src="data:audio/wav;base64,'
            f'{beep_b64}" type="audio/wav">'
            f'</audio>',
            unsafe_allow_html=True,
        )

    except Exception:

        # Sound is optional.
        pass
