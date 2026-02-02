from typing import List, Optional
from selectolax.lexbor import LexborHTMLParser

class FastParser:
    """
    High-performance HTML parser using selectolax (Lexbor engine).
    Significantly faster than BeautifulSoup.
    """
    
    def __init__(self, html: str):
        self.parser = LexborHTMLParser(html)

    def text(self, selector: str) -> Optional[str]:
        """Returns the text content of the first matching element."""
        node = self.parser.css_first(selector)
        return node.text(strip=True) if node else None

    def attributes(self, selector: str, attr: str) -> List[str]:
        """Returns a list of attribute values for all matching elements."""
        return [node.attributes.get(attr) for node in self.parser.css(selector) if node.attributes.get(attr)]

    def count(self, selector: str) -> int:
        """Returns the number of elements matching the selector."""
        return len(self.parser.css(selector))

    def extract_list(self, list_selector: str, item_selectors: dict) -> List[dict]:
        """Extracts a list of items based on a parent selector and a dictionary of sub-selectors."""
        items = []
        for node in self.parser.css(list_selector):
            item = {}
            for key, selector in item_selectors.items():
                child = node.css_first(selector)
                item[key] = child.text(strip=True) if child else None
            items.append(item)
        return items

if __name__ == "__main__":
    html = "<html><body><ul class='products'><li><span class='name'>Phone</span><span class='price'>$99</span></li></ul></body></html>"
    parser = FastParser(html)
    print(parser.extract_list(".products li", {"name": ".name", "price": ".price"}))
