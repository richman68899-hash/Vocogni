"""sections/profile.py — Learner profile (spec section 5).

All fields are optional; nothing here is required to save a profile.
"""

import html

import streamlit as st

import data


def _safe_index(options, value):
    try:
        return options.index(value)
    except (ValueError, TypeError):
        return 0


def _display(value):
    if value is None:
        text = "Not specified"
    elif isinstance(value, list):
        text = ", ".join(value) if value else "Not specified"
    else:
        text = str(value).strip() or "Not specified"
    # Free-text fields often contain math symbols (<, >, =) that would
    # otherwise be parsed as HTML when injected via unsafe_allow_html.
    return html.escape(text)


def _field_row(label, value):
    st.markdown(
        f"<div style='margin-bottom:0.55rem;'>"
        f"<span class='vc-muted'>{label}</span><br>{_display(value)}</div>",
        unsafe_allow_html=True,
    )


def render():
    st.markdown("<h2>Profile</h2>", unsafe_allow_html=True)
    st.markdown(
        "<p class='vc-muted'>Tell VOCogni a little about yourself. Every field "
        "here is optional — skip anything you'd rather not share.</p>",
        unsafe_allow_html=True,
    )

    profile = st.session_state.profile

    if st.session_state.editing_profile:
        _render_edit_form(profile)
    else:
        _render_read_only(profile)


