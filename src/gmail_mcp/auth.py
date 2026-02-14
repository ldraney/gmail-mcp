"""OAuth configuration — paths.

The actual OAuth flow and token refresh are handled by ldraney-gmail-sdk.
This module provides the shared SECRETS_DIR path.
"""

from __future__ import annotations

import os
from pathlib import Path

SECRETS_DIR = Path(os.environ.get("SECRETS_DIR", os.path.expanduser("~/secrets/google-oauth")))
