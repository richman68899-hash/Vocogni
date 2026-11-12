"""Regression tests for learner identity and persistence lifecycle safeguards."""
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import app
import persistence
import state


class FakeSessionState(dict):
    """Small dict-backed stand-in for Streamlit's session-state proxy."""

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    def __setattr__(self, name, value):
        self[name] = value


class FakeQuery:
    def __init__(self, rows=None, error=None):
        self.rows = [] if rows is None else rows
        self.error = error
        self.filters = []
        self.selected = None
        self.limit_value = None
        self.upsert_payload = None
        self.update_payload = None
        self.insert_payload = None
        self.conflict_target = None

    def select(self, columns):
        self.selected = columns
        return self

    def eq(self, column, value):
        self.filters.append((column, value))
        return self

    def limit(self, value):
        self.limit_value = value
        return self

    def upsert(self, payload, on_conflict=None):
        self.upsert_payload = payload
        self.conflict_target = on_conflict
        return self

    def update(self, payload):
        self.update_payload = payload
        return self

    def insert(self, payload):
        self.insert_payload = payload
        return self

    def is_(self, column, value):
        self.filters.append((column, f"is:{value}"))
        return self

    def execute(self):
        if self.error is not None:
            raise self.error
        return SimpleNamespace(data=self.rows)


class FakeClient:
    def __init__(self, query):
        self.query = query
        self.table_name = None

    def table(self, name):
        self.table_name = name
        return self.query


class PersistenceIdentityTests(unittest.TestCase):
    def test_user_id_comes_from_authenticated_oidc_subject_not_email(self):
        with (
            patch.object(persistence, "_is_logged_in", return_value=True),
            patch.object(
                persistence,
                "_get_user_claims",
                return_value={"sub": "auth0|learner-a", "email": "a@example.test"},
            ),
        ):
            self.assertEqual(persistence.get_user_id(), "auth0|learner-a")

    def test_user_id_rejects_unauthenticated_session(self):
        with patch.object(persistence, "_is_logged_in", return_value=False):
            with self.assertRaisesRegex(RuntimeError, "No authenticated"):
                persistence.get_user_id()

    def test_user_id_rejects_missing_oidc_subject(self):
        with (
            patch.object(persistence, "_is_logged_in", return_value=True),
            patch.object(persistence, "_get_user_claims", return_value={"email": "a@example.test"}),
        ):
            with self.assertRaisesRegex(RuntimeError, "no OIDC 'sub'"):
                persistence.get_user_id()


