"""
sections/course.py — Course detail + interactive lesson flow.

Vocogni Version 1.4.0
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
import assessment


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

    if course_id == "word_problems":
        _render_course_diagnostic_row(course_id, progress)

    diagnostic_lesson_id = logic.course_diagnostic_lesson_id(course_id)
    if diagnostic_lesson_id:
        _render_course_diagnostic_row(course_id, progress)

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
            display_index=(idx + 2 if diagnostic_lesson_id else idx + 1),
        )

    # -----------------------------------------------------------------------
    # Course completed
    # -----------------------------------------------------------------------

    if next_lesson is None:
        if logic.course_diagnostic_completed(progress, course_id):
            st.markdown(
                "<div class='vc-card' style='margin-top:0.5rem;'>"
                "You've completed every item in this course. "
                "Check the Progress page for a full breakdown of how you did."
                "</div>",
                unsafe_allow_html=True,
            )
        else:
            st.info("Complete the course-entry diagnostic to finish this course.")


def _render_course_diagnostic_row(course_id, progress) -> None:
    """Render the saved one-time diagnostic as the first item in a course."""
    course = data.get_course(course_id)
    diagnostic_lesson_id = logic.course_diagnostic_lesson_id(course_id)
    if not course or not diagnostic_lesson_id:
        return

    course_progress = progress.get(course_id, {})
    result = course_progress.get("diagnostics", {}).get(diagnostic_lesson_id)
    done = result is not None
    row_class = "vc-lesson-row" if done else "vc-lesson-row vc-lesson-row--current"
    status_text = (
        "✓ Completed — baseline result saved"
        if done
        else "Up next — complete this before starting new lessons"
    )

    col_info, col_action = st.columns([3, 1])
    with col_info:
        st.markdown(
            f"<div class='{row_class}'><div>"
            f"<strong>1. Diagnostic — {course['title']}</strong><br>"
            f"<span class='vc-muted'>{status_text}</span>"
            f"</div></div>",
            unsafe_allow_html=True,
        )

    with col_action:
        label = "View result" if done else "Start diagnostic"
        if st.button(label, key=f"course_diagnostic_{course_id}", use_container_width=True):
            st.session_state.current_lesson = diagnostic_lesson_id
            flow = state.new_lesson_flow(course_id, diagnostic_lesson_id)
            flow["launch_mode"] = "course_diagnostic"
            st.session_state.lesson_flow = flow
            st.rerun()


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
    display_index=None,
) -> None:
    """
    Render one lesson row.
    """

    if display_index is None:
        display_index = idx + 1

    diagnostic_lesson_id = logic.course_diagnostic_lesson_id(course_id)
    diagnostic_done = logic.course_diagnostic_completed(progress, course_id)
    is_done = lesson["id"] in completed

    unlocked = logic.is_lesson_unlocked(
        progress,
        course_id,
        idx,
    )
    # Preserve access to lessons learners had already completed before this
    # release, but require the diagnostic before starting new course lessons.
    if is_done:
        unlocked = True
    elif diagnostic_lesson_id and not diagnostic_done:
        unlocked = False

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
            "🔒 Complete the diagnostic first"
            if diagnostic_lesson_id and not diagnostic_done
            else "🔒 Locked — finish the previous lesson first"
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
            f"<strong>{display_index}. {lesson['title']}</strong> "
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
    """Render a predictable hub -> diagnostic -> pathway -> practice flow."""
    flow = st.session_state.lesson_flow
    if not isinstance(flow, dict):
        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None
        st.rerun()
        return

    course_id, lesson_id = flow.get("course_id"), flow.get("lesson_id")
    course = data.get_course(course_id)
    lesson, _ = data.get_lesson(course_id, lesson_id)
    if course is None or lesson is None:
        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None
        st.rerun()
        return

    prog = state.get_course_progress(course_id)
    diagnostic_config = lesson.get("diagnostic")
    diagnostic_records = prog.setdefault("diagnostics", {})
    diagnostic_result = diagnostic_records.get(lesson_id)
    attempts = prog.setdefault("practice_attempts", {})
    lesson_attempts = attempts.setdefault(lesson_id, [])
    already_done = lesson_id in prog.get("completed_lessons", [])

    if st.button("← Back to course", key=f"back_to_course_{lesson_id}"):
        state.flush_persistent_save()
        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None
        st.rerun()

    launch_mode = flow.get("launch_mode")
    st.markdown(f"<span class='vc-muted'>{course['title']}</span>", unsafe_allow_html=True)
    display_title = f"Diagnostic — {course['title']}" if launch_mode == "course_diagnostic" else lesson["title"]
    st.markdown(f"<h2>{display_title}</h2>", unsafe_allow_html=True)

    if launch_mode == "course_diagnostic":
        if diagnostic_result is not None:
            _render_course_diagnostic_result(lesson, diagnostic_result)
        else:
            _render_diagnostic(lesson, course_id)
        return

    # Structured lessons across every course share the same three-screen flow.
    if lesson.get("worked_example") and lesson.get("interactive_question"):
        if diagnostic_config and diagnostic_result is None:
            st.info("Complete the course-entry diagnostic before starting this lesson.")
            _render_diagnostic(lesson, course_id)
            return

        if not flow.get("structured_lesson"):
            _initialize_structured_lesson_flow(
                lesson, course_id, flow, diagnostic_result
            )

        if flow.get("view") == "attempt_complete":
            _render_attempt_complete(course, lesson, flow, diagnostic_result, lesson_attempts)
            return

        stage = flow.get("stage", "concept")
        if stage in ("concept", "worked_example"):
            _render_three_screen_lesson(lesson, flow, diagnostic_result, course_id)
        elif stage == "question":
            _render_question(lesson, flow, course_id)
        elif stage == "feedback":
            _render_feedback(lesson, flow)
        elif stage == "complete":
            _finish_practice_attempt(course, lesson, flow, course_id, diagnostic_result)
        else:
            flow["view"] = "structured_lesson"
            flow["stage"] = "concept"
            st.rerun()
        return

    # Legacy fallback remains available for any lesson not yet converted.
    if diagnostic_config and diagnostic_result is None:
        _render_diagnostic(lesson, course_id)
        return

    if diagnostic_config and diagnostic_result is not None:
        if flow.get("view") not in ("practice", "attempt_complete"):
            _render_lesson_hub(course, lesson, flow, diagnostic_result, lesson_attempts)
            return
    elif flow.get("view") not in ("practice", "attempt_complete"):
        flow["view"] = "hub"

    if flow.get("view") == "attempt_complete":
        _render_attempt_complete(course, lesson, flow, diagnostic_result, lesson_attempts)
        return

    if flow.get("view") == "practice":
        if not flow.get("active_questions"):
            route = flow.get("selected_pathway", "level_1")
            flow["active_questions"] = (
                diagnostics.get_pathway_questions(lesson, route)
                if diagnostic_config else lesson.get("questions", [])
            )
        stage = flow.get("stage", "intro")
        if stage == "intro":
            _render_intro(lesson, flow)
        elif stage == "question":
            _render_question(lesson, flow, course_id)
        elif stage == "feedback":
            _render_feedback(lesson, flow)
        elif stage == "complete":
            _finish_practice_attempt(course, lesson, flow, course_id, diagnostic_result)
        else:
            flow["stage"] = "intro"
            st.rerun()
        return

    _render_lesson_hub(course, lesson, flow, diagnostic_result, lesson_attempts)


def _render_lesson_hub(course, lesson, flow, diagnostic_result, attempts) -> None:
    """Stable lesson landing screen; diagnostics are never reset here."""
    st.markdown(f"<div class='{_box_class(lesson)}'>{lesson['explanation']}</div>", unsafe_allow_html=True)
    if diagnostic_result:
        st.markdown("### Your diagnostic")
        st.metric("Baseline score", f"{diagnostic_result.get('score', 0)} / {diagnostic_result.get('total', 5)}",
                  f"{diagnostic_result.get('percent', 0)}%")
        weaknesses = diagnostic_result.get("weaknesses", [])
        if weaknesses:
            st.markdown("**Skills to review**")
            for item in weaknesses:
                st.markdown(f"- **{item.get('skill_tag', 'Skill')}** — {item.get('recommended_action', 'Review this concept.')}")
        else:
            st.write("No weaknesses were flagged by this diagnostic.")
        unlocked = diagnostics.unlocked_pathways_for_score(diagnostic_result)
        labels = {key: value["label"] for key, value in diagnostics.PATHWAY_META.items()}
        st.markdown("### Choose a practice test")
        st.caption("You can repeat practice tests. Your one-time diagnostic remains unchanged.")
        selected = st.selectbox(
            "Unlocked practice tests",
            options=unlocked,
            format_func=lambda key: labels.get(key, key),
            key=f"hub_route_{lesson['id']}",
        )
        if st.button("Start practice test", type="primary", key=f"hub_start_{lesson['id']}"):
            _start_practice_attempt(lesson, flow, diagnostic_result, selected)
            st.rerun()
        if attempts:
            st.markdown("### Previous practice attempts")
            for i, attempt in enumerate(reversed(attempts), start=1):
                st.write(f"Attempt {len(attempts) - i + 1}: {attempt.get('correct', 0)}/{attempt.get('total', 0)} correct — {attempt.get('pathway_label', attempt.get('pathway', 'Practice'))}")
    else:
        if st.button("Begin lesson", type="primary", key=f"hub_start_{lesson['id']}"):
            flow.update({"view": "practice", "stage": "intro", "q_index": 0, "results": [],
                         "active_questions": lesson.get("questions", []), "attempt_number": 1})
            st.rerun()


def _select_structured_question(lesson, diagnostic_result):
    """Choose Screen 3's question and route, using placement when a diagnostic exists."""
    authored = lesson.get("interactive_question")
    route = "standard"
    candidates = [authored] if authored else []
    if lesson.get("diagnostic") and diagnostic_result:
        route = diagnostic_result.get("outcome_key", "level_1")
        if route in ("prerequisite", "level_1"):
            route = "level_1"
            candidates = [authored] if authored else []
        else:
            candidates = diagnostics.get_pathway_questions(lesson, route)
        if not candidates:
            candidates = [authored] if authored else []
    candidates = [item for item in candidates if isinstance(item, dict)]
    return (candidates[0] if candidates else None), route


