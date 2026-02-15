# Gmail MCP — Agent Guide

Instructions for AI agents using the gmail-mcp toolset. This server manages 3 Gmail accounts through a single MCP server instance with 41 tools.

## Accounts

| Alias | Email |
|---|---|
| `draneylucas` | draneylucas@gmail.com |
| `lucastoddraney` | lucastoddraney@gmail.com |
| `devopsphilosopher` | devopsphilosopher@gmail.com |

Every tool accepts an `account` parameter. Pass the alias string (e.g., `"draneylucas"`) or full email. If only one account has tokens configured, omitting `account` auto-selects it. If multiple are configured, you **must** specify which account.

## Tool Overview

### Reading (safe, no side effects)

| Tool | Purpose | Key params |
|---|---|---|
| `gmail_get_profile` | Email address, total counts, history ID | — |
| `gmail_messages_list` | Search/list messages (IDs only) | `query`, `max_results`, `label_ids` |
| `gmail_message_get` | Full message content | `message_id`, `response_format` |
| `gmail_threads_list` | Search/list threads (IDs only) | `query`, `max_results`, `label_ids` |
| `gmail_thread_get` | Full thread with all messages | `thread_id`, `response_format` |
| `gmail_drafts_list` | List drafts | `query`, `max_results` |
| `gmail_draft_get` | Full draft content | `draft_id` |
| `gmail_labels_list` | All labels (system + user) | — |
| `gmail_label_get` | Single label with counts | `label_id` |
| `gmail_filters_list` | All email filters | — |
| `gmail_filter_get` | Single filter details | `filter_id` |
| `gmail_vacation_get` | Auto-reply settings | — |
| `gmail_attachment_get` | Base64 attachment data | `message_id`, `attachment_id` |
| `gmail_history_list` | Mailbox changes since a history ID | `start_history_id` |

### Organizing (reversible)

| Tool | Purpose | Notes |
|---|---|---|
| `gmail_message_modify` | Add/remove labels on a message | Pass comma-separated label IDs |
| `gmail_messages_batch_modify` | Modify labels on multiple messages | Comma-separated message IDs |
| `gmail_thread_modify` | Add/remove labels on entire thread | Applies to all messages in thread |
| `gmail_mark_as_read` | Remove UNREAD label | — |
| `gmail_mark_as_unread` | Add UNREAD label | — |
| `gmail_message_archive` | Remove INBOX label | Message stays in All Mail |
| `gmail_message_trash` | Move to trash | Auto-deleted after 30 days |
| `gmail_message_untrash` | Restore from trash | — |
| `gmail_thread_trash` | Trash entire thread | — |
| `gmail_thread_untrash` | Restore thread from trash | — |
| `gmail_label_create` | Create a user label | Returns label ID |
| `gmail_label_update` | Rename or change visibility | — |
| `gmail_label_delete` | Delete a user label | Cannot delete system labels |

### Composing (sends email or creates drafts)

| Tool | Purpose | Notes |
|---|---|---|
| `gmail_message_send` | Send a new email | `to`, `subject`, `body` required |
| `gmail_message_reply` | Reply to sender only | Preserves thread |
| `gmail_message_reply_all` | Reply to all recipients | Preserves thread |
| `gmail_message_forward` | Forward to another address | Optional `note` prepended |
| `gmail_draft_create` | Create a draft | Optional `thread_id` for reply drafts |
| `gmail_draft_update` | Replace draft content | Requires all fields (to, subject, body) |
| `gmail_draft_send` | Send an existing draft | — |
| `gmail_draft_delete` | Delete a draft | Permanent |

### Destructive (irreversible)

| Tool | Purpose | Danger level |
|---|---|---|
| `gmail_message_delete` | Permanently delete a message | **Bypasses trash, unrecoverable** |
| `gmail_messages_batch_delete` | Permanently delete multiple messages | **Bypasses trash, unrecoverable** |
| `gmail_thread_delete` | Permanently delete entire thread | **Bypasses trash, unrecoverable** |

### Settings (currently broken — OAuth scope missing)

| Tool | Status | Fix needed |
|---|---|---|
| `gmail_filter_create` | 403 | Add `gmail.settings.basic` scope to SDK, re-auth |
| `gmail_filter_delete` | 403 | Same |
| `gmail_vacation_set` | 403 | Same |

