"""Regression checks for Notes saved-asset actions.

These UI wiring tests intentionally avoid importing Streamlit widgets. The runtime
state mutations remain in the shared Notes module and use Vocogni's autosave hook.
"""
import ast
from pathlib import Path


SOURCE_PATH = Path(__file__).resolve().parents[1] / "sections" / "notes.py"
SOURCE = SOURCE_PATH.read_text(encoding="utf-8")
TREE = ast.parse(SOURCE)


def function_source(name: str) -> str:
    """Return the source for one top-level function."""
    node = next(
        item for item in TREE.body
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name == name
    )
    lines = SOURCE.splitlines()
    return "\n".join(lines[node.lineno - 1:node.end_lineno])


def test_note_title_validation_rejects_blank_and_non_text_values():
    node = next(
        item for item in TREE.body
        if isinstance(item, ast.FunctionDef) and item.name == "_clean_note_title"
    )
    isolated = ast.Module(body=[node], type_ignores=[])
    namespace = {}
    exec(compile(isolated, str(SOURCE_PATH), "exec"), namespace)
    clean = namespace["_clean_note_title"]
    assert clean("  Algebra notes  ") == "Algebra notes"
    for invalid in ("", "   ", None, 12):
        try:
            clean(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid note title was accepted: " + repr(invalid))


def test_editor_validates_note_title_before_mutating_saved_notes():
    editor = function_source("_render_editor")
    assert editor.index("_clean_note_title(title)") < editor.index("existing.update(")
    assert editor.index("_clean_note_title(title)") < editor.index("st.session_state.notes.append(")
    assert "st.warning(str(exc))" in editor


def test_notes_folders_and_milestones_have_three_dot_menus():
    assert 'st.popover("⋯"' in function_source("_render_note_overflow_menu")
    assert 'st.popover("⋯"' in function_source("_render_folder_overflow_menu")
    assert 'st.popover("⋯"' in function_source("_render_milestone_overflow_menu")


def test_bulk_toolbar_supports_select_all_delete_and_note_move():
    toolbar = function_source("_render_bulk_toolbar")
    assert "Select all shown" in toolbar
    assert "Delete selected" in toolbar
    assert "Move selected notes to" in toolbar
    assert '_mark_changed()' in toolbar


def test_deleting_folder_preserves_and_unfiles_its_notes():
    deletion = function_source("_confirm_pending_asset_deletion")
    assert 'note["folder_id"] = None' in deletion
    assert "st.session_state.note_folders = [" in deletion
    assert "no note content will be deleted" in function_source("_render_pending_asset_deletion")


def test_destructive_actions_require_confirmation_and_can_be_cancelled():
    confirmation = function_source("_render_pending_asset_deletion")
    editor = function_source("_render_editor")
    assert 'st.button("Confirm delete"' in confirmation
    assert 'st.button("Cancel"' in confirmation
    assert '_confirm_pending_asset_deletion()' in confirmation
    assert '_request_asset_deletion("note"' in editor
