"""Shared test fixtures — mock GmailClient for all tool tests."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_client():
    """Patch get_client() so no real API calls are made.

    Yields a MagicMock that stands in for GmailClient. Tests can configure
    return values like: mock_client.get_profile.return_value = {...}
    """
    client = MagicMock()
    with patch("gmail_mcp.server._clients", {}):
        with patch("gmail_mcp.server.GmailClient", return_value=client):
            yield client
