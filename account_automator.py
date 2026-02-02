import random
import string
import time
from typing import Optional, List, Dict, Any
import httpx

class AccountAutomator:
    """
    Automates credential generation and handles temporary emails for registrations.
    """
    
    SECMAIL_API = "https://www.1secmail.com/api/v1/"

    def __init__(self):
        self.domains = ["1secmail.com", "1secmail.org", "1secmail.net"]

    def generate_random_string(self, length: int = 12) -> str:
        """Generates a random alphanumeric string."""
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def generate_identity(self) -> Dict[str, str]:
        """Generates a random user identity."""
        username = self.generate_random_string(8).lower()
        domain = random.choice(self.domains)
        return {
            "username": username,
            "password": self.generate_random_string(16),
            "email": f"{username}@{domain}",
            "first_name": "Antigravity",
            "last_name": "Bot"
        }

    def get_messages(self, email: str) -> List[Dict[str, Any]]:
        """Fetches messages for the given 1secmail email."""
        username, domain = email.split('@')
        params = {"action": "getMessages", "login": username, "domain": domain}
        resp = httpx.get(self.SECMAIL_API, params=params)
        return resp.json()

    def wait_for_email(self, email: str, timeout: int = 60, interval: int = 5) -> Optional[Dict[str, Any]]:
        """Polls for a new email for a specific duration."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            messages = self.get_messages(email)
            if messages:
                # Get the latest message content
                msg_id = messages[0]['id']
                username, domain = email.split('@')
                resp = httpx.get(self.SECMAIL_API, params={
                    "action": "readMessage",
                    "login": username,
                    "domain": domain,
                    "id": msg_id
                })
                return resp.json()
            time.sleep(interval)
        return None

if __name__ == "__main__":
    automator = AccountAutomator()
    identity = automator.generate_identity()
    print(f"Generated Identity: {identity}")
