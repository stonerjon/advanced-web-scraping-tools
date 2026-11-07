from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .agent_cli import AgentCLIConfig, AgentCLIProvider
from .base import TextProvider
from .ollama import OllamaProvider
from .openai_compatible import OpenAICompatibleProvider


class ProviderUnavailable(RuntimeError):
    """A configured provider could not be constructed."""


def load_provider_config(path: str, name: str | None = None) -> tuple[str, dict[str, Any]]:
    """Load a named provider from JSON config and return (name, settings)."""
    try:
        data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    except OSError as exc:
        raise ProviderUnavailable(f"Could not read provider config: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ProviderUnavailable(f"Invalid provider config JSON: {exc}") from exc
    if not isinstance(data, dict) or not isinstance(data.get("providers"), dict):
        raise ProviderUnavailable("Provider config must contain a 'providers' object.")
    selected = name or data.get("default_provider")
    if not isinstance(selected, str) or selected not in data["providers"]:
        raise ProviderUnavailable(f"Configured provider '{selected}' was not found.")
    entry = data["providers"][selected]
    if not isinstance(entry, dict):
        raise ProviderUnavailable(f"Provider entry '{selected}' must be an object.")
    return selected, entry


def create_provider(config: dict[str, Any]) -> TextProvider:
    """Build a provider adapter from an explicit configuration mapping."""
    kind = str(config.get("type", "ollama")).lower()
    timeout = float(config.get("timeout", 30))
    if timeout <= 0 or timeout > 600:
        raise ProviderUnavailable("Provider timeout must be greater than 0 and at most 600 seconds.")
    if kind == "ollama":
        return OllamaProvider(config.get("base_url", os.getenv("OLLAMA_URL", "http://localhost:11434")), timeout)
    if kind in {"openai-compatible", "cloudflare-workers-ai", "cloudflare-ai-gateway", "worker-gateway"}:
        url = config.get("chat_completions_url") or config.get("base_url")
        if not url:
            raise ProviderUnavailable(f"Provider '{kind}' requires chat_completions_url or base_url.")
        return OpenAICompatibleProvider(url, config.get("api_key_env"), timeout)
    if kind in {"opencode", "claude-code"}:
        return AgentCLIProvider(AgentCLIConfig(
            enabled=bool(config.get("enabled", False)), provider=kind,
            model=config.get("model"), timeout=timeout,
        ))
    raise ProviderUnavailable(f"Unknown provider type '{kind}'.")
