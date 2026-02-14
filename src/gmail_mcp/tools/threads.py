"""Gmail thread tools — list, get, modify, trash, untrash, delete."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response


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
        client = get_client(account)
        label_list = [lid.strip() for lid in label_ids.split(",")] if label_ids else None
        result = client.list_threads(
            query=query,
            max_results=max_results,
            label_ids=label_list,
            page_token=page_token,
        )
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_get(
    thread_id: Annotated[str, Field(description="The thread ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    response_format: Annotated[str, Field(description="Response format: 'full', 'metadata', or 'minimal'")] = "full",
) -> str:
    """Get a thread with all its messages."""
    try:
        client = get_client(account)
        result = client.get_thread(thread_id, format_=response_format)
        return json.dumps(_slim_response(result), indent=2)
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
        client = get_client(account)
        add_list = [lid.strip() for lid in add_label_ids.split(",")] if add_label_ids else None
        remove_list = [lid.strip() for lid in remove_label_ids.split(",")] if remove_label_ids else None
        result = client.modify_thread(thread_id, add_label_ids=add_list, remove_label_ids=remove_list)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_trash(
    thread_id: Annotated[str, Field(description="The thread ID to move to trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Move all messages in a thread to the trash."""
    try:
        client = get_client(account)
        result = client.trash_thread(thread_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_untrash(
    thread_id: Annotated[str, Field(description="The thread ID to remove from trash")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Remove all messages in a thread from the trash."""
    try:
        client = get_client(account)
        result = client.untrash_thread(thread_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_thread_delete(
    thread_id: Annotated[str, Field(description="The thread ID to permanently delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Permanently delete a thread (requires full access scope). Bypasses trash."""
    try:
        client = get_client(account)
        client.delete_thread(thread_id)
        return json.dumps({"success": True, "thread_id": thread_id, "action": "permanently_deleted"}, indent=2)
    except Exception as exc:
        return _error_response(exc)
