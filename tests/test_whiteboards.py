"""Unit tests for Vocogni private whiteboard documents and restoration."""

import json
import unittest
from datetime import datetime, timezone

import whiteboards


class WhiteboardModelTests(unittest.TestCase):
    def test_create_board_starts_with_one_editable_graph_page(self):
        board = whiteboards.create_whiteboard(
            7, "Quadratic Functions", folder_id=3,
            now="2026-10-24T08:00:00+00:00",
        )
        self.assertEqual(board["id"], "board_7")
        self.assertEqual(board["title"], "Quadratic Functions")
        self.assertEqual(board["folder_id"], 3)
        self.assertEqual(len(board["pages"]), 1)
        self.assertEqual(board["pages"][0]["background"], "grid")
        self.assertEqual(board["pages"][0]["objects"], [])
        self.assertEqual(board["active_page_id"], "page_1")

    def test_sanitize_round_trips_all_supported_editable_objects(self):
        board = whiteboards.create_whiteboard(1, "Mixed board")
        board["pages"][0]["objects"] = [
            {"id": "stroke_1", "type": "stroke", "points": [[1, 2], [3, 4]],
             "color": "#2563EB", "width": 4, "opacity": 1},
            {"id": "shape_1", "type": "shape", "shape": "arrow", "x": 10, "y": 20,
             "width": 80, "height": -30, "color": "#D94A4A", "fill": "#FFFFFF",
             "filled": False, "stroke_width": 2},
            {"id": "text_1", "type": "text", "x": 30, "y": 60,
             "text": "y = x²", "color": "#1D2730", "font_size": 28},
            {"id": "sticky_1", "type": "sticky", "x": 50, "y": 70,
             "width": 220, "height": 140, "text": "Remember this",
             "color": "#FFF2A8", "text_color": "#303238", "font_size": 19},
        ]
        cleaned = whiteboards.sanitize_board(board)
        self.assertEqual([x["type"] for x in cleaned["pages"][0]["objects"]],
                         ["stroke", "shape", "text", "sticky"])
        self.assertEqual(cleaned["pages"][0]["objects"][2]["text"], "y = x²")
        self.assertEqual(cleaned["pages"][0]["objects"][3]["text"], "Remember this")
        self.assertEqual(cleaned["pages"][0]["objects"][0]["points"], [[1.0, 2.0], [3.0, 4.0]])

    def test_invalid_objects_are_skipped_and_strings_are_not_executed(self):
        board = whiteboards.create_whiteboard(1, "Safe board")
        board["pages"][0]["objects"] = [
            {"id": "unknown", "type": "image", "src": "javascript:alert(1)"},
            {"id": "bad-color", "type": "text", "x": 10, "y": 20,
             "text": "<script>alert('x')</script>", "color": "url(javascript:bad)"},
            {"id": "empty-stroke", "type": "stroke", "points": []},
            {"id": "unknown-shape", "type": "shape", "shape": "star"},
        ]
        clean = whiteboards.sanitize_board(board)
        self.assertEqual(len(clean["pages"][0]["objects"]), 1)
        self.assertEqual(clean["pages"][0]["objects"][0]["color"], "#2563EB")
        self.assertEqual(clean["pages"][0]["objects"][0]["text"], "<script>alert('x')</script>")

    def test_board_ids_and_page_ids_are_normalized_to_unique_supported_ids(self):
        board = whiteboards.create_whiteboard(1, "Pages")
        board["pages"] = [
            {"id": "duplicate", "background": "grid", "objects": []},
            {"id": "duplicate", "background": "dots", "objects": []},
            {"id": "../bad id", "background": "unknown", "objects": []},
        ]
        board["active_page_id"] = "duplicate"
        clean = whiteboards.sanitize_board(board)
        ids = [page["id"] for page in clean["pages"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(clean["pages"][2]["background"], "blank")
        self.assertIn(clean["active_page_id"], ids)

    def test_sanitize_enforces_page_object_point_and_document_limits(self):
        board = whiteboards.create_whiteboard(1, "Limits")
        board["pages"] = [
            {"id": "p" + str(i), "background": "blank", "objects": []}
            for i in range(whiteboards.MAX_PAGES + 5)
        ]
        clean = whiteboards.sanitize_board(board)
        self.assertEqual(len(clean["pages"]), whiteboards.MAX_PAGES)
        huge_stroke = {
            "id": "long", "type": "stroke",
            "points": [[i, i] for i in range(whiteboards.MAX_POINTS_PER_STROKE + 50)],
        }
        clean_stroke = whiteboards.sanitize_board({
            **board, "pages": [{"id": "p1", "objects": [huge_stroke]}]
        })["pages"][0]["objects"][0]
        self.assertEqual(len(clean_stroke["points"]), whiteboards.MAX_POINTS_PER_STROKE)
        with self.assertRaises(ValueError):
            whiteboards.sanitize_board({
                **board,
                "pages": [{"id": "p1", "objects": [
                    {"id": "t1", "type": "text", "text": "x" * whiteboards.MAX_OBJECT_TEXT_LENGTH,
                     "x": 0, "y": 20}
                    for _ in range(400)
                ]}],
            })

    def test_sanitize_caps_object_count_and_rejects_excessive_total_objects(self):
        board = whiteboards.create_whiteboard(1, "Many objects")
        board["pages"] = [{
            "id": "page_1",
            "background": "blank",
            "objects": [
                {"id": "text_" + str(i), "type": "text", "x": i, "y": i,
                 "text": "Note " + str(i), "color": "#2563EB", "font_size": 14}
                for i in range(whiteboards.MAX_OBJECTS_PER_PAGE + 100)
            ],
        }]
        cleaned = whiteboards.sanitize_board(board)
        self.assertEqual(len(cleaned["pages"][0]["objects"]), whiteboards.MAX_OBJECTS_PER_PAGE)

        too_many_pages = whiteboards.create_whiteboard(2, "Overflow")
        too_many_pages["pages"] = [
            {"id": "p" + str(i), "background": "blank",
             "objects": [
                 {"id": "text_" + str(j), "type": "text", "x": j, "y": j,
                  "text": "object", "font_size": 12}
                 for j in range(whiteboards.MAX_OBJECTS_PER_PAGE)
             ]}
            for i in range(4)
        ]
        with self.assertRaises(ValueError):
            whiteboards.sanitize_board(too_many_pages)

    def test_restore_ignores_corrupt_records_preserves_private_board_content(self):
        original = whiteboards.create_whiteboard(1, "Persisted board", 2)
        original["pages"][0]["objects"].append({
            "id": "text_1", "type": "text", "x": 30, "y": 50,
            "text": "My working", "color": "#2563EB", "font_size": 22,
        })
        cleaned = whiteboards.sanitize_whiteboards([
            None,
            {"title": ""},
            original,
            original,
        ])
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(cleaned[0]["title"], "Persisted board")
        self.assertEqual(cleaned[0]["pages"][0]["objects"][0]["text"], "My working")
        self.assertNotEqual(cleaned[0]["id"], cleaned[1]["id"])

    def test_next_id_avoids_reusing_numeric_board_ids(self):
        self.assertEqual(whiteboards.next_whiteboard_id([
            {"id": "board_1"}, {"id": "board_12"}, {"id": "custom-id"}
        ]), 13)

    def test_metadata_update_validates_title_and_preserves_page_objects(self):
        board = whiteboards.create_whiteboard(1, "Original", None)
        board["pages"][0]["objects"].append({
            "id": "text_1", "type": "text", "x": 1, "y": 2,
            "text": "Keep", "color": "#2563EB", "font_size": 20,
        })
        whiteboards.update_whiteboard_metadata(board, title="  Renamed  ", folder_id=4)
        self.assertEqual(board["title"], "Renamed")
        self.assertEqual(board["folder_id"], 4)
        self.assertEqual(board["pages"][0]["objects"][0]["text"], "Keep")
        with self.assertRaises(ValueError):
            whiteboards.update_whiteboard_metadata(board, title=" ", folder_id=None)

    def test_document_json_is_plain_json_and_within_declared_limit(self):
        board = whiteboards.create_whiteboard(3, "JSON")
        encoded = json.dumps(whiteboards.sanitize_board(board), ensure_ascii=False)
        self.assertLessEqual(len(encoded.encode("utf-8")), whiteboards.MAX_BOARD_BYTES)
        self.assertIsInstance(json.loads(encoded), dict)


if __name__ == "__main__":
    unittest.main()
