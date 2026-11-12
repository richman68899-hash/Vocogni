import unittest
from unittest.mock import patch

import intervention_tracking
import question_engine


class InterventionTrackingTests(unittest.TestCase):
    def test_record_is_idempotent_and_does_not_store_answer_content(self):
        progress = {}
        kwargs = {
            "course_id": "fractions",
            "lesson_id": "fractions_l1",
            "intervention_type": "hint",
            "event_id": "fractions:fractions_l1:1:hint:fractions_l1_q1",
            "skill_id": "math.number.fraction_representation",
            "question_id": "fractions_l1_q1",
            "attempt_number": 1,
            "occurred_at": "2026-10-30T09:00:00+00:00",
        }
        self.assertTrue(intervention_tracking.record_intervention(progress, **kwargs))
        self.assertFalse(intervention_tracking.record_intervention(progress, **kwargs))
        stored = progress["fractions"]["intervention_events"]
        self.assertEqual(len(stored), 1)
        self.assertNotIn("user_answer", stored[0])
        self.assertNotIn("prompt", stored[0])

    def test_invalid_support_type_and_missing_event_id_are_rejected(self):
        with self.assertRaises(ValueError):
            intervention_tracking.record_intervention(
                {}, course_id="fractions", lesson_id="fractions_l1",
                intervention_type="unknown", event_id="event-1",
            )
        with self.assertRaises(ValueError):
            intervention_tracking.record_intervention(
                {}, course_id="fractions", lesson_id="fractions_l1",
                intervention_type="hint", event_id="",
            )

    def test_report_links_only_later_verified_answers_for_same_skill(self):
        progress = {
            "fractions": {
                "intervention_events": [{
                    "event_id": "support-1",
                    "intervention_type": "hint",
                    "skill_id": "math.number.fraction_representation",
                    "lesson_id": "fractions_l1",
                    "occurred_at": "2026-10-30T09:00:00+00:00",
                }],
                "practice_attempts": {
                    "fractions_l1": [{
                        "results": [
                            {
                                "question_id": "fractions_l1_q1",
                                "skill_id": "math.number.fraction_representation",
                                "verification_status": "verified",
                                "correct": True,
                                "answered_at": "2026-10-30T09:10:00+00:00",
                            },
                            {
                                "question_id": "fractions_l1_q2",
                                "skill_id": "math.number.fraction_representation",
                                "verification_status": "verified",
                                "score": 0,
                                "max_marks": 1,
                                "answered_at": "2026-10-30T09:11:00+00:00",
                            },
                            {
                                "question_id": "not-registered",
                                "skill_id": "math.number.fraction_representation",
                                "verification_status": "verified",
                                "correct": False,
                                "answered_at": "2026-10-30T09:12:00+00:00",
                            },
                            {
                                "question_id": "fractions_l1_screen3",
                                "skill_id": "math.number.fraction_representation",
                                "verification_status": "verified",
                                "correct": False,
                                "answered_at": "2026-10-30T08:59:00+00:00",
                            },
                        ],
                    }]
                },
            }
        }
        report = intervention_tracking.build_intervention_report(progress)
        self.assertEqual(report["events_total"], 1)
        self.assertEqual(report["events"][0]["follow_up_answer_count"], 2)
        self.assertEqual(report["events"][0]["follow_up_accuracy_percent"], 50)

    def test_report_uses_saved_source_lesson_for_cross_lesson_practice(self):
        progress = {
            "fractions": {
                "intervention_events": [{
                    "event_id": "support-1",
                    "intervention_type": "worked_example",
                    "skill_id": "math.number.fraction_representation",
                    "lesson_id": "fractions_l1",
                    "occurred_at": "2026-10-30T09:00:00+00:00",
                }],
                "practice_attempts": {
                    # The attempt is stored under a later lesson, but this
                    # selected revision item originally belongs to lesson 1.
                    "fractions_l2": [{
                        "results": [{
                            "question_id": "fractions_l1_q1",
                            "skill_id": "math.number.fraction_representation",
                            "course_id": "fractions",
                            "lesson_id": "fractions_l1",
                            "verification_status": "verified",
                            "correct": True,
                            "answered_at": "2026-10-30T09:10:00+00:00",
                        }]
                    }]
                },
            }
        }
        with patch.object(
            question_engine,
            "attempt_metadata",
            return_value={
                "verification_status": "verified",
                "skill_id": "math.number.fraction_representation",
            },
        ) as resolve:
            report = intervention_tracking.build_intervention_report(progress)

        resolve.assert_called_once_with(
            "fractions_l1_q1",
            course_id="fractions",
            lesson_id="fractions_l1",
        )
        self.assertEqual(report["events"][0]["follow_up_answer_count"], 1)
        self.assertEqual(report["events"][0]["follow_up_accuracy_percent"], 100)

    def test_report_indexes_answer_history_once_for_multiple_events(self):
        progress = {
            "fractions": {
                "intervention_events": [
                    {
                        "event_id": f"support-{index}",
                        "intervention_type": "hint",
                        "skill_id": "math.number.fraction_representation",
                        "lesson_id": "fractions_l1",
                        "occurred_at": f"2026-10-30T09:{index:02d}:00+00:00",
                    }
                    for index in range(10)
                ],
                "practice_attempts": {
                    "fractions_l1": [{
                        "results": [{
                            "question_id": "fractions_l1_q1",
                            "skill_id": "math.number.fraction_representation",
                            "verification_status": "verified",
                            "correct": True,
                            "answered_at": "2026-10-30T10:00:00+00:00",
                        }]
                    }]
                },
            }
        }
        with patch.object(
            question_engine,
            "attempt_metadata",
            return_value={
                "verification_status": "verified",
                "skill_id": "math.number.fraction_representation",
            },
        ) as resolve:
            report = intervention_tracking.build_intervention_report(progress)
        self.assertEqual(resolve.call_count, 1)
        self.assertEqual(len(report["events"]), 10)
        self.assertTrue(
            all(event["follow_up_answer_count"] == 1 for event in report["events"])
        )

    def test_intervention_history_is_bounded(self):
        progress = {}
        for index in range(intervention_tracking.HISTORY_LIMIT + 20):
            intervention_tracking.record_intervention(
                progress,
                course_id="fractions",
                lesson_id="fractions_l1",
                intervention_type="hint",
                event_id=f"hint-{index}",
            )
        events = progress["fractions"]["intervention_events"]
        self.assertEqual(len(events), intervention_tracking.HISTORY_LIMIT)
        self.assertEqual(events[0]["event_id"], "hint-20")

    def test_report_does_not_mutate_legacy_progress(self):
        progress = {"fractions": {"practice_attempts": {}, "intervention_events": []}}
        before = repr(progress)
        intervention_tracking.build_intervention_report(progress)
        self.assertEqual(repr(progress), before)


if __name__ == "__main__":
    unittest.main()
