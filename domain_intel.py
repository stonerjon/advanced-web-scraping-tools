import os
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

class DomainIntel:
    """
    Gathers WHOIS and deep DNS intelligence via WhoXy and ViewDNS.
    """
    
    def __init__(self, domain: str):
        self.domain = domain

    def whoxy_lookup(self) -> Dict[str, Any]:
        """Deep WHOIS lookup via WhoXy."""
        api_key = os.getenv("WHOXY_API_KEY")
        if not api_key:
            return {"error": "WHOXY_API_KEY missing"}

        url = f"https://api.whoxy.com/?key={api_key}&whois={self.domain}"
        try:
            resp = httpx.get(url, timeout=10.0)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def viewdns_lookup(self, action: str = "dnsrecord") -> Dict[str, Any]:
        """DNS history and record lookup via ViewDNS."""
        api_key = os.getenv("VIEWDNS_API_KEY")
        if not api_key:
            return {"error": "VIEWDNS_API_KEY missing"}

        # Actions: reverseip, dnsrecord, whois, etc.
        url = f"https://viewdns.info/{action}/?domain={self.domain}&apikey={api_key}&output=json"
        try:
            resp = httpx.get(url, timeout=10.0)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    intel = DomainIntel("example.com")
    # print(intel.whoxy_lookup())
