import json
import os
from typing import Optional, Dict, Any
from .stealth_requester import StealthRequester

class AuthManager:
    """
    Handles automated login flows and maintains session persistence.
    """
    
    def __init__(self, requester: Optional[StealthRequester] = None, session_file: str = "session.json"):
        self.requester = requester or StealthRequester()
        self.session_file = session_file
        self.cookies = {}
        self._load_session()

    def _load_session(self):
        """Loads cookies from a local file if they exist."""
        if os.path.exists(self.session_file):
            try:
                with open(self.session_file, 'r') as f:
                    self.cookies = json.load(f)
                    self.requester.session.cookies.update(self.cookies)
            except Exception:
                pass

    def save_session(self):
        """Saves current session cookies to a local file."""
        cookies_dict = self.requester.session.cookies.get_dict()
        with open(self.session_file, 'w') as f:
            json.dump(cookies_dict, f)

    def login(self, login_url: str, credentials: Dict[str, str], form_data: Optional[Dict[str, str]] = None) -> bool:
        """
        Generic login handler. Submits credentials to a login URL.
        """
        data = form_data or {}
        data.update(credentials)
        
        response = self.requester.post(login_url, data=data)
        
        if response.status_code in [200, 302]:
            self.save_session()
            return True
        return False

    def is_logged_in(self, check_url: str, pattern: str) -> bool:
        """Checks if current session is logged in by looking for a pattern in a check URL's response."""
        response = self.requester.get(check_url)
        return pattern in response.text

if __name__ == "__main__":
    # Example usage
    auth = AuthManager()
    # auth.login("https://example.com/login", {"user": "test", "pass": "test"})
