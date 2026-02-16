[![PyPI](https://img.shields.io/pypi/v/gmail-mcp-ldraney)](https://pypi.org/project/gmail-mcp-ldraney/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

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
