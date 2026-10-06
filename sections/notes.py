"""
sections/notes.py — Simple personal notes.

VOCogni Version 1.2.0

Deliberately minimal:
- title
- free-text content
- create/edit/delete
- no AI summarization
- no collaboration

Persistence behavior:
- Creating, editing, or deleting a note changes durable learner state.
- After each durable mutation, state.mark_persistent_dirty() is called.
- app.py flushes the pending change to Supabase after the section renders.
- No manual rerun is performed after durable mutations.
- Navigation-only actions may still rerun safely because they do not change
  durable learner data.
"""

from __future__ import annotations

import datetime
import html
from typing import Any

import streamlit as st

import state


# ===========================================================================
# HELPERS
# ===========================================================================

def _now_str() -> str:
    """
    Return a human-readable timestamp for note metadata.
    """

    return datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M"
    )


def _find_note(
    note_id: Any,
) -> dict[str, Any] | None:
    """
    Find a note by its numeric ID.

    Returns:
        The note dictionary, or None if not found.
    """

    if note_id is None:
        return None

    for note in st.session_state.notes:

        if not isinstance(note, dict):
            continue

        if note.get("id") == note_id:
            return note

    return None


# ===========================================================================
# MAIN
# ===========================================================================

def render() -> None:
    """
    Render the Notes page.
    """

    st.markdown(
        "<h2>Notes</h2>",
        unsafe_allow_html=True,
    )

    if st.session_state.note_editor_open:
        _render_editor()
    else:
        _render_list()


# ===========================================================================
# NOTE LIST
# ===========================================================================

def _render_list() -> None:
    """
    Render the existing note list.
    """

    if st.button(
        "+ New Note",
        type="primary",
        key="new_note",
    ):

        # These are session/UI changes only.
        st.session_state.selected_note_id = None
        st.session_state.note_editor_open = True
        st.session_state.note_draft_title = ""

        st.rerun()

    # ---------------------------------------------------------------
    # Sort notes by latest update.
    # ---------------------------------------------------------------

    notes = sorted(
        [
            note
            for note in st.session_state.notes
            if isinstance(note, dict)
        ],
        key=lambda note: note.get(
            "updated_at",
            "",
        ),
        reverse=True,
    )

    if not notes:

        st.markdown(
            "<div class='vc-card' style='margin-top:0.8rem;'>"
            "You don't have any notes yet. Use "
            "&ldquo;+ New Note&rdquo; to jot down rules, "
            "mistakes to remember, or strategies while you learn."
            "</div>",
            unsafe_allow_html=True,
        )

        return

    st.markdown(
        "<div style='margin-top:0.6rem;'></div>",
        unsafe_allow_html=True,
    )

    for note in notes:

        note_id = note.get("id")

        title = html.escape(
            str(
                note.get(
                    "title",
                    "",
                )
            ).strip()
            or "Untitled note"
        )

        raw_content = str(
            note.get(
                "content",
                "",
            )
        ).strip()

        raw_snippet = raw_content.replace(
            "\n",
            " ",
        )

        snippet_text = raw_snippet[:140]

        snippet = html.escape(
            snippet_text
        )

        if len(raw_snippet) > 140:
            snippet += "\u2026"

        updated_at = html.escape(
            str(
                note.get(
                    "updated_at",
                    "Unknown",
                )
            )
        )

        st.markdown(
            "<div class='vc-card'>",
            unsafe_allow_html=True,
        )

        st.markdown(
            f"<strong>{title}</strong><br>"
            f"<span class='vc-muted'>"
            f"{snippet or 'No content yet.'}"
            f"</span><br>"
            f"<span class='vc-muted'>"
            f"Last updated {updated_at}"
            f"</span>",
            unsafe_allow_html=True,
        )

        if st.button(
            "Open",
            key=f"open_note_{note_id}",
        ):

            # Session/UI-only changes.
            st.session_state.selected_note_id = note_id
            st.session_state.note_editor_open = True

            st.rerun()

        st.markdown(
            "</div>",
            unsafe_allow_html=True,
        )


