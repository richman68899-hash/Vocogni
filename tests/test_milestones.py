"""Unit tests for milestone and checklist data helpers."""
import unittest
from datetime import date, timedelta

import milestones


class MilestoneDataTests(unittest.TestCase):
    def test_create_milestone_trims_title_and_stores_metadata(self):
        due = date(2026, 11, 7)
        milestone = milestones.create_milestone(
            4,
            "  Finish fractions  ",
            due,
            section="Maths",
            color="Purple",
            emoji="📐",
            now="2026-10-24 10:00",
        )

        self.assertEqual(milestone["id"], 4)
        self.assertEqual(milestone["title"], "Finish fractions")
        self.assertEqual(milestone["end_date"], "2026-11-07")
        self.assertEqual(milestone["section"], "Maths")
        self.assertEqual(milestone["color"], "Purple")
        self.assertEqual(milestone["emoji"], "📐")
        self.assertEqual(milestone["checklist"], [])
        self.assertEqual(milestone["next_item_id"], 1)

    def test_create_milestone_rejects_blank_title_and_invalid_date(self):
        with self.assertRaises(ValueError):
            milestones.create_milestone(1, "  ", date.today())
        with self.assertRaises(ValueError):
            milestones.create_milestone(1, "Valid title", "not-a-date")

    def test_checklist_supports_many_items_and_never_reuses_deleted_ids(self):
        milestone = milestones.create_milestone(
            1, "Large goal", date.today() + timedelta(days=30)
        )
        items = [
            milestones.add_checklist_item(milestone, f"Step {index}")
            for index in range(150)
        ]

        self.assertEqual(len(milestone["checklist"]), 150)
        self.assertEqual(items[0]["id"], 1)
        self.assertEqual(items[-1]["id"], 150)
        self.assertTrue(milestones.delete_checklist_item(milestone, 150))
        next_item = milestones.add_checklist_item(milestone, "New step")
        self.assertEqual(next_item["id"], 151)
        self.assertFalse(next_item["done"])
        self.assertEqual(len(milestone["checklist"]), 150)

    def test_checklist_item_can_be_completed_reopened_and_edited(self):
        milestone = milestones.create_milestone(
            1, "Study goal", date.today() + timedelta(days=7)
        )
        item = milestones.add_checklist_item(milestone, "Do practice")
        milestones.set_checklist_item_done(milestone, item["id"], True)
        milestones.update_checklist_item(milestone, item["id"], "Finish 10 questions")

        self.assertTrue(item["done"])
        self.assertEqual(item["text"], "Finish 10 questions")
        milestones.set_checklist_item_done(milestone, item["id"], False)
        self.assertFalse(item["done"])

    def test_checklist_item_operations_reject_blank_text_or_unknown_ids(self):
        milestone = milestones.create_milestone(
            1, "Study goal", date.today() + timedelta(days=7)
        )
        with self.assertRaises(ValueError):
            milestones.add_checklist_item(milestone, " ")
        with self.assertRaises(KeyError):
            milestones.update_checklist_item(milestone, 123, "New text")
        with self.assertRaises(KeyError):
            milestones.set_checklist_item_done(milestone, 123, True)
        self.assertFalse(milestones.delete_checklist_item(milestone, 123))

    def test_update_milestone_changes_metadata_without_resetting_checklist(self):
        milestone = milestones.create_milestone(
            1, "Original title", date.today() + timedelta(days=7)
        )
        item = milestones.add_checklist_item(milestone, "Saved step")
        milestones.set_checklist_item_done(milestone, item["id"], True)

        milestones.update_milestone(
            milestone,
            title="Updated title",
            end_date=date(2026, 12, 1),
            section="Productivity",
            color="Orange",
            emoji="🚀",
        )

        self.assertEqual(milestone["title"], "Updated title")
        self.assertEqual(milestone["end_date"], "2026-12-01")
        self.assertEqual(milestone["section"], "Productivity")
        self.assertEqual(milestone["color"], "Orange")
        self.assertEqual(milestone["emoji"], "🚀")
        self.assertEqual(milestone["checklist"], [item])
        self.assertTrue(item["done"])

    def test_sanitize_milestones_preserves_valid_data_and_ignores_bad_records(self):
        saved = [
            None,
            {"id": 1, "title": "Valid", "end_date": "2026-11-01",
             "section": "Maths", "color": "Green", "emoji": "📐",
             "checklist": [
                 {"id": 1, "text": "Completed step", "done": True},
                 {"id": 2, "text": "  ", "done": False},
             ]},
            {"id": 1, "title": "Duplicate ID", "end_date": "bad date",
             "section": "Not a section", "color": "not a color", "emoji": "not emoji",
             "checklist": [{"id": 1, "text": "Recovered step"}]},
            {"id": 4, "title": "   "},
        ]
        cleaned = milestones.sanitize_milestones(saved)

        self.assertEqual(len(cleaned), 2)
        self.assertEqual([item["id"] for item in cleaned], [1, 2])
        self.assertEqual(cleaned[0]["checklist"][0]["text"], "Completed step")
        self.assertTrue(cleaned[0]["checklist"][0]["done"])
        self.assertEqual(cleaned[1]["section"], "Other")
        self.assertEqual(cleaned[1]["color"], "Grey")
        self.assertEqual(cleaned[1]["emoji"], "🎯")
        self.assertEqual(cleaned[1]["checklist"][0]["id"], 1)
        self.assertEqual(milestones.next_milestone_id(cleaned), 3)

    def test_sanitize_handles_missing_or_non_list_data(self):
        self.assertEqual(milestones.sanitize_milestones(None), [])
        self.assertEqual(milestones.sanitize_milestones({"bad": "shape"}), [])


if __name__ == "__main__":
    unittest.main()