def _render_read_only(profile):
    if not profile.get("saved"):
        st.markdown(
            "<div class='vc-card'>You haven't set up your profile yet. "
            "Add your name, goals, and preferences to help personalize your "
            "VOCogni experience — or skip it entirely and start learning.</div>",
            unsafe_allow_html=True,
        )

    name = html.escape(profile.get("name", "").strip() or "Learner")
    st.markdown(f"<h3>{name}</h3>", unsafe_allow_html=True)

    st.markdown("<div class='vc-card'>", unsafe_allow_html=True)
    st.markdown("<span class='vc-muted'>Basic info</span>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        _field_row("Age", profile.get("age"))
        _field_row("Grade", _clean_pref(profile.get("grade")))
    with col2:
        _field_row("Country", profile.get("country"))
        _field_row("Timezone", _clean_pref(profile.get("timezone")))
    with col3:
        _field_row("Preferred language", _clean_pref(profile.get("preferred_language")))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='vc-card'>", unsafe_allow_html=True)
    st.markdown("<span class='vc-muted'>Learning preferences</span>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        _field_row("Preferred learning style", _clean_pref(profile.get("learning_style")))
        _field_row("Preferred difficulty", profile.get("preferred_difficulty"))
    with col2:
        _field_row("Preferred session length", _clean_pref(profile.get("preferred_session_length")))
        _field_row("Preferred feedback style", _clean_pref(profile.get("preferred_feedback_style")))
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='vc-card'>", unsafe_allow_html=True)
    st.markdown("<span class='vc-muted'>Subjects & goals</span>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        _field_row("Favorite subjects", profile.get("favorite_subjects"))
        _field_row("Strong subjects", profile.get("strong_subjects"))
        _field_row("Subjects you find difficult", profile.get("weak_subjects"))
    with col2:
        _field_row("Learning goals", profile.get("learning_goals"))
        _field_row("Interests", profile.get("interests"))
        _field_row("Career / vocational interests", profile.get("career_interests"))
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("Edit Profile", type="primary"):
        st.session_state.editing_profile = True
        st.rerun()


def _clean_pref(value):
    if value in (None, "", "Prefer not to say"):
        return None
    return value


def _render_edit_form(profile):
    with st.form("profile_form", clear_on_submit=False):
        st.markdown("<span class='vc-muted'>Basic info</span>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Name", value=profile.get("name", ""), placeholder="Optional")
            age = st.text_input("Age", value=profile.get("age", ""), placeholder="Optional")
            grade = st.selectbox(
                "Grade", data.GRADE_OPTIONS,
                index=_safe_index(data.GRADE_OPTIONS, profile.get("grade", "Prefer not to say")),
            )
        with c2:
            country = st.text_input("Country", value=profile.get("country", ""), placeholder="Optional")
            timezone = st.selectbox(
                "Timezone", data.TIMEZONE_OPTIONS,
                index=_safe_index(data.TIMEZONE_OPTIONS, profile.get("timezone", "Prefer not to say")),
            )
            preferred_language = st.selectbox(
                "Preferred language", data.LANGUAGE_OPTIONS,
                index=_safe_index(data.LANGUAGE_OPTIONS, profile.get("preferred_language", "Prefer not to say")),
            )

        st.markdown("<span class='vc-muted'>Learning preferences</span>", unsafe_allow_html=True)
        c3, c4 = st.columns(2)
        with c3:
            learning_style = st.selectbox(
                "Preferred learning style", data.LEARNING_STYLE_OPTIONS,
                index=_safe_index(data.LEARNING_STYLE_OPTIONS, profile.get("learning_style", "Prefer not to say")),
            )
            preferred_difficulty = st.selectbox(
                "Preferred difficulty", data.DIFFICULTY_OPTIONS,
                index=_safe_index(data.DIFFICULTY_OPTIONS, profile.get("preferred_difficulty", "Adaptive")),
            )
        with c4:
            preferred_session_length = st.selectbox(
                "Preferred session length", data.SESSION_LENGTH_OPTIONS,
                index=_safe_index(data.SESSION_LENGTH_OPTIONS, profile.get("preferred_session_length", "Prefer not to say")),
            )
            preferred_feedback_style = st.selectbox(
                "Preferred feedback style", data.FEEDBACK_STYLE_OPTIONS,
                index=_safe_index(data.FEEDBACK_STYLE_OPTIONS, profile.get("preferred_feedback_style", "Prefer not to say")),
            )

        st.markdown("<span class='vc-muted'>Subjects & goals</span>", unsafe_allow_html=True)
        c5, c6 = st.columns(2)
        with c5:
            favorite_subjects = st.multiselect(
                "Favorite subjects", data.SUBJECT_OPTIONS, default=profile.get("favorite_subjects", []),
            )
            strong_subjects = st.multiselect(
                "Strong subjects", data.SUBJECT_OPTIONS, default=profile.get("strong_subjects", []),
            )
            weak_subjects = st.multiselect(
                "Subjects you find difficult", data.SUBJECT_OPTIONS, default=profile.get("weak_subjects", []),
            )
        with c6:
            learning_goals = st.text_area(
                "Learning goals", value=profile.get("learning_goals", ""), placeholder="Optional",
            )
            interests = st.text_area(
                "Interests", value=profile.get("interests", ""), placeholder="Optional",
            )
            career_interests = st.text_area(
                "Career / vocational interests", value=profile.get("career_interests", ""), placeholder="Optional",
            )

        col_save, col_cancel = st.columns(2)
        with col_save:
            submitted = st.form_submit_button("Save Profile", type="primary", use_container_width=True)
        with col_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

    if submitted:
        profile.update({
            "name": name.strip(),
            "age": age.strip(),
            "grade": grade,
            "country": country.strip(),
            "timezone": timezone,
            "favorite_subjects": favorite_subjects,
            "learning_goals": learning_goals.strip(),
            "strong_subjects": strong_subjects,
            "weak_subjects": weak_subjects,
            "interests": interests.strip(),
            "career_interests": career_interests.strip(),
            "learning_style": learning_style,
            "preferred_difficulty": preferred_difficulty,
            "preferred_session_length": preferred_session_length,
            "preferred_feedback_style": preferred_feedback_style,
            "preferred_language": preferred_language,
            "saved": True,
        })
        st.session_state.editing_profile = False
        st.success("Profile saved.")
        st.rerun()

    if cancelled:
        st.session_state.editing_profile = False
        st.rerun()