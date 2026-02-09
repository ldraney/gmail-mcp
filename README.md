# gmail-mcp

Gmail MCP server for Claude Code.

## What is this?

An MCP (Model Context Protocol) server that gives Claude Code direct access to Gmail. Read, triage, draft replies, and send emails across multiple accounts.

## Accounts

- draneylucas@gmail.com
- lucastoddraney@gmail.com
- devopsphilosopher@gmail.com

## Architecture

Part of the **Claude Agent** execution layer:

```
OpenClaw Commander (orchestration)
  └── Claude Agent: Email Triage
        ├── MCP: gmail-mcp (this repo)
        ├── Skills: /triage-email, /draft-reply, /email-summary
        └── SOP: Email Triage Workflow
```

## Status

**Planning** — Setting up Google OAuth and MCP server.

## Setup

See the [Google OAuth Setup Guide](docs/google-oauth-setup.md) (coming soon — shared setup with calendar-mcp).
