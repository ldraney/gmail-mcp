"""Tests for _slim_response — verifies API noise stripping."""

from __future__ import annotations

from gmail_mcp.server import _slim_response


class TestSlimResponse:
    def test_strips_null_values(self):
        data = {"id": "msg1", "snippet": None, "labelIds": ["INBOX"]}
        result = _slim_response(data)
        assert "snippet" not in result
        assert result["id"] == "msg1"

    def test_strips_empty_strings(self):
        data = {"id": "msg1", "snippet": "", "historyId": "123"}
        result = _slim_response(data)
        assert "snippet" not in result
        assert result["historyId"] == "123"

    def test_strips_empty_lists(self):
        data = {"id": "msg1", "labelIds": [], "threadId": "t1"}
        result = _slim_response(data)
        assert "labelIds" not in result
        assert result["threadId"] == "t1"

    def test_strips_etag(self):
        data = {"id": "msg1", "etag": "abc123", "threadId": "t1"}
        result = _slim_response(data)
        assert "etag" not in result

    def test_strips_server_response(self):
        data = {"id": "msg1", "serverResponse": {"code": 200}}
        result = _slim_response(data)
        assert "serverResponse" not in result

    def test_recurses_into_dicts(self):
        data = {
            "id": "msg1",
            "payload": {
                "mimeType": "text/plain",
                "etag": "xyz",
                "body": {"data": "abc", "size": None},
            },
        }
        result = _slim_response(data)
        assert "etag" not in result["payload"]
        assert "size" not in result["payload"]["body"]
        assert result["payload"]["body"]["data"] == "abc"

    def test_recurses_into_lists(self):
        data = [
            {"id": "msg1", "etag": "a"},
            {"id": "msg2", "snippet": None},
        ]
        result = _slim_response(data)
        assert len(result) == 2
        assert "etag" not in result[0]
        assert "snippet" not in result[1]

    def test_passes_through_primitives(self):
        assert _slim_response(42) == 42
        assert _slim_response("hello") == "hello"
        assert _slim_response(True) is True

    def test_preserves_non_empty_values(self):
        data = {
            "id": "msg1",
            "threadId": "t1",
            "labelIds": ["INBOX", "UNREAD"],
            "snippet": "Hello world",
        }
        result = _slim_response(data)
        assert result == data
