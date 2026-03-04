# Mono Memory MCP

> **One shared brain for every AI on your team — persistent across sessions, searchable, always in sync.**

A lightweight, self-hosted [MCP](https://modelcontextprotocol.io/) server that gives your AI coding assistants long-term memory. Built for teams where multiple people use AI-powered editors (Claude Code, Cursor, Windsurf) and need their AIs to remember past decisions, share discoveries, and stay aligned — without re-explaining everything every session.

## The Problem

- Your AI assistant **forgets everything** when a session ends.
- Each team member's AI works in isolation — **no shared knowledge**.
- Critical decisions, bug fixes, and architectural context get lost between sessions.

## The Solution

Mono Memory gives your team's AI assistants a **shared, persistent memory** backed by a single SQLite file. Any AI can save and retrieve observations, project context, and decisions — across sessions, across team members.

## Features

- **6 tools** — save, get, search, timeline, init, context
- **SQLite storage** — zero-config, WAL mode, single-file database
- **Streamable HTTP** — network-ready transport for team use
- **Environment variable config** — host, port, database path
- **Multi-project** — multiple authors and projects, keyword search, timeline view

---

## Quick Start

### Option 1: Claude Code Plugin (Recommended)

```
/plugin marketplace add potato-castle/mono-memory-mcp
/plugin install mono-memory-mcp@mono-memory-mcp
```

MCP server is auto-connected after install. Restart Claude Code to activate.

### Option 2: One-line Install

```bash
curl -fsSL https://raw.githubusercontent.com/potato-castle/mono-memory-mcp/main/install.sh | bash
```

### Option 3: Manual Setup

```bash
git clone https://github.com/potato-castle/mono-memory-mcp.git
cd mono-memory-mcp
uv run python server.py
```

The server starts on `http://0.0.0.0:8765` using streamable-http transport.

---

## Connecting from Claude Code

Add a `.mcp.json` file to your project root or home directory (`~`):

```json
{
  "mcpServers": {
    "mono-memory": {
      "type": "streamable-http",
      "url": "http://<server-ip>:8765/mcp"
    }
  }
}
```

After adding the config, restart Claude Code to connect.

---

## Tools

### `memory_save` — Save an observation

Store a discovery, decision, debugging insight, or any knowledge.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `author` | Yes | Author name (e.g. `"alice"`) |
| `project` | Yes | Project name (e.g. `"my-app"`) |
| `content` | Yes | The content to save |
| `tags` | No | Comma-separated tags (e.g. `"bug,fix,api"`) |

### `memory_get` — Retrieve by ID

| Parameter | Required | Description |
|-----------|----------|-------------|
| `id` | Yes | UUID of the observation |

### `memory_search` — Keyword search

Searches both observations and project contexts.

| Parameter | Required | Description |
|-----------|----------|-------------|
| `query` | Yes | Search keywords (space = AND) |
| `author` | No | Filter by author |
| `project` | No | Filter by project |
| `limit` | No | Max results (default 20) |

### `memory_timeline` — Chronological view

| Parameter | Required | Description |
|-----------|----------|-------------|
| `project` | No | Filter by project |
| `author` | No | Filter by author |
| `since` | No | Start date (ISO 8601, e.g. `"2025-01-01"`) |
| `until` | No | End date (ISO 8601, e.g. `"2025-01-31"`) |
| `limit` | No | Max results (default 50) |

### `memory_init` — Initialize/update project context

Store project information by section. Same project+section overwrites (upsert).

| Parameter | Required | Description |
|-----------|----------|-------------|
| `project` | Yes | Project name |
| `section` | Yes | Section name (e.g. `"overview"`, `"architecture"`, `"api"`) |
| `content` | Yes | Section content |
| `author` | No | Who updated it |

### `memory_context` — Retrieve project context

| Parameter | Required | Description |
|-----------|----------|-------------|
| `project` | Yes | Project name |
| `section` | No | Section name (omit to list all sections) |

---

## Install from PyPI

```bash
pip install mono-memory-mcp
mono-memory-mcp
```

Or with a specific transport:

```bash
mono-memory-mcp --transport stdio
```

---

## Usage Examples

### Example 1: Save a debugging discovery

```
User: "Save that the login timeout was caused by Redis connection pool exhaustion."

Tool: memory_save
  project: "auth-service"
  content: "Login timeout root cause: Redis connection pool exhaustion under load. Fix: increased pool size from 10 to 50 and added retry logic in auth/session.py"
  tags: "bug,fix,redis,performance"

Response: {"status": "saved", "id": "a1b2c3d4-...", "author": "alice", "created_at": "2025-06-15T10:30:00+09:00"}
```

### Example 2: Search for past decisions

```
User: "What do we know about Redis in auth-service?"

Tool: memory_search
  query: "redis"
  project: "auth-service"

Response: {"count": 2, "results": [
  {"author": "alice", "content": "Login timeout root cause: Redis connection pool...", "source": "observation"},
  {"author": "bob", "content": "Migrated Redis from 6.x to 7.x for ACL support...", "source": "observation"}
]}
```

### Example 3: Initialize project context

```
User: "Set up the architecture overview for the payments project."

Tool: memory_init
  project: "payments"
  section: "architecture"
  content: "Microservice arch. Gateway (Express) -> Payment Service (FastAPI) -> Stripe API. PostgreSQL for transactions, Redis for idempotency keys."
  author: "carol"

Response: {"status": "updated", "project": "payments", "section": "architecture", "updated_at": "2025-06-15T14:00:00+09:00"}
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONO_MEMORY_HOST` | `0.0.0.0` | Server bind address |
| `MONO_MEMORY_PORT` | `8765` | Server port |
| `MONO_MEMORY_DB_DIR` | `./data` | Directory for the SQLite database |
| `DEFAULT_AUTHOR` | _(empty)_ | Default author name for `memory_save` |

---

## Testing

```bash
cd mono-memory-mcp
uv run python test_server.py
```

The test script spawns the server with an isolated temporary database and verifies all 6 tools via streamable-http.

---

## Deployment

### Background process

```bash
nohup uv run python server.py > /tmp/mono-memory.log 2>&1 &
```

### Stop

```bash
lsof -ti:8765 | xargs kill
```

### Database location

By default: `./data/memory.db` (SQLite, WAL mode)

---

## CLAUDE.md Integration

To have Claude Code automatically record observations during work sessions, add the template from [`CLAUDE_MD_TEMPLATE.md`](CLAUDE_MD_TEMPLATE.md) to your project's `CLAUDE.md`.

---

## Privacy Policy

Mono Memory MCP is a fully self-hosted, local server.

- **No data leaves your machine**: All data is stored in a local SQLite file.
- **No telemetry**: The server does not collect, transmit, or share any usage data.
- **No external network calls**: The server does not make any outbound HTTP requests.
- **No authentication data**: The server does not handle credentials or tokens for third-party services.
- **Data retention**: Data persists in the SQLite database until you manually delete it.

Your memory data is entirely under your control.

<!-- mcp-name: io.github.potato-castle/mono-memory-mcp -->

---

## License

[MIT](LICENSE)
