# Mono Memory MCP

> **One shared brain for every AI on your team — persistent across sessions, searchable, always in sync.**

A lightweight, self-hosted [MCP](https://modelcontextprotocol.io/) server that gives your AI coding assistants long-term memory. Built for teams where multiple people use AI-powered editors (Claude Code, Cursor, Windsurf) and need their AIs to remember past decisions, share discoveries, and stay aligned — without re-explaining everything every session.

## The Problem

- Your AI assistant **forgets everything** when a session ends.
- Each team member's AI works in isolation — **no shared knowledge**.
- Critical decisions, bug fixes, and architectural context get lost between sessions.

## The Solution

Mono Memory gives your team's AI assistants a **shared, persistent memory** backed by a single SQLite file. Any AI can save and retrieve observations, project context, and decisions — across sessions, across team members.

> **Why "Mono"?** — Like a monorepo manages all code in one place, Mono Memory manages all your team's AI knowledge in one server.

## How It Works

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

There are two roles: **Host** (runs the server) and **Client** (connects via plugin).

### Host: Start the Server

The host is the person (or machine) that runs the Mono Memory server for the team.

```bash
git clone https://github.com/potato-castle/mono-memory-mcp.git
cd mono-memory-mcp
uv run python server.py

The server starts on `http://0.0.0.0:8765/mcp` (streamable-http). Share this URL with your team — replace `0.0.0.0` with your machine's IP address (e.g. `http://192.168.0.10:8765/mcp`).

**Custom configuration:**

```bash
# Change port
MONO_MEMORY_PORT=9000 python server.py

# Change database directory
MONO_MEMORY_DB_DIR=/path/to/data python server.py

# Run in background
nohup python server.py > /tmp/mono-memory.log 2>&1 &

### Client: Install the Plugin (Claude Code)

Clients do **not** need to clone the repo. Just install the plugin in Claude Code:

/plugin marketplace add potato-castle/mono-memory-mcp
/plugin install mono-memory-mcp@mono-memory-mcp

> When prompted for scope, select **"Install for you, in this repo only (local scope)"**. This keeps the plugin active only in the current project.

Then run the setup skill to connect to your team's server:

/mono-memory-mcp:setup

This will prompt you for:
1. **Server URL** — the host's server address (e.g. `http://192.168.0.10:8765/mcp`)
2. **Author name** — your name, used to tag memories you save

The project name is automatically detected from your current directory name.

The setup will:
- Write `.mcp.json` in your project root (MCP server connection)
- Append auto-recording rules to `CLAUDE.md` (so your AI automatically saves discoveries)

Restart Claude Code to activate.

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

## Usage Examples

### Example 1: Save a debugging discovery

User: "Save that the login timeout was caused by Redis connection pool exhaustion."

Tool: memory_save
  project: "auth-service"
  content: "Login timeout root cause: Redis connection pool exhaustion under load. Fix: increased pool size from 10 to 50 and added retry logic in auth/session.py"
  tags: "bug,fix,redis,performance"

Response: {"status": "saved", "id": "a1b2c3d4-...", "author": "alice", "created_at": "2025-06-15T10:30:00+09:00"}

### Example 2: Search for past decisions

User: "What do we know about Redis in auth-service?"

Tool: memory_search
  query: "redis"
  project: "auth-service"

Response: {"count": 2, "results": [
  {"author": "alice", "content": "Login timeout root cause: Redis connection pool...", "source": "observation"},
  {"author": "bob", "content": "Migrated Redis from 6.x to 7.x for ACL support...", "source": "observation"}
]}

### Example 3: Initialize project context

User: "Set up the architecture overview for the payments project."

Tool: memory_init
  project: "payments"
  section: "architecture"
  content: "Microservice arch. Gateway (Express) -> Payment Service (FastAPI) -> Stripe API. PostgreSQL for transactions, Redis for idempotency keys."
  author: "carol"

Response: {"status": "updated", "project": "payments", "section": "architecture", "updated_at": "2025-06-15T14:00:00+09:00"}

---

## Skills

### `/api-docs` — Generate API Documentation

Generates a Swagger-style HTML API documentation page from memories stored in the mono-memory server.

/api-docs

The skill automatically:
1. Detects your project name from the current directory
2. Searches all API-related memories (endpoints, schemas, changes)
3. Generates a self-contained `api-docs.html` with:
   - Color-coded HTTP method badges (GET, POST, PUT, DELETE, PATCH)
   - Request/Response code boxes per endpoint
   - **Try it** panels — test APIs directly from the browser
   - Path parameter & query parameter input fields (Swagger-style)
   - Auth type selector (Bearer, JWT, Basic Auth, API Key)
   - Send button with live response display
   - Copy as curl button

**Prerequisite:** Save some API observations first so the skill has data to work with:

memory_save(project: "my-app", content: "GET /api/users - returns paginated user list with {page} and {limit} query params", tags: "api,endpoint")
memory_save(project: "my-app", content: "POST /api/users - creates user. Request: {name, email, role}. Response: {id, name, email, created_at}", tags: "api,endpoint")
memory_init(project: "my-app", section: "api", content: "REST API base URL: /api/v1. Auth: Bearer token required.")

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

The test script spawns the server with an isolated temporary database and verifies all 6 tools via streamable-http.

---

## Server Management

Scripts are provided in the `scripts/` directory:

```bash
./scripts/start.sh      # Start the server
./scripts/stop.sh       # Stop the server
./scripts/restart.sh    # Restart the server
./scripts/logs.sh       # Tail server logs in real-time
```

### Database location

By default: `./data/memory.db` (SQLite, WAL mode)

---

## CLAUDE.md Integration

The `/mono-memory-mcp:setup` skill automatically appends auto-recording rules to your project's `CLAUDE.md`. This tells your AI assistant to:
- Automatically save bugs, decisions, and discoveries to the shared memory
- Search existing memories at the start of each session
- Write all observations in English for team consistency

For manual setup, see [`CLAUDE_MD_TEMPLATE.md`](CLAUDE_MD_TEMPLATE.md).

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