class SupabasePersistenceTests(unittest.TestCase):
    def test_load_is_scoped_to_authenticated_subject(self):
        query = FakeQuery(rows=[{"progress": {"profile": {"name": "Learner A"}}}])
        client = FakeClient(query)

        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=client),
        ):
            result = persistence.load_progress()

        self.assertEqual(result, {"profile": {"name": "Learner A"}})
        self.assertEqual(client.table_name, persistence.TABLE_NAME)
        self.assertIn(("user_id", "auth0|learner-a"), query.filters)
        self.assertEqual(query.limit_value, 1)

    def test_load_returns_empty_state_when_no_row_exists(self):
        query = FakeQuery(rows=[])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            self.assertEqual(persistence.load_progress(), {})

    def test_load_progress_record_reports_missing_row(self):
        query = FakeQuery(rows=[])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            self.assertEqual(
                persistence.load_progress_record(),
                {"progress": {}, "updated_at": None, "exists": False},
            )

    def test_load_rejects_non_object_progress(self):
        query = FakeQuery(rows=[{"progress": ["unexpected"]}])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            with self.assertRaisesRegex(RuntimeError, "must be a JSON object"):
                persistence.load_progress()

    def test_save_updates_only_when_loaded_revision_matches(self):
        revision = "2026-11-09T00:00:00+00:00"
        query = FakeQuery(rows=[{"user_id": "auth0|learner-a", "updated_at": "2026-11-09T00:01:00+00:00"}])
        client = FakeClient(query)
        learner_state = {"profile": {"name": "Learner A"}}

        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=client),
        ):
            new_revision = persistence.save_progress(
                learner_state, expected_updated_at=revision, record_exists=True
            )

        self.assertEqual(client.table_name, persistence.TABLE_NAME)
        self.assertEqual(query.filters, [("user_id", "auth0|learner-a"), ("updated_at", revision)])
        self.assertEqual(query.update_payload["user_id"], "auth0|learner-a")
        self.assertEqual(query.update_payload["progress"], learner_state)
        self.assertTrue(query.update_payload["updated_at"])
        self.assertEqual(query.selected, "user_id, updated_at")
        self.assertEqual(new_revision, "2026-11-09T00:01:00+00:00")

    def test_first_save_uses_insert_instead_of_upsert(self):
        query = FakeQuery(rows=[{"user_id": "auth0|learner-a", "updated_at": "2026-11-09T00:01:00+00:00"}])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            persistence.save_progress({"profile": {}}, record_exists=False)
        self.assertIsNotNone(query.insert_payload)
        self.assertIsNone(query.upsert_payload)

    def test_stale_conditional_update_is_reported_as_a_conflict(self):
        query = FakeQuery(rows=[])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            with self.assertRaises(persistence.ConcurrentProgressUpdateError):
                persistence.save_progress(
                    {"profile": {}},
                    expected_updated_at="stale-revision",
                    record_exists=True,
                )

    def test_load_returns_progress_and_revision(self):
        revision = "2026-11-09T00:00:00+00:00"
        query = FakeQuery(rows=[{"progress": {"profile": {}}, "updated_at": revision}])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            record = persistence.load_progress_record()
        self.assertEqual(record, {"progress": {"profile": {}}, "updated_at": revision, "exists": True})
        self.assertEqual(query.selected, "progress, updated_at")

    def test_save_rejects_a_response_for_another_user(self):
        query = FakeQuery(rows=[{"user_id": "auth0|learner-b"}])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            with self.assertRaisesRegex(RuntimeError, "different identity"):
                persistence.save_progress({"profile": {}})

    def test_save_rejects_unverified_empty_upsert_response(self):
        query = FakeQuery(rows=[])
        with (
            patch.object(persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(persistence, "get_supabase", return_value=FakeClient(query)),
        ):
            with self.assertRaisesRegex(RuntimeError, "write could not be verified"):
                persistence.save_progress({"profile": {}})

    def test_save_rejects_non_dictionary_state_before_database_access(self):
        with patch.object(persistence, "get_supabase") as get_supabase:
            with self.assertRaises(TypeError):
                persistence.save_progress(["not", "a", "dictionary"])
        get_supabase.assert_not_called()


class SessionIdentityBoundaryTests(unittest.TestCase):
    def test_same_identity_does_not_reload_or_reset_session(self):
        session = FakeSessionState(
            {
                "_persistent_state_loaded": True,
                "_persistent_user_id": "auth0|learner-a",
                "profile": {"name": "Learner A"},
                "custom_state": "keep",
            }
        )

        with (
            patch.object(state.st, "session_state", session),
            patch.object(state.persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(state.persistence, "load_progress_record") as load_progress,
        ):
            state.load_saved_learner_state()

        load_progress.assert_not_called()
        self.assertEqual(session["profile"]["name"], "Learner A")
        self.assertEqual(session["custom_state"], "keep")

    def test_account_switch_clears_previous_learner_data_before_loading_new_user(self):
        session = FakeSessionState(
            {
                "_persistent_state_loaded": True,
                "_persistent_user_id": "auth0|learner-a",
                "_persistent_dirty": False,
                "profile": {"name": "Learner A"},
                "progress": {"private-course": {"secret": "A-only"}},
                "notes": [{"id": 1, "title": "A-only note"}],
                "assistant_history": [{"content": "A-only conversation"}],
            }
        )
        learner_b_data = {
            "profile": {"name": "Learner B"},
            "progress": {},
            "notes": [{"id": 2, "title": "B-only note"}],
            "settings": {"appearance": "Dark"},
        }

        with (
            patch.object(state.st, "session_state", session),
            patch.object(state.persistence, "get_user_id", return_value="auth0|learner-b"),
            patch.object(state.persistence, "load_progress_record", return_value={
                "progress": learner_b_data, "updated_at": "2026-11-12T09:00:00+00:00", "exists": True,
            }) as load_progress,
        ):
            state.load_saved_learner_state()

        load_progress.assert_called_once()
        self.assertEqual(session["_persistent_user_id"], "auth0|learner-b")
        self.assertEqual(session["profile"]["name"], "Learner B")
        self.assertEqual(
            session["notes"],
            [{"id": 2, "title": "B-only note", "folder_id": None}],
        )
        self.assertEqual(session["settings"]["appearance"], "Dark")
        self.assertNotIn("assistant_history", session)
        self.assertNotIn("A-only", repr(session))


    def test_failed_conflict_reload_preserves_local_session(self):
        session = FakeSessionState({
            "_persistent_state_loaded": True,
            "_persistent_user_id": "auth0|learner-a",
            "_persistent_dirty": True,
            "_persistent_conflict": True,
            "profile": {"name": "Local unsaved edit"},
            "notes": [{"id": 1, "title": "Unsaved note"}],
        })
        with (
            patch.object(state.st, "session_state", session),
            patch.object(state.persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(
                state.persistence,
                "load_progress_record",
                side_effect=RuntimeError("temporary database outage"),
            ),
        ):
            with self.assertRaisesRegex(RuntimeError, "temporary database outage"):
                state.load_saved_learner_state(force_reload=True)

        self.assertEqual(session["profile"]["name"], "Local unsaved edit")
        self.assertEqual(session["notes"], [{"id": 1, "title": "Unsaved note"}])
        self.assertTrue(session["_persistent_dirty"])
        self.assertTrue(session["_persistent_conflict"])

    def test_successful_conflict_reload_replaces_local_state_and_clears_conflict(self):
        session = FakeSessionState({
            "_persistent_state_loaded": True,
            "_persistent_user_id": "auth0|learner-a",
            "_persistent_dirty": True,
            "_persistent_conflict": True,
            "profile": {"name": "Local unsaved edit"},
            "notes": [{"id": 1, "title": "Unsaved note"}],
        })
        saved = {
            "profile": {"name": "Latest saved profile"},
            "progress": {},
            "notes": [{"id": 2, "title": "Latest saved note"}],
            "settings": {},
        }
        with (
            patch.object(state.st, "session_state", session),
            patch.object(state.persistence, "get_user_id", return_value="auth0|learner-a"),
            patch.object(
                state.persistence,
                "load_progress_record",
                return_value={
                    "progress": saved,
                    "updated_at": "2026-11-12T10:00:00+00:00",
                    "exists": True,
                },
            ),
        ):
            state.load_saved_learner_state(force_reload=True)

        self.assertEqual(session["profile"]["name"], "Latest saved profile")
        self.assertEqual(session["notes"], [{"id": 2, "title": "Latest saved note", "folder_id": None}])
        self.assertFalse(session["_persistent_dirty"])
        self.assertFalse(session["_persistent_conflict"])
        self.assertEqual(session["_persistent_updated_at"], "2026-11-12T10:00:00+00:00")


class StartupLoadFailureTests(unittest.TestCase):
    def test_load_failure_stops_before_showing_or_saving_empty_workspace(self):
        with (
            patch.object(app, "_load_persistent_state", side_effect=RuntimeError("database unavailable")),
            patch.object(app.st, "error") as show_error,
            patch.object(app.st, "caption") as show_caption,
            patch.object(app.st, "button", return_value=False) as button,
            patch.object(app.st, "stop") as stop,
        ):
            result = app._load_persistent_state_safely()

        self.assertFalse(result)
        show_error.assert_called_once()
        show_caption.assert_called_once()
        button.assert_called_once_with(
            "Retry loading saved learning data",
            key="retry_persistent_state_load",
            type="primary",
        )
        stop.assert_called_once()
        self.assertNotIn("database unavailable", show_error.call_args.args[0])

    def test_load_retry_reruns_but_never_marks_defaults_as_loaded(self):
        with (
            patch.object(app, "_load_persistent_state", side_effect=RuntimeError("temporary outage")),
            patch.object(app.st, "error"),
            patch.object(app.st, "caption"),
            patch.object(app.st, "button", return_value=True),
            patch.object(app.st, "rerun") as rerun,
            patch.object(app.st, "stop") as stop,
        ):
            result = app._load_persistent_state_safely()

        self.assertFalse(result)
        rerun.assert_called_once()
        stop.assert_called_once()

    def test_successful_load_allows_application_to_continue(self):
        with patch.object(app, "_load_persistent_state") as load:
            result = app._load_persistent_state_safely()
        self.assertTrue(result)
        load.assert_called_once()


class LogoutPersistenceTests(unittest.TestCase):
    def test_logout_stays_signed_in_when_forced_save_fails(self):
        with (
            patch("app.st.sidebar.button", return_value=True),
            patch.object(app.state, "mark_persistent_dirty") as mark_dirty,
            patch.object(app.state, "flush_persistent_save", return_value=False) as flush,
            patch.object(app.st, "error") as show_error,
            patch.object(app.st, "logout") as logout,
        ):
            app._render_logout()

        mark_dirty.assert_called_once()
        flush.assert_called_once()
        show_error.assert_called_once()
        logout.assert_not_called()

    def test_logout_occurs_only_after_successful_forced_save(self):
        with (
            patch("app.st.sidebar.button", return_value=True),
            patch.object(app.state, "mark_persistent_dirty") as mark_dirty,
            patch.object(app.state, "flush_persistent_save", return_value=True) as flush,
            patch.object(app.st, "logout") as logout,
        ):
            app._render_logout()

        mark_dirty.assert_called_once()
        flush.assert_called_once()
        logout.assert_called_once()

    def test_no_logout_action_does_not_force_a_save(self):
        with (
            patch("app.st.sidebar.button", return_value=False),
            patch.object(app.state, "mark_persistent_dirty") as mark_dirty,
            patch.object(app.state, "flush_persistent_save") as flush,
            patch.object(app.st, "logout") as logout,
        ):
            app._render_logout()

        mark_dirty.assert_not_called()
        flush.assert_not_called()
        logout.assert_not_called()


if __name__ == "__main__":
    unittest.main()
