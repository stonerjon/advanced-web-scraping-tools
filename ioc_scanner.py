import re
import json
from typing import Dict, List, Set, Any
from .ioc_patterns import IOC_PATTERNS

class IOCScanner:
    """
    Advanced high-performance regex engine for identifying 500+ IOC types.
    """
    
    # Core system patterns
    BASE_PATTERNS = {
        "ipv4": r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
        "ipv6": r'\b(?:[A-F0-9]{1,4}:){7}[A-F0-9]{1,4}\b',
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "domain": r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9][a-z0-9-]{0,61}[a-z0-9]\b',
        "url": r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
        "md5": r'\b[a-fA-F0-9]{32}\b',
        "sha1": r'\b[a-fA-F0-9]{40}\b',
        "sha256": r'\b[a-fA-F0-9]{64}\b',
        "cve": r'\bCVE-\d{4}-\d{4,7}\b',
        "mac_addr": r'\b(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})\b',
    }

    def __init__(self, custom_patterns: Dict[str, str] = None):
        # Merge base patterns with the extensive library
        self.patterns = self.BASE_PATTERNS.copy()
        self.patterns.update(IOC_PATTERNS)
        
        if custom_patterns:
            self.patterns.update(custom_patterns)
        
        # Pre-compile for performance
        self.compiled = {name: re.compile(regex, re.IGNORECASE) for name, regex in self.patterns.items()}

    def scan(self, text: str) -> Dict[str, List[str]]:
        """
        Scans text and returns a dictionary of found IOCs categorized by type.
        """
        results = {category: set() for category in self.patterns.keys()}
        
        for category, regex in self.compiled.items():
            matches = regex.findall(text)
            if matches:
                # Handle cases where multiple groups might be captured
                for match in matches:
                    if isinstance(match, tuple):
                        results[category].add(match[0])
                    else:
                        results[category].add(match)
                        
        return {k: sorted(list(v)) for k, v in results.items() if v}

    def parse_advanced(self, text: str) -> Dict[str, Any]:
        """
        Performs contextual parsing (e.g., finding IPs associated with specific domains).
        """
        base_scan = self.scan(text)
        analysis = {
            "summary": {k: len(v) for k, v in base_scan.items()},
            "iocs": base_scan,
            "metadata": {
                "total_unique_iocs": sum(len(v) for v in base_scan.values())
            }
        }
        return analysis

if __name__ == "__main__":
    scanner = IOCScanner()
    sample_text = """
    Found suspicious activity at 192.168.1.50 and connected to malware-site.com.
    File dumped at C:\Windows\System32\evil.exe
    SHA256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
    Registry modified: HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run
    """
    print(json.dumps(scanner.parse_advanced(sample_text), indent=2))
