"""MCP server entry point — FastMCP app, error helpers, and tool registration."""

from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from .auth import OAuthNotConfiguredError

mcp = FastMCP("gmail")


def _error_response(exc: Exception) -> str:
    """Format an exception into a JSON error string for tool responses."""
    if isinstance(exc, OAuthNotConfiguredError):
        return json.dumps(
            {
                "error": True,
                "error_type": "OAuthNotConfiguredError",
                "message": str(exc),
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
