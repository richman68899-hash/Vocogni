"""sections/progress.py — Progress tracker (spec sections 10-13, 18)."""

import html

import streamlit as st

import data
import logic
import coach


def render():
    st.markdown("<h2>Progress</h2>", unsafe_allow_html=True)

    progress = st.session_state.progress
    profile = st.session_state.profile

    _render_overview(progress)
    st.markdown("<hr>", unsafe_allow_html=True)
    _render_topic_detail(progress)
    st.markdown("<hr>", unsafe_allow_html=True)
    _render_recommendations(progress)
    st.markdown("<hr>", unsafe_allow_html=True)
    coach.render(progress)
    st.markdown("<hr>", unsafe_allow_html=True)
    _render_lesson_diagnostics(progress)
    st.markdown("<hr>", unsafe_allow_html=True)
    _render_ai_summary(profile, progress)


def _stat_block(label, value):
    st.markdown(
        f"<div class='vc-stat-number'>{value}</div><div class='vc-stat-label'>{label}</div>",
        unsafe_allow_html=True,
    )


def _render_overview(progress):
    st.markdown("<h3>Overview</h3>", unsafe_allow_html=True)
    stats = logic.overall_stats(progress)

    row1 = st.columns(3)
    with row1[0]:
        _stat_block("Courses attempted", stats["courses_attempted"])
    with row1[1]:
        _stat_block("Courses completed", stats["courses_completed"])
    with row1[2]:
        _stat_block("Lessons completed", stats["lessons_completed"])

    row2 = st.columns(3)
    with row2[0]:
        _stat_block("Questions attempted", stats["questions_attempted"])
    with row2[1]:
        _stat_block("Correct answers", stats["correct_answers"])
    with row2[2]:
        _stat_block("Total mistakes", stats["total_mistakes"])

    diagnostic_records = [
        record
        for course_progress in progress.values()
        if isinstance(course_progress, dict)
        for record in course_progress.get("diagnostics", {}).values()
        if isinstance(record, dict)
    ]
    lesson_assessments = [
        record
        for course_progress in progress.values()
        if isinstance(course_progress, dict)
        for record in course_progress.get("lesson_assessments", {}).values()
        if isinstance(record, dict)
    ]
    avg_baseline = (
        round(sum(item.get("percent", 0) for item in diagnostic_records) / len(diagnostic_records))
        if diagnostic_records else "—"
    )
    avg_post = (
        round(sum(item.get("post_practice_percent", 0) for item in lesson_assessments) / len(lesson_assessments))
        if lesson_assessments else "—"
    )
    row3 = st.columns(3)
    with row3[0]:
        _stat_block("Diagnostics completed", len(diagnostic_records))
    with row3[1]:
        _stat_block("Average baseline", f"{avg_baseline}%" if diagnostic_records else "—")
    with row3[2]:
        _stat_block("Average post-lesson practice", f"{avg_post}%" if lesson_assessments else "—")
    st.caption("Diagnostic results are tracked separately from regular practice. Baseline and post-lesson scores are descriptive, not a validated learning-gain measure.")


_STRENGTH_BADGE_CLASS = {"Strength": "vc-badge--success", "Weakness": "vc-badge--warn", "Developing": ""}