def _find_lesson_question_by_id(lesson, question_id):
    """Find an authored question by stable ID, including diagnostic pathways."""
    if not question_id:
        return None
    candidates = []
    authored = lesson.get("interactive_question")
    if isinstance(authored, dict):
        candidates.append(authored)
    candidates.extend(lesson.get("questions", []))
    diagnostic = lesson.get("diagnostic", {})
    if isinstance(diagnostic, dict):
        candidates.extend(diagnostic.get("questions", []))
        for pathway in diagnostic.get("pathways", {}).values():
            if isinstance(pathway, dict):
                candidates.extend(pathway.get("questions", []))
    return next(
        (question for question in candidates
         if isinstance(question, dict) and question.get("id") == question_id),
        None,
    )


def _save_lesson_screen_checkpoint(course_id, lesson_id, updates) -> bool:
    """Save one lesson's resumable screen state inside the existing progress record."""
    logic.update_lesson_screen_checkpoint(
        st.session_state.progress, course_id, lesson_id, updates
    )
    state.mark_persistent_dirty()
    return state.flush_persistent_save()


def _initialize_structured_lesson_flow(lesson, course_id, flow, diagnostic_result) -> None:
    """Resume an unfinished saved lesson; leave completed history intact for review."""
    progress = st.session_state.progress
    checkpoint = logic.get_lesson_screen_checkpoint(progress, course_id, lesson["id"])
    history = (
        progress.get(course_id, {})
        .get("practice_attempts", {})
        .get(lesson["id"], [])
    )
    next_attempt = len(history) + 1
    if not checkpoint.get("completed"):
        screen = checkpoint.get("current_screen", 1)
        try:
            screen = int(screen)
        except (TypeError, ValueError):
            screen = 1
        if screen not in (1, 2, 3):
            screen = 1
        attempt_number = int(checkpoint.get("attempt_number", next_attempt) or next_attempt)
        route = checkpoint.get("selected_pathway", "standard")
        base = {
            "structured_lesson": True,
            "attempt_number": attempt_number,
            "selected_pathway": route,
            "q_index": 0,
            "results": [],
            "last_correct": None,
            "last_user_answer": None,
        }
        if screen in (1, 2):
            base.update({
                "view": "structured_lesson",
                "stage": "concept" if screen == 1 else "worked_example",
                "active_questions": [],
            })
        else:
            question = _find_lesson_question_by_id(lesson, checkpoint.get("question_id"))
            if question is None:
                question, route = _select_structured_question(lesson, diagnostic_result)
                base["selected_pathway"] = route
            if question is not None:
                submitted = bool(checkpoint.get("screen_3_submitted"))
                base.update({
                    "view": "practice",
                    "stage": "feedback" if submitted else "question",
                    "active_questions": [question],
                    "last_correct": checkpoint.get("last_correct") if submitted else None,
                    "last_user_answer": checkpoint.get("last_answer") if submitted else None,
                })
                if submitted:
                    base["results"] = [{
                        "correct": bool(checkpoint.get("last_correct")),
                        "explanation": question.get("explanation", ""),
                    }]
            else:
                base.update({
                    "view": "structured_lesson",
                    "stage": "worked_example",
                    "active_questions": [],
                })
        flow.update(base)
        return

    # A completed lesson opens at Screen 1 for review; its history is untouched.
    flow.update({
        "structured_lesson": True,
        "view": "structured_lesson",
        "stage": "concept",
        "attempt_number": next_attempt,
        "selected_pathway": "standard",
        "q_index": 0,
        "results": [],
        "active_questions": [],
        "last_correct": None,
        "last_user_answer": None,
    })


