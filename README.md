# Advanced AI-Ready Web Scraper & Recon Toolkit

A comprehensive suite of 20 modular tools for stealthy web scraping, automated account management, and OSINT-powered reconnaissance.

## Features

- **Stealth Engine:** Bypasses TLS/HTTP2 fingerprinting with `curl-cffi`.
- **AI Extraction:** Unified interface for **Ollama** and 15+ cloud providers (Groq, Anthropic, etc.).
- **Auth & Account Automation:** Automated logins and account creation via temp-emails.
- **Deep Recon:** Subdomain discovery, tech profiling, and lead extraction.
- **Enrichment:** Identity validation and threat intelligence via Shodan, Hunter.io, Censys, etc.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### 1. Quick Scrape with AI Extraction

```bash
python main.py scrape "https://example.com" --schema '{"title": "string"}'
```

### 2. Full Domain Reconnaissance

```bash
python main.py recon "example.com"
```

## Project Structure

- `advanced_scraper/`: Core package containing all 20 modules.
- `main.py`: Unified CLI entry point.
- `agents.py`: Agent layer for autonomous consumption.
