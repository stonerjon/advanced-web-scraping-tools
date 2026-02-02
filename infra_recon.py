import os
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

class InfraRecon:
    """
    Gathers infrastructure data (IPs, Ports, Services) using Shodan and Censys.
    """
    
    def __init__(self, target: str):
        self.target = target

    def shodan_lookup(self) -> Dict[str, Any]:
        """Gathers data from Shodan API."""
        api_key = os.getenv("SHODAN_API_KEY")
        if not api_key:
            return {"error": "SHODAN_API_KEY missing"}

        try:
            # Query Shodan for host info
            resp = httpx.get(f"https://api.shodan.io/shodan/host/{self.target}?key={api_key}", timeout=10.0)
            return resp.json() if resp.status_code == 200 else {"error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def censys_lookup(self) -> Dict[str, Any]:
        """Gathers data from Censys Search API."""
        api_id = os.getenv("CENSYS_API_ID")
        api_secret = os.getenv("CENSYS_API_SECRET") # Note: Secret usually required
        if not api_id:
            return {"error": "CENSYS_API_ID missing"}

        # Placeholder for Censys API call
        return {"info": "Censys lookup requires API ID and Secret for full access."}

    def virustotal_lookup(self) -> Dict[str, Any]:
        """Gathers domain information from VirusTotal."""
        api_key = os.getenv("VIRUSTOTAL_API_KEY")
        if not api_key:
            return {"error": "VIRUSTOTAL_API_KEY missing"}

        url = f"https://www.virustotal.com/api/v3/domains/{self.target}"
        try:
            resp = httpx.get(url, headers={"x-apikey": api_key}, timeout=10.0)
            return resp.json() if resp.status_code == 200 else {"error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    infra = InfraRecon("8.8.8.8")
    # print(infra.shodan_lookup())
