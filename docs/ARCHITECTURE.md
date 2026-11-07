# Modular package map

- `advanced_scraper/core/`: public facades for passive discovery and safe checks. Historical root modules remain import-compatible.
- `advanced_scraper/providers/`: provider protocol, Ollama and OpenAI-compatible adapters, optional headless coding-agent adapters, and named-provider registry.
- `advanced_scraper/integrations/`: optional account-owned service integrations. Cloudflare account diagnostics are read-only; no Worker deployment or configuration writes are implemented.
- `advanced_scraper/storage/`: persistence interfaces (SQLite by default).
- `advanced_scraper/reporters/`: JSON and Markdown export facade.
- `advanced_scraper/cli/`: local diagnostics and command support.
- `config/`: placeholder-only sample config; secrets are read from environment variables.
- `docs/PROVIDERS.md`: provider configuration and official docs.

Optional install profiles are defined in `pyproject.toml`. The base install uses `httpx`; DNS, browser/scraping, and development dependencies are opt-in. Cloudflare and generic gateway adapters need no vendor SDK, only account-configured endpoints and environment secrets.

## Extension contract

Implement `TextProvider.generate(prompt, system=..., model=...)` for additional text providers. Keep network calls timeout-bounded, avoid logging secrets or prompts, return descriptive errors, and add offline-fallback tests. For new recon modules, use read-only methods, enforce scope/host boundaries, make external services opt-in, and add tests with mocked HTTP responses.
