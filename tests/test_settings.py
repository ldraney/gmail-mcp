"""Tests for settings tools — verifies SDK calls and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestVacationGet:
    def test_get(self, mock_client):
        from gmail_mcp.tools.settings import gmail_vacation_get

        mock_client.get_vacation_settings.return_value = {
            "enableAutoReply": False,
            "responseSubject": "Out of Office",
        }
        result = json.loads(gmail_vacation_get(account="draneylucas"))
        assert result["enableAutoReply"] is False
        assert result["responseSubject"] == "Out of Office"
        mock_client.get_vacation_settings.assert_called_once()

    def test_get_error(self, mock_client):
        from gmail_mcp.tools.settings import gmail_vacation_get

        mock_client.get_vacation_settings.side_effect = GmailAPIError(401, "Unauthorized")
        result = json.loads(gmail_vacation_get(account="draneylucas"))
        assert result["error"] is True


class TestVacationSet:
    def test_set_enable(self, mock_client):
        from gmail_mcp.tools.settings import gmail_vacation_set

        mock_client.update_vacation_settings.return_value = {
            "enableAutoReply": True,
            "responseSubject": "Away",
            "responseBodyPlainText": "I'm out.",
        }
        result = json.loads(gmail_vacation_set(
            enable_auto_reply=True,
            account="draneylucas",
            response_subject="Away",
            response_body_plain_text="I'm out.",
        ))
        assert result["enableAutoReply"] is True
        mock_client.update_vacation_settings.assert_called_once_with(
            enable_auto_reply=True,
            response_subject="Away",
            response_body_plain_text="I'm out.",
            response_body_html=None,
            restrict_to_contacts=False,
            restrict_to_domain=False,
            start_time=None,
            end_time=None,
        )

    def test_set_disable(self, mock_client):
        from gmail_mcp.tools.settings import gmail_vacation_set

        mock_client.update_vacation_settings.return_value = {"enableAutoReply": False}
        result = json.loads(gmail_vacation_set(
            enable_auto_reply=False, account="draneylucas",
        ))
        assert result["enableAutoReply"] is False
