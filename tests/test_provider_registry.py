from advanced_scraper.providers.agent_cli import AgentCLIConfig, AgentCLIProvider
from advanced_scraper.providers.registry import create_provider


def test_openai_compatible_provider_requires_endpoint():
    try:
        create_provider({"type": "worker-gateway"})
    except ValueError:
        pass
    else:
        raise AssertionError("Gateway should require an explicit endpoint")


def test_agent_cli_disabled_by_default():
    adapter = AgentCLIProvider(AgentCLIConfig(provider="opencode"))
    try:
        adapter.generate("prompt", system="system", model="model")
    except PermissionError:
        pass
    else:
        raise AssertionError("Agent CLI must be opt-in")
