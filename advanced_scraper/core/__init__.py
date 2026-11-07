"""Core read-only discovery and assessment interfaces.

Implementations remain in their historical modules for backwards compatibility;
new code should import from ``advanced_scraper.core``.
"""

from ..api_inventory import APIInventory
from ..domain_recon import DomainRecon
from ..safe_fuzzer import SafeFuzzer
from ..vuln_enumerator import SafeVulnEnumerator
from ..web_app_fingerprint import WebAppFingerprint

__all__ = ["APIInventory", "DomainRecon", "SafeFuzzer", "SafeVulnEnumerator", "WebAppFingerprint"]
