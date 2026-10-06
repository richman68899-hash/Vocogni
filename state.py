"""
state.py — Session + persistent learner state for VOCogni Version 1.2.0.

Architecture:

    Google
        ↓
    Auth0
        ↓
    Streamlit OIDC / st.user
        ↓
    state.py
        ↓
    persistence.py
        ↓
    Supabase PostgreSQL

Version 1.2.0 upgrade:
- Adds meaningful-change autosave coordination.
- Tracks dirty/saving/saved/error states.
- Keeps durable learner state separate from transient UI state.
- Restores existing learner data safely.
- Creates a new learner record automatically through the autosave
  mechanism on first login.
- Preserves the existing state shapes used by sections/*.py and logic.py.

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

Important design rule:

    UI mutation
        ↓
    mark_persistent_dirty()
        ↓
    app continues / reruns
        ↓
    flush_persistent_save()
        ↓
    persistence.py
        ↓
    Supabase

This module does NOT save on every Streamlit rerun unless there is
actually a pending durable change.
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any

import streamlit as st

import data
import persistence


# ===========================================================================
# DEFAULT STATE FACTORIES
# ===========================================================================

def _default_profile() -> dict[str, Any]:
    """
    Return the default learner profile.
    """

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
    """
    Return the default progress structure for one course.
    """

    return {
        "started": False,
        "completed_lessons": [],
        "questions_attempted": 0,
        "correct_answers": 0,
        "mistakes": {},
    }


def _default_progress() -> dict[str, dict[str, Any]]:
    """
    Return the default progress structure for all known courses.
    """

    return {
        course_id: _default_course_progress()
        for course_id in data.COURSE_ORDER
    }


def _default_settings() -> dict[str, Any]:
    """
    Return the default learner settings.
    """

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


# ===========================================================================
# SESSION STATE INITIALIZATION
# ===========================================================================

def init_session_state() -> None:
    """
    Populate st.session_state with defaults.

    Existing values are never overwritten.

    Streamlit reruns the application after widget interactions, so this
    function must only initialize missing keys.
    """

    defaults = {
        # ------------------------------------------------------------------
        # Navigation
        # ------------------------------------------------------------------
        "nav": "Browse",

        # ------------------------------------------------------------------
        # Durable learner state
        # ------------------------------------------------------------------
        "profile": _default_profile(),
        "progress": _default_progress(),
        "notes": [],
        "settings": _default_settings(),

        # ------------------------------------------------------------------
        # Current learning session
        # ------------------------------------------------------------------
        "current_course": None,
        "current_lesson": None,
        "lesson_flow": None,

        # ------------------------------------------------------------------
        # UI state
        # ------------------------------------------------------------------
        "editing_profile": False,
        "browse_search": "",
        "browse_status_filter": "All",
        "selected_note_id": None,
        "note_editor_open": False,
        "note_draft_title": "",
        "play_sound_once": False,
        "next_note_id": 1,

        # ------------------------------------------------------------------
        # Persistence bookkeeping
        # ------------------------------------------------------------------
        "_persistent_state_loaded": False,
        "_persistent_user_id": None,

        # Has durable learner state changed since last successful save?
        "_persistent_dirty": False,

        # One of:
        #   saved
        #   pending
        #   saving
        #   error
        "_persistent_save_status": "saved",

        # Last persistence error message.
        "_persistent_save_error": None,

        # ISO timestamp of the most recent successful save.
        "_persistent_last_saved_at": None,

        # Number of successful saves in this Streamlit session.
        # Useful for development/testing.
        "_persistent_save_count": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# ===========================================================================
# LESSON FLOW
# ===========================================================================

def new_lesson_flow(
    course_id: str,
    lesson_id: str,
) -> dict[str, Any]:
    """
    Return a fresh in-progress state for opening a lesson.

    lesson_flow is deliberately session-only in v1.2.0.
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


