"""OpenAI-compatible Chat Completions client using only the Python standard library."""
from __future__ import annotations

import ipaddress
import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class LLMError(RuntimeError):
    """Raised when the optional model provider is unavailable or misconfigured."""


MAX_PROVIDER_RESPONSE_BYTES = 1_000_000


class _RejectRedirectHandler(HTTPRedirectHandler):
    """Do not forward an authenticated learner request to a redirect target."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _chat_completions_url(endpoint: str) -> str:
    """Validate the operator-configured endpoint and return its completion URL.

    Remote providers must use HTTPS so the bearer token is not sent in cleartext.
    Plain HTTP is reserved for local development on loopback addresses.
    """
    try:
        parts = urlsplit(endpoint)
        hostname = parts.hostname
        # Accessing .port also validates malformed port declarations.
        _ = parts.port
    except ValueError as exc:
        raise LLMError("The configured AI provider URL is invalid.") from exc

    if parts.scheme not in {"https", "http"} or not hostname:
        raise LLMError("The AI provider URL must use HTTPS and include a valid host.")
    if parts.username is not None or parts.password is not None:
        raise LLMError("The AI provider URL must not contain embedded credentials.")
    if parts.query or parts.fragment:
        raise LLMError("The AI provider URL must not contain a query string or fragment.")

    if parts.scheme == "http":
        normalized_host = hostname.casefold().rstrip(".")
        is_loopback = normalized_host == "localhost"
        if not is_loopback:
            try:
                is_loopback = ipaddress.ip_address(normalized_host).is_loopback
            except ValueError:
                is_loopback = False
        if not is_loopback:
            raise LLMError("Plain HTTP is allowed only for a local loopback AI provider.")

    path = parts.path.rstrip("/")
    if not path.endswith("/chat/completions"):
        path += "/chat/completions"
    return urlunsplit((parts.scheme, parts.netloc, path, "", ""))


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
    """Return whether required settings and a supported endpoint are present."""
    resolved = resolve_config(config)
    if not all(resolved.values()):
        return False
    try:
        _chat_completions_url(resolved["base_url"])
    except LLMError:
        return False
    return True


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

    url = _chat_completions_url(endpoint)
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
        # Reject redirects: a configured endpoint must receive the request
        # directly, rather than forwarding the Authorization header elsewhere.
        opener = build_opener(_RejectRedirectHandler())
        with opener.open(request, timeout=timeout) as response:
            response_body = response.read(MAX_PROVIDER_RESPONSE_BYTES + 1)
        if len(response_body) > MAX_PROVIDER_RESPONSE_BYTES:
            raise LLMError("The AI provider response exceeded the 1 MB size limit.")
        data: dict[str, Any] = json.loads(response_body.decode("utf-8"))
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
