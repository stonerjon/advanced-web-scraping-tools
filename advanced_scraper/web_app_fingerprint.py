from __future__ import annotations

from typing import Any, Dict

import httpx


class WebAppFingerprint:
    """Lightweight read-only response and technology-header inspection."""

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(follow_redirects=True, timeout=10.0)

    def fingerprint(self, url: str) -> Dict[str, Any]:
        response = self.client.get(url)
        headers = {key.lower(): value for key, value in response.headers.items()}
        text = response.text[:500_000].lower()
        signals = {
            "wordpress": "wp-content" in text,
            "react": "react" in text or "__next" in text,
            "django": "csrftoken" in str(response.headers.get("set-cookie", "")).lower(),
            "express": headers.get("x-powered-by", "").lower() == "express",
            "cloudflare": "cloudflare" in headers.get("server", "").lower() or "cf-ray" in headers,
        }
        return {
            "url": str(response.url), "status_code": response.status_code,
            "server": headers.get("server"), "x_powered_by": headers.get("x-powered-by"),
            "content_type": headers.get("content-type"),
            "frameworks": sorted(name for name, present in signals.items() if present),
            "security_headers": {name: headers.get(name) for name in (
                "strict-transport-security", "x-frame-options", "x-content-type-options",
                "content-security-policy", "referrer-policy")},
        }
