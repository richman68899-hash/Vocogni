"""Notes > Whiteboards: private editable boards backed by learner persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

import state
import whiteboards


_COMPONENT_PATH = Path(__file__).resolve().parents[1] / "components" / "whiteboard"
_whiteboard_component = components.declare_component(
    "vocogni_whiteboard_canvas",
    path=str(_COMPONENT_PATH),
)


def render() -> None:
    """Render the private whiteboard library or one board editor."""
    _ensure_session_keys()
    selected_id = st.session_state.get("selected_whiteboard_id")
    board = _find_board(selected_id) if selected_id else None
    if selected_id is not None and board is None:
        st.session_state.selected_whiteboard_id = None
        selected_id = None

    if board is None:
        _render_library()
    else:
        _render_editor(board)


def _ensure_session_keys() -> None:
    st.session_state.setdefault("selected_whiteboard_id", None)
    st.session_state.setdefault("_whiteboard_component_ack", {})
    st.session_state.setdefault("_whiteboard_component_save_status", {})


def _find_board(board_id: Any) -> dict[str, Any] | None:
    return next(
        (
            board for board in st.session_state.whiteboards
            if isinstance(board, dict) and board.get("id") == board_id
        ),
        None,
    )


def _folder_options() -> tuple[list[str], dict[str, int | None]]:
    labels = ["Unfiled"]
    values: dict[str, int | None] = {"Unfiled": None}
    for folder in st.session_state.note_folders:
        if not isinstance(folder, dict) or not isinstance(folder.get("id"), int):
            continue
        label = f"{folder.get('name', 'Folder')} · folder #{folder['id']}"
        labels.append(label)
        values[label] = folder["id"]
    return labels, values


def _folder_label(folder_id: int | None, labels: list[str], values: dict[str, int | None]) -> str:
    return next((label for label in labels if values[label] == folder_id), "Unfiled")


def _folder_color(folder_id: int | None) -> str:
    folder = next(
        (
            item for item in st.session_state.note_folders
            if isinstance(item, dict) and item.get("id") == folder_id
        ),
        None,
    )
    if not folder:
        return "#858B95"
    value = folder.get("color", "Grey")
    if value == "System":
        return "#858B95"
    return whiteboards.PALETTE.get(value, value if isinstance(value, str) and value.startswith("#") else "#858B95")


def _render_library() -> None:
    st.markdown("### Whiteboards")
    st.caption(
        "Draw, annotate, organize ideas, and keep your work editable. "
        "Boards are private to your Vocogni account."
    )
    boards = st.session_state.whiteboards

    with st.expander("＋ Create a whiteboard", expanded=not boards):
        labels, values = _folder_options()
        with st.form("create_whiteboard_form", clear_on_submit=True):
            title = st.text_input(
                "Whiteboard title",
                placeholder="e.g. Quadratic Functions",
                max_chars=whiteboards.MAX_BOARD_TITLE_LENGTH,
            )
            folder_label = st.selectbox("Folder", labels)
            template = st.selectbox(
                "Starting template",
                options=["grid", "blank", "dots", "ruled", "coordinate", "mind_map", "flowchart"],
                format_func=lambda value: {
                    "grid": "Graph paper",
                    "blank": "Blank canvas",
                    "dots": "Dot grid",
                    "ruled": "Ruled notes",
                    "coordinate": "Coordinate plane",
                    "mind_map": "Mind map",
                    "flowchart": "Flowchart",
                }[value],
            )
            create = st.form_submit_button("Create whiteboard", type="primary")
        if create:
            clean = title.strip()
            if not clean:
                st.warning("Enter a title for this whiteboard.")
            elif len(boards) >= whiteboards.MAX_WHITEBOARDS:
                st.warning(f"You can currently keep up to {whiteboards.MAX_WHITEBOARDS} whiteboards.")
            else:
                new_id = int(st.session_state.next_whiteboard_id)
                board = whiteboards.create_whiteboard(
                    new_id,
                    title=clean,
                    folder_id=values[folder_label],
                    template=template,
                )
                boards.append(board)
                st.session_state.next_whiteboard_id = new_id + 1
                st.session_state.selected_whiteboard_id = board["id"]
                state.mark_persistent_dirty()
                saved = state.flush_persistent_save()
                st.session_state["_whiteboard_component_save_status"][board["id"]] = "saved" if saved else "error"
                st.rerun()

    if not boards:
        st.info("No whiteboards yet. Create one above to start drawing.")
        return

    search = st.text_input("Search whiteboards", key="whiteboard_search", placeholder="Find a board by title or folder")
    visible = []
    for board in boards:
        folder = next(
            (
                f for f in st.session_state.note_folders
                if isinstance(f, dict) and f.get("id") == board.get("folder_id")
            ),
            None,
        )
        folder_name = str(folder.get("name", "")) if folder else "Unfiled"
        if search and search.casefold() not in (str(board.get("title", "")) + " " + folder_name).casefold():
            continue
        visible.append((board, folder_name))

    if not visible:
        st.info("No whiteboards match that search.")
        return

    cols = st.columns(2, gap="medium")
    for index, (board, folder_name) in enumerate(visible):
        with cols[index % 2]:
            color = _folder_color(board.get("folder_id"))
            pages, objects = whiteboards.board_object_counts(board)
            safe_title = str(board.get("title") or "Untitled whiteboard")
            with st.container(border=True):
                st.markdown(
                    f"<div style='border-top:6px solid {color};margin:-8px -8px 10px -8px;padding:12px 10px 2px 10px;border-radius:8px 8px 0 0;'>"
                    f"<div style='font-size:1.8rem;line-height:1.1'>🎨</div>"
                    f"<div style='font-weight:700;font-size:1.08rem;margin-top:5px'>{_escape(safe_title)}</div>"
                    f"<div style='opacity:.72;font-size:.85rem;margin-top:4px'>{_escape(folder_name)} · {pages} {'page' if pages == 1 else 'pages'} · {objects} {'object' if objects == 1 else 'objects'}</div></div>",
                    unsafe_allow_html=True,
                )
                st.caption(f"Updated {board.get('updated_at') or 'not yet edited'}")
                if st.button(
                    "Open whiteboard →",
                    key=f"open_whiteboard_{board['id']}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.selected_whiteboard_id = board["id"]
                    st.rerun()

                duplicate_col, delete_col = st.columns(2)
                with duplicate_col:
                    if st.button(
                        "Duplicate",
                        key=f"duplicate_whiteboard_{board['id']}",
                        use_container_width=True,
                    ):
                        if len(st.session_state.whiteboards) >= whiteboards.MAX_WHITEBOARDS:
                            st.warning(f"You can currently keep up to {whiteboards.MAX_WHITEBOARDS} whiteboards.")
                        else:
                            next_id = int(st.session_state.next_whiteboard_id)
                            copy = whiteboards.duplicate_whiteboard(board, next_id)
                            st.session_state.whiteboards.append(copy)
                            st.session_state.next_whiteboard_id = next_id + 1
                            state.mark_persistent_dirty()
                            saved = state.flush_persistent_save()
                            st.session_state["_whiteboard_component_save_status"][copy["id"]] = "saved" if saved else "error"
                            st.rerun()
                with delete_col:
                    if st.button(
                        "Delete",
                        key=f"request_delete_whiteboard_{board['id']}",
                        use_container_width=True,
                    ):
                        st.session_state["_confirm_delete_whiteboard_id"] = board["id"]
                        st.rerun()

                if st.session_state.get("_confirm_delete_whiteboard_id") == board["id"]:
                    st.warning("Delete this whiteboard and all of its pages?")
                    yes_col, no_col = st.columns(2)
                    with yes_col:
                        if st.button("Confirm delete", key=f"confirm_delete_whiteboard_{board['id']}", type="primary"):
                            st.session_state.whiteboards = [
                                item for item in st.session_state.whiteboards
                                if item.get("id") != board["id"]
                            ]
                            st.session_state["_whiteboard_component_save_status"].pop(board["id"], None)
                            st.session_state["_whiteboard_component_ack"].pop(board["id"], None)
                            if st.session_state.get("selected_whiteboard_id") == board["id"]:
                                st.session_state.selected_whiteboard_id = None
                            st.session_state.pop("_confirm_delete_whiteboard_id", None)
                            state.mark_persistent_dirty()
                            saved = state.flush_persistent_save()
                            if not saved:
                                st.error("The board was deleted from this session, but saving the deletion failed. Retry saving before leaving.")
                            st.rerun()
                    with no_col:
                        if st.button("Keep board", key=f"cancel_delete_whiteboard_{board['id']}"):
                            st.session_state.pop("_confirm_delete_whiteboard_id", None)
                            st.rerun()


def _render_editor(board: dict[str, Any]) -> None:
    board_id = board["id"]
    labels, values = _folder_options()
    col_back, col_title = st.columns([1, 4], vertical_alignment="center")
    with col_back:
        if st.button("← Whiteboards", key=f"back_whiteboards_{board_id}"):
            st.session_state.selected_whiteboard_id = None
            st.rerun()
    with col_title:
        st.markdown(f"### {_escape(str(board.get('title') or 'Untitled whiteboard'))}")

    with st.expander("Board details", expanded=False):
        current_folder_label = _folder_label(board.get("folder_id"), labels, values)
        with st.form(f"whiteboard_metadata_{board_id}"):
            title = st.text_input(
                "Whiteboard title",
                value=str(board.get("title", "")),
                max_chars=whiteboards.MAX_BOARD_TITLE_LENGTH,
                key=f"whiteboard_title_{board_id}",
            )
            folder_label = st.selectbox(
                "Folder",
                labels,
                index=labels.index(current_folder_label),
                key=f"whiteboard_folder_{board_id}",
            )
            save_metadata = st.form_submit_button("Save details", type="primary")
        if save_metadata:
            try:
                whiteboards.update_whiteboard_metadata(
                    board,
                    title=title,
                    folder_id=values[folder_label],
                )
            except ValueError as exc:
                st.warning(str(exc))
            else:
                state.mark_persistent_dirty()
                saved = state.flush_persistent_save()
                st.session_state["_whiteboard_component_save_status"][board_id] = "saved" if saved else "error"
                st.rerun()

    status = st.session_state.get("_persistent_save_status", "saved")
    status_map = st.session_state["_whiteboard_component_save_status"]
    if status == "saved" and not state.has_pending_persistence():
        status_map[board_id] = "saved"
    elif status == "error":
        status_map[board_id] = "error"
    if status == "error":
        st.error("Vocogni could not confirm that all changes were saved.")
        if st.button("Retry save", key=f"whiteboard_retry_save_{board_id}"):
            saved = state.flush_persistent_save()
            st.session_state["_whiteboard_component_save_status"][board_id] = "saved" if saved else "error"
            st.rerun()

    st.caption(
        "Pen, highlighter, eraser, text, sticky notes, shapes, selection, zoom, "
        "multi-page boards, undo/redo, and export are available in the canvas below."
    )
    ack_map = st.session_state["_whiteboard_component_ack"]
    event = _whiteboard_component(
        board=board,
        ack_event_id=ack_map.get(board_id, ""),
        save_status=status_map.get(board_id, status),
        key=f"whiteboard_canvas_{board_id}",
    )
    _consume_component_event(board, event)


def _consume_component_event(board: dict[str, Any], event: Any) -> None:
    """Validate component messages before they enter persistent learner state."""
    if not isinstance(event, dict) or event.get("type") != "board_update":
        return
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id or len(event_id) > 100:
        return

    board_id = board["id"]
    ack_map = st.session_state["_whiteboard_component_ack"]
    if ack_map.get(board_id) == event_id:
        return

    ack_map[board_id] = event_id
    status_map = st.session_state["_whiteboard_component_save_status"]
    try:
        candidate = whiteboards.sanitize_board(
            event.get("board"),
            default_id=board_id,
        )
        if candidate.get("id") != board_id:
            raise ValueError("This editor message does not belong to the open board.")

        # Metadata is managed by Python, not by the canvas iframe. Accept only
        # page/object content from the browser component.
        candidate["title"] = board["title"]
        candidate["folder_id"] = board.get("folder_id")
        candidate["created_at"] = board.get("created_at", "")
        old_content = {
            "pages": board.get("pages", []),
            "active_page_id": board.get("active_page_id"),
        }
        new_content = {
            "pages": candidate["pages"],
            "active_page_id": candidate["active_page_id"],
        }
        if old_content != new_content:
            board["pages"] = candidate["pages"]
            board["active_page_id"] = candidate["active_page_id"]
            board["updated_at"] = candidate.get("updated_at") or whiteboards.now_utc()
            state.mark_persistent_dirty()
            saved = state.flush_persistent_save()
            status_map[board_id] = "saved" if saved else "error"
        else:
            saved = state.flush_persistent_save()
            status_map[board_id] = "saved" if saved else "error"
    except (TypeError, ValueError) as exc:
        status_map[board_id] = "error"
        st.error(f"Whiteboard changes were rejected: {exc}")

    # The next component render receives the acknowledgement and save status.
    st.rerun()


def _escape(value: str) -> str:
    return (
        value.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&#39;")
    )