def get_course_progress(
    course_id: str,
) -> dict[str, Any]:
    """
    Fetch and lazily create the progress record for a course.

    Creating a new course record changes durable state, so it is marked
    dirty and will be persisted by the autosave mechanism.
    """

    progress = st.session_state.progress

    if course_id not in progress:
        progress[course_id] = _default_course_progress()
        mark_persistent_dirty()

    return progress[course_id]


# ===========================================================================
# RESTORATION HELPERS
# ===========================================================================

def _merge_profile(
    saved_profile: Any,
) -> dict[str, Any]:
    """
    Merge saved profile data onto the latest default profile schema.

    This protects older learner records when new profile fields are added.
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

    Existing courses receive all current default fields.

    Unknown courses are preserved rather than deleted.
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
    Merge saved settings onto the current settings schema.
    """

    settings = _default_settings()

    if isinstance(saved_settings, dict):
        settings.update(saved_settings)

    return settings


def _sanitize_notes(
    saved_notes: Any,
) -> list[dict[str, Any]]:
    """
    Restore only valid note dictionaries.

    Invalid database entries are ignored rather than crashing the learner
    session.
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
    Calculate the next safe numeric note ID.

    This prevents duplicate IDs when restoring older data.
    """

    numeric_ids: list[int] = []

    for note in notes:

        note_id = note.get("id")

        if (
            isinstance(note_id, int)
            and not isinstance(note_id, bool)
        ):
            numeric_ids.append(note_id)

    if not numeric_ids:
        return 1

    return max(numeric_ids) + 1


# ===========================================================================
# PERSISTENT STATE SERIALIZATION
# ===========================================================================

def _build_persistent_state() -> dict[str, Any]:
    """
    Build the durable learner-state bundle sent to persistence.py.

    Transient UI state and lesson-flow state are deliberately excluded.

    deepcopy() prevents accidental mutation of the object being prepared
    for persistence while the current Streamlit run continues.
    """

    return {
        "profile": deepcopy(
            st.session_state.profile
        ),
        "progress": deepcopy(
            st.session_state.progress
        ),
        "notes": deepcopy(
            st.session_state.notes
        ),
        "settings": deepcopy(
            st.session_state.settings
        ),
        "next_note_id": int(
            st.session_state.next_note_id
        ),
    }


# ===========================================================================
# DIRTY-STATE MANAGEMENT
# ===========================================================================

def mark_persistent_dirty() -> None:
    """
    Mark durable learner state as changed.

    This function does NOT contact Supabase.

    It simply tells the end-of-run autosave system that a database write
    is required.

    Typical callers:
    - profile save
    - settings change
    - note create/edit/delete
    - question progress update
    - lesson completion
    """

    st.session_state["_persistent_dirty"] = True
    st.session_state["_persistent_save_status"] = "pending"
    st.session_state["_persistent_save_error"] = None


def has_pending_persistence() -> bool:
    """
    Return True when durable learner state has not been successfully saved.
    """

    return bool(
        st.session_state.get(
            "_persistent_dirty",
            False,
        )
    )


# ===========================================================================
# ACTUAL SAVE
# ===========================================================================

def persist_learner_state() -> None:
    """
    Save the current authenticated learner's durable state.

    The authenticated user ID is derived internally by persistence.py from
    the OIDC identity.

    This function intentionally raises when persistence fails.

    flush_persistent_save() is responsible for catching the failure and
    preserving the dirty state for a later retry.
    """

    if not persistence._is_logged_in():
        raise RuntimeError(
            "Cannot persist learner state without authentication."
        )

    user_id = persistence.get_user_id()

    known_user_id = st.session_state.get(
        "_persistent_user_id"
    )

    if (
        known_user_id is not None
        and known_user_id != user_id
    ):
        raise RuntimeError(
            "The authenticated user changed during the session. "
            "Refusing to overwrite learner data."
        )

    persistent_state = _build_persistent_state()

    persistence.save_progress(
        persistent_state
    )


# ===========================================================================
# AUTOSAVE FLUSH
# ===========================================================================

