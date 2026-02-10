"""Gmail settings tools — vacation auto-reply get/set."""

from __future__ import annotations

import json
from typing import Annotated

from pydantic import Field

from ..accounts import get_gmail_service
from ..server import mcp, _error_response


@mcp.tool()
def gmail_vacation_get(
    account: Annotated[str | None, Field(description="Account alias or email. Omit to auto-select if only one account is configured.")] = None,
) -> str:
    """Get the current vacation auto-reply settings."""
    try:
        service = get_gmail_service(account)
        result = service.users().settings().getVacation(userId="me").execute()
        return json.dumps(result, indent=2)
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
    start_time: Annotated[str | None, Field(description="Start time in epoch milliseconds (as string)")] = None,
    end_time: Annotated[str | None, Field(description="End time in epoch milliseconds (as string)")] = None,
) -> str:
    """Set vacation auto-reply settings."""
    try:
        service = get_gmail_service(account)
        body: dict = {
            "enableAutoReply": enable_auto_reply,
            "restrictToContacts": restrict_to_contacts,
            "restrictToDomain": restrict_to_domain,
        }
        if response_subject is not None:
            body["responseSubject"] = response_subject
        if response_body_html is not None:
            body["responseBodyHtml"] = response_body_html
        elif response_body_plain_text is not None:
            body["responseBodyPlainText"] = response_body_plain_text
        if start_time is not None:
            body["startTime"] = int(start_time)
        if end_time is not None:
            body["endTime"] = int(end_time)
        result = service.users().settings().updateVacation(
            userId="me", body=body
        ).execute()
        return json.dumps(result, indent=2)
    except Exception as exc:
        return _error_response(exc)
