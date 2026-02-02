import os
from typing import Optional, Dict, Any
from curl_cffi import requests
from dotenv import load_dotenv

load_dotenv()

class StealthRequester:
    """
    Advanced requester using curl-cffi to bypass TLS and HTTP/2 fingerprinting.
    Supports impersonating various browsers and handling complex headers.
    """
    
    DEFAULT_IMPERSONATE = "chrome110"

    def __init__(self, impersonate: str = DEFAULT_IMPERSONATE, proxy: Optional[str] = None):
        self.impersonate = impersonate
        self.proxy = proxy
        self.session = requests.Session()
        
    def get(self, url: str, headers: Optional[Dict[str, str]] = None, params: Optional[Dict[str, Any]] = None, **kwargs) -> requests.Response:
        """Perform a stealthy GET request."""
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        return self.session.get(
            url,
            headers=headers,
            params=params,
            impersonate=self.impersonate,
            proxies=proxies,
            **kwargs
        )

    def post(self, url: str, data: Optional[Any] = None, json: Optional[Any] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """Perform a stealthy POST request."""
        proxies = {"http": self.proxy, "https": self.proxy} if self.proxy else None
        return self.session.post(
            url,
            data=data,
            json=json,
            headers=headers,
            impersonate=self.impersonate,
            proxies=proxies,
            **kwargs
        )

    def firecrawl_scrape(self, url: str) -> Dict[str, Any]:
        """
        Fallback using Firecrawl for extremely difficult targets.
        Requires FIRECRAWL_API_KEY.
        """
        api_key = os.getenv("FIRECRAWL_API_KEY")
        if not api_key:
            raise ValueError("FIRECRAWL_API_KEY not found in environment")
            
        # Simplified Firecrawl call (placeholder for real SDK or API request)
        response = requests.post(
            "https://api.firecrawl.dev/v0/scrape",
            json={"url": url},
            headers={"Authorization": f"Bearer {api_key}"},
            impersonate=self.impersonate
        )
        return response.json()

if __name__ == "__main__":
    # Quick test
    requester = StealthRequester()
    try:
        resp = requester.get("https://tls.peet.ws/api/all")
        print(f"Status: {resp.status_code}")
        print(f"Fingerprint: {resp.json().get('tls', {}).get('ja3')}")
    except Exception as e:
        print(f"Error: {e}")
