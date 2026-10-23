"""Profile-page Learning Rhythm: streaks, learning goals, and spaced review."""

from __future__ import annotations

import streamlit as st

import data
import learning_maintenance
import state


_RED_FLAME = "<span style='color:#ef4444;font-size:1.1rem;' role='img' aria-label='Learning streak'>🔥</span>"


def _plural_word(count, singular):
    return singular if count == 1 else singular + "s"


def _maintenance_stat_block(label, value):
    st.markdown(
        f"<div class='vc-stat-number'>{value}</div><div class='vc-stat-label'>{label}</div>",
        unsafe_allow_html=True,
    )


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

    saved_period = settings.get("learning_goal_period", "week")
    if saved_period not in ("week", "month"):
        saved_period = "week"
    selected_period = st.selectbox(
        "Goal period",
        options=["week", "month"],
        index=["week", "month"].index(saved_period),
        format_func=lambda period: "Weekly" if period == "week" else "Monthly",
        key="maintenance_goal_period_select",
        help="Choose a weekly or monthly consistency goal. Streaks still track consecutive learning days.",
    )

    target_options = (
        list(learning_maintenance.WEEKLY_TARGET_OPTIONS)
        if selected_period == "week"
        else list(range(1, 32))
    )
    target_setting = (
        "weekly_learning_goal_days"
        if selected_period == "week"
        else "monthly_learning_goal_days"
    )
    default_target = (
        learning_maintenance.DEFAULT_WEEKLY_TARGET
        if selected_period == "week"
        else 12
    )
    saved_target = settings.get(target_setting, default_target)
    try:
        saved_target = int(saved_target)
    except (TypeError, ValueError):
        saved_target = default_target
    if saved_target not in target_options:
        saved_target = default_target

    selected_target = st.selectbox(
        "Learning days per week" if selected_period == "week" else "Learning days per month",
        options=target_options,
        index=target_options.index(saved_target),
        format_func=lambda days: f"{days} learning {'day' if days == 1 else 'days'}",
        key=f"maintenance_target_{selected_period}",
        help="Set a realistic target for meaningful learning activity, not time spent in the app.",
    )

    if settings.get("learning_goal_period", "week") != selected_period:
        settings["learning_goal_period"] = selected_period
        state.mark_persistent_dirty()
    if settings.get(target_setting, default_target) != selected_target:
        settings[target_setting] = selected_target
        state.mark_persistent_dirty()
    timezone_label = profile.get("timezone", "Prefer not to say") if isinstance(profile, dict) else "Prefer not to say"
    summary = learning_maintenance.build_maintenance_summary(
        progress,
        timezone_label=timezone_label,
        weekly_target=selected_target if selected_period == "week" else learning_maintenance.DEFAULT_WEEKLY_TARGET,
    )
    if selected_period == "week":
        period_active_days = summary["active_days_this_week"]
        period_label = "This week"
        goal_period_label = "weekly"
    else:
        period_active_days = learning_maintenance.activity_days_in_period(
            summary["active_dates"], period="month", today=summary["today"]
        )
        period_label = "This month"
        goal_period_label = "monthly"
    goal_met = period_active_days >= selected_target

    row = st.columns(4)
    with row[0]:
        _maintenance_stat_block("Current streak", f"{_RED_FLAME} {summary['current_streak']} {_plural_word(summary['current_streak'], 'day')}")
    with row[1]:
        _maintenance_stat_block("Longest streak", f"{_RED_FLAME} {summary['longest_streak']} {_plural_word(summary['longest_streak'], 'day')}")
    with row[2]:
        _maintenance_stat_block(
            period_label,
            f"{period_active_days} / {selected_target} days",
        )
    with row[3]:
        _maintenance_stat_block("Learning today", "Complete" if summary["today_complete"] else "Not yet")

    if goal_met:
        st.caption(
            f"{goal_period_label.capitalize()} target reached. Any further practice is optional; the aim is "
            "consistent learning, not maximizing time spent in the app."
        )
    else:
        remaining = max(0, summary["weekly_target"] - summary["active_days_this_week"])
        st.caption(
            f"{remaining} more learning {_plural_word(remaining, 'day')} to reach your {goal_period_label} target. "
            "A missed day does not erase your progress."
        )

    week_status = "   ·   ".join(
        f"{day['label']} {_RED_FLAME if day['active'] else ('—' if not day['future'] else '&nbsp;')}"
        for day in summary["week_day_cards"]
    )
    st.markdown("**This week's activity**")
    st.markdown(week_status, unsafe_allow_html=True)

    if summary["today_complete"]:
        st.caption(
            "A meaningful learning action is already saved for today. You can stop here "
            "and return when it suits your schedule."
        )
    elif summary["current_streak"] > 0:
        st.write(
            f"Your {summary['current_streak']}-day streak is still in reach. Submit an answer with feedback, complete a practice set, or finish a diagnostic today to continue it."
        )
    elif summary["last_active_day"]:
        st.write(
            "Welcome back. Your earlier learning history is still saved; a learning "
            "session today starts a new streak without resetting that history."
        )
    else:
        st.write(
            "Start by submitting an answer with feedback, completing a practice set, or finishing a diagnostic. That creates your first recorded learning day."
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
                    detail += f" · {overdue} {_plural_word(overdue, 'day')} overdue
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
                f"{summary['total_due_reviews'] - len(summary['due_reviews'])} more {_plural_word(summary['total_due_reviews'] - len(summary['due_reviews']), 'review')} "
                "are due. Vocogni shows the first few so the queue stays manageable."
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


def render(progress, profile):
    """Render Learning Rhythm below the learner's Profile details."""
    _render_learning_maintenance(progress, profile)
