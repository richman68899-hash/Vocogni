"""sections/browse.py — Course catalog (spec section 6).

Also owns the drill-down: when a course or lesson is selected, this module
hands off to sections/course.py instead of showing the grid. Browse ->
Course -> Lesson is one continuous flow (spec section 17), so it lives
under a single sidebar nav slot rather than three separate ones.
"""

import html

import streamlit as st

import data
import logic
from . import revision_sprint as revision_sprint_section


STATUS_OPTIONS = ["All", "Not started", "In progress", "Completed"]


def render():
    if st.session_state.get("current_lesson"):
        from sections import course as course_section
        course_section.render_lesson_flow()
        return

    if st.session_state.get("current_course"):
        from sections import course as course_section
        course_section.render_course_detail()
        return

    _render_grid()


def _status_for_course(course_id, progress):
    course = data.get_course(course_id)
    prog = progress.get(course_id, {})
    done = len(prog.get("completed_lessons", []))
    total = len(course["lessons"])
    diagnostic_id = logic.course_diagnostic_lesson_id(course_id)
    if diagnostic_id:
        total += 1
        done += int(diagnostic_id in prog.get("diagnostics", {}))
    if not prog.get("started") and done == 0:
        return "Not started"
    if total > 0 and done >= total:
        return "Completed"
    return "In progress"


def _render_grid():
    st.markdown("<h1>Explore courses</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='vc-page-intro'>Build understanding step by step. Continue a course or choose a topic to work on next.</p>",
        unsafe_allow_html=True,
    )

    progress = st.session_state.progress
    # Keep the sprint discoverable directly on the Browse landing page.
    if revision_sprint_section.render_browse_entry(progress):
        return
    coach = logic.get_mistake_coach(progress)
    if coach:
        st.markdown("### Your next step")
        st.markdown(
            f"""
            <div class='vc-card vc-card--current'>
              <div class='vc-eyebrow'>From your recent practice</div>
              <div style='font-weight:650;font-size:1.05rem;'>{html.escape(str(coach.get('skill', '')))}</div>
              <div style='margin:.45rem 0;'>{html.escape(str(coach.get('why', '')))}</div>
              <div style='margin:.4rem 0;'><strong>Why this:</strong> {html.escape(str(coach.get('evidence_label', '')))}</div>
              <div><strong>Try next:</strong> {html.escape(str(coach.get('action', '')))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if coach["available_course_ids"]:
            target_id = coach["available_course_ids"][0]
            target = data.get_course(target_id)
            if st.button(
                f"Practise in {target['title']}",
                key=f"mistake_coach_open_{target_id}",
            ):
                st.session_state.current_course = target_id
                st.session_state.current_lesson = None
                st.session_state.lesson_flow = None
                st.session_state.nav = "Browse"
                st.rerun()

    recs = logic.generate_recommendations(progress)
    if recs:
        st.markdown("<span class='vc-muted'>Related topics</span>", unsafe_allow_html=True)
        chips = "".join(f"<span class='vc-recommend-chip'>{html.escape(str(r))}</span>" for r in recs)
        st.markdown(f"<div style='margin:0.4rem 0 1.1rem 0;'>{chips}</div>", unsafe_allow_html=True)

    # Search gets its own full-width row. The four filters share a consistent
    # second row, with CSS wrapping them cleanly on narrow screens.
    search = st.text_input(
        "Search courses", value=st.session_state.browse_search,
        placeholder="Search by course, subject, or topic",
    )

    status_col, diff_col, category_col, subject_col = st.columns(4, gap="medium")
    with status_col:
        status_filter = st.selectbox(
            "Status", STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(st.session_state.browse_status_filter),
        )
    with diff_col:
        difficulties = sorted({c["difficulty"] for c in data.COURSES.values()})
        diff_filter = st.selectbox("Difficulty", ["All"] + difficulties)
    with category_col:
        category_labels = {item["id"]: item["label"] for item in data.COURSE_CATEGORIES}
        category_filter = st.selectbox(
            "Category", ["All"] + list(category_labels),
            format_func=lambda key: "All" if key == "All" else category_labels.get(key, key),
            key="browse_category_filter",
        )
    with subject_col:
        subject_labels = {item["id"]: item["label"] for item in data.COURSE_SUBJECTS}
        subject_filter = st.selectbox(
            "Subject", ["All"] + list(subject_labels),
            format_func=lambda key: "All" if key == "All" else subject_labels.get(key, key),
            key="browse_subject_filter",
        )

    st.session_state.browse_search = search
    st.session_state.browse_status_filter = status_filter

    filtered = []
    for course in data.all_courses_in_order():
        haystack = " ".join([
            course["title"], course["short_description"],
            course.get("category_label", ""), course.get("subject_label", ""),
            course.get("level", ""), course.get("curriculum", ""),
        ]).lower()
        if search and search.lower() not in haystack:
            continue
        status = _status_for_course(course["id"], progress)
        if status_filter != "All" and status != status_filter:
            continue
        if diff_filter != "All" and course["difficulty"] != diff_filter:
            continue
        if category_filter != "All" and course.get("category_id") != category_filter:
            continue
        if subject_filter != "All" and course.get("subject_id") != subject_filter:
            continue
        filtered.append(course)

    if not filtered:
        st.markdown(
            "<div class='vc-card vc-empty-state'>"
            "<strong>No courses found</strong>"
            "<p>Clear a filter or try a different search.</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    cols = st.columns(3)
    for i, course in enumerate(filtered):
        with cols[i % 3]:
            _render_course_card(course, progress)


def _course_card_metadata(course):
    """Format only configured, learner-useful course metadata."""
    level = course.get("level")
    if not isinstance(level, str) or not level.strip() or level.strip().casefold() in {
        "not specified", "level not specified", "none", "null", "n/a"
    }:
        level = ""

    metadata_parts = [
        course.get("category_label", "Other"),
        course.get("subject_label", "Other"),
        f'{course.get("lesson_count", len(course.get("lessons", [])))} lessons',
        level,
    ]
    return " · ".join(
        html.escape(str(value).strip())
        for value in metadata_parts
        if value is not None and str(value).strip()
    )


def _render_course_card(course, progress):
    status = _status_for_course(course["id"], progress)
    pct = logic.course_lesson_progress_percent(progress, course["id"])

    title = html.escape(str(course.get("title", "Untitled course")))
    description = html.escape(str(course.get("short_description", "")))
    metadata = _course_card_metadata(course)

    # A real Streamlit container keeps the card intact across reruns and
    # responsive layouts; no HTML wrapper is left open across UI blocks.
    with st.container(border=True):
        st.markdown(f"<h3 style='margin-top:0'>{title}</h3>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='vc-badge'>{html.escape(str(course.get('difficulty', '')))}</span> "
            f"<span class='vc-badge'>{html.escape(status)}</span>",
            unsafe_allow_html=True,
        )
        st.markdown(
            f"<p style='margin-top:0.65rem'>{description}</p>",
            unsafe_allow_html=True,
        )
        if metadata:
            st.caption(metadata)
        st.progress(pct)
        st.markdown(
            f"<div class='vc-course-progress-label'>{pct}% complete</div>",
            unsafe_allow_html=True,
        )

        button_label = {
            "Not started": "Start learning",
            "In progress": "Continue course",
            "Completed": "Review course",
        }[status]
        if st.button(
            button_label,
            key=f"start_{course['id']}",
            type="primary",
            use_container_width=True,
        ):
            st.session_state.current_course = course["id"]
            st.rerun()
