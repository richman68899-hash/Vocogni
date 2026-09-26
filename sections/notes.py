"""sections/notes.py — Simple personal notes (spec section 14).

Deliberately minimal: a title, free-text content, and create/edit/delete.
No AI summarization and no collaboration, per the spec.
"""

import datetime
import html

import streamlit as st


def _now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def render():
    st.markdown("<h2>Notes</h2>", unsafe_allow_html=True)

    if st.session_state.note_editor_open:
        _render_editor()
    else:
        _render_list()


def _render_list():
    if st.button("+ New Note", type="primary"):
        st.session_state.selected_note_id = None
        st.session_state.note_editor_open = True
        st.rerun()

    notes = sorted(st.session_state.notes, key=lambda n: n["updated_at"], reverse=True)
    if not notes:
        st.markdown(
            "<div class='vc-card' style='margin-top:0.8rem;'>You don't have any "
            "notes yet. Use \u201c+ New Note\u201d to jot down rules, mistakes to "
            "remember, or strategies while you learn.</div>",
            unsafe_allow_html=True,
        )
        return

    st.markdown("<div style='margin-top:0.6rem;'></div>", unsafe_allow_html=True)
    for note in notes:
        title = html.escape(note["title"] or "Untitled note")
        raw_snippet = (note["content"] or "").strip().replace("\n", " ")
        snippet = html.escape(raw_snippet[:140]) + ("\u2026" if len(raw_snippet) > 140 else "")

        st.markdown("<div class='vc-card'>", unsafe_allow_html=True)
        st.markdown(
            f"<strong>{title}</strong><br>"
            f"<span class='vc-muted'>{snippet or 'No content yet.'}</span><br>"
            f"<span class='vc-muted'>Last updated {note['updated_at']}</span>",
            unsafe_allow_html=True,
        )
        if st.button("Open", key=f"open_note_{note['id']}"):
            st.session_state.selected_note_id = note["id"]
            st.session_state.note_editor_open = True
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)


def _find_note(note_id):
    for note in st.session_state.notes:
        if note["id"] == note_id:
            return note
    return None


def _render_editor():
    note_id = st.session_state.selected_note_id
    existing = _find_note(note_id) if note_id is not None else None

    if st.button("\u2190 Back to Notes"):
        st.session_state.note_editor_open = False
        st.rerun()

    draft_title = ""
    if not existing and st.session_state.get("note_draft_title"):
        draft_title = st.session_state.note_draft_title
        st.session_state.note_draft_title = ""  # consume once

    with st.form("note_form", clear_on_submit=False):
        title = st.text_input(
            "Note title", value=existing["title"] if existing else draft_title,
            placeholder="e.g. Fractions \u2014 Important Rules",
        )
        content = st.text_area(
            "Note content", value=existing["content"] if existing else "",
            height=220, placeholder="Write your note here...",
        )
        col_save, col_delete = st.columns(2)
        with col_save:
            save_clicked = st.form_submit_button("Save Note", type="primary", use_container_width=True)
        with col_delete:
            delete_clicked = st.form_submit_button(
                "Delete Note", use_container_width=True, disabled=existing is None,
            )

    if save_clicked:
        if existing:
            existing["title"] = title.strip()
            existing["content"] = content
            existing["updated_at"] = _now_str()
        else:
            new_id = st.session_state.next_note_id
            st.session_state.next_note_id += 1
            st.session_state.notes.append({
                "id": new_id,
                "title": title.strip(),
                "content": content,
                "created_at": _now_str(),
                "updated_at": _now_str(),
            })
        st.session_state.note_editor_open = False
        st.success("Note saved.")
        st.rerun()

    if delete_clicked and existing:
        st.session_state.notes = [n for n in st.session_state.notes if n["id"] != existing["id"]]
        st.session_state.note_editor_open = False
        st.rerun()