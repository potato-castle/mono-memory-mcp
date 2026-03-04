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
import re
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
        DROP INDEX IF EXISTS idx_obs_content;
        DROP INDEX IF EXISTS idx_obs_tags;
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

        -- FTS5 full-text search indexes (external content)
        CREATE VIRTUAL TABLE IF NOT EXISTS observations_fts USING fts5(
            content, tags,
            content=observations, content_rowid=rowid,
            tokenize='unicode61'
        );
        CREATE VIRTUAL TABLE IF NOT EXISTS contexts_fts USING fts5(
            section, content,
            content=project_contexts, content_rowid=rowid,
            tokenize='unicode61'
        );
    """)
    # Rebuild FTS indexes only when empty (first migration or fresh DB)
    if conn.execute("SELECT count(*) FROM observations_fts").fetchone()[0] == 0:
        conn.execute("INSERT INTO observations_fts(observations_fts) VALUES('rebuild')")
        conn.execute("INSERT INTO contexts_fts(contexts_fts) VALUES('rebuild')")
        logger.info("FTS indexes rebuilt from existing data")
    conn.commit()
    logger.info("Database initialized at %s (FTS5 enabled)", DB_PATH)
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


def _sanitize_fts_query(query: str) -> str | None:
    """Convert user input into a safe FTS5 query string.

    Strips special characters, skips reserved keywords,
    wraps each term in double quotes, and joins with AND.
    Returns None if no valid search terms remain.
    """
    words = query.strip().split()
    safe_terms: list[str] = []
    for word in words:
        cleaned = re.sub(r'[()\"*^:{}\[\]]', '', word)
        if not cleaned or cleaned.upper() in ('AND', 'OR', 'NOT', 'NEAR'):
            continue
        safe_terms.append('"' + cleaned + '"')
    return ' AND '.join(safe_terms) if safe_terms else None


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
    author = author.strip()
    project = project.strip()
    content = content.strip()
    tags = tags.strip()

    cursor = db.execute(
        """INSERT INTO observations (id, author, project, content, tags, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (obs_id, author, project, content, tags, now, now),
    )
    # Sync FTS index
    db.execute(
        "INSERT INTO observations_fts(rowid, content, tags) VALUES (?, ?, ?)",
        (cursor.lastrowid, content, tags),
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
    """Search the shared memory using full-text search.

    Searches both observations and project contexts with BM25 relevance ranking.

    Args:
        query: Search keywords (space-separated words are combined with AND)
        author: Filter by author name
        project: Filter by project name
        limit: Maximum number of results (default 20)
    """
    db = _get_db()
    author = author.strip()
    project = project.strip()
    fts_query = _sanitize_fts_query(query)

    if fts_query is None:
        return json.dumps({"count": 0, "results": []}, ensure_ascii=False)

    # --- Search observations via FTS5 ---
    obs_conds: list[str] = ["observations_fts MATCH ?"]
    obs_params: list[object] = [fts_query]
    if author:
        obs_conds.append("o.author = ?")
        obs_params.append(author)
    if project:
        obs_conds.append("o.project = ?")
        obs_params.append(project)
    obs_where = " AND ".join(obs_conds)
    obs_sql = f"""
        SELECT o.*, 'observation' as source, observations_fts.rank
        FROM observations_fts
        JOIN observations o ON o.rowid = observations_fts.rowid
        WHERE {obs_where}
        ORDER BY observations_fts.rank
        LIMIT ?
    """
    obs_params.append(limit)
    obs_rows = db.execute(obs_sql, obs_params).fetchall()

    # --- Search project contexts via FTS5 ---
    ctx_conds: list[str] = ["contexts_fts MATCH ?"]
    ctx_params: list[object] = [fts_query]
    if project:
        ctx_conds.append("pc.project = ?")
        ctx_params.append(project)
    ctx_where = " AND ".join(ctx_conds)
    ctx_sql = f"""
        SELECT pc.project, pc.section, pc.content, pc.updated_by as author,
               pc.updated_at as created_at, 'context' as source, contexts_fts.rank
        FROM contexts_fts
        JOIN project_contexts pc ON pc.rowid = contexts_fts.rowid
        WHERE {ctx_where}
        ORDER BY contexts_fts.rank
        LIMIT ?
    """
    ctx_params.append(limit)
    ctx_rows = db.execute(ctx_sql, ctx_params).fetchall()

    # Merge, sort by relevance, and enforce limit
    results = sorted(
        [_row_to_dict(r) for r in obs_rows] + [_row_to_dict(r) for r in ctx_rows],
        key=lambda r: r.get("rank", 0),
    )[:limit]

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
    project = project.strip()
    section = section.strip()
    content = content.strip()
    author = author.strip()

    # Capture old row for FTS delete (if updating)
    old_row = db.execute(
        "SELECT rowid, section, content FROM project_contexts WHERE project = ? AND section = ?",
        (project, section),
    ).fetchone()

    cursor = db.execute(
        """INSERT INTO project_contexts (project, section, content, updated_by, updated_at)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(project, section) DO UPDATE SET
               content = excluded.content,
               updated_by = excluded.updated_by,
               updated_at = excluded.updated_at""",
        (project, section, content, author, now),
    )

    # Sync FTS index
    if old_row:
        db.execute(
            "INSERT INTO contexts_fts(contexts_fts, rowid, section, content) VALUES('delete', ?, ?, ?)",
            (old_row[0], old_row[1], old_row[2]),
        )
        rowid = old_row[0]  # rowid unchanged on UPDATE
    else:
        rowid = cursor.lastrowid
    db.execute(
        "INSERT INTO contexts_fts(rowid, section, content) VALUES (?, ?, ?)",
        (rowid, section, content),
    )
    db.commit()
    logger.info("Init project=%s section=%s by %s", project, section, author)

    return json.dumps(
        {"status": "updated", "project": project, "section": section, "updated_at": now},
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
