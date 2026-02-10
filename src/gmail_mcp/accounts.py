"""Multi-account resolution and per-account Gmail service cache."""

from __future__ import annotations

from pathlib import Path

from .auth import SECRETS_DIR, build_gmail_service

KNOWN_ACCOUNTS: dict[str, str] = {
    "draneylucas": "draneylucas@gmail.com",
    "lucastoddraney": "lucastoddraney@gmail.com",
    "devopsphilosopher": "devopsphilosopher@gmail.com",
}

_service_cache: dict[str, object] = {}


def resolve_account(account: str | None) -> str:
    """Resolve an account parameter to a known alias.

    Accepts:
    - None: auto-select if only one account has tokens configured
    - An alias (e.g. "draneylucas")
    - A full email (e.g. "draneylucas@gmail.com")

    Returns the alias string.
    """
    if account is None:
        configured = list_configured_accounts()
        if len(configured) == 1:
            return configured[0]
        if len(configured) == 0:
            raise ValueError(
                "No configured accounts found. "
                "Set up OAuth tokens — see docs/gmail-api-setup.md"
            )
        raise ValueError(
            f"Multiple accounts configured: {configured}. "
            "Please specify which account to use."
        )

    # Direct alias match
    if account in KNOWN_ACCOUNTS:
        return account

    # Email match — find alias
    for alias, email in KNOWN_ACCOUNTS.items():
        if account == email:
            return alias

    # Unknown account — still allow it (custom setups)
    return account


def get_gmail_service(account: str | None = None):
    """Get a Gmail API service for the given account (cached per alias)."""
    alias = resolve_account(account)
    if alias not in _service_cache:
        _service_cache[alias] = build_gmail_service(alias)
    return _service_cache[alias]


def list_configured_accounts() -> list[str]:
    """Return aliases that have token files present."""
    configured = []
    for alias in KNOWN_ACCOUNTS:
        token_path = SECRETS_DIR / f"gmail-{alias}.json"
        if token_path.exists():
            configured.append(alias)
    return configured


def get_account_email(alias: str) -> str:
    """Get the email address for an alias, or construct one."""
    return KNOWN_ACCOUNTS.get(alias, f"{alias}@gmail.com")
