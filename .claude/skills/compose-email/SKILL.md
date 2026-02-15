---
name: compose-email
description: Draft, review, and send an email with confirmation at each step
argument-hint: "[account] [recipient or reply-to-message-id]"
disable-model-invocation: true
---

# Compose Email

Draft and send an email with explicit user confirmation before sending.

## Modes

### New email
User provides recipient, subject, and intent. Agent drafts the body.

1. Confirm which `account` to send from
2. Draft the email content based on user's intent
3. Create the draft: `gmail_draft_create(to, subject, body, account)`
4. Present the full draft for review:
   ```
   From: draneylucas@gmail.com
   To: recipient@example.com
   Subject: ...
   ─────────────
   [body]
   ```
5. Ask: "Send this, edit it, or discard?"
6. On confirm: `gmail_draft_send(draft_id, account)`
7. On edit: get changes, `gmail_draft_update(draft_id, to, subject, body)`, repeat from step 4
8. On discard: `gmail_draft_delete(draft_id, account)`

### Reply
User provides a message ID to reply to.

1. Fetch the original: `gmail_message_get(message_id, response_format="full")`
2. Show the original message context (from, subject, key content)
3. Draft reply based on user's intent
4. Create draft reply: `gmail_draft_create(to, subject, body, thread_id=..., account)`
5. Present for review (same as above)
6. On confirm: `gmail_draft_send(draft_id)`

### Forward
User provides a message ID and target recipient.

1. Fetch the original: `gmail_message_get(message_id)`
2. Ask if user wants to add a note
3. Forward: `gmail_message_forward(message_id, to, note, account)`

## Safety

- **Always create a draft first**, never call `gmail_message_send` directly unless the user has provided the exact text they want sent
- **Always show the full draft** before sending
- **Double-check the sending account** — confirm with the user which account they want to send from
- **Reply vs Reply-All**: default to reply (sender only). Only use `gmail_message_reply_all` when user explicitly asks to reply all
