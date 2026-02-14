"""Tests for history tool — verifies SDK calls and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestHistoryList:
    def test_list_basic(self, mock_client):
        from gmail_mcp.tools.history import gmail_history_list

        mock_client.list_history.return_value = {
            "history": [
                {"id": "100", "messagesAdded": [{"message": {"id": "msg1"}}]},
            ],
            "historyId": "101",
        }
        result = json.loads(gmail_history_list("99", account="draneylucas"))
        assert len(result["history"]) == 1
        assert result["historyId"] == "101"
        mock_client.list_history.assert_called_once_with(
            start_history_id="99",
            label_id=None,
            max_results=100,
            history_types=None,
        )

    def test_list_with_filters(self, mock_client):
        from gmail_mcp.tools.history import gmail_history_list

        mock_client.list_history.return_value = {"historyId": "200"}
        gmail_history_list(
            "100", account="draneylucas",
            label_id="INBOX",
            max_results=50,
            history_types="messageAdded,labelAdded",
        )
        mock_client.list_history.assert_called_once_with(
            start_history_id="100",
            label_id="INBOX",
            max_results=50,
            history_types=["messageAdded", "labelAdded"],
        )

    def test_list_no_changes(self, mock_client):
        from gmail_mcp.tools.history import gmail_history_list

        mock_client.list_history.return_value = {"historyId": "99"}
        result = json.loads(gmail_history_list("99", account="draneylucas"))
        assert "history" not in result
        assert result["historyId"] == "99"

    def test_list_error(self, mock_client):
        from gmail_mcp.tools.history import gmail_history_list

        mock_client.list_history.side_effect = GmailAPIError(404, "Invalid historyId")
        result = json.loads(gmail_history_list("0", account="draneylucas"))
        assert result["error"] is True
        assert result["status_code"] == 404
