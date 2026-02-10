"""Gmail attachment tool — get attachment data."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..accounts import get_gmail_service
from ..server import mcp, _error_response


@mcp.tool()
def gmail_attachment_get(
    message_id: Annotated[str, Field(description="The message ID containing the attachment")],
    attachment_id: Annotated[str, Field(description="The attachment ID to retrieve")],
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """Get attachment data (base64-encoded) from a message."""
    try:
        service = get_gmail_service(account)
        result = service.users().messages().attachments().get(
            userId="me", messageId=message_id, id=attachment_id
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
