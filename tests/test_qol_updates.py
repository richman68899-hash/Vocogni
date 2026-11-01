"""Regression tests for five small learner-experience improvements."""
import unittest
from pathlib import Path
from unittest.mock import patch

from sections import browse


ROOT = Path(__file__).resolve().parents[1]


class BrowseFilterQolTests(unittest.TestCase):
    def setUp(self):
        self.courses = [
            {
                "id": "fractions",
                "title": "Fractions",
                "short_description": "Add and compare fractions",
                "category_label": "Mathematics",
                "subject_label": "Mathematics",
                "level": "Grade 7",
                "curriculum": "General",
                "difficulty": "Beginner",
                "category_id": "math",
                "subject_id": "mathematics",
            },
            {
                "id": "chemistry",
                "title": "Atomic Structure",
                "short_description": "Learn the atom",
                "category_label": "Science",
                "subject_label": "Chemistry",
                "level": "IGCSE",
                "curriculum": "Cambridge",
                "difficulty": "Intermediate",
                "category_id": "science",
                "subject_id": "chemistry",
            },
        ]

    def test_empty_filters_show_every_course(self):
        with patch("sections.browse._status_for_course", return_value="Not started"):
            result = browse._filter_courses(self.courses, {})
        self.assertEqual([course["id"] for course in result], ["fractions", "chemistry"])

    def test_search_is_case_insensitive_and_combines_with_other_filters(self):
        with patch(
            "sections.browse._status_for_course",
            side_effect=lambda course_id, _progress: (
                "In progress" if course_id == "chemistry" else "Not started"
            ),
        ):
            result = browse._filter_courses(
                self.courses,
                {},
                search="CAMBRIDGE",
                status_filter="In progress",
                difficulty_filter="Intermediate",
                category_filter="science",
                subject_filter="chemistry",
            )
        self.assertEqual([course["id"] for course in result], ["chemistry"])

    def test_non_matching_search_returns_no_courses(self):
        with patch("sections.browse._status_for_course", return_value="Not started"):
            result = browse._filter_courses(self.courses, {}, search="biology")
        self.assertEqual(result, [])

    def test_clear_filters_resets_all_five_controls_and_catalog_shows_count(self):
        source = (ROOT / "sections" / "browse.py").read_text(encoding="utf-8")
        for key in (
            "browse_search_input",
            "browse_status_filter",
            "browse_difficulty_filter",
            "browse_category_filter",
            "browse_subject_filter",
        ):
            self.assertIn(f'"{key}"', source)
        self.assertIn('key="browse_clear_filters"', source)
        self.assertIn('st.caption(f"Showing {len(filtered)} of {len(courses)} courses")', source)
        self.assertIn("st.session_state.browse_search = \"\"", source)


class NavigationQolTests(unittest.TestCase):
    def test_course_page_has_quick_action_for_the_next_diagnostic_or_lesson(self):
        source = (ROOT / "sections" / "course.py").read_text(encoding="utf-8")
        self.assertIn('key=f"course_quick_continue_{course_id}"', source)
        self.assertIn('"Start course-entry diagnostic"', source)
        self.assertIn('f"Continue to {quick_target.get(\'title\', \'next lesson\')}"', source)
        self.assertIn('flow["launch_mode"] = "course_diagnostic"', source)

    def test_progress_topic_can_open_that_course_in_learn(self):
        source = (ROOT / "sections" / "progress.py").read_text(encoding="utf-8")
        self.assertIn('f"Open {course[\'title\']} in Learn"', source)
        self.assertIn("st.session_state.current_course = course_id", source)
        self.assertIn('st.session_state.nav = "Browse"', source)
        self.assertIn("st.session_state.lesson_flow = None", source)


if __name__ == "__main__":
    unittest.main()
