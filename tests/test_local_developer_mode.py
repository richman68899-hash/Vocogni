"""Regression tests for the isolated, loopback-only developer workspace."""
from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import adaptive_learning
import persistence
from developer_mode import build_synthetic_learner_state


class LocalDeveloperPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.env_patch = patch.dict(
            os.environ,
            {"VOCogni_LOCAL_DEVELOPER_MODE": "true"},
        )
        self.env_patch.start()
        self.addCleanup(self.env_patch.stop)
        self.path_patch = patch.object(
            persistence,
            "LOCAL_DEVELOPER_DATA_DIR",
            Path(self.temp_dir.name),
        )
        self.path_patch.start()
        self.addCleanup(self.path_patch.stop)

    def test_local_mode_uses_a_synthetic_identity_without_auth0(self):
        self.assertTrue(persistence.local_developer_mode_enabled())
        self.assertTrue(persistence._is_logged_in())
        self.assertEqual(persistence.get_user_id(), "local-developer")

    def test_local_load_starts_empty_and_save_round_trips_json(self):
        self.assertEqual(
            persistence.load_progress_record(),
            {"progress": {}, "updated_at": None, "exists": False},
        )
        learner_state = {
            "profile": {"name": "Synthetic developer"},
            "progress": {"fractions": {"questions_attempted": 3}},
            "notes": [],
        }
        with patch.object(persistence, "get_supabase") as get_supabase:
            revision = persistence.save_progress(learner_state, record_exists=False)
            loaded = persistence.load_progress_record()

        get_supabase.assert_not_called()
        self.assertTrue(loaded["exists"])
        self.assertEqual(loaded["progress"], learner_state)
        self.assertEqual(loaded["updated_at"], revision)
        self.assertTrue(
            (Path(self.temp_dir.name) / "learner_progress.json").exists()
        )

    def test_local_save_detects_stale_revisions(self):
        first = persistence.save_progress({"version": 1}, record_exists=False)
        second = persistence.save_progress(
            {"version": 2},
            expected_updated_at=first,
            record_exists=True,
        )
        self.assertNotEqual(first, second)
        with self.assertRaises(persistence.ConcurrentProgressUpdateError):
            persistence.save_progress(
                {"version": 3},
                expected_updated_at=first,
                record_exists=True,
            )

    def test_supabase_is_explicitly_unavailable_in_local_mode(self):
        with self.assertRaisesRegex(RuntimeError, "Supabase is disabled"):
            persistence.get_supabase()


class SyntheticLearnerTests(unittest.TestCase):
    def test_synthetic_records_feed_the_real_adaptive_engine(self):
        sample = build_synthetic_learner_state()
        self.assertIn("Synthetic", sample["profile"]["description"])
        self.assertTrue(
            sample["settings"]["personalized_progress_recommendations"]
        )
        self.assertFalse(sample["settings"]["ai_share_learning_summary"])
        self.assertFalse(sample["settings"]["ai_share_recent_chat_history"])

        plan = adaptive_learning.build_learning_plan(sample["progress"])
        trajectories = adaptive_learning.build_skill_trajectories(sample["progress"])
        timeline = adaptive_learning.build_intervention_timeline(sample["progress"])

        self.assertGreaterEqual(trajectories["skills_with_comparable_windows"], 2)
        self.assertGreater(len(plan["actions"]), 0)
        self.assertGreater(len(timeline["events"]), 0)


if __name__ == "__main__":
    unittest.main()
