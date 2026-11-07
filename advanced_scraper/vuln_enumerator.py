from __future__ import annotations

from typing import Any, Dict, List
from urllib.parse import urlsplit

import httpx


class SafeVulnEnumerator:
    """Non-invasive checks for common HTTP security configuration signals."""

    REQUIRED_HEADERS = ("strict-transport-security", "x-frame-options", "x-content-type-options", "content-security-policy", "referrer-policy")

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(follow_redirects=True, timeout=10.0)

    @staticmethod
    def _validate(url: str) -> None:
        if urlsplit(url).scheme not in {"http", "https"} or not urlsplit(url).netloc:
            raise ValueError("Target must be an absolute http(s) URL.")

    def run(self, url: str) -> Dict[str, Any]:
        self._validate(url)
        checks: Dict[str, Any] = {}
        try:
            response = self.client.get(url)
            headers = {key.lower(): value for key, value in response.headers.items()}
            missing = [key for key in self.REQUIRED_HEADERS if key not in headers]
            checks["security_headers"] = {"status": "warning" if missing else "ok", "missing": missing}
            cookies = response.headers.get_list("set-cookie")
            cookie_issues = []
            for cookie in cookies:
                low = cookie.lower()
                for flag in ("secure", "httponly", "samesite"):
                    if flag not in low:
                        cookie_issues.append(f"missing_{flag}")
            checks["cookies"] = {"status": "warning" if cookie_issues else "ok", "issues": sorted(set(cookie_issues))}
        except httpx.HTTPError as exc:
            checks["http"] = {"status": "error", "error": type(exc).__name__, "message": str(exc)}
            return {"url": url, "checks": checks}

        try:
            response = self.client.options(url)
            headers = {key.lower(): value for key, value in response.headers.items()}
            origin = headers.get("access-control-allow-origin")
            credentials = headers.get("access-control-allow-credentials", "false").lower() == "true"
            status = "potentially_exposed" if origin == "*" and credentials else ("review" if origin else "ok")
            checks["cors"] = {"status": status, "allow_origin": origin, "allow_credentials": credentials}
        except httpx.HTTPError as exc:
            checks["cors"] = {"status": "error", "error": type(exc).__name__, "message": str(exc)}
        return {"url": url, "checks": checks}
