"""Python bridge for the local Streamlit v1 whiteboard component.

The browser retains an unacknowledged edit until Python validates the board and
confirms a successful save through the ordinary learner-state persistence path.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import streamlit as st
import streamlit.components.v1 as components

import state
import whiteboards


_COMPONENT_DIR = Path(__file__).resolve().parents[1] / "components" / "whiteboard"
whiteboard_canvas = components.declare_component(
    "vocogni_whiteboard",
    path=str(_COMPONENT_DIR),
)


def _replace_saved_board(board_id: str, board: dict[str, Any]) -> bool:
    """Replace a board without touching any other learner data."""
    current = st.session_state.get("whiteboards", [])
    if not isinstance(current, list):
        return False
    for index, item in enumerate(current):
        if isinstance(item, dict) and item.get("id") == board_id:
            current[index] = board
            st.session_state.whiteboards = current
            return True
    return False


def _consume_component_event(event: Any, expected_board_id: str) -> bool:
    """Validate, persist, and acknowledge a completed browser edit.

    Event IDs make the component protocol idempotent across Streamlit reruns.
    The acknowledgement only advances after flush_persistent_save() reports
    success, so a temporary database failure never silently discards an edit.
    """
    if not isinstance(event, dict):
        return False

    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id or len(event_id) > 120:
        return False
    if event_id == st.session_state.get("whiteboard_ack_event_id"):
        return False
    if event.get("board_id") != expected_board_id:
        return False

    incoming = event.get("board")
    board = whiteboards.sanitize_board(incoming)
    if board is None or board.get("id") != expected_board_id:
        return False
    if not board.get("pages"):
        return False
    event_page_id = event.get("page_id")
    if not isinstance(event_page_id, str) or event_page_id not in {p.get("id") for p in board["pages"]}:
        return False

    # The component can update pages and object lists, but cannot change a
    # board's placement/title or create a different board via a canvas event.
    existing = next(
        (item for item in st.session_state.get("whiteboards", [])
         if isinstance(item, dict) and item.get("id") == expected_board_id),
        None,
    )
    if existing is None:
        return False
    board["title"] = str(existing.get("title", board.get("title", "Whiteboard")))[:100]
    board["folder_id"] = existing.get("folder_id")
    board["created_at"] = existing.get("created_at", board.get("created_at", ""))
    import datetime
    board["updated_at"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    if not _replace_saved_board(expected_board_id, board):
        return False

    state.mark_persistent_dirty()
    if not state.flush_persistent_save():
        st.session_state["whiteboard_save_error"] = True
        return False

    st.session_state["whiteboard_ack_event_id"] = event_id
    st.session_state["selected_whiteboard_page_id"] = event_page_id
    st.session_state["whiteboard_save_error"] = False
    return True


def render_editor(board: dict[str, Any]) -> None:
    """Mount the browser canvas and handle its last event."""
    if not isinstance(board, dict) or not board.get("pages"):
        st.error("This whiteboard has no valid pages.")
        return

    page_id = st.session_state.get("selected_whiteboard_page_id")
    if not any(page.get("id") == page_id for page in board["pages"]):
        page_id = board["pages"][0]["id"]
        st.session_state["selected_whiteboard_page_id"] = page_id

    result = whiteboard_canvas(
        board=board,
        page_id=page_id,
        ack_event_id=st.session_state.get("whiteboard_ack_event_id"),
        key=f"whiteboard_component_{board['id']}",
        default=None,
    )
    if _consume_component_event(result, board["id"]):
        # Re-render with the acknowledged event ID.
        st.rerun()

    if st.session_state.get("whiteboard_save_error"):
        st.warning(
            "The whiteboard edit is still pending because saving failed. "
            "The canvas keeps the unacknowledged edit; press Save now to retry."
        )