def flush_persistent_save() -> bool:
    """
    Save durable state when a meaningful change is pending.

    This should be called once near the end of app.py's main() function.

    Returns:
        True  → no pending changes, or save succeeded.
        False → save failed and changes remain marked dirty.
    """

    if not has_pending_persistence():
        return True

    st.session_state["_persistent_save_status"] = "saving"
    st.session_state["_persistent_save_error"] = None

    try:
        persist_learner_state()

    except Exception as exc:
        # IMPORTANT:
        # Dirty remains True so the session does not falsely claim that
        # the learner's changes have been saved.
        st.session_state["_persistent_dirty"] = True

        st.session_state["_persistent_save_status"] = "error"

        st.session_state["_persistent_save_error"] = str(
            exc
        )

        return False

    # ---------------------------------------------------------------
    # Save succeeded
    # ---------------------------------------------------------------

    st.session_state["_persistent_dirty"] = False

    st.session_state["_persistent_save_status"] = "saved"

    st.session_state["_persistent_save_error"] = None

    st.session_state["_persistent_last_saved_at"] = (
        datetime.now(timezone.utc).isoformat()
    )

    st.session_state["_persistent_save_count"] = (
        st.session_state.get(
            "_persistent_save_count",
            0,
        ) + 1
    )

    return True


# ===========================================================================
# LOAD PERSISTENT STATE
# ===========================================================================

def load_saved_learner_state() -> None:
    """
    Load durable learner state from Supabase.

    This function is safe to call on every Streamlit rerun because it
    performs the actual database read only once per session.

    For a first-time learner:
        - defaults remain in session state
        - the state is marked dirty
        - the normal end-of-run autosave creates the database record

    This prevents the loading stage from having to perform a separate
    database write before the rest of the application renders.
    """

    if st.session_state.get(
        "_persistent_state_loaded",
        False,
    ):
        return

    # ---------------------------------------------------------------
    # Authentication
    # ---------------------------------------------------------------

    user_id = persistence.get_user_id()

    # ---------------------------------------------------------------
    # Load database record
    # ---------------------------------------------------------------

    saved = persistence.load_progress()

    if not isinstance(saved, dict):
        raise RuntimeError(
            "Persistent learner state has an invalid top-level format."
        )

    # ---------------------------------------------------------------
    # First-time learner
    # ---------------------------------------------------------------

    if not saved:

        st.session_state["_persistent_user_id"] = user_id

        st.session_state["_persistent_state_loaded"] = True

        # No row exists yet.
        # Keep defaults and let the normal autosave flush create it.
        mark_persistent_dirty()

        return

    # ---------------------------------------------------------------
    # Backward compatibility
    # ---------------------------------------------------------------
    #
    # Very old prototype records may contain only the course-progress
    # dictionary directly inside the progress JSON column.
    #
    # A full v1.1/v1.2 record looks like:
    #
    # {
    #     "profile": ...,
    #     "progress": ...,
    #     "notes": ...,
    #     "settings": ...,
    #     "next_note_id": ...
    # }
    #
    # A legacy progress-only record may instead look like:
    #
    # {
    #     "course_a": {...},
    #     "course_b": {...}
    # }
    # ---------------------------------------------------------------

    full_state_keys = {
        "profile",
        "progress",
        "notes",
        "settings",
        "next_note_id",
    }

    looks_like_full_state = any(
        key in saved
        for key in full_state_keys
    )

    if not looks_like_full_state:

        # Legacy progress-only record.
        st.session_state.progress = _merge_progress(
            saved
        )

    else:

        # -----------------------------------------------------------
        # Profile
        # -----------------------------------------------------------

        st.session_state.profile = _merge_profile(
            saved.get("profile")
        )

        # -----------------------------------------------------------
        # Course progress
        # -----------------------------------------------------------

        st.session_state.progress = _merge_progress(
            saved.get("progress")
        )

        # -----------------------------------------------------------
        # Notes
        # -----------------------------------------------------------

        restored_notes = _sanitize_notes(
            saved.get("notes")
        )

        st.session_state.notes = restored_notes

        # -----------------------------------------------------------
        # Settings
        # -----------------------------------------------------------

        st.session_state.settings = _merge_settings(
            saved.get("settings")
        )

        # -----------------------------------------------------------
        # Note ID
        # -----------------------------------------------------------

        saved_next_note_id = saved.get(
            "next_note_id"
        )

        derived_next_note_id = _derive_next_note_id(
            restored_notes
        )

        if (
            isinstance(
                saved_next_note_id,
                int,
            )
            and not isinstance(
                saved_next_note_id,
                bool,
            )
            and saved_next_note_id >= 1
        ):
            st.session_state.next_note_id = max(
                saved_next_note_id,
                derived_next_note_id,
            )

        else:
            st.session_state.next_note_id = (
                derived_next_note_id
            )

    # ---------------------------------------------------------------
    # Identity bookkeeping
    # ---------------------------------------------------------------

    st.session_state["_persistent_user_id"] = user_id

    st.session_state["_persistent_state_loaded"] = True

    # The restored data already matches the database.
    st.session_state["_persistent_dirty"] = False

    st.session_state["_persistent_save_status"] = "saved"

    st.session_state["_persistent_save_error"] = None


