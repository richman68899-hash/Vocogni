"""
VOCogni Notes — personal notes with flat, color-coded folders.

Folder records are deliberately flat: folders cannot contain folders.
Existing notes remain compatible; notes without a valid folder_id are
shown under Unfiled. All durable changes use state.mark_persistent_dirty()
and the central autosave mechanism.
"""
from __future__ import annotations

import datetime
import html
from typing import Any

import streamlit as st
import state

COLORS = {
    "Amber": "#E0A43A",
    "Blue": "#4C8DDA",
    "Green": "#43A77A",
    "Purple": "#9875D4",
    "Pink": "#D96F9B",
    "Teal": "#36A6A6",
    "Grey": "#8A8F98",
}


def _now() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _find_note(note_id: Any) -> dict[str, Any] | None:
    return next(
        (n for n in st.session_state.notes
         if isinstance(n, dict) and n.get("id") == note_id),
        None,
    )


def _find_folder(folder_id: Any) -> dict[str, Any] | None:
    return next(
        (f for f in st.session_state.note_folders
         if isinstance(f, dict) and f.get("id") == folder_id),
        None,
    )


def _mark_changed() -> None:
    state.mark_persistent_dirty()


def render() -> None:
    st.markdown("## Notes")
    st.caption("Keep notes organized in simple, color-coded folders.")
    if st.session_state.get("note_editor_open", False):
        _render_editor()
        return
    _render_folders_and_notes()


def _render_folders_and_notes() -> None:
    folders = st.session_state.note_folders
    notes = [n for n in st.session_state.notes if isinstance(n, dict)]

    st.markdown("### Your folders")
    with st.expander("＋ Create a folder", expanded=not folders):
        with st.form("create_note_folder", clear_on_submit=True):
            name = st.text_input("Folder title", placeholder="e.g. Algebra")
            color_name = st.selectbox("Folder color", list(COLORS))
            create = st.form_submit_button("Create folder", type="primary")
        if create:
            clean = name.strip()
            if not clean:
                st.warning("Enter a folder title.")
            elif any(f.get("name", "").casefold() == clean.casefold() for f in folders):
                st.warning("A folder with that title already exists.")
            else:
                folder_id = st.session_state.next_note_folder_id
                st.session_state.next_note_folder_id += 1
                folders.append({"id": folder_id, "name": clean, "color": COLORS[color_name], "created_at": _now()})
                _mark_changed()
                st.rerun()

    if folders:
        cols = st.columns(2)
        for i, folder in enumerate(folders):
            with cols[i % 2]:
                color = folder.get("color", COLORS["Amber"])
                safe_name = html.escape(str(folder.get("name", "Untitled folder")))
                count = sum(n.get("folder_id") == folder.get("id") for n in notes)
                st.markdown(
                    f"<div style='border:1px solid {color};border-top:8px solid {color};"
                    f"border-radius:12px;padding:14px 12px;margin:4px 0 8px 0;"
                    f"background:linear-gradient(180deg,{color}20,transparent);min-height:90px'>"
                    f"<div style='font-size:1.05rem;font-weight:650'>▱ {safe_name}</div>"
                    f"<div style='opacity:.75;font-size:.85rem'>{count} note(s)</div></div>",
                    unsafe_allow_html=True,
                )
                with st.expander(f"Manage: {folder.get('name', 'Folder')}"):
                    with st.form(f"edit_folder_{folder['id']}"):
                        new_name = st.text_input("Folder title", value=folder.get("name", ""))
                        color_options = list(COLORS)
                        current_color = next((k for k, v in COLORS.items() if v == color), "Amber")
                        new_color_name = st.selectbox("Color", color_options, index=color_options.index(current_color))
                        save_folder = st.form_submit_button("Save folder")
                    if save_folder:
                        clean = new_name.strip()
                        duplicate = any(
                            f["id"] != folder["id"] and f.get("name", "").casefold() == clean.casefold()
                            for f in folders
                        )
                        if not clean:
                            st.warning("Folder title cannot be empty.")
                        elif duplicate:
                            st.warning("A folder with that title already exists.")
                        else:
                            folder["name"] = clean
                            folder["color"] = COLORS[new_color_name]
                            _mark_changed()
                            st.rerun()
                    if st.button("Delete folder", key=f"delete_folder_{folder['id']}"):
                        # Keep notes: move them to Unfiled rather than deleting them.
                        for note in notes:
                            if note.get("folder_id") == folder["id"]:
                                note["folder_id"] = None
                        st.session_state.note_folders = [f for f in folders if f["id"] != folder["id"]]
                        _mark_changed()
                        st.rerun()

    st.divider()
    col_filter, col_new = st.columns([3, 1])
    with col_filter:
        options = {"All notes": "all", "Unfiled": None}
        options.update({f.get("name", "Folder"): f["id"] for f in folders})
        selected_label = st.selectbox("Show", list(options), key="notes_folder_filter")
        selected_folder = options[selected_label]
    with col_new:
        st.write("")
        if st.button("＋ New note", type="primary", use_container_width=True):
            st.session_state.selected_note_id = None
            st.session_state.note_editor_open = True
            st.session_state.note_draft_folder_id = selected_folder if selected_folder != "all" else None
            st.rerun()

    visible = notes if selected_folder == "all" else [
        n for n in notes if n.get("folder_id") == selected_folder
    ]
    visible.sort(key=lambda n: n.get("updated_at", ""), reverse=True)
    if not visible:
        st.info("No notes here yet. Create a note or choose another folder.")
        return
    for note in visible:
        with st.container(border=True):
            st.markdown(f"**{html.escape(str(note.get('title') or 'Untitled note'))}**")
            body = str(note.get("content", "")).strip().replace("\n", " ")
            st.caption((body[:180] + ("…" if len(body) > 180 else "")) or "No content yet.")
            folder = _find_folder(note.get("folder_id"))
            st.caption(f"{folder.get('name')} · Updated {note.get('updated_at', 'unknown')}" if folder else f"Unfiled · Updated {note.get('updated_at', 'unknown')}")
            c1, c2 = st.columns([1, 2])
            with c1:
                if st.button("Open", key=f"open_note_{note.get('id')}"):
                    st.session_state.selected_note_id = note.get("id")
                    st.session_state.note_editor_open = True
                    st.rerun()
            with c2:
                destinations = {"Unfiled": None}
                destinations.update({f.get("name", "Folder"): f["id"] for f in folders})
                current_folder = note.get("folder_id")
                current_label = next((label for label, value in destinations.items() if value == current_folder), "Unfiled")
                dest = st.selectbox("Move to", list(destinations), index=list(destinations).index(current_label), key=f"move_note_{note.get('id')}")
                if destinations[dest] != current_folder:
                    note["folder_id"] = destinations[dest]
                    note["updated_at"] = _now()
                    _mark_changed()
                    st.rerun()


