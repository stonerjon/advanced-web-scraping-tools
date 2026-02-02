import os
from typing import Dict, Any
import httpx
from dotenv import load_dotenv

load_dotenv()

class IdentityValidator:
    """
    Validates emails, phones, and IPs using specialized security APIs.
    """
    
    def validate_ip(self, ip: str) -> Dict[str, Any]:
        """Checks IP reputation via IPQualityScore."""
        api_key = os.getenv("IPQUALITYSCORE_API_KEY")
        if not api_key:
            return {"error": "IPQUALITYSCORE_API_KEY missing"}

        url = f"https://www.ipqualityscore.com/api/json/ip/{api_key}/{ip}"
        try:
            resp = httpx.get(url, timeout=10.0)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

    def validate_phone(self, phone: str) -> Dict[str, Any]:
        """Validates phone number via Numverify."""
        api_key = os.getenv("NUMVERIFY_API_KEY")
        if not api_key:
            return {"error": "NUMVERIFY_API_KEY missing"}

        url = f"http://apilayer.net/api/validate?access_key={api_key}&number={phone}"
        try:
            resp = httpx.get(url, timeout=10.0)
            return resp.json()
        except Exception as e:
            return {"error": str(e)}

if __name__ == "__main__":
    validator = IdentityValidator()
    # print(validator.validate_ip("1.1.1.1"))
