"""User-friendly, automation-first command line interface."""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import platform
import shutil
import sys
from pathlib import Path
from typing import Any

from advanced_scraper.ai_summarizer import FindingsSummarizer
from advanced_scraper.report_builder import build_report, export_report, to_markdown
from advanced_scraper.sqlite_store import SQLiteStore

LOG = logging.getLogger("piratecove.cli")
ACTIVE_COMMANDS = {"api-scan", "fingerprint", "vuln", "fuzz", "assess"}


def emit(data: Any, fmt: str = "json") -> str:
    if fmt == "markdown":
        return to_markdown(data if "report_version" in data else build_report(data))
    return json.dumps(data, indent=2, ensure_ascii=False, default=str)


def _get_target(args: argparse.Namespace) -> str:
    return str(getattr(args, "url", None) or getattr(args, "domain", None) or "unknown")


def _add_scan_output_options(command: argparse.ArgumentParser) -> None:
    command.add_argument("--authorized", action="store_true", help="Confirm this target is within your written authorization and scope")
    command.add_argument("--format", choices=("json", "markdown"), default="json", help="Output format (default: json)")
    command.add_argument("--output", help="Write output to a file instead of stdout")
    command.add_argument("--summarize", action="store_true", help="Add an optional LLM summary; offline fallback is used if unavailable")
    command.add_argument("--llm-provider", default="auto", help="Summary provider: auto, ollama, opencode, claude-code, or none")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="piratecove-recon",
        description="Authorized, read-only domain and web reconnaissance. Active HTTP commands require --authorized.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--version", action="version", version="PirateCove Recon 0.4.0")
    parser.add_argument("--db", default="data/recon.sqlite3", help="SQLite database path")
    parser.add_argument("--debug", action="store_true", help="Enable diagnostic logs on stderr")
    sub = parser.add_subparsers(dest="command", required=True)

    scrape = sub.add_parser("scrape", help="Extract structured content from a URL")
    scrape.add_argument("url")
    scrape.add_argument("--schema", default='{"data":"string"}', help="JSON object describing extraction fields")
    scrape.add_argument("--provider", default="ollama", help="Existing extraction provider")
    _add_scan_output_options(scrape)

    recon = sub.add_parser("recon", help="Passive DNS and certificate-transparency inventory")
    recon.add_argument("domain")
    _add_scan_output_options(recon)

    subdomains = sub.add_parser("subdomains", help="Passive certificate-transparency subdomain discovery")
    subdomains.add_argument("domain")
    _add_scan_output_options(subdomains)

    for name, description in (
        ("api-scan", "Find API references in a supplied page"),
        ("fingerprint", "Inspect basic web application signals"),
        ("vuln", "Check common HTTP security configuration indicators"),
    ):
        command = sub.add_parser(name, help=description)
        command.add_argument("url")
        _add_scan_output_options(command)

    fuzz = sub.add_parser("fuzz", help="Low-rate GET-only path inventory for an authorized target")
    fuzz.add_argument("url")
    fuzz.add_argument("--wordlist", help="Optional newline-delimited wordlist (maximum 200 entries)")
    fuzz.add_argument("--delay", type=float, default=0.75, help="Delay between requests; minimum 0.25 seconds")
    _add_scan_output_options(fuzz)

    assess = sub.add_parser("assess", help="Run independent read-only fingerprint, API, and HTTP configuration checks")
    assess.add_argument("url")
    _add_scan_output_options(assess)

    history = sub.add_parser("history", help="List saved scan records")
    history.add_argument("--limit", type=int, default=20)
    history.add_argument("--format", choices=("json", "markdown"), default="json")
    history.add_argument("--output")

    report = sub.add_parser("report", help="Export a saved scan by ID, or the latest scan")
    report.add_argument("--id", type=int, help="Scan ID; defaults to latest")
    report.add_argument("--format", choices=("json", "markdown"), default="json")
    report.add_argument("--output", help="Output filename; format can be inferred from extension")
    report.add_argument("--summarize", action="store_true")
    report.add_argument("--llm-provider", default="auto")

    doctor = sub.add_parser("doctor", help="Check local Python dependencies, tools, and database health without scanning targets")
    doctor.add_argument("--check-ollama", action="store_true", help="Optionally test the configured local Ollama endpoint")
    doctor.add_argument("--format", choices=("json", "markdown"), default="json")
    doctor.add_argument("--output")

    sub.add_parser("debug", help="Alias for doctor with detailed logging")
    sub.add_parser("providers", help="Show configured optional provider names without displaying secrets")
    return parser


