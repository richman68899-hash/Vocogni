"""
Vocogni Notes — flat folders, durable note organization, and responsive controls.

Folders cannot contain folders. Existing notes without a valid folder assignment
remain available under Unfiled. Durable changes use the central autosave flow.
"""
from __future__ import annotations

import datetime
import html
from typing import Any

import streamlit as st
import state
import milestones as milestone_logic
from . import whiteboard as whiteboard_section

PALETTE = milestone_logic.PALETTE


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


def _all_asset_ids(kind: str) -> list[Any]:
    collection_key = {"note": "notes", "folder": "note_folders", "milestone": "milestones"}[kind]
    return [
        item.get("id") for item in st.session_state.get(collection_key, [])
        if isinstance(item, dict) and item.get("id") is not None
    ]


def _start_asset_selection(kind: str, asset_id: Any | None = None) -> None:
    """Enter bulk-selection mode and optionally preselect the asset that opened it."""
    st.session_state[f"{kind}_bulk_select_mode"] = True
    selected_key = f"selected_{kind}_ids"
    selected = list(st.session_state.get(selected_key, []))
    if asset_id is not None and asset_id not in selected:
        selected.append(asset_id)
    st.session_state[selected_key] = selected
    if asset_id is not None:
        st.session_state[f"{kind}_select_{asset_id}"] = True
    if kind == "folder":
        st.session_state.selected_note_folder_id = None


def _toggle_asset_selection(kind: str, asset_id: Any, widget_key: str) -> None:
    selected_key = f"selected_{kind}_ids"
    selected = list(st.session_state.get(selected_key, []))
    if st.session_state.get(widget_key, False):
        if asset_id not in selected:
            selected.append(asset_id)
    else:
        selected = [item_id for item_id in selected if item_id != asset_id]
    st.session_state[selected_key] = selected


def _end_asset_selection(kind: str, asset_ids: list[Any] | None = None) -> None:
    """Exit bulk selection and reset widget state so old checks do not reappear."""
    selected_key = f"selected_{kind}_ids"
    tracked = list(st.session_state.get(selected_key, []))
    all_ids = _all_asset_ids(kind) if asset_ids is None else list(asset_ids)
    for asset_id in dict.fromkeys([*all_ids, *tracked]):
        st.session_state[f"{kind}_select_{asset_id}"] = False
    st.session_state[f"{kind}_bulk_select_mode"] = False
    st.session_state[selected_key] = []


def _select_visible_assets(kind: str, visible_ids: list[Any]) -> None:
    selected_key = f"selected_{kind}_ids"
    selected = list(st.session_state.get(selected_key, []))
    for asset_id in visible_ids:
        if asset_id not in selected:
            selected.append(asset_id)
        st.session_state[f"{kind}_select_{asset_id}"] = True
    st.session_state[selected_key] = selected


def _request_asset_deletion(kind: str, asset_ids: list[Any]) -> None:
    st.session_state.pending_asset_deletion = {
        "kind": kind,
        "ids": list(dict.fromkeys(asset_ids)),
    }


def _confirm_pending_asset_deletion() -> None:
    pending = st.session_state.get("pending_asset_deletion")
    if not isinstance(pending, dict):
        return
    kind, asset_ids = pending.get("kind"), pending.get("ids", [])
    if kind not in {"note", "folder", "milestone"} or not asset_ids:
        st.session_state.pop("pending_asset_deletion", None)
        return

    ids = set(asset_ids)
    ids_before = _all_asset_ids(kind)
    if kind == "note":
        st.session_state.notes = [
            note for note in st.session_state.get("notes", [])
            if not isinstance(note, dict) or note.get("id") not in ids
        ]
        if st.session_state.get("selected_note_id") in ids:
            st.session_state.note_editor_open = False
            st.session_state.selected_note_id = None
    elif kind == "folder":
        # Folder deletion preserves every note and moves its contents to Unfiled.
        now = _now()
        for note in st.session_state.get("notes", []):
            if isinstance(note, dict) and note.get("folder_id") in ids:
                note["folder_id"] = None
                note["updated_at"] = now
        st.session_state.note_folders = [
            folder for folder in st.session_state.get("note_folders", [])
            if not isinstance(folder, dict) or folder.get("id") not in ids
        ]
        if st.session_state.get("selected_note_folder_id") in ids:
            st.session_state.selected_note_folder_id = None
    else:
        st.session_state.milestones = [
            item for item in st.session_state.get("milestones", [])
            if not isinstance(item, dict) or item.get("id") not in ids
        ]

    _end_asset_selection(kind, ids_before)
    st.session_state.pop("pending_asset_deletion", None)
    _mark_changed()
    st.rerun()


