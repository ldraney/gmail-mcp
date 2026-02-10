"""OAuth authentication for Gmail API — STUBBED.

This module will be filled in when OAuth is wired up.
For now, it raises OAuthNotConfiguredError with clear instructions.
"""

from __future__ import annotations

import os
from pathlib import Path

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://mail.google.com/",
]

SECRETS_DIR = Path(os.environ.get("SECRETS_DIR", os.path.expanduser("~/secrets/google-oauth")))


class OAuthNotConfiguredError(Exception):
    """Raised when OAuth tokens are not yet set up for an account."""


def build_gmail_service(alias: str):
    """Build an authenticated Gmail API service for the given account alias.

    Currently stubbed — raises OAuthNotConfiguredError with setup instructions.
    """
    token_path = SECRETS_DIR / f"gmail-{alias}.json"
    raise OAuthNotConfiguredError(
        f"OAuth not configured for account '{alias}'. "
        f"Expected token file at: {token_path}\n"
        f"See docs/gmail-api-setup.md for setup instructions."
    )
