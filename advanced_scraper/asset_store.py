from __future__ import annotations

from typing import Any, Dict, List

import httpx


class SafeVulnEnumerator:
    """Safe, read-only checks for common web exposures and security misconfigurations."""

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(follow_redirects=True, timeout=10.0)

    def _headers(self, response: httpx.Response) -> Dict[str, str]:
        return {k.lower(): str(v) for k, v in response.headers.items()}

    def check_missing_security_headers(self, url: str) -> Dict[str, Any]:
        response = self.client.get(url, timeout=10.0)
        headers = self._headers(response)
        required = [
            "strict-transport-security",
            "x-frame-options",
            "x-content-type-options",
            "content-security-policy",
            "referrer-policy",
        ]
        missing = [header for header in required if header not in headers]
        return {
            "check": "missing_security_headers",
            "status": "warning" if missing else "ok",
            "missing": missing,
        }

    def check_cors(self, url: str) -> Dict[str, Any]:
        try:
            response = self.client.options(url, timeout=10.0)
        except Exception as exc:
            return {"check": "cors", "status": "error", "message": str(exc)}
        headers = self._headers(response)
        origin = headers.get("access-control-allow-origin")
        credentials = headers.get("access-control-allow-credentials")
        if origin and origin not in {"none", "null"}:
            return {
                "check": "cors",
                "status": "potentially_exposed",
                "allow_origin": origin,
                "allow_credentials": credentials,
            }
        return {"check": "cors", "status": "ok"}

    def check_cookie_security(self, url: str) -> Dict[str, Any]:
        response = self.client.get(url, timeout=10.0)
        headers = self._headers(response)
        cookies = [value for key, value in headers.items() if key == "set-cookie"]
        issues: List[str] = []
        for cookie in cookies:
            if "secure" not in cookie.lower():
                issues.append("missing_secure_flag")
            if "httponly" not in cookie.lower():
                issues.append("missing_httponly_flag")
            if "samesite" not in cookie.lower():
                issues.append("missing_samesite_flag")
        return {
            "check": "cookie_security",
            "status": "warning" if issues else "ok",
            "issues": sorted(set(issues)),
        }

    def run(self, url: str) -> Dict[str, Any]:
        return {
            "url": url,
            "checks": {
                "security_headers": self.check_missing_security_headers(url),
                "cors": self.check_cors(url),
                "cookies": self.check_cookie_security(url),
            },
        }
