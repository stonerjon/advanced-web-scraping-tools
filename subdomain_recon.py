import os
from typing import List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

class SubdomainRecon:
    """
    Discovers subdomains using passive OSINT sources and active patterns.
    """
    
    def __init__(self, domain: str):
        self.domain = domain
        self.subdomains = set()

    def securitytrails_discovery(self) -> List[str]:
        """Passive discovery via SecurityTrails API."""
        api_key = os.getenv("SECURITYTRAILS_API_KEY")
        if not api_key:
            return []

        url = f"https://api.securitytrails.com/v1/domain/{self.domain}/subdomains"
        try:
            resp = httpx.get(url, headers={"apikey": api_key}, timeout=10.0)
            if resp.status_code == 200:
                subs = [f"{s}.{self.domain}" for s in resp.json().get("subdomains", [])]
                self.subdomains.update(subs)
                return subs
        except Exception:
            pass
        return []

    def crtsh_discovery(self) -> List[str]:
        """Passive discovery via crt.sh (Certificate Transparency logs)."""
        url = f"https://crt.sh/?q=%25.{self.domain}&output=json"
        try:
            resp = httpx.get(url, timeout=20.0)
            if resp.status_code == 200:
                subs = [item['name_value'] for item in resp.json()]
                # Flatten and clean
                cleaned = set()
                for s in subs:
                    for part in s.split('\n'):
                        if part.endswith(self.domain) and "*" not in part:
                            cleaned.add(part.lower())
                self.subdomains.update(cleaned)
                return list(cleaned)
        except Exception:
            pass
        return []

    def get_all(self) -> List[str]:
        """Runs all discovery methods and returns unique subdomains."""
        self.securitytrails_discovery()
        self.crtsh_discovery()
        return sorted(list(self.subdomains))

if __name__ == "__main__":
    recon = SubdomainRecon("google.com")
    # print(recon.crtsh_discovery()[:10])
