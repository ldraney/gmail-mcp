---
name: account-overview
description: Quick status check across all configured Gmail accounts — unread counts, recent activity, storage
argument-hint: "[account or 'all']"
---

# Account Overview

Get a quick status summary for one or all configured Gmail accounts.

## Steps

1. **Get profiles** — call `gmail_get_profile` for each configured account (parallel):
   ```
   gmail_get_profile(account="draneylucas")
   gmail_get_profile(account="lucastoddraney")
   gmail_get_profile(account="devopsphilosopher")
   ```

2. **Get unread counts** — for each account (parallel):
   ```
   gmail_messages_list(query="is:unread", max_results=1, account=...)
   ```
   The `resultSizeEstimate` field gives approximate unread count.

3. **Get recent activity** — for each account (parallel):
   ```
   gmail_messages_list(query="newer_than:1d", max_results=5, account=...)
   ```
   Then fetch metadata for the top 5 to show recent senders/subjects.

4. **Present summary**:
   ```
   Gmail Account Overview
   ══════════════════════

   draneylucas@gmail.com
     Unread: ~42 | Total: 12,847 | Threads: 8,203
     Recent: LinkedIn, ByteByteGo, GitHub Actions

   lucastoddraney@gmail.com
     Unread: ~3 | Total: 1,204 | Threads: 890
     Recent: Google Security Alert

   devopsphilosopher@gmail.com
     Unread: ~17 | Total: 5,631 | Threads: 3,102
     Recent: AWS, HashiCorp, KubeCon
   ```

5. **Offer next steps**:
   - "Want me to triage [account] inbox?" (invoke /inbox-triage)
   - "Want to search for something specific?" (invoke /search-emails)
   - "Want to clean up [account]?" (invoke /bulk-cleanup)

## Notes

- Skip accounts that don't have tokens configured (the tool will return an error)
- If only one account is configured, just show that one without asking
