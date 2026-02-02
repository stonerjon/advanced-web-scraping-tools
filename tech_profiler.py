from typing import Dict, List, Set

class TechProfiler:
    """
    Identifies the technology stack (CMS, Frameworks, Servers) using signatures.
    """
    
    SIGNATURES = {
        "WordPress": ["wp-content", "wp-includes", "wp-json"],
        "React": ["react-root", "_reactRootContainer"],
        "Vue.js": ["data-v-", "vue.js", "vue.min.js"],
        "Django": ["csrfmiddlewaretoken", "django-debug-toolbar"],
        "Next.js": ["_next/static", "__NEXT_DATA__"],
        "Cloudflare": ["cf-ray", "__cf_bm"],
        "NGINX": ["server: nginx"],
        "Apache": ["server: apache"]
    }

    def profile(self, html: str, headers: Dict[str, str]) -> Set[str]:
        """Identifies technologies based on HTML content and response headers."""
        found = set()
        
        # Check Headers
        header_str = "\n".join([f"{k}: {v}" for k, v in headers.items()]).lower()
        for tech, sigs in self.SIGNATURES.items():
            for sig in sigs:
                if ":" in sig and sig.lower() in header_str:
                    found.add(tech)
        
        # Check HTML
        html_low = html.lower()
        for tech, sigs in self.SIGNATURES.items():
            for sig in sigs:
                if ":" not in sig and sig.lower() in html_low:
                    found.add(tech)
                    
        return found

if __name__ == "__main__":
    profiler = TechProfiler()
    print(profiler.profile("<html><div id='react-root'></div></html>", {"Server": "nginx"}))
