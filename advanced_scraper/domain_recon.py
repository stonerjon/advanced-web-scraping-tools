from __future__ import annotations

from typing import Dict, List, Set

import dns.exception
import dns.resolver
import httpx


class DomainRecon:
    """Passive certificate and basic DNS inventory; does not brute-force DNS."""

    def __init__(self, domain: str):
        self.domain = domain.strip().lower().rstrip(".")
        if not self.domain or "/" in self.domain or " " in self.domain:
            raise ValueError("Provide a valid bare domain name (for example, example.org).")
        self.subdomains: Set[str] = set()

    def _clean(self, names: List[str]) -> List[str]:
        suffix = "." + self.domain
        return sorted({name.strip().lower().rstrip(".") for name in names
                       if name.strip() and "*" not in name and
                       (name.strip().lower().rstrip(".") == self.domain or name.strip().lower().rstrip(".").endswith(suffix))})

    def crtsh(self) -> List[str]:
        try:
            response = httpx.get("https://crt.sh/", params={"q": f"%.{self.domain}", "output": "json"}, timeout=15.0)
            response.raise_for_status()
            rows = response.json()
            names = [name for row in rows if isinstance(row, dict) for name in row.get("name_value", "").splitlines()]
            results = self._clean(names)
            self.subdomains.update(results)
            return results
        except (httpx.HTTPError, ValueError, TypeError):
            return []

    def dns_probe(self) -> Dict[str, List[str]]:
        records: Dict[str, List[str]] = {kind: [] for kind in ("A", "AAAA", "CNAME", "MX", "NS", "TXT")}
        resolver = dns.resolver.Resolver()
        resolver.lifetime = 4.0
        for kind in records:
            try:
                records[kind] = [str(answer) for answer in resolver.resolve(self.domain, kind)]
            except (dns.exception.DNSException, OSError):
                continue
        return records

    def run(self) -> dict:
        cert_names = self.crtsh()
        return {"domain": self.domain, "subdomains": cert_names, "dns": self.dns_probe(),
                "sources": {"certificate_transparency": "available" if cert_names else "unavailable_or_empty"}}
