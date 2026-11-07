from __future__ import annotations

import re
from typing import Set
from urllib.parse import urljoin, urlparse

import httpx


class APIInventory:
    """Passively extract candidate API references from supplied source text."""

    PATTERNS = (
        r"(?i)\b(?:https?|wss?)://[^\s\"'<>`]+",
        r"(?i)(?:^|[\"'`\s(=:])((?:/|\\/)(?:api|apis|rest|rpc|trpc|graphql|graphiql|gql|oauth|auth|openapi|swagger|asyncapi|v\d+)(?:/[^\s\"'<>`)]*)?)",
        r"(?i)[\"'`]((?:/)?(?:api|apis|rest|rpc|trpc|graphql|graphiql|gql|oauth|auth|openapi|swagger|asyncapi|v\d+)[^\"'`]{0,240})[\"'`]",
        r"(?i)[\"'`](/[^\"'`]{1,240})[\"'`]",
    )
    API_MARKERS = ("/api", "/apis", "/rest", "/rpc", "/trpc", "/graphql", "/graphiql", "/gql",
                   "/oauth", "/auth", "/openapi", "/swagger", "/asyncapi", "/v1", "/v2", "/v3")

    def __init__(self, base_url: str, client: httpx.Client | None = None, allow_external_hosts: bool = False):
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Base URL must be an absolute http(s) URL.")
        self.base_url = base_url.rstrip("/")
        self.base_host = (parsed.hostname or "").lower()
        self.client = client or httpx.Client(follow_redirects=True, timeout=10.0)
        self.allow_external_hosts = allow_external_hosts
        self.endpoints: Set[str] = set()

    @classmethod
    def _looks_like_api(cls, url: str) -> bool:
        path = urlparse(url).path.lower()
        return any(marker in path for marker in cls.API_MARKERS)

    def extract_from_text(self, content: str) -> list[str]:
        found: Set[str] = set()
        for pattern in self.PATTERNS:
            for match in re.findall(pattern, content, flags=re.IGNORECASE | re.MULTILINE):
                value = (match if isinstance(match, str) else match[0]).strip()
                value = value.strip("'\"` ").rstrip(".,;:!?)\\}").replace("\\/", "/")
                if not value:
                    continue
                if value.startswith(("ws://", "wss://")):
                    value = "https://" + value.split("://", 1)[1]
                candidate = urljoin(self.base_url + "/", value)
                parsed = urlparse(candidate)
                host = (parsed.hostname or "").lower()
                if parsed.scheme not in {"http", "https"} or not host or not self._looks_like_api(candidate):
                    continue
                if not self.allow_external_hosts and host != self.base_host:
                    continue
                found.add(candidate)
        return sorted(found)

    def scan_url(self, url: str) -> list[str]:
        response = self.client.get(url)
        response.raise_for_status()
        self.endpoints.update(self.extract_from_text(response.text))
        return sorted(self.endpoints)

    def scan_html(self, html: str) -> list[str]:
        self.endpoints.update(self.extract_from_text(html))
        return sorted(self.endpoints)

    def scan_asset_url(self, url: str) -> dict:
        response = self.client.get(url)
        response.raise_for_status()
        return {"url": url, "endpoints": self.extract_from_text(response.text)}
