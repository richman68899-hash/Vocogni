"""
sections/profile.py — Learner profile.

VOCogni Version 1.2.0

All profile fields are optional.

Persistence behavior:
- The learner edits the profile inside a form.
- Clicking "Save Profile" updates durable session state.
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


def _field_row(
    label: str,
    value: Any,
) -> None:
    """
    Render one profile field/value pair.
    """

    st.markdown(
        f"<div style='margin-bottom:0.55rem;'>"
        f"<span class='vc-muted'>{html.escape(label)}</span>"
        f"<br>{_display(value)}</div>",
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
    """
    Render the learner profile page.
    """

    st.markdown(
        "<h2>Profile</h2>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<p class='vc-muted'>"
        "Tell VOCogni a little about yourself. Every field "
        "here is optional — skip anything you'd rather not share."
        "</p>",
        unsafe_allow_html=True,
    )

    profile = st.session_state.profile

    if st.session_state.editing_profile:
        _render_edit_form(profile)

    else:
        _render_read_only(profile)


# ===========================================================================
# READ-ONLY PROFILE
# ===========================================================================

def _render_read_only(
    profile: dict[str, Any],
) -> None:
    """
    Render the saved learner profile.
    """

    if not profile.get("saved"):

        st.markdown(
            "<div class='vc-card'>"
            "You haven't set up your profile yet. "
            "Add your name, goals, and preferences to help "
            "personalize your VOCogni experience — or skip it "
            "entirely and start learning."
            "</div>",
            unsafe_allow_html=True,
        )

    name = html.escape(
        str(
            profile.get(
                "name",
                "",
            )
        ).strip()
        or "Learner"
    )

    st.markdown(
        f"<h3>{name}</h3>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Basic information
    # -----------------------------------------------------------------------

    st.markdown(
        "<div class='vc-card'>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<span class='vc-muted'>Basic info</span>",
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        _field_row(
            "Age",
            profile.get("age"),
        )

        _field_row(
            "Grade",
            _clean_pref(
                profile.get("grade")
            ),
        )

    with col2:

        _field_row(
            "Country",
            profile.get("country"),
        )

        _field_row(
            "Timezone",
            _clean_pref(
                profile.get("timezone")
            ),
        )

    with col3:

        _field_row(
            "Preferred language",
            _clean_pref(
                profile.get("preferred_language")
            ),
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Learning preferences
    # -----------------------------------------------------------------------

    st.markdown(
        "<div class='vc-card'>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<span class='vc-muted'>Learning preferences</span>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        _field_row(
            "Preferred learning style",
            _clean_pref(
                profile.get("learning_style")
            ),
        )

        _field_row(
            "Preferred difficulty",
            profile.get(
                "preferred_difficulty"
            ),
        )

    with col2:

        _field_row(
            "Preferred session length",
            _clean_pref(
                profile.get("preferred_session_length")
            ),
        )

        _field_row(
            "Preferred feedback style",
            _clean_pref(
                profile.get("preferred_feedback_style")
            ),
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Subjects and goals
    # -----------------------------------------------------------------------

    st.markdown(
        "<div class='vc-card'>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<span class='vc-muted'>Subjects & goals</span>",
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:

        _field_row(
            "Favorite subjects",
            profile.get("favorite_subjects"),
        )

        _field_row(
            "Strong subjects",
            profile.get("strong_subjects"),
        )

        _field_row(
            "Subjects you find difficult",
            profile.get("weak_subjects"),
        )

    with col2:

        _field_row(
            "Learning goals",
            profile.get("learning_goals"),
        )

        _field_row(
            "Interests",
            profile.get("interests"),
        )

        _field_row(
            "Career / vocational interests",
            profile.get("career_interests"),
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # -----------------------------------------------------------------------
    # Edit button
    # -----------------------------------------------------------------------

    if st.button(
        "Edit Profile",
        type="primary",
        key="edit_profile",
    ):

        st.session_state.editing_profile = True

        # This is UI-only state, so an explicit rerun is safe.
        st.rerun()


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

    with st.form(
        "profile_form",
        clear_on_submit=False,
    ):

        # -------------------------------------------------------------------
        # Basic information
        # -------------------------------------------------------------------

        st.markdown(
            "<span class='vc-muted'>Basic info</span>",
            unsafe_allow_html=True,
        )

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

        st.markdown(
            "<span class='vc-muted'>Learning preferences</span>",
            unsafe_allow_html=True,
        )

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

        st.markdown(
            "<span class='vc-muted'>Subjects & goals</span>",
            unsafe_allow_html=True,
        )

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
            "Profile updated. Saving your changes..."
        )

    # =========================================================================
    # CANCEL
    # =========================================================================

    if cancelled:

        st.session_state.editing_profile = False

        # Cancel only changes UI state. No durable learner data changed,
        # so an immediate rerun is safe.
        st.rerun()
