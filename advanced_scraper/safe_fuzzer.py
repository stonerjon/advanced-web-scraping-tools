from __future__ import annotations

from typing import Any, Dict, List

import httpx


class WebAppFingerprint:
    """Perform lightweight application fingerprinting with safe, read-only requests."""

    def __init__(self, client: httpx.Client | None = None):
        self.client = client or httpx.Client(follow_redirects=True, timeout=10.0)

    def fingerprint(self, url: str) -> Dict[str, Any]:
        response = self.client.get(url, timeout=10.0)
        body = (response.text or "").lower()
        headers = {k.lower(): v for k, v in response.headers.items()}

        framework_signals = {
            "nginx": ["nginx", "x-powered-by: nginx"],
            "apache": ["apache"],
            "gunicorn": ["gunicorn"],
            "django": ["django", "x-frame-options"],
            "flask": ["flask", "werkzeug"],
            "express": ["express", "x-powered-by: express"],
            "wordpress": ["wp-content", "wordpress"],
            "php": ["php", "x-powered-by: php"],
            "asp.net": ["asp.net", "x-aspnet-version"],
            "react": ["react", "__next"],
        }

        detected: List[str] = []
        for name, patterns in framework_signals.items():
            if any(pattern in body for pattern in patterns):
                detected.append(name)

        detected.extend(
            [
                "cloudflare"
                for key, value in headers.items()
                if "cloudflare" in str(key).lower() or "cloudflare" in str(value).lower()
            ]
        )

        return {
            "url": url,
            "status_code": response.status_code,
            "server": headers.get("server"),
            "x_powered_by": headers.get("x-powered-by"),
            "content_type": headers.get("content-type"),
            "redirected": response.history and len(response.history) > 0,
            "frameworks": sorted(set(detected)),
            "security_headers": {
                "strict_transport_security": headers.get("strict-transport-security"),
                "x_frame_options": headers.get("x-frame-options"),
                "x_content_type_options": headers.get("x-content-type-options"),
                "content_security_policy": headers.get("content-security-policy"),
            },
        }
