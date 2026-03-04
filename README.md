# Mono Memory MCP

A lightweight, self-hosted [MCP](https://modelcontextprotocol.io/) server for persistent team and project memory. Store observations, decisions, and project context in a local SQLite database and access them from any MCP-compatible client (e.g. Claude Code, Cursor, Windsurf).

## Features

- **6 tools** — save, get, search, timeline, init, context
- **SQLite storage** — zero-config, WAL mode, single-file database
- **3 transports** — stdio, SSE, streamable-http
- **Environment variable config** — host, port, database path
- **Team-ready** — multiple authors and projects, keyword search, timeline view

---

## Quick Start

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Install & Run

```bash
git clone https://github.com/chul0061/mono-memory-mcp.git
cd mono-memory-mcp
uv run python server.py
```

The server starts on `http://0.0.0.0:8765` with streamable-http transport by default.

### Transport Options

```bash
uv run python server.py              # streamable-http (default)
uv run python server.py --sse        # SSE
uv run python server.py --stdio      # stdio (for local MCP clients)
```

---

## Connecting from Claude Code

Add a `.mcp.json` file to your project root or home directory (`~`):

### Option 1: stdio (local, recommended for single-user)

```json
{
  "mcpServers": {
    "mono-memory": {
      "command": "uv",
      "args": ["--directory", "/path/to/mono-memory-mcp", "run", "python", "server.py", "--stdio"]
    }
  }
}
```

### Option 2: streamable-http (network, recommended for teams)

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

### Option 3: SSE (legacy network transport)

```json
{
  "mcpServers": {
    "mono-memory": {
      "type": "sse",
      "url": "http://<server-ip>:8765/sse"
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

The test script spawns the server in stdio mode with an isolated temporary database and verifies all 6 tools.

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
