"""Static integration tests for the local whiteboard component."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "components" / "whiteboard"


class WhiteboardComponentTests(unittest.TestCase):
    def test_component_assets_are_local_and_linked(self):
        html = (COMPONENT / "index.html").read_text(encoding="utf-8")
        css = (COMPONENT / "whiteboard.css").read_text(encoding="utf-8")
        js = (COMPONENT / "whiteboard.js").read_text(encoding="utf-8")

        self.assertIn('href="whiteboard.css"', html)
        self.assertIn('src="whiteboard.js"', html)
        self.assertIn('id="stage"', html)
        self.assertIn("touch-action: none", css)
        self.assertNotIn("unpkg.com", html + js)
        self.assertNotIn("cdn.jsdelivr.net", html + js)

    def test_component_has_core_drawing_tools_and_accessible_controls(self):
        html = (COMPONENT / "index.html").read_text(encoding="utf-8")
        for tool in (
            'data-tool="select"',
            'data-tool="pen"',
            'data-tool="highlighter"',
            'data-tool="eraser"',
            'data-tool="text"',
            'data-tool="sticky"',
            'data-tool="hand"',
            'data-tool="rectangle"',
            'data-tool="ellipse"',
            'data-tool="triangle"',
            'data-tool="line"',
            'data-tool="arrow"',
        ):
            with self.subTest(tool=tool):
                self.assertIn(tool, html)
        for action in (
            'id="undo"', 'id="redo"', 'id="duplicate"',
            'id="delete-selected"', 'id="previous-page"',
            'id="next-page"', 'id="new-page"', 'id="duplicate-page"',
            'id="delete-page"', 'id="export-png"', 'id="export-pdf"',
            'id="export-json"', 'id="save-now"', 'id="clear-page"', 'id="zoom"',
        ):
            with self.subTest(action=action):
                self.assertIn(action, html)

    def test_component_uses_bidirectional_streamlit_messages_and_acknowledged_saves(self):
        js = (COMPONENT / "whiteboard.js").read_text(encoding="utf-8")
        self.assertIn("streamlit:componentReady", js)
        self.assertIn("streamlit:render", js)
        self.assertIn("streamlit:setComponentValue", js)
        self.assertIn("ack_event_id", js)
        self.assertIn("pendingRev", js)
        self.assertIn("function undoFn", js)
        self.assertIn("function redoFn", js)
        self.assertIn("function exportSvg", js)
        self.assertIn("function pdf", js)
        self.assertIn('$("#clear-page")', js)
        self.assertIn('$("#zoom")', js)
        self.assertIn("state.dragging.resize", js)

    def test_editor_uses_local_component_and_validates_board_updates(self):
        editor = (ROOT / "sections" / "whiteboard_editor.py").read_text(encoding="utf-8")
        self.assertIn("components.declare_component", editor)
        self.assertIn("_consume_component_event", editor)
        self.assertIn("whiteboards.sanitize_board", editor)
        self.assertIn("state.flush_persistent_save()", editor)
        self.assertIn("event_id", editor)


if __name__ == "__main__":
    unittest.main()
