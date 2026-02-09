# Gmail API Setup Guide

This guide covers Gmail-specific configuration for the `gmail-mcp` server. It assumes you have already completed the shared Google OAuth setup.

## Prerequisites

Complete the [Google OAuth Setup Guide](https://github.com/ldraney/calendar-mcp/blob/main/docs/google-oauth-setup.md) first. That guide walks through:

- Creating a Google Cloud project
- Enabling APIs (including Gmail API)
- Configuring the OAuth consent screen
- Adding test users
- Creating OAuth 2.0 **Desktop** credentials
- Downloading `credentials.json` to `~/secrets/google-oauth/credentials.json`

**Do not duplicate that setup.** Everything below is Gmail-specific.

> **Note:** This guide depends on the shared OAuth guide (calendar-mcp#2). If that guide is not yet available, you will need to complete the Google Cloud project and OAuth consent screen setup yourself before continuing.

---

## 1. Gmail-Specific OAuth Scopes

The Gmail API uses granular scopes. When the `gmail-mcp` server initiates the OAuth flow in your browser, it will request permissions based on these scopes:

| Scope | URL | Allows |
|-------|-----|--------|
| `gmail.readonly` | `https://www.googleapis.com/auth/gmail.readonly` | Read messages, threads, labels, drafts, and profile info. No modifications. |
| `gmail.send` | `https://www.googleapis.com/auth/gmail.send` | Send and forward emails, send drafts. Does not grant read access. |
| `gmail.modify` | `https://www.googleapis.com/auth/gmail.modify` | All of `readonly` plus: archive, trash/untrash, add/remove labels, batch modify. Does **not** include permanent delete or settings changes. |
| Full access | `https://mail.google.com/` | Everything above plus permanent delete. Required for `gmail_message_delete`, `gmail_messages_batch_delete`, and `gmail_thread_delete`. |

### Which scopes to request

For full `gmail-mcp` functionality including permanent delete, all three granular scopes plus the full-access scope are needed. The `gmail-mcp` server handles scope requests automatically during the OAuth flow.

If you do not need permanent delete, the three granular scopes (`gmail.readonly`, `gmail.send`, `gmail.modify`) are sufficient.

### Scope vs. what it unlocks in gmail-mcp

| gmail-mcp tool | Required scope |
|----------------|---------------|
| `gmail_get_profile` | `gmail.readonly` |
| `gmail_messages_list`, `gmail_message_get` | `gmail.readonly` |
| `gmail_threads_list`, `gmail_thread_get` | `gmail.readonly` |
| `gmail_labels_list`, `gmail_label_get` | `gmail.readonly` |
| `gmail_drafts_list`, `gmail_draft_get` | `gmail.readonly` |
| `gmail_attachment_get` | `gmail.readonly` |
| `gmail_filters_list`, `gmail_filter_get` | `gmail.readonly` |
| `gmail_vacation_get` | `gmail.readonly` |
| `gmail_message_send`, `gmail_message_forward` | `gmail.send` |
| `gmail_draft_send` | `gmail.send` |
| `gmail_message_modify`, `gmail_message_archive` | `gmail.modify` |
| `gmail_message_trash`, `gmail_message_untrash` | `gmail.modify` |
| `gmail_thread_modify`, `gmail_thread_trash`, `gmail_thread_untrash` | `gmail.modify` |
| `gmail_messages_batch_modify` | `gmail.modify` |
| `gmail_label_create`, `gmail_label_update`, `gmail_label_delete` | `gmail.modify` |
| `gmail_draft_create`, `gmail_draft_update`, `gmail_draft_delete` | `gmail.modify` |
| `gmail_filter_create`, `gmail_filter_delete` | `gmail.modify` |
| `gmail_vacation_set` | `gmail.modify` |
| `gmail_message_delete`, `gmail_messages_batch_delete` | `https://mail.google.com/` (full access) |
| `gmail_thread_delete` | `https://mail.google.com/` (full access) |

> **Note:** Trash operations (`gmail_message_trash`, `gmail_thread_trash`) use `gmail.modify` and move items to Trash. Permanent delete operations (`gmail_message_delete`, `gmail_thread_delete`) bypass Trash entirely and require the full `https://mail.google.com/` scope. Google will reject permanent delete API calls made with only `gmail.modify`.

---

## 2. Multi-Account Setup

We manage three Gmail accounts. The `gmail-mcp` server handles OAuth and token management itself -- you run one server instance per account, and each server handles its own authentication through a browser-based OAuth flow.

| Account | Server name | Port |
|---------|------------|------|
| `draneylucas@gmail.com` | `gmail-draneylucas` | 3010 |
| `lucastoddraney@gmail.com` | `gmail-lucastoddraney` | 3011 |
| `devopsphilosopher@gmail.com` | `gmail-devopsphilosopher` | 3012 |

### How authentication works

The `gmail-mcp` server uses **Desktop** OAuth credentials (the same `credentials.json` from the [OAuth guide](https://github.com/ldraney/calendar-mcp/blob/main/docs/google-oauth-setup.md)). There is no need to create separate Web Application credentials.

The flow is:

1. Claude Code starts the `gmail-mcp` server (via `.mcp.json` config)
2. On first use, the server opens your browser for Google sign-in
3. You sign in with the correct Google account and grant permissions
4. The server receives the authorization code via a local loopback redirect and exchanges it for tokens
5. The server stores and manages tokens automatically, refreshing them as needed

**Important:** When the browser opens, make sure you sign in with the correct Google account for that server instance. If you are already signed into a different account, use the account picker or an incognito window.

After the initial auth, the server uses refresh tokens automatically. You only need to re-authorize if you revoke access or the refresh token expires.

### Verifying the connection

After authentication, use the `gmail_get_profile` tool through Claude Code to verify each account is connected:

```
Ask Claude: "Use the gmail-draneylucas server to get my Gmail profile"
```

You should see the email address in the response.

---

## 3. MCP Server Configuration for Claude Code

The `gmail-mcp` server (npm package: `gmail-mcp`) runs one instance per account. Choose **one** of the two approaches below.

### Approach A: `.mcp.json` config (recommended)

Claude Code manages the server lifecycle. When Claude Code starts, it launches each server automatically. This is the simplest approach.

**.mcp.json** (place in your project root):

```json
{
  "mcpServers": {
    "gmail-draneylucas": {
      "command": "npx",
      "args": ["gmail-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "GOCSPX-YOUR_SECRET",
        "PORT": "3010"
      }
    },
    "gmail-lucastoddraney": {
      "command": "npx",
      "args": ["gmail-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "GOCSPX-YOUR_SECRET",
        "PORT": "3011"
      }
    },
    "gmail-devopsphilosopher": {
      "command": "npx",
      "args": ["gmail-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "GOCSPX-YOUR_SECRET",
        "PORT": "3012"
      }
    }
  }
}
```

Get your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from `~/secrets/google-oauth/credentials.json` (the Desktop OAuth credentials created in the [OAuth guide](https://github.com/ldraney/calendar-mcp/blob/main/docs/google-oauth-setup.md)).

You can also add the same config to `~/.claude/settings.json` under the `"mcpServers"` key for global availability across all projects.

### Approach B: Manual server management + CLI registration (alternative)

If you prefer to manage server processes yourself (e.g., via tmux, systemd, or background processes), start each server manually and register them with Claude Code.

**Step 1: Start the servers:**

```bash
# Start each server in separate terminals or background processes
GOOGLE_CLIENT_ID='...' GOOGLE_CLIENT_SECRET='...' PORT=3010 npx gmail-mcp &
GOOGLE_CLIENT_ID='...' GOOGLE_CLIENT_SECRET='...' PORT=3011 npx gmail-mcp &
GOOGLE_CLIENT_ID='...' GOOGLE_CLIENT_SECRET='...' PORT=3012 npx gmail-mcp &
```

**Step 2: Register with Claude Code:**

```bash
claude mcp add --transport http gmail-draneylucas http://localhost:3010/mcp
claude mcp add --transport http gmail-lucastoddraney http://localhost:3011/mcp
claude mcp add --transport http gmail-devopsphilosopher http://localhost:3012/mcp
```

> **Do not combine both approaches.** If you use `.mcp.json` (Approach A), Claude Code launches the servers itself. If you also start servers manually, you will have port conflicts. Pick one.

---

## 4. Available Tools

Once connected, Claude Code gets access to the full set of Gmail tools per account:

- **Messages**: list, get, send, forward, modify labels, archive, trash/untrash, delete, batch operations
- **Threads**: list, get (all messages), modify labels, trash/untrash, delete
- **Drafts**: list, get, create, update, send, delete
- **Labels**: list, get, create, update, delete
- **Attachments**: download
- **Filters**: list, get, create, delete
- **Settings**: get/set vacation auto-reply

Use `gmail_threads_list` and `gmail_thread_get` over `gmail_messages_list` when working with conversations -- threads give better context.

---

## 5. Security

### What never to commit

- `credentials.json` -- your Google OAuth client credentials
- `gmail-*.json` -- per-account token files containing refresh tokens
- `.mcp.json` -- if it contains client secrets (see below)
- Any file containing `client_secret`, `refresh_token`, or `access_token`
- `.env` files with OAuth credentials

### File permissions

```bash
# Restrict the secrets directory
chmod 700 ~/secrets/google-oauth/
chmod 600 ~/secrets/google-oauth/credentials.json
```

### .gitignore patterns

This repo's `.gitignore` includes patterns to prevent accidental commits:

```gitignore
# OAuth credentials and tokens
credentials.json
**/credentials.json
gmail-*.json
**/gmail-*.json
**/token*.json

# MCP config with secrets
.mcp.json

# Environment files
.env
.env.*
*.env

# Secrets directory (should never be in repo)
secrets/
```

### MCP config security

The `.mcp.json` file contains your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. While client IDs are semi-public, client secrets should be protected:

- **Project-level `.mcp.json`**: Add it to `.gitignore` (included in the patterns above)
- **`~/.claude/settings.json`**: Already outside any repo
- **Environment variables** (most secure): Set credentials in your shell profile and reference them in config:

```bash
# In ~/.bashrc or ~/.zshrc
export GOOGLE_CLIENT_ID="your-client-id"
export GOOGLE_CLIENT_SECRET="your-client-secret"
```

Then reference them in `.mcp.json` (Claude Code expands env vars in MCP config):

```json
{
  "mcpServers": {
    "gmail-draneylucas": {
      "command": "npx",
      "args": ["gmail-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}",
        "PORT": "3010"
      }
    }
  }
}
```

### Revoking access

If a token is compromised, revoke it immediately:

1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find your OAuth app and click **Remove Access**
3. Restart the `gmail-mcp` server for that account -- it will prompt for re-authentication on next use
