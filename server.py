"""
Mono Memory MCP Server

A lightweight, self-hosted MCP (Model Context Protocol) server for persistent
team/project memory. Stores observations, decisions, and project context in a
local SQLite database and exposes them as MCP tools.

Supports stdio, SSE, and streamable-http transports.
"""

import json
import logging
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# === Configuration ===
DB_DIR = Path(os.environ.get("MONO_MEMORY_DB_DIR", Path(__file__).parent / "data"))
DB_PATH = DB_DIR / "memory.db"
HOST = os.environ.get("MONO_MEMORY_HOST", "0.0.0.0")
PORT = int(os.environ.get("MONO_MEMORY_PORT", "8765"))

# stdout is reserved for MCP JSON-RPC — all logging goes to stderr
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mono-memory")

# === Database ===
_db: sqlite3.Connection | None = None


def _init_database() -> sqlite3.Connection:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS observations (
            id          TEXT PRIMARY KEY,
            author      TEXT NOT NULL,
            project     TEXT NOT NULL,
            content     TEXT NOT NULL,
            tags        TEXT NOT NULL DEFAULT '',
            created_at  TEXT NOT NULL,
            updated_at  TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_obs_content
            ON observations(content);
        CREATE INDEX IF NOT EXISTS idx_obs_tags
            ON observations(tags);
        CREATE INDEX IF NOT EXISTS idx_obs_project_time
            ON observations(project, created_at);
        CREATE INDEX IF NOT EXISTS idx_obs_author
            ON observations(author);

        CREATE TABLE IF NOT EXISTS project_contexts (
            project     TEXT NOT NULL,
            section     TEXT NOT NULL,
            content     TEXT NOT NULL,
            updated_by  TEXT NOT NULL DEFAULT '',
            updated_at  TEXT NOT NULL,
            PRIMARY KEY (project, section)
        );
    """)
    conn.commit()
    logger.info("Database initialized at %s", DB_PATH)
    return conn


def _get_db() -> sqlite3.Connection:
    global _db
    if _db is None:
        _db = _init_database()
    return _db


def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


def _now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat()


# === MCP Server ===
mcp = FastMCP("mono-memory", host=HOST, port=PORT)


@mcp.tool()
async def memory_save(
    author: str,
    project: str,
    content: str,
    tags: str = "",
) -> str:
    """Save an observation or piece of knowledge to the shared memory.

    Args:
        author: Name of the person recording (e.g. "alice", "bob")
        project: Project name (e.g. "my-app", "backend-api")
        content: The observation, decision, discovery, or knowledge to store
        tags: Comma-separated tags for categorization (e.g. "bug,fix,api")
    """
    db = _get_db()
    obs_id = str(uuid.uuid4())
    now = _now_iso()

    db.execute(
        """INSERT INTO observations (id, author, project, content, tags, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (obs_id, author.strip(), project.strip(), content.strip(), tags.strip(), now, now),
    )
    db.commit()
    logger.info("Saved observation %s by %s", obs_id, author)

    return json.dumps({"status": "saved", "id": obs_id, "created_at": now}, ensure_ascii=False)


@mcp.tool()
async def memory_get(id: str) -> str:
    """Retrieve a specific observation by its ID.

    Args:
        id: UUID of the observation to retrieve
    """
    db = _get_db()
    row = db.execute("SELECT * FROM observations WHERE id = ?", (id,)).fetchone()

    if row is None:
        return json.dumps(
            {"error": "not_found", "message": f"No observation found with ID '{id}'."},
            ensure_ascii=False,
        )

    return json.dumps(_row_to_dict(row), ensure_ascii=False)


@mcp.tool()
async def memory_search(
    query: str,
    author: str = "",
    project: str = "",
    limit: int = 20,
) -> str:
    """Search the shared memory by keyword.

    Searches both observations and project contexts.

    Args:
        query: Search keywords (space-separated words are combined with AND)
        author: Filter by author name
        project: Filter by project name
        limit: Maximum number of results (default 20)
    """
    db = _get_db()
    words = query.strip().split()

    # --- Search observations ---
    obs_conds: list[str] = []
    obs_params: list[str] = []
    for word in words:
        obs_conds.append("(content LIKE ? OR tags LIKE ?)")
        obs_params.extend([f"%{word}%", f"%{word}%"])
    if author.strip():
        obs_conds.append("author = ?")
        obs_params.append(author.strip())
    if project.strip():
        obs_conds.append("project = ?")
        obs_params.append(project.strip())
    obs_where = " AND ".join(obs_conds) if obs_conds else "1=1"
    obs_sql = f"SELECT *, 'observation' as source FROM observations WHERE {obs_where} ORDER BY created_at DESC LIMIT ?"
    obs_params.append(str(limit))
    obs_rows = db.execute(obs_sql, obs_params).fetchall()

    # --- Search project contexts ---
    ctx_conds: list[str] = []
    ctx_params: list[str] = []
    for word in words:
        ctx_conds.append("(content LIKE ? OR section LIKE ?)")
        ctx_params.extend([f"%{word}%", f"%{word}%"])
    if project.strip():
        ctx_conds.append("project = ?")
        ctx_params.append(project.strip())
    ctx_where = " AND ".join(ctx_conds) if ctx_conds else "1=1"
    ctx_sql = f"SELECT project, section, content, updated_by as author, updated_at as created_at, 'context' as source FROM project_contexts WHERE {ctx_where} ORDER BY updated_at DESC LIMIT ?"
    ctx_params.append(str(limit))
    ctx_rows = db.execute(ctx_sql, ctx_params).fetchall()

    results = [_row_to_dict(r) for r in obs_rows] + [_row_to_dict(r) for r in ctx_rows]

    return json.dumps({"count": len(results), "results": results}, ensure_ascii=False)


@mcp.tool()
async def memory_timeline(
    project: str = "",
    author: str = "",
    since: str = "",
    until: str = "",
    limit: int = 50,
) -> str:
    """Retrieve observations in chronological order.

    Useful for understanding the history of decisions and discoveries in a project.

    Args:
        project: Filter by project name
        author: Filter by author name
        since: Start date/time in ISO 8601 format (e.g. "2025-01-01")
        until: End date/time in ISO 8601 format (e.g. "2025-01-31")
        limit: Maximum number of results (default 50)
    """
    db = _get_db()
    conditions: list[str] = []
    params: list[str] = []

    if project.strip():
        conditions.append("project = ?")
        params.append(project.strip())

    if author.strip():
        conditions.append("author = ?")
        params.append(author.strip())

    if since.strip():
        conditions.append("created_at >= ?")
        params.append(since.strip())

    if until.strip():
        conditions.append("created_at <= ?")
        params.append(until.strip())

    where = " AND ".join(conditions) if conditions else "1=1"
    sql = f"SELECT * FROM observations WHERE {where} ORDER BY created_at ASC LIMIT ?"
    params.append(str(limit))

    rows = db.execute(sql, params).fetchall()
    entries = [_row_to_dict(r) for r in rows]

    return json.dumps(
        {
            "count": len(entries),
            "period": {"since": since or "(beginning)", "until": until or "(now)"},
            "entries": entries,
        },
        ensure_ascii=False,
    )


@mcp.tool()
async def memory_init(
    project: str,
    section: str,
    content: str,
    author: str = "",
) -> str:
    """Initialize or update a project context section.

    Stores project information by section in the central memory.
    If the same project+section already exists, it will be overwritten (upsert).

    Args:
        project: Project name (e.g. "my-app", "backend-api")
        section: Section name (e.g. "overview", "architecture", "api", "conventions", "env")
        content: The context content for this section
        author: Name of the person updating (e.g. "alice")
    """
    db = _get_db()
    now = _now_iso()

    db.execute(
        """INSERT INTO project_contexts (project, section, content, updated_by, updated_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(project, section) DO UPDATE SET
               content = excluded.content,
               updated_by = excluded.updated_by,
               updated_at = excluded.updated_at""",
        (project.strip(), section.strip(), content.strip(), author.strip(), now),
    )
    db.commit()
    logger.info("Init project=%s section=%s by %s", project, section, author)

    return json.dumps(
        {"status": "updated", "project": project.strip(), "section": section.strip(), "updated_at": now},
        ensure_ascii=False,
    )


@mcp.tool()
async def memory_context(
    project: str,
    section: str = "",
) -> str:
    """Retrieve project context information.

    If a section is specified, returns that section only.
    If section is omitted, returns a list of all sections for the project.

    Args:
        project: Project name
        section: Section name to retrieve (omit to list all sections)
    """
    db = _get_db()

    if section.strip():
        row = db.execute(
            "SELECT * FROM project_contexts WHERE project = ? AND section = ?",
            (project.strip(), section.strip()),
        ).fetchone()
        if row is None:
            return json.dumps(
                {"error": "not_found", "message": f"No context found for '{project}/{section}'."},
                ensure_ascii=False,
            )
        return json.dumps(_row_to_dict(row), ensure_ascii=False)

    rows = db.execute(
        "SELECT project, section, updated_by, updated_at FROM project_contexts WHERE project = ? ORDER BY section",
        (project.strip(),),
    ).fetchall()

    if not rows:
        return json.dumps(
            {"error": "not_found", "message": f"No context found for project '{project}'."},
            ensure_ascii=False,
        )

    sections = [_row_to_dict(r) for r in rows]
    return json.dumps({"project": project.strip(), "sections": sections}, ensure_ascii=False)


# === Entry Point ===
if __name__ == "__main__":
    logger.info("Starting mono-memory MCP server (streamable-http)")
    logger.info("Listening on http://%s:%s", HOST, PORT)
    mcp.run(transport="streamable-http")
