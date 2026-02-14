"""Gmail history tool — list mailbox changes since a history ID."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response


@mcp.tool()
def gmail_history_list(
    start_history_id: Annotated[str, Field(description="History ID to start listing from (get this from gmail_get_profile)")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    label_id: Annotated[str | None, Field(description="Only return history for this label ID")] = None,
    max_results: Annotated[int, Field(description="Maximum number of history records to return")] = 100,
    history_types: Annotated[str | None, Field(description="Comma-separated history types: messageAdded, messageDeleted, labelAdded, labelRemoved")] = None,
) -> str:
    """List history of mailbox changes since a given history ID. Useful for incremental sync."""
    try:
        client = get_client(account)
        types_list = [t.strip() for t in history_types.split(",")] if history_types else None
        result = client.list_history(
            start_history_id=start_history_id,
            label_id=label_id,
            max_results=max_results,
            history_types=types_list,
        )
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)
