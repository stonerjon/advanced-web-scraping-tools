from __future__ import annotations

import os
from typing import Any

from .agent_cli import AgentCLIConfig, AgentCLIProvider
from .base import TextProvider
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider


class ProviderUnavailable(RuntimeError):
    """A configured provider could not be constructed."""


def create_provider(config: dict[str, Any]) -> TextProvider:
    """Create one optional provider adapter from a provider config mapping.

    Supported types: ollama, openai-compatible, cloudflare-workers-ai,
    cloudflare-ai-gateway, worker-gateway, opencode, and claude-code.
    Cloud provider base URLs are explicit config values to track official API
    changes and support custom account-owned routes.
    """
    kind = str(config.get("type", "ollama")).lower()
    timeout = float(config.get("timeout", 30))
    if kind == "ollama":
        return OllamaProvider(config.get("base_url", os.getenv("OLLAMA_URL", "http://localhost:11434")), timeout)
    if kind in {"openai-compatible", "cloudflare-workers-ai", "cloudflare-ai-gateway", "worker-gateway"}:
        url = config.get("chat_completions_url") or config.get("base_url")
        if not url:
            raise ProviderUnavailable(f"Provider '{kind}' requires chat_completions_url or base_url.")
        # Cloudflare and user-hosted Worker routes are treated as compatible
        # only when the account owner configures a compatible endpoint.
        return OpenAICompatibleProvider(url, config.get("api_key_env"), timeout)
    if kind in {"opencode", "claude-code"}:
        return AgentCLIProvider(AgentCLIConfig(
            enabled=bool(config.get("enabled", False)),
            provider="opencode" if kind == "opencode" else "claude-code",
            model=config.get("model"), timeout=timeout,
        ))
    raise ProviderUnavailable(f"Unknown provider type '{kind}'.")
