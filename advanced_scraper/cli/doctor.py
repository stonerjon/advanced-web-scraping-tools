from __future__ import annotations

import importlib.util
import platform
import shutil
import sys
from pathlib import Path
from typing import Any


def doctor_checks(db_path: str = "data/recon.sqlite3") -> dict[str, Any]:
    """Return local environment checks without making target network requests."""
    checks: dict[str, Any] = {
        "python": {"version": platform.python_version(), "supported": sys.version_info >= (3, 10)},
        "optional_modules": {name: importlib.util.find_spec(name) is not None for name in ("httpx", "dns", "pytest", "ruff")},
        "executables": {name: shutil.which(name) for name in ("git", "docker", "ollama", "opencode", "claude")},
        "database_path": str(Path(db_path).expanduser()),
    }
    return checks
