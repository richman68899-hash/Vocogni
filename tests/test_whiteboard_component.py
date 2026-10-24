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

    def test_component_has_drawing_and_page_controls(self):
        html = (COMPONENT / "index.html").read_text(encoding="utf-8")
        for tool in (
            'data-tool="select"', 'data-tool="pen"', 'data-tool="highlighter"',
            'data-tool="eraser"', 'data-tool="text"', 'data-tool="sticky"',
            'data-tool="hand"', 'data-tool="rectangle"', 'data-tool="ellipse"',
            'data-tool="triangle"', 'data-tool="line"', 'data-tool="arrow"',
        ):
            with self.subTest(tool=tool):
                self.assertIn(tool, html)
        for action in (
            'id="undo"', 'id="redo"', 'id="duplicate"', 'id="delete-selected"',
            'id="previous-page"', 'id="next-page"', 'id="new-page"',
            'id="duplicate-page"', 'id="delete-page"', 'id="export-png"',
            'id="export-pdf"', 'id="export-json"', 'id="save-now"',
        ):
            with self.subTest(action=action):
                self.assertIn(action, html)

    def test_component_uses_bidirectional_streamlit_messages_and_save_ack(self):
        js = (COMPONENT / "whiteboard.js").read_text(encoding="utf-8")
        for token in (
            "streamlit:componentReady", "streamlit:render",
            "streamlit:setComponentValue", "ack_event_id", "pendingRev",
            "function undoFn", "function redoFn", "function exportSvg",
            "function pdf",
        ):
            with self.subTest(token=token):
                self.assertIn(token, js)

    def test_editor_uses_local_component_and_validates_updates(self):
        editor = (ROOT / "sections" / "whiteboard_editor.py").read_text(encoding="utf-8")
        self.assertIn("components.declare_component", editor)
        self.assertIn("_consume_component_event", editor)
        self.assertIn("whiteboards.sanitize_board", editor)
        self.assertIn("state.flush_persistent_save()", editor)
        self.assertIn("event_id", editor)

    def test_notes_workspace_exposes_whiteboards(self):
        notes = (ROOT / "sections" / "notes.py").read_text(encoding="utf-8")
        self.assertIn('"Whiteboards"', notes)
        self.assertIn("whiteboard_editor.render()", notes)


if __name__ == "__main__":
    unittest.main()
