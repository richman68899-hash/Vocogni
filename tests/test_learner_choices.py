import unittest

from learner_choices import CHOICE_WIDGET_KEYS, choice_enabled
from settings_model import DEFAULT_SETTINGS


class LearnerChoiceTests(unittest.TestCase):
    def test_all_optional_data_use_choices_default_off(self):
        for key in CHOICE_WIDGET_KEYS:
            with self.subTest(key=key):
                self.assertIs(DEFAULT_SETTINGS[key], False)

    def test_only_explicit_true_enables_a_choice(self):
        for key in CHOICE_WIDGET_KEYS:
            with self.subTest(key=key):
                self.assertTrue(choice_enabled({key: True}, key))
                self.assertFalse(choice_enabled({key: False}, key))
                self.assertFalse(choice_enabled({key: "true"}, key))
                self.assertFalse(choice_enabled({}, key))
                self.assertFalse(choice_enabled(None, key))

    def test_unknown_choice_never_enables(self):
        self.assertFalse(choice_enabled({"unexpected": True}, "unexpected"))

    def test_core_account_storage_is_not_misrepresented_as_optional(self):
        self.assertNotIn("save_learning_progress", CHOICE_WIDGET_KEYS)
        self.assertNotIn("store_account_data", CHOICE_WIDGET_KEYS)


    def test_developer_sandbox_is_explicit_and_fail_closed(self):
        from learner_choices import developer_sandbox_enabled, DEVELOPER_SANDBOX_ENV
        self.assertFalse(developer_sandbox_enabled({}))
        self.assertFalse(developer_sandbox_enabled({DEVELOPER_SANDBOX_ENV: "false"}))
        self.assertFalse(developer_sandbox_enabled({DEVELOPER_SANDBOX_ENV: "dev"}))
        self.assertTrue(developer_sandbox_enabled({DEVELOPER_SANDBOX_ENV: "true"}))
        self.assertTrue(developer_sandbox_enabled({DEVELOPER_SANDBOX_ENV: "1"}))


if __name__ == "__main__":
    unittest.main()