def _render_pending_asset_deletion(allowed_kinds: set[str]) -> None:
    """Show a confirmation step before removing saved assets."""
    pending = st.session_state.get("pending_asset_deletion")
    if not isinstance(pending, dict) or pending.get("kind") not in allowed_kinds:
        return
    kind, count = pending.get("kind"), len(pending.get("ids", []))
    if kind == "folder":
        message = (
            f"Delete {count} selected folder{'s' if count != 1 else ''}? "
            "Notes inside will be moved to Unfiled; no note content will be deleted."
        )
    elif kind == "milestone":
        message = (
            f"Delete {count} selected milestone{'s' if count != 1 else ''} "
            "and their checklist items? This cannot be undone."
        )
    else:
        message = (
            f"Delete {count} selected note{'s' if count != 1 else ''}? "
            "The saved note content will be removed. This cannot be undone."
        )
    st.warning(message)
    confirm_col, cancel_col = st.columns([1, 1], gap="small")
    with confirm_col:
        if st.button("Confirm delete", type="primary", key="confirm_pending_asset_delete", use_container_width=True):
            _confirm_pending_asset_deletion()
    with cancel_col:
        if st.button("Cancel", key="cancel_pending_asset_delete", use_container_width=True):
            st.session_state.pop("pending_asset_deletion", None)
            st.rerun()


def _render_bulk_toolbar(kind: str, visible_assets: list[dict[str, Any]], allow_move: bool = False) -> None:
    """Common select-all, delete, and exit controls for saved assets."""
    if not st.session_state.get(f"{kind}_bulk_select_mode", False):
        return
    selected = list(st.session_state.get(f"selected_{kind}_ids", []))
    visible_ids = [
        item.get("id") for item in visible_assets
        if isinstance(item, dict) and item.get("id") is not None
    ]
    labels = {"note": "notes", "folder": "folders", "milestone": "milestones"}
    with st.container(border=True):
        st.markdown("**Select multiple**")
        st.caption(f"{len(selected)} {labels[kind]} selected")
        select_col, delete_col, done_col = st.columns([1.2, 1.2, 0.8], gap="small")
        with select_col:
            if st.button("Select all shown", key=f"select_all_{kind}_visible", use_container_width=True):
                _select_visible_assets(kind, visible_ids)
                st.rerun()
        with delete_col:
            if st.button(
                f"Delete selected ({len(selected)})", key=f"delete_selected_{kind}",
                type="primary", disabled=not selected, use_container_width=True,
            ):
                _request_asset_deletion(kind, selected)
                st.rerun()
        with done_col:
            if st.button("Done", key=f"finish_select_{kind}", use_container_width=True):
                _end_asset_selection(kind)
                st.rerun()

        if allow_move and selected:
            destinations = {"Unfiled": None}
            destinations.update({
                str(folder.get("name", "Folder")): folder.get("id")
                for folder in st.session_state.get("note_folders", [])
                if isinstance(folder, dict)
            })
            move_col, action_col = st.columns([3, 1.2], vertical_alignment="bottom", gap="small")
            with move_col:
                target_label = st.selectbox("Move selected notes to", list(destinations), key="notes_bulk_move_target")
            with action_col:
                if st.button("Move notes", key="move_selected_notes", use_container_width=True):
                    selected_ids = set(selected)
                    now = _now()
                    for note in st.session_state.get("notes", []):
                        if isinstance(note, dict) and note.get("id") in selected_ids:
                            note["folder_id"] = destinations[target_label]
                            note["updated_at"] = now
                    _end_asset_selection("note")
                    _mark_changed()
                    st.rerun()


def _render_folder_overflow_menu(folder: dict[str, Any]) -> None:
    folder_id = folder.get("id")
    with st.popover("⋯", key=f"folder_overflow_{folder_id}", help="Folder actions"):
        if st.button("Select multiple folders", key=f"select_folder_{folder_id}", use_container_width=True):
            _start_asset_selection("folder", folder_id)
            st.rerun()
        if st.button("Delete folder", key=f"delete_folder_menu_{folder_id}", use_container_width=True):
            _request_asset_deletion("folder", [folder_id])
            st.rerun()


