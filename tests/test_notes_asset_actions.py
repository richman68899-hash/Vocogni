"""Regression tests for saved-asset action and multi-select helpers."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from sections import notes as notes_section


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
        self.streamlit = SimpleNamespace(session_state=self.session)
        self.streamlit_patch = patch.object(notes_section, "st", self.streamlit)
        self.streamlit_patch.start()
        self.addCleanup(self.streamlit_patch.stop)
        self.dirty_patch = patch.object(notes_section.state, "mark_persistent_dirty")
        self.mark_dirty = self.dirty_patch.start()
        self.addCleanup(self.dirty_patch.stop)

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

        notes_section._delete_folders([1])

        self.assertEqual([row["id"] for row in self.session.note_folders], [2])
        self.assertEqual([row["id"] for row in self.session.notes], [10, 11])
        self.assertIsNone(self.session.notes[0]["folder_id"])
        self.assertEqual(self.session.notes[1]["folder_id"], 2)
        self.assertIsNone(self.session.selected_note_folder_id)
        self.assertFalse(self.session.folders_bulk_select_mode)
        self.assertTrue(self.session.folders_reset_selection_widgets)
        self.assertIn(1, self.session.folders_reset_selection_widget_ids)
        self.mark_dirty.assert_called_once()

    def test_delete_note_clears_editor_and_marks_saved_data_dirty(self):
        self.session.notes = [
            {"id": 10, "title": "Keep"},
            {"id": 11, "title": "Delete"},
        ]
        self.session.selected_note_id = 11
        self.session.note_editor_open = True
        self.session.selected_notes_ids = [11]
        self.session.notes_bulk_select_mode = True

        notes_section._delete_notes([11])

        self.assertEqual([row["id"] for row in self.session.notes], [10])
        self.assertIsNone(self.session.selected_note_id)
        self.assertFalse(self.session.note_editor_open)
        self.assertFalse(self.session.notes_bulk_select_mode)
        self.assertEqual(self.session.selected_notes_ids, [])
        self.assertTrue(self.session.notes_reset_selection_widgets)
        self.mark_dirty.assert_called_once()

    def test_delete_milestones_removes_only_requested_items(self):
        self.session.milestones = [{"id": 1}, {"id": 2}]
        self.session.selected_milestones_ids = [1]
        self.session.milestones_bulk_select_mode = True

        notes_section._delete_milestones([1])

        self.assertEqual(self.session.milestones, [{"id": 2}])
        self.assertEqual(self.session.selected_milestones_ids, [])
        self.assertFalse(self.session.milestones_bulk_select_mode)
        self.mark_dirty.assert_called_once()

    def test_checkbox_keys_are_reset_before_the_next_render(self):
        self.session.notes = [{"id": 10}]
        self.session.selected_notes_ids = [10]
        self.session.notes_bulk_select_mode = True
        self.session["select_notes_10"] = True

        notes_section._clear_asset_selection("notes")
        # A rendered Streamlit widget key is not mutated during the same run.
        self.assertTrue(self.session["select_notes_10"])

        notes_section._reset_asset_selection_widgets("notes", self.session.notes)

        self.assertNotIn("select_notes_10", self.session)
        self.assertFalse(self.session.notes_reset_selection_widgets)
        self.assertNotIn("notes_reset_selection_widget_ids", self.session)


if __name__ == "__main__":
    unittest.main()
