"""Core safe reconnaissance helpers."""

__all__ = ["APIInventory", "DomainRecon", "WebAppFingerprint", "SafeFuzzer", "SafeVulnEnumerator"]


def __getattr__(name):
    # Lazy imports keep optional/network-facing modules from breaking unrelated CLI commands.
    if name == "APIInventory":
        from .api_inventory import APIInventory
        return APIInventory
    if name == "DomainRecon":
        from .domain_recon import DomainRecon
        return DomainRecon
    if name == "WebAppFingerprint":
        from .web_app_fingerprint import WebAppFingerprint
        return WebAppFingerprint
    if name == "SafeFuzzer":
        from .safe_fuzzer import SafeFuzzer
        return SafeFuzzer
    if name == "SafeVulnEnumerator":
        from .vuln_enumerator import SafeVulnEnumerator
        return SafeVulnEnumerator
    raise AttributeError(name)
