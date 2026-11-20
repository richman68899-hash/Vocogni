"""Dedicated entry point for Vocogni's loopback-only developer workspace."""
from __future__ import annotations

import os

# These flags are set only by this entry point, not by the hosted app.py path.
os.environ["VOCogni_LOCAL_DEVELOPER_MODE"] = "true"
os.environ["VOCogni_DEVELOPER_SANDBOX"] = "true"

import app  # noqa: E402


if __name__ == "__main__":
    app.main()
