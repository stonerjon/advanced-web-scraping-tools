# Optional provider integrations

The provider package separates inference/gateway adapters from the core recon modules. HTTP integrations use the core `httpx` dependency; they do not install vendor SDKs or require paid services.

## Optional install profiles

```bash
python -m pip install -e .                 # core + HTTP client
python -m pip install -e '.[dns]'          # passive DNS helpers
python -m pip install -e '.[scraping]'     # browser/parser integrations
python -m pip install -e '.[gateways]'     # reserved provider profile; uses core httpx
python -m pip install -e '.[agent-cli]'    # use installed OpenCode/Claude Code CLIs (no CLI is bundled)
python -m pip install -e '.[all,dev]'
```

Cloud provider account IDs, tokens, gateway names, models, and endpoint URLs are configuration, not baked-in defaults. Copy `config/providers.example.json`, replace placeholders with the current URLs from your Cloudflare/provider account docs, and keep secrets only in environment variables. Never commit tokens.

## Provider types

- `ollama`: local `/api/chat` inference, no paid API or external SDK.
- `cloudflare-workers-ai`: account-configured OpenAI-compatible chat-completions endpoint for the account's Workers AI offering.
- `cloudflare-ai-gateway`: account's configured AI Gateway compatibility endpoint. Routing/model syntax is provider/account specific; copy the current URL and model format from the official dashboard/docs.
- `worker-gateway`: an account-owned Cloudflare Worker or other service exposing a compatible chat-completions endpoint. This is a request hook only; it does not deploy or edit Workers.
- `openai-compatible`: any compatible paid or free gateway, configured with an environment-variable name for its secret.
- `opencode` / `claude-code`: optional external coding-agent CLIs. Disabled by default; enabling requires reviewing and restricting the installed CLI's own tools/permissions. These are not treated as inference APIs and their flags can evolve independently.

All providers implement `generate(prompt, system=..., model=...)`. Applications select a named provider from `providers` in the config, instantiate with `create_provider(entry)`, and gracefully fall back if unavailable. Avoid sending sensitive data to hosted providers unless policy permits.

Official docs to re-check before updating endpoint templates:
- Cloudflare Workers AI REST API: https://developers.cloudflare.com/workers-ai/get-started/rest-api/
- Cloudflare AI Gateway REST API: https://developers.cloudflare.com/ai-gateway/usage/rest-api/
- OpenCode providers/CLI: https://opencode.ai/docs/providers/ and https://opencode.ai/docs/cli/
- Claude Code CLI: https://code.claude.com/docs/en/cli-reference
- Ollama OpenCode integration: https://docs.ollama.com/integrations/opencode
