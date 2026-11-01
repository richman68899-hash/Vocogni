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
        self.assertIn('profile_avatar_upload_', source)
        self.assertIn("process_profile_avatar(raw_bytes)", source)
        self.assertIn("state.mark_persistent_dirty()", source)
        self.assertIn("Remove profile picture", source)

    def test_profile_header_has_shop_button_and_vocoins_balance(self):
        source = (ROOT / "sections" / "profile.py").read_text(encoding="utf-8")
        state_source = (ROOT / "state.py").read_text(encoding="utf-8")
        self.assertIn('key="profile_shop_button"', source)
        self.assertIn("profile_shop_open", source)
        self.assertIn("Vocoins", source)
        self.assertIn('profile.get("vocoins", 0)', source)
        self.assertIn('"vocoins": 0', state_source)
        self.assertIn("max(0, int(raw_vocoins))", source)
        self.assertIn("M7.2 7.1 12 17l4.8-9.9", source)
        self.assertIn("justify-content:flex-end", source)
        self.assertIn("width:max-content", source)
        self.assertIn("width:16px;height:16px", source)

    def test_description_is_in_default_durable_profile_schema(self):
        source = (ROOT / "state.py").read_text(encoding="utf-8")
        self.assertIn('"description": ""', source)


if __name__ == "__main__":
    unittest.main()
