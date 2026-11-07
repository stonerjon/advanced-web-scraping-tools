from __future__ import annotations

from typing import Protocol


class TextProvider(Protocol):
    """Minimal contract shared by optional text-generation adapters."""

    def generate(self, prompt: str, *, system: str, model: str) -> str: ...
