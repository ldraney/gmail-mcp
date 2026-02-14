"""Tests for account resolution — alias match, email match, unknown passthrough."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from gmail_mcp.accounts import resolve_account, KNOWN_ACCOUNTS


class TestResolveAccount:
    def test_alias_match(self):
        """Known alias returns the alias directly."""
        assert resolve_account("draneylucas") == "draneylucas"
        assert resolve_account("lucastoddraney") == "lucastoddraney"
        assert resolve_account("devopsphilosopher") == "devopsphilosopher"

    def test_email_match(self):
        """Known email returns the corresponding alias."""
        assert resolve_account("draneylucas@gmail.com") == "draneylucas"
        assert resolve_account("lucastoddraney@gmail.com") == "lucastoddraney"

    def test_unknown_passthrough(self):
        """Unknown account string is passed through as-is."""
        assert resolve_account("customaccount") == "customaccount"
        assert resolve_account("other@domain.com") == "other@domain.com"

    def test_none_single_configured(self):
        """None auto-selects when exactly one account is configured."""
        with patch("gmail_mcp.accounts.list_configured_accounts", return_value=["draneylucas"]):
            assert resolve_account(None) == "draneylucas"

    def test_none_no_configured(self):
        """None raises ValueError when no accounts are configured."""
        with patch("gmail_mcp.accounts.list_configured_accounts", return_value=[]):
            with pytest.raises(ValueError, match="No configured accounts"):
                resolve_account(None)

    def test_none_multiple_configured(self):
        """None raises ValueError when multiple accounts are configured."""
        with patch("gmail_mcp.accounts.list_configured_accounts", return_value=["draneylucas", "lucastoddraney"]):
            with pytest.raises(ValueError, match="Multiple accounts"):
                resolve_account(None)
