from typing import Optional, Dict, Any, List
from .stealth_requester import StealthRequester
from .auth_manager import AuthManager
from .account_automator import AccountAutomator
from .ai_extractor import AIExtractor
from .fast_parser import FastParser
from .rate_limiter import AdaptiveRateLimiter
from .streaming_sink import StreamingSink
from .header_spoofer import HeaderSpoofer
from .lite_proxy import LiteProxyRotator
from .subdomain_recon import SubdomainRecon
from .infra_recon import InfraRecon
from .api_hunter import APIHunter
from .tech_profiler import TechProfiler
from .lead_extractor import LeadExtractor
from .identity_validator import IdentityValidator
from .domain_intel import DomainIntel
from .threat_intel import ThreatIntel
from .social_scoper import SocialScoper
from .state_manager import StateManager
from .ioc_scanner import IOCScanner

class ScrapingAgent:
    """
    Unified Agent Interface that provides coordinated access to all 21 tools.
    Designed for easy consumption by LLMs and autonomous agents.
    """
    
    def __init__(self, ai_provider: str = "ollama", ai_model: Optional[str] = None):
        self.spoofer = HeaderSpoofer()
        self.requester = StealthRequester()
        self.auth = AuthManager(requester=self.requester)
        self.automator = AccountAutomator()
        self.ai = AIExtractor(provider=ai_provider, model=ai_model)
        self.limiter = AdaptiveRateLimiter()
        self.proxies = LiteProxyRotator()
        self.state = StateManager()
        self.ioc = IOCScanner()

    def quick_scrape(self, url: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Fetches a page stealthily and extracts structured data."""
        self.limiter.wait()
        headers = self.spoofer.generate()
        proxy = self.proxies.get_proxy()
        
        try:
            resp = self.requester.get(url, headers=headers, proxy=proxy)
            if resp.status_code == 200:
                self.limiter.report_success()
                if proxy: self.proxies.report_success(proxy)
                return self.ai.extract(resp.text, schema)
            else:
                self.limiter.report_error_429() if resp.status_code == 429 else None
                if proxy: self.proxies.report_failure(proxy)
                return {"error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def scan_security(self, url: str) -> Dict[str, Any]:
        """Scans a target for IOCs (Indicators of Compromise)."""
        headers = self.spoofer.generate()
        try:
            resp = self.requester.get(url, headers=headers)
            if resp.status_code == 200:
                return self.ioc.parse_advanced(resp.text)
            return {"error": f"Status {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def full_recon(self, domain: str) -> Dict[str, Any]:
        """Runs a complete reconnaissance suite on a domain."""
        results = {}
        
        # Subdomains
        recon = SubdomainRecon(domain)
        results["subdomains"] = recon.get_all()
        
        # Tech & API
        try:
            headers = self.spoofer.generate()
            resp = self.requester.get(f"https://{domain}", headers=headers)
            results["tech_stack"] = list(TechProfiler().profile(resp.text, resp.headers))
            results["api_endpoints"] = APIHunter().scan(resp.text)
        except:
            results["tech_stack"] = []
            
        # Domain Intel
        results["domain_intel"] = DomainIntel(domain).whoxy_lookup()
        
        # Leads
        results["leads"] = LeadExtractor().extract_from_text(resp.text if 'resp' in locals() else "")
        results["hunter_leads"] = LeadExtractor().hunter_enrich(domain)
        
        return results

if __name__ == "__main__":
    agent = ScrapingAgent()
    # print(agent.full_recon("example.com"))
