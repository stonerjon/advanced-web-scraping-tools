from __future__ import annotations

import json
from typing import Any

import httpx

from .base import TextProvider


class OllamaProvider:
    """Direct Ollama chat API adapter; local by default."""

    def __init__(self, base_url: str = "http://localhost:11434", timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(self, prompt: str, *, system: str, model: str) -> str:
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={"model": model, "stream": False, "messages": [
                {"role": "system", "content": system}, {"role": "user", "content": prompt}
            ]},
            timeout=self.timeout,
        )
        response.raise_for_status()
        data: dict[str, Any] = response.json()
        text = data.get("message", {}).get("content", "")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Ollama returned no text content.")
        return text.strip()
