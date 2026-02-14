"""Tests for label tools — verifies SDK calls and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestLabelsList:
    def test_list(self, mock_client):
        from gmail_mcp.tools.labels import gmail_labels_list

        mock_client.list_labels.return_value = {
            "labels": [
                {"id": "INBOX", "name": "INBOX", "type": "system"},
                {"id": "Label_1", "name": "Work", "type": "user"},
            ],
        }
        result = json.loads(gmail_labels_list(account="draneylucas"))
        assert len(result["labels"]) == 2
        mock_client.list_labels.assert_called_once()

    def test_list_error(self, mock_client):
        from gmail_mcp.tools.labels import gmail_labels_list

        mock_client.list_labels.side_effect = GmailAPIError(401, "Unauthorized")
        result = json.loads(gmail_labels_list(account="draneylucas"))
        assert result["error"] is True


class TestLabelGet:
    def test_get(self, mock_client):
        from gmail_mcp.tools.labels import gmail_label_get

        mock_client.get_label.return_value = {
            "id": "Label_1",
            "name": "Work",
            "messagesTotal": 42,
            "threadsTotal": 10,
        }
        result = json.loads(gmail_label_get("Label_1", account="draneylucas"))
        assert result["name"] == "Work"
        assert result["messagesTotal"] == 42
        mock_client.get_label.assert_called_once_with("Label_1")


class TestLabelCreate:
    def test_create_default(self, mock_client):
        from gmail_mcp.tools.labels import gmail_label_create

        mock_client.create_label.return_value = {"id": "Label_2", "name": "Projects"}
        result = json.loads(gmail_label_create("Projects", account="draneylucas"))
        assert result["name"] == "Projects"
        mock_client.create_label.assert_called_once_with(
            name="Projects",
            label_list_visibility="labelShow",
            message_list_visibility="show",
        )

    def test_create_hidden(self, mock_client):
        from gmail_mcp.tools.labels import gmail_label_create

        mock_client.create_label.return_value = {"id": "Label_3", "name": "Hidden"}
        gmail_label_create(
            "Hidden", account="draneylucas",
            label_list_visibility="labelHide", message_list_visibility="hide",
        )
        mock_client.create_label.assert_called_once_with(
            name="Hidden",
            label_list_visibility="labelHide",
            message_list_visibility="hide",
        )


class TestLabelUpdate:
    def test_update_name(self, mock_client):
        from gmail_mcp.tools.labels import gmail_label_update

        mock_client.update_label.return_value = {"id": "Label_1", "name": "Renamed"}
        result = json.loads(gmail_label_update(
            "Label_1", account="draneylucas", name="Renamed",
        ))
        assert result["name"] == "Renamed"
        mock_client.update_label.assert_called_once_with(
            "Label_1", name="Renamed",
            label_list_visibility=None, message_list_visibility=None,
        )


class TestLabelDelete:
    def test_delete(self, mock_client):
        from gmail_mcp.tools.labels import gmail_label_delete

        mock_client.delete_label.return_value = None
        result = json.loads(gmail_label_delete("Label_1", account="draneylucas"))
        assert result["success"] is True
        assert result["action"] == "deleted"
        assert result["label_id"] == "Label_1"
        mock_client.delete_label.assert_called_once_with("Label_1")
