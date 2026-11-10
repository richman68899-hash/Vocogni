import unittest

import intervention_tracking


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

    def test_report_does_not_mutate_legacy_progress(self):
        progress = {"fractions": {"practice_attempts": {}, "intervention_events": []}}
        before = repr(progress)
        intervention_tracking.build_intervention_report(progress)
        self.assertEqual(repr(progress), before)


if __name__ == "__main__":
    unittest.main()
