import os
import re
from typing import List, Set, Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

class LeadExtractor:
    """
    Extracts contact information (emails, phones) and enriches via Hunter.io.
    """
    
    EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    PHONE_REGEX = r'\+?1?\d{9,15}'

    def __init__(self):
        self.leads: Dict[str, Set[str]] = {"emails": set(), "phones": set()}

    def extract_from_text(self, text: str) -> Dict[str, List[str]]:
        """Extracts emails and phones using regex."""
        emails = re.findall(self.EMAIL_REGEX, text)
        phones = re.findall(self.PHONE_REGEX, text)
        
        self.leads["emails"].update(emails)
        self.leads["phones"].update(phones)
        
        return {k: sorted(list(v)) for k, v in self.leads.items()}

    def hunter_enrich(self, domain: str) -> List[Dict[str, Any]]:
        """Enriches leads using Hunter.io for a given domain."""
        api_key = os.getenv("HUNTER_API_KEY")
        if not api_key:
            return []

        url = f"https://api.hunter.io/v2/domain-search?domain={domain}&api_key={api_key}"
        try:
            resp = httpx.get(url, timeout=10.0)
            if resp.status_code == 200:
                return resp.json().get("data", {}).get("emails", [])
        except Exception:
            pass
        return []

if __name__ == "__main__":
    extractor = LeadExtractor()
    print(extractor.extract_from_text("Contact us at support@example.com or +1234567890"))
