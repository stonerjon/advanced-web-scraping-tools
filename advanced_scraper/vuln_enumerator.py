import time
from typing import Dict, List

import httpx


class SafeFuzzer:
    """Low-noise directory and path discovery for authorized reconnaissance."""

    DEFAULT_PATHS = [
        "",
        "api",
        "api/v1",
        "api/v2",
        "graphql",
        "swagger",
        "openapi.json",
        "swagger.json",
        ".well-known",
        "admin",
        "login",
        "health",
        "metrics",
        "debug",
        "status",
        "robots.txt",
        "sitemap.xml",
    ]

    def __init__(self, base_url: str, wordlist: List[str] | None = None, delay: float = 0.5):
        self.base_url = base_url.rstrip("/")
        self.wordlist = wordlist or self.DEFAULT_PATHS
        self.delay = delay

    def probe_paths(self) -> List[Dict[str, object]]:
        results: List[Dict[str, object]] = []
        for path in self.wordlist:
            url = f"{self.base_url}/{path.lstrip('/')}" if path else self.base_url
            try:
                response = httpx.get(url, timeout=5.0, follow_redirects=False)
            except Exception:
                time.sleep(self.delay)
                continue

            if response.status_code in {200, 301, 302, 401, 403, 405, 500}:
                results.append(
                    {
                        "url": url,
                        "status_code": response.status_code,
                        "content_type": response.headers.get("content-type"),
                        "location": response.headers.get("location"),
                    }
                )
            time.sleep(self.delay)
        return results
