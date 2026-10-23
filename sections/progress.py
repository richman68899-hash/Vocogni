"""sections/progress.py — Progress tracker (spec sections 10-13, 18)."""

import html

import streamlit as st

import data
import logic
import coach
import learning_maintenance
import state


def render():
    st.markdown("<h2>Progress</h2>", unsafe_allow_html=True)

    progress = st.session_state.progress
    profile = st.session_state.profile

    _render_overview(progress)
    st.markdown("<hr>", unsafe_allow_html=True)
    _render_learning_maintenance(progress, profile)
    st.markdown("<hr>", unsafe_allow_html=True)
    _render_topic_detail(progress)
    st.markdown("<hr>", unsafe_allow_html=True)
    _render_mastery_receipt(progress)
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



def _start_maintenance_lesson(course_id, lesson_id):
    """Open an existing lesson as a fresh review attempt, without resetting history."""
    if not data.get_course(course_id):
        return
    lesson, _ = data.get_lesson(course_id, lesson_id)
    if not lesson:
        return
    st.session_state.nav = "Browse"
    st.session_state.current_course = course_id
    st.session_state.current_lesson = lesson_id
    st.session_state.lesson_flow = state.new_lesson_flow(course_id, lesson_id)
    st.rerun()


def _render_learning_maintenance(progress, profile):
    """Render meaningful learning consistency and the spaced-review queue."""
    st.markdown("<h3>Learning Rhythm</h3>", unsafe_allow_html=True)
    st.caption(
        "Build a sustainable learning routine. A saved answer with feedback, a "
        "completed practice set, or a diagnostic counts as a learning day; simply "
        "opening Vocogni or viewing a lesson does not."
    )

    settings = st.session_state.get("settings", {})
    if not isinstance(settings, dict):
        settings = {}
        st.session_state.settings = settings
    saved_target = settings.get(
        "weekly_learning_goal_days",
        learning_maintenance.DEFAULT_WEEKLY_TARGET,
    )
    try:
        saved_target = int(saved_target)
    except (TypeError, ValueError):
        saved_target = learning_maintenance.DEFAULT_WEEKLY_TARGET
    if saved_target not in learning_maintenance.WEEKLY_TARGET_OPTIONS:
        saved_target = learning_maintenance.DEFAULT_WEEKLY_TARGET

    selected_target = st.selectbox(
        "Weekly learning target",
        options=list(learning_maintenance.WEEKLY_TARGET_OPTIONS),
        index=list(learning_maintenance.WEEKLY_TARGET_OPTIONS).index(saved_target),
        format_func=lambda days: f"{days} learning days",
        key="maintenance_weekly_target_select",
        help="Choose a sustainable target. You do not need to study every day.",
    )
    if saved_target != selected_target:
        settings["weekly_learning_goal_days"] = selected_target
        state.mark_persistent_dirty()

    timezone_label = profile.get("timezone", "Prefer not to say") if isinstance(profile, dict) else "Prefer not to say"
    summary = learning_maintenance.build_maintenance_summary(
        progress,
        timezone_label=timezone_label,
        weekly_target=selected_target,
    )

    row = st.columns(4)
    with row[0]:
        _stat_block("Current streak", f"{summary['current_streak']} day(s)")
    with row[1]:
        _stat_block("Longest streak", f"{summary['longest_streak']} day(s)")
    with row[2]:
        _stat_block(
            "This week",
            f"{summary['active_days_this_week']} / {summary['weekly_target']} days",
        )
    with row[3]:
        _stat_block("Learning today", "Complete" if summary["today_complete"] else "Not yet")

    if summary["week_goal_met"]:
        st.caption(
            "Weekly target reached. Any further practice is optional; the aim is "
            "consistent learning, not maximizing time spent in the app."
        )
    else:
        remaining = max(0, summary["weekly_target"] - summary["active_days_this_week"])
        st.caption(
            f"{remaining} more learning day(s) to reach your weekly target. "
            "A missed day does not erase your progress."
        )

    week_status = "   ·   ".join(
        f"{day['label']} {'✓' if day['active'] else ('—' if not day['future'] else ' ')}"
        for day in summary["week_day_cards"]
    )
    st.markdown(f"**This week's activity**")
    st.write(week_status)

    if summary["today_complete"]:
        st.caption(
            "A meaningful learning action is already saved for today. You can stop here "
            "and return when it suits your schedule."
        )
    elif summary["current_streak"] > 0:
        st.write(
            f"Your {summary['current_streak']}-day streak is still in reach. Complete "
            "one practice set or diagnostic today to continue it."
        )
    elif summary["last_active_day"]:
        st.write(
            "Welcome back. Your earlier learning history is still saved; a learning "
            "session today starts a new streak without resetting that history."
        )
    else:
        st.write(
            "Start with one practice set or diagnostic. That creates your first "
            "recorded learning day."
        )

    st.markdown("#### Spaced review")
    st.caption(
        "Reviews bring earlier learning back after a gap. Lower recent performance "
        "is scheduled sooner; stronger practice is spaced farther apart."
    )

    if summary["due_reviews"]:
        for item in summary["due_reviews"]:
            left, right = st.columns([4, 1])
            with left:
                st.markdown(f"**{item['lesson_title']}**")
                overdue = item["days_overdue"]
                detail = f"{item['course_title']} · due {item['due_date'].strftime('%d %b')}"
                if overdue:
                    detail += f" · {overdue} day(s) overdue"
                if item["latest_percent"] is not None:
                    detail += f" · latest result {item['latest_percent']}%"
                st.caption(detail)
            with right:
                if st.button(
                    "Review",
                    key=f"maintenance_review_{item['course_id']}_{item['lesson_id']}",
                    use_container_width=True,
                ):
                    _start_maintenance_lesson(item["course_id"], item["lesson_id"])
        if summary["total_due_reviews"] > len(summary["due_reviews"]):
            st.caption(
                f"{summary['total_due_reviews'] - len(summary['due_reviews'])} more review(s) "
                "are due. VOCogni shows the first few so the queue stays manageable."
            )
    elif summary["upcoming_reviews"]:
        item = summary["upcoming_reviews"][0]
        st.caption(
            f"No review is due yet. Next: {item['lesson_title']} "
            f"({item['course_title']}) on {item['due_date'].strftime('%d %b')}."
        )
    else:
        st.caption(
            "No review is scheduled yet. Complete a practice set in a lesson to create "
            "a follow-up review date."
        )

    st.caption(
        summary["review_schedule_note"]
        + " Days follow your Profile timezone; UTC is used when no UTC offset is selected."
    )
    if not summary["today_complete"] and not summary["due_reviews"]:
        if st.button("Choose a course", key="maintenance_browse_courses"):
            st.session_state.nav = "Browse"
            st.session_state.current_course = None
            st.session_state.current_lesson = None
            st.session_state.lesson_flow = None
            st.rerun()


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




