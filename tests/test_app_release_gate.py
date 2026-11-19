"""Application wiring tests for the child-facing release gate."""
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AppReleaseGateWiringTests(unittest.TestCase):
    def test_release_gate_runs_before_authentication_or_learner_state_load(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        main = source.split("def main() -> None:", 1)[1]
        gate_index = main.index("release_gate.learner_access_block_reason(")
        auth_index = main.index("if not st.user.is_logged_in:")
        state_index = main.index("state.init_session_state()")
        load_index = main.index("_load_persistent_state_safely()")
        stop_index = main.index("st.stop()", gate_index)
        self.assertLess(gate_index, auth_index)
        self.assertLess(gate_index, state_index)
        self.assertLess(gate_index, load_index)
        self.assertLess(gate_index, stop_index)

    def test_block_screen_does_not_claim_legal_or_consent_clearance(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8").casefold()
        self.assertIn("not open to learners yet", source)
        self.assertIn("pre-launch safeguard", source)

    def test_login_screen_clearly_labels_the_private_prototype_preview(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        login = source.split("def _render_login() -> None:", 1)[1].split(
            "\ndef _render_logo", 1
        )[0].casefold()
        self.assertIn("vocogni is a prototype", login)
        self.assertIn("not open to general learners yet", login)
        self.assertIn("invited testers", login)
        self.assertIn("test accounts", login)
        self.assertIn("continue to prototype preview", login)

    def test_preview_gate_checks_oidc_subject_before_loading_learner_data(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        main = source.split("def main() -> None:", 1)[1]
        gate_index = main.index("release_gate.learner_access_block_reason(")
        subject_index = main.index("authenticated_subject_from_user(")
        state_index = main.index("state.init_session_state()")
        self.assertLess(subject_index, gate_index)
        self.assertLess(gate_index, state_index)
        self.assertIn('st.button("Sign out of this account"', main)

    def test_unknown_authentication_state_stops_before_gate_or_learner_loading(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        main = source.split("def main() -> None:", 1)[1]
        auth_check = main.index("is_logged_in = bool(st.user.is_logged_in)")
        auth_error = main.index("Vocogni could not verify your sign-in state")
        stop = main.index("st.stop()", auth_check)
        gate = main.index("release_gate.learner_access_block_reason(")
        state_init = main.index("state.init_session_state()")
        self.assertLess(auth_check, auth_error)
        self.assertLess(auth_error, stop)
        self.assertLess(stop, gate)
        self.assertLess(gate, state_init)

    def test_authenticated_subject_extraction_error_is_not_downgraded_to_anonymous(self):
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        main = source.split("def main() -> None:", 1)[1]
        identity_block = main.split("block_reason =", 1)[0]
        self.assertIn("authenticated_subject_from_user(", identity_block)
        self.assertNotIn("is_logged_in = False", identity_block)


if __name__ == "__main__":
    unittest.main()