def _render_course_diagnostic_result(lesson, result) -> None:
    """Show the saved one-time course diagnostic without opening a practice route."""
    st.markdown("### Diagnostic results")
    st.metric("Baseline score", f"{result.get('score', 0)} / {result.get('total', 5)}",
              f"{result.get('percent', 0)}%")
    st.subheader(result.get("outcome_label", "Diagnostic completed"))
    st.write(result.get("outcome_summary", "Your baseline result has been saved."))
    st.caption(result.get("next_action", "Continue to the first learning lesson."))

    weaknesses = result.get("weaknesses", [])
    if weaknesses:
        st.markdown("#### Skills to review")
        for weakness in weaknesses:
            st.markdown(
                f"- **{weakness.get('skill_tag', 'Skill')}** — "
                f"{weakness.get('recommended_action', 'Review this concept.')}"
            )
    else:
        st.success("No weaknesses were flagged by these five diagnostic items.")

    with st.expander("Review diagnostic answers"):
        for index, item in enumerate(result.get("answer_review", []), start=1):
            label = "Correct" if item.get("correct") else "Needs review"
            st.markdown(f"**{index}. {label} — {item.get('skill_tag', 'Skill')}**")
            st.caption(item.get("prompt", ""))
            st.write(f"Your answer: {item.get('user_answer')}")
            st.write(f"Expected answer: {item.get('expected_answer')}")
            st.write(item.get("explanation", ""))

    st.caption(
        "This is a one-time baseline diagnostic. It is the first course item, "
        "not a replacement for the four learning lessons."
    )


