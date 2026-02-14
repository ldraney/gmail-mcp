"""Gmail filter tools — list, get, create, delete."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response, _parse_json


@mcp.tool()
def gmail_filters_list(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """List all filters in the account."""
    try:
        client = get_client(account)
        result = client.list_filters()
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_filter_get(
    filter_id: Annotated[str, Field(description="The filter ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Get a single filter by ID."""
    try:
        client = get_client(account)
        result = client.get_filter(filter_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_filter_create(
    criteria: Annotated[str, Field(description='JSON string with filter criteria, e.g. {"from": "boss@company.com", "subject": "urgent"}')],
    action: Annotated[str, Field(description='JSON string with filter action, e.g. {"addLabelIds": ["IMPORTANT"], "removeLabelIds": ["UNREAD"]}')],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Create a new email filter with matching criteria and actions."""
    try:
        criteria_obj = _parse_json(criteria, "criteria")
        action_obj = _parse_json(action, "action")
        client = get_client(account)
        result = client.create_filter(criteria=criteria_obj, action=action_obj)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_filter_delete(
    filter_id: Annotated[str, Field(description="The filter ID to delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Delete a filter."""
    try:
        client = get_client(account)
        client.delete_filter(filter_id)
        return json.dumps({"success": True, "filter_id": filter_id, "action": "deleted"}, indent=2)
    except Exception as exc:
        return _error_response(exc)
