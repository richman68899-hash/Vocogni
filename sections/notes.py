"""
VOCogni Notes — flat folders, durable note organization, and responsive controls.

Folders cannot contain folders. Existing notes without a valid folder assignment
remain available under Unfiled. Durable changes use the central autosave flow.
"""
from __future__ import annotations

import datetime
import html
from typing import Any

import streamlit as st
import state

PALETTE = {
    "Red": "#D94A4A",
    "Orange": "#E58A32",
    "Yellow": "#D9B52B",
    "Green": "#399568",
    "Cyan": "#2BA6B4",
    "Blue": "#477ED1",
    "Pink": "#D66D9B",
    "Purple": "#8D6BC1",
    "Grey": "#858B95",
    "System": None,
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


def _is_dark_mode() -> bool:
    appearance = str(st.session_state.get("settings", {}).get("appearance", "Light")).casefold()
    return appearance == "dark"


def _resolved_color(folder: dict[str, Any]) -> str:
    raw = folder.get("color", "#858B95")
    # Accept the new semantic palette names and legacy hex values.
    if raw in PALETTE:
        color_name = raw
    else:
        legacy = {
            "#E0A43A": "Orange", "#4C8DDA": "Blue", "#43A77A": "Green",
            "#9875D4": "Purple", "#D96F9B": "Pink", "#36A6A6": "Cyan",
            "#8A8F98": "Grey",
        }
        color_name = legacy.get(str(raw).upper(), legacy.get(str(raw), "Grey"))
    if color_name == "System":
        return "#FFFFFF" if _is_dark_mode() else "#202124"
    return PALETTE.get(color_name) or str(raw)


def _color_name(folder: dict[str, Any]) -> str:
    raw = folder.get("color", "Grey")
    if raw in PALETTE:
        return str(raw)
    legacy = {
        "#E0A43A": "Orange", "#4C8DDA": "Blue", "#43A77A": "Green",
        "#9875D4": "Purple", "#D96F9B": "Pink", "#36A6A6": "Cyan",
        "#8A8F98": "Grey",
    }
    return legacy.get(str(raw), "Grey")


def _folder_count(folder_id: Any, notes: list[dict[str, Any]]) -> int:
    return sum(1 for note in notes if note.get("folder_id") == folder_id)


def render() -> None:
    st.markdown("## Notes")
    st.caption("Keep notes organized in simple, color-coded folders.")
    if st.session_state.get("note_editor_open", False):
        _render_editor()
        return

    selected_folder_id = st.session_state.get("selected_note_folder_id")
    selected_folder = _find_folder(selected_folder_id) if selected_folder_id is not None else None
    if selected_folder_id is not None and selected_folder is None:
        st.session_state.selected_note_folder_id = None
        selected_folder_id = None

    if selected_folder is None:
        _render_folder_index()
    else:
        _render_folder_view(selected_folder)


def _render_folder_index() -> None:
    folders = st.session_state.note_folders
    notes = [n for n in st.session_state.notes if isinstance(n, dict)]

    st.markdown("### Folders")
    with st.expander("＋ Create a folder", expanded=not folders):
        with st.form("create_note_folder", clear_on_submit=True):
            name = st.text_input("Folder title", placeholder="e.g. Algebra")
            color_name = st.selectbox("Folder color", list(PALETTE))
            create = st.form_submit_button("Create folder", type="primary")
        if create:
            clean = name.strip()
            if not clean:
                st.warning("Enter a folder title.")
            elif any(str(f.get("name", "")).casefold() == clean.casefold() for f in folders):
                st.warning("A folder with that title already exists.")
            else:
                folder_id = st.session_state.next_note_folder_id
                st.session_state.next_note_folder_id += 1
                folders.append({
                    "id": folder_id, "name": clean, "color": color_name,
                    "created_at": _now(),
                })
                _mark_changed()
                st.rerun()

    if folders:
        cols = st.columns(2, gap="medium")
        for i, folder in enumerate(folders):
            with cols[i % 2]:
                color = _resolved_color(folder)
                safe_name = html.escape(str(folder.get("name", "Untitled folder")))
                count = _folder_count(folder.get("id"), notes)
                st.markdown(
                    f"<div style='border:1px solid {color};border-top:7px solid {color};"
                    f"border-radius:12px;padding:16px;margin:4px 0 8px 0;"
                    f"background:linear-gradient(180deg,{color}18,transparent);min-height:94px'>"
                    f"<div style='font-size:1.05rem;font-weight:650'>{safe_name}</div>"
                    f"<div style='opacity:.75;font-size:.9rem;margin-top:8px'>{count} Notes</div></div>",
                    unsafe_allow_html=True,
                )
                if st.button("Open folder →", key=f"open_folder_{folder['id']}", use_container_width=True):
                    st.session_state.selected_note_folder_id = folder["id"]
                    st.rerun()

    st.divider()
    _render_notes_list(notes, selected_folder_id=None, show_all=True)


def _render_folder_view(folder: dict[str, Any]) -> None:
    notes = [n for n in st.session_state.notes if isinstance(n, dict)]
    color = _resolved_color(folder)
    safe_name = html.escape(str(folder.get("name", "Folder")))
    st.button("← All folders", key="back_to_folder_index", on_click=_go_to_folder_index)
    st.markdown(
        f"<div style='border-left:6px solid {color};padding:6px 0 6px 14px;margin:6px 0 16px 0'>"
        f"<div style='font-size:1.5rem;font-weight:700'>{safe_name}</div>"
        f"<div style='opacity:.75'>{_folder_count(folder.get('id'), notes)} Notes</div></div>",
        unsafe_allow_html=True,
    )

    # Folder management belongs inside the folder view, not on the folder card.
    with st.expander("Manage folder", expanded=False):
        with st.form(f"edit_folder_{folder['id']}"):
            new_name = st.text_input("Folder title", value=folder.get("name", ""))
            options = list(PALETTE)
            current_color = _color_name(folder)
            new_color_name = st.selectbox("Folder color", options, index=options.index(current_color))
            save_folder = st.form_submit_button("Save changes", type="primary")
        if save_folder:
            clean = new_name.strip()
            duplicate = any(
                f.get("id") != folder.get("id")
                and str(f.get("name", "")).casefold() == clean.casefold()
                for f in st.session_state.note_folders
            )
            if not clean:
                st.warning("Folder title cannot be empty.")
            elif duplicate:
                st.warning("A folder with that title already exists.")
            else:
                folder["name"] = clean
                folder["color"] = new_color_name
                _mark_changed()
                st.rerun()
        if st.button("Delete folder", key=f"delete_folder_{folder['id']}"):
            # Preserve notes and move them to Unfiled.
            for note in notes:
                if note.get("folder_id") == folder["id"]:
                    note["folder_id"] = None
                    note["updated_at"] = _now()
            st.session_state.note_folders = [
                f for f in st.session_state.note_folders if f.get("id") != folder["id"]
            ]
            st.session_state.selected_note_folder_id = None
            _mark_changed()
            st.rerun()

    st.divider()
    _render_notes_list(notes, selected_folder_id=folder["id"], show_all=False)


def _go_to_folder_index() -> None:
    st.session_state.selected_note_folder_id = None


def _render_notes_list(
    notes: list[dict[str, Any]],
    selected_folder_id: Any,
    show_all: bool,
) -> None:
    # The selector and primary action share one row for consistent alignment.
    col_filter, col_new = st.columns([3, 1], vertical_alignment="bottom", gap="medium")
    with col_filter:
        if show_all:
            show_options = ["All notes", "Unfiled"]
            show_options.extend(str(f.get("name", "Folder")) for f in st.session_state.note_folders)
            selected = st.selectbox("Show", show_options, key="notes_folder_filter")
            if selected == "All notes":
                selected_id = "all"
            elif selected == "Unfiled":
                selected_id = None
            else:
                folder = next((f for f in st.session_state.note_folders if f.get("name") == selected), None)
                selected_id = folder.get("id") if folder else None
        else:
            st.selectbox("Folders", ["This folder", "Unfiled"] + [
                str(f.get("name", "Folder")) for f in st.session_state.note_folders
            ], index=0, key=f"folder_selector_{selected_folder_id}",
            help="Choose a destination in the note card below to move a note.")
            selected_id = selected_folder_id
    with col_new:
        if st.button("＋ New note", type="primary", use_container_width=True, key=f"new_note_{selected_folder_id}_{show_all}"):
            st.session_state.selected_note_id = None
            st.session_state.note_editor_open = True
            st.session_state.note_draft_folder_id = selected_folder_id
            st.rerun()

    if show_all:
        visible = notes if selected_id == "all" else [n for n in notes if n.get("folder_id") == selected_id]
    else:
        visible = [n for n in notes if n.get("folder_id") == selected_folder_id]

    visible.sort(key=lambda n: n.get("updated_at", ""), reverse=True)
    if not visible:
        st.info("No notes here yet. Create a note or choose another folder.")
        return

    for note in visible:
        with st.container(border=True):
            title = html.escape(str(note.get("title") or "Untitled note"))
            st.markdown(f"**{title}**")
            body = str(note.get("content", "")).strip().replace("\n", " ")
            st.caption((body[:180] + ("…" if len(body) > 180 else "")) or "No content yet.")
            folder = _find_folder(note.get("folder_id"))
            st.caption(f"{folder.get('name')} · Updated {note.get('updated_at', 'unknown')}" if folder else f"Unfiled · Updated {note.get('updated_at', 'unknown')}")
            c1, c2 = st.columns([1, 2], vertical_alignment="center")
            with c1:
                if st.button("Open", key=f"open_note_{note.get('id')}"):
                    st.session_state.selected_note_id = note.get("id")
                    st.session_state.note_editor_open = True
                    st.rerun()
            with c2:
                destinations = {"Unfiled": None}
                destinations.update({
                    str(f.get("name", "Folder")): f.get("id")
                    for f in st.session_state.note_folders
                })
                current_folder = note.get("folder_id")
                current_label = next(
                    (label for label, value in destinations.items() if value == current_folder),
                    "Unfiled",
                )
                dest = st.selectbox(
                    "Folders", list(destinations),
                    index=list(destinations).index(current_label),
                    key=f"move_note_{note.get('id')}",
                )
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
    folder_labels = ["Unfiled"] + [str(f.get("name", "Folder")) for f in folders]
    folder_ids = [None] + [f["id"] for f in folders]
    current_id = existing.get("folder_id") if existing else st.session_state.get("note_draft_folder_id")
    current_index = folder_ids.index(current_id) if current_id in folder_ids else 0

    with st.form("note_form", clear_on_submit=False):
        title = st.text_input("Note title", value=existing.get("title", "") if existing else "", placeholder="e.g. Fractions — Important Rules")
        content = st.text_area("Note content", value=existing.get("content", "") if existing else "", height=220, placeholder="Write your note here…")
        folder_label = st.selectbox("Folders", folder_labels, index=current_index)
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
        st.rerun()

    if delete_clicked and existing:
        st.session_state.notes = [n for n in st.session_state.notes if n.get("id") != existing.get("id")]
        _mark_changed()
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None
        st.info("Note deleted. Saving changes…")
        st.rerun()
