"""
sections/profile.py — Learner profile.

Vocogni Version 1.2.0

All profile fields are optional.

Persistence behavior:
- The learner edits the profile inside a form.
- Clicking "Save profile" updates durable session state.
- The profile is marked dirty with state.mark_persistent_dirty().
- app.py flushes the pending save to Supabase at the end of the run.
- No manual rerun is performed after saving, so the autosave flush can
  complete normally.

Cancel only changes temporary UI state and may safely trigger a rerun.
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

import data
from . import learning_rhythm
import state


# ===========================================================================
# HELPERS
# ===========================================================================

def _safe_index(
    options: list[Any],
    value: Any,
) -> int:
    """
    Return the index of value in options.

    Falls back to the first option when the value is missing or invalid.
    """

    try:
        return options.index(value)

    except (ValueError, TypeError):
        return 0


def _display(
    value: Any,
) -> str:
    """
    Safely format a profile value for HTML display.
    """

    if value is None:

        text = "Not specified"

    elif isinstance(value, list):

        text = (
            ", ".join(
                str(item)
                for item in value
            )
            if value
            else "Not specified"
        )

    else:

        text = (
            str(value).strip()
            or "Not specified"
        )

    # Escape HTML because profile fields can contain symbols such as
    # <, >, and =.
    return html.escape(text)


def _icon_svg(name: str) -> str:
    """Return a small, consistent, decorative line icon for profile sections."""
    icons = {
        "user": (
            '<circle cx="12" cy="8" r="3.5"/>'
            '<path d="M5 20c.6-3.2 3-5 7-5s6.4 1.8 7 5"/>'
        ),
        "book": (
            '<path d="M3.5 5.5A2.5 2.5 0 0 1 6 3h5v17H6a2.5 2.5 0 0 0-2.5 2z"/>'
            '<path d="M20.5 5.5A2.5 2.5 0 0 0 18 3h-5v17h5a2.5 2.5 0 0 1 2.5 2z"/>'
        ),
        "target": (
            '<circle cx="12" cy="12" r="8.5"/>'
            '<circle cx="12" cy="12" r="4.8"/>'
            '<circle cx="12" cy="12" r="1.3"/>'
        ),
        "spark": (
            '<path d="m12 3 1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/>'
            '<path d="m19 15 .9 2.1L22 18l-2.1.9L19 21l-.9-2.1L16 18l2.1-.9z"/>'
        ),
        "shield": (
            '<path d="M12 22s8-4 8-11V5l-8-3-8 3v6c0 7 8 11 8 11z"/>'
            '<path d="m9 12 2 2 4-4"/>'
        ),
    }
    paths = icons.get(name, icons["spark"])
    return (
        '<svg class="vc-profile-icon-art" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round" '
        'aria-hidden="true" focusable="false">'
        + paths + '</svg>'
    )


def _initials(name: Any) -> str:
    """Create a stable, privacy-light avatar monogram from the display name."""
    clean = str(name or "").strip()
    if not clean:
        return "L"
    parts = clean.split()
    if len(parts) >= 2:
        return (parts[0][0] + parts[-1][0]).upper()
    return clean[:1].upper()


def _section_heading(icon: str, title: str, subtitle: str = "") -> None:
    """Render a consistent icon-led heading for a profile section."""
    detail = (
        f"<p class='vc-profile-section-subtitle'>{html.escape(subtitle)}</p>"
        if subtitle else ""
    )
    st.markdown(
        "<div class='vc-profile-section-heading'>"
        f"<span class='vc-profile-section-icon'>{_icon_svg(icon)}</span>"
        "<div class='vc-profile-section-copy'>"
        f"<div class='vc-profile-section-title'>{html.escape(title)}</div>"
        f"{detail}"
        "</div></div>",
        unsafe_allow_html=True,
    )


def _field_row(
    label: str,
    value: Any,
) -> None:
    """Render a profile value with a clear label/value hierarchy."""
    empty = value is None or value == "" or value == []
    if isinstance(value, list) and value:
        rendered = (
            "<div class='vc-profile-tags'>"
            + "".join(
                f"<span class='vc-profile-tag'>{html.escape(str(item))}</span>"
                for item in value
                if str(item).strip()
            )
            + "</div>"
        )
    else:
        rendered = _display(value)

    value_class = " vc-profile-value--empty" if empty else ""
    st.markdown(
        "<div class='vc-profile-field'>"
        f"<div class='vc-profile-field-label'>{html.escape(label)}</div>"
        f"<div class='vc-profile-field-value{value_class}'>{rendered}</div>"
        "</div>",
        unsafe_allow_html=True,
    )


def _clean_pref(
    value: Any,
) -> Any:
    """
    Convert 'Prefer not to say' and empty values into None for display.
    """

    if value in (
        None,
        "",
        "Prefer not to say",
    ):
        return None

    return value


# ===========================================================================
# MAIN RENDER
# ===========================================================================

def render() -> None:
    """Render the learner profile and the learner's existing review rhythm."""
    st.markdown(
        "<div class='vc-profile-page-heading'>"
        "<div class='vc-eyebrow'>YOUR SPACE</div>"
        "<h1>Your learning profile</h1>"
        "<p class='vc-page-intro'>A few details can make your learning space more relevant. "
        "Share only what is useful to you; every field is optional.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    profile = st.session_state.profile

    if st.session_state.editing_profile:
        _render_edit_form(profile)
    else:
        _render_read_only(profile)

    st.divider()
    learning_rhythm.render(st.session_state.progress, profile)


# ===========================================================================
# READ-ONLY PROFILE
# ===========================================================================

def _render_identity_card(profile: dict[str, Any]) -> None:
    """Render a calm identity header with a generated monogram avatar."""
    raw_name = str(profile.get("name", "") or "").strip() or "Learner"
    name = html.escape(raw_name)
    initials = html.escape(_initials(raw_name))
    status = (
        "<span class='vc-profile-status'>"
        + _icon_svg("shield")
        + "<span>Profile saved</span></span>"
        if profile.get("saved")
        else "<span class='vc-profile-status vc-profile-status--quiet'>Optional profile</span>"
    )
    st.markdown(
        "<div class='vc-profile-hero'>"
        f"<div class='vc-profile-avatar' aria-label='Avatar initials {initials}'>{initials}</div>"
        "<div class='vc-profile-identity-copy'>"
        f"<div class='vc-profile-name'>{name}</div>"
        "<div class='vc-profile-identity-subtitle'>Your preferences, interests and learning goals.</div>"
        f"{status}"
        "</div></div>",
        unsafe_allow_html=True,
    )


def _start_editing_profile() -> None:
    """Open the existing edit form without changing durable learner data."""
    # Streamlit runs this callback before the next script execution.
    st.session_state.editing_profile = True


def _render_read_only(profile: dict[str, Any]) -> None:
    """Render the saved profile as a small set of clearly grouped cards."""
    if not profile.get("saved"):
        with st.container(border=True):
            st.markdown(
                "<div class='vc-profile-empty'>"
                "<div class='vc-profile-empty-icon'>" + _icon_svg("user") + "</div>"
                "<div class='vc-profile-empty-title'>Make this space yours</div>"
                "<p class='vc-profile-empty-copy'>Add a name, a learning goal or a few preferences. "
                "Vocogni can still be used without a completed profile.</p>"
                "</div>",
                unsafe_allow_html=True,
            )
            st.button(
                "Personalize profile",
                type="primary",
                key="create_profile",
                on_click=_start_editing_profile,
            )
        return

    identity_col, action_col = st.columns([5, 1.25], vertical_alignment="center", gap="medium")
    with identity_col:
        _render_identity_card(profile)
    with action_col:
        st.button(
            "Edit profile",
            type="primary",
            key="edit_profile",
            use_container_width=True,
            on_click=_start_editing_profile,
        )

    with st.container(border=True):
        _section_heading("user", "About you", "Basic details you choose to share.")
        col1, col2, col3 = st.columns(3, gap="large")
        with col1:
            _field_row("Age", profile.get("age"))
            _field_row("Gender", profile.get("gender", data.GENDER_OPTIONS[2]))
        with col2:
            _field_row("Grade", _clean_pref(profile.get("grade")))
            _field_row("Country", profile.get("country"))
        with col3:
            _field_row("Timezone", _clean_pref(profile.get("timezone")))
            _field_row("Preferred language", _clean_pref(profile.get("preferred_language")))

    with st.container(border=True):
        _section_heading("book", "How you learn", "Preferences that help shape your learning experience.")
        col1, col2 = st.columns(2, gap="large")
        with col1:
            _field_row("Learning style", _clean_pref(profile.get("learning_style")))
            _field_row("Preferred difficulty", profile.get("preferred_difficulty"))
        with col2:
            _field_row("Session length", _clean_pref(profile.get("preferred_session_length")))
            _field_row("Feedback style", _clean_pref(profile.get("preferred_feedback_style")))

    with st.container(border=True):
        _section_heading("target", "Subjects & goals", "Keep your priorities visible; you can change them at any time.")
        subject_cols = st.columns(3, gap="medium")
        with subject_cols[0]:
            _field_row("Favorite subjects", profile.get("favorite_subjects"))
        with subject_cols[1]:
            _field_row("Subjects you feel confident in", profile.get("strong_subjects"))
        with subject_cols[2]:
            _field_row("Subjects to work on", profile.get("weak_subjects"))

        goal_cols = st.columns(3, gap="medium")
        with goal_cols[0]:
            _field_row("Learning goals", profile.get("learning_goals"))
        with goal_cols[1]:
            _field_row("Interests", profile.get("interests"))
        with goal_cols[2]:
            _field_row("Career interests", profile.get("career_interests"))


# ===========================================================================
# EDIT FORM
# ===========================================================================

def _render_edit_form(
    profile: dict[str, Any],
) -> None:
    """
    Render the learner profile edit form.

    IMPORTANT:
    Save Profile does NOT call st.rerun().

    The form submission itself causes Streamlit's execution flow,
    then the current run reaches app.py's:
        state.flush_persistent_save()

    Therefore the modified profile can be saved before the next run.
    """

    st.markdown(
        "<div class='vc-profile-form-note'>"
        + _icon_svg("shield")
        + "<span><strong>Your details stay under your control.</strong> "
        + "Every field is optional. Save only the information you want in your learner profile.</span>"
        + "</div>",
        unsafe_allow_html=True,
    )

    with st.form(
        "profile_form",
        clear_on_submit=False,
    ):

        # -------------------------------------------------------------------
        # Basic information
        # -------------------------------------------------------------------

        _section_heading("user", "About you", "Only share details you are comfortable saving.")

        c1, c2 = st.columns(2)

        with c1:

            name = st.text_input(
                "Name",
                value=profile.get(
                    "name",
                    "",
                ),
                placeholder="Optional",
            )

            age = st.text_input(
                "Age",
                value=profile.get(
                    "age",
                    "",
                ),
                placeholder="Optional",
            )

            gender = st.selectbox(
                "Gender",
                data.GENDER_OPTIONS,
                index=_safe_index(
                    data.GENDER_OPTIONS,
                    profile.get("gender", data.GENDER_OPTIONS[2]),
                ),
                help="Optional. This preference is saved to your profile.",
            )

            grade = st.selectbox(
                "Grade",
                data.GRADE_OPTIONS,
                index=_safe_index(
                    data.GRADE_OPTIONS,
                    profile.get(
                        "grade",
                        "Prefer not to say",
                    ),
                ),
            )

        with c2:

            country = st.text_input(
                "Country",
                value=profile.get(
                    "country",
                    "",
                ),
                placeholder="Optional",
            )

            timezone = st.selectbox(
                "Timezone",
                data.TIMEZONE_OPTIONS,
                index=_safe_index(
                    data.TIMEZONE_OPTIONS,
                    profile.get(
                        "timezone",
                        "Prefer not to say",
                    ),
                ),
            )

            preferred_language = st.selectbox(
                "Preferred language",
                data.LANGUAGE_OPTIONS,
                index=_safe_index(
                    data.LANGUAGE_OPTIONS,
                    profile.get(
                        "preferred_language",
                        "Prefer not to say",
                    ),
                ),
            )

        # -------------------------------------------------------------------
        # Learning preferences
        # -------------------------------------------------------------------

        _section_heading("book", "How you learn", "Choose the support and pace that suit you.")

        c3, c4 = st.columns(2)

        with c3:

            learning_style = st.selectbox(
                "Preferred learning style",
                data.LEARNING_STYLE_OPTIONS,
                index=_safe_index(
                    data.LEARNING_STYLE_OPTIONS,
                    profile.get(
                        "learning_style",
                        "Prefer not to say",
                    ),
                ),
            )

            preferred_difficulty = st.selectbox(
                "Preferred difficulty",
                data.DIFFICULTY_OPTIONS,
                index=_safe_index(
                    data.DIFFICULTY_OPTIONS,
                    profile.get(
                        "preferred_difficulty",
                        "Adaptive",
                    ),
                ),
            )

        with c4:

            preferred_session_length = st.selectbox(
                "Preferred session length",
                data.SESSION_LENGTH_OPTIONS,
                index=_safe_index(
                    data.SESSION_LENGTH_OPTIONS,
                    profile.get(
                        "preferred_session_length",
                        "Prefer not to say",
                    ),
                ),
            )

            preferred_feedback_style = st.selectbox(
                "Preferred feedback style",
                data.FEEDBACK_STYLE_OPTIONS,
                index=_safe_index(
                    data.FEEDBACK_STYLE_OPTIONS,
                    profile.get(
                        "preferred_feedback_style",
                        "Prefer not to say",
                    ),
                ),
            )

        # -------------------------------------------------------------------
        # Subjects and goals
        # -------------------------------------------------------------------

        _section_heading("target", "Subjects & goals", "Tell Vocogni what you are working toward.")

        c5, c6 = st.columns(2)

        with c5:

            favorite_subjects = st.multiselect(
                "Favorite subjects",
                data.SUBJECT_OPTIONS,
                default=profile.get(
                    "favorite_subjects",
                    [],
                ),
            )

            strong_subjects = st.multiselect(
                "Strong subjects",
                data.SUBJECT_OPTIONS,
                default=profile.get(
                    "strong_subjects",
                    [],
                ),
            )

            weak_subjects = st.multiselect(
                "Subjects you find difficult",
                data.SUBJECT_OPTIONS,
                default=profile.get(
                    "weak_subjects",
                    [],
                ),
            )

        with c6:

            learning_goals = st.text_area(
                "Learning goals",
                value=profile.get(
                    "learning_goals",
                    "",
                ),
                placeholder="Optional",
            )

            interests = st.text_area(
                "Interests",
                value=profile.get(
                    "interests",
                    "",
                ),
                placeholder="Optional",
            )

            career_interests = st.text_area(
                "Career / vocational interests",
                value=profile.get(
                    "career_interests",
                    "",
                ),
                placeholder="Optional",
            )

        # -------------------------------------------------------------------
        # Form controls
        # -------------------------------------------------------------------

        col_save, col_cancel = st.columns(2)

        with col_save:

            submitted = st.form_submit_button(
                "Save Profile",
                type="primary",
                use_container_width=True,
            )

        with col_cancel:

            cancelled = st.form_submit_button(
                "Cancel",
                use_container_width=True,
            )

    # =========================================================================
    # SAVE PROFILE
    # =========================================================================

    if submitted:

        # ---------------------------------------------------------------
        # Update durable learner state
        # ---------------------------------------------------------------

        profile.update(
            {
                "name": name.strip(),
                "age": age.strip(),
                "gender": gender,
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
            }
        )

        # ---------------------------------------------------------------
        # Mark persistent state dirty.
        #
        # app.py will call flush_persistent_save() after this section
        # finishes rendering.
        # ---------------------------------------------------------------

        state.mark_persistent_dirty()

        st.session_state.editing_profile = False

        # Do NOT call st.rerun() here.
        #
        # The current Streamlit run must reach:
        #
        #     state.flush_persistent_save()
        #
        # in app.py.
        #
        # The sidebar save-status indicator will report the resulting
        # persistence state after that flush.

        st.info(
            "Profile updated. Saving your changes…"
        )

    # =========================================================================
    # CANCEL
    # =========================================================================

    if cancelled:

        st.session_state.editing_profile = False

        # Cancel only changes UI state. No durable learner data changed,
        # so an immediate rerun is safe.
        st.rerun()
