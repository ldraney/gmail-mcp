"""Tests for draft tools — verifies SDK calls and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestDraftsList:
    def test_list_default(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_drafts_list

        mock_client.list_drafts.return_value = {
            "drafts": [{"id": "d1", "message": {"id": "msg1"}}],
            "resultSizeEstimate": 1,
        }
        result = json.loads(gmail_drafts_list(account="draneylucas"))
        assert len(result["drafts"]) == 1
        mock_client.list_drafts.assert_called_once_with(
            max_results=10, page_token=None, query=None,
        )

    def test_list_with_query(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_drafts_list

        mock_client.list_drafts.return_value = {"drafts": []}
        gmail_drafts_list(account="draneylucas", query="subject:report", max_results=5)
        mock_client.list_drafts.assert_called_once_with(
            max_results=5, page_token=None, query="subject:report",
        )

    def test_list_error(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_drafts_list

        mock_client.list_drafts.side_effect = GmailAPIError(401, "Unauthorized")
        result = json.loads(gmail_drafts_list(account="draneylucas"))
        assert result["error"] is True


class TestDraftGet:
    def test_get_full(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_draft_get

        mock_client.get_draft.return_value = {
            "id": "d1",
            "message": {"id": "msg1", "threadId": "t1"},
        }
        result = json.loads(gmail_draft_get("d1", account="draneylucas"))
        assert result["id"] == "d1"
        mock_client.get_draft.assert_called_once_with("d1", format_="full")

    def test_get_metadata_format(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_draft_get

        mock_client.get_draft.return_value = {"id": "d1"}
        gmail_draft_get("d1", account="draneylucas", response_format="metadata")
        mock_client.get_draft.assert_called_once_with("d1", format_="metadata")


class TestDraftCreate:
    def test_create_basic(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_draft_create

        mock_client.create_draft.return_value = {"id": "d1", "message": {"id": "msg1"}}
        result = json.loads(gmail_draft_create(
            to="recipient@example.com", subject="Draft", body="Content",
            account="draneylucas",
        ))
        assert result["id"] == "d1"
        mock_client.create_draft.assert_called_once_with(
            to="recipient@example.com", subject="Draft", body="Content",
            cc=None, bcc=None, thread_id=None,
        )

    def test_create_with_thread(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_draft_create

        mock_client.create_draft.return_value = {"id": "d2"}
        gmail_draft_create(
            to="a@b.com", subject="Re: Stuff", body="Reply",
            account="draneylucas", thread_id="t1",
        )
        mock_client.create_draft.assert_called_once_with(
            to="a@b.com", subject="Re: Stuff", body="Reply",
            cc=None, bcc=None, thread_id="t1",
        )


class TestDraftUpdate:
    def test_update(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_draft_update

        mock_client.update_draft.return_value = {"id": "d1"}
        result = json.loads(gmail_draft_update(
            "d1", to="new@example.com", subject="Updated", body="New body",
            account="draneylucas",
        ))
        assert result["id"] == "d1"
        mock_client.update_draft.assert_called_once_with(
            "d1", to="new@example.com", subject="Updated", body="New body",
            cc=None, bcc=None,
        )


class TestDraftSend:
    def test_send(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_draft_send

        mock_client.send_draft.return_value = {"id": "sent1", "labelIds": ["SENT"]}
        result = json.loads(gmail_draft_send("d1", account="draneylucas"))
        assert result["id"] == "sent1"
        mock_client.send_draft.assert_called_once_with("d1")


class TestDraftDelete:
    def test_delete(self, mock_client):
        from gmail_mcp.tools.drafts import gmail_draft_delete

        mock_client.delete_draft.return_value = None
        result = json.loads(gmail_draft_delete("d1", account="draneylucas"))
        assert result["success"] is True
        assert result["action"] == "deleted"
        assert result["draft_id"] == "d1"
        mock_client.delete_draft.assert_called_once_with("d1")