def _render_three_screen_lesson(lesson, flow, diagnostic_result, course_id) -> None:
    """Render Screen 1 (concept), Screen 2 (worked example), or advance to Screen 3."""
    stage = flow.get("stage", "concept")

    if stage == "concept":
        st.markdown("### Screen 1 of 3 — Concept explanation")
        st.markdown(
            f"<div class='{_box_class(lesson)}'>{lesson['explanation']}</div>",
            unsafe_allow_html=True,
        )
        if lesson.get("diagnostic") and diagnostic_result:
            st.info(
                f"Diagnostic placement: {diagnostic_result.get('outcome_label', 'Start with the core idea')}. "
                f"{diagnostic_result.get('next_action', '')}"
            )
            if diagnostic_result.get("outcome_key") == "prerequisite":
                review = lesson.get("diagnostic", {}).get("prerequisite_review", "")
                if review:
                    st.caption(f"Prerequisite to review: {review}")

        if st.button("Next: Worked example", type="primary", key=f"screen1_next_{lesson['id']}"):
            history = (
                st.session_state.progress.get(course_id, {})
                .get("practice_attempts", {})
                .get(lesson["id"], [])
            )
            attempt_number = len(history) + 1
            saved = _save_lesson_screen_checkpoint(course_id, lesson["id"], {
                "current_screen": 2,
                "completed_screens": [1],
                "completed": False,
                "screen_3_submitted": False,
                "question_id": None,
                "last_answer": None,
                "last_correct": None,
                "attempt_number": attempt_number,
            })
            flow["stage"] = "worked_example"
            flow["attempt_number"] = attempt_number
            if saved:
                st.rerun()
            else:
                st.error("Screen progress is pending save. Keep the app open and retry saving before leaving.")
        return

    if stage == "worked_example":
        st.markdown("### Screen 2 of 3 — Worked example")
        st.markdown(
            f"<div class='{_box_class(lesson)}'>{lesson.get('worked_example', '')}</div>",
            unsafe_allow_html=True,
        )
        if st.button("← Back to concept", key=f"screen2_back_{lesson['id']}"):
            checkpoint = logic.get_lesson_screen_checkpoint(
                st.session_state.progress, course_id, lesson["id"]
            )
            saved = _save_lesson_screen_checkpoint(course_id, lesson["id"], {
                "current_screen": 1,
                "completed_screens": [],
                "completed": False,
                "screen_3_submitted": False,
                "question_id": None,
                "last_answer": None,
                "last_correct": None,
                "attempt_number": checkpoint.get("attempt_number", flow.get("attempt_number", 1)),
            })
            flow["stage"] = "concept"
            if saved:
                st.rerun()
            else:
                st.error("Screen progress is pending save. Keep the app open and retry saving before leaving.")

        if st.button("Next: Interactive question", type="primary", key=f"screen2_next_{lesson['id']}"):
            question, route = _select_structured_question(lesson, diagnostic_result)
            if question is None:
                st.error("This lesson needs one interactive question before it can continue.")
                return

            checkpoint = logic.get_lesson_screen_checkpoint(
                st.session_state.progress, course_id, lesson["id"]
            )
            history = (
                st.session_state.progress.get(course_id, {})
                .get("practice_attempts", {})
                .get(lesson["id"], [])
            )
            attempt_number = int(checkpoint.get("attempt_number", len(history) + 1) or (len(history) + 1))
            saved = _save_lesson_screen_checkpoint(course_id, lesson["id"], {
                "current_screen": 3,
                "completed_screens": [1, 2],
                "completed": False,
                "screen_3_submitted": False,
                "question_id": question.get("id"),
                "last_answer": None,
                "last_correct": None,
                "attempt_number": attempt_number,
                "selected_pathway": route,
            })
            flow.update({
                "view": "practice",
                "stage": "question",
                "q_index": 0,
                "results": [],
                "active_questions": [question],
                "attempt_number": attempt_number,
                "selected_pathway": route,
                "structured_lesson": True,
                "last_correct": None,
                "last_user_answer": None,
            })
            if saved:
                st.rerun()
            else:
                st.error("Screen 3 is open, but saving this checkpoint has not been confirmed. Keep the app open and retry saving before leaving.")
        return


