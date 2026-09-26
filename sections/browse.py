"""sections/browse.py — Course catalog (spec section 6).

Also owns the drill-down: when a course or lesson is selected, this module
hands off to sections/course.py instead of showing the grid. Browse ->
Course -> Lesson is one continuous flow (spec section 17), so it lives
under a single sidebar nav slot rather than three separate ones.
"""

import streamlit as st

import data
import logic


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
    if not prog.get("started") and done == 0:
        return "Not started"
    if total > 0 and done >= total:
        return "Completed"
    return "In progress"


def _render_grid():
    st.markdown("<h2>Browse Courses</h2>", unsafe_allow_html=True)

    progress = st.session_state.progress
    recs = logic.generate_recommendations(progress)
    if recs:
        st.markdown("<span class='vc-muted'>Recommended for you</span>", unsafe_allow_html=True)
        chips = "".join(f"<span class='vc-recommend-chip'>{r}</span>" for r in recs)
        st.markdown(f"<div style='margin:0.4rem 0 1.1rem 0;'>{chips}</div>", unsafe_allow_html=True)

    col_search, col_status, col_diff = st.columns([2, 1, 1])
    with col_search:
        search = st.text_input(
            "Search courses", value=st.session_state.browse_search,
            placeholder="Search by title or topic",
        )
    with col_status:
        status_filter = st.selectbox(
            "Status", STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(st.session_state.browse_status_filter),
        )
    with col_diff:
        difficulties = sorted({c["difficulty"] for c in data.COURSES.values()})
        diff_filter = st.selectbox("Difficulty", ["All"] + difficulties)

    st.session_state.browse_search = search
    st.session_state.browse_status_filter = status_filter

    filtered = []
    for course in data.all_courses_in_order():
        haystack = (course["title"] + " " + course["short_description"]).lower()
        if search and search.lower() not in haystack:
            continue
        status = _status_for_course(course["id"], progress)
        if status_filter != "All" and status != status_filter:
            continue
        if diff_filter != "All" and course["difficulty"] != diff_filter:
            continue
        filtered.append(course)

    if not filtered:
        st.markdown(
            "<div class='vc-card'>No courses match your search or filters.</div>",
            unsafe_allow_html=True,
        )
        return

    cols = st.columns(3)
    for i, course in enumerate(filtered):
        with cols[i % 3]:
            _render_course_card(course, progress)


def _render_course_card(course, progress):
    status = _status_for_course(course["id"], progress)
    pct = logic.course_lesson_progress_percent(progress, course["id"])

    st.markdown("<div class='vc-card'>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='margin-bottom:0.3rem;'>{course['title']}</h4>", unsafe_allow_html=True)
    st.markdown(
        f"<span class='vc-badge'>{course['difficulty']}</span> "
        f"<span class='vc-badge'>{status}</span>",
        unsafe_allow_html=True,
    )
    st.markdown(f"<p style='margin-top:0.6rem;'>{course['short_description']}</p>", unsafe_allow_html=True)
    st.progress(pct)
    st.markdown(f"<span class='vc-muted'>{pct}% complete</span>", unsafe_allow_html=True)

    button_label = {"Not started": "Start", "In progress": "Continue", "Completed": "Review"}[status]
    if st.button(button_label, key=f"start_{course['id']}", type="primary", use_container_width=True):
        st.session_state.current_course = course["id"]
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)