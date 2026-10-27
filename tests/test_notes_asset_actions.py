"""Framework-free regression tests for saved-asset selection helpers.

The diagnostics workflow intentionally does not install Streamlit. Extracting
these pure session-state helpers from sections/notes.py lets CI execute their
real implementations without importing the UI framework.
"""

import ast
import unittest
from pathlib import Path
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[1]
NOTES_SOURCE = ROOT / "sections" / "notes.py"
HELPER_NAMES = {
    "_begin_asset_selection",
    "_toggle_asset_selection",
    "_clear_asset_selection",
    "_reset_asset_selection_widgets",
    "_delete_notes",
    "_delete_folders",
    "_delete_milestones",
}


class FakeSessionState(dict):
    """Small dict-backed stand-in for Streamlit's attribute-access state."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class SavedAssetActionTests(unittest.TestCase):
    def setUp(self):
        self.session = FakeSessionState()
        self.dirty_calls = []
        namespace = {
            "Any": object,
            "st": SimpleNamespace(session_state=self.session),
            "_now": lambda: "2026-10-27 20:00",
            "_mark_changed": lambda: self.dirty_calls.append(True),
        }
        tree = ast.parse(NOTES_SOURCE.read_text(encoding="utf-8"))
        selected = [
            node for node in tree.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in HELPER_NAMES
        ]
        self.assertEqual({node.name for node in selected}, HELPER_NAMES)
        module = ast.Module(body=selected, type_ignores=[])
        exec(compile(module, str(NOTES_SOURCE), "exec"), namespace)
        self.helpers = namespace

    def test_delete_folder_preserves_notes_and_returns_them_to_unfiled(self):
        self.session.note_folders = [
            {"id": 1, "name": "Algebra"},
            {"id": 2, "name": "Geometry"},
        ]
        self.session.notes = [
            {"id": 10, "folder_id": 1, "updated_at": "old"},
            {"id": 11, "folder_id": 2, "updated_at": "old"},
        ]
        self.session.selected_note_folder_id = 1
        self.session.selected_folders_ids = [1]
        self.session.folders_bulk_select_mode = True
        self.session["select_folders_1"] = True

        self.helpers["_delete_folders"]([1])

        self.assertEqual([row["id"] for row in self.session.note_folders], [2])
        self.assertEqual([row["id"] for row in self.session.notes], [10, 11])
        self.assertIsNone(self.session.notes[0]["folder_id"])
        self.assertEqual(self.session.notes[1]["folder_id"], 2)
        self.assertIsNone(self.session.selected_note_folder_id)
        self.assertFalse(self.session.folders_bulk_select_mode)
        self.assertTrue(self.session.folders_reset_selection_widgets)
        self.assertIn(1, self.session.folders_reset_selection_widget_ids)
        self.assertEqual(len(self.dirty_calls), 1)

    def test_delete_note_clears_editor_and_marks_saved_data_dirty(self):
        self.session.notes = [
            {"id": 10, "title": "Keep"},
            {"id": 11, "title": "Delete"},
        ]
        self.session.selected_note_id = 11
        self.session.note_editor_open = True
        self.session.selected_notes_ids = [11]
        self.session.notes_bulk_select_mode = True

        self.helpers["_delete_notes"]([11])

        self.assertEqual([row["id"] for row in self.session.notes], [10])
        self.assertIsNone(self.session.selected_note_id)
        self.assertFalse(self.session.note_editor_open)
        self.assertFalse(self.session.notes_bulk_select_mode)
        self.assertEqual(self.session.selected_notes_ids, [])
        self.assertTrue(self.session.notes_reset_selection_widgets)
        self.assertEqual(len(self.dirty_calls), 1)

    def test_delete_milestones_removes_only_requested_items(self):
        self.session.milestones = [{"id": 1}, {"id": 2}]
        self.session.selected_milestones_ids = [1]
        self.session.milestones_bulk_select_mode = True

        self.helpers["_delete_milestones"]([1])

        self.assertEqual(self.session.milestones, [{"id": 2}])
        self.assertEqual(self.session.selected_milestones_ids, [])
        self.assertFalse(self.session.milestones_bulk_select_mode)
        self.assertEqual(len(self.dirty_calls), 1)

    def test_select_all_and_toggle_update_selection_state(self):
        begin = self.helpers["_begin_asset_selection"]
        toggle = self.helpers["_toggle_asset_selection"]
        begin("notes", [10, 11])

        self.assertTrue(self.session.notes_bulk_select_mode)
        self.assertEqual(self.session.selected_notes_ids, [10, 11])
        self.assertTrue(self.session["select_notes_10"])
        self.assertTrue(self.session["select_notes_11"])

        self.session["select_notes_10"] = False
        toggle("notes", 10, "select_notes_10")
        self.assertEqual(self.session.selected_notes_ids, [11])

        self.session["select_notes_12"] = True
        toggle("notes", 12, "select_notes_12")
        self.assertEqual(self.session.selected_notes_ids, [11, 12])

    def test_checkbox_keys_are_reset_before_the_next_render(self):
        self.session.notes = [{"id": 10}]
        self.session.selected_notes_ids = [10]
        self.session.notes_bulk_select_mode = True
        self.session["select_notes_10"] = True

        self.helpers["_clear_asset_selection"]("notes")
        self.assertTrue(self.session["select_notes_10"])

        self.helpers["_reset_asset_selection_widgets"]("notes", self.session.notes)

        self.assertNotIn("select_notes_10", self.session)
        self.assertFalse(self.session.notes_reset_selection_widgets)
        self.assertNotIn("notes_reset_selection_widget_ids", self.session)


if __name__ == "__main__":
    unittest.main()
