import httpx
from typing import List, Dict

class SocialScoper:
    """
    Finds and validates social media profiles across popular platforms.
    """
    
    PLATFORMS = {
        "Twitter": "https://twitter.com/{}",
        "GitHub": "https://github.com/{}",
        "LinkedIn": "https://www.linkedin.com/in/{}",
        "Instagram": "https://www.instagram.com/{}",
        "Youtube": "https://www.youtube.com/@{}",
        "Reddit": "https://www.reddit.com/user/{}"
    }

    def find_profiles(self, username: str) -> Dict[str, str]:
        """Checks for the existence of a username on various platforms."""
        results = {}
        for platform, url_pattern in self.PLATFORMS.items():
            url = url_pattern.format(username)
            try:
                # Use a standard client for simple existence checks
                resp = httpx.get(url, timeout=5.0, follow_redirects=True)
                if resp.status_code == 200:
                    results[platform] = url
            except Exception:
                pass
        return results

if __name__ == "__main__":
    scoper = SocialScoper()
    # print(scoper.find_profiles("google"))
