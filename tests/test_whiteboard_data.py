"""Data validation and export tests for the Notes whiteboard."""
import unittest

import whiteboard_data


class WhiteboardDataTests(unittest.TestCase):
    def test_create_board_keeps_template_and_ids(self):
        board = whiteboard_data.create_board(
            title="  Coordinate plane  ", folder_id=2, template="Coordinate plane"
        )
        self.assertEqual(board["title"], "Coordinate plane")
        self.assertEqual(board["folder_id"], 2)
        self.assertEqual(len(board["pages"]), 1)
        self.assertEqual(board["pages"][0]["background"], "grid")
        self.assertGreaterEqual(len(board["pages"][0]["objects"]), 2)
        self.assertTrue(board["id"])

    def test_sanitize_page_rejects_invalid_objects_and_bounds_size(self):
        page = {
            "id": "valid-page",
            "background": "javascript:alert(1)",
            "objects": [
                {"id": "invalid", "type": "arbitrary-html", "value": "<script>"},
                {"id": "text", "type": "text", "x": "nan", "y": 20,
                 "text": "hello", "color": "red", "fontSize": 1},
                {"id": "stroke", "type": "stroke", "color": "#112233", "width": 4,
                 "points": [{"x": 1, "y": 2}, {"x": 3, "y": 4}]},
            ],
        }
        cleaned = whiteboard_data.sanitize_page(page)
        self.assertEqual(cleaned["background"], "grid")
        self.assertEqual(len(cleaned["objects"]), 2)
        text = cleaned["objects"][0]
        self.assertEqual(text["color"], "#273142")
        self.assertEqual(text["x"], 0.0)
        self.assertEqual(text["fontSize"], 10.0)
        self.assertEqual(len(cleaned["objects"][1]["points"]), 2)

    def test_sanitize_boards_discards_invalid_and_duplicate_ids(self):
        good = whiteboard_data.create_board(title="Valid board")
        duplicate = dict(good)
        invalid = {"id": "bad", "title": "No pages", "pages": "not a list"}
        restored = whiteboard_data.sanitize_boards([good, duplicate, invalid, None])
        self.assertEqual(len(restored), 2)
        self.assertEqual(restored[0]["id"], good["id"])
        self.assertEqual(len(restored[1]["pages"]), 1)
        self.assertLessEqual(len(restored), whiteboard_data.MAX_BOARDS)

    def test_svg_export_escapes_text_and_keeps_vector_objects(self):
        page = whiteboard_data.create_page("Export", "plain")
        page["objects"] = [
            {"id": "text-1", "type": "text", "x": 30, "y": 45,
             "text": "<script>alert('x')</script>", "color": "#112233", "fontSize": 22},
            {"id": "shape-1", "type": "shape", "shape": "ellipse",
             "x": 50, "y": 50, "w": 100, "h": 60, "color": "#445566", "width": 3},
        ]
        svg = whiteboard_data.page_to_svg(page)
        self.assertIn("<svg", svg)
        self.assertIn("&lt;script&gt;", svg)
        self.assertNotIn("<script>", svg)
        self.assertIn("<ellipse", svg)

    def test_aggregate_board_limits_bound_objects_and_strokes(self):
        board = whiteboard_data.create_board(title="Large board")
        board["pages"] = []
        for index in range(10):
            page = whiteboard_data.create_page(f"Page {index + 1}", "plain")
            page["objects"] = [
                {"id": f"{index}-{item}", "type": "text", "x": 0, "y": 20,
                 "text": "x", "color": "#273142", "fontSize": 20}
                for item in range(whiteboard_data.MAX_OBJECTS_PER_PAGE)
            ]
            board["pages"].append(page)
        cleaned = whiteboard_data.sanitize_boards([board])[0]
        total_objects = sum(len(page["objects"]) for page in cleaned["pages"])
        total_text = sum(
            len(obj.get("text", ""))
            for page in cleaned["pages"]
            for obj in page["objects"]
            if obj.get("type") in {"text", "sticky"}
        )
        self.assertLessEqual(total_objects, whiteboard_data.MAX_OBJECTS_PER_BOARD)
        self.assertLessEqual(total_text, whiteboard_data.MAX_TEXT_CHARS_PER_BOARD)

    def test_limits_bound_large_inputs(self):
        raw = whiteboard_data.create_page()
        raw["objects"] = [
            {"id": f"t{i}", "type": "text", "x": 0, "y": 0, "text": "x",
             "color": "#273142", "fontSize": 24}
            for i in range(whiteboard_data.MAX_OBJECTS_PER_PAGE + 10)
        ]
        cleaned = whiteboard_data.sanitize_page(raw)
        self.assertEqual(len(cleaned["objects"]), whiteboard_data.MAX_OBJECTS_PER_PAGE)


if __name__ == "__main__":
    unittest.main()
