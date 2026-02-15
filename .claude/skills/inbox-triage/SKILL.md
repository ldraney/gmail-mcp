---
name: inbox-triage
description: Scan and triage unread emails — categorize, take bulk action, summarize what needs attention
argument-hint: "[account] [timeframe]"
---

# Inbox Triage

Triage unread email for the specified account (or ask which account). Default timeframe is 3 days.

## Steps

1. **Get unread messages**
   ```
   gmail_messages_list(query="is:unread newer_than:$1", max_results=50, account=$0)
   ```
   If more than 50, paginate. Note the total count.

2. **Fetch metadata for categorization**
   For each message, call `gmail_message_get(message_id, response_format="metadata")` to get From, Subject, Date headers. Batch these calls in parallel where possible.

3. **Categorize every message** into one of these buckets:

   | Category | Action | Example |
   |----------|--------|---------|
   | **Actionable** | Leave unread, summarize for user | Bills, direct messages, job opportunities |
   | **Newsletters** | Archive + mark read | ByteByteGo, Superhuman AI, LinkedIn articles |
   | **CI/GitHub** | Archive + mark read | GitHub Actions, Dependabot, PR notifications |
   | **Alerts** | Archive + mark read (flag security) | Google security alerts, sign-in notifications |
   | **Promotions** | Archive + mark read | Retail deals, cashback offers, restaurant promos |
   | **Spam/Scam** | Trash | Pressure sales ("FINAL NOTICE"), unsolicited job spam |

4. **Present the categorization** to the user as a table before taking action. Include message count per category and list specific senders/subjects for Actionable items.

5. **After user confirms**, execute in this order:
   - Collect message IDs per action group
   - `gmail_messages_batch_modify` to mark read + archive (remove UNREAD and INBOX labels)
   - `gmail_message_trash` for spam/scam items (use individual calls, not batch_delete — trash is recoverable)
   - Report summary: "Archived X, trashed Y, Z messages need your attention"

6. **For actionable items**, offer next steps:
   - "Want me to draft a reply to [sender]?"
   - "Want me to read the full message from [sender]?"
   - "Want to set up a filter for [recurring sender]?"

## Important

- Never auto-archive or trash without showing the categorization first
- When in doubt about a category, leave it as Actionable
- Security alerts (new sign-in, password change) should always be surfaced even if archived
- If a message is from a known contact, lean toward Actionable
