# Development Guide

## Project Structure

```
src/gmail_mcp/
  server.py            # FastMCP server entry point (main())
  auth.py              # OAuth (STUBBED — raises OAuthNotConfiguredError)
  accounts.py          # Multi-account resolution + service cache
  tools/
    messages.py        # 13 tools: profile, list, get, send, reply, forward, modify, archive, trash/untrash, delete, batch
    threads.py         # 6 tools: list, get, modify, trash/untrash, delete
    drafts.py          # 6 tools: list, get, create, update, send, delete
    labels.py          # 5 tools: list, get, create, update, delete
    attachments.py     # 1 tool: get attachment data
    filters.py         # 4 tools: list, get, create, delete
    settings.py        # 2 tools: vacation get/set
manifest.json          # .mcpb desktop extension
```

## Setup

```bash
# Install dependencies
uv sync

# Run the server locally
uv run python -m gmail_mcp

# Run tests
uv run pytest
```

## Multi-Account Architecture

Single server instance with `account` parameter on every tool:
- Accepts alias (`"draneylucas"`), email (`"draneylucas@gmail.com"`), or `None` (auto-select)
- Token files at `~/secrets/google-oauth/gmail-{alias}.json` (configurable via `SECRETS_DIR` env var)
- Per-account service cache in `accounts.py`

## Adding/Modifying Tools

Each tool module in `src/gmail_mcp/tools/` maps to Gmail API methods. When adding a tool:

1. Use `@mcp.tool()` decorator
2. Parameters must use `Annotated[type, Field(description=...)]` — FastMCP only puts descriptions in JSON schema from this pattern
3. Every tool takes `account: Annotated[str | None, Field(description="...")] = None`
4. Always return JSON strings (even errors — use `_error_response()`)
5. Register the tool module in `tools/__init__.py`

## Releasing

CI auto-publishes on push to `main` when the version is bumped.

1. Bump version in **both** `pyproject.toml` and `manifest.json` (CI fails if they differ)
2. Push to `main`
3. CI: publish to PyPI (OIDC) -> build `.mcpb` -> create GitHub Release

Download link (always latest): `https://github.com/ldraney/gmail-mcp/releases/latest/download/ldraney-gmail-mcp.mcpb`
