"""Regression tests for the learner profile layout and avatar workflow."""
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ProfileUiTests(unittest.TestCase):
    def test_description_section_follows_subjects_and_goals(self):
        source = (ROOT / "sections" / "profile.py").read_text(encoding="utf-8")
        self.assertLess(source.index('"id": "goals"'), source.index('"id": "description"'))
        description = source[source.index('"id": "description"'):]
        self.assertIn('("description", "About me", "textarea", None)', description)

    def test_save_profile_control_is_after_profile_sections(self):
        source = (ROOT / "sections" / "profile.py").read_text(encoding="utf-8")
        render = source[source.index("def render()"):]
        self.assertLess(render.index("for section in _SECTIONS:"), render.index("_render_save_control(profile)"))

    def test_avatar_is_clickable_and_uses_processed_profile_image(self):
        source = (ROOT / "sections" / "profile.py").read_text(encoding="utf-8")
        self.assertIn('key="profile_avatar_trigger"', source)
        self.assertIn('key="profile_avatar_upload"', source)
        self.assertIn("process_profile_avatar(raw_bytes)", source)
        self.assertIn("state.mark_persistent_dirty()", source)
        self.assertIn("Remove profile picture", source)

    def test_description_is_in_default_durable_profile_schema(self):
        source = (ROOT / "state.py").read_text(encoding="utf-8")
        self.assertIn('"description": ""', source)


if __name__ == "__main__":
    unittest.main()
