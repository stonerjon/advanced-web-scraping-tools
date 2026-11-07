from advanced_scraper.core import APIInventory, DomainRecon, SafeFuzzer, SafeVulnEnumerator, WebAppFingerprint
from advanced_scraper.reporters import build_report, export_report, to_markdown
from advanced_scraper.storage import SQLiteStore


def test_modular_facades_keep_legacy_implementations_available():
    assert APIInventory.__name__ == "APIInventory"
    assert DomainRecon.__name__ == "DomainRecon"
    assert SafeFuzzer.__name__ == "SafeFuzzer"
    assert SafeVulnEnumerator.__name__ == "SafeVulnEnumerator"
    assert WebAppFingerprint.__name__ == "WebAppFingerprint"
    assert callable(build_report) and callable(export_report) and callable(to_markdown)
    assert SQLiteStore.__name__ == "SQLiteStore"
