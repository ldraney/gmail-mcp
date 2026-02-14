"""Tests for attachment tool — verifies SDK calls and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestAttachmentGet:
    def test_get(self, mock_client):
        from gmail_mcp.tools.attachments import gmail_attachment_get

        mock_client.get_attachment.return_value = {
            "attachmentId": "att1",
            "size": 1024,
            "data": "base64encodeddata==",
        }
        result = json.loads(gmail_attachment_get(
            "msg1", "att1", account="draneylucas",
        ))
        assert result["attachmentId"] == "att1"
        assert result["size"] == 1024
        assert result["data"] == "base64encodeddata=="
        mock_client.get_attachment.assert_called_once_with("msg1", "att1")

    def test_get_error(self, mock_client):
        from gmail_mcp.tools.attachments import gmail_attachment_get

        mock_client.get_attachment.side_effect = GmailAPIError(404, "Not found")
        result = json.loads(gmail_attachment_get("msg1", "att1", account="draneylucas"))
        assert result["error"] is True
        assert result["status_code"] == 404