# ===========================================================================
# NOTE EDITOR
# ===========================================================================

def _render_editor() -> None:
    """
    Render the create/edit note form.
    """

    note_id = st.session_state.selected_note_id

    existing = _find_note(
        note_id
    )

    # ---------------------------------------------------------------
    # Back button
    # ---------------------------------------------------------------

    if st.button(
        "← Back to Notes",
        key="back_to_notes",
    ):

        # UI-only state.
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None

        st.rerun()

    # ---------------------------------------------------------------
    # Existing/new-note draft
    # ---------------------------------------------------------------

    draft_title = ""

    if (
        not existing
        and st.session_state.get(
            "note_draft_title",
            "",
        )
    ):

        draft_title = st.session_state.note_draft_title

        # Consume the temporary draft title.
        st.session_state.note_draft_title = ""

    # ---------------------------------------------------------------
    # Form
    # ---------------------------------------------------------------

    with st.form(
        "note_form",
        clear_on_submit=False,
    ):

        title = st.text_input(
            "Note title",
            value=(
                existing.get("title", "")
                if existing
                else draft_title
            ),
            placeholder=(
                "e.g. Fractions — Important Rules"
            ),
        )

        content = st.text_area(
            "Note content",
            value=(
                existing.get("content", "")
                if existing
                else ""
            ),
            height=220,
            placeholder="Write your note here...",
        )

        col_save, col_delete = st.columns(2)

        with col_save:

            save_clicked = st.form_submit_button(
                "Save Note",
                type="primary",
                use_container_width=True,
            )

        with col_delete:

            delete_clicked = st.form_submit_button(
                "Delete Note",
                use_container_width=True,
                disabled=existing is None,
            )

    # =========================================================================
    # SAVE / CREATE NOTE
    # =========================================================================

    if save_clicked:

        now = _now_str()

        if existing:

            # -----------------------------------------------------------
            # EDIT EXISTING NOTE
            # -----------------------------------------------------------

            existing["title"] = title.strip()
            existing["content"] = content
            existing["updated_at"] = now

        else:

            # -----------------------------------------------------------
            # CREATE NEW NOTE
            # -----------------------------------------------------------

            new_id = st.session_state.next_note_id

            st.session_state.next_note_id += 1

            st.session_state.notes.append(
                {
                    "id": new_id,
                    "title": title.strip(),
                    "content": content,
                    "created_at": now,
                    "updated_at": now,
                }
            )

        # ---------------------------------------------------------------
        # IMPORTANT V1.2 AUTOSAVE HOOK
        # ---------------------------------------------------------------
        #
        # The note has now changed durable learner state.
        #
        # We do NOT save directly here.
        # We simply mark the state dirty.
        #
        # app.py will later call:
        #
        #     state.flush_persistent_save()
        #
        # ---------------------------------------------------------------

        state.mark_persistent_dirty()

        # Close the editor. This is session/UI state.
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None

        st.info(
            "Note updated. Saving your changes..."
        )

        # ---------------------------------------------------------------
        # DELIBERATELY NO st.rerun()
        # ---------------------------------------------------------------
        #
        # app.py must reach its end-of-run autosave.
        #
        # A manual rerun here could terminate execution before the
        # central save mechanism runs.
        # ---------------------------------------------------------------

    # =========================================================================
    # DELETE NOTE
    # =========================================================================

    if delete_clicked and existing:

        deleted_id = existing.get("id")

        st.session_state.notes = [
            note
            for note in st.session_state.notes
            if note.get("id") != deleted_id
        ]

        # ---------------------------------------------------------------
        # IMPORTANT V1.2 AUTOSAVE HOOK
        # ---------------------------------------------------------------

        state.mark_persistent_dirty()

        # Close editor.
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None

        st.info(
            "Note deleted. Saving your changes..."
        )

        # ---------------------------------------------------------------
        # DELIBERATELY NO st.rerun()
        # ---------------------------------------------------------------
        #
        # app.py will flush the deletion to Supabase.
        # ---------------------------------------------------------------