def _render_mastery_receipt(progress):
    """Render question-level learning evidence for the selected course."""
    courses = data.all_courses_in_order()
    if not courses:
        return

    labels = [course.get("topic_label", course.get("title", course["id"])) for course in courses]
    selected_label = st.session_state.get("progress_topic_select", labels[0])
    course = next(
        (
            item for item in courses
            if item.get("topic_label", item.get("title", item["id"])) == selected_label
        ),
        courses[0],
    )
    receipt = logic.mastery_receipt_for_course(progress, course["id"])

    st.markdown("<h3>Mastery Receipt</h3>", unsafe_allow_html=True)
    st.caption(
        f"A course-specific summary built automatically from {course.get('title', course['id'])}'s "
        "published questions, saved practice attempts, and diagnostic reviews. "
        "No course-specific receipt configuration is required."
    )

    if not receipt or not receipt["skills"]:
        st.info("This course does not yet expose question-level skills that can be tracked.")
        return

    counts = receipt["status_counts"]
    columns = st.columns(4)
    with columns[0]:
        _stat_block("Skills tracked", receipt["skills_total"])
    with columns[1]:
        _stat_block("Need review", counts.get("Needs review", 0))
    with columns[2]:
        _stat_block("Developing", counts.get("Developing", 0))
    with columns[3]:
        _stat_block("Promising evidence", counts.get("Promising evidence", 0))

    st.markdown("**Recommended next action**")
    st.write(receipt["next_action"])

    status_order = {
        "Needs review": 0,
        "Developing": 1,
        "Not tested": 2,
        "Promising evidence": 3,
    }
    skills = sorted(
        receipt["skills"],
        key=lambda item: status_order.get(item["status"], 4),
    )
    first_review_expanded = True

    st.markdown("#### Skill-by-skill evidence")
    for item in skills:
        status = item["status"]
        expanded = status == "Needs review" and first_review_expanded
        if expanded:
            first_review_expanded = False
        with st.expander(f"{item['skill']} — {status}", expanded=expanded):
            if item["lesson_titles"]:
                st.caption("Course content: " + ", ".join(item["lesson_titles"]))

            if item["practice_performance_percent"] is None:
                st.write("Practice performance: no question-level practice answers recorded.")
            else:
                st.write(
                    f"Practice performance: {item['practice_performance_percent']}% "
                    f"across {item['practice_answers']} answered item(s), with "
                    f"{item['distinct_practice_questions']} distinct question ID(s)."
                )
                latest = item["latest_practice_percent"]
                if latest is not None:
                    st.caption(f"Latest recorded item: {latest}% performance.")
                st.caption(
                    f"Full-credit answers: {item['full_credit_answers']} of "
                    f"{item['practice_answers']} answered item(s)."
                )

            if item["diagnostic_performance_percent"] is not None:
                st.caption(
                    f"Entry diagnostic baseline: {item['diagnostic_performance_percent']}% "
                    f"across {item['diagnostic_items']} item(s). A diagnostic is baseline "
                    "evidence, not proof of current mastery."
                )
            if item["diagnostic_flagged"]:
                st.warning(
                    "The entry diagnostic flagged this skill. Current practice evidence "
                    "takes priority once practice has been recorded."
                )
            if item["legacy_error_count"]:
                st.caption(
                    f"Older aggregate error counter: {item['legacy_error_count']} error(s). "
                    "This counter has no item-level timeline."
                )

            st.write("**Next action:** " + item["next_action"])

    st.caption(receipt["evidence_note"])

def _render_lesson_diagnostics(progress):
    courses = data.all_courses_in_order()
    labels = [course["topic_label"] for course in courses]
    if not labels:
        return
    selected_label = st.session_state.get("progress_topic_select", labels[0])
    course = next((item for item in courses if item["topic_label"] == selected_label), courses[0])
    course_id = course["id"]
    prog = progress.get(course_id, {})

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