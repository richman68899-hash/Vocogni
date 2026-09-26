"""
state.py — Session state initialization for VOCogni Version 1.

Everything the app remembers during a session lives in st.session_state.
This is a deliberate Version 1 choice (see spec section 16: "Use session
state or local storage appropriate for a prototype. Do not implement a
database unless genuinely necessary").

To migrate to a real backend later:
  - Replace `init_session_state()` with a function that loads the same
    shapes (profile / progress / notes / settings) from a database or API
    for the logged-in user, keyed by user id instead of a single session.
  - The rest of the app reads and writes st.session_state using the same
    keys, so section files (sections/*.py) and logic.py would not need to
    change — only where the data comes from at startup and where it's
    persisted would change.
"""

import streamlit as st

import data


def _default_profile():
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


def _default_course_progress():
    return {
        "started": False,
        "completed_lessons": [],   # list of lesson ids, in completion order
        "questions_attempted": 0,
        "correct_answers": 0,
        "mistakes": {},            # mistake_tag -> count
    }


def _default_progress():
    return {course_id: _default_course_progress() for course_id in data.COURSE_ORDER}


def _default_settings():
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


def init_session_state():
    """Populate st.session_state with default values on first run only."""
    defaults = {
        "nav": "Browse",
        "profile": _default_profile(),
        "progress": _default_progress(),
        "notes": [],                 # list of note dicts
        "settings": _default_settings(),
        "current_course": None,      # course id, or None
        "current_lesson": None,      # lesson id, or None
        "lesson_flow": None,         # dict describing in-progress lesson state
        "editing_profile": False,
        "browse_search": "",
        "browse_status_filter": "All",
        "selected_note_id": None,
        "note_editor_open": False,
        "note_draft_title": "",
        "play_sound_once": False,
        "next_note_id": 1,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def new_lesson_flow(course_id, lesson_id):
    """Return a fresh in-progress state for opening a lesson."""
    return {
        "course_id": course_id,
        "lesson_id": lesson_id,
        "stage": "intro",     # intro -> question -> feedback -> complete
        "q_index": 0,
        "last_correct": None,
        "last_user_answer": None,
        "results": [],         # accumulated (question, correct, user_answer) for "after submission" mode
    }


def get_course_progress(course_id):
    """Fetch (and lazily create) the progress record for a course."""
    progress = st.session_state.progress
    if course_id not in progress:
        progress[course_id] = _default_course_progress()
    return progress[course_id]