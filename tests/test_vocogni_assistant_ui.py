"""Regression checks for persistent quick-request shortcuts in the assistant UI."""

from pathlib import Path
import unittest


class AssistantPromptVisibilityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (Path(__file__).resolve().parents[1] / "vocogni_assistant.py").read_text(
            encoding="utf-8"
        )

    def test_quick_requests_are_sticky_within_the_scrollable_panel(self):
        selector = ".st-key-vocogni_assistant_quick_requests {"
        self.assertIn(selector, self.source)
        rule_start = self.source.index(selector)
        rule_end = self.source.index("}", rule_start)
        rule = self.source[rule_start:rule_end]

        self.assertIn("position: sticky", rule)
        self.assertIn("top:", rule)
        self.assertIn("z-index:", rule)

    def test_quick_requests_render_independently_of_message_history(self):
        render = self.source.split("def render_assistant(", 1)[1]
        quick_requests = 'with st.container(key="vocogni_assistant_quick_requests")'
        self.assertIn(quick_requests, render)
        prompts_index = render.index(quick_requests)
        history_index = render.index("for message in messages[-8:]")
        self.assertLess(prompts_index, history_index)
        self.assertNotIn("if messages", render[prompts_index:history_index])
        self.assertIn("These shortcuts stay available while you chat.", render)


if __name__ == "__main__":
    unittest.main()
