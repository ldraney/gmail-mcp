# Gmail API Setup Guide

This guide covers Gmail-specific configuration for the `gmail-mcp` server. It assumes you have already completed the shared Google OAuth setup.

## Prerequisites

Complete the [Google OAuth Setup Guide](https://github.com/ldraney/calendar-mcp/blob/main/docs/google-oauth-setup.md) first. That guide walks through:

- Creating a Google Cloud project
- Enabling APIs (including Gmail API)
- Configuring the OAuth consent screen
- Adding test users
- Creating OAuth 2.0 Desktop credentials
- Downloading `credentials.json` to `~/secrets/google-oauth/credentials.json`
- Running the initial token exchange script

**Do not duplicate that setup.** Everything below is Gmail-specific.

---

## 1. Gmail-Specific OAuth Scopes

The Gmail API uses granular scopes. When running the token exchange script from the OAuth guide, request these scopes for Gmail access:

| Scope | URL | Allows |
|-------|-----|--------|
| `gmail.readonly` | `https://www.googleapis.com/auth/gmail.readonly` | Read messages, threads, labels, drafts, and profile info. No modifications. |
| `gmail.send` | `https://www.googleapis.com/auth/gmail.send` | Send and forward emails, send drafts. Does not grant read access. |
| `gmail.modify` | `https://www.googleapis.com/auth/gmail.modify` | All of `readonly` plus: archive, trash/untrash, add/remove labels, batch modify. Does **not** include permanent delete or settings changes. |

### Which scopes to request

For full `gmail-mcp` functionality, request all three:

```
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.send
https://www.googleapis.com/auth/gmail.modify
```

**Note:** `gmail.modify` is a superset of `gmail.readonly` for message operations, but the `gmail-mcp` server checks for each scope individually. Request all three to avoid permission errors.

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
| `gmail_message_delete`, `gmail_messages_batch_delete`, `gmail_thread_delete` | `gmail.modify` |

---

## 2. Multi-Account Token Management

We manage three Gmail accounts, each with its own OAuth refresh token:

| Account | Token file |
|---------|-----------|
| `draneylucas@gmail.com` | `~/secrets/google-oauth/gmail-draneylucas.json` |
| `lucastoddraney@gmail.com` | `~/secrets/google-oauth/gmail-lucastoddraney.json` |
| `devopsphilosopher@gmail.com` | `~/secrets/google-oauth/gmail-devopsphilosopher.json` |

### Token file naming convention

```
~/secrets/google-oauth/gmail-{account-name}.json
```

Where `{account-name}` is the part before `@gmail.com`. This keeps Gmail tokens clearly separated from Calendar tokens (which use `calendar-{account-name}.json`).

### Authorizing each account

Run the token exchange script from the [OAuth guide](https://github.com/ldraney/calendar-mcp/blob/main/docs/google-oauth-setup.md) once per account. Each run opens a browser where you sign in as that specific Google account and grant consent.

```bash
# Authorize draneylucas@gmail.com
python3 ~/calendar-mcp/scripts/get-refresh-token.py \
  --credentials ~/secrets/google-oauth/credentials.json \
  --scopes "https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.modify" \
  --output ~/secrets/google-oauth/gmail-draneylucas.json

# Authorize lucastoddraney@gmail.com
python3 ~/calendar-mcp/scripts/get-refresh-token.py \
  --credentials ~/secrets/google-oauth/credentials.json \
  --scopes "https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.modify" \
  --output ~/secrets/google-oauth/gmail-lucastoddraney.json

# Authorize devopsphilosopher@gmail.com
python3 ~/calendar-mcp/scripts/get-refresh-token.py \
  --credentials ~/secrets/google-oauth/credentials.json \
  --scopes "https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send,https://www.googleapis.com/auth/gmail.modify" \
  --output ~/secrets/google-oauth/gmail-devopsphilosopher.json
```

**Important:** When the browser opens for each command, make sure you sign in with the correct Google account. If you are already signed into a different account, use the account picker or an incognito window.

### Token file format

Each token file is a JSON object containing the OAuth tokens:

```json
{
  "access_token": "ya29.a0...",
  "refresh_token": "1//0e...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "123456789.apps.googleusercontent.com",
  "client_secret": "GOCSPX-...",
  "scopes": [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify"
  ]
}
```

### Verifying tokens

After authorization, verify each token works:

```bash
# Quick test: get the profile for each account
# Replace TOKEN_FILE with the path to each token file
TOKEN_FILE=~/secrets/google-oauth/gmail-draneylucas.json
ACCESS_TOKEN=$(python3 -c "import json; print(json.load(open('$TOKEN_FILE'))['access_token'])")
curl -s -H "Authorization: Bearer $ACCESS_TOKEN" \
  "https://gmail.googleapis.com/gmail/v1/users/me/profile" | python3 -m json.tool
```

You should see the email address in the response. If you get a 401 error, the access token may have expired -- the MCP server handles refresh automatically using the refresh token.

---

## 3. MCP Server Configuration for Claude Code

The `gmail-mcp` server (npm package: `gmail-mcp`) uses an HTTP transport with a built-in OAuth proxy. You run one server instance per account.

### How it works

1. Start the `gmail-mcp` server with your Google OAuth client credentials
2. The server handles the OAuth flow and token management
3. Claude Code connects to the server via HTTP transport
4. The server proxies Gmail API requests using the authenticated token

### Running the server

Each account needs its own server instance on a different port:

```bash
# draneylucas@gmail.com
GOOGLE_CLIENT_ID='your-client-id' \
GOOGLE_CLIENT_SECRET='your-client-secret' \
MCP_TRANSPORT=http \
PORT=3010 \
npx gmail-mcp

# lucastoddraney@gmail.com (different port)
GOOGLE_CLIENT_ID='your-client-id' \
GOOGLE_CLIENT_SECRET='your-client-secret' \
MCP_TRANSPORT=http \
PORT=3011 \
npx gmail-mcp

# devopsphilosopher@gmail.com (different port)
GOOGLE_CLIENT_ID='your-client-id' \
GOOGLE_CLIENT_SECRET='your-client-secret' \
MCP_TRANSPORT=http \
PORT=3012 \
npx gmail-mcp
```

Get your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` from `~/secrets/google-oauth/credentials.json` (the Desktop OAuth credentials you created in the [OAuth guide](https://github.com/ldraney/calendar-mcp/blob/main/docs/google-oauth-setup.md)).

### Claude Code MCP config

Add the following to your project-level `.mcp.json` or global `~/.claude/settings.json`. This example uses project-level config:

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
        "MCP_TRANSPORT": "http",
        "PORT": "3010"
      }
    },
    "gmail-lucastoddraney": {
      "command": "npx",
      "args": ["gmail-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "GOCSPX-YOUR_SECRET",
        "MCP_TRANSPORT": "http",
        "PORT": "3011"
      }
    },
    "gmail-devopsphilosopher": {
      "command": "npx",
      "args": ["gmail-mcp"],
      "env": {
        "GOOGLE_CLIENT_ID": "YOUR_CLIENT_ID.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "GOCSPX-YOUR_SECRET",
        "MCP_TRANSPORT": "http",
        "PORT": "3012"
      }
    }
  }
}
```

**Or add to `~/.claude/settings.json`** under the `"mcpServers"` key using the same structure above for global availability across all projects.

### First-time auth per account

When Claude Code first connects to each `gmail-mcp` server, the server will initiate the OAuth flow:

1. The server opens a browser for Google sign-in
2. Sign in with the correct Google account (e.g., `draneylucas@gmail.com` for the first server)
3. Grant the requested Gmail permissions
4. The callback completes and the server stores the token in memory

After the initial auth, the server uses refresh tokens automatically. You only need to re-authorize if you revoke access or the refresh token expires.

### Adding the server via CLI

Alternatively, start the servers manually and add them via the `claude` CLI:

```bash
# Start each server in the background (or in separate terminals)
GOOGLE_CLIENT_ID='...' GOOGLE_CLIENT_SECRET='...' MCP_TRANSPORT=http PORT=3010 npx gmail-mcp &
GOOGLE_CLIENT_ID='...' GOOGLE_CLIENT_SECRET='...' MCP_TRANSPORT=http PORT=3011 npx gmail-mcp &
GOOGLE_CLIENT_ID='...' GOOGLE_CLIENT_SECRET='...' MCP_TRANSPORT=http PORT=3012 npx gmail-mcp &

# Register each with Claude Code
claude mcp add --transport http gmail-draneylucas http://localhost:3010/mcp
claude mcp add --transport http gmail-lucastoddraney http://localhost:3011/mcp
claude mcp add --transport http gmail-devopsphilosopher http://localhost:3012/mcp
```

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
- Any file containing `client_secret`, `refresh_token`, or `access_token`
- `.env` files with OAuth credentials

### File permissions

```bash
# Restrict the secrets directory
chmod 700 ~/secrets/google-oauth/
chmod 600 ~/secrets/google-oauth/credentials.json
chmod 600 ~/secrets/google-oauth/gmail-*.json
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

# Environment files
.env
.env.*
*.env

# Secrets directory (should never be in repo)
secrets/
```

### MCP config security

The `.mcp.json` file contains your `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`. While client IDs are semi-public, client secrets should be protected:

- If using a **project-level `.mcp.json`**, add it to `.gitignore` if the repo is public
- If using **`~/.claude/settings.json`**, it is already outside any repo
- Consider using environment variables in your shell profile instead of hardcoding in config files:

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
        "MCP_TRANSPORT": "http",
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
3. Delete the local token file: `rm ~/secrets/google-oauth/gmail-{account}.json`
4. Re-authorize using the token exchange script