def _render_note_overflow_menu(note: dict[str, Any]) -> None:
    note_id = note.get("id")
    with st.popover("⋯", key=f"note_overflow_{note_id}", help="Note actions"):
        if st.button("Select multiple notes", key=f"select_note_{note_id}", use_container_width=True):
            _start_asset_selection("note", note_id)
            st.rerun()
        if st.button("Delete note", key=f"delete_note_menu_{note_id}", use_container_width=True):
            _request_asset_deletion("note", [note_id])
            st.rerun()


def _render_milestone_overflow_menu(milestone: dict[str, Any]) -> None:
    milestone_id = milestone.get("id")
    with st.popover("⋯", key=f"milestone_overflow_{milestone_id}", help="Milestone actions"):
        if st.button("Select multiple milestones", key=f"select_milestone_{milestone_id}", use_container_width=True):
            _start_asset_selection("milestone", milestone_id)
            st.rerun()
        if st.button("Delete milestone", key=f"delete_milestone_menu_{milestone_id}", use_container_width=True):
            _request_asset_deletion("milestone", [milestone_id])
            st.rerun()


def render() -> None:
    st.markdown("<h1>Notes</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='vc-page-intro'>Keep lesson notes organized, plan learning milestones, and sketch ideas on the whiteboard.</p>",
        unsafe_allow_html=True,
    )
    if st.session_state.get("note_editor_open", False):
        _render_pending_asset_deletion({"note"})
        _render_editor()
        return

    workspace = st.radio(
        "Notes workspace",
        ["Notes & folders", "Learning milestones", "Whiteboard"],
        horizontal=True,
        key="notes_workspace_view",
        label_visibility="collapsed",
    )
    st.divider()
    if workspace == "Notes & folders":
        _render_pending_asset_deletion({"note", "folder"})
    if workspace == "Learning milestones":
        _render_milestones()
        return
    if workspace == "Whiteboard":
        whiteboard_section.render()
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
    folders = [f for f in st.session_state.note_folders if isinstance(f, dict)]
    notes = [n for n in st.session_state.notes if isinstance(n, dict)]

    st.markdown("### Folders")
    with st.expander("Create a folder", expanded=not folders):
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
                folders.append({"id": folder_id, "name": clean, "color": color_name, "created_at": _now()})
                st.session_state.note_folders = folders
                _mark_changed()
                st.rerun()

    _render_bulk_toolbar("folder", folders)
    if folders:
        cols = st.columns(2, gap="medium")
        for i, folder in enumerate(folders):
            with cols[i % 2]:
                folder_id = folder.get("id")
                color = _resolved_color(folder)
                safe_name = html.escape(str(folder.get("name", "Untitled folder")))
                count = _folder_count(folder_id, notes)
                with st.container(border=True):
                    if st.session_state.get("folder_bulk_select_mode", False):
                        select_col, content_col, menu_col = st.columns([0.42, 4, 0.5], vertical_alignment="top", gap="small")
                        with select_col:
                            checkbox_key = f"folder_select_{folder_id}"
                            st.checkbox(
                                "Select folder", value=folder_id in st.session_state.get("selected_folder_ids", []),
                                key=checkbox_key, label_visibility="collapsed",
                                on_change=_toggle_asset_selection, args=("folder", folder_id, checkbox_key),
                            )
                    else:
                        content_col, menu_col = st.columns([4, 0.5], vertical_alignment="top", gap="small")
                    with content_col:
                        st.markdown(
                            f"<div style='border-left:3px solid {color};padding:4px 0 4px 10px'>"
                            f"<div style='font-size:1.05rem;font-weight:650'>{safe_name}</div>"
                            f"<div style='color:var(--vc-subtext);font-size:.85rem;margin-top:6px'>"
                            f"{count} {'note' if count == 1 else 'notes'}</div></div>",
                            unsafe_allow_html=True,
                        )
                        if st.button("Open folder", key=f"open_folder_{folder_id}", use_container_width=True):
                            st.session_state.selected_note_folder_id = folder_id
                            st.rerun()
                    with menu_col:
                        _render_folder_overflow_menu(folder)
    elif not st.session_state.get("folder_bulk_select_mode", False):
        st.info("No folders yet. Create one above, or save notes without a folder.")

    st.divider()
    _render_notes_list(notes, selected_folder_id=None, show_all=True)

