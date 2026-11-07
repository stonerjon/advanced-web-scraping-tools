# PirateCove Recon Toolkit

Modular Python toolkit for **authorized** passive domain inventory, API reference discovery, web application fingerprinting, safe HTTP configuration checks, and low-rate path inventory. It defaults to read-only behavior. Only assess systems you own or have explicit permission to test.

## Install only what you need

```bash
python -m pip install -e .                 # core CLI, reports, SQLite, HTTP provider adapters
python -m pip install -e '.[dns]'          # DNS record inventory
python -m pip install -e '.[scraping]'     # optional parsing/browser helpers
python -m pip install -e '.[agent-cli]'    # adapter only; install OpenCode/Claude Code separately
python -m pip install -e '.[all,dev]'      # everything plus lint/test tools
python main.py --help
```

Cloudflare, AI Gateway, and compatible gateway integrations are optional HTTP adapters and add no required vendor SDK. They do not deploy Workers or alter account settings. Account metadata hooks are read-only.

## Main workflow

```bash
python main.py doctor
python main.py recon example.org
python main.py api-scan https://example.org
python main.py fingerprint https://example.org
python main.py vuln https://example.org
python main.py fuzz https://example.org --delay 1.0
python main.py history --limit 20
python main.py report --format markdown --output reports/latest.md --summarize
```

The `assess URL --authorized` command requires an explicit authorization acknowledgement. Fuzzing uses a small fixed list and GET requests only. Scan history is stored in SQLite at `data/recon.sqlite3`; override with `--db PATH` before the command.

## LLM and gateways

Provider adapters are under `advanced_scraper/providers/`; named provider definitions live in `config/providers.example.json`; Cloudflare account checks are in `advanced_scraper/integrations/`; scanners, storage, and reporters have stable facades under `core/`, `storage/`, and `reporters/`. Historical module imports remain supported.

Supported optional providers: local Ollama; OpenAI-compatible endpoints; Cloudflare Workers AI/AI Gateway when configured with the current account endpoint; an account-owned Workers gateway; OpenCode and Claude Code CLI adapters. Select them in a JSON provider file and set `RECON_PROVIDER_CONFIG=/path/to/providers.json`. Keep tokens in environment variables named by `api_key_env`, never in the JSON file.

Ollama is a local inference endpoint. OpenCode and Claude Code are coding-agent CLIs, not plain inference APIs; they are disabled unless explicitly enabled in provider config. Before enabling, restrict each CLI's own permissions/tools and use isolated working directories. All provider errors fall back to a deterministic offline summary. Avoid sending confidential findings to hosted providers unless policy permits.

```bash
cp config/providers.example.json config/providers.local.json
# Edit model/account/gateway identifiers and set token environment variables.
RECON_PROVIDER_CONFIG=config/providers.local.json python main.py report --summarize
```

Check official docs before changing provider endpoints or CLI flags:
- [Cloudflare Workers AI REST API](https://developers.cloudflare.com/workers-ai/get-started/rest-api/)
- [Cloudflare AI Gateway REST API](https://developers.cloudflare.com/ai-gateway/usage/rest-api/)
- [OpenCode providers](https://opencode.ai/docs/providers/) and [CLI](https://opencode.ai/docs/cli/)
- [Ollama OpenCode integration](https://docs.ollama.com/integrations/opencode)
- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)

## Development quality checks

```bash
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
pytest -q
python -m compileall -q advanced_scraper main.py
```

`api-scan` extracts candidate REST/versioned, GraphQL, tRPC/RPC, OAuth/auth, OpenAPI/Swagger, AsyncAPI, and absolute URL references from source text. It does not probe discovered routes; same-host filtering is the default. Regex discovery has false positives and false negatives.

## Safety and operations

Use written scope, start with passive discovery, respect service rules, and manually verify all indicators. External feeds, DNS, Ollama, and gateways may be unavailable or rate-limited; individual provider failures should not discard other results. Database and report files can include internal URLs and hostnames; protect them and do not commit local secrets or outputs.
