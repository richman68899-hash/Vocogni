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


def render() -> None:
    st.markdown("<h1>Notes</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p class='vc-page-intro'>Keep study notes organized, track learning milestones, or sketch an idea on the whiteboard.</p>",
        unsafe_allow_html=True,
    )
    if st.session_state.get("note_editor_open", False):
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
    folders = st.session_state.note_folders
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
                    f"<div style='border:1px solid var(--vc-border);border-left:3px solid {color};"
                    f"border-radius:10px;padding:14px;margin:4px 0 8px 0;"
                    f"background:var(--vc-surface);min-height:84px'>"
                    f"<div style='font-size:1.05rem;font-weight:650'>{safe_name}</div>"
                    f"<div style='color:var(--vc-subtext);font-size:.85rem;margin-top:7px'>{count} {'note' if count == 1 else 'notes'}</div></div>",
                    unsafe_allow_html=True,
                )
                if st.button("Open folder", key=f"open_folder_{folder['id']}", use_container_width=True):
                    st.session_state.selected_note_folder_id = folder["id"]
                    st.rerun()

    st.divider()
    _render_notes_list(notes, selected_folder_id=None, show_all=True)


def _render_folder_view(folder: dict[str, Any]) -> None:
    notes = [n for n in st.session_state.notes if isinstance(n, dict)]
    color = _resolved_color(folder)
    safe_name = html.escape(str(folder.get("name", "Folder")))
    st.button("All folders", key="back_to_folder_index", on_click=_go_to_folder_index)
    st.markdown(
        f"<div style='border-left:3px solid {color};padding:8px 0 8px 12px;margin:6px 0 16px 0'>"
        f"<div style='font-size:1.4rem;font-weight:650'>{safe_name}</div>"
        f"<div style='color:var(--vc-subtext);font-size:.86rem'>{_folder_count(folder.get('id'), notes)} {'note' if _folder_count(folder.get('id'), notes) == 1 else 'notes'}</div></div>",
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
            st.caption("Showing notes in this folder.")
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
            # Keep the note title and folder destination control on one row.
            title_col, folder_col = st.columns([3, 2], vertical_alignment="center", gap="medium")
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
                current_label = next(
                    (label for label, value in destinations.items() if value == current_folder),
                    "Unfiled",
                )
                dest = st.selectbox(
                    "Folders", list(destinations),
                    index=list(destinations).index(current_label),
                    key=f"move_note_{note.get('id')}",
                    label_visibility="visible",
                )
                if destinations[dest] != current_folder:
                    note["folder_id"] = destinations[dest]
                    note["updated_at"] = _now()
                    _mark_changed()
                    st.rerun()
            body = str(note.get("content", "")).strip().replace("\\n", " ")
            st.caption((body[:180] + ("…" if len(body) > 180 else "")) or "No content yet.")
            folder = _find_folder(note.get("folder_id"))
            st.caption(
                f"{folder.get('name')} · Updated {note.get('updated_at', 'unknown')}"
                if folder else f"Unfiled · Updated {note.get('updated_at', 'unknown')}"
            )
            if st.button("Open", key=f"open_note_{note.get('id')}"):
                st.session_state.selected_note_id = note.get("id")
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
        st.success("Note saved. Saving changes…")
        st.rerun()

    if delete_clicked and existing:
        st.session_state.notes = [n for n in st.session_state.notes if n.get("id") != existing.get("id")]
        _mark_changed()
        st.session_state.note_editor_open = False
        st.session_state.selected_note_id = None
        st.info("Note deleted. Saving changes…")
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
    """Render goal categories and the milestone cards in the Notes workspace."""
    milestones = st.session_state.milestones
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
        icon_col, title_col, date_col = st.columns([0.75, 3.8, 1.7], vertical_alignment="center")
        with icon_col:
            st.markdown(
                f"<div style='font-size:2.35rem;line-height:1.1;text-align:center'>{emoji}</div>",
                unsafe_allow_html=True,
            )
        with title_col:
            st.markdown(
                f"<div style='font-size:1.15rem;font-weight:700;line-height:1.25'>{safe_title}</div>"
                f"<div style='color:{color};font-size:.85rem;margin-top:4px;font-weight:600'>{safe_section}</div>",
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
                "<div style='text-align:right;font-size:.82rem;opacity:.8'>END DATE</div>"
                f"<div style='text-align:right;font-weight:600'>{html.escape(due_label)}</div>",
                unsafe_allow_html=True,
            )

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
                    f"<div style='padding:5px 0;{style}'>{safe_item_text}</div>",
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

        confirm_key = f"confirm_delete_milestone_{milestone_id}"
        if st.button("Delete milestone", key=f"delete_milestone_{milestone_id}"):
            st.session_state[confirm_key] = True
            st.rerun()
        if st.session_state.get(confirm_key):
            st.warning("Delete this milestone and all its checklist items?")
            confirm_col, cancel_col = st.columns(2)
            with confirm_col:
                if st.button("Confirm delete", key=f"confirm_delete_milestone_button_{milestone_id}", type="primary"):
                    st.session_state.milestones = [
                        row for row in st.session_state.milestones
                        if row.get("id") != milestone_id
                    ]
                    st.session_state.pop(confirm_key, None)
                    _mark_changed()
                    st.rerun()
            with cancel_col:
                if st.button("Keep milestone", key=f"cancel_delete_milestone_{milestone_id}"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
