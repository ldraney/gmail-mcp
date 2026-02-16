[![PyPI](https://img.shields.io/pypi/v/gmail-mcp-ldraney)](https://pypi.org/project/gmail-mcp-ldraney/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

# gmail-mcp

MCP server for Gmail, built on [gmail-sdk](https://github.com/ldraney/gmail-sdk). Gives Claude Code (or any MCP client) full access to read, send, triage, draft, and manage email across multiple Gmail accounts through a single server instance.

## Install

```bash
pip install gmail-mcp-ldraney
```

## Run

```bash
gmail-mcp-ldraney
# or
python -m gmail_mcp
```

## Claude Code config

Add to your `.mcp.json`:

```json
{
  "mcpServers": {
    "gmail": {
      "command": "uvx",
      "args": ["gmail-mcp-ldraney"],
      "env": {
        "SECRETS_DIR": "~/secrets/google-oauth"
      }
    }
  }
}
```

Or register via CLI:

```bash
claude mcp add gmail -- uvx gmail-mcp-ldraney
```

## Prerequisites

Google OAuth credentials must be set up at `~/secrets/google-oauth/` (or the path in `SECRETS_DIR`):

- `credentials.json` -- OAuth client credentials (Desktop type)
- `gmail-{alias}.json` -- per-account token files (created automatically on first auth)

On first use the server opens your browser for Google sign-in. After that, tokens refresh automatically.

See the [Gmail API Setup Guide](docs/gmail-api-setup.md) for full details including scopes, multi-account configuration, and security.

## Multi-account support

A single server instance handles multiple Gmail accounts. Every tool accepts an optional `account` parameter (alias or full email). If only one account is configured, it is selected automatically.

Token files are stored per-account: `gmail-draneylucas.json`, `gmail-lucastoddraney.json`, etc.

## Available tools

### Messages
- `gmail_get_profile` -- Get authenticated user's Gmail profile
- `gmail_messages_list` -- List messages matching a search query
- `gmail_message_get` -- Get a single message by ID
- `gmail_message_send` -- Send a new email
- `gmail_message_reply` -- Reply to a message (preserves thread)
- `gmail_message_reply_all` -- Reply-all to a message
- `gmail_message_forward` -- Forward a message
- `gmail_message_modify` -- Add/remove labels on a message
- `gmail_message_archive` -- Archive a message (remove INBOX label)
- `gmail_mark_as_read` -- Mark a message as read
- `gmail_mark_as_unread` -- Mark a message as unread
- `gmail_message_trash` -- Move a message to trash
- `gmail_message_untrash` -- Remove a message from trash
- `gmail_message_delete` -- Permanently delete a message
- `gmail_messages_batch_modify` -- Batch modify labels on multiple messages
- `gmail_messages_batch_delete` -- Permanently delete multiple messages

### Threads
- `gmail_threads_list` -- List threads matching a search query
- `gmail_thread_get` -- Get a thread with all its messages
- `gmail_thread_modify` -- Modify labels on all messages in a thread
- `gmail_thread_trash` -- Move a thread to trash
- `gmail_thread_untrash` -- Remove a thread from trash
- `gmail_thread_delete` -- Permanently delete a thread

### Drafts
- `gmail_drafts_list` -- List drafts
- `gmail_draft_get` -- Get a single draft by ID
- `gmail_draft_create` -- Create a new draft
- `gmail_draft_update` -- Update an existing draft
- `gmail_draft_send` -- Send a draft
- `gmail_draft_delete` -- Delete a draft

### Labels
- `gmail_labels_list` -- List all labels (system and user-created)
- `gmail_label_get` -- Get label details with message/thread counts
- `gmail_label_create` -- Create a new label
- `gmail_label_update` -- Update a label's name or visibility
- `gmail_label_delete` -- Delete a user label

### Attachments
- `gmail_attachment_get` -- Get attachment data from a message

### Filters
- `gmail_filters_list` -- List all filters
- `gmail_filter_get` -- Get a single filter by ID
- `gmail_filter_create` -- Create a new filter with criteria and actions
- `gmail_filter_delete` -- Delete a filter

### History
- `gmail_history_list` -- List mailbox changes since a history ID (incremental sync)

### Settings
- `gmail_vacation_get` -- Get vacation auto-reply settings
- `gmail_vacation_set` -- Set vacation auto-reply settings

## License

[MIT](LICENSE)
