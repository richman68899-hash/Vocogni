"""OpenAI-compatible Chat Completions client using only the Python standard library."""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any


class LLMError(RuntimeError):
    """Raised when the optional model provider is unavailable or misconfigured."""


def resolve_config(config: dict[str, str] | None = None) -> dict[str, str]:
    """Resolve provider settings without ever storing credentials in source control."""
    supplied = config if isinstance(config, dict) else {}
    resolved = {
        "base_url": str(supplied.get("base_url") or os.getenv("VOCogni_LLM_BASE_URL", "")).strip().rstrip("/"),
        "model": str(supplied.get("model") or os.getenv("VOCogni_LLM_MODEL", "")).strip(),
        "api_key": str(supplied.get("api_key") or os.getenv("VOCogni_LLM_API_KEY", "")).strip(),
    }
    return resolved


def is_configured(config: dict[str, str] | None = None) -> bool:
    """Return whether all required provider settings are present."""
    resolved = resolve_config(config)
    return all(resolved.values())


def chat_completion(
    messages: list[dict[str, str]],
    *,
    timeout: int = 35,
    config: dict[str, str] | None = None,
) -> str:
    """Call a provider that implements the OpenAI-compatible chat-completions API."""
    resolved = resolve_config(config)
    endpoint = resolved["base_url"]
    model = resolved["model"]
    api_key = resolved["api_key"]
    if not endpoint or not model or not api_key:
        raise LLMError(
            "LLM is not configured. Set VOCogni_LLM_BASE_URL, "
            "VOCogni_LLM_MODEL, and VOCogni_LLM_API_KEY."
        )

    url = endpoint if endpoint.endswith("/chat/completions") else endpoint + "/chat/completions"
    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 800,
    }).encode("utf-8")
    request = Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(
                str(part.get("text", ""))
                for part in content
                if isinstance(part, dict)
            )
        if not isinstance(content, str) or not content.strip():
            raise LLMError("The model returned an empty response.")
        return content.strip()
    except LLMError:
        raise
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc
