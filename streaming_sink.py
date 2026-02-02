import json
import csv
import os
from typing import Any, Dict, List

class StreamingSink:
    """
    Memory-efficient data exporter that streams items directly to disk.
    """
    
    def __init__(self, filename: str, format: str = "jsonl"):
        self.filename = filename
        self.format = format.lower()
        self._first_item = True

    def write(self, item: Dict[str, Any]):
        """Writes a single item to the file."""
        if self.format == "jsonl":
            with open(self.filename, 'a', encoding='utf-8') as f:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        elif self.format == "csv":
            file_exists = os.path.isfile(self.filename)
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=item.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(item)

    def write_batch(self, items: List[Dict[str, Any]]):
        """Writes a list of items."""
        for item in items:
            self.write(item)

if __name__ == "__main__":
    sink = StreamingSink("test_output.jsonl")
    sink.write({"id": 1, "name": "Item A"})
    sink.write({"id": 2, "name": "Item B"})
    print("Data written to test_output.jsonl")
