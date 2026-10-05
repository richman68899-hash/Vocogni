"""
state.py — Session + persistent learner state for VOCogni Version 1.1.0.

Architecture:
    Auth0
        ↓
    Streamlit OIDC / st.user
        ↓
    state.py
        ↓
    persistence.py
        ↓
    Supabase PostgreSQL

Responsibilities:
- initialize Streamlit session state
- provide the existing state shapes used by the UI
- load durable learner data after authentication
- persist durable learner data
- keep transient lesson/UI state session-only

Durable learner state:
- profile
- progress
- notes
- settings
- next_note_id

Session-only state:
- nav
- current_course
- current_lesson
- lesson_flow
- editing_profile
- browse_search
- browse_status_filter
- selected_note_id
- note_editor_open
- note_draft_title
- play_sound_once

The section files and logic.py continue using st.session_state
without needing to know how persistence works.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import streamlit as st

import data
import persistence


# ---------------------------------------------------------------------------
# Default state factories
# ---------------------------------------------------------------------------

def _default_profile() -> dict[str, Any]:
    return {
        "name": "",
        "age": "",
        "grade": "Prefer not to say",
        "country": "",
        "timezone": "Prefer not to say",
        "favorite_subjects": [],
        "learning_goals": "",
        "strong_subjects": [],
        "weak_subjects": [],
        "interests": "",
        "career_interests": "",
        "learning_style": "Prefer not to say",
        "preferred_difficulty": "Adaptive",
        "preferred_session_length": "Prefer not to say",
        "preferred_feedback_style": "Prefer not to say",
        "preferred_language": "Prefer not to say",
        "saved": False,
    }


def _default_course_progress() -> dict[str, Any]:
    return {
        "started": False,
        "completed_lessons": [],
        "questions_attempted": 0,
        "correct_answers": 0,
        "mistakes": {},
    }


def _default_progress() -> dict[str, dict[str, Any]]:
    return {
        course_id: _default_course_progress()
        for course_id in data.COURSE_ORDER
    }


def _default_settings() -> dict[str, Any]:
    return {
        "appearance": "Light",
        "text_size": "Medium",
        "animations": True,
        "sound": True,
        "feedback_timing": "Immediate",
        "difficulty": "Adaptive",
        "reduced_motion": False,
        "larger_text": False,
        "high_readability": False,
    }


# ---------------------------------------------------------------------------
# Session-state initialization
# ---------------------------------------------------------------------------

def init_session_state() -> None:
    """
    Populate st.session_state with defaults on first run.

    Existing values are never overwritten. This is important because
    Streamlit reruns the script frequently during normal interaction.
    """

    defaults = {
        # Navigation / UI
        "nav": "Browse",

        # Durable learner state
        "profile": _default_profile(),
        "progress": _default_progress(),
        "notes": [],
        "settings": _default_settings(),

        # Current learning session
        "current_course": None,
        "current_lesson": None,
        "lesson_flow": None,

        # UI state
        "editing_profile": False,
        "browse_search": "",
        "browse_status_filter": "All",
        "selected_note_id": None,
        "note_editor_open": False,
        "note_draft_title": "",
        "play_sound_once": False,
        "next_note_id": 1,

        # Persistence bookkeeping
        "_persistent_state_loaded": False,
        "_persistent_user_id": None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ---------------------------------------------------------------------------
# Lesson-flow helpers
# ---------------------------------------------------------------------------

def new_lesson_flow(
    course_id: str,
    lesson_id: str,
) -> dict[str, Any]:
    """
    Return a fresh in-progress state for opening a lesson.
    """

    return {
        "course_id": course_id,
        "lesson_id": lesson_id,
        "stage": "intro",
        "q_index": 0,
        "last_correct": None,
        "last_user_answer": None,
        "results": [],
    }


def get_course_progress(course_id: str) -> dict[str, Any]:
    """
    Fetch and lazily create the progress record for a course.
    """

    progress = st.session_state.progress

    if course_id not in progress:
        progress[course_id] = _default_course_progress()

    return progress[course_id]


# ---------------------------------------------------------------------------
# Persistence helpers
# ---------------------------------------------------------------------------

def _merge_profile(
    saved_profile: Any,
) -> dict[str, Any]:
    """
    Merge saved profile data onto the current default schema.

    This keeps newly introduced profile fields from breaking older
    persisted learner records.
    """

    profile = _default_profile()

    if isinstance(saved_profile, dict):
        profile.update(saved_profile)

    return profile


def _merge_progress(
    saved_progress: Any,
) -> dict[str, dict[str, Any]]:
    """
    Merge saved course progress onto the current course schema.

    Existing courses receive all new default fields automatically.
    Unknown saved courses are preserved rather than silently deleted.
    """

    progress = _default_progress()

    if not isinstance(saved_progress, dict):
        return progress

    for course_id, saved_course in saved_progress.items():
        if not isinstance(saved_course, dict):
            continue

        course_progress = _default_course_progress()
        course_progress.update(saved_course)
        progress[course_id] = course_progress

    return progress


def _merge_settings(
    saved_settings: Any,
) -> dict[str, Any]:
    """
    Merge saved settings onto the current default settings schema.
    """

    settings = _default_settings()

    if isinstance(saved_settings, dict):
        settings.update(saved_settings)

    return settings


def _sanitize_notes(
    saved_notes: Any,
) -> list[dict[str, Any]]:
    """
    Restore only valid note objects.

    Invalid entries are ignored so one malformed database value does not
    break the entire learner session.
    """

    if not isinstance(saved_notes, list):
        return []

    return [
        note
        for note in saved_notes
        if isinstance(note, dict)
    ]


def _derive_next_note_id(
    notes: list[dict[str, Any]],
) -> int:
    """
    Calculate a safe next numeric note ID from restored notes.
    """

    numeric_ids = []

    for note in notes:
        note_id = note.get("id")

        if isinstance(note_id, int) and not isinstance(note_id, bool):
            numeric_ids.append(note_id)

    if not numeric_ids:
        return 1

    return max(numeric_ids) + 1


def _build_persistent_state() -> dict[str, Any]:
    """
    Build the exact learner-state bundle stored in Supabase.

    Transient UI and lesson-flow state is deliberately excluded.
    """

    return {
        "profile": deepcopy(st.session_state.profile),
        "progress": deepcopy(st.session_state.progress),
        "notes": deepcopy(st.session_state.notes),
        "settings": deepcopy(st.session_state.settings),
        "next_note_id": int(st.session_state.next_note_id),
    }


def load_saved_learner_state() -> None:
    """
    Load the authenticated learner's durable state from Supabase.

    Safe to call on every app run because the actual database read occurs
    only once per Streamlit session.

    When no persistent record exists yet, the initialized defaults remain
    in place.
    """

    if st.session_state.get("_persistent_state_loaded", False):
        return

    # Authentication must already have completed before this function
    # is called by app.py.
    if not getattr(st.user, "is_logged_in", False):
        raise RuntimeError(
            "Cannot load learner state before authentication."
        )

    saved = persistence.load_progress()

    if not isinstance(saved, dict):
        raise RuntimeError(
            "Persistent learner state has an invalid top-level format."
        )

    # No saved record yet.
    if not saved:
        st.session_state["_persistent_state_loaded"] = True
        st.session_state["_persistent_user_id"] = (
            persistence.get_user_id()
        )
        return

    # -----------------------------------------------------------------------
    # Backward compatibility:
    #
    # Older prototype records may contain only course progress directly
    # inside the "progress" JSON column rather than the new full state bundle.
    # Detect that shape and restore it as progress.
    # -----------------------------------------------------------------------

    looks_like_full_state = any(
        key in saved
        for key in (
            "profile",
            "progress",
            "notes",
            "settings",
            "next_note_id",
        )
    )

    if not looks_like_full_state:
        st.session_state.progress = _merge_progress(saved)

    else:
        st.session_state.profile = _merge_profile(
            saved.get("profile")
        )

        st.session_state.progress = _merge_progress(
            saved.get("progress")
        )

        restored_notes = _sanitize_notes(
            saved.get("notes")
        )

        st.session_state.notes = restored_notes

        st.session_state.settings = _merge_settings(
            saved.get("settings")
        )

        saved_next_note_id = saved.get("next_note_id")

        derived_next_note_id = _derive_next_note_id(
            restored_notes
        )

        if (
            isinstance(saved_next_note_id, int)
            and not isinstance(saved_next_note_id, bool)
            and saved_next_note_id >= 1
        ):
            st.session_state.next_note_id = max(
                saved_next_note_id,
                derived_next_note_id,
            )
        else:
            st.session_state.next_note_id = derived_next_note_id

    # -----------------------------------------------------------------------
    # Persistent learner identity bookkeeping
    # -----------------------------------------------------------------------

    st.session_state["_persistent_state_loaded"] = True
    st.session_state["_persistent_user_id"] = (
        persistence.get_user_id()
    )


def persist_learner_state() -> None:
    """
    Save the authenticated learner's durable state to Supabase.

    The learner ID is derived internally by persistence.py from
    st.user["sub"]. The caller cannot choose another learner's ID.

    This function intentionally raises an exception when persistence fails.
    app.py can then prevent logout rather than silently losing learner data.
    """

    if not getattr(st.user, "is_logged_in", False):
        raise RuntimeError(
            "Cannot persist learner state without authentication."
        )

    persistent_state = _build_persistent_state()

    persistence.save_progress(
        persistent_state
    )


def reset_transient_learning_state() -> None:
    """
    Clear temporary lesson/UI state without deleting durable learner data.

    Useful when starting a new lesson, leaving a lesson, or resetting
    navigation state.
    """

    st.session_state.current_course = None
    st.session_state.current_lesson = None
    st.session_state.lesson_flow = None

    st.session_state.selected_note_id = None
    st.session_state.note_editor_open = False
    st.session_state.note_draft_title = ""

    st.session_state.play_sound_once = False
