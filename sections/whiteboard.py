"""Whiteboard library and course-friendly canvas entry point for Notes."""
from __future__ import annotations

import io
import json
import zipfile
from typing import Any

import streamlit as st

import state
import whiteboards
from sections import whiteboard_editor


TEMPLATES = ["Blank", "Graph paper", "Coordinate plane", "Mind map", "Flowchart"]


def _now() -> str:
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


def _find_board(board_id: str) -> dict[str, Any] | None:
    return next((b for b in st.session_state.whiteboards if isinstance(b, dict) and b.get("id") == board_id), None)


def _mark_changed() -> None:
    state.mark_persistent_dirty()


def _create_form() -> None:
    boards = st.session_state.whiteboards
    with st.expander("＋ Create a whiteboard", expanded=not boards):
        folders = st.session_state.note_folders
        folder_ids = [None] + [f.get("id") for f in folders]
        folder_labels = ["Unfiled"] + [str(f.get("name", "Folder")) for f in folders]
        with st.form("create_whiteboard_form", clear_on_submit=True):
            title = st.text_input("Whiteboard title", placeholder="e.g. Quadratics visual map")
            template = st.selectbox("Start with", TEMPLATES)
            folder_label = st.selectbox("Folder", folder_labels)
            submitted = st.form_submit_button("Create whiteboard", type="primary")
        if submitted:
            if len(boards) >= whiteboards.whiteboard_data.MAX_BOARDS:
                st.error("You have reached the whiteboard limit. Export an old board before creating another.")
                return
            board = whiteboards.create_board(
                title=title, folder_id=folder_ids[folder_labels.index(folder_label)], template=template
            )
            st.session_state.whiteboards.append(board)
            st.session_state.selected_whiteboard_id = board["id"]
            st.session_state.selected_whiteboard_page_id = board["pages"][0]["id"]
            _mark_changed()
            st.rerun()


def _render_board_actions(board: dict[str, Any]) -> None:
    """Keep secondary whiteboard actions in a compact, predictable overflow menu."""
    board_id = board["id"]
    _, menu_col = st.columns([6, 0.65], vertical_alignment="center")
    with menu_col:
        with st.popover("⋮", help="Whiteboard actions", use_container_width=True):
            if st.button("Rename whiteboard", key=f"rename_whiteboard_{board_id}", use_container_width=True):
                st.session_state[f"renaming_whiteboard_{board_id}"] = True
                st.rerun()

            if st.button("Delete whiteboard", key=f"delete_whiteboard_{board_id}", use_container_width=True):
                st.session_state[f"confirm_delete_whiteboard_{board_id}"] = True
                st.rerun()

            folders = st.session_state.note_folders
            ids = [None] + [f.get("id") for f in folders]
            labels = ["Unfiled"] + [str(f.get("name", "Folder")) for f in folders]
            current_folder = board.get("folder_id")
            idx = ids.index(current_folder) if current_folder in ids else 0
            chosen_folder = st.selectbox(
                "Folder",
                ids,
                index=idx,
                format_func=lambda value: labels[ids.index(value)] if value in ids else "Unfiled",
                key=f"whiteboard_folder_{board_id}",
            )
            if st.button("Move to folder", key=f"move_whiteboard_{board_id}", use_container_width=True):
                board["folder_id"] = chosen_folder
                board["updated_at"] = _now()
                _mark_changed()
                st.rerun()

    if st.session_state.get(f"renaming_whiteboard_{board_id}", False):
        with st.form(f"rename_whiteboard_form_{board_id}"):
            new_title = st.text_input("New whiteboard title", value=board.get("title", ""))
            save_title = st.form_submit_button("Save title")
        if save_title:
            if new_title.strip():
                board["title"] = new_title.strip()[:100]
                board["updated_at"] = _now()
                _mark_changed()
            st.session_state[f"renaming_whiteboard_{board_id}"] = False
            st.rerun()

    if st.session_state.get(f"confirm_delete_whiteboard_{board_id}", False):
        st.warning(f"Delete **{board.get('title', 'this whiteboard')}** and all its pages? This cannot be undone.")
        confirm, cancel = st.columns(2)
        with confirm:
            if st.button("Confirm delete", type="primary", key=f"confirm_delete_{board_id}"):
                st.session_state.whiteboards = [b for b in st.session_state.whiteboards if b.get("id") != board_id]
                remaining = st.session_state.whiteboards
                st.session_state.selected_whiteboard_id = remaining[0]["id"] if remaining else None
                st.session_state.selected_whiteboard_page_id = remaining[0]["pages"][0]["id"] if remaining else None
                _mark_changed()
                st.rerun()
        with cancel:
            if st.button("Cancel", key=f"cancel_delete_{board_id}"):
                st.session_state[f"confirm_delete_whiteboard_{board_id}"] = False
                st.rerun()

def _render_exports(board: dict[str, Any]) -> None:
    col_json, col_svg = st.columns(2)
    title = str(board.get("title", "whiteboard")).replace("/", "-").replace("\\", "-")
    with col_json:
        st.download_button(
            "Download editable board (.json)",
            data=json.dumps(board, ensure_ascii=False, indent=2),
            file_name=f"{title}.json",
            mime="application/json",
            key=f"download_whiteboard_{board['id']}",
            use_container_width=True,
        )
    with col_svg:
        output = io.BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for index, page in enumerate(board.get("pages", []), start=1):
                safe_title = str(page.get("title", f"page-{index}")).replace("/", "-").replace("\\", "-")
                archive.writestr(f"{index:02d}-{safe_title}.svg", whiteboards.page_to_svg(page))
        st.download_button(
            "Download all pages (SVG ZIP)",
            data=output.getvalue(),
            file_name=f"{title}-pages.zip",
            mime="application/zip",
            key=f"download_whiteboard_svg_{board['id']}",
            use_container_width=True,
        )


def render() -> None:
    """Render the whiteboard library within Notes."""
    st.markdown("### Whiteboard")
    st.caption("Sketch concepts, map ideas, and solve problems on a canvas. The canvas keeps edits locally until Vocogni confirms that the saved learner record was updated.")
    _create_form()
    boards = st.session_state.whiteboards
    if not boards:
        st.info("Create a whiteboard to begin. Boards are stored with your existing Vocogni learner data.")
        return

    board_ids = [b["id"] for b in boards]
    selected_id = st.session_state.get("selected_whiteboard_id")
    if selected_id not in board_ids:
        selected_id = board_ids[0]
        st.session_state.selected_whiteboard_id = selected_id

    chosen_id = st.selectbox(
        "Your whiteboards",
        board_ids,
        index=board_ids.index(selected_id),
        format_func=lambda value: str((_find_board(value) or {}).get("title", "Whiteboard")),
        key="notes_whiteboard_picker",
    )
    if chosen_id != selected_id:
        st.session_state.selected_whiteboard_id = chosen_id
        chosen = _find_board(chosen_id)
        st.session_state.selected_whiteboard_page_id = chosen["pages"][0]["id"] if chosen and chosen.get("pages") else None
        st.rerun()

    board = _find_board(chosen_id)
    if board is None:
        st.error("This whiteboard could not be loaded.")
        return
    _render_board_actions(board)
    _render_exports(board)
    st.divider()
    whiteboard_editor.render_editor(board)