def _start_practice_attempt(lesson, flow, diagnostic_result, pathway) -> None:
    """Initialize a clean practice attempt without touching the diagnostic."""
    previous = int(flow.get("attempt_number", 0))
    questions = diagnostics.get_pathway_questions(lesson, pathway)
    flow.update({
        "view": "practice", "stage": "intro", "q_index": 0, "results": [],
        "active_questions": questions, "selected_pathway": pathway,
        "attempt_number": previous + 1, "last_correct": None, "last_user_answer": None,
    })
    # Persist the most recently selected route for a consistent return experience.
    diagnostic_result["selected_pathway"] = pathway
    diagnostic_result["selected_pathway_at"] = datetime.now(timezone.utc).isoformat()
    state.mark_persistent_dirty()
    if not state.flush_persistent_save():
        flow["save_warning"] = "Route selection could not be saved yet. Retry save before leaving."


def _finish_practice_attempt(course, lesson, flow, course_id, diagnostic_result) -> None:
    """Persist one immutable practice-attempt summary, then show its result."""
    prog = state.get_course_progress(course_id)
    history = prog.setdefault("practice_attempts", {}).setdefault(lesson["id"], [])
    attempt_number = int(flow.get("attempt_number", len(history) + 1))
    existing = next((x for x in history if x.get("attempt_number") == attempt_number), None)
    results = flow.get("results", [])
    correct = sum(bool(x.get("correct")) for x in results)
    if existing is None:
        route = flow.get("selected_pathway", "standard")
        label = diagnostics.PATHWAY_META.get(route, {}).get("label", "Standard practice")
        history.append({
            "attempt_number": attempt_number, "pathway": route, "pathway_label": label,
            "correct": correct, "total": len(results),
            "percent": round(correct / len(results) * 100) if results else 0,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "results": list(results),
        })
        state.mark_persistent_dirty()
    # Legacy completion tracking is preserved; it no longer blocks practice retakes.
    if lesson["id"] not in prog.setdefault("completed_lessons", []):
        logic.mark_lesson_complete(st.session_state.progress, course_id, lesson["id"])
        state.mark_persistent_dirty()
    if diagnostic_result and not prog.setdefault("lesson_assessments", {}).get(lesson["id"]) and results:
        baseline = diagnostic_result
        prog["lesson_assessments"][lesson["id"]] = {
            "baseline_score": baseline.get("score", 0), "baseline_total": baseline.get("total", 5),
            "baseline_percent": baseline.get("percent", 0), "post_correct": correct,
            "post_total": len(results), "post_practice_percent": round(correct / len(results) * 100),
            "percentage_point_difference": round(correct / len(results) * 100) - baseline.get("percent", 0),
            "pathway": flow.get("selected_pathway", "unknown"),
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
        state.mark_persistent_dirty()
    if flow.get("structured_lesson"):
        active_questions = flow.get("active_questions", [])
        current_question = active_questions[0] if active_questions else {}
        logic.update_lesson_screen_checkpoint(
            st.session_state.progress, course_id, lesson["id"], {
                "current_screen": 3,
                "completed_screens": [1, 2, 3],
                "completed": True,
                "screen_3_submitted": True,
                "question_id": current_question.get("id"),
                "last_answer": flow.get("last_user_answer"),
                "last_correct": flow.get("last_correct"),
                "attempt_number": attempt_number,
                "selected_pathway": flow.get("selected_pathway", "standard"),
            }
        )
        state.mark_persistent_dirty()

    save_ok = state.flush_persistent_save()
    flow["view"] = "attempt_complete"
    flow["stage"] = "complete"
    if not save_ok:
        st.error("Your attempt is shown, but saving failed. Retry the save before leaving.")
    _render_attempt_complete(course, lesson, flow, diagnostic_result, history)


def _render_attempt_complete(course, lesson, flow, diagnostic_result, attempts) -> None:
    if flow.get("structured_lesson"):
        results = flow.get("results", [])
        correct = sum(bool(item.get("correct")) for item in results)
        total = len(results)
        st.markdown("### Lesson checkpoint")
        st.metric("Interactive question", f"{correct} / {total}", f"{round(correct / total * 100) if total else 0}%")
        st.markdown(
            "<div class='vc-card'>"
            "The concept, worked example, and interactive question are complete. "
            "Your answer and feedback have been recorded."
            "</div>",
            unsafe_allow_html=True,
        )
        review_col, back_col = st.columns(2)
        with review_col:
            if st.button("Review this lesson", type="primary", use_container_width=True,
                         key=f"structured_review_{lesson['id']}"):
                flow.update({
                    "view": "structured_lesson", "stage": "concept",
                    "q_index": 0, "results": [], "active_questions": [],
                    "last_correct": None, "last_user_answer": None,
                })
                st.rerun()
        with back_col:
            if st.button("Back to lessons", use_container_width=True,
                         key=f"structured_back_{lesson['id']}"):
                state.flush_persistent_save()
                st.session_state.current_lesson = None
                st.session_state.lesson_flow = None
                st.rerun()
        return

    results = flow.get("results", [])
    correct = sum(bool(x.get("correct")) for x in results)
    st.markdown("### Practice results")
    st.metric("Score", f"{correct} / {len(results)}",
              f"{round(correct / len(results) * 100) if results else 0}%")
    st.caption("This is a practice attempt, not a replacement for your original diagnostic.")
    if st.button("Return to lesson hub", type="primary", key=f"return_hub_{lesson['id']}"):
        flow["view"] = "hub"
        flow["stage"] = "intro"
        flow["results"] = []
        flow["active_questions"] = []
        st.rerun()
    if st.button("Back to course", key=f"attempt_back_{lesson['id']}"):
        state.flush_persistent_save()
        st.session_state.current_lesson = None
        st.session_state.lesson_flow = None
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
        "✓ You already completed this lesson. Your original completion and "
        "one-time diagnostic remain saved. You can review the practice again "
        "without resetting the diagnostic."
        "</div>",
        unsafe_allow_html=True,
    )

    col_retake, col_back = st.columns(2)
    with col_retake:
        if st.button(
            "Retake practice test",
            type="primary",
            use_container_width=True,
            key=f"retake_practice_{lesson['id']}",
        ):
            flow = st.session_state.lesson_flow
            prog = st.session_state.progress.get(flow["course_id"], {})
            saved = prog.get("diagnostics", {}).get(lesson["id"], {})
            selected = saved.get("selected_pathway", saved.get("outcome_key", "level_1"))
            questions = diagnostics.get_pathway_questions(lesson, selected)
            attempt_number = int(flow.get("attempt_number", 1)) + 1
            flow.update({
                "stage": "intro",
                "q_index": 0,
                "results": [],
                "active_questions": questions,
                "selected_pathway": selected,
                "attempt_number": attempt_number,
                "last_correct": None,
                "last_user_answer": None,
            })
            st.rerun()

    with col_back:
        if st.button(
            "Back to course",
            use_container_width=True,
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

    if flow.get("structured_lesson"):
        st.markdown("### Screen 3 of 3 — Interactive question")

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
        f"answer_{lesson['id']}_{flow.get('attempt_number', 1)}_{question['id']}"
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

    elif question.get("type") == "open_ended":

        if settings.get("difficulty") == "Easy" and question.get("input_hint"):
            st.caption(f"Guidance: {question['input_hint']}")

        st.caption(
            "Show your reasoning. Marks are awarded for the configured criteria; "
            "valid equivalent wording and notation may be accepted."
        )
        user_answer = st.text_area(
            "Your answer:",
            key=answer_key,
            height=150,
            placeholder="Type your formula, equation, calculation, or explanation...",
        )
        can_submit = bool(user_answer and user_answer.strip())

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
        key=f"submit_answer_{lesson['id']}_{flow.get('attempt_number', 1)}_{question['id']}",
    ):

        # ---------------------------------------------------------------
        # Calculate correctness
        # ---------------------------------------------------------------

        grade = (
            assessment.grade_open_ended(question, user_answer)
            if question.get("type") == "open_ended"
            else None
        )
        is_correct = (
            grade["is_full_credit"]
            if grade is not None
            else logic.check_answer(question, user_answer)
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

        if flow.get("structured_lesson"):
            logic.update_lesson_screen_checkpoint(
                st.session_state.progress, course_id, lesson["id"], {
                    "current_screen": 3,
                    "completed_screens": [1, 2, 3],
                    "completed": False,
                    "screen_3_submitted": True,
                    "question_id": question.get("id"),
                    "last_answer": user_answer,
                    "last_correct": is_correct,
                    "last_grade": grade,
                    "attempt_number": flow.get("attempt_number", 1),
                    "selected_pathway": flow.get("selected_pathway", "standard"),
                }
            )

        state.mark_persistent_dirty()

        # ---------------------------------------------------------------
        # Update transient lesson state
        # ---------------------------------------------------------------

        flow["last_correct"] = is_correct
        flow["last_user_answer"] = user_answer
        flow["last_grade"] = grade

        result_record = {
            "correct": is_correct,
            "explanation": question["explanation"],
            "question_id": question.get("id"),
            "raw_answer": str(user_answer) if question.get("type") == "open_ended" else None,
        }
        if grade is not None:
            result_record.update({
                "marks_awarded": grade["marks_awarded"],
                "max_marks": grade["max_marks"],
                "marking_feedback": grade["feedback"],
                "warnings": grade["warnings"],
                "point_results": grade["point_results"],
            })
            course_progress = st.session_state.progress.setdefault(course_id, {})
            course_progress["open_ended_marks_awarded"] = (
                course_progress.get("open_ended_marks_awarded", 0) + grade["marks_awarded"]
            )
            course_progress["open_ended_marks_available"] = (
                course_progress.get("open_ended_marks_available", 0) + grade["max_marks"]
            )
            course_progress.setdefault("open_ended_attempts", []).append({
                "lesson_id": lesson["id"],
                "question_id": question.get("id"),
                "marks_awarded": grade["marks_awarded"],
                "max_marks": grade["max_marks"],
                "percent": grade["percent"],
                "submitted_at": datetime.now(timezone.utc).isoformat(),
                "warnings": grade["warnings"],
            })
        flow["results"].append(result_record)

        # ---------------------------------------------------------------
        # Determine next stage
        # ---------------------------------------------------------------

        if flow.get("structured_lesson") or (
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

        if flow.get("structured_lesson"):
            if state.flush_persistent_save():
                st.rerun()
            else:
                st.error(
                    "Your answer is recorded in this session, but the save failed. "
                    "Use the retry-save option before leaving; the answer checkpoint remains pending."
                )
        else:
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

    if flow.get("structured_lesson"):
        st.markdown("### Screen 3 of 3 — Interactive question")
        st.markdown(f"#### {question['prompt']}")
        st.caption(f"Your answer: {flow.get('last_user_answer')}")

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

    grade = flow.get("last_grade")
    if grade:
        st.metric(
            "Mark-scheme practice score",
            f"{grade.get('marks_awarded', 0)} / {grade.get('max_marks', 0)} marks",
            f"{grade.get('percent', 0)}%",
        )
        if grade.get("warnings"):
            for warning in grade["warnings"]:
                st.warning(warning)
        feedback_items = grade.get("feedback", [])
        if feedback_items:
            with st.expander("Marking-point feedback", expanded=not grade.get("is_full_credit", False)):
                for item in feedback_items:
                    st.write(f"• {item}")
        st.caption(
            "This is transparent, rubric-based practice marking. It is not an official Cambridge mark scheme."
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
