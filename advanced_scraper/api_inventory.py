from __future__ import annotations

import re
from typing import List, Set
from urllib.parse import urljoin, urlparse

import httpx


class APIInventory:
    """Find likely API references in a supplied page or source text."""

    PATTERNS = (
        r'https?://[^\s"\'<>]+',
        r'/(?:v\d+|api|graphql|openapi|swagger|oauth|auth|rest)(?:/[^\s"\'<>]*)?',
    )

    def __init__(self, base_url: str, client: httpx.Client | None = None):
        self.base_url = base_url.rstrip("/")
        self.client = client or httpx.Client(follow_redirects=True, timeout=10.0)
        self.endpoints: Set[str] = set()

    @staticmethod
    def _looks_like_api(url: str) -> bool:
        path = urlparse(url).path.lower()
        return any(marker in path for marker in ("/api", "/graphql", "/oauth", "/auth", "/swagger", "/openapi", "/rest", "/v1", "/v2", "/v3"))

    def extract_from_text(self, content: str) -> List[str]:
        found: Set[str] = set()
        for pattern in self.PATTERNS:
            for match in re.findall(pattern, content, flags=re.IGNORECASE):
                candidate = urljoin(self.base_url + "/", match.strip("'\"`),)
                parsed = urlparse(candidate)
                if parsed.scheme in {"http", "https"} and parsed.netloc and self._looks_like_api(candidate):
                    found.add(candidate.rstrip(".,);"))
        return sorted(found)

    def scan_url(self, url: str) -> List[str]:
        response = self.client.get(url)
        response.raise_for_status()
        self.endpoints.update(self.extract_from_text(response.text))
        return sorted(self.endpoints)

    def scan_html(self, html: str) -> List[str]:
        self.endpoints.update(self.extract_from_text(html))
        return sorted(self.endpoints)

    def scan_asset_url(self, url: str) -> dict:
        response = self.client.get(url)
        response.raise_for_status()
        return {"url": url, "endpoints": self.extract_from_text(response.text)}