def _render_folder_view(folder: dict[str, Any]) -> None:
    notes = [n for n in st.session_state.notes if isinstance(n, dict)]
    folder_id = folder.get("id")
    color = _resolved_color(folder)
    safe_name = html.escape(str(folder.get("name", "Folder")))
    count = _folder_count(folder_id, notes)

    top_col, menu_col = st.columns([5, 0.55], vertical_alignment="center", gap="small")
    with top_col:
        st.button("← All folders", key="back_to_folder_index", on_click=_go_to_folder_index)
        st.markdown(
            f"<div style='border-left:3px solid {color};padding:6px 0 6px 12px;margin:4px 0 14px 0'>"
            f"<div style='font-size:1.4rem;font-weight:650'>{safe_name}</div>"
            f"<div style='color:var(--vc-subtext);font-size:.86rem'>{count} {'note' if count == 1 else 'notes'}</div></div>",
            unsafe_allow_html=True,
        )
    with menu_col:
        _render_folder_overflow_menu(folder)

    with st.expander("Manage folder", expanded=False):
        with st.form(f"edit_folder_{folder_id}"):
            new_name = st.text_input("Folder title", value=folder.get("name", ""))
            options = list(PALETTE)
            current_color = _color_name(folder)
            new_color_name = st.selectbox("Folder color", options, index=options.index(current_color))
            save_folder = st.form_submit_button("Save changes", type="primary")
        if save_folder:
            clean = new_name.strip()
            duplicate = any(
                f.get("id") != folder_id
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

    st.divider()
    _render_notes_list(notes, selected_folder_id=folder_id, show_all=False)

def _go_to_folder_index() -> None:
    st.session_state.selected_note_folder_id = None


def _render_notes_list(
    notes: list[dict[str, Any]],
    selected_folder_id: Any,
    show_all: bool,
) -> None:
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
            st.caption("Notes in this folder.")
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
    _render_bulk_toolbar("note", visible, allow_move=True)
    if not visible:
        st.info("No notes here yet. Create one or choose another folder.")
        return

    note_bulk_mode = st.session_state.get("note_bulk_select_mode", False)
    for note in visible:
        note_id = note.get("id")
        with st.container(border=True):
            if note_bulk_mode:
                select_col, title_col, folder_col, menu_col = st.columns([0.38, 3, 2, 0.48], vertical_alignment="center", gap="small")
                with select_col:
                    checkbox_key = f"note_select_{note_id}"
                    st.checkbox(
                        "Select note", value=note_id in st.session_state.get("selected_note_ids", []),
                        key=checkbox_key, label_visibility="collapsed",
                        on_change=_toggle_asset_selection, args=("note", note_id, checkbox_key),
                    )
            else:
                title_col, folder_col, menu_col = st.columns([3, 2, 0.48], vertical_alignment="center", gap="small")
            with title_col:
                title = html.escape(str(note.get("title") or "Untitled note"))
                st.markdown(f"**{title}**")
            with folder_col:
                destinations = {"Unfiled": None}
                destinations.update({
                    str(f.get("name", "Folder")): f.get("id")
                    for f in st.session_state.note_folders
                })
                current_folder = note.get("folder_id")
                current_label = next((label for label, value in destinations.items() if value == current_folder), "Unfiled")
                dest = st.selectbox(
                    "Folders", list(destinations),
                    index=list(destinations).index(current_label),
                    key=f"move_note_{note_id}",
                    label_visibility="collapsed",
                )
                if destinations[dest] != current_folder:
                    note["folder_id"] = destinations[dest]
                    note["updated_at"] = _now()
                    _mark_changed()
                    st.rerun()
            with menu_col:
                _render_note_overflow_menu(note)

            body = str(note.get("content", "")).strip().replace("\\n", " ")
            st.caption((body[:180] + ("…" if len(body) > 180 else "")) or "No content yet.")
            folder = _find_folder(note.get("folder_id"))
            st.caption(
                f"{folder.get('name')} · Updated {note.get('updated_at', 'unknown')}"
                if folder else f"Unfiled · Updated {note.get('updated_at', 'unknown')}"
            )
            if st.button("Open note", key=f"open_note_{note_id}"):
                st.session_state.selected_note_id = note_id
                st.session_state.note_editor_open = True
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
        st.success("Note saved. Syncing changes…")
        st.rerun()

    if delete_clicked and existing:
        _request_asset_deletion("note", [existing.get("id")])
        st.rerun()


# ===========================================================================
# LEARNING MILESTONES
# ===========================================================================

def _find_milestone(milestone_id: Any) -> dict[str, Any] | None:
    return next(
        (
            milestone for milestone in st.session_state.milestones
            if isinstance(milestone, dict) and milestone.get("id") == milestone_id
        ),
        None,
    )


def _find_checklist_item(milestone: dict[str, Any], item_id: Any) -> dict[str, Any] | None:
    return next(
        (
            item for item in milestone.get("checklist", [])
            if isinstance(item, dict) and item.get("id") == item_id
        ),
        None,
    )


def _toggle_milestone_item(milestone_id: int, item_id: int, widget_key: str) -> None:
    milestone = _find_milestone(milestone_id)
    if milestone is None:
        return
    item = _find_checklist_item(milestone, item_id)
    if item is None:
        return
    milestone_logic.set_checklist_item_done(
        milestone, item_id, bool(st.session_state.get(widget_key, False))
    )
    milestone["updated_at"] = _now()
    _mark_changed()


def _render_milestones() -> None:
    """Render goal categories and milestone cards with bulk actions."""
    _render_pending_asset_deletion({"milestone"})
    milestones = [item for item in st.session_state.milestones if isinstance(item, dict)]
    st.markdown("### Learning milestones")
    st.caption(
        "Turn larger goals into dated checklists. Milestones and checklist changes "
        "are saved with your existing Vocogni learner data."
    )

    with st.expander("＋ Create a milestone", expanded=not milestones):
        with st.form("create_learning_milestone", clear_on_submit=True):
            title = st.text_input(
                "Milestone title",
                placeholder="e.g. Master quadratic equations",
            )
            end_date = st.date_input(
                "End date",
                value=datetime.date.today() + datetime.timedelta(days=7),
                help="Choose the date by which you want to finish this milestone.",
            )
            section = st.selectbox(
                "Goal section",
                options=list(milestone_logic.MILESTONE_SECTIONS),
            )
            icon_col, color_col = st.columns(2)
            with icon_col:
                emoji = st.selectbox(
                    "Icon",
                    options=list(milestone_logic.MILESTONE_EMOJIS),
                )
            with color_col:
                color_name = st.selectbox(
                    "Milestone color",
                    options=list(PALETTE),
                    index=list(PALETTE).index("Blue"),
                )
            create = st.form_submit_button("Create milestone", type="primary")

        if create:
            try:
                milestone = milestone_logic.create_milestone(
                    milestone_id=st.session_state.next_milestone_id,
                    title=title,
                    end_date=end_date,
                    section=section,
                    color=color_name,
                    emoji=emoji,
                    now=_now(),
                )
            except ValueError as exc:
                st.warning(str(exc))
            else:
                st.session_state.milestones.append(milestone)
                st.session_state.next_milestone_id += 1
                _mark_changed()
                st.rerun()

    section_labels = ["All sections", *milestone_logic.MILESTONE_SECTIONS]
    selected_section = st.selectbox(
        "Show goal section",
        options=section_labels,
        key="milestone_section_filter",
    )
    visible = [
        milestone for milestone in milestones
        if selected_section == "All sections" or milestone.get("section") == selected_section
    ]
    visible.sort(key=lambda row: (str(row.get("end_date", "9999-12-31")), str(row.get("title", "")).casefold()))
    _render_bulk_toolbar("milestone", visible)

    if not visible:
        st.info(
            "No milestones in this section yet. Create one above and add checklist steps "
            "to make the goal actionable."
        )
        return

    groups = (
        [selected_section]
        if selected_section != "All sections"
        else list(milestone_logic.MILESTONE_SECTIONS)
    )
    for section_name in groups:
        section_milestones = [
            milestone for milestone in visible
            if milestone.get("section", "Other") == section_name
        ]
        if not section_milestones:
            continue
        st.markdown(f"### {html.escape(section_name)}")
        for milestone in section_milestones:
            _render_milestone_card(milestone)


def _render_milestone_card(milestone: dict[str, Any]) -> None:
    milestone_id = milestone["id"]
    color = _resolved_color({"color": milestone.get("color", "Grey")})
    safe_title = html.escape(str(milestone.get("title") or "Untitled milestone"))
    safe_section = html.escape(str(milestone.get("section", "Other")))
    emoji = milestone.get("emoji") if milestone.get("emoji") in milestone_logic.MILESTONE_EMOJIS else "🎯"
    checklist = [
        item for item in milestone.get("checklist", [])
        if isinstance(item, dict)
    ]
    done_count = sum(bool(item.get("done")) for item in checklist)

    with st.container(border=True):
        st.markdown(
            f"<div style='height:5px;background:{color};border-radius:8px;margin-bottom:12px'></div>",
            unsafe_allow_html=True,
        )
        if st.session_state.get("milestone_bulk_select_mode", False):
            select_col, spacer_col = st.columns([0.5, 5.5], gap="small")
            with select_col:
                checkbox_key = f"milestone_select_{milestone_id}"
                st.checkbox(
                    "Select milestone",
                    value=milestone_id in st.session_state.get("selected_milestone_ids", []),
                    key=checkbox_key,
                    label_visibility="collapsed",
                    on_change=_toggle_asset_selection,
                    args=("milestone", milestone_id, checkbox_key),
                )
        icon_col, title_col, date_col, menu_col = st.columns(
            [0.75, 3.7, 1.55, 0.55],
            vertical_alignment="center",
            gap="small",
        )
        with icon_col:
            st.markdown(
                f"<div class='vc-milestone-icon' aria-hidden='true'>{emoji}</div>",
                unsafe_allow_html=True,
            )
        with title_col:
            st.markdown(
                f"<div class='vc-milestone-title'>"
                f"<div class='vc-milestone-name'>{safe_title}</div>"
                f"<div class='vc-milestone-section' style='color:{color}'>{safe_section}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )
        with date_col:
            try:
                parsed_due = datetime.date.fromisoformat(str(milestone.get("end_date", "")))
                due_label = parsed_due.strftime("%d %b %Y")
            except ValueError:
                due_label = "Date not set"
                parsed_due = None
            st.markdown(
                "<div class='vc-milestone-date'>"
                "<span class='vc-milestone-date-label'>END DATE</span>"
                f"<span class='vc-milestone-date-value'>{html.escape(due_label)}</span>"
                "</div>",
                unsafe_allow_html=True,
            )

        with menu_col:
            _render_milestone_overflow_menu(milestone)

        if checklist:
            st.progress(done_count / len(checklist))
            st.caption(f"{done_count} of {len(checklist)} checklist items complete")
        else:
            st.caption("No checklist items yet.")

        if parsed_due and parsed_due < datetime.date.today() and checklist and done_count < len(checklist):
            st.caption("End date has passed. You can edit the date or continue working through the checklist.")
        elif checklist and done_count == len(checklist):
            st.caption("Milestone checklist complete.")

        st.markdown("**Checklist**")
        if not checklist:
            st.caption("Add your first step below.")
        for item in checklist:
            item_id = item["id"]
            checkbox_key = f"milestone_check_{milestone_id}_{item_id}"
            edit_key = f"milestone_editing_item_{milestone_id}"
            item_is_editing = st.session_state.get(edit_key) == item_id

            check_col, text_col, edit_col, delete_col = st.columns(
                [0.45, 4.0, 0.8, 0.9],
                vertical_alignment="center",
            )
            with check_col:
                st.checkbox(
                    str(item.get("text", "Checklist item")),
                    value=bool(item.get("done", False)),
                    key=checkbox_key,
                    label_visibility="collapsed",
                    on_change=_toggle_milestone_item,
                    args=(milestone_id, item_id, checkbox_key),
                )
            with text_col:
                safe_item_text = html.escape(str(item.get("text") or "Checklist item"))
                style = "text-decoration:line-through;opacity:.55" if item.get("done") else "font-weight:500"
                st.markdown(
                    f"<div class='vc-checklist-item-text' style='{style}'>{safe_item_text}</div>",
                    unsafe_allow_html=True,
                )
            with edit_col:
                if st.button("Edit", key=f"edit_milestone_item_button_{milestone_id}_{item_id}", use_container_width=True):
                    st.session_state[edit_key] = item_id
                    st.rerun()
            with delete_col:
                if st.button("Delete", key=f"delete_milestone_item_{milestone_id}_{item_id}", use_container_width=True):
                    milestone_logic.delete_checklist_item(milestone, item_id)
                    milestone["updated_at"] = _now()
                    if st.session_state.get(edit_key) == item_id:
                        st.session_state.pop(edit_key, None)
                    _mark_changed()
                    st.rerun()

            if item_is_editing:
                with st.form(f"edit_milestone_item_form_{milestone_id}_{item_id}"):
                    replacement = st.text_input(
                        "Checklist item",
                        value=str(item.get("text", "")),
                        key=f"edit_milestone_item_text_{milestone_id}_{item_id}",
                    )
                    save_item = st.form_submit_button("Save item", type="primary")
                    cancel_item = st.form_submit_button("Cancel")
                if save_item:
                    try:
                        milestone_logic.update_checklist_item(milestone, item_id, replacement)
                    except ValueError as exc:
                        st.warning(str(exc))
                    else:
                        milestone["updated_at"] = _now()
                        st.session_state.pop(edit_key, None)
                        _mark_changed()
                        st.rerun()
                if cancel_item:
                    st.session_state.pop(edit_key, None)
                    st.rerun()

        with st.form(f"add_milestone_item_form_{milestone_id}", clear_on_submit=True):
            new_item_text = st.text_input(
                "Add checklist item",
                placeholder="e.g. Solve 10 mixed questions",
                key=f"new_milestone_item_text_{milestone_id}",
            )
            add_item = st.form_submit_button("＋ Add checklist item")
        if add_item:
            try:
                milestone_logic.add_checklist_item(milestone, new_item_text)
            except ValueError as exc:
                st.warning(str(exc))
            else:
                milestone["updated_at"] = _now()
                _mark_changed()
                st.rerun()

        with st.expander("Edit milestone details", expanded=False):
            try:
                existing_due = datetime.date.fromisoformat(str(milestone.get("end_date", "")))
            except ValueError:
                existing_due = datetime.date.today() + datetime.timedelta(days=7)
            with st.form(f"edit_milestone_form_{milestone_id}"):
                new_title = st.text_input(
                    "Milestone title",
                    value=str(milestone.get("title", "")),
                    key=f"edit_milestone_title_{milestone_id}",
                )
                new_due = st.date_input(
                    "End date",
                    value=existing_due,
                    key=f"edit_milestone_due_{milestone_id}",
                )
                section_options = list(milestone_logic.MILESTONE_SECTIONS)
                new_section = st.selectbox(
                    "Goal section",
                    options=section_options,
                    index=section_options.index(milestone.get("section", "Other"))
                    if milestone.get("section", "Other") in section_options else section_options.index("Other"),
                    key=f"edit_milestone_section_{milestone_id}",
                )
                metadata_col1, metadata_col2 = st.columns(2)
                with metadata_col1:
                    new_emoji = st.selectbox(
                        "Icon",
                        options=list(milestone_logic.MILESTONE_EMOJIS),
                        index=list(milestone_logic.MILESTONE_EMOJIS).index(emoji),
                        key=f"edit_milestone_emoji_{milestone_id}",
                    )
                with metadata_col2:
                    color_options = list(PALETTE)
                    new_color = st.selectbox(
                        "Milestone color",
                        options=color_options,
                        index=color_options.index(milestone.get("color", "Grey"))
                        if milestone.get("color", "Grey") in color_options else color_options.index("Grey"),
                        key=f"edit_milestone_color_{milestone_id}",
                    )
                save_details = st.form_submit_button("Save milestone", type="primary")
            if save_details:
                try:
                    milestone_logic.update_milestone(
                        milestone,
                        title=new_title,
                        end_date=new_due,
                        section=new_section,
                        color=new_color,
                        emoji=new_emoji,
                    )
                except ValueError as exc:
                    st.warning(str(exc))
                else:
                    milestone["updated_at"] = _now()
                    _mark_changed()
                    st.rerun()


