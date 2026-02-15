---
name: search-emails
description: Search across Gmail accounts using natural language — translates intent to Gmail query syntax
argument-hint: "[search description]"
---

# Search Emails

Translate a natural language search request into Gmail query syntax and return results.

## Steps

1. **Parse the user's intent** and build a Gmail query. Common translations:

   | User says | Gmail query |
   |-----------|------------|
   | "emails from John last week" | `from:john newer_than:7d` |
   | "unread newsletters" | `is:unread category:promotions OR category:updates` |
   | "attachments from boss" | `from:boss has:attachment` |
   | "large files" | `larger:10M` |
   | "that thread about the project" | `subject:project` or keyword search |
   | "emails I sent to X" | `to:X in:sent` |
   | "starred but not replied" | `is:starred -in:sent` |

2. **Determine scope**:
   - If user specifies an account, search that one
   - If not specified and multiple are configured, ask which account (or search all)
   - For cross-account search, run queries in parallel across all accounts

3. **Execute search**:
   ```
   gmail_messages_list(query=..., max_results=20, account=...)
   ```

4. **Fetch metadata** for results:
   ```
   gmail_message_get(message_id, response_format="metadata")
   ```
   Extract From, To, Subject, Date headers.

5. **Present results** as a numbered list:
   ```
   Found 12 messages matching "invoices from 2025":

   1. Jan 15 — QuickBooks <noreply@intuit.com> — "Invoice #1234"
   2. Feb 02 — Stripe <receipts@stripe.com> — "Payment receipt"
   ...
   ```

6. **Offer follow-up actions**:
   - "Want to read message #3?"
   - "Want to archive all of these?"
   - "Want to search with different terms?"

## Tips

- Use `response_format="metadata"` for search results — avoid loading full bodies unless the user asks to read a specific message
- Gmail queries are case-insensitive
- Use `{term1 OR term2}` for OR logic
- Use `-term` to exclude
- Dates: `after:2025/01/01 before:2025/06/01` for ranges
- For conversation context, use `gmail_thread_get` instead of `gmail_message_get`
