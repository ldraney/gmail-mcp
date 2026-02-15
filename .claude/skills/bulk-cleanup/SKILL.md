---
name: bulk-cleanup
description: Deep clean an inbox — find and remove old newsletters, promotions, large emails, and duplicate senders
argument-hint: "[account]"
---

# Bulk Email Cleanup

Perform a deep cleanup of an account's inbox. This goes beyond triage — it targets accumulated noise across the full mailbox.

## Steps

1. **Get account overview**
   ```
   gmail_get_profile(account=...)
   ```
   Note total messages and threads to gauge mailbox size.

2. **Identify cleanup targets** by running these searches in parallel:
   ```
   gmail_messages_list(query="category:promotions older_than:7d", max_results=100)
   gmail_messages_list(query="category:social older_than:7d", max_results=100)
   gmail_messages_list(query="category:updates older_than:14d", max_results=100)
   gmail_messages_list(query="from:noreply older_than:7d", max_results=100)
   gmail_messages_list(query="larger:5M older_than:30d", max_results=50)
   gmail_messages_list(query="is:unread older_than:30d", max_results=100)
   ```

3. **Sample and categorize** — for each search, fetch metadata on a sample (first 10-20) to understand what's in there. Group by sender domain.

4. **Present cleanup plan** to user:
   ```
   Cleanup Plan for draneylucas@gmail.com
   ─────────────────────────────────────
   Old promotions (>7d):     142 messages  → Archive + mark read
   Social notifications:      87 messages  → Archive + mark read
   Update emails (>14d):      63 messages  → Archive + mark read
   No-reply senders:          95 messages  → Archive + mark read
   Large emails (>5MB, >30d): 12 messages  → Review individually
   Stale unread (>30d):       34 messages  → Archive + mark read

   Total: ~433 messages to clean up
   ```

5. **After user confirms**, execute batch operations:
   - Use `gmail_messages_batch_modify` with `remove_label_ids="INBOX,UNREAD"` for archive+read
   - Process in batches of 50-100 message IDs (API limits)
   - Paginate through all results if more than one page

6. **Report results** with before/after counts.

## Escalation

- Large emails: show sender, subject, and size — let user decide individually
- Anything from a real person: flag for manual review, don't auto-archive
- If >500 messages match a single sender, suggest creating a filter for that sender

## Permanent Delete

Only use `gmail_messages_batch_delete` or `gmail_message_delete` when the user explicitly asks to permanently remove messages. Default to archive (remove from inbox, keep in All Mail).
