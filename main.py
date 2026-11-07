from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

from advanced_scraper.ai_summarizer import FindingsSummarizer
from advanced_scraper.report_builder import build_report, export_report
from advanced_scraper.sqlite_store import SQLiteStore


def _json_out(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False, default=str))


def _target_for(args: argparse.Namespace) -> str:
    return getattr(args, "url", None) or getattr(args, "domain", None) or "unknown"


def _run_scan(args: argparse.Namespace) -> Dict[str, Any]:
    if args.command == "scrape":
        from advanced_scraper.agents import ScrapingAgent
        schema = json.loads(args.schema)
        return ScrapingAgent(ai_provider=args.provider).quick_scrape(args.url, schema)
    if args.command in {"recon", "subdomains"}:
        from advanced_scraper.domain_recon import DomainRecon
        return DomainRecon(args.domain).run()
    if args.command == "api-scan":
        from advanced_scraper.api_inventory import APIInventory
        scanner = APIInventory(args.url)
        return {"url": args.url, "endpoints": scanner.scan_url(args.url)}
    if args.command == "fingerprint":
        from advanced_scraper.web_app_fingerprint import WebAppFingerprint
        return WebAppFingerprint().fingerprint(args.url)
    if args.command == "vuln":
        from advanced_scraper.vuln_enumerator import SafeVulnEnumerator
        return SafeVulnEnumerator().run(args.url)
    if args.command == "fuzz":
        from advanced_scraper.safe_fuzzer import SafeFuzzer
        wordlist = args.wordlist if args.wordlist is not None else SafeFuzzer.DEFAULT_PATHS
        return {"url": args.url, "results": SafeFuzzer(args.url, wordlist=wordlist, delay=args.delay).probe_paths()}
    raise ValueError(f"Unsupported scan command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Authorized API, web app, and domain reconnaissance toolkit")
    parser.add_argument("--db", default="data/recon.sqlite3", help="SQLite database path (default: data/recon.sqlite3)")
    sub = parser.add_subparsers(dest="command", required=True)

    scrape = sub.add_parser("scrape", help="Extract structured content from a URL")
    scrape.add_argument("url"); scrape.add_argument("--schema", default='{"data":"string"}'); scrape.add_argument("--provider", default="ollama")
    recon = sub.add_parser("recon", help="Passive domain and DNS inventory"); recon.add_argument("domain")
    subs = sub.add_parser("subdomains", help="Certificate-transparency subdomain discovery"); subs.add_argument("domain")
    for name, help_text in (("api-scan", "Find API references"), ("fingerprint", "Inspect app signals"), ("vuln", "Run safe HTTP configuration checks")):
        command = sub.add_parser(name, help=help_text); command.add_argument("url")
    fuzz = sub.add_parser("fuzz", help="Rate-limited GET-only path inventory")
    fuzz.add_argument("url"); fuzz.add_argument("--wordlist", nargs="*", default=None); fuzz.add_argument("--delay", type=float, default=0.5)

    report = sub.add_parser("report", help="Export a stored scan report")
    report.add_argument("--id", type=int, default=None, help="Scan ID (default: latest scan)")
    report.add_argument("--format", choices=("json", "markdown"), default="json")
    report.add_argument("--output", default=None, help="Output path; prints to stdout if omitted")
    report.add_argument("--summarize", action="store_true", help="Generate/update an optional AI summary")
    report.add_argument("--provider", default="auto", help="Summary provider: auto, ollama, or none")
    history = sub.add_parser("history", help="List saved scans"); history.add_argument("--limit", type=int, default=20)

    args = parser.parse_args(argv)
    try:
        store = SQLiteStore(args.db)
    except (OSError, ValueError) as exc:
        print(f"Storage warning: {exc}", file=sys.stderr)
        store = None

    try:
        if args.command == "history":
            _json_out(store.list_scans(max(1, args.limit)) if store else [])
            return 0
        if args.command == "report":
            scan = store.get_scan(args.id) if store else None
            if not scan:
                print("No saved scan found. Run a scan first or check --db.", file=sys.stderr)
                return 2
            if args.summarize:
                summary = FindingsSummarizer(provider=args.provider).summarize(scan)
                scan["summary"] = summary["summary"]
                if store and scan.get("id"):
                    store.update_summary(scan["id"], scan["summary"])
                if summary.get("warning"):
                    print(f"Summary fallback: {summary['warning']}", file=sys.stderr)
            payload = build_report(scan)
            if args.output:
                print(f"Report written to {export_report(payload, args.output, args.format)}")
            elif args.format == "markdown":
                from advanced_scraper.report_builder import to_markdown
                print(to_markdown(payload))
            else:
                _json_out(payload)
            return 0

        try:
            result = _run_scan(args)
            if not isinstance(result, dict):
                result = {"data": result}
        except (ValueError, json.JSONDecodeError) as exc:
            print(f"Invalid input: {exc}", file=sys.stderr)
            return 2
        except Exception as exc:
            result = {"error": {"type": type(exc).__name__, "message": str(exc)}}
            print(f"Scan failed gracefully: {type(exc).__name__}: {exc}", file=sys.stderr)
            scan_id = None
        else:
            scan_id = None
            if store:
                try:
                    scan_id = store.save_scan(args.command, _target_for(args), result)
                except (OSError, ValueError) as exc:
                    print(f"Storage warning: scan results were not persisted: {exc}", file=sys.stderr)

        output = {"scan_id": scan_id, "command": args.command, "target": _target_for(args), "result": result}
        _json_out(output)
        return 1 if "error" in result else 0
    except (OSError, ValueError) as exc:
        print(f"Operation failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
