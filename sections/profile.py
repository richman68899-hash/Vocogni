"""
sections/profile.py — Learner profile.

Profile fields are edited in place by opening a section. The single Save Profile
button stays disabled and neutral grey until a field differs from its saved
value; once changed, it becomes green. Saving updates the visible profile
immediately and marks durable state dirty for app.py's end-of-run autosave.
"""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

import data
from . import learning_rhythm
import state
from profile_presentation import (
    display_profile_value as _display,
    profile_icon_svg as _icon_svg,
    profile_initials as _initials,
)


# Fields are defined once and shared by display/edit logic. Adding a profile
# field here is sufficient to make it available in its section.
_SECTIONS = [
    {
        "id": "about",
        "icon": "user",
        "title": "About you",
        "subtitle": "Basic details you choose to share.",
        "fields": [
            ("name", "Name", "text", None),
            ("age", "Age", "text", None),
            ("gender", "Gender", "select", "GENDER_OPTIONS"),
            ("grade", "Grade", "select", "GRADE_OPTIONS"),
            ("country", "Country", "text", None),
            ("timezone", "Timezone", "select", "TIMEZONE_OPTIONS"),
            ("preferred_language", "Preferred language", "select", "LANGUAGE_OPTIONS"),
        ],
    },
    {
        "id": "learning",
        "icon": "book",
        "title": "How you learn",
        "subtitle": "Preferences that help shape your learning experience.",
        "fields": [
            ("learning_style", "Learning style", "select", "LEARNING_STYLE_OPTIONS"),
            ("preferred_difficulty", "Preferred difficulty", "select", "DIFFICULTY_OPTIONS"),
            ("preferred_session_length", "Session length", "select", "SESSION_LENGTH_OPTIONS"),
            ("preferred_feedback_style", "Feedback style", "select", "FEEDBACK_STYLE_OPTIONS"),
        ],
    },
    {
        "id": "goals",
        "icon": "target",
        "title": "Subjects & goals",
        "subtitle": "Keep your priorities visible; you can change them at any time.",
        "fields": [
            ("favorite_subjects", "Favorite subjects", "multiselect", "SUBJECT_OPTIONS"),
            ("strong_subjects", "Subjects you feel confident in", "multiselect", "SUBJECT_OPTIONS"),
            ("weak_subjects", "Subjects to work on", "multiselect", "SUBJECT_OPTIONS"),
            ("learning_goals", "Learning goals", "textarea", None),
            ("interests", "Interests", "textarea", None),
            ("career_interests", "Career interests", "textarea", None),
        ],
    },
]

_WIDGET_PREFIX = "profile_inline_"
_DEFAULTS = {
    "name": "",
    "age": "",
    "gender": "Prefer not to say / others",
    "grade": "Prefer not to say",
    "country": "",
    "timezone": "Prefer not to say",
    "preferred_language": "Prefer not to say",
    "learning_style": "Prefer not to say",
    "preferred_difficulty": "Adaptive",
    "preferred_session_length": "Prefer not to say",
    "preferred_feedback_style": "Prefer not to say",
    "favorite_subjects": [],
    "strong_subjects": [],
    "weak_subjects": [],
    "learning_goals": "",
    "interests": "",
    "career_interests": "",
}


def _section_heading(icon: str, title: str, subtitle: str = "") -> None:
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


def _clean_pref(value: Any) -> Any:
    if value in (None, "", "Prefer not to say"):
        return None
    return value


def _profile_value(profile: dict[str, Any], field: str) -> Any:
    value = profile.get(field, _DEFAULTS.get(field))
    if field in {"grade", "timezone", "preferred_language", "learning_style",
                 "preferred_session_length", "preferred_feedback_style"}:
        return _clean_pref(value)
    return value


def _widget_key(field: str) -> str:
    return _WIDGET_PREFIX + field


def _options_for(option_key: str) -> list:
    options = getattr(data, option_key, [])
    return list(options) if isinstance(options, (list, tuple)) else []


def _valid_default(field: str, kind: str, option_key: str | None, profile: dict[str, Any]) -> Any:
    value = profile.get(field, _DEFAULTS.get(field))
    if kind == "multiselect":
        options = _options_for(option_key or "")
        return [item for item in (value or []) if item in options] if isinstance(value, list) else []
    if kind == "select":
        options = _options_for(option_key or "")
        return value if value in options else (options[0] if options else "")
    if value is None:
        return ""
    return value


def _initialize_section_widgets(section: dict[str, Any], profile: dict[str, Any]) -> None:
    for field, _label, kind, option_key in section["fields"]:
        key = _widget_key(field)
        st.session_state[key] = _valid_default(field, kind, option_key, profile)


def _field_is_dirty(field: str, profile: dict[str, Any]) -> bool:
    key = _widget_key(field)
    if key not in st.session_state:
        return False
    current = st.session_state[key]
    saved = _valid_default(
        field,
        next(
            kind for section in _SECTIONS for name, _label, kind, _options in section["fields"]
            if name == field
        ),
        next(
            options for section in _SECTIONS for name, _label, _kind, options in section["fields"]
            if name == field
        ),
        profile,
    )
    if isinstance(current, list):
        current = list(current)
        saved = list(saved or [])
    return current != saved


def _dirty_fields(profile: dict[str, Any]) -> list[str]:
    return [
        field
        for section in _SECTIONS
        for field, _label, _kind, _options in section["fields"]
        if _field_is_dirty(field, profile)
    ]


