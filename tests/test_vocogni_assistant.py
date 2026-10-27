"""Tests for the framework-free Vocogni Assistant request handler."""
import unittest

import data
from vocogni_assistant import answer_request, _recent_mistakes, render_assistant



class _FakeScope:
    """Minimal Streamlit context manager for testing assistant layout decisions."""

    def __init__(self, streamlit):
        self.streamlit = streamlit

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class _FakeSessionState(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError as exc:
            raise AttributeError(key) from exc

    def __setattr__(self, key, value):
        self[key] = value


class _FakeStreamlit:
    """Capture rendered button labels without needing a Streamlit server."""

    def __init__(self, messages):
        self.session_state = _FakeSessionState({
            "vocogni_assistant_open": True,
            "vocogni_assistant_messages": list(messages),
        })
        self.button_labels = []

    def markdown(self, *args, **kwargs):
        return None

    def caption(self, *args, **kwargs):
        return None

    def container(self, **kwargs):
        return _FakeScope(self)

    def columns(self, specification, **kwargs):
        return [_FakeScope(self) for _ in specification]

    def button(self, label, **kwargs):
        self.button_labels.append(label)
        return False

    def rerun(self):
        return None

    def chat_message(self, *args, **kwargs):
        return _FakeScope(self)

    def form(self, *args, **kwargs):
        return _FakeScope(self)

    def text_input(self, *args, **kwargs):
        return ""

    def form_submit_button(self, *args, **kwargs):
        return False


class VocogniAssistantTests(unittest.TestCase):
    def setUp(self):
        self.profile = {
            "name": "Ari",
            "grade": "Grade 10",
            "learning_goals": "Improve algebra",
            "favorite_subjects": ["Math", "Physics"],
            "weak_subjects": ["Chemistry"],
            "preferred_difficulty": "Adaptive",
            "preferred_language": "English",
        }
        self.progress = {
            course_id: {
                "started": False,
                "completed_lessons": [],
                "questions_attempted": 0,
                "correct_answers": 0,
                "mistakes": {},
                "diagnostics": {},
                "lesson_assessments": {},
                "practice_attempts": {},
                "lesson_screen_progress": {},
            }
            for course_id in data.COURSE_ORDER
        }


    def test_quick_prompts_remain_visible_after_conversation_starts(self):
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "How can I help?"},
        ]
        fake_st = _FakeStreamlit(messages)

        render_assistant(fake_st, self.profile, self.progress)

        self.assertTrue({
            "Summarise profile",
            "Latest mistakes",
            "My progress",
            "Next step",
        }.issubset(set(fake_st.button_labels)))

    def test_profile_summary_uses_only_recorded_profile_fields(self):
        reply, route = answer_request("Summarize my profile", self.profile, self.progress)
        self.assertIsNone(route)
        self.assertIn("Ari", reply)
        self.assertIn("Grade 10", reply)
        self.assertIn("Improve algebra", reply)
        self.assertIn("Chemistry", reply)
        self.assertNotIn("not provided", reply.casefold())

    def test_empty_profile_is_not_filled_with_inferences(self):
        reply, _ = answer_request("summarize my profile", {}, self.progress)
        self.assertIn("mostly blank", reply)
        self.assertIn("optional", reply)

    def test_latest_mistakes_are_sorted_by_attempt_timestamp(self):
        course_id = data.COURSE_ORDER[0]
        course = data.get_course(course_id)
        lesson_id = course["lessons"][0]["id"]
        self.progress[course_id]["practice_attempts"] = {
            lesson_id: [
                {
                    "completed_at": "2026-10-20T10:00:00+00:00",
                    "results": [{"correct": False, "skill_tag": "Older error"}],
                },
                {
                    "completed_at": "2026-10-26T09:30:00+00:00",
                    "results": [
                        {"correct": True, "skill_tag": "Correct answer"},
                        {"correct": False, "skill_tag": "Latest error"},
                    ],
                },
            ]
        }

        items = _recent_mistakes(self.progress)
        self.assertEqual(items[0]["label"], "Latest error")
        self.assertEqual(items[1]["label"], "Older error")

        reply, route = answer_request("show my latest mistakes", self.profile, self.progress)
        self.assertIsNone(route)
        self.assertLess(reply.index("Latest error"), reply.index("Older error"))
        self.assertIn("2026-10-26", reply)
        self.assertNotIn("Correct answer", reply)

    def test_aggregate_counters_are_not_mislabeled_as_recent(self):
        course_id = data.COURSE_ORDER[0]
        self.progress[course_id]["mistakes"] = {"Sign errors": 3}
        reply, _ = answer_request("show my latest mistakes", self.profile, self.progress)
        self.assertIn("can't reliably label these as the latest", reply)
        self.assertIn("Sign errors", reply)
        self.assertIn("3 recorded errors", reply)

    def test_no_mistakes_message_when_history_is_empty(self):
        reply, _ = answer_request("show my mistakes", self.profile, self.progress)
        self.assertIn("couldn't find any recorded", reply)

    def test_progress_summary_shows_saved_numbers_and_limits(self):
        course_id = data.COURSE_ORDER[0]
        self.progress[course_id].update({
            "started": True,
            "questions_attempted": 4,
            "correct_answers": 3,
        })
        reply, _ = answer_request("summarize my progress", self.profile, self.progress)
        self.assertIn("75%", reply)
        self.assertIn("4", reply)
        self.assertIn("not official grades", reply)

    def test_course_library_lists_published_courses(self):
        reply, _ = answer_request("list courses", self.profile, self.progress)
        for course in data.all_courses_in_order():
            self.assertIn(course["title"], reply)

    def test_navigation_is_explicit_and_returns_route(self):
        reply, route = answer_request("open progress page", self.profile, self.progress)
        self.assertEqual(route, "Progress")
        self.assertIn("Opening", reply)

    def test_help_lists_supported_requests(self):
        reply, route = answer_request("help", self.profile, self.progress)
        self.assertIsNone(route)
        self.assertIn("profile", reply.casefold())
        self.assertIn("mistake", reply.casefold())
        self.assertIn("next learning step", reply.casefold())

    def test_unsupported_subject_question_is_not_fabricated(self):
        reply, route = answer_request("Explain quantum mechanics", self.profile, self.progress)
        self.assertIsNone(route)
        self.assertIn("don't have a supported instruction", reply)
        self.assertIn("worked examples", reply)


if __name__ == "__main__":
    unittest.main()
