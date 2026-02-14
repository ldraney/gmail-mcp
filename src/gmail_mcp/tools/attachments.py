"""Gmail attachment tool — get attachment data."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response


@mcp.tool()
def gmail_attachment_get(
    message_id: Annotated[str, Field(description="The message ID containing the attachment")],
    attachment_id: Annotated[str, Field(description="The attachment ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """Get attachment data (base64-encoded) from a message."""
    try:
        client = get_client(account)
        result = client.get_attachment(message_id, attachment_id)
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)
