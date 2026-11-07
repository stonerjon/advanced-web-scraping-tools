from __future__ import annotations

import time
from typing import Dict, List
from urllib.parse import urlsplit

import httpx


class SafeFuzzer:
    """Rate-limited GET-only path inventory for explicitly authorized targets."""

    DEFAULT_PATHS = ["", "api", "api/v1", "graphql", "swagger", "openapi.json", "health", "status", "robots.txt", "sitemap.xml"]

    def __init__(self, base_url: str, wordlist: List[str] | None = None, delay: float = 0.5):
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Target must be an absolute http(s) URL.")
        self.base_url = base_url.rstrip("/")
        self.wordlist = wordlist if wordlist is not None else self.DEFAULT_PATHS
        self.delay = max(0.0, delay)

    def probe_paths(self) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        with httpx.Client(timeout=5.0, follow_redirects=False) as client:
            for path in self.wordlist:
                url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
                try:
                    response = client.get(url)
                    if response.status_code not in (404, 410):
                        results.append({"url": url, "status_code": response.status_code,
                                        "content_type": response.headers.get("content-type"),
                                        "location": response.headers.get("location")})
                except httpx.HTTPError as exc:
                    results.append({"url": url, "error": type(exc).__name__, "message": str(exc)})
                if self.delay:
                    time.sleep(self.delay)
        return results
