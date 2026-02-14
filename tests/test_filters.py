"""Tests for filter tools — verifies SDK calls, _parse_json, and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestFiltersList:
    def test_list(self, mock_client):
        from gmail_mcp.tools.filters import gmail_filters_list

        mock_client.list_filters.return_value = {
            "filter": [
                {"id": "f1", "criteria": {"from": "boss@co.com"}},
            ],
        }
        result = json.loads(gmail_filters_list(account="draneylucas"))
        assert len(result["filter"]) == 1
        mock_client.list_filters.assert_called_once()

    def test_list_error(self, mock_client):
        from gmail_mcp.tools.filters import gmail_filters_list

        mock_client.list_filters.side_effect = GmailAPIError(403, "Forbidden")
        result = json.loads(gmail_filters_list(account="draneylucas"))
        assert result["error"] is True


class TestFilterGet:
    def test_get(self, mock_client):
        from gmail_mcp.tools.filters import gmail_filter_get

        mock_client.get_filter.return_value = {
            "id": "f1",
            "criteria": {"from": "boss@co.com"},
            "action": {"addLabelIds": ["IMPORTANT"]},
        }
        result = json.loads(gmail_filter_get("f1", account="draneylucas"))
        assert result["id"] == "f1"
        mock_client.get_filter.assert_called_once_with("f1")


class TestFilterCreate:
    def test_create_with_json_strings(self, mock_client):
        from gmail_mcp.tools.filters import gmail_filter_create

        mock_client.create_filter.return_value = {"id": "f2"}
        criteria = '{"from": "alerts@service.com"}'
        action = '{"addLabelIds": ["Label_1"], "removeLabelIds": ["UNREAD"]}'
        result = json.loads(gmail_filter_create(
            criteria=criteria, action=action, account="draneylucas",
        ))
        assert result["id"] == "f2"
        mock_client.create_filter.assert_called_once_with(
            criteria={"from": "alerts@service.com"},
            action={"addLabelIds": ["Label_1"], "removeLabelIds": ["UNREAD"]},
        )

    def test_create_invalid_json(self, mock_client):
        from gmail_mcp.tools.filters import gmail_filter_create

        result = json.loads(gmail_filter_create(
            criteria="not valid json", action="{}", account="draneylucas",
        ))
        assert result["error"] is True
        assert "Invalid JSON" in result["message"]

    def test_parse_json_passthrough(self, mock_client):
        """_parse_json passes through dicts and lists without JSON parsing."""
        from gmail_mcp.server import _parse_json

        assert _parse_json({"key": "val"}, "test") == {"key": "val"}
        assert _parse_json([1, 2], "test") == [1, 2]
        assert _parse_json(None, "test") is None


class TestFilterDelete:
    def test_delete(self, mock_client):
        from gmail_mcp.tools.filters import gmail_filter_delete

        mock_client.delete_filter.return_value = None
        result = json.loads(gmail_filter_delete("f1", account="draneylucas"))
        assert result["success"] is True
        assert result["action"] == "deleted"
        assert result["filter_id"] == "f1"
        mock_client.delete_filter.assert_called_once_with("f1")
