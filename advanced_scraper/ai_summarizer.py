from __future__ import annotations

import os
import urllib.error
import urllib.request
from typing import Any, Dict


class FindingsSummarizer:
    """Optional LLM summaries with deterministic offline fallback. Uses Ollama by default."""

    def __init__(self, provider: str = "auto", model: str | None = None, timeout: float = 20.0):
        self.provider = provider.lower()
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2")
        self.timeout = timeout

    @staticmethod
    def fallback(scan: Dict[str, Any]) -> str:
        result = scan.get("result", scan)
        if not isinstance(result, dict):
            return "Scan completed. Review the structured results for details."
        checks = result.get("checks", {})
        warnings = []
        for name, value in checks.items() if isinstance(checks, dict) else []:
            if isinstance(value, dict) and value.get("status") not in {"ok", None}:
                warnings.append(f"{name}: {value.get('status')}")
        assets = result.get("subdomains", [])
        parts = [f"Scan '{scan.get('command', 'unknown')}' for {scan.get('target', 'target')} completed."]
        if assets:
            parts.append(f"Discovered {len(assets)} subdomain name(s).")
        if warnings:
            parts.append("Items needing review: " + "; ".join(warnings) + ".")
        else:
            parts.append("No flagged checks were reported in the available structured results.")
        parts.append("Treat scanner output as indicators, not proof; verify findings within the authorized scope.")
        return " ".join(parts)

    def _ollama(self, scan: Dict[str, Any]) -> str:
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": "Summarize authorized security assessment findings. Be factual, concise, distinguish evidence from inference, and do not invent vulnerabilities."},
                {"role": "user", "content": str(scan)[:30000]},
            ],
        }
        request = urllib.request.Request(
            os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/") + "/api/chat",
            data=__import__("json").dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(request, timeout=self.timeout) as response:
            import json
            body = json.loads(response.read().decode("utf-8"))
        summary = body.get("message", {}).get("content", "").strip()
        if not summary:
            raise ValueError("Ollama returned an empty summary")
        return summary

    def summarize(self, scan: Dict[str, Any]) -> Dict[str, str]:
        if self.provider in {"auto", "ollama"}:
            try:
                return {"summary": self._ollama(scan), "provider": "ollama"}
            except (OSError, urllib.error.URLError, TimeoutError, ValueError, KeyError) as exc:
                reason = f"Ollama unavailable ({type(exc).__name__}); using offline summary."
                return {"summary": self.fallback(scan), "provider": "fallback", "warning": reason}
        if self.provider == "none":
            return {"summary": self.fallback(scan), "provider": "fallback"}
        return {"summary": self.fallback(scan), "provider": "fallback", "warning": f"Unsupported provider '{self.provider}'; used offline summary."}
