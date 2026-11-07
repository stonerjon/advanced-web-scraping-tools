import json
from typing import Any, Dict, List


class AssetStore:
    """Stores discovered assets and findings in a simple in-memory repository."""

    def __init__(self):
        self.assets: List[Dict[str, Any]] = []

    def add(self, asset_type: str, value: str, **metadata: Any) -> Dict[str, Any]:
        item = {"type": asset_type, "value": value, **metadata}
        self.assets.append(item)
        return item

    def to_dict(self) -> Dict[str, List[Dict[str, Any]]]:
        return {"assets": self.assets}

    def save_json(self, path: str) -> str:
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)
        return path