def _render_topic_detail(progress):
    st.markdown("<h3>Topic progress</h3>", unsafe_allow_html=True)
    courses = data.all_courses_in_order()
    labels = [c["topic_label"] for c in courses]
    selected_label = st.selectbox("Select a topic", labels, key="progress_topic_select")
    course = next(c for c in courses if c["topic_label"] == selected_label)
    course_id = course["id"]
    prog = progress.get(course_id, {})

    pct = logic.course_lesson_progress_percent(progress, course_id)
    accuracy = logic.course_accuracy(progress, course_id)
    strength = logic.classify_strength(accuracy)

    st.progress(pct)
    lessons_done = len(prog.get("completed_lessons", []))
    st.markdown(
        f"<span class='vc-muted'>{pct}% course progress — {lessons_done} of "
        f"{len(course['lessons'])} learning lessons completed</span>",
        unsafe_allow_html=True,
    )
    diagnostic_id = logic.course_diagnostic_lesson_id(course_id)
    if diagnostic_id:
        diagnostic_done = diagnostic_id in prog.get("diagnostics", {})
        st.caption(
            "Course-entry diagnostic: completed and saved."
            if diagnostic_done
            else "Course-entry diagnostic: not completed yet."
        )

    row = st.columns(3)
    with row[0]:
        _stat_block("Questions attempted", prog.get("questions_attempted", 0))
    with row[1]:
        _stat_block("Correct answers", prog.get("correct_answers", 0))
    with row[2]:
        _stat_block("Mistakes", sum(prog.get("mistakes", {}).values()))

    st.markdown("<div style='margin-top:0.6rem;'>", unsafe_allow_html=True)
    if strength:
        badge_class = _STRENGTH_BADGE_CLASS.get(strength, "")
        st.markdown(
            f"<span class='vc-badge {badge_class}'>{strength}</span> "
            f"<span class='vc-muted'>{accuracy:.0f}% accuracy \u2014 prototype logic based on "
            f"your activity data, not an AI-diagnosed assessment</span>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            "<span class='vc-muted'>No practice questions attempted yet in this topic.</span>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    mistakes = logic.common_mistakes_for_course(progress, course_id)
    if mistakes:
        st.markdown("<h4 style='margin-top:1rem;'>Common mistakes</h4>", unsafe_allow_html=True)
        for tag, count in mistakes:
            st.markdown(f"- {tag} ({count})")



def _render_lesson_diagnostics(progress):
    courses = data.all_courses_in_order()
    labels = [course["topic_label"] for course in courses]
    if not labels:
        return
    selected_label = st.session_state.get("progress_topic_select", labels[0])
    course = next((item for item in courses if item["topic_label"] == selected_label), courses[0])
    course_id = course["id"]
    prog = progress.get(course_id, {})
# Lesson-level diagnostic results and the later practice checkpoint.
st.markdown("<h4 style='margin-top:1rem;'>Lesson diagnostics</h4>", unsafe_allow_html=True)
diagnostic_records = prog.get("diagnostics", {})
lesson_assessments = prog.get("lesson_assessments", {})
if not diagnostic_records:
    st.caption("No lesson diagnostics have been completed for this topic yet.")
else:
    for lesson_id, result in diagnostic_records.items():
        lesson, _ = data.get_lesson(course_id, lesson_id)
        lesson_title = lesson.get("title", lesson_id) if lesson else lesson_id
        st.markdown(f"**{lesson_title}**")
        st.write(
            f"Baseline: {result.get('score', 0)}/{result.get('total', 5)} "
            f"({result.get('percent', 0)}%) — {result.get('outcome_label', 'Placement unavailable')}"
        )
        weaknesses = [
            item.get("skill_tag")
            for item in result.get("weaknesses", [])
            if item.get("skill_tag")
        ]
        if weaknesses:
            st.write("Skills flagged: " + ", ".join(dict.fromkeys(weaknesses)))
        assessment = lesson_assessments.get(lesson_id)
        if assessment:
            st.write(
                f"Post-lesson practice: {assessment.get('post_correct', 0)}/"
                f"{assessment.get('post_total', 0)} "
                f"({assessment.get('post_practice_percent', 0)}%); descriptive difference "
                f"{assessment.get('percentage_point_difference', 0):+d} percentage points."
            )
st.caption("The current diagnostic is a rule-based prototype. Results identify areas to investigate; they are not a clinical, psychometric, or validated mastery assessment.")




def _render_recommendations(progress):
    st.markdown("<h3>Recommended next steps</h3>", unsafe_allow_html=True)
    recs = logic.generate_recommendations(progress)
    if not recs:
        st.markdown(
            "<span class='vc-muted'>Nothing to recommend yet \u2014 start a course "
            "to see personalized suggestions here.</span>",
            unsafe_allow_html=True,
        )
        return
    chips = "".join(f"<span class='vc-recommend-chip'>{r}</span>" for r in recs)
    st.markdown(f"<div>{chips}</div>", unsafe_allow_html=True)


def _render_ai_summary(profile, progress):
    st.markdown("<h3>AI progress summary</h3>", unsafe_allow_html=True)
    st.markdown(
        "<span class='vc-muted'>A prototype simulation built from your own stored "
        "statistics \u2014 no AI model is called in Version 1. See README.md for how "
        "to connect a real one later.</span>",
        unsafe_allow_html=True,
    )
    if st.button("Generate Summary", type="primary"):
        st.session_state.ai_summary_text = logic.generate_progress_summary(profile, progress)

    summary = st.session_state.get("ai_summary_text")
    if summary:
        # profile["name"] is free text, so escape before injecting as HTML.
        st.markdown(f"<div class='vc-summary-box'>{html.escape(summary)}</div>", unsafe_allow_html=True)