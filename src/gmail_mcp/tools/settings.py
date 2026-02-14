"""Gmail settings tools — vacation auto-reply get/set."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..server import mcp, get_client, _error_response, _slim_response


@mcp.tool()
def gmail_vacation_get(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """Get the current vacation auto-reply settings."""
    try:
        client = get_client(account)
        result = client.get_vacation_settings()
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)


@mcp.tool()
def gmail_vacation_set(
    enable_auto_reply: Annotated[bool, Field(description="Whether to enable the vacation auto-reply")],
    account: Annotated[str | None, Field(description="Account alias or email")] = None,
    response_subject: Annotated[str | None, Field(description="Subject line for the auto-reply")] = None,
    response_body_plain_text: Annotated[str | None, Field(description="Plain text body for the auto-reply")] = None,
    response_body_html: Annotated[str | None, Field(description="HTML body for the auto-reply (takes precedence over plain text)")] = None,
    restrict_to_contacts: Annotated[bool, Field(description="Only send auto-reply to contacts")] = False,
    restrict_to_domain: Annotated[bool, Field(description="Only send auto-reply to same domain")] = False,
    start_time: Annotated[int | None, Field(description="Start time in epoch milliseconds")] = None,
    end_time: Annotated[int | None, Field(description="End time in epoch milliseconds")] = None,
) -> str:
    """Set vacation auto-reply settings."""
    try:
        client = get_client(account)
        result = client.update_vacation_settings(
            enable_auto_reply=enable_auto_reply,
            response_subject=response_subject,
            response_body_plain_text=response_body_plain_text,
            response_body_html=response_body_html,
            restrict_to_contacts=restrict_to_contacts,
            restrict_to_domain=restrict_to_domain,
            start_time=start_time,
            end_time=end_time,
        )
        return json.dumps(_slim_response(result), indent=2)
    except Exception as exc:
        return _error_response(exc)
