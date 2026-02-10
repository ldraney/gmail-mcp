"""Gmail filter tools — list, get, create, delete."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..accounts import get_gmail_service
from ..server import mcp, _error_response


@mcp.tool()
def gmail_filters_list(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """List all filters in the account."""
    try:
        service = get_gmail_service(account)
        result = service.users().settings().filters().list(userId="me").execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_filter_get(
    filter_id: Annotated[str, Field(description="The filter ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Get a single filter by ID."""
    try:
        service = get_gmail_service(account)
        result = service.users().settings().filters().get(
            userId="me", id=filter_id
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_filter_create(
    criteria: Annotated[str, Field(description="JSON string with filter criteria, e.g. {\"from\": \"boss@company.com\", \"subject\": \"urgent\"}")],
    action: Annotated[str, Field(description="JSON string with filter action, e.g. {\"addLabelIds\": [\"IMPORTANT\"], \"removeLabelIds\": [\"UNREAD\"]}")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Create a new email filter with matching criteria and actions."""
    try:
        service = get_gmail_service(account)
        criteria_obj = json.loads(criteria) if isinstance(criteria, str) else criteria
        action_obj = json.loads(action) if isinstance(action, str) else action
        body = {"criteria": criteria_obj, "action": action_obj}
        result = service.users().settings().filters().create(
            userId="me", body=body
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_filter_delete(
    filter_id: Annotated[str, Field(description="The filter ID to delete")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
) -> str:
    """Delete a filter."""
    try:
        service = get_gmail_service(account)
        service.users().settings().filters().delete(
            userId="me", id=filter_id
        ).execute()
        return json.dumps({"success": True, "filter_id": filter_id, "action": "deleted"}, indent=2)
    except Exception as exc:
        return _error_response(exc)