Read-only counterparts (`gmail_filters_list`, `gmail_filter_get`, `gmail_vacation_get`) work fine.

## Gmail Search Query Syntax

The `query` parameter on list tools uses Gmail's native search syntax. Key operators:

```
is:unread                        Unread messages
is:starred                       Starred messages
is:important                     Priority inbox
from:sender@example.com          From specific sender
to:recipient@example.com         To specific recipient
subject:meeting                  Subject contains "meeting"
has:attachment                   Has attachments
filename:pdf                     Attachment filename
larger:5M                        Larger than 5MB
newer_than:2d                    Within last 2 days
older_than:1y                    Older than 1 year
after:2025/01/01                 After a date
before:2025/12/31                Before a date
label:INBOX                      In a specific label
-label:TRASH                     NOT in a label
category:promotions              Gmail category
{from:a OR from:b}               OR grouping
```

Combine freely: `is:unread newer_than:3d -category:promotions from:linkedin.com`

## Key Patterns

### 1. List then get

`messages_list` and `threads_list` return only IDs. You must call `message_get` or `thread_get` to read content. For triage workflows, fetch with `response_format="metadata"` first (headers only, much smaller), then `"full"` only when you need the body.

### 2. Threads vs messages

- **Use threads** when you want to see a conversation in context or take action on an entire conversation (trash, label, archive).
- **Use messages** when you need to act on individual messages within a thread, or when searching for specific content.
- `thread_modify` applies labels to ALL messages in the thread. `message_modify` targets one message.

### 3. Label IDs vs names

Tools that modify labels require **label IDs**, not display names. System labels use uppercase names as IDs (`INBOX`, `UNREAD`, `STARRED`, `TRASH`, `SPAM`, `IMPORTANT`, `SENT`, `DRAFT`). User labels have opaque IDs like `Label_123`. Call `gmail_labels_list` to map names to IDs.

### 4. Batch operations

`batch_modify` and `batch_delete` accept comma-separated message IDs. Use these for bulk cleanup instead of looping individual calls. Much more efficient.

### 5. Pagination

List tools return a `nextPageToken` when there are more results. Pass it as `page_token` on the next call. Set `max_results` up to 500 per page.

### 6. History for incremental sync

`gmail_history_list` returns changes since a `start_history_id` (get it from `gmail_get_profile`). Use `history_types` to filter: `messageAdded`, `messageDeleted`, `labelAdded`, `labelRemoved`.

## Safety Rules

1. **Always confirm before sending email.** Present the draft (to, subject, body) and get explicit approval before calling `message_send`, `message_reply`, `message_reply_all`, `message_forward`, or `draft_send`.

2. **Prefer trash over delete.** Trash is recoverable (30 days). Permanent delete (`message_delete`, `batch_delete`, `thread_delete`) is irreversible. Only use permanent delete when explicitly requested for bulk cleanup of obvious spam/noise.

3. **Confirm destructive batch operations.** Before `batch_delete` or `batch_modify` on more than 10 messages, list what will be affected and confirm.

4. **Don't read emails unprompted.** Only access email content when the user asks. Don't proactively scan or summarize the inbox without a request.

5. **Multi-account awareness.** Always specify the `account` parameter when multiple accounts are configured. Sending an email from the wrong account is a serious mistake. Double-check which account is being used for send/reply/forward operations.

## Response Format Notes

- All tools return JSON strings. Responses are run through `_slim_response()` which strips nulls, empty values, and API noise (etag, serverResponse).
- Errors return `{"error": true, "message": "..."}` with optional `status_code` for API errors.
- `attachment_get` returns base64-encoded data that can be very large. Only fetch attachments when specifically needed.

## Common Gotchas

- **`draft_update` requires all fields.** You must pass `to`, `subject`, and `body` even if only changing one field — it replaces the entire draft content.
- **`message_modify` label params are comma-separated strings**, not JSON arrays. Same for `batch_modify` message IDs. E.g., `add_label_ids="STARRED,IMPORTANT"`.
- **`filter_create` params ARE JSON strings.** The `criteria` and `action` parameters take JSON: `criteria='{"from": "foo@bar.com"}'`.
- **`response_format` matters for performance.** Use `"metadata"` for scanning (returns headers only), `"minimal"` for IDs/labels only, `"full"` only when you need the body.
- **Archive does not delete.** It just removes the INBOX label. The message remains in All Mail and any other labels.