def _run_scan(args: argparse.Namespace) -> dict[str, Any]:
    command = args.command
    if command == "scrape":
        try:
            schema = json.loads(args.schema)
        except json.JSONDecodeError as exc:
            raise ValueError(f"--schema must be valid JSON: {exc.msg}") from exc
        if not isinstance(schema, dict):
            raise ValueError("--schema must be a JSON object.")
        from advanced_scraper.agents import ScrapingAgent

        return ScrapingAgent(ai_provider=args.provider).quick_scrape(args.url, schema)

    if command in {"recon", "subdomains"}:
        from advanced_scraper.domain_recon import DomainRecon

        result = DomainRecon(args.domain).run()
        return result if command == "recon" else {"domain": args.domain, "subdomains": result.get("subdomains", []), "sources": result.get("sources", {})}

    if command == "api-scan":
        from advanced_scraper.api_inventory import APIInventory

        return {"url": args.url, "endpoints": APIInventory(args.url).scan_url(args.url)}

    if command == "fingerprint":
        from advanced_scraper.web_app_fingerprint import WebAppFingerprint

        return WebAppFingerprint().fingerprint(args.url)

    if command == "vuln":
        from advanced_scraper.vuln_enumerator import SafeVulnEnumerator

        return SafeVulnEnumerator().run(args.url)

    if command == "fuzz":
        from advanced_scraper.safe_fuzzer import SafeFuzzer

        if args.delay < 0.25:
            raise ValueError("--delay must be at least 0.25 seconds.")
        if args.wordlist:
            paths = [line.strip() for line in Path(args.wordlist).read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#")]
            if len(paths) > 200:
                raise ValueError("Wordlists are limited to 200 non-comment entries per run.")
        else:
            paths = SafeFuzzer.DEFAULT_PATHS
        return {"url": args.url, "results": SafeFuzzer(args.url, paths, args.delay).probe_paths()}

    if command == "assess":
        from advanced_scraper.api_inventory import APIInventory
        from advanced_scraper.vuln_enumerator import SafeVulnEnumerator
        from advanced_scraper.web_app_fingerprint import WebAppFingerprint

        stages = {
            "fingerprint": lambda: WebAppFingerprint().fingerprint(args.url),
            "api_inventory": lambda: {"endpoints": APIInventory(args.url).scan_url(args.url)},
            "http_configuration": lambda: SafeVulnEnumerator().run(args.url),
        }
        results: dict[str, Any] = {"url": args.url, "authorization_acknowledged": True, "stages": {}}
        for name, operation in stages.items():
            try:
                results["stages"][name] = operation()
            except Exception as exc:  # Keep successful stages when a peer fails.
                LOG.exception("Assessment stage %s failed", name)
                results["stages"][name] = {"error": {"type": type(exc).__name__, "message": str(exc)}}
        return results

    raise ValueError(f"Unsupported command: {command}")


def _doctor(args: argparse.Namespace) -> dict[str, Any]:
    modules = ("httpx", "dns", "pytest", "ruff")
    result: dict[str, Any] = {
        "python": {"version": platform.python_version(), "supported": sys.version_info >= (3, 10)},
        "modules": {name: importlib.util.find_spec(name) is not None for name in modules},
        "executables": {name: shutil.which(name) is not None for name in ("git", "docker", "ollama", "opencode", "claude")},
        "database": {"path": args.db, "healthy": False},
    }
    try:
        SQLiteStore(args.db).list_scans(1)
        result["database"]["healthy"] = True
    except Exception as exc:
        result["database"]["error"] = f"{type(exc).__name__}: {exc}"
    if args.check_ollama:
        import os
        import httpx

        endpoint = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/tags"
        try:
            response = httpx.get(endpoint, timeout=2.0)
            response.raise_for_status()
            result["ollama"] = {"reachable": True}
        except httpx.HTTPError as exc:
            result["ollama"] = {"reachable": False, "error": type(exc).__name__}
    return result


def _provider_status() -> dict[str, Any]:
    import os

    config_path = os.getenv("RECON_PROVIDER_CONFIG")
    if not config_path:
        return {"config": None, "providers": [], "note": "Set RECON_PROVIDER_CONFIG to a provider JSON file. Secrets are not displayed."}
    try:
        payload = json.loads(Path(config_path).expanduser().read_text(encoding="utf-8"))
        providers = payload.get("providers", {})
        return {"config": config_path, "default_provider": payload.get("default_provider"),
                "providers": [{"name": name, "type": value.get("type"), "enabled": value.get("enabled", True)}
                              for name, value in providers.items() if isinstance(value, dict)]}
    except (OSError, json.JSONDecodeError, AttributeError) as exc:
        return {"config": config_path, "error": f"{type(exc).__name__}: {exc}", "providers": []}


def _write_output(text: str, output: str | None) -> None:
    if output:
        destination = Path(output).expanduser()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text.rstrip() + "\n", encoding="utf-8")
        print(f"Wrote {destination}", file=sys.stderr)
    else:
        print(text)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if args.debug or args.command == "debug" else logging.WARNING,
                        format="%(levelname)s %(name)s: %(message)s", stream=sys.stderr)

    if args.command in {"doctor", "debug"}:
        doctor_args = args
        if args.command == "debug":
            doctor_args.check_ollama = False
            doctor_args.format = "json"
            doctor_args.output = None
        result = _doctor(doctor_args)
        _write_output(emit(result, getattr(args, "format", "json")), getattr(args, "output", None))
        return 0 if result["python"]["supported"] and result["database"]["healthy"] else 1

    if args.command == "providers":
        _write_output(emit(_provider_status()), None)
        return 0

    try:
        store = SQLiteStore(args.db)
    except Exception as exc:
        LOG.exception("SQLite database unavailable")
        store = None
        storage_warning = f"Database unavailable; scan results will not persist ({type(exc).__name__})."
    else:
        storage_warning = None

    try:
        if args.command == "history":
            if args.limit < 1 or args.limit > 1000:
                raise ValueError("--limit must be between 1 and 1000.")
            records = store.list_scans(args.limit) if store else []
            _write_output(emit({"scans": records, "storage_warning": storage_warning}, args.format), args.output)
            return 0

        if args.command == "report":
            scan = store.get_scan(args.id) if store else None
            if not scan:
                raise LookupError("No saved scan found. Run a scan first or check --db.")
            if args.summarize:
                summary = FindingsSummarizer(provider=args.llm_provider).summarize(scan)
                scan["summary"] = summary["summary"]
                if store and scan.get("id"):
                    store.update_summary(scan["id"], scan["summary"])
                if summary.get("warning"):
                    LOG.warning("Summary fallback: %s", summary["warning"])
            report = build_report(scan)
            text = emit(report, args.format)
            if args.output:
                export_report(report, args.output, args.format)
                print(f"Wrote {Path(args.output).expanduser()}", file=sys.stderr)
            else:
                print(text)
            return 0

        if args.command in ACTIVE_COMMANDS and not args.authorized:
            raise PermissionError(f"'{args.command}' can send requests to a target; rerun with --authorized only if you have permission and the target is in scope.")

        result = _run_scan(args)
        if not isinstance(result, dict):
            result = {"data": result}
        record = {"command": args.command, "target": _get_target(args), "result": result}
        scan_id = None
        if store:
            try:
                scan_id = store.save_scan(args.command, _get_target(args), result)
            except Exception as exc:
                LOG.exception("Could not save scan record")
                storage_warning = f"Results were returned but not persisted ({type(exc).__name__})."
        record["scan_id"] = scan_id
        if storage_warning:
            record["storage_warning"] = storage_warning
        if args.summarize:
            summary = FindingsSummarizer(provider=args.llm_provider).summarize(record)
            record["summary"] = summary["summary"]
            record["summary_provider"] = summary["provider"]
            if summary.get("warning"):
                record["summary_warning"] = summary["warning"]
            if scan_id and store:
                try:
                    store.update_summary(scan_id, record["summary"])
                except Exception:
                    LOG.exception("Could not persist summary")
        output = emit(record, args.format)
        _write_output(output, args.output)
        return 0
    except PermissionError as exc:
        print(f"Authorization required: {exc}", file=sys.stderr)
        return 2
    except LookupError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Invalid input: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted. No partial result was saved.", file=sys.stderr)
        return 130
    except Exception as exc:
        LOG.exception("Command failed")
        _write_output(emit({"command": args.command, "target": _get_target(args),
                            "error": {"type": type(exc).__name__, "message": str(exc)}}, "json"), None)
        return 1
