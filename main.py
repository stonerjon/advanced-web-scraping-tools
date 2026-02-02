import sys
import argparse
import json
from advanced_scraper.agents import ScrapingAgent

def main():
    parser = argparse.ArgumentParser(description="Advanced AI-Ready Web Scraper & Recon Toolkit")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scrape command
    scrape_parser = subparsers.add_parser("scrape", help="Stealthy scrape and AI extraction")
    scrape_parser.add_argument("url", help="URL to scrape")
    scrape_parser.add_argument("--schema", help="JSON schema for extraction", default='{"data": "string"}')
    scrape_parser.add_argument("--provider", help="AI provider (ollama, groq, etc.)", default="ollama")

    # Recon command
    recon_parser = subparsers.add_parser("recon", help="Full domain reconnaissance")
    recon_parser.add_argument("domain", help="Domain to research")

    # Scan command (IOCs)
    scan_parser = subparsers.add_parser("scan", help="Scan for security IOCs")
    scan_parser.add_argument("url", help="URL to scan for indicators")

    args = parser.parse_args()

    agent = ScrapingAgent(ai_provider=args.provider if hasattr(args, 'provider') else "ollama")

    if args.command == "scrape":
        schema = json.loads(args.schema)
        print(f"[*] Scraping {args.url}...")
        result = agent.quick_scrape(args.url, schema)
        print(json.dumps(result, indent=2))

    elif args.command == "recon":
        print(f"[*] Starting full recon on {args.domain}...")
        result = agent.full_recon(args.domain)
        print(json.dumps(result, indent=2))

    elif args.command == "scan":
        print(f"[*] Scanning {args.url} for IOCs...")
        result = agent.scan_security(args.url)
        print(json.dumps(result, indent=2))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
