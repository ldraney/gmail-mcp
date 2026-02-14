"""Gmail message tools — profile, list, get, send, reply, forward, modify, archive, trash, delete, batch."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response


@mcp.tool()
def gmail_get_profile(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """Get the authenticated user's Gmail profile (email, messages total, threads total, history ID)."""
    try:
        client = get_client(account)
        result = client.get_profile()
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


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
        client = get_client(account)
        label_list = [lid.strip() for lid in label_ids.split(",")] if label_ids else None
        result = client.list_messages(
            query=query,
            max_results=max_results,
            label_ids=label_list,
            page_token=page_token,
        )
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_get(
    message_id: Annotated[str, Field(description="The message ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    response_format: Annotated[str, Field(description="Response format: 'full', 'metadata', 'minimal', or 'raw'")] = "full",
) -> str:
    """Get a single message by ID with full content."""
    try:
        client = get_client(account)
        result = client.get_message(message_id, format_=response_format)
        return json.dumps(_slim_response(result), indent=2)
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
        client = get_client(account)
        result = client.send_message(to=to, subject=subject, body=body, cc=cc, bcc=bcc)
        return json.dumps(_slim_response(result), indent=2)
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
        client = get_client(account)
        result = client.reply(message_id, body)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_forward(
    message_id: Annotated[str, Field(description="The message ID to forward")],
    to: Annotated[str, Field(description="Recipient email address for the forward")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    note: Annotated[str | None, Field(description="Text to prepend to the forwarded message")] = None,
) -> str:
    """Forward an existing message to another recipient."""
    try:
        client = get_client(account)
        result = client.forward(message_id, to=to, note=note)
        return json.dumps(_slim_response(result), indent=2)
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
        client = get_client(account)
        add_list = [lid.strip() for lid in add_label_ids.split(",")] if add_label_ids else None
        remove_list = [lid.strip() for lid in remove_label_ids.split(",")] if remove_label_ids else None
        result = client.modify_message(message_id, add_label_ids=add_list, remove_label_ids=remove_list)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_archive(
    message_id: Annotated[str, Field(description="The message ID to archive")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Archive a message (remove INBOX label)."""
    try:
        client = get_client(account)
        result = client.archive(message_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_trash(
    message_id: Annotated[str, Field(description="The message ID to move to trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Move a message to the trash."""
    try:
        client = get_client(account)
        result = client.trash_message(message_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_untrash(
    message_id: Annotated[str, Field(description="The message ID to remove from trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Remove a message from the trash."""
    try:
        client = get_client(account)
        result = client.untrash_message(message_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_message_delete(
    message_id: Annotated[str, Field(description="The message ID to permanently delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Permanently delete a message (requires full access scope). Bypasses trash."""
    try:
        client = get_client(account)
        client.delete_message(message_id)
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
        client = get_client(account)
        ids = [mid.strip() for mid in message_ids.split(",")]
        add_list = [lid.strip() for lid in add_label_ids.split(",")] if add_label_ids else None
        remove_list = [lid.strip() for lid in remove_label_ids.split(",")] if remove_label_ids else None
        client.batch_modify_messages(ids, add_label_ids=add_list, remove_label_ids=remove_list)
        return json.dumps({"success": True, "action": "batch_modified", "count": len(ids)}, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_mark_as_read(
    message_id: Annotated[str, Field(description="The message ID to mark as read")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Mark a message as read (remove UNREAD label)."""
    try:
        client = get_client(account)
        result = client.modify_message(message_id, remove_label_ids=["UNREAD"])
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_mark_as_unread(
    message_id: Annotated[str, Field(description="The message ID to mark as unread")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Mark a message as unread (add UNREAD label)."""
    try:
        client = get_client(account)
        result = client.modify_message(message_id, add_label_ids=["UNREAD"])
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)
