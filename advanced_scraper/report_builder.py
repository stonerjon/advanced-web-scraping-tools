from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


def build_report(scan: Dict[str, Any]) -> Dict[str, Any]:
    result = scan.get("result", scan)
    if not isinstance(result, dict):
        result = {"data": result}
    return {
        "report_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan": {key: scan.get(key) for key in ("id", "created_at", "command", "target") if key in scan},
        "summary": scan.get("summary") or "No AI summary generated.",
        "result": result,
    }


def to_markdown(report: Dict[str, Any]) -> str:
    scan = report.get("scan", {})
    lines = ["# Reconnaissance report", "", f"- **Target:** {scan.get('target', 'unknown')}",
             f"- **Command:** {scan.get('command', 'unknown')}", f"- **Created:** {scan.get('created_at', report.get('generated_at', 'unknown'))}", "",
             "## Summary", "", str(report.get("summary", "No summary available.")), "", "## Results", "",
             "```json", json.dumps(report.get("result", {}), indent=2, ensure_ascii=False, default=str), "```", ""]
    return "\n".join(lines)


def export_report(report: Dict[str, Any], output: str, format: str | None = None) -> str:
    destination = Path(output).expanduser()
    destination.parent.mkdir(parents=True, exist_ok=True)
    kind = (format or destination.suffix.lstrip(".") or "json").lower()
    if kind not in {"json", "md", "markdown"}:
        raise ValueError("Report format must be json or markdown.")
    content = json.dumps(report, indent=2, ensure_ascii=False, default=str) if kind == "json" else to_markdown(report)
    destination.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
    return str(destination)
