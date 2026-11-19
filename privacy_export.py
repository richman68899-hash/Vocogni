"""Build a transparent, scoped export of Vocogni's durable learner data."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


EXPORT_FORMAT = "vocogni.learner-data.v1"
EXPORT_SCOPE = (
    "This file contains the durable learner-state snapshot currently held in "
    "the authenticated Vocogni session. It may include unsaved session changes. "
    "It does not include identity-provider records, hosting or provider logs, "
    "provider backups, or session-only AI conversation history."
)


def build_privacy_export_json(
    learner_data: dict[str, Any],
    *,
    last_saved_at: str | None,
    includes_unsaved_changes: bool,
) -> str:
    """Serialize a learner-owned data snapshot without exporting auth secrets.

    The caller is responsible for confirming that the active session is
    authenticated and that the loaded learner state belongs to that identity.
    """
    if not isinstance(learner_data, dict):
        raise TypeError("Learner export data must be a dictionary.")

    document = {
        "format": EXPORT_FORMAT,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "last_successful_save_at": (
            last_saved_at if isinstance(last_saved_at, str) else None
        ),
        "includes_unsaved_changes": bool(includes_unsaved_changes),
        "scope": EXPORT_SCOPE,
        "learner_data": learner_data,
    }

    try:
        return json.dumps(
            document,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Vocogni could not safely serialize this learner-data snapshot."
        ) from exc
