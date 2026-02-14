"""Tests for message tools — verifies SDK calls and response formatting."""

from __future__ import annotations

import json

from gmail_sdk import GmailAPIError


class TestGetProfile:
    def test_returns_profile(self, mock_client):
        from gmail_mcp.tools.messages import gmail_get_profile

        mock_client.get_profile.return_value = {
            "emailAddress": "test@gmail.com",
            "messagesTotal": 1234,
            "threadsTotal": 567,
            "historyId": "99999",
        }
        result = json.loads(gmail_get_profile(account="draneylucas"))
        assert result["emailAddress"] == "test@gmail.com"
        assert result["messagesTotal"] == 1234
        mock_client.get_profile.assert_called_once()

    def test_error_handling(self, mock_client):
        from gmail_mcp.tools.messages import gmail_get_profile

        mock_client.get_profile.side_effect = GmailAPIError(401, "Invalid credentials")
        result = json.loads(gmail_get_profile(account="draneylucas"))
        assert result["error"] is True
        assert result["status_code"] == 401
        assert "Invalid credentials" in result["message"]


class TestMessagesList:
    def test_list_default(self, mock_client):
        from gmail_mcp.tools.messages import gmail_messages_list

        mock_client.list_messages.return_value = {
            "messages": [{"id": "msg1", "threadId": "t1"}],
            "resultSizeEstimate": 1,
        }
        result = json.loads(gmail_messages_list(account="draneylucas"))
        assert len(result["messages"]) == 1
        mock_client.list_messages.assert_called_once_with(
            query=None, max_results=10, label_ids=None, page_token=None,
        )

    def test_list_with_query(self, mock_client):
        from gmail_mcp.tools.messages import gmail_messages_list

        mock_client.list_messages.return_value = {"messages": [], "resultSizeEstimate": 0}
        gmail_messages_list(account="draneylucas", query="is:unread", max_results=5)
        mock_client.list_messages.assert_called_once_with(
            query="is:unread", max_results=5, label_ids=None, page_token=None,
        )

    def test_list_with_label_ids(self, mock_client):
        from gmail_mcp.tools.messages import gmail_messages_list

        mock_client.list_messages.return_value = {"messages": []}
        gmail_messages_list(account="draneylucas", label_ids="INBOX,UNREAD")
        mock_client.list_messages.assert_called_once_with(
            query=None, max_results=10, label_ids=["INBOX", "UNREAD"], page_token=None,
        )


class TestMessageGet:
    def test_get_full(self, mock_client):
        from gmail_mcp.tools.messages import gmail_message_get

        mock_client.get_message.return_value = {
            "id": "msg1",
            "threadId": "t1",
            "labelIds": ["INBOX"],
            "payload": {"mimeType": "text/plain"},
        }
        result = json.loads(gmail_message_get("msg1", account="draneylucas"))
        assert result["id"] == "msg1"
        mock_client.get_message.assert_called_once_with("msg1", format_="full")


class TestMessageSend:
    def test_send_basic(self, mock_client):
        from gmail_mcp.tools.messages import gmail_message_send

        mock_client.send_message.return_value = {"id": "sent1", "threadId": "t1"}
        result = json.loads(gmail_message_send(
            to="recipient@example.com",
            subject="Hello",
            body="Test body",
            account="draneylucas",
        ))
        assert result["id"] == "sent1"
        mock_client.send_message.assert_called_once_with(
            to="recipient@example.com", subject="Hello", body="Test body", cc=None, bcc=None,
        )


class TestMessageReply:
    def test_reply(self, mock_client):
        from gmail_mcp.tools.messages import gmail_message_reply

        mock_client.reply.return_value = {"id": "reply1", "threadId": "t1"}
        result = json.loads(gmail_message_reply("msg1", "Thanks!", account="draneylucas"))
        assert result["id"] == "reply1"
        mock_client.reply.assert_called_once_with("msg1", "Thanks!")


class TestMessageForward:
    def test_forward(self, mock_client):
        from gmail_mcp.tools.messages import gmail_message_forward

        mock_client.forward.return_value = {"id": "fwd1"}
        result = json.loads(gmail_message_forward(
            "msg1", to="other@example.com", account="draneylucas",
        ))
        assert result["id"] == "fwd1"
        mock_client.forward.assert_called_once_with("msg1", to="other@example.com", note=None)


class TestMessageModify:
    def test_modify_add_labels(self, mock_client):
        from gmail_mcp.tools.messages import gmail_message_modify

        mock_client.modify_message.return_value = {"id": "msg1", "labelIds": ["STARRED"]}
        result = json.loads(gmail_message_modify(
            "msg1", account="draneylucas", add_label_ids="STARRED",
        ))
        assert "STARRED" in result["labelIds"]
        mock_client.modify_message.assert_called_once_with(
            "msg1", add_label_ids=["STARRED"], remove_label_ids=None,
        )


class TestMarkAsRead:
    def test_mark_as_read(self, mock_client):
        from gmail_mcp.tools.messages import gmail_mark_as_read

        mock_client.modify_message.return_value = {"id": "msg1", "labelIds": ["INBOX"]}
        result = json.loads(gmail_mark_as_read("msg1", account="draneylucas"))
        assert "UNREAD" not in result.get("labelIds", [])
        mock_client.modify_message.assert_called_once_with(
            "msg1", remove_label_ids=["UNREAD"],
        )

    def test_mark_as_unread(self, mock_client):
        from gmail_mcp.tools.messages import gmail_mark_as_unread

        mock_client.modify_message.return_value = {"id": "msg1", "labelIds": ["INBOX", "UNREAD"]}
        result = json.loads(gmail_mark_as_unread("msg1", account="draneylucas"))
        assert "UNREAD" in result["labelIds"]
        mock_client.modify_message.assert_called_once_with(
            "msg1", add_label_ids=["UNREAD"],
        )


class TestBatchModify:
    def test_batch_modify(self, mock_client):
        from gmail_mcp.tools.messages import gmail_messages_batch_modify

        mock_client.batch_modify_messages.return_value = None
        result = json.loads(gmail_messages_batch_modify(
            "msg1,msg2", account="draneylucas", add_label_ids="STARRED",
        ))
        assert result["success"] is True
        mock_client.batch_modify_messages.assert_called_once_with(
            ["msg1", "msg2"], add_label_ids=["STARRED"], remove_label_ids=None,
        )


class TestMessageDelete:
    def test_delete(self, mock_client):
        from gmail_mcp.tools.messages import gmail_message_delete

        mock_client.delete_message.return_value = 204
        result = json.loads(gmail_message_delete("msg1", account="draneylucas"))
        assert result["success"] is True
        assert result["action"] == "permanently_deleted"
        mock_client.delete_message.assert_called_once_with("msg1")