def _render_editor() -> None:
    note_id = st.session_state.get("selected_note_id")
    existing = _find_note(note_id)
    if st.button("← Back to Notes", key="back_to_notes"):
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None
        st.rerun()

    folders = st.session_state.note_folders
    folder_labels = ["Unfiled"] + [f.get("name", "Folder") for f in folders]
    folder_ids = [None] + [f["id"] for f in folders]
    current_id = existing.get("folder_id") if existing else st.session_state.get("note_draft_folder_id")
    current_index = folder_ids.index(current_id) if current_id in folder_ids else 0

    with st.form("note_form", clear_on_submit=False):
        title = st.text_input("Note title", value=existing.get("title", "") if existing else "", placeholder="e.g. Fractions — Important Rules")
        content = st.text_area("Note content", value=existing.get("content", "") if existing else "", height=220, placeholder="Write your note here…")
        folder_label = st.selectbox("Folder", folder_labels, index=current_index)
        save_clicked = st.form_submit_button("Save note", type="primary")
        delete_clicked = st.form_submit_button("Delete note", disabled=existing is None)

    if save_clicked:
        now = _now()
        chosen_folder_id = folder_ids[folder_labels.index(folder_label)]
        if existing:
            existing.update({"title": title.strip(), "content": content, "folder_id": chosen_folder_id, "updated_at": now})
        else:
            new_id = st.session_state.next_note_id
            st.session_state.next_note_id += 1
            st.session_state.notes.append({
                "id": new_id, "title": title.strip(), "content": content,
                "folder_id": chosen_folder_id, "created_at": now, "updated_at": now,
            })
        _mark_changed()
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None
        st.session_state.note_draft_folder_id = None
        st.success("Note saved. Saving changes…")

    if delete_clicked and existing:
        st.session_state.notes = [n for n in st.session_state.notes if n.get("id") != existing.get("id")]
        _mark_changed()
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None
        st.info("Note deleted. Saving changes…")
