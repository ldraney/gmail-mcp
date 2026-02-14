"""Tests for thread tools — verifies SDK calls and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestThreadsList:
    def test_list_default(self, mock_client):
        from gmail_mcp.tools.threads import gmail_threads_list

        mock_client.list_threads.return_value = {
            "threads": [{"id": "t1", "historyId": "100"}],
            "resultSizeEstimate": 1,
        }
        result = json.loads(gmail_threads_list(account="draneylucas"))
        assert len(result["threads"]) == 1
        mock_client.list_threads.assert_called_once_with(
            query=None, max_results=10, label_ids=None, page_token=None,
        )

    def test_list_with_query_and_labels(self, mock_client):
        from gmail_mcp.tools.threads import gmail_threads_list

        mock_client.list_threads.return_value = {"threads": []}
        gmail_threads_list(account="draneylucas", query="from:boss", label_ids="INBOX,IMPORTANT")
        mock_client.list_threads.assert_called_once_with(
            query="from:boss", max_results=10, label_ids=["INBOX", "IMPORTANT"], page_token=None,
        )

    def test_list_error(self, mock_client):
        from gmail_mcp.tools.threads import gmail_threads_list

        mock_client.list_threads.side_effect = GmailAPIError(500, "Server error")
        result = json.loads(gmail_threads_list(account="draneylucas"))
        assert result["error"] is True
        assert result["status_code"] == 500


class TestThreadGet:
    def test_get_full(self, mock_client):
        from gmail_mcp.tools.threads import gmail_thread_get

        mock_client.get_thread.return_value = {
            "id": "t1",
            "messages": [{"id": "msg1"}, {"id": "msg2"}],
        }
        result = json.loads(gmail_thread_get("t1", account="draneylucas"))
        assert result["id"] == "t1"
        assert len(result["messages"]) == 2
        mock_client.get_thread.assert_called_once_with("t1", format_="full")

    def test_get_metadata_format(self, mock_client):
        from gmail_mcp.tools.threads import gmail_thread_get

        mock_client.get_thread.return_value = {"id": "t1", "messages": []}
        gmail_thread_get("t1", account="draneylucas", response_format="metadata")
        mock_client.get_thread.assert_called_once_with("t1", format_="metadata")


class TestThreadModify:
    def test_modify_add_labels(self, mock_client):
        from gmail_mcp.tools.threads import gmail_thread_modify

        mock_client.modify_thread.return_value = {"id": "t1", "messages": []}
        result = json.loads(gmail_thread_modify(
            "t1", account="draneylucas", add_label_ids="STARRED",
        ))
        assert result["id"] == "t1"
        mock_client.modify_thread.assert_called_once_with(
            "t1", add_label_ids=["STARRED"], remove_label_ids=None,
        )

    def test_modify_remove_labels(self, mock_client):
        from gmail_mcp.tools.threads import gmail_thread_modify

        mock_client.modify_thread.return_value = {"id": "t1"}
        gmail_thread_modify("t1", account="draneylucas", remove_label_ids="UNREAD,INBOX")
        mock_client.modify_thread.assert_called_once_with(
            "t1", add_label_ids=None, remove_label_ids=["UNREAD", "INBOX"],
        )


class TestThreadTrash:
    def test_trash(self, mock_client):
        from gmail_mcp.tools.threads import gmail_thread_trash

        mock_client.trash_thread.return_value = {"id": "t1"}
        result = json.loads(gmail_thread_trash("t1", account="draneylucas"))
        assert result["id"] == "t1"
        mock_client.trash_thread.assert_called_once_with("t1")


class TestThreadUntrash:
    def test_untrash(self, mock_client):
        from gmail_mcp.tools.threads import gmail_thread_untrash

        mock_client.untrash_thread.return_value = {"id": "t1"}
        result = json.loads(gmail_thread_untrash("t1", account="draneylucas"))
        assert result["id"] == "t1"
        mock_client.untrash_thread.assert_called_once_with("t1")


class TestThreadDelete:
    def test_delete(self, mock_client):
        from gmail_mcp.tools.threads import gmail_thread_delete

        mock_client.delete_thread.return_value = None
        result = json.loads(gmail_thread_delete("t1", account="draneylucas"))
        assert result["success"] is True
        assert result["action"] == "permanently_deleted"
        assert result["thread_id"] == "t1"
        mock_client.delete_thread.assert_called_once_with("t1")