def _start_section_edit(section_id: str, profile: dict[str, Any]) -> None:
    section = next(item for item in _SECTIONS if item["id"] == section_id)
    _initialize_section_widgets(section, profile)
    st.session_state.profile_edit_section = section_id


def _render_identity_card(profile: dict[str, Any]) -> None:
    raw_name = str(profile.get("name", "") or "").strip() or "Learner"
    name = html.escape(raw_name)
    initials = html.escape(_initials(raw_name))
    status = (
        "<span class='vc-profile-status'>" + _icon_svg("shield")
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
        f"{status}</div></div>",
        unsafe_allow_html=True,
    )


def _render_field_value(label: str, value: Any) -> None:
    empty = value is None or value == "" or value == []
    if isinstance(value, list) and value:
        rendered = (
            "<div class='vc-profile-tags'>"
            + "".join(
                f"<span class='vc-profile-tag'>{html.escape(str(item))}</span>"
                for item in value if str(item).strip()
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


def _render_section_editor(section: dict[str, Any], profile: dict[str, Any]) -> None:
    fields = section["fields"]
    columns = st.columns(2, gap="large")
    for index, (field, label, kind, option_key) in enumerate(fields):
        with columns[index % 2]:
            key = _widget_key(field)
            if kind == "text":
                st.text_input(label, key=key, placeholder="Optional")
            elif kind == "textarea":
                st.text_area(label, key=key, placeholder="Optional")
            elif kind == "select":
                options = _options_for(option_key or "")
                if options:
                    st.selectbox(label, options, key=key)
                else:
                    st.caption(f"{label}: no options are configured yet.")
            elif kind == "multiselect":
                options = _options_for(option_key or "")
                st.multiselect(label, options, key=key)


def _save_profile_changes(profile: dict[str, Any], dirty_fields: list[str]) -> None:
    for field in dirty_fields:
        value = st.session_state[_widget_key(field)]
        profile[field] = value.strip() if isinstance(value, str) else value
    profile["saved"] = True
    state.mark_persistent_dirty()
    st.session_state.profile_edit_section = None
    for field, *_ in (field for section in _SECTIONS for field in section["fields"]):
        st.session_state.pop(_widget_key(field), None)


def _render_save_control(profile: dict[str, Any]) -> None:
    dirty_fields = _dirty_fields(profile)
    dirty = bool(dirty_fields)
    st.markdown(
        """
        <style>
        div[class*="st-key-save_profile"] button {
            background: #e5e7eb !important;
            color: #6b7280 !important;
            border: 1px solid #d1d5db !important;
            opacity: 1 !important;
        }
        div[class*="st-key-save_profile"] button[kind="primary"] {
            background: #16803c !important;
            color: #ffffff !important;
            border-color: #16803c !important;
        }
        div[class*="st-key-save_profile"] button:disabled {
            cursor: not-allowed !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    if st.button(
        "Save Profile",
        key="save_profile",
        type="primary" if dirty else "secondary",
        disabled=not dirty,
        use_container_width=False,
        help="Save becomes active when you change a profile field.",
    ):
        _save_profile_changes(profile, dirty_fields)
        st.toast("Profile saved. Saving your changes…")
        # Render the updated, non-editing profile in this same run. app.py
        # still reaches its normal end-of-run persistence flush.
        st.session_state.profile_edit_section = None


def _render_profile_section(section: dict[str, Any], profile: dict[str, Any]) -> None:
    section_id = section["id"]
    editing = st.session_state.get("profile_edit_section") == section_id

    with st.container(border=True):
        header_col, action_col = st.columns([5, 1.35], vertical_alignment="center")
        with header_col:
            _section_heading(section["icon"], section["title"], section["subtitle"])
        with action_col:
            if editing:
                if st.button("Cancel section", key=f"cancel_profile_section_{section_id}",
                             use_container_width=True):
                    for field, *_ in section["fields"]:
                        st.session_state.pop(_widget_key(field), None)
                    st.session_state.profile_edit_section = None
                    st.rerun()
            else:
                if st.button("Edit section", key=f"edit_profile_section_{section_id}",
                             use_container_width=True):
                    _start_section_edit(section_id, profile)
                    st.rerun()

        if editing:
            _render_section_editor(section, profile)
        else:
            fields = section["fields"]
            for start in range(0, len(fields), 3):
                cols = st.columns(3, gap="large")
                for col, (field, label, _kind, _option_key) in zip(cols, fields[start:start + 3]):
                    with col:
                        _render_field_value(label, _profile_value(profile, field))


def render() -> None:
    """Render an inline-editable profile with a clear, stateful save action."""
    st.markdown(
        "<div class='vc-profile-page-heading'>"
        "<div class='vc-eyebrow'>YOUR SPACE</div>"
        "<h1>Your learning profile</h1>"
        "<p class='vc-page-intro'>Click Edit section to change only the details you need. "
        "Save Profile turns green when your changes are ready to save. Every field is optional.</p>"
        "</div>",
        unsafe_allow_html=True,
    )

    profile = st.session_state.profile

    # Handle the save action before drawing the identity card and sections,
    # so the new name and values are visible in the very same run.
    save_col, _spacer = st.columns([1.4, 5])
    with save_col:
        _render_save_control(profile)

    _render_identity_card(profile)
    st.caption("Save Profile is grey when there are no unsaved edits and green when a change is detected.")

    for section in _SECTIONS:
        _render_profile_section(section, profile)

    st.divider()
    learning_rhythm.render(st.session_state.progress, profile)
