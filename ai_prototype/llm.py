"""Small OpenAI-compatible chat-completions client using only the Python standard library."""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from typing import Any


class LLMError(RuntimeError):
    """Raised when the optional model provider is unavailable or misconfigured."""


def chat_completion(messages: list[dict[str, str]], *, timeout: int = 30) -> str:
    endpoint = os.getenv("VOCogni_LLM_BASE_URL", "").strip().rstrip("/")
    model = os.getenv("VOCogni_LLM_MODEL", "").strip()
    api_key = os.getenv("VOCogni_LLM_API_KEY", "").strip()
    if not endpoint or not model or not api_key:
        raise LLMError("LLM is not configured. Set VOCogni_LLM_BASE_URL, VOCogni_LLM_MODEL, and VOCogni_LLM_API_KEY.")
    url = endpoint if endpoint.endswith("/chat/completions") else endpoint + "/chat/completions"
    payload = json.dumps({"model": model, "messages": messages, "temperature": 0.3}).encode("utf-8")
    request = Request(url, data=payload, headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }, method="POST")
    try:
        with urlopen(request, timeout=timeout) as response:
            data: dict[str, Any] = json.loads(response.read().decode("utf-8"))
        content = data["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(str(part.get("text", "")) for part in content if isinstance(part, dict))
        if not isinstance(content, str) or not content.strip():
            raise LLMError("The model returned an empty response.")
        return content.strip()
    except (HTTPError, URLError, TimeoutError, KeyError, IndexError, TypeError, ValueError) as exc:
        raise LLMError(f"LLM request failed: {exc}") from exc
