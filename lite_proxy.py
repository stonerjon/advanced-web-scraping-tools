import random
import time
from typing import List, Optional, Dict
import httpx

class LiteProxyRotator:
    """
    Manages a pool of proxies with health checking and automated fetching from free APIs.
    """
    
    FREE_API_URLS = [
        "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"
    ]

    def __init__(self, proxies: Optional[List[str]] = None, auto_fetch: bool = True):
        self.proxies = proxies or []
        self.health_scores = {p: 1.0 for p in self.proxies}  # Score from 0 to 1
        
        if not self.proxies and auto_fetch:
            self.fetch_free_proxies()

    def fetch_free_proxies(self):
        """Fetches fresh proxies from popular free public APIs."""
        print("[*] Fetching fresh proxies from free APIs...")
        new_proxies = set()
        for url in self.FREE_API_URLS:
            try:
                resp = httpx.get(url, timeout=10.0)
                if resp.status_code == 200:
                    # Public lists are usually newline-separated IP:PORT
                    lines = resp.text.strip().split('\n')
                    for line in lines:
                        proxy = line.strip()
                        if ":" in proxy:
                            # Ensure it has a protocol
                            if not proxy.startswith("http"):
                                proxy = f"http://{proxy}"
                            new_proxies.add(proxy)
            except Exception as e:
                print(f"[!] Error fetching from {url}: {e}")
        
        for p in list(new_proxies)[:50]: # Limit to 50 for performance
            self.add_proxy(p)
        print(f"[+] Loaded {len(self.proxies)} proxies into the pool.")

    def add_proxy(self, proxy: str):
        if proxy not in self.proxies:
            self.proxies.append(proxy)
            self.health_scores[proxy] = 1.0

    def get_proxy(self) -> Optional[str]:
        """Returns a proxy based on weighted health score."""
        if not self.proxies:
            return None
            
        # Filter proxies with scores > 0.1
        active_proxies = [p for p in self.proxies if self.health_scores.get(p, 0) > 0.1]
        if not active_proxies:
            if not self.proxies: return None
            return random.choice(self.proxies)
            
        return random.choices(active_proxies, weights=[self.health_scores[p] for p in active_proxies], k=1)[0]

    def report_success(self, proxy: str):
        """Boost health score on successful request."""
        if proxy in self.health_scores:
            self.health_scores[proxy] = min(1.0, self.health_scores[proxy] + 0.1)

    def report_failure(self, proxy: str):
        """Reduce health score on failed request."""
        if proxy in self.health_scores:
            self.health_scores[proxy] = max(0.0, self.health_scores[proxy] - 0.2)
            # If a free proxy falls too low, consider it dead
            if self.health_scores[proxy] < 0.1:
                self.proxies.remove(proxy)

    def check_health(self, check_url: str = "http://httpbin.org/ip"):
        """Checks all proxies against a test URL."""
        to_check = self.proxies[:]
        for p in to_check:
            try:
                with httpx.Client(proxies={"http": p, "https": p}, timeout=5.0) as client:
                    resp = client.get(check_url)
                    if resp.status_code == 200:
                        self.report_success(p)
                    else:
                        self.report_failure(p)
            except Exception:
                self.report_failure(p)

if __name__ == "__main__":
    rotator = LiteProxyRotator()
    proxy = rotator.get_proxy()
    print(f"Next Live Proxy: {proxy}")
