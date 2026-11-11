"""Unit tests for Vocogni's LLM adapter and explainable pattern layer."""
import unittest
from unittest.mock import patch

from ai_prototype.engine import answer, analyze_learning_patterns
from ai_prototype.llm import (
    LLMError,
    MAX_PROVIDER_RESPONSE_BYTES,
    _RejectRedirectHandler,
    _chat_completions_url,
    chat_completion,
    is_configured,
    resolve_config,
)
from ai_prototype.patterns import detect_patterns
from vocogni_ai import _external_ai_tutoring_enabled, _learner_context


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

    def test_provider_failure_is_preserved_as_a_safe_diagnostic(self):
        config = {
            "base_url": "https://example.test/v1",
            "model": "example-model",
            "api_key": "do-not-leak-this",
        }
        with patch("ai_prototype.engine.chat_completion", side_effect=LLMError("HTTP 401 unauthorized")):
            result = answer("hello", llm_config=config)
        self.assertEqual(result["mode"], "fallback")
        self.assertEqual(result["fallback_reason"], "HTTP 401 unauthorized")
        self.assertNotIn("do-not-leak-this", result["fallback_reason"])

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


class ExternalAiOperatorGateTests(unittest.TestCase):
    def test_external_ai_is_disabled_by_default_even_with_provider_credentials(self):
        from types import SimpleNamespace
        secrets = {"llm": {
            "base_url": "https://example.test/v1",
            "model": "test-model",
            "api_key": "configured-secret",
        }}
        st = SimpleNamespace(secrets=secrets)
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(_external_ai_tutoring_enabled(st))

    def test_environment_flag_must_be_explicitly_truthy(self):
        from types import SimpleNamespace
        st = SimpleNamespace(secrets={})
        for value in ("", "false", "0", "no", "off", "enabled"):
            with self.subTest(value=value), patch.dict(
                "os.environ",
                {"VOCogni_ENABLE_EXTERNAL_AI_TUTORING": value},
                clear=True,
            ):
                self.assertFalse(_external_ai_tutoring_enabled(st))
        for value in ("true", "1", "yes", "on", " TRUE "):
            with self.subTest(value=value), patch.dict(
                "os.environ",
                {"VOCogni_ENABLE_EXTERNAL_AI_TUTORING": value},
                clear=True,
            ):
                self.assertTrue(_external_ai_tutoring_enabled(st))

    def test_streamlit_secret_overrides_environment_flag(self):
        from types import SimpleNamespace
        st = SimpleNamespace(secrets={
            "llm": {"enable_external_ai_tutoring": False}
        })
        with patch.dict(
            "os.environ",
            {"VOCogni_ENABLE_EXTERNAL_AI_TUTORING": "true"},
            clear=True,
        ):
            self.assertFalse(_external_ai_tutoring_enabled(st))

    def test_streamlit_secret_can_explicitly_enable_gate(self):
        from types import SimpleNamespace
        st = SimpleNamespace(secrets={
            "llm": {"enable_external_ai_tutoring": True}
        })
        with patch.dict("os.environ", {}, clear=True):
            self.assertTrue(_external_ai_tutoring_enabled(st))

    def test_unreadable_or_missing_secret_does_not_enable_gate(self):
        from types import SimpleNamespace

        class BrokenSecrets:
            def get(self, *_args, **_kwargs):
                raise RuntimeError("secrets unavailable")

        st = SimpleNamespace(secrets=BrokenSecrets())
        with patch.dict("os.environ", {}, clear=True):
            self.assertFalse(_external_ai_tutoring_enabled(st))


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


class ProviderTransportHardeningTests(unittest.TestCase):
    def test_remote_provider_requires_https(self):
        for endpoint in (
            "http://provider.example/v1",
            "http://192.0.2.10/v1",
            "http://example.test/v1",
        ):
            with self.subTest(endpoint=endpoint):
                with self.assertRaisesRegex(LLMError, "loopback"):
                    _chat_completions_url(endpoint)

    def test_local_loopback_http_is_allowed_for_development(self):
        self.assertEqual(
            _chat_completions_url("http://localhost:8080/v1"),
            "http://localhost:8080/v1/chat/completions",
        )
        self.assertEqual(
            _chat_completions_url("http://127.0.0.1:8080/v1"),
            "http://127.0.0.1:8080/v1/chat/completions",
        )
        self.assertEqual(
            _chat_completions_url("http://[::1]:8080/v1"),
            "http://[::1]:8080/v1/chat/completions",
        )

    def test_invalid_schemes_hosts_credentials_and_query_values_are_rejected(self):
        endpoints = (
            "file:///tmp/provider",
            "https:///missing-host",
            "https://user:password@provider.example/v1",
            "https://provider.example/v1?api_key=secret",
            "https://provider.example/v1#fragment",
            "https://provider.example:invalid/v1",
        )
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(LLMError):
                    _chat_completions_url(endpoint)

    def test_completion_path_is_not_duplicated(self):
        self.assertEqual(
            _chat_completions_url("https://provider.example/v1/chat/completions"),
            "https://provider.example/v1/chat/completions",
        )

    def test_redirect_handler_refuses_redirect_targets(self):
        from urllib.request import Request

        handler = _RejectRedirectHandler()
        request = Request("https://provider.example/v1/chat/completions", method="POST")
        redirected = handler.redirect_request(
            request,
            None,
            307,
            "Temporary Redirect",
            {},
            "https://other.example/collect",
        )
        self.assertIsNone(redirected)

    def test_provider_response_is_read_with_a_hard_size_limit(self):
        class FakeResponse:
            def __init__(self):
                self.read_limit = None

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, limit):
                self.read_limit = limit
                return b"x" * limit

        class FakeOpener:
            def __init__(self, response):
                self.response = response

            def open(self, _request, timeout):
                self.timeout = timeout
                return self.response

        response = FakeResponse()
        opener = FakeOpener(response)
        with patch("ai_prototype.llm.build_opener", return_value=opener):
            with self.assertRaisesRegex(LLMError, "1 MB size limit"):
                chat_completion(
                    [{"role": "user", "content": "Explain fractions."}],
                    config={
                        "base_url": "https://provider.example/v1",
                        "model": "test-model",
                        "api_key": "test-key",
                    },
                )
        self.assertEqual(response.read_limit, MAX_PROVIDER_RESPONSE_BYTES + 1)

    def test_valid_provider_response_is_parsed_and_sent_to_configured_https_host(self):
        import json

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self, _limit):
                return json.dumps({
                    "choices": [{"message": {"content": "  A fraction is part of a whole.  "}}]
                }).encode("utf-8")

        class FakeOpener:
            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return FakeResponse()

        opener = FakeOpener()
        with patch("ai_prototype.llm.build_opener", return_value=opener):
            result = chat_completion(
                [{"role": "user", "content": "Explain fractions."}],
                timeout=12,
                config={
                    "base_url": "https://provider.example/v1",
                    "model": "test-model",
                    "api_key": "test-key",
                },
            )

        self.assertEqual(result, "A fraction is part of a whole.")
        self.assertEqual(opener.request.full_url, "https://provider.example/v1/chat/completions")
        self.assertEqual(opener.request.get_header("Authorization"), "Bearer test-key")
        self.assertEqual(opener.timeout, 12)


if __name__ == "__main__":
    unittest.main()
