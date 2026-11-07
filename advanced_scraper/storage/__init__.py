"""Persistence adapters; SQLite is the built-in zero-service default."""

from ..sqlite_store import SQLiteStore

__all__ = ["SQLiteStore"]
