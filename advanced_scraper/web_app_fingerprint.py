from __future__ import annotations

import re
from typing import Dict, List, Set

import dns.exception
import dns.name
import dns.resolver
import httpx


class DomainRecon:
    """Passive, low-noise reconnaissance for domains and subdomains."""

    COMMON_SUBDOMAINS = [
        "www",
        "mail",
        "api",
        "admin",
        "dev",
        "staging",
        "login",
        "app",
        "portal",
        "assets",
        "cdn",
        "internal",
        "beta",
        "www2",
    ]

    def __init__(self, domain: str):
        self.domain = domain.strip().lower().strip(".")
        self.subdomains: Set[str] = set()

    def _clean_subdomains(self, values: List[str]) -> List[str]:
        cleaned: Set[str] = set()
        for value in values:
            item = value.strip().lower().rstrip(".")
            if not item or item == self.domain:
                continue
            if self.domain in item and "*" not in item:
                cleaned.add(item)
        return sorted(cleaned)

    def crtsh(self) -> List[str]:
        try:
            response = httpx.get(f"https://crt.sh/?q=%25.{self.domain}&output=json", timeout=20.0)
            response.raise_for_status()
            data = response.json()
            names: List[str] = []
            for item in data:
                name_value = item.get("name_value", "")
                if name_value:
                    names.extend(name_value.split("\n"))
            found = self._clean_subdomains(names)
            self.subdomains.update(found)
            return found
        except Exception:
            return []

    def common_candidates(self) -> List[str]:
        names = [f"{prefix}.{self.domain}" for prefix in self.COMMON_SUBDOMAINS]
        self.subdomains.update(names)
        return sorted(names)

    def dns_probe(self) -> Dict[str, List[str]]:
        resolver = dns.resolver.Resolver()
        records: Dict[str, List[str]] = {
            "A": [],
            "AAAA": [],
            "CNAME": [],
            "MX": [],
            "NS": [],
        }
        for record_type in records:
            try:
                answers = resolver.resolve(self.domain, record_type)
                records[record_type] = [str(item) for item in answers]
            except (dns.exception.DNSException, Exception):
                pass
        return records

    def run(self) -> Dict[str, object]:
        subs = []
        subs.extend(self.crtsh())
        subs.extend(self.common_candidates())
        uniq = sorted(set(subs))
        self.subdomains = set(uniq)
        return {
            "domain": self.domain,
            "subdomains": uniq,
            "dns": self.dns_probe(),
        }
