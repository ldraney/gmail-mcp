"""Gmail label tools — list, get, create, update, delete."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..accounts import get_gmail_service
from ..server import mcp, _error_response


@mcp.tool()
def gmail_labels_list(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """List all labels in the account (system and user-created)."""
    try:
        service = get_gmail_service(account)
        result = service.users().labels().list(userId="me").execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_label_get(
    label_id: Annotated[str, Field(description="The label ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Get details of a single label including message/thread counts."""
    try:
        service = get_gmail_service(account)
        result = service.users().labels().get(userId="me", id=label_id).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_label_create(
    name: Annotated[str, Field(description="Name for the new label")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    label_list_visibility: Annotated[str, Field(description="Visibility in label list: 'labelShow', 'labelShowIfUnread', or 'labelHide'")] = "labelShow",
    message_list_visibility: Annotated[str, Field(description="Visibility in message list: 'show' or 'hide'")] = "show",
) -> str:
    """Create a new user label."""
    try:
        service = get_gmail_service(account)
        body = {
            "name": name,
            "labelListVisibility": label_list_visibility,
            "messageListVisibility": message_list_visibility,
        }
        result = service.users().labels().create(userId="me", body=body).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_label_update(
    label_id: Annotated[str, Field(description="The label ID to update")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    name: Annotated[str | None, Field(description="New name for the label")] = None,
    label_list_visibility: Annotated[str | None, Field(description="Visibility in label list: 'labelShow', 'labelShowIfUnread', or 'labelHide'")] = None,
    message_list_visibility: Annotated[str | None, Field(description="Visibility in message list: 'show' or 'hide'")] = None,
) -> str:
    """Update a label's name or visibility settings."""
    try:
        service = get_gmail_service(account)
        body: dict = {}
        if name is not None:
            body["name"] = name
        if label_list_visibility is not None:
            body["labelListVisibility"] = label_list_visibility
        if message_list_visibility is not None:
            body["messageListVisibility"] = message_list_visibility
        result = service.users().labels().update(
            userId="me", id=label_id, body=body
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_label_delete(
    label_id: Annotated[str, Field(description="The label ID to delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Delete a user label. System labels cannot be deleted."""
    try:
        service = get_gmail_service(account)
        service.users().labels().delete(userId="me", id=label_id).execute()
        return json.dumps({"success": True, "label_id": label_id, "action": "deleted"}, indent=2)
    except Exception as exc:
        return _error_response(exc)
