"""Regression checks for the compact Profile Streak Forest entry point."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class StreakForestUiTests(unittest.TestCase):
    def test_forest_is_hidden_behind_profile_entry_button(self):
        source = (ROOT / "streak_garden" / "ui.py").read_text(encoding="utf-8")
        self.assertIn('key="view_streak_forest"', source)
        self.assertIn('"View streak forest"', source)
        self.assertIn('if not st.session_state.get("streak_forest_open", False):', source)
        self.assertIn('"← Back to Profile"', source)

    def test_one_forest_is_created_per_existing_milestone_only_on_request(self):
        source = (ROOT / "streak_garden" / "ui.py").read_text(encoding="utf-8")
        self.assertIn('f"milestone_{int(milestone[\'id\'])}"', source)
        self.assertIn('"Add milestone forest"', source)
        self.assertIn('forest_id not in current_state.get("forests", {})', source)
        self.assertIn('if forest is None:', source)

    def test_original_local_svg_assets_are_embedded_without_remote_urls(self):
        source = (ROOT / "streak_garden" / "ui.py").read_text(encoding="utf-8")
        self.assertIn('data:image/svg+xml;base64,', source)
        self.assertIn('"forest_landscape.svg"', source)
        for asset in (
            "tree_seedling.svg",
            "tree_sapling.svg",
            "tree_mature.svg",
            "forest_landscape.svg",
        ):
            path = ROOT / "assets" / "streak_forest" / asset
            self.assertTrue(path.exists(), asset)
            self.assertIn("<svg", path.read_text(encoding="utf-8"))

if __name__ == "__main__":
    unittest.main()
