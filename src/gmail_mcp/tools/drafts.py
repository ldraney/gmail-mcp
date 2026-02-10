"""Gmail draft tools — list, get, create, update, send, delete."""

from __future__ import annotations

import base64
import json
from email.mime.text import MIMEText
from typing import Annotated

from pydantic import Field

from ..accounts import get_gmail_service
from ..server import mcp, _error_response


@mcp.tool()
def gmail_drafts_list(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
    max_results: Annotated[int, Field(description="Maximum number of drafts to return")] = 10,
    page_token: Annotated[str | None, Field(description="Token for fetching the next page of results")] = None,
) -> str:
    """List drafts in the account."""
    try:
        service = get_gmail_service(account)
        kwargs: dict = {"userId": "me", "maxResults": max_results}
        if page_token:
            kwargs["pageToken"] = page_token
        result = service.users().drafts().list(**kwargs).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_draft_get(
    draft_id: Annotated[str, Field(description="The draft ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    response_format: Annotated[str, Field(description="Response format: 'full', 'metadata', 'minimal', or 'raw'")] = "full",
) -> str:
    """Get a single draft by ID."""
    try:
        service = get_gmail_service(account)
        result = service.users().drafts().get(
            userId="me", id=draft_id, format=response_format
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_draft_create(
    to: Annotated[str, Field(description="Recipient email address")],
    subject: Annotated[str, Field(description="Email subject line")],
    body: Annotated[str, Field(description="Email body (plain text)")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    cc: Annotated[str | None, Field(description="CC recipients (comma-separated)")] = None,
    bcc: Annotated[str | None, Field(description="BCC recipients (comma-separated)")] = None,
    thread_id: Annotated[str | None, Field(description="Thread ID to associate the draft with (for replies)")] = None,
) -> str:
    """Create a new draft email."""
    try:
        service = get_gmail_service(account)
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft_body: dict = {"message": {"raw": raw}}
        if thread_id:
            draft_body["message"]["threadId"] = thread_id
        result = service.users().drafts().create(userId="me", body=draft_body).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_draft_update(
    draft_id: Annotated[str, Field(description="The draft ID to update")],
    to: Annotated[str, Field(description="Recipient email address")],
    subject: Annotated[str, Field(description="Email subject line")],
    body: Annotated[str, Field(description="Email body (plain text)")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    cc: Annotated[str | None, Field(description="CC recipients (comma-separated)")] = None,
    bcc: Annotated[str | None, Field(description="BCC recipients (comma-separated)")] = None,
) -> str:
    """Update an existing draft with new content."""
    try:
        service = get_gmail_service(account)
        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        result = service.users().drafts().update(
            userId="me", id=draft_id, body={"message": {"raw": raw}}
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_draft_send(
    draft_id: Annotated[str, Field(description="The draft ID to send")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Send an existing draft."""
    try:
        service = get_gmail_service(account)
        result = service.users().drafts().send(
            userId="me", body={"id": draft_id}
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_draft_delete(
    draft_id: Annotated[str, Field(description="The draft ID to delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Permanently delete a draft."""
    try:
        service = get_gmail_service(account)
        service.users().drafts().delete(userId="me", id=draft_id).execute()
        return json.dumps({"success": True, "draft_id": draft_id, "action": "deleted"}, indent=2)
    except Exception as exc:
        return _error_response(exc)
