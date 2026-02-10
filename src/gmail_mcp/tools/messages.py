"""Gmail message tools — list, get, send, forward, modify, archive, trash, delete, batch."""

from __future__ import annotations

import base64
import json
from email.mime.text import MIMEText
from typing import Annotated

from pydantic import Field

from ..accounts import get_gmail_service, get_account_email
from ..server import mcp, _error_response


@mcp.tool()
def gmail_messages_list(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
    query: Annotated[str | None, Field(description="Gmail search query (same syntax as Gmail search box), e.g. 'is:unread from:boss@company.com'")] = None,
    max_results: Annotated[int, Field(description="Maximum number of messages to return (1-500)")] = 10,
    label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to filter by, e.g. 'INBOX,UNREAD'")] = None,
    page_token: Annotated[str | None, Field(description="Token for fetching the next page of results")] = None,
) -> str:
    """List messages matching a query. Returns message IDs and thread IDs."""
    try:
        service = get_gmail_service(account)
        kwargs: dict = {"userId": "me", "maxResults": max_results}
        if query:
            kwargs["q"] = query
        if label_ids:
            kwargs["labelIds"] = [lid.strip() for lid in label_ids.split(",")]
        if page_token:
            kwargs["pageToken"] = page_token
        result = service.users().messages().list(**kwargs).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_get(
    message_id: Annotated[str, Field(description="The message ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    format: Annotated[str, Field(description="Response format: 'full', 'metadata', 'minimal', or 'raw'")] = "full",
) -> str:
    """Get a single message by ID with full content."""
    try:
        service = get_gmail_service(account)
        result = service.users().messages().get(
            userId="me", id=message_id, format=format
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_send(
    to: Annotated[str, Field(description="Recipient email address")],
    subject: Annotated[str, Field(description="Email subject line")],
    body: Annotated[str, Field(description="Email body (plain text)")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    cc: Annotated[str | None, Field(description="CC recipients (comma-separated)")] = None,
    bcc: Annotated[str | None, Field(description="BCC recipients (comma-separated)")] = None,
) -> str:
    """Send an email from the specified account."""
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
        result = service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_reply(
    message_id: Annotated[str, Field(description="The message ID to reply to")],
    body: Annotated[str, Field(description="Reply body (plain text)")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Reply to an existing message (preserves thread)."""
    try:
        service = get_gmail_service(account)
        original = service.users().messages().get(
            userId="me", id=message_id, format="metadata",
            metadataHeaders=["Subject", "From", "To", "Message-ID"],
        ).execute()

        headers = {h["name"]: h["value"] for h in original.get("payload", {}).get("headers", [])}
        reply = MIMEText(body)
        reply["to"] = headers.get("From", "")
        reply["subject"] = "Re: " + headers.get("Subject", "")
        reply["In-Reply-To"] = headers.get("Message-ID", "")
        reply["References"] = headers.get("Message-ID", "")

        raw = base64.urlsafe_b64encode(reply.as_bytes()).decode()
        result = service.users().messages().send(
            userId="me",
            body={"raw": raw, "threadId": original.get("threadId")},
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_forward(
    message_id: Annotated[str, Field(description="The message ID to forward")],
    to: Annotated[str, Field(description="Recipient email address for the forward")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    additional_text: Annotated[str | None, Field(description="Text to prepend to the forwarded message")] = None,
) -> str:
    """Forward an existing message to another recipient."""
    try:
        service = get_gmail_service(account)
        original = service.users().messages().get(
            userId="me", id=message_id, format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in original.get("payload", {}).get("headers", [])}

        # Extract body text
        body_text = ""
        payload = original.get("payload", {})
        if "body" in payload and payload["body"].get("data"):
            body_text = base64.urlsafe_b64decode(payload["body"]["data"]).decode()
        elif "parts" in payload:
            for part in payload["parts"]:
                if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
                    body_text = base64.urlsafe_b64decode(part["body"]["data"]).decode()
                    break

        forward_body = ""
        if additional_text:
            forward_body = additional_text + "\n\n"
        forward_body += f"---------- Forwarded message ----------\n"
        forward_body += f"From: {headers.get('From', '')}\n"
        forward_body += f"Date: {headers.get('Date', '')}\n"
        forward_body += f"Subject: {headers.get('Subject', '')}\n"
        forward_body += f"To: {headers.get('To', '')}\n\n"
        forward_body += body_text

        fwd = MIMEText(forward_body)
        fwd["to"] = to
        fwd["subject"] = "Fwd: " + headers.get("Subject", "")

        raw = base64.urlsafe_b64encode(fwd.as_bytes()).decode()
        result = service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_modify(
    message_id: Annotated[str, Field(description="The message ID to modify")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    add_label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to add")] = None,
    remove_label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to remove")] = None,
) -> str:
    """Modify labels on a message (add/remove labels like UNREAD, STARRED, etc.)."""
    try:
        service = get_gmail_service(account)
        body: dict = {}
        if add_label_ids:
            body["addLabelIds"] = [lid.strip() for lid in add_label_ids.split(",")]
        if remove_label_ids:
            body["removeLabelIds"] = [lid.strip() for lid in remove_label_ids.split(",")]
        result = service.users().messages().modify(
            userId="me", id=message_id, body=body
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_archive(
    message_id: Annotated[str, Field(description="The message ID to archive")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Archive a message (remove INBOX label)."""
    try:
        service = get_gmail_service(account)
        result = service.users().messages().modify(
            userId="me", id=message_id, body={"removeLabelIds": ["INBOX"]}
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_trash(
    message_id: Annotated[str, Field(description="The message ID to move to trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Move a message to the trash."""
    try:
        service = get_gmail_service(account)
        result = service.users().messages().trash(userId="me", id=message_id).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_untrash(
    message_id: Annotated[str, Field(description="The message ID to remove from trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Remove a message from the trash."""
    try:
        service = get_gmail_service(account)
        result = service.users().messages().untrash(userId="me", id=message_id).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_delete(
    message_id: Annotated[str, Field(description="The message ID to permanently delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Permanently delete a message (requires full access scope). Bypasses trash."""
    try:
        service = get_gmail_service(account)
        service.users().messages().delete(userId="me", id=message_id).execute()
        return json.dumps({"success": True, "message_id": message_id, "action": "permanently_deleted"}, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_messages_batch_modify(
    message_ids: Annotated[str, Field(description="Comma-separated message IDs to modify")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    add_label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to add")] = None,
    remove_label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to remove")] = None,
) -> str:
    """Batch modify labels on multiple messages at once."""
    try:
        service = get_gmail_service(account)
        body: dict = {"ids": [mid.strip() for mid in message_ids.split(",")]}
        if add_label_ids:
            body["addLabelIds"] = [lid.strip() for lid in add_label_ids.split(",")]
        if remove_label_ids:
            body["removeLabelIds"] = [lid.strip() for lid in remove_label_ids.split(",")]
        service.users().messages().batchModify(userId="me", body=body).execute()
        return json.dumps({"success": True, "action": "batch_modified"}, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_messages_batch_delete(
    message_ids: Annotated[str, Field(description="Comma-separated message IDs to permanently delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Permanently delete multiple messages (requires full access scope). Bypasses trash."""
    try:
        service = get_gmail_service(account)
        ids = [mid.strip() for mid in message_ids.split(",")]
        service.users().messages().batchDelete(userId="me", body={"ids": ids}).execute()
        return json.dumps({"success": True, "action": "batch_deleted", "count": len(ids)}, indent=2)
    except Exception as exc:
        return _error_response(exc)
