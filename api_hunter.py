import re
from typing import List, Set

class APIHunter:
    """
    Scans HTML and JS content for hidden API endpoints and sensitive paths.
    """
    
    # Common API version and path patterns
    PATTERNS = [
        r'/(?:api|v[0-9])/[\w\-/]+',
        r'https?://[\w\-\.]+/api/[\w\-/]+',
        r'\\?/(?:graphql|v[0-9]|rest|api|auth|login|register)\\?/',
        r'[\w\-]+\.(?:azurewebsites\.net|herokuapp\.com|cloudfunctions\.net)'
    ]

    def __init__(self):
        self.endpoints: Set[str] = set()

    def scan(self, content: str) -> List[str]:
        """Scans the provided text for API patterns."""
        for pattern in self.PATTERNS:
            matches = re.findall(pattern, content, re.IGNORECASE)
            self.endpoints.update(matches)
        return sorted(list(self.endpoints))

    def scan_js_links(self, html: str) -> List[str]:
        """Extracts potential JS file links from HTML."""
        return re.findall(r'src=["\'](.*?\.js)["\']', html)

if __name__ == "__main__":
    hunter = APIHunter()
    content = "Fetch from /api/v1/user and check https://api.prod.site/auth/token"
    print(hunter.scan(content))
