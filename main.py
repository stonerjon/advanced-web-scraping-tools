import re
from typing import List, Set
from urllib.parse import urljoin, urlparse

import httpx


class APIInventory:
    """Collects API and service endpoints from HTML, JS, and discovery responses."""

    PATTERNS = [
        r'https?://[^\s"\'<>]+(?:/api(?:/|[?/#])[^\s"\'<>]*)',
        r'/(?:v\d+|api|graphql|openapi|swagger|oauth|auth|rest)[^\s"\'<>]*',
        r'["\'](?:/v\d+|/api|/graphql|/openapi|/swagger|/auth)[^"\'\s<>]*',
    ]

    def __init__(self, base_url: str, client: httpx.Client | None = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(follow_redirects=True, timeout=10.0)
        self.endpoints: Set[str] = set()

    def _normalize_url(self, value: str) -> str:
        value = value.strip().strip('"\'')
        if not value:
            return ""
        if value.startswith("http://") or value.startswith("https://"):
            return value
        if value.startswith("/"):
            return urljoin(self.base_url + "/", value)
        return urljoin(self.base_url + "/", value)

    def _looks_like_api(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        markers = [
            "/api",
            "/graphql",
            "/oauth",
            "/auth",
            "/swagger",
            "/openapi",
            "/rest",
            "/v1",
            "/v2",
            "/v3",
        ]
        return any(marker in path for marker in markers)

    def extract_from_text(self, content: str) -> List[str]:
        found: List[str] = []
        for pattern in self.PATTERNS:
            matches = re.findall(pattern, content, flags=re.IGNORECASE)
            for match in matches:
                normalized = self._normalize_url(match)
                if normalized and self._looks_like_api(normalized):
                    found.append(normalized)
        return sorted(set(found))

    def scan_url(self, url: str) -> List[str]:
        response = self.client.get(url, timeout=10.0)
        response.raise_for_status()
        endpoints = self.extract_from_text(response.text)
        self.endpoints.update(endpoints)
        return sorted(self.endpoints)

    def scan_html(self, html: str) -> List[str]:
        endpoints = self.extract_from_text(html)
        self.endpoints.update(endpoints)
        return sorted(self.endpoints)

    def scan_asset_url(self, url: str) -> dict:
        response = self.client.get(url, timeout=10.0)
        response.raise_for_status()
        return {
            "url": url,
            "endpoints": self.extract_from_text(response.text),
        }
