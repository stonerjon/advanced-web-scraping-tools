from __future__ import annotations

import os
from typing import Any

import httpx


class CloudflareAccountClient:
    """Minimal read-only Cloudflare account diagnostics for an account owner.

    This class intentionally does not deploy Workers, change DNS, or edit
    gateway settings. Use a narrowly scoped token and supply it via env var.
    """

    API = "https://api.cloudflare.com/client/v4"

    def __init__(self, token_env: str = "CLOUDFLARE_API_TOKEN", timeout: float = 10.0):
        token = os.getenv(token_env)
        if not token:
            raise RuntimeError(f"Set {token_env} to use this optional integration.")
        self.client = httpx.Client(
            base_url=self.API,
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            timeout=timeout,
            follow_redirects=False,
        )

    def verify_token(self) -> dict[str, Any]:
        """Check token validity only; Cloudflare returns token status/metadata."""
        response = self.client.get("/user/tokens/verify")
        response.raise_for_status()
        payload = response.json()
        return {"success": payload.get("success", False), "result": payload.get("result"), "errors": payload.get("errors", [])}

    def list_account_workers(self, account_id: str) -> dict[str, Any]:
        """Read-only list of Workers scripts for the explicitly supplied account."""
        if not account_id or any(char in account_id for char in "/?#"):
            raise ValueError("Provide a valid account ID.")
        response = self.client.get(f"/accounts/{account_id}/workers/scripts")
        response.raise_for_status()
        payload = response.json()
        return {"success": payload.get("success", False), "result": payload.get("result", []), "errors": payload.get("errors", [])}
