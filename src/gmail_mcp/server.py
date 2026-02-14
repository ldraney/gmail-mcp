"""MCP server entry point — FastMCP app, GmailClient lifecycle, and helpers."""

from __future__ import annotations

import json
import os
from typing import Any

from gmail_sdk import GmailClient, GmailAPIError
from mcp.server.fastmcp import FastMCP

from .accounts import resolve_account

mcp = FastMCP("gmail")

SECRETS_DIR = os.environ.get("SECRETS_DIR", os.path.expanduser("~/secrets/google-oauth"))

# ---------------------------------------------------------------------------
# Per-account client cache
# ---------------------------------------------------------------------------

_clients: dict[str, GmailClient] = {}


def get_client(account: str | None = None) -> GmailClient:
    """Return a cached GmailClient for the resolved account alias.

    Creates the client on first call per account. The SDK handles token
    loading and refresh internally.
    """
    alias = resolve_account(account)
    if alias not in _clients:
        _clients[alias] = GmailClient(account=alias, secrets_dir=SECRETS_DIR)
    return _clients[alias]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_STRIP_KEYS = {"etag", "serverResponse"}


def _slim_response(data: Any) -> Any:
    """Recursively strip API noise (nulls, empty values, metadata keys)."""
    if isinstance(data, list):
        return [_slim_response(item) for item in data]
    if not isinstance(data, dict):
        return data
    result: dict[str, Any] = {}
    for key, value in data.items():
        if value is None or value == "" or value == []:
            continue
        if key in _STRIP_KEYS:
            continue
        result[key] = _slim_response(value)
    return result


def _parse_json(value: str | dict | list | None, name: str) -> Any:
    """Parse a JSON string into a Python object, or pass through if already parsed."""
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON for parameter '{name}': {exc}") from exc


def _error_response(exc: Exception) -> str:
    """Format an exception into a JSON error string for tool responses."""
    if isinstance(exc, GmailAPIError):
        return json.dumps(
            {
                "error": True,
                "status_code": exc.status_code,
                "message": exc.message,
            },
            indent=2,
        )
    return json.dumps({"error": True, "message": str(exc)}, indent=2)


# ---------------------------------------------------------------------------
# Register tool modules — each module calls @mcp.tool() at import time
# ---------------------------------------------------------------------------

from .tools import register_all_tools  # noqa: E402

register_all_tools()


def main() -> None:
    """Entry point for the console script."""
    mcp.run()
