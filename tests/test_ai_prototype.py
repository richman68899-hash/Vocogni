"""Unit tests for the isolated experimental AI core."""
import unittest

from ai_prototype.engine import answer, analyze_learning_patterns
from ai_prototype.patterns import detect_patterns


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


class EngineTests(unittest.TestCase):
    def test_empty_question_returns_fallback(self):
        self.assertEqual(answer("  ", use_llm=False)["mode"], "fallback")

    def test_disabled_llm_returns_explainable_fallback(self):
        result = answer("Help me solve this equation", use_llm=False)
        self.assertEqual(result["mode"], "fallback")
        self.assertIn("structured approach", result["text"])

    def test_pattern_evidence_is_attached_to_answer(self):
        result = answer("How should I improve?", attempts=[
            {"correct": False, "response": "I forgot the minus sign."}
        ], use_llm=False)
        self.assertEqual(result["patterns"]["patterns"][0]["key"], "sign_error")
        self.assertIn("sign handling", result["text"].lower())


if __name__ == "__main__":
    unittest.main()
