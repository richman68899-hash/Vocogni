"""Tests for descriptive pre/post lesson checkpoint calculations."""
import unittest

import learning_measurement


class PostLessonCheckpointTests(unittest.TestCase):
    def test_transfer_checks_are_excluded_from_numerator_and_denominator(self):
        checkpoint = learning_measurement.build_post_lesson_checkpoint(
            {"score": 2, "total": 5, "percent": 40},
            [
                {"correct": True},
                {"correct": False},
                {"correct": True, "evidence_type": "independent_transfer"},
                {"correct": True},
            ],
            pathway="level_2",
            completed_at="2026-11-10T00:00:00+00:00",
        )
        self.assertEqual(checkpoint["post_correct"], 2)
        self.assertEqual(checkpoint["post_total"], 3)
        self.assertEqual(checkpoint["post_practice_percent"], 67)
        self.assertEqual(checkpoint["percentage_point_difference"], 27)
        self.assertEqual(checkpoint["completed_at"], "2026-11-10T00:00:00+00:00")

    def test_transfer_only_attempt_does_not_create_practice_checkpoint(self):
        checkpoint = learning_measurement.build_post_lesson_checkpoint(
            {"score": 5, "total": 5, "percent": 100},
            [{"correct": True, "evidence_type": "independent_transfer"}],
        )
        self.assertIsNone(checkpoint)

    def test_malformed_results_are_ignored_without_dividing_by_zero(self):
        checkpoint = learning_measurement.build_post_lesson_checkpoint(
            {"percent": 50},
            [None, {"correct": "yes"}, {"correct": True}],
        )
        self.assertEqual(checkpoint["post_correct"], 1)
        self.assertEqual(checkpoint["post_total"], 1)
        self.assertEqual(checkpoint["post_practice_percent"], 100)

    def test_missing_baseline_does_not_create_checkpoint(self):
        self.assertIsNone(
            learning_measurement.build_post_lesson_checkpoint(
                None, [{"correct": True}]
            )
        )


if __name__ == "__main__":
    unittest.main()
