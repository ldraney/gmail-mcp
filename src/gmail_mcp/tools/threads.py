"""Gmail thread tools — list, get, modify, trash, untrash, delete."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..accounts import get_gmail_service
from ..server import mcp, _error_response


@mcp.tool()
def gmail_threads_list(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
    query: Annotated[str | None, Field(description="Gmail search query (same syntax as Gmail search box)")] = None,
    max_results: Annotated[int, Field(description="Maximum number of threads to return (1-500)")] = 10,
    label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to filter by")] = None,
    page_token: Annotated[str | None, Field(description="Token for fetching the next page of results")] = None,
) -> str:
    """List threads matching a query. Prefer this over messages_list for conversations."""
    try:
        service = get_gmail_service(account)
        kwargs: dict = {"userId": "me", "maxResults": max_results}
        if query:
            kwargs["q"] = query
        if label_ids:
            kwargs["labelIds"] = [lid.strip() for lid in label_ids.split(",")]
        if page_token:
            kwargs["pageToken"] = page_token
        result = service.users().threads().list(**kwargs).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_get(
    thread_id: Annotated[str, Field(description="The thread ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    format: Annotated[str, Field(description="Response format: 'full', 'metadata', or 'minimal'")] = "full",
) -> str:
    """Get a thread with all its messages."""
    try:
        service = get_gmail_service(account)
        result = service.users().threads().get(
            userId="me", id=thread_id, format=format
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_modify(
    thread_id: Annotated[str, Field(description="The thread ID to modify")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    add_label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to add")] = None,
    remove_label_ids: Annotated[str | None, Field(description="Comma-separated label IDs to remove")] = None,
) -> str:
    """Modify labels on all messages in a thread."""
    try:
        service = get_gmail_service(account)
        body: dict = {}
        if add_label_ids:
            body["addLabelIds"] = [lid.strip() for lid in add_label_ids.split(",")]
        if remove_label_ids:
            body["removeLabelIds"] = [lid.strip() for lid in remove_label_ids.split(",")]
        result = service.users().threads().modify(
            userId="me", id=thread_id, body=body
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_trash(
    thread_id: Annotated[str, Field(description="The thread ID to move to trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Move all messages in a thread to the trash."""
    try:
        service = get_gmail_service(account)
        result = service.users().threads().trash(userId="me", id=thread_id).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_untrash(
    thread_id: Annotated[str, Field(description="The thread ID to remove from trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Remove all messages in a thread from the trash."""
    try:
        service = get_gmail_service(account)
        result = service.users().threads().untrash(userId="me", id=thread_id).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_delete(
    thread_id: Annotated[str, Field(description="The thread ID to permanently delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Permanently delete a thread (requires full access scope). Bypasses trash."""
    try:
        service = get_gmail_service(account)
        service.users().threads().delete(userId="me", id=thread_id).execute()
        return json.dumps({"success": True, "thread_id": thread_id, "action": "permanently_deleted"}, indent=2)
    except Exception as exc:
        return _error_response(exc)
