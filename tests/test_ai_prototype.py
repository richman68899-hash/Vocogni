"""Unit tests for Vocogni's LLM adapter and explainable pattern layer."""
import unittest
from unittest.mock import patch

from ai_prototype.engine import answer, analyze_learning_patterns
from ai_prototype.llm import is_configured, resolve_config
from ai_prototype.patterns import detect_patterns
from vocogni_ai import _learner_context


class PatternRecognitionTests(unittest.TestCase):
    def test_detects_sign_handling_signal(self):
        found = detect_patterns("I made a sign error and forgot the minus.")
        self.assertIn("sign_error", [item["key"] for item in found])

    def test_ignores_correct_attempts(self):
        report = analyze_learning_patterns([
            {"correct": True, "response": "I added denominators."},
            {"correct": False, "response": "I added denominators."},
        ])
        self.assertEqual(report["incorrect_attempts_inspected"], 1)
        self.assertEqual(report["patterns"][0]["key"], "fraction_denominator")

    def test_repeated_signal_is_counted_without_claiming_diagnosis(self):
        attempts = [{"correct": False, "response": "I forgot the minus sign."} for _ in range(3)]
        report = analyze_learning_patterns(attempts)
        self.assertEqual(report["patterns"][0]["evidence_count"], 3)
        self.assertEqual(report["patterns"][0]["signal"], "repeated signal")
        self.assertIn("not proof", report["interpretation"])

    def test_multiple_pattern_categories_can_be_found(self):
        found = detect_patterns("I added denominators and forgot to multiply every term.")
        keys = {item["key"] for item in found}
        self.assertIn("fraction_denominator", keys)
        self.assertIn("distribution", keys)


class ProviderConfigTests(unittest.TestCase):
    def test_config_can_be_supplied_without_environment_variables(self):
        config = {
            "base_url": "https://example.test/v1",
            "model": "example-model",
            "api_key": "test-key",
        }
        self.assertEqual(resolve_config(config), config)
        self.assertTrue(is_configured(config))

    def test_partial_provider_config_is_not_configured(self):
        self.assertFalse(is_configured({"base_url": "https://example.test/v1"}))


class EngineTests(unittest.TestCase):
    def test_empty_question_returns_fallback(self):
        self.assertEqual(answer("  ", use_llm=False)["mode"], "fallback")

    def test_disabled_llm_returns_explainable_fallback(self):
        result = answer("Help me solve this equation", use_llm=False)
        self.assertEqual(result["mode"], "fallback")
        self.assertIn("what is given", result["text"])

    def test_pattern_evidence_is_attached_to_answer(self):
        result = answer("How should I improve?", attempts=[
            {"correct": False, "response": "I forgot the minus sign."}
        ], use_llm=False)
        self.assertEqual(result["patterns"]["patterns"][0]["key"], "sign_error")
        self.assertIn("sign handling", result["text"].lower())

    @patch("ai_prototype.engine.chat_completion", return_value="Let's solve it step by step.")
    def test_llm_receives_limited_context_and_provider_config(self, mock_chat):
        config = {"base_url": "https://example.test/v1", "model": "test", "api_key": "secret"}
        result = answer(
            "Explain linear equations",
            history=[{"role": "user", "content": "I am practising algebra."}],
            learner_context="Grade: 8; preferred language: English.",
            llm_config=config,
        )
        self.assertEqual(result["mode"], "llm")
        self.assertEqual(result["text"], "Let's solve it step by step.")
        sent_messages = mock_chat.call_args.args[0]
        self.assertIn("Grade: 8", sent_messages[0]["content"])
        self.assertEqual(mock_chat.call_args.kwargs["config"], config)


class LearnerContextTests(unittest.TestCase):
    def test_context_excludes_identity_and_private_workspace(self):
        context = _learner_context(
            {
                "name": "Private Name",
                "email": "private@example.test",
                "grade": "8",
                "preferred_language": "English",
            },
            {},
        )
        self.assertIn("Grade level: 8", context)
        self.assertNotIn("Private Name", context)
        self.assertNotIn("private@example.test", context)
        self.assertNotIn("email", context.lower())


class ChatHistoryPrivacyTests(unittest.TestCase):
    def test_local_account_summaries_are_excluded_from_ai_history(self):
        from vocogni_ai import _recent_ai_history

        messages = [
            {"role": "user", "content": "summarise my profile"},
            {"role": "assistant", "content": "Private profile details", "mode": "local"},
            {"role": "user", "content": "Explain linear equations"},
            {"role": "assistant", "content": "An equation has two equal sides.", "mode": "llm"},
        ]
        history = _recent_ai_history(messages)
        self.assertEqual([item["content"] for item in history], [
            "Explain linear equations",
            "An equation has two equal sides.",
        ])
        self.assertNotIn("Private profile details", str(history))


if __name__ == "__main__":
    unittest.main()
