# Mono Memory MCP

> **One shared brain for every AI on your team — persistent across sessions, searchable, always in sync.**

A lightweight, self-hosted [MCP](https://modelcontextprotocol.io/) server that gives your AI coding assistants long-term memory. Built for teams where multiple people use AI-powered editors (Claude Code, Cursor, Windsurf) and need their AIs to remember past decisions, share discoveries, and stay aligned — without re-explaining everything every session.

## The Problem

- Your AI assistant **forgets everything** when a session ends.
- Each team member's AI works in isolation — **no shared knowledge**.
- Critical decisions, bug fixes, and architectural context get lost between sessions.

## The Solution

Mono Memory gives your team's AI assistants a **shared, persistent memory** backed by a single SQLite file. Any AI can save and retrieve observations, project context, and decisions — across sessions, across team members.

## How It Works

```
Session 1 (Alice — morning)
├─ AI discovers a tricky bug in auth logic
├─ → memory_save: "JWT refresh token race condition fix — added mutex lock"
└─ Session ends. AI forgets everything.

Session 2 (Bob — afternoon)
├─ AI starts working on auth-related feature
├─ → memory_search: "auth"
├─ ← Gets Alice's bug fix context instantly
└─ Avoids the same pitfall, builds on her solution.

Session 3 (Alice — next day)
├─ → memory_timeline: project="my-app", since="2025-03-01"
└─ ← Sees everything the team's AIs learned this week.
```

Every observation is stored in a shared SQLite database. Any team member's AI can save and query it through 6 MCP tools.

## Use Cases

### Solo Developer
- **Session continuity** — Your AI remembers yesterday's debugging insights, architectural decisions, and TODO notes without you copy-pasting context.
- **Project context** — Store your project's architecture, conventions, and API specs once. Your AI loads them on demand instead of re-reading files every session.

### Team (2-10 developers)
- **Shared knowledge base** — One person's AI discovers a gotcha? Everyone's AI knows about it.
- **Onboarding** — New team members' AIs instantly access the full history of decisions and patterns.
- **Cross-project awareness** — Working on the frontend? Search what the backend team's AI learned about the API yesterday.

### Multi-project
- **Centralized memory** — One server, multiple projects. Search across all or filter by project.
- **Timeline view** — See the evolution of decisions across your entire organization.

## Features

- **6 tools** — save, get, search, timeline, init, context
- **SQLite storage** — zero-config, WAL mode, single-file database
- **Streamable HTTP** — network-ready transport for team use
- **Environment variable config** — host, port, database path
- **Multi-project** — multiple authors and projects, keyword search, timeline view

---

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install & Run

```bash
git clone https://github.com/potato-castle/mono-memory-mcp.git
cd mono-memory-mcp
uv run python server.py
```

The server starts on `http://0.0.0.0:8765` using streamable-http transport.

---

## Connecting Your AI Editor

### Claude Code

Add to `.mcp.json` in your project root or home directory (`~`):

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

### Cursor

Add to `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "mono-memory": {
      "url": "http://<server-ip>:8765/mcp"
    }
  }
}
```

### Windsurf

Add to `~/.codeium/windsurf/mcp_config.json`:

```json
{
  "mcpServers": {
    "mono-memory": {
      "serverUrl": "http://<server-ip>:8765/mcp"
    }
  }
}
```

### VS Code (Copilot)

Add to `.vscode/mcp.json` in your project root:

```json
{
  "servers": {
    "mono-memory": {
      "type": "http",
      "url": "http://<server-ip>:8765/mcp"
    }
  }
}
```

After adding the config, restart your editor to connect.

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

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONO_MEMORY_HOST` | `0.0.0.0` | Server bind address |
| `MONO_MEMORY_PORT` | `8765` | Server port |
| `MONO_MEMORY_DB_DIR` | `./data` | Directory for the SQLite database |

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

## License

[MIT](LICENSE)