# ===========================================================================
# SAVE STATUS UI
# ===========================================================================

def render_save_status() -> None:
    """
    Display a compact learner-facing persistence status.

    Intended for a sidebar or another unobtrusive application area.
    """

    status = st.session_state.get(
        "_persistent_save_status",
        "saved",
    )

    error = st.session_state.get(
        "_persistent_save_error"
    )

    if status == "pending":

        st.caption(
            "Saving changes..."
        )

    elif status == "saving":

        st.caption(
            "Saving..."
        )

    elif status == "error":

        st.error(
            "Couldn't save your changes."
        )

        if error:
            st.caption(
                f"Save error: {error}"
            )

        if st.button(
            "Retry save",
            key="retry_persistent_save",
        ):
            flush_persistent_save()
            st.rerun()

    else:

        last_saved_at = st.session_state.get(
            "_persistent_last_saved_at"
        )

        if last_saved_at:

            # Keep the normal status intentionally quiet.
            st.caption(
                "Saved ✓"
            )

        else:

            st.caption(
                "Saved ✓"
            )


# ===========================================================================
# DEVELOPMENT DIAGNOSTICS
# ===========================================================================

def get_persistence_debug_state() -> dict[str, Any]:
    """
    Return non-secret persistence diagnostics for development/testing.

    This is safe to display in a developer-only diagnostics panel.

    It deliberately does NOT return:
    - OAuth tokens
    - Supabase keys
    - passwords
    - full learner state
    """

    return {
        "loaded": bool(
            st.session_state.get(
                "_persistent_state_loaded",
                False,
            )
        ),
        "user_id": st.session_state.get(
            "_persistent_user_id"
        ),
        "dirty": bool(
            st.session_state.get(
                "_persistent_dirty",
                False,
            )
        ),
        "save_status": st.session_state.get(
            "_persistent_save_status",
            "saved",
        ),
        "save_error": st.session_state.get(
            "_persistent_save_error"
        ),
        "last_saved_at": st.session_state.get(
            "_persistent_last_saved_at"
        ),
        "save_count": st.session_state.get(
            "_persistent_save_count",
            0,
        ),
    }


# ===========================================================================
# TRANSIENT STATE RESET
# ===========================================================================

def reset_transient_learning_state() -> None:
    """
    Clear temporary lesson/UI state without deleting durable learner data.

    Durable state such as profile, progress, notes, and settings remains
    untouched.
    """

    st.session_state.current_course = None
    st.session_state.current_lesson = None
    st.session_state.lesson_flow = None

    st.session_state.selected_note_id = None
    st.session_state.note_editor_open = False
    st.session_state.note_draft_title = ""

    st.session_state.play_sound_once = False
