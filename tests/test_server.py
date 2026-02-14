"""Tests for server helpers — _parse_json and _error_response."""

from __future__ import annotations

import json

import pytest
from gmail_sdk import GmailAPIError

from gmail_mcp.server import _parse_json, _error_response


class TestParseJson:
    def test_none_returns_none(self):
        assert _parse_json(None, "test") is None

    def test_dict_passthrough(self):
        data = {"key": "value", "nested": {"a": 1}}
        assert _parse_json(data, "test") is data

    def test_list_passthrough(self):
        data = [1, 2, 3]
        assert _parse_json(data, "test") is data

    def test_valid_json_string(self):
        result = _parse_json('{"from": "boss@co.com"}', "criteria")
        assert result == {"from": "boss@co.com"}

    def test_valid_json_array_string(self):
        result = _parse_json('["INBOX", "UNREAD"]', "labels")
        assert result == ["INBOX", "UNREAD"]

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON for parameter 'criteria'"):
            _parse_json("not json at all", "criteria")

    def test_invalid_json_includes_name(self):
        with pytest.raises(ValueError, match="'my_param'"):
            _parse_json("{bad", "my_param")


class TestErrorResponse:
    def test_gmail_api_error(self):
        exc = GmailAPIError(404, "Message not found")
        result = json.loads(_error_response(exc))
        assert result["error"] is True
        assert result["status_code"] == 404
        assert result["message"] == "Message not found"

    def test_gmail_api_error_server(self):
        exc = GmailAPIError(500, "Internal server error")
        result = json.loads(_error_response(exc))
        assert result["status_code"] == 500

    def test_generic_exception(self):
        exc = RuntimeError("Something went wrong")
        result = json.loads(_error_response(exc))
        assert result["error"] is True
        assert result["message"] == "Something went wrong"
        assert "status_code" not in result

    def test_value_error(self):
        exc = ValueError("Bad input")
        result = json.loads(_error_response(exc))
        assert result["error"] is True
        assert result["message"] == "Bad input"
