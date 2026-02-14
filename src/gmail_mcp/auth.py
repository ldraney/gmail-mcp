"""OAuth configuration — paths and error types.

The actual OAuth flow and token refresh are handled by ldraney-gmail-sdk.
This module provides the shared SECRETS_DIR path and a custom error type.
"""

from __future__ import annotations

import os
from pathlib import Path

SECRETS_DIR = Path(os.environ.get("SECRETS_DIR", os.path.expanduser("~/secrets/google-oauth")))


class OAuthNotConfiguredError(Exception):
    """Raised when OAuth tokens are not yet set up for an account."""
