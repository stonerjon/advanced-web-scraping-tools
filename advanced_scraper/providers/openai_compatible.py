from __future__ import annotations

import os
from typing import Any

import httpx

from .base import TextProvider


class OpenAICompatibleProvider:
    """Adapter for OpenAI-compatible services, including self-hosted gateways.

    Set the complete chat-completions URL in configuration. This avoids baking
    provider-specific paths into the package and supports account-owned Worker
    gateways and paid API gateways without SDK lock-in.
    """

    def __init__(self, base_url: str, api_key_env: str | None = None, timeout: float = 30.0):
        if not base_url.startswith(("https://", "http://")):
            raise ValueError("Provider base_url must be an absolute HTTP(S) URL.")
        self.base_url = base_url.rstrip("/")
        self.api_key_env = api_key_env
        self.timeout = timeout

    def generate(self, prompt: str, *, system: str, model: str) -> str:
        headers = {"Content-Type": "application/json"}
        if self.api_key_env:
            token = os.getenv(self.api_key_env)
            if not token:
                raise RuntimeError(f"Missing credential environment variable {self.api_key_env}.")
            headers["Authorization"] = f"Bearer {token}"
        payload: dict[str, Any] = {
            "model": model,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            "temperature": 0.2,
        }
        with httpx.Client(timeout=self.timeout, follow_redirects=False) as client:
            response = client.post(self.base_url, headers=headers, json=payload)
            response.raise_for_status()
            data = response.json()
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if isinstance(text, list):
            text = "".join(item.get("text", "") for item in text if isinstance(item, dict))
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Provider returned no text content.")
        return text.strip()
