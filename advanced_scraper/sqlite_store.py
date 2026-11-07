from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


class SQLiteStore:
    """Small durable local store for scan outputs; each operation opens a safe connection."""

    def __init__(self, path: str = "data/recon.sqlite3"):
        self.path = path
        if path != ":memory:":
            Path(path).expanduser().parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute("""CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                command TEXT NOT NULL,
                target TEXT NOT NULL,
                result_json TEXT NOT NULL,
                summary TEXT
            )""")

    def save_scan(self, command: str, target: str, result: Dict[str, Any], summary: str | None = None) -> int:
        payload = json.dumps(result, ensure_ascii=False, default=str)
        with self._connect() as db:
            cursor = db.execute("INSERT INTO scans(created_at, command, target, result_json, summary) VALUES (?, ?, ?, ?, ?)",
                                (datetime.now(timezone.utc).isoformat(), command, target, payload, summary))
            return int(cursor.lastrowid)

    def update_summary(self, scan_id: int, summary: str) -> None:
        with self._connect() as db:
            db.execute("UPDATE scans SET summary = ? WHERE id = ?", (summary, scan_id))

    def get_scan(self, scan_id: int | None = None) -> Dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM scans WHERE id = ?" if scan_id is not None else "SELECT * FROM scans ORDER BY id DESC LIMIT 1",
                             (scan_id,) if scan_id is not None else ()).fetchone()
        return self._row_to_dict(row) if row else None

    def list_scans(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute("SELECT id, created_at, command, target, summary FROM scans ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
        item = dict(row)
        item["result"] = json.loads(item.pop("result_json"))
        return item
